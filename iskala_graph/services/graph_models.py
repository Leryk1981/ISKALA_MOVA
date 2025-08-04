"""
Graph Models для ISKALA MOVA
Модель даних та автогенерація Cypher запитів
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import uuid
import hashlib

class NodeType(str, Enum):
    """Типи вузлів в ISKALA MOVA graph"""
    INTENT = "Intent"
    PHASE = "Phase"
    CONTEXT_CHUNK = "ContextChunk"
    USER = "User"
    SESSION = "Session"
    TOOL = "Tool"
    RESPONSE = "Response"

class RelationType(str, Enum):
    """Типи зв'язків"""
    LEADS_TO = "LEADS_TO"
    CONTAINS = "CONTAINS"
    REFERENCES = "REFERENCES"
    USES = "USES"
    RESPONDS_TO = "RESPONDS_TO"
    SIMILAR_TO = "SIMILAR_TO"
    PART_OF = "PART_OF"

class BaseNode(BaseModel):
    """Базова модель для всіх вузлів"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @staticmethod
    def merge_query(label: str, props: Dict[str, Any], unique_key: str = "id") -> str:
        """Автогенерація MERGE запитів з оптимізацією"""
        
        # Формуємо WHERE умову для унікального ключа
        where_clause = f"{unique_key}: ${unique_key}"
        
        # Формуємо SET клаузулу для оновлення властивостей
        set_clauses = []
        for key, value in props.items():
            if key != unique_key:  # Унікальний ключ не оновлюємо
                set_clauses.append(f"n.{key} = ${key}")
        
        set_clause = "SET " + ", ".join(set_clauses) if set_clauses else ""
        
        query = f"""
        MERGE (n:{label} {{{where_clause}}})
        ON CREATE SET n += $props, n.created_at = datetime()
        ON MATCH SET n.updated_at = datetime()
        {set_clause}
        RETURN n
        """
        
        return query.strip()
    
    def to_cypher_params(self) -> Dict[str, Any]:
        """Конвертація в параметри для Cypher"""
        return {
            **self.dict(),
            "props": self.dict()
        }

class Intent(BaseNode):
    """Намір користувача в ISKALA MOVA"""
    name: str = Field(..., description="Назва наміру")
    description: Optional[str] = Field(None, description="Опис наміру")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    lang: str = Field(default="uk", description="Мова")
    category: Optional[str] = Field(None, description="Категорія")
    
    # Метадані для аналізу
    frequency: int = Field(default=1, description="Частота використання")
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def get_unique_key(self) -> str:
        """Унікальний ключ на основі name + lang"""
        return hashlib.md5(f"{self.name}_{self.lang}".encode()).hexdigest()

class Phase(BaseNode):
    """Фаза мислення в ISKALA MOVA"""
    name: str = Field(..., description="Назва фази")
    order: int = Field(..., description="Порядок виконання")
    description: Optional[str] = Field(None)
    
    # Phase-specific properties
    input_schema: Optional[Dict[str, Any]] = Field(None)
    output_schema: Optional[Dict[str, Any]] = Field(None)
    timeout_seconds: int = Field(default=30)
    
    class Config:
        # Дозволяємо зберігання JSON в Neo4j
        json_encoders = {
            dict: lambda v: v
        }

class ContextChunk(BaseNode):
    """🧠 Enhanced ContextChunk with vector embeddings for semantic search"""
    content: str = Field(..., description="Текстовий контент")
    source_doc: str = Field(..., description="Назва джерельного документа")
    chunk_hash: str = Field(..., description="Хеш для дедуплікації")
    
    # 🧠 Vector embeddings (384-dimensional for sentence-transformers)
    embedding: List[float] = Field(default_factory=list, description="384-dim embedding vector")
    
    # 🌍 Multilingual support
    language: str = Field(default="uk", description="ISO 639-1 language code")
    
    # 📊 Processing metadata from MultilingualDocumentProcessor
    position: int = Field(default=0, description="Chunk position in document")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Processing confidence")
    word_count: int = Field(default=0, ge=0)
    sentence_count: int = Field(default=0, ge=0)
    
    # 🔍 Search optimization
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def create_from_text(cls, text: str, source: str) -> "ContextChunk":
        """Створення ContextChunk з тексту"""
        chunk_hash = hashlib.sha256(text.encode()).hexdigest()
        return cls(
            content=text,
            source_doc=source,
            chunk_hash=chunk_hash
        )
    
    @classmethod
    def from_doc_chunk(cls, doc_chunk, embedding: List[float]) -> "ContextChunk":
        """Create ContextChunk from MultilingualDocumentProcessor DocChunk + embedding"""
        return cls(
            content=doc_chunk.content,
            source_doc=doc_chunk.source_doc,
            chunk_hash=doc_chunk.chunk_hash,
            embedding=embedding,
            language=doc_chunk.language,
            position=doc_chunk.position,
            confidence=doc_chunk.confidence,
            word_count=doc_chunk.word_count,
            sentence_count=doc_chunk.sentence_count,
            metadata=doc_chunk.metadata
        )
    
    def validate_embedding_dimensions(self) -> bool:
        """Validate that embedding has correct dimensions (384 for sentence-transformers)"""
        return len(self.embedding) == 384 if self.embedding else True
    
    def to_cypher_merge(self) -> str:
        """Generate optimized Cypher MERGE query with vector support"""
        return f"""
        MERGE (c:ContextChunk {{chunk_hash: '{self.chunk_hash}'}})
        SET c.content = $content,
            c.source_doc = $source_doc,
            c.language = $language,
            c.embedding = $embedding,
            c.position = $position,
            c.confidence = $confidence,
            c.word_count = $word_count,
            c.sentence_count = $sentence_count,
            c.keywords = $keywords,
            c.metadata = $metadata,
            c.updated_at = datetime()
        ON CREATE SET c.created_at = datetime()
        RETURN c
        """

class User(BaseNode):
    """Користувач системи"""
    username: str = Field(..., description="Ім'я користувача")
    email: Optional[str] = Field(None)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    def get_unique_key(self) -> str:
        return self.username

class Session(BaseNode):
    """Сесія взаємодії"""
    user_id: str = Field(..., description="ID користувача")
    session_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Статистика сесії
    queries_count: int = Field(default=0)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)

class GraphQueryBuilder:
    """Будівник складних Cypher запитів"""
    
    @staticmethod
    def create_intent_tree_query(root_intent: str) -> str:
        """Запит для створення дерева намірів"""
        return """
        // Знаходимо корневий намір
        MATCH (root:Intent {name: $root_intent})
        
        // Створюємо граф пов'язаних намірів
        OPTIONAL MATCH (root)-[:LEADS_TO*1..3]->(child:Intent)
        
        // Повертаємо структуру дерева
        RETURN root, 
               collect(DISTINCT child) as children,
               [p = (root)-[:LEADS_TO*1..3]->(child) | p] as paths
        """
    
    @staticmethod
    def rag_context_search_query(intent_name: str, limit: int = 5) -> str:
        """Пошук релевантного контексту для наміру"""
        return """
        // Знаходимо намір
        MATCH (i:Intent {name: $intent_name})
        
        // Шукаємо пов'язаний контекст
        MATCH (i)-[:REFERENCES]->(chunk:ContextChunk)
        
        // Або шукаємо схожий контекст за ключовими словами
        OPTIONAL MATCH (similar:ContextChunk)
        WHERE any(keyword IN similar.keywords WHERE keyword IN i.keywords)
        
        // Повертаємо найрелевантніші чанки
        WITH i, chunk, similar, 
             CASE WHEN chunk IS NOT NULL THEN 1.0 ELSE 0.5 END as relevance_score
        
        RETURN DISTINCT 
               coalesce(chunk, similar) as context_chunk,
               relevance_score
        ORDER BY relevance_score DESC
        LIMIT $limit
        """
    
    @staticmethod
    def user_session_analysis_query(user_id: str) -> str:
        """Аналіз сесій користувача"""
        return """
        MATCH (u:User {id: $user_id})-[:HAS_SESSION]->(s:Session)
        MATCH (s)-[:CONTAINS]->(i:Intent)
        
        WITH u, s, i, 
             count(i) as intent_count,
             collect(DISTINCT i.category) as categories
        
        RETURN u.username as username,
               s.id as session_id,
               s.start_time as session_start,
               intent_count,
               categories,
               s.queries_count as total_queries
        ORDER BY s.start_time DESC
        """

class CypherTemplates:
    """Колекція готових Cypher запитів"""
    
    # Створення індексів
    CREATE_INDEXES = [
        "CREATE INDEX intent_name_idx IF NOT EXISTS FOR (i:Intent) ON (i.name)",
        "CREATE INDEX intent_category_idx IF NOT EXISTS FOR (i:Intent) ON (i.category)",
        "CREATE INDEX chunk_hash_idx IF NOT EXISTS FOR (c:ContextChunk) ON (c.chunk_hash)",
        "CREATE INDEX user_username_idx IF NOT EXISTS FOR (u:User) ON (u.username)",
        "CREATE INDEX session_user_idx IF NOT EXISTS FOR (s:Session) ON (s.user_id)",
        
        # Vector index для embeddings (потребує Neo4j 5.x)
        """CREATE VECTOR INDEX chunk_embedding_idx IF NOT EXISTS
           FOR (c:ContextChunk) ON (c.embedding)
           OPTIONS {indexConfig: {
             `vector.dimensions`: 384,
             `vector.similarity_function`: 'cosine'
           }}"""
    ]
    
    # Constraints
    CREATE_CONSTRAINTS = [
        "CREATE CONSTRAINT intent_name_unique IF NOT EXISTS FOR (i:Intent) ON (i.name, i.lang)",
        "CREATE CONSTRAINT chunk_hash_unique IF NOT EXISTS FOR (c:ContextChunk) ON (c.chunk_hash)",
        "CREATE CONSTRAINT user_username_unique IF NOT EXISTS FOR (u:User) ON (u.username)"
    ]
    
    @staticmethod
    def vector_similarity_query(embedding: List[float], top_k: int = 10) -> str:
        """Пошук схожих ContextChunk за embedding"""
        return f"""
        CALL db.index.vector.queryNodes('chunk_embedding_idx', {top_k}, $embedding)
        YIELD node as chunk, score
        RETURN chunk.content as content,
               chunk.source as source,
               chunk.keywords as keywords,
               score
        ORDER BY score DESC
        """ 