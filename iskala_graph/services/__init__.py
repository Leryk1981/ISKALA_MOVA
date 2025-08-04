# services/__init__.py - ISKALA MOVA Services Module
"""
🌍 ISKALA MOVA Services Package
Enterprise-grade services for multilingual AI system
"""

# Core graph infrastructure (existing)
from .neo4j_driver import (
    Neo4jConnection,
    get_neo4j_connection,
    close_neo4j_connection
)

from .graph_models import (
    BaseNode,
    Intent,
    Phase, 
    ContextChunk,
    User,
    Session,
    NodeType,
    RelationType,
    GraphQueryBuilder,
    CypherTemplates
)

# Embedding services (existing)
from .embedding_service import (
    EmbeddingService,
    get_embedding_service,
    close_embedding_service
)

# 🌍 NEW: Multilingual document processing
from .document_processor import (
    # Main processor
    MultilingualDocumentProcessor,
    
    # Data models
    DocChunk,
    DetectedLanguage,
    LanguageCode,
    
    # Tokenizers
    BaseTokenizer,
    UkrainianTokenizer,
    EnglishTokenizer,
    RussianTokenizer,
    DefaultTokenizer,
    TokenizerRegistry,
    
    # Language detection
    LanguageDetector,
    
    # Convenience functions
    process_multilingual_document,
    chunk_multilingual_text
)

# Version info
__version__ = "2.2.0"  # Updated for multilingual support
__all__ = [
    # Neo4j infrastructure
    "Neo4jConnection",
    "get_neo4j_connection", 
    "close_neo4j_connection",
    
    # Graph models
    "BaseNode",
    "Intent",
    "Phase",
    "ContextChunk", 
    "User",
    "Session",
    "NodeType",
    "RelationType",
    "GraphQueryBuilder",
    "CypherTemplates",
    
    # Embedding services
    "EmbeddingService",
    "get_embedding_service",
    "close_embedding_service",
    
    # 🌍 Multilingual document processing
    "MultilingualDocumentProcessor",
    "DocChunk",
    "DetectedLanguage",
    "LanguageCode",
    "BaseTokenizer",
    "UkrainianTokenizer",
    "EnglishTokenizer", 
    "RussianTokenizer",
    "DefaultTokenizer",
    "TokenizerRegistry",
    "LanguageDetector",
    "process_multilingual_document",
    "chunk_multilingual_text"
]

# Package metadata
__author__ = "ISKALA MOVA Team"
__description__ = "Multilingual AI services for knowledge graph and document processing"
__status__ = "Production Ready"

# Service registry for dependency injection
SERVICES = {
    "neo4j": Neo4jConnection,
    "embedding": EmbeddingService,
    "multilingual_processor": MultilingualDocumentProcessor,
    "tokenizer_registry": TokenizerRegistry,
    "language_detector": LanguageDetector
} 