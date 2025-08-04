"""
ISKALA MOVA Graph Infrastructure
===============================

Neo4j-based знаннєвий граф для української AI системи ISKALA MOVA.

Основні компоненти:
- Neo4j connection pool з retry logic
- Graph models для Intent, Phase, ContextChunk
- RAG integration з vector embeddings
- Cypher templates та query builders
- Health check та моніторинг

Використання:
    from iskala_graph import get_neo4j_connection
    
    conn = await get_neo4j_connection()
    result = await conn.execute_query("RETURN 'Hello Graph' as message")
"""

__version__ = "0.1.0"
__author__ = "ISKALA MOVA Team"

# Основні імпорти
from .services.neo4j_driver import (
    get_neo4j_connection,
    close_neo4j_connection,
    Neo4jConnection,
    Neo4jConfig
)

from .services.graph_models import (
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

from .services.embedding_service import (
    EmbeddingService,
    EmbeddingConfig,
    get_embedding_service,
    close_embedding_service
)

__all__ = [
    # Connection
    "get_neo4j_connection",
    "close_neo4j_connection", 
    "Neo4jConnection",
    "Neo4jConfig",
    
    # Models
    "Intent",
    "Phase",
    "ContextChunk", 
    "User",
    "Session",
    "NodeType",
    "RelationType",
    
    # Query builders
    "GraphQueryBuilder",
    "CypherTemplates",
    
    # Embedding Service
    "EmbeddingService",
    "EmbeddingConfig", 
    "get_embedding_service",
    "close_embedding_service"
] 