"""
🧠 Graph Vector Integration Service for ISKALA MOVA
Enterprise-grade service for seamless integration of:
- MultilingualDocumentProcessor (chunking)
- EmbeddingService (vectors)  
- Neo4j (graph storage + vector search)
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path

import neo4j
from neo4j import AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from .document_processor import MultilingualDocumentProcessor, DocChunk
from .embedding_service import EmbeddingService
from .neo4j_driver import Neo4jConnection
from .graph_models import ContextChunk, Intent, BaseNode

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Vector search result with metadata"""
    content: str
    language: str
    chunk_hash: str
    source_doc: str
    score: float
    intent_name: Optional[str] = None
    position: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class IndexingResult:
    """Result of document indexing operation"""
    success: bool
    document_name: str
    chunks_created: int
    chunks_indexed: int
    processing_time: float
    language_detected: str
    error_message: Optional[str] = None

class GraphVectorService:
    """
    🌍 Enterprise Graph Vector Integration Service
    
    Provides seamless integration between:
    - Document processing (multilingual chunking)
    - Embedding generation (cached vectors)
    - Graph storage (Neo4j + vector search)
    
    Features:
    - Transactional chunk storage
    - Batch processing optimization
    - Multilingual search support
    - Performance monitoring
    - Error resilience
    """
    
    def __init__(
        self,
        neo4j_connection: Neo4jConnection,
        embedding_service: EmbeddingService,
        document_processor: Optional[MultilingualDocumentProcessor] = None
    ):
        self.neo4j = neo4j_connection
        self.embedding_service = embedding_service
        self.document_processor = document_processor or MultilingualDocumentProcessor()
        
        # Performance metrics
        self.stats = {
            "documents_processed": 0,
            "chunks_stored": 0,
            "searches_performed": 0,
            "avg_search_latency": 0.0,
            "avg_indexing_latency": 0.0,
            "cache_hit_rate": 0.0
        }
        
        # Search latency tracking
        self._search_times = []
        self._indexing_times = []
        
        logger.info("🧠 GraphVectorService initialized")

    async def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize Neo4j connection
            await self.neo4j.initialize()
            if not await self.neo4j.verify_connectivity():
                raise ConnectionError("Neo4j connection failed")
            
            # Initialize embedding service
            await self.embedding_service.initialize()
            
            # Verify vector schema exists
            await self._verify_vector_schema()
            
            logger.info("✅ GraphVectorService fully initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ GraphVectorService initialization failed: {e}")
            return False

    async def _verify_vector_schema(self) -> bool:
        """Verify that vector indexes exist in Neo4j"""
        try:
            query = """
            CALL db.indexes() YIELD name, type, state
            WHERE name = 'chunk_embedding_idx' AND type = 'VECTOR' AND state = 'ONLINE'
            RETURN count(*) as index_count
            """
            
            result = await self.neo4j.execute_query(query)
            records = await result.data()
            
            if records and records[0]['index_count'] > 0:
                logger.info("✅ Vector index 'chunk_embedding_idx' verified")
                return True
            else:
                logger.warning("⚠️ Vector index 'chunk_embedding_idx' not found or offline")
                return False
                
        except Exception as e:
            logger.error(f"❌ Vector schema verification failed: {e}")
            return False

    async def process_and_index_document(
        self, 
        file_path: Path, 
        source_language: str = "auto"
    ) -> IndexingResult:
        """
        Complete pipeline: Document → Chunks → Embeddings → Neo4j
        
        Args:
            file_path: Path to document file
            source_language: Language hint or "auto" for detection
            
        Returns:
            IndexingResult with processing statistics
        """
        start_time = time.time()
        document_name = file_path.name
        
        try:
            logger.info(f"📄 Processing document: {document_name}")
            
            # Step 1: Process document into chunks
            chunks = await self.document_processor.process_file(file_path)
            if not chunks:
                return IndexingResult(
                    success=False,
                    document_name=document_name,
                    chunks_created=0,
                    chunks_indexed=0,
                    processing_time=time.time() - start_time,
                    language_detected="unknown",
                    error_message="No chunks created from document"
                )
            
            # Step 2: Store chunks with embeddings
            indexed_count = await self.store_document_chunks(chunks)
            
            processing_time = time.time() - start_time
            detected_language = chunks[0].language if chunks else "unknown"
            
            # Update stats
            self.stats["documents_processed"] += 1
            self.stats["chunks_stored"] += indexed_count
            self._indexing_times.append(processing_time)
            self._update_avg_indexing_time()
            
            logger.info(f"✅ Document processed: {document_name} → {len(chunks)} chunks → {indexed_count} indexed")
            
            return IndexingResult(
                success=True,
                document_name=document_name,
                chunks_created=len(chunks),
                chunks_indexed=indexed_count,
                processing_time=processing_time,
                language_detected=detected_language
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Document processing failed: {document_name}: {e}")
            
            return IndexingResult(
                success=False,
                document_name=document_name,
                chunks_created=0,
                chunks_indexed=0,
                processing_time=processing_time,
                language_detected="error",
                error_message=str(e)
            )

    async def store_document_chunks(self, chunks: List[DocChunk]) -> int:
        """
        Store document chunks with embeddings in Neo4j
        
        Args:
            chunks: List of processed document chunks
            
        Returns:
            Number of successfully stored chunks
        """
        if not chunks:
            return 0
        
        try:
            # Step 1: Generate embeddings for all chunks (batch processing)
            logger.info(f"🧠 Generating embeddings for {len(chunks)} chunks")
            contents = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_service.get_embeddings_batch(contents)
            
            if len(embeddings) != len(chunks):
                raise ValueError(f"Embedding count mismatch: {len(embeddings)} != {len(chunks)}")
            
            # Step 2: Prepare chunk data for Neo4j
            chunk_data = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_record = {
                    "chunk_hash": chunk.chunk_hash,
                    "content": chunk.content,
                    "language": chunk.language,
                    "source_doc": chunk.source_doc,
                    "position": chunk.position,
                    "confidence": chunk.confidence,
                    "embedding": embedding,
                    "metadata": chunk.metadata,
                    "word_count": chunk.word_count,
                    "sentence_count": chunk.sentence_count,
                    "created_at": chunk.created_at or datetime.utcnow().isoformat()
                }
                chunk_data.append(chunk_record)
            
            # Step 3: Transactional storage in Neo4j
            stored_count = await self._store_chunks_transaction(chunk_data)
            
            logger.info(f"✅ Stored {stored_count}/{len(chunks)} chunks in Neo4j")
            return stored_count
            
        except Exception as e:
            logger.error(f"❌ Chunk storage failed: {e}")
            return 0

    async def _store_chunks_transaction(self, chunk_data: List[Dict[str, Any]]) -> int:
        """Store chunks in Neo4j using transaction for atomicity"""
        try:
            query = """
            UNWIND $chunks AS chunk
            
            // Create or update ContextChunk node
            MERGE (c:ContextChunk {chunk_hash: chunk.chunk_hash})
            SET c.content = chunk.content,
                c.language = chunk.language,
                c.source_doc = chunk.source_doc,
                c.position = chunk.position,
                c.confidence = chunk.confidence,
                c.embedding = chunk.embedding,
                c.metadata = chunk.metadata,
                c.word_count = chunk.word_count,
                c.sentence_count = chunk.sentence_count,
                c.created_at = chunk.created_at,
                c.updated_at = datetime()
            
            // Optional: Link to Intent if mentioned in metadata
            WITH c, chunk
            FOREACH (intent_name IN CASE 
                WHEN chunk.metadata.intent_name IS NOT NULL 
                THEN [chunk.metadata.intent_name] 
                ELSE [] 
            END |
                MERGE (i:Intent {name: intent_name})
                ON CREATE SET i.created_at = datetime()
                MERGE (c)-[:DETAILS]->(i)
            )
            
            // Optional: Link to source document node
            WITH c, chunk
            MERGE (doc:Document {name: chunk.source_doc})
            ON CREATE SET doc.created_at = datetime()
            MERGE (c)-[:PART_OF]->(doc)
            
            RETURN c.chunk_hash
            """
            
            result = await self.neo4j.execute_query(query, chunks=chunk_data)
            records = await result.data()
            
            return len(records)
            
        except Exception as e:
            logger.error(f"❌ Neo4j transaction failed: {e}")
            return 0

    async def similarity_search(
        self,
        query: str,
        language_filter: Optional[str] = None,
        k: int = 5,
        confidence_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Semantic similarity search using vector index
        
        Args:
            query: Search query text
            language_filter: Optional language filter ("uk", "en", etc.)
            k: Number of results to return
            confidence_threshold: Minimum confidence score
            
        Returns:
            List of SearchResult objects ordered by similarity
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate query embedding
            logger.info(f"🔍 Semantic search: '{query[:50]}...' (lang={language_filter}, k={k})")
            query_embedding = await self.embedding_service.get_embedding(query)
            
            # Step 2: Vector search in Neo4j
            search_results = await self._vector_search_neo4j(
                query_embedding, 
                language_filter, 
                k, 
                confidence_threshold
            )
            
            # Update performance stats
            search_time = time.time() - start_time
            self.stats["searches_performed"] += 1
            self._search_times.append(search_time)
            self._update_avg_search_time()
            
            logger.info(f"✅ Search completed: {len(search_results)} results in {search_time:.3f}s")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Similarity search failed: {e}")
            return []

    async def _vector_search_neo4j(
        self,
        query_embedding: List[float],
        language_filter: Optional[str],
        k: int,
        confidence_threshold: float
    ) -> List[SearchResult]:
        """Execute vector search query in Neo4j"""
        try:
            # Build Cypher query with optional language filter
            cypher_query = """
            CALL db.index.vector.queryNodes('chunk_embedding_idx', $k, $query_embedding)
            YIELD node, score
            
            // Apply filters
            WHERE score >= $confidence_threshold
              AND ($language_filter IS NULL OR node.language = $language_filter)
            
            // Optional: Get linked Intent information
            OPTIONAL MATCH (node)-[:DETAILS]->(intent:Intent)
            
            RETURN 
                node.content as content,
                node.language as language,
                node.chunk_hash as chunk_hash,
                node.source_doc as source_doc,
                node.position as position,
                node.metadata as metadata,
                intent.name as intent_name,
                score
            ORDER BY score DESC
            LIMIT $k
            """
            
            params = {
                "k": k * 2,  # Request more results to account for filtering
                "query_embedding": query_embedding,
                "language_filter": language_filter,
                "confidence_threshold": confidence_threshold
            }
            
            result = await self.neo4j.execute_query(cypher_query, **params)
            records = await result.data()
            
            # Convert to SearchResult objects
            search_results = []
            for record in records[:k]:  # Limit to requested count
                search_result = SearchResult(
                    content=record['content'],
                    language=record['language'],
                    chunk_hash=record['chunk_hash'],
                    source_doc=record['source_doc'],
                    score=record['score'],
                    intent_name=record.get('intent_name'),
                    position=record.get('position', 0),
                    metadata=record.get('metadata', {})
                )
                search_results.append(search_result)
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ Neo4j vector search failed: {e}")
            return []

    async def get_chunk_by_hash(self, chunk_hash: str) -> Optional[SearchResult]:
        """Retrieve specific chunk by hash"""
        try:
            query = """
            MATCH (c:ContextChunk {chunk_hash: $chunk_hash})
            OPTIONAL MATCH (c)-[:DETAILS]->(intent:Intent)
            RETURN 
                c.content as content,
                c.language as language,
                c.chunk_hash as chunk_hash,
                c.source_doc as source_doc,
                c.position as position,
                c.confidence as score,
                c.metadata as metadata,
                intent.name as intent_name
            """
            
            result = await self.neo4j.execute_query(query, chunk_hash=chunk_hash)
            records = await result.data()
            
            if records:
                record = records[0]
                return SearchResult(
                    content=record['content'],
                    language=record['language'],
                    chunk_hash=record['chunk_hash'],
                    source_doc=record['source_doc'],
                    score=record['score'],
                    intent_name=record.get('intent_name'),
                    position=record.get('position', 0),
                    metadata=record.get('metadata', {})
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Chunk retrieval failed for {chunk_hash}: {e}")
            return None

    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        try:
            # Neo4j statistics
            neo4j_stats = await self._get_neo4j_stats()
            
            # Embedding service statistics
            embedding_stats = await self.embedding_service.get_stats()
            
            # Combined statistics
            return {
                "service_stats": self.stats.copy(),
                "neo4j_stats": neo4j_stats,
                "embedding_stats": embedding_stats,
                "performance": {
                    "avg_search_latency_ms": self.stats["avg_search_latency"] * 1000,
                    "avg_indexing_latency_ms": self.stats["avg_indexing_latency"] * 1000,
                    "total_searches": self.stats["searches_performed"],
                    "total_documents": self.stats["documents_processed"]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Statistics collection failed: {e}")
            return {"error": str(e)}

    async def _get_neo4j_stats(self) -> Dict[str, Any]:
        """Get Neo4j-specific statistics"""
        try:
            queries = {
                "total_chunks": "MATCH (c:ContextChunk) RETURN count(c) as count",
                "language_distribution": """
                    MATCH (c:ContextChunk) 
                    RETURN c.language as language, count(*) as count 
                    ORDER BY count DESC
                """,
                "document_count": "MATCH (d:Document) RETURN count(d) as count",
                "intent_count": "MATCH (i:Intent) RETURN count(i) as count"
            }
            
            stats = {}
            for stat_name, query in queries.items():
                result = await self.neo4j.execute_query(query)
                records = await result.data()
                
                if stat_name == "language_distribution":
                    stats[stat_name] = {r['language']: r['count'] for r in records}
                else:
                    stats[stat_name] = records[0]['count'] if records else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Neo4j stats collection failed: {e}")
            return {}

    def _update_avg_search_time(self):
        """Update average search time metric"""
        if self._search_times:
            self.stats["avg_search_latency"] = sum(self._search_times) / len(self._search_times)
            # Keep only last 100 measurements
            if len(self._search_times) > 100:
                self._search_times = self._search_times[-100:]

    def _update_avg_indexing_time(self):
        """Update average indexing time metric"""
        if self._indexing_times:
            self.stats["avg_indexing_latency"] = sum(self._indexing_times) / len(self._indexing_times)
            # Keep only last 100 measurements
            if len(self._indexing_times) > 100:
                self._indexing_times = self._indexing_times[-100:]

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health = {
            "service": "GraphVectorService",
            "status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check Neo4j connectivity
            neo4j_healthy = await self.neo4j.verify_connectivity()
            health["components"]["neo4j"] = {
                "status": "healthy" if neo4j_healthy else "unhealthy",
                "vector_index_exists": await self._verify_vector_schema()
            }
            
            # Check embedding service
            embedding_health = await self.embedding_service.health_check()
            health["components"]["embedding_service"] = embedding_health
            
            # Overall health
            if not neo4j_healthy or embedding_health.get("status") != "healthy":
                health["status"] = "degraded"
            
            return health
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
            return health

    async def close(self):
        """Cleanup resources"""
        try:
            await self.neo4j.close()
            await self.embedding_service.close()
            logger.info("✅ GraphVectorService closed")
        except Exception as e:
            logger.error(f"❌ GraphVectorService close error: {e}")

# Convenience functions for easy usage
async def create_graph_vector_service(
    neo4j_uri: str = "bolt://localhost:7687",
    neo4j_user: str = "neo4j", 
    neo4j_password: str = "iskala-neo4j-2024-secure"
) -> GraphVectorService:
    """Create and initialize GraphVectorService with default settings"""
    from .neo4j_driver import Neo4jConfig, Neo4jConnection
    from .embedding_service import EmbeddingService
    
    # Initialize components
    neo4j_config = Neo4jConfig(uri=neo4j_uri, username=neo4j_user, password=neo4j_password)
    neo4j_conn = Neo4jConnection(neo4j_config)
    
    embedding_service = EmbeddingService()
    
    # Create service
    service = GraphVectorService(neo4j_conn, embedding_service)
    
    # Initialize
    if await service.initialize():
        return service
    else:
        raise RuntimeError("Failed to initialize GraphVectorService")

async def quick_search(query: str, language: str = None, k: int = 5) -> List[SearchResult]:
    """Quick semantic search (for testing/demo purposes)"""
    service = await create_graph_vector_service()
    try:
        return await service.similarity_search(query, language, k)
    finally:
        await service.close() 