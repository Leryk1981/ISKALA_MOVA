# iskala_graph/__init__.py
"""
🌍 ISKALA MOVA - Multilingual AI Graph Infrastructure
====================================================

Enterprise-grade multilingual AI system with knowledge graph and document processing.

Key Features:
- 🧠 Neo4j Knowledge Graph with vector search
- 🌍 Multilingual document processing (50+ languages)  
- ⚡ Redis-cached embedding service with zstd compression
- 🔍 Intelligent text chunking with language-specific rules
- 🚀 FastAPI async architecture
- 📊 Production-ready monitoring and statistics

Architecture:
- Core Graph Infrastructure (Neo4j, Vector Search)
- Embedding Service (sentence-transformers + Redis)
- Multilingual Document Processor (langchain + language detection)
- Universal API layer (FastAPI + async)
"""

# Version and metadata
__version__ = "2.2.0"
__title__ = "ISKALA MOVA Multilingual AI Graph"
__description__ = "Enterprise multilingual AI system with knowledge graph"
__author__ = "ISKALA MOVA Team"
__status__ = "Production Ready"

# Core services export
from .services import (
    # 🧠 Neo4j Graph Infrastructure
    Neo4jConnection,
    get_neo4j_connection,
    close_neo4j_connection,
    
    # 📊 Graph Data Models
    BaseNode,
    Intent,
    Phase,
    ContextChunk,
    User,
    Session,
    NodeType,
    RelationType,
    GraphQueryBuilder,
    CypherTemplates,
    
    # 🧠 Embedding Services  
    EmbeddingService,
    get_embedding_service,
    close_embedding_service,
    
    # 🌍 Multilingual Document Processing
    MultilingualDocumentProcessor,
    DocChunk,
    DetectedLanguage,
    LanguageCode,
    BaseTokenizer,
    UkrainianTokenizer,
    EnglishTokenizer,
    RussianTokenizer,
    DefaultTokenizer,
    TokenizerRegistry,
    LanguageDetector,
    process_multilingual_document,
    chunk_multilingual_text,
    
    # 🔧 Service Registry
    SERVICES
)

# Cypher query templates
from .cypher import (
    INTENT_CREATE,
    PHASE_LINK,
    RAG_CHUNK_ADD
)

# Convenience imports for common use cases
from .services.document_processor import MultilingualDocumentProcessor as DocumentProcessor
from .services.embedding_service import EmbeddingService
from .services.neo4j_driver import Neo4jConnection as GraphDB

# Package-level exports
__all__ = [
    # Version info
    "__version__",
    "__title__", 
    "__description__",
    "__author__",
    "__status__",
    
    # 🧠 Core Infrastructure
    "Neo4jConnection",
    "GraphDB",  # Alias
    "get_neo4j_connection",
    "close_neo4j_connection",
    
    # 📊 Data Models
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
    
    # 🧠 Embeddings
    "EmbeddingService",
    "get_embedding_service",
    "close_embedding_service",
    
    # 🌍 Multilingual Processing
    "MultilingualDocumentProcessor",
    "DocumentProcessor",  # Alias
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
    "chunk_multilingual_text",
    
    # 🔧 Infrastructure
    "SERVICES",
    
    # 📝 Cypher Templates
    "INTENT_CREATE",
    "PHASE_LINK", 
    "RAG_CHUNK_ADD"
]

# Package configuration
SUPPORTED_LANGUAGES = [
    "en", "uk", "ru", "zh", "es", "fr", "de", "ja", "ko", "ar",
    "pt", "it", "nl", "pl", "cs", "da", "sv", "no", "fi", "hu"
]

FEATURES = {
    "multilingual_processing": True,
    "vector_search": True,
    "graph_database": True,
    "embedding_cache": True,
    "async_support": True,
    "enterprise_ready": True
}

# Quick start helpers
def quick_start():
    """
    🚀 Quick start guide for ISKALA MOVA
    
    Example usage:
    ```python
    import iskala_graph
    
    # Initialize services
    processor = iskala_graph.DocumentProcessor()
    embedding_service = iskala_graph.EmbeddingService()
    graph_db = iskala_graph.GraphDB()
    
    # Process multilingual document
    chunks = await processor.process_file("document.pdf")
    
    # Generate embeddings
    for chunk in chunks:
        embedding = await embedding_service.get_embedding(chunk.content)
        await graph_db.save_chunk_with_embedding(chunk, embedding)
    ```
    """
    return {
        "version": __version__,
        "supported_languages": len(SUPPORTED_LANGUAGES),
        "features": FEATURES,
        "quick_example": quick_start.__doc__
    }

# Module initialization
def initialize():
    """Initialize ISKALA MOVA package"""
    import logging
    
    # Setup logging
    logging.getLogger("iskala_graph").setLevel(logging.INFO)
    
    # Package banner
    print(f"""
🌍 ISKALA MOVA v{__version__} - Multilingual AI Graph Infrastructure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Neo4j Graph Database ready
✅ Embedding Service with Redis cache ready  
✅ Multilingual Processor ({len(SUPPORTED_LANGUAGES)} languages) ready
✅ Enterprise features enabled
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Use iskala_graph.quick_start() for examples
📖 Documentation: https://github.com/Leryk1981/ISKALA_MOVA
    """)

# Auto-initialize when imported
if __name__ != "__main__":
    initialize() 