"""
Neo4j Connection Driver для ISKALA MOVA
Production-ready драйвер з connection pool, error handling та retry policy
"""

import os
import logging
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

import neo4j
from neo4j import GraphDatabase, AsyncGraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable, TransientError
import redis.asyncio as redis
from pydantic import BaseModel, Field

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jConfig(BaseModel):
    """Конфігурація Neo4j з валідацією"""
    uri: str = Field(default="bolt://localhost:7687")
    username: str = Field(default="neo4j")
    password: str = Field(default="iskala-neo4j-2024-secure")
    database: str = Field(default="iskala-mova")
    
    # Connection pool settings
    max_connection_pool_size: int = Field(default=50)
    connection_acquisition_timeout: int = Field(default=60)
    max_transaction_retry_time: int = Field(default=15)
    
    # Security
    encrypted: bool = Field(default=False)
    trust: str = Field(default="TRUST_ALL_CERTIFICATES")

class Neo4jConnection:
    """Асинхронний Neo4j клієнт з connection pool та retry механізмом"""
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        self.config = config or Neo4jConfig()
        self.driver: Optional[neo4j.AsyncDriver] = None
        self.redis_client: Optional[redis.Redis] = None
        self._initialized = False
        
        # Статистика підключень
        self.connection_stats = {
            "total_queries": 0,
            "failed_queries": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def initialize(self):
        """Ініціалізація з'єднання з Neo4j та Redis"""
        if self._initialized:
            return
            
        try:
            # Neo4j driver
            self.driver = AsyncGraphDatabase.driver(
                self.config.uri,
                auth=(self.config.username, self.config.password),
                max_connection_pool_size=self.config.max_connection_pool_size,
                connection_acquisition_timeout=self.config.connection_acquisition_timeout,
                max_transaction_retry_time=self.config.max_transaction_retry_time,
                encrypted=self.config.encrypted,
                trust=self.config.trust
            )
            
            # Перевірка підключення
            await self.verify_connectivity()
            
            # Redis для кешування
            redis_password = os.getenv("REDIS_PASSWORD", "iskala-redis-2024")
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=redis_password,
                decode_responses=True
            )
            
            self._initialized = True
            logger.info("✅ Neo4j і Redis з'єднання успішно ініціалізовано")
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації Neo4j: {e}")
            raise
    
    async def close(self):
        """Закриття всіх з'єднань"""
        if self.driver:
            await self.driver.close()
        if self.redis_client:
            await self.redis_client.close()
        self._initialized = False
        logger.info("Neo4j та Redis з'єднання закрито")
    
    async def verify_connectivity(self) -> bool:
        """Перевірка доступності Neo4j"""
        if not self.driver:
            return False
            
        try:
            await self.driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Neo4j connectivity check failed: {e}")
            return False
    
    @asynccontextmanager
    async def get_session(self, database: Optional[str] = None):
        """Context manager для Neo4j сесії"""
        if not self._initialized:
            await self.initialize()
            
        db_name = database or self.config.database
        session = self.driver.session(database=db_name)
        
        try:
            yield session
        finally:
            await session.close()
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        cache_key: Optional[str] = None,
        cache_ttl: int = 300
    ) -> List[Dict[str, Any]]:
        """
        Виконання Cypher запиту з кешуванням та retry logic
        
        Args:
            query: Cypher запит
            parameters: Параметри запиту
            database: Назва бази даних
            cache_key: Ключ для кешування результату
            cache_ttl: Час життя кешу в секундах
        """
        
        self.connection_stats["total_queries"] += 1
        
        # Перевіряємо кеш
        if cache_key and self.redis_client:
            try:
                cached_result = await self.redis_client.get(f"neo4j:{cache_key}")
                if cached_result:
                    self.connection_stats["cache_hits"] += 1
                    logger.debug(f"Cache hit for key: {cache_key}")
                    import json
                    return json.loads(cached_result)
            except Exception as e:
                logger.warning(f"Redis cache error: {e}")
        
        self.connection_stats["cache_misses"] += 1
        
        # Виконуємо запит з retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.get_session(database) as session:
                    result = await session.run(query, parameters or {})
                    records = await result.data()
                    
                    # Кешуємо результат
                    if cache_key and records and self.redis_client:
                        try:
                            import json
                            await self.redis_client.set(
                                f"neo4j:{cache_key}", 
                                json.dumps(records), 
                                ex=cache_ttl
                            )
                        except Exception as e:
                            logger.warning(f"Failed to cache result: {e}")
                    
                    logger.debug(f"Query executed successfully: {len(records)} records")
                    return records
                    
            except (ServiceUnavailable, TransientError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Transient error, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    self.connection_stats["failed_queries"] += 1
                    raise
            except Exception as e:
                self.connection_stats["failed_queries"] += 1
                logger.error(f"Query execution failed: {e}")
                raise
    
    async def execute_write_transaction(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> Dict[str, Any]:
        """Виконання write транзакції"""
        
        async def _write_tx(tx):
            result = await tx.run(query, parameters or {})
            return await result.single()
        
        async with self.get_session(database) as session:
            return await session.execute_write(_write_tx)
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check для моніторингу"""
        health_status = {
            "neo4j": False,
            "redis": False,
            "timestamp": datetime.utcnow().isoformat(),
            "stats": self.connection_stats
        }
        
        try:
            # Перевірка Neo4j
            result = await self.execute_query("RETURN 'Graph ready' as status")
            health_status["neo4j"] = len(result) > 0
            
            # Перевірка Redis
            if self.redis_client:
                await self.redis_client.ping()
                health_status["redis"] = True
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            
        return health_status

# Глобальний instance
_neo4j_connection: Optional[Neo4jConnection] = None

async def get_neo4j_connection() -> Neo4jConnection:
    """Отримання глобального Neo4j connection"""
    global _neo4j_connection
    
    if not _neo4j_connection:
        config = Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "iskala-neo4j-2024-secure"),
            database=os.getenv("NEO4J_DATABASE", "iskala-mova")
        )
        _neo4j_connection = Neo4jConnection(config)
        await _neo4j_connection.initialize()
    
    return _neo4j_connection

async def close_neo4j_connection():
    """Закриття глобального з'єднання"""
    global _neo4j_connection
    if _neo4j_connection:
        await _neo4j_connection.close()
        _neo4j_connection = None 