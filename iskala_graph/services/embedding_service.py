"""
Embedding Service для ISKALA MOVA
=================================

Production-ready сервіс для генерації та кешування embeddings з використанням:
- sentence-transformers (all-MiniLM-L6-v2) - оптимізований для української мови
- Redis кешування з zstd компресією
- Async/await підтримка з batch processing
- Multi-GPU підтримка для production навантаження
"""

import os
import asyncio
import hashlib
import json
import logging
import time
from typing import List, Dict, Any, Optional, Union
from functools import wraps
import numpy as np

import redis.asyncio as redis
import zstd
from sentence_transformers import SentenceTransformer, util
import torch
from pydantic import BaseModel, Field

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingConfig(BaseModel):
    """Конфігурація для Embedding Service"""
    model_name: str = Field(default="all-MiniLM-L6-v2", description="Sentence-transformers модель")
    device: str = Field(default="auto", description="Обчислювальний пристрій")
    normalize_embeddings: bool = Field(default=True, description="Нормалізація для dot-product")
    
    # Redis конфігурація
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: Optional[str] = Field(default=None)
    cache_ttl: int = Field(default=3600, description="TTL в секундах")
    use_compression: bool = Field(default=True, description="zstd компресія")
    
    # Performance налаштування
    batch_size: int = Field(default=32, description="Розмір batch для encode")
    max_seq_length: int = Field(default=512, description="Максимальна довжина послідовності")
    
    # Multi-processing
    multi_process_devices: Optional[List[str]] = Field(default=None, description="Список пристроїв для multi-process")

class EmbeddingStats(BaseModel):
    """Статистика роботи Embedding Service"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    total_tokens_processed: int = 0
    avg_processing_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Відсоток попадань у кеш"""
        if self.total_requests == 0:
            return 0.0
        return (self.cache_hits / self.total_requests) * 100

def timing_decorator(func):
    """Декоратор для вимірювання часу виконання"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        logger.debug(f"{func.__name__} took {duration_ms:.2f}ms")
        return result
    return wrapper

class EmbeddingService:
    """
    Production-ready Embedding Service для ISKALA MOVA
    
    Особливості:
    - Async/await API
    - Redis кешування з компресією
    - Batch processing для оптимізації
    - Multi-GPU підтримка
    - Детальна статистика та моніторинг
    """
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self.model: Optional[SentenceTransformer] = None
        self.redis_client: Optional[redis.Redis] = None
        self.multi_process_pool = None
        self.stats = EmbeddingStats()
        self._initialized = False
        
        logger.info(f"EmbeddingService ініціалізовано з моделлю: {self.config.model_name}")
    
    async def initialize(self):
        """Асинхронна ініціалізація сервісу"""
        if self._initialized:
            return
        
        try:
            # Ініціалізація sentence-transformers моделі
            await self._init_model()
            
            # Ініціалізація Redis клієнта
            await self._init_redis()
            
            self._initialized = True
            logger.info("✅ EmbeddingService успішно ініціалізовано")
            
        except Exception as e:
            logger.error(f"❌ Помилка ініціалізації EmbeddingService: {e}")
            raise
    
    async def _init_model(self):
        """Ініціалізація sentence-transformers моделі"""
        # Визначення пристрою
        if self.config.device == "auto":
            if torch.cuda.is_available():
                device = "cuda"
                logger.info(f"🚀 Використовується CUDA: {torch.cuda.get_device_name()}")
            elif torch.backends.mps.is_available():
                device = "mps"
                logger.info("🚀 Використовується Apple MPS")
            else:
                device = "cpu"
                logger.info("💻 Використовується CPU")
        else:
            device = self.config.device
        
        # Завантаження моделі
        self.model = SentenceTransformer(
            self.config.model_name,
            device=device
        )
        
        # Налаштування максимальної довжини послідовності
        if hasattr(self.model, 'max_seq_length'):
            self.model.max_seq_length = self.config.max_seq_length
        
        # Опціональне налаштування multi-process pool
        if self.config.multi_process_devices:
            self.multi_process_pool = self.model.start_multi_process_pool(
                devices=self.config.multi_process_devices
            )
            logger.info(f"🔄 Multi-process pool створено з пристроями: {self.config.multi_process_devices}")
        
        logger.info(f"📊 Модель завантажено на пристрій: {device}")
        logger.info(f"📏 Максимальна довжина послідовності: {self.config.max_seq_length}")
        logger.info(f"📐 Розмірність embedding: {self.model.get_sentence_embedding_dimension()}")
    
    async def _init_redis(self):
        """Ініціалізація Redis клієнта"""
        try:
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                decode_responses=False,  # Для binary data
                socket_connect_timeout=5,
                socket_timeout=5,
                health_check_interval=30
            )
            
            # Перевірка з'єднання
            await self.redis_client.ping()
            logger.info("✅ Redis з'єднання встановлено")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis недоступний, продовжуємо без кешування: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, text: str) -> str:
        """Генерація ключа кешу на основі SHA256 хешу тексту"""
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        model_version = self.config.model_name.replace('/', '_')
        max_len = self.config.max_seq_length
        return f"emb:{model_version}:{max_len}:{text_hash}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[List[float]]:
        """Отримання embedding з кешу"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                if self.config.use_compression:
                    # Декомпресія zstd
                    decompressed_data = zstd.decompress(cached_data)
                    embedding = json.loads(decompressed_data.decode('utf-8'))
                else:
                    embedding = json.loads(cached_data.decode('utf-8'))
                
                self.stats.cache_hits += 1
                logger.debug(f"Cache hit for key: {cache_key[:16]}...")
                return embedding
                
        except Exception as e:
            logger.warning(f"Помилка читання з кешу: {e}")
        
        self.stats.cache_misses += 1
        return None
    
    async def _save_to_cache(self, cache_key: str, embedding: List[float]):
        """Збереження embedding в кеш"""
        if not self.redis_client:
            return
        
        try:
            embedding_json = json.dumps(embedding).encode('utf-8')
            
            if self.config.use_compression:
                # Компресія zstd
                compressed_data = zstd.compress(embedding_json, level=3)
                data_to_save = compressed_data
            else:
                data_to_save = embedding_json
            
            await self.redis_client.set(
                cache_key,
                data_to_save,
                ex=self.config.cache_ttl
            )
            
            logger.debug(f"Збережено в кеш: {cache_key[:16]}...")
            
        except Exception as e:
            logger.warning(f"Помилка збереження в кеш: {e}")
    
    @timing_decorator
    async def get_embedding(self, text: str) -> List[float]:
        """
        Отримання embedding для одного тексту
        
        Args:
            text: Вхідний текст для encoding
            
        Returns:
            Список float значень embedding
        """
        if not self._initialized:
            await self.initialize()
        
        self.stats.total_requests += 1
        
        # Генерація ключа кешу
        cache_key = self._generate_cache_key(text)
        
        # Спроба отримати з кешу
        cached_embedding = await self._get_from_cache(cache_key)
        if cached_embedding:
            return cached_embedding
        
        # Генерація нового embedding
        start_time = time.time()
        
        if self.multi_process_pool:
            embeddings = self.model.encode([text], pool=self.multi_process_pool)
        else:
            embeddings = self.model.encode([text])
        
        # Нормалізація для оптимізації dot-product
        if self.config.normalize_embeddings:
            embeddings = util.normalize_embeddings(embeddings)
        
        embedding = embeddings[0].tolist()
        
        # Оновлення статистики
        processing_time = (time.time() - start_time) * 1000
        self.stats.total_tokens_processed += len(text.split())
        self._update_avg_processing_time(processing_time)
        
        # Збереження в кеш
        await self._save_to_cache(cache_key, embedding)
        
        return embedding
    
    @timing_decorator
    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Batch encoding для списку текстів (оптимізовано для продуктивності)
        
        Args:
            texts: Список текстів для encoding
            
        Returns:
            Список embedding векторів
        """
        if not self._initialized:
            await self.initialize()
        
        if not texts:
            return []
        
        self.stats.total_requests += len(texts)
        
        # Перевірка кешу для всіх текстів
        cache_keys = [self._generate_cache_key(text) for text in texts]
        cached_results = {}
        texts_to_process = []
        indices_to_process = []
        
        for i, (text, cache_key) in enumerate(zip(texts, cache_keys)):
            cached_embedding = await self._get_from_cache(cache_key)
            if cached_embedding:
                cached_results[i] = cached_embedding
            else:
                texts_to_process.append(text)
                indices_to_process.append(i)
        
        logger.info(f"Batch processing: {len(cached_results)} з кешу, {len(texts_to_process)} нових")
        
        # Batch encoding для нових текстів
        new_embeddings = []
        if texts_to_process:
            start_time = time.time()
            
            if self.multi_process_pool:
                embeddings = self.model.encode(texts_to_process, pool=self.multi_process_pool)
            else:
                embeddings = self.model.encode(
                    texts_to_process,
                    batch_size=self.config.batch_size,
                    show_progress_bar=len(texts_to_process) > 100
                )
            
            # Нормалізація
            if self.config.normalize_embeddings:
                embeddings = util.normalize_embeddings(embeddings)
            
            new_embeddings = [emb.tolist() for emb in embeddings]
            
            # Статистика
            processing_time = (time.time() - start_time) * 1000
            total_tokens = sum(len(text.split()) for text in texts_to_process)
            self.stats.total_tokens_processed += total_tokens
            self._update_avg_processing_time(processing_time)
            
            # Збереження нових embedding в кеш
            for i, (text, embedding) in enumerate(zip(texts_to_process, new_embeddings)):
                cache_key = self._generate_cache_key(text)
                await self._save_to_cache(cache_key, embedding)
        
        # Збирання результатів у правильному порядку
        results = [None] * len(texts)
        
        # Додаємо кешовані результати
        for i, embedding in cached_results.items():
            results[i] = embedding
        
        # Додаємо нові результати
        for i, embedding_idx in enumerate(indices_to_process):
            results[embedding_idx] = new_embeddings[i]
        
        return results
    
    def _update_avg_processing_time(self, new_time_ms: float):
        """Оновлення середнього часу обробки"""
        if self.stats.avg_processing_time_ms == 0:
            self.stats.avg_processing_time_ms = new_time_ms
        else:
            # Експоненціальне згладжування
            alpha = 0.1
            self.stats.avg_processing_time_ms = (
                alpha * new_time_ms + (1 - alpha) * self.stats.avg_processing_time_ms
            )
    
    async def get_similarity(self, text1: str, text2: str) -> float:
        """Обчислення cosine similarity між двома текстами"""
        embeddings = await self.get_embeddings_batch([text1, text2])
        
        # Використовуємо util.cos_sim з sentence-transformers
        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
        return similarity
    
    async def find_most_similar(
        self, 
        query: str, 
        candidates: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Пошук найбільш схожих текстів з кандидатами"""
        
        # Отримуємо embeddings
        all_texts = [query] + candidates
        embeddings = await self.get_embeddings_batch(all_texts)
        
        query_embedding = embeddings[0]
        candidate_embeddings = embeddings[1:]
        
        # Обчислюємо similarities
        similarities = util.cos_sim([query_embedding], candidate_embeddings)[0]
        
        # Сортуємо та повертаємо top_k
        results = []
        for i, sim_score in enumerate(similarities):
            results.append({
                "text": candidates[i],
                "similarity": sim_score.item(),
                "index": i
            })
        
        # Сортування за спаданням similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:top_k]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Отримання статистики роботи сервісу"""
        redis_info = {}
        if self.redis_client:
            try:
                redis_info = await self.redis_client.info("memory")
                redis_info = {
                    "used_memory_human": redis_info.get("used_memory_human", "N/A"),
                    "used_memory_peak_human": redis_info.get("used_memory_peak_human", "N/A")
                }
            except:
                redis_info = {"status": "error"}
        
        return {
            "model_info": {
                "name": self.config.model_name,
                "device": str(self.model.device) if self.model else "not_loaded",
                "dimension": self.model.get_sentence_embedding_dimension() if self.model else 0,
                "max_seq_length": self.config.max_seq_length
            },
            "performance": {
                "total_requests": self.stats.total_requests,
                "cache_hit_rate": f"{self.stats.hit_rate:.2f}%",
                "total_tokens_processed": self.stats.total_tokens_processed,
                "avg_processing_time_ms": f"{self.stats.avg_processing_time_ms:.2f}"
            },
            "cache": {
                "enabled": self.redis_client is not None,
                "compression": self.config.use_compression,
                "ttl_seconds": self.config.cache_ttl,
                "redis_info": redis_info
            },
            "multi_process": {
                "enabled": self.multi_process_pool is not None,
                "devices": self.config.multi_process_devices
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check для моніторингу"""
        health = {
            "service": "embedding_service",
            "status": "healthy",
            "model_loaded": self.model is not None,
            "redis_connected": False,
            "timestamp": time.time()
        }
        
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health["redis_connected"] = True
            except:
                health["redis_connected"] = False
        
        # Тест простого encoding
        try:
            test_embedding = await self.get_embedding("test")
            health["embedding_test"] = len(test_embedding) > 0
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
        
        return health
    
    async def clear_cache(self, pattern: str = "emb:*") -> int:
        """Очищення кешу за паттерном"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Видалено {deleted} ключів з кешу")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Помилка очищення кешу: {e}")
            return 0
    
    async def close(self):
        """Закриття всіх з'єднань та ресурсів"""
        if self.multi_process_pool:
            self.model.stop_multi_process_pool(self.multi_process_pool)
            logger.info("Multi-process pool зупинено")
        
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis з'єднання закрито")
        
        self._initialized = False
        logger.info("EmbeddingService закрито")

# Глобальний instance для reuse
_embedding_service: Optional[EmbeddingService] = None

async def get_embedding_service(config: Optional[EmbeddingConfig] = None) -> EmbeddingService:
    """Отримання глобального instance EmbeddingService"""
    global _embedding_service
    
    if not _embedding_service:
        # Конфігурація з environment variables
        env_config = EmbeddingConfig(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            cache_ttl=int(os.getenv("EMBEDDING_CACHE_TTL", "3600"))
        )
        
        _embedding_service = EmbeddingService(config or env_config)
        await _embedding_service.initialize()
    
    return _embedding_service

async def close_embedding_service():
    """Закриття глобального сервісу"""
    global _embedding_service
    if _embedding_service:
        await _embedding_service.close()
        _embedding_service = None 