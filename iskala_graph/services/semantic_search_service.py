"""
🔍 Semantic Search Service for ISKALA MOVA
Advanced hybrid search combining vector similarity and graph traversal
with intelligent ranking, multilingual support, and production optimizations
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from pathlib import Path
import hashlib

import redis.asyncio as redis
from neo4j import AsyncDriver
import numpy as np

from .graph_vector_service import GraphVectorService, SearchResult as VectorSearchResult
from .embedding_service import EmbeddingService
from .neo4j_driver import Neo4jConnection
from .graph_models import Intent, Phase, ContextChunk

logger = logging.getLogger(__name__)

@dataclass
class GraphPath:
    """Path through the knowledge graph"""
    start_node_id: str
    end_node_id: str
    path_nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    path_length: int
    confidence: float = 0.0
    total_weight: float = 0.0
    
    @property
    def path_summary(self) -> str:
        """Human-readable path summary"""
        if not self.path_nodes:
            return "Empty path"
        
        start_type = self.path_nodes[0].get('type', 'Unknown')
        end_type = self.path_nodes[-1].get('type', 'Unknown')
        return f"{start_type} → {end_type} (distance: {self.path_length})"

@dataclass
class SearchResult:
    """Enhanced search result with hybrid scoring"""
    id: str
    content: str
    language: str
    source_doc: str
    
    # Scoring components
    vector_score: float = 0.0
    graph_score: float = 0.0
    intent_score: float = 0.0
    language_score: float = 0.0
    combined_score: float = 0.0
    
    # Result type and metadata
    result_type: str = "hybrid"  # vector, graph, hybrid
    intent_name: Optional[str] = None
    phase_name: Optional[str] = None
    graph_distance: int = 0
    related_intents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.metadata:
            self.metadata = {}

@dataclass
class SearchFacets:
    """Search result facets and aggregations"""
    languages: Dict[str, int] = field(default_factory=dict)
    intents: Dict[str, int] = field(default_factory=dict)
    phases: Dict[str, int] = field(default_factory=dict)
    sources: Dict[str, int] = field(default_factory=dict)
    result_types: Dict[str, int] = field(default_factory=dict)

@dataclass
class PaginatedSearchResponse:
    """Paginated search response with facets"""
    results: List[SearchResult]
    total_count: int
    page: int
    size: int
    facets: SearchFacets
    query_time_ms: float
    cache_hit: bool = False

class SemanticSearchService:
    """
    🧠 Advanced Semantic Search Service
    
    Provides hybrid search combining:
    - Vector similarity search (embeddings)
    - Graph traversal (knowledge connections)
    - Intelligent re-ranking algorithms
    - Multi-language support
    - Caching and performance optimization
    
    Search strategies:
    1. Vector-only: Pure embedding similarity
    2. Graph-only: Knowledge graph traversal
    3. Hybrid: Combined vector + graph with re-ranking
    """
    
    def __init__(
        self,
        vector_service: GraphVectorService,
        neo4j_connection: Neo4jConnection,
        embedding_service: EmbeddingService,
        redis_client: Optional[redis.Redis] = None
    ):
        self.vector_service = vector_service
        self.neo4j = neo4j_connection
        self.embedding_service = embedding_service
        self.redis = redis_client
        
        # Ranking weights (configurable)
        self.ranking_weights = {
            "vector_similarity": 0.40,
            "graph_centrality": 0.30,
            "intent_match": 0.20,
            "language_confidence": 0.10
        }
        
        # Performance metrics
        self.search_stats = {
            "total_searches": 0,
            "cache_hits": 0,
            "avg_search_time": 0.0,
            "hybrid_searches": 0,
            "vector_only_searches": 0,
            "graph_only_searches": 0
        }
        
        logger.info("🔍 SemanticSearchService initialized with hybrid search capabilities")

    async def hybrid_search(
        self,
        query: str,
        language: Optional[str] = None,
        intent_filter: Optional[str] = None,
        phase_filter: Optional[str] = None,
        k: int = 5,
        use_cache: bool = True
    ) -> List[SearchResult]:
        """
        🎯 Hybrid search combining vector similarity and graph traversal
        
        Strategy:
        1. Vector search for semantic similarity
        2. Graph search for connected knowledge
        3. Intelligent re-ranking
        4. Result aggregation and deduplication
        
        Args:
            query: Search query text
            language: Language filter (uk, en, zh, etc.)
            intent_filter: Filter by specific intent
            phase_filter: Filter by thinking phase
            k: Number of results to return
            use_cache: Whether to use Redis caching
            
        Returns:
            List of ranked SearchResult objects
        """
        start_time = time.time()
        
        try:
            # Check cache first
            if use_cache and self.redis:
                cached_results = await self._get_cached_results(
                    query, language, intent_filter, phase_filter, k
                )
                if cached_results:
                    self.search_stats["cache_hits"] += 1
                    logger.info(f"🔍 Cache hit for query: '{query[:30]}...'")
                    return cached_results
            
            logger.info(f"🔍 Hybrid search: '{query[:50]}...' (lang={language}, intent={intent_filter})")
            
            # Run vector and graph searches in parallel
            vector_task = self._vector_search(query, language, k * 2)  # Get more for re-ranking
            graph_task = self._graph_search(query, intent_filter, phase_filter, k * 2)
            
            vector_results, graph_results = await asyncio.gather(
                vector_task, graph_task, return_exceptions=True
            )
            
            # Handle potential exceptions
            if isinstance(vector_results, Exception):
                logger.error(f"Vector search failed: {vector_results}")
                vector_results = []
            if isinstance(graph_results, Exception):
                logger.error(f"Graph search failed: {graph_results}")
                graph_results = []
            
            # Combine and rank results
            combined_results = await self._combine_and_rank_results(
                vector_results, graph_results, query, intent_filter, k
            )
            
            # Cache results
            if use_cache and self.redis and combined_results:
                await self._cache_results(
                    query, language, intent_filter, phase_filter, k, combined_results
                )
            
            # Update statistics
            search_time = time.time() - start_time
            self._update_search_stats("hybrid", search_time)
            
            logger.info(f"✅ Hybrid search completed: {len(combined_results)} results in {search_time:.3f}s")
            return combined_results
            
        except Exception as e:
            logger.error(f"❌ Hybrid search failed: {e}")
            return []

    async def _vector_search(
        self,
        query: str,
        language: Optional[str],
        k: int
    ) -> List[VectorSearchResult]:
        """Execute vector similarity search"""
        try:
            return await self.vector_service.similarity_search(
                query=query,
                language_filter=language,
                k=k,
                confidence_threshold=0.3  # Filter low-confidence results
            )
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    async def _graph_search(
        self,
        query: str,
        intent_filter: Optional[str],
        phase_filter: Optional[str],
        k: int
    ) -> List[Dict[str, Any]]:
        """Execute graph-based search using knowledge connections"""
        try:
            # Build graph search query
            cypher_query = """
            // Find intent nodes matching query keywords
            CALL db.index.fulltext.queryNodes('chunk_content_idx', $query) 
            YIELD node, score
            WHERE node:ContextChunk
            AND ($language IS NULL OR node.language = $language)
            
            // Follow graph connections
            OPTIONAL MATCH (node)-[:DETAILS]->(intent:Intent)
            WHERE ($intent_filter IS NULL OR intent.name = $intent_filter)
            
            OPTIONAL MATCH (intent)-[:LEADS_TO]->(next_intent:Intent)-[:DETAILS]<-(related:ContextChunk)
            
            // Collect results with graph metadata
            WITH node, score, intent, related,
                 CASE WHEN related IS NOT NULL THEN score * 0.8 ELSE score END as graph_score
            
            RETURN DISTINCT
                COALESCE(related, node) as result_node,
                graph_score,
                intent.name as intent_name,
                CASE WHEN related IS NOT NULL THEN 2 ELSE 1 END as graph_distance
            ORDER BY graph_score DESC
            LIMIT $k
            """
            
            # Extract keywords from query for full-text search
            query_keywords = self._extract_keywords(query)
            fulltext_query = " OR ".join(query_keywords) if query_keywords else query
            
            params = {
                "query": fulltext_query,
                "intent_filter": intent_filter,
                "k": k
            }
            
            result = await self.neo4j.execute_query(cypher_query, **params)
            records = await result.data()
            
            # Convert to standardized format
            graph_results = []
            for record in records:
                node = record['result_node']
                graph_result = {
                    "id": node.get('chunk_hash', ''),
                    "content": node.get('content', ''),
                    "language": node.get('language', ''),
                    "source_doc": node.get('source_doc', ''),
                    "score": record['graph_score'],
                    "intent_name": record.get('intent_name'),
                    "graph_distance": record['graph_distance'],
                    "result_type": "graph"
                }
                graph_results.append(graph_result)
            
            return graph_results
            
        except Exception as e:
            logger.error(f"Graph search error: {e}")
            return []

    async def _combine_and_rank_results(
        self,
        vector_results: List[VectorSearchResult],
        graph_results: List[Dict[str, Any]],
        query: str,
        intent_filter: Optional[str],
        k: int
    ) -> List[SearchResult]:
        """Combine vector and graph results with intelligent re-ranking"""
        try:
            combined_results = {}  # Use dict to deduplicate by ID
            
            # Process vector results
            for vr in vector_results:
                search_result = SearchResult(
                    id=vr.chunk_hash,
                    content=vr.content,
                    language=vr.language,
                    source_doc=vr.source_doc,
                    vector_score=vr.score,
                    result_type="vector",
                    intent_name=vr.intent_name,
                    metadata=vr.metadata
                )
                combined_results[vr.chunk_hash] = search_result
            
            # Process graph results and merge with vector results
            for gr in graph_results:
                result_id = gr['id']
                if result_id in combined_results:
                    # Merge with existing vector result
                    result = combined_results[result_id]
                    result.graph_score = gr['score']
                    result.graph_distance = gr['graph_distance']
                    result.result_type = "hybrid"
                else:
                    # Create new graph-only result  
                    search_result = SearchResult(
                        id=result_id,
                        content=gr['content'],
                        language=gr['language'],
                        source_doc=gr['source_doc'],
                        graph_score=gr['score'],
                        result_type="graph",
                        intent_name=gr.get('intent_name'),
                        graph_distance=gr['graph_distance']
                    )
                    combined_results[result_id] = search_result
            
            # Calculate combined scores and apply ranking
            for result in combined_results.values():
                result.combined_score = self._calculate_combined_score(
                    result, query, intent_filter
                )
            
            # Sort by combined score and return top k
            ranked_results = sorted(
                combined_results.values(),
                key=lambda x: x.combined_score,
                reverse=True
            )
            
            return ranked_results[:k]
            
        except Exception as e:
            logger.error(f"Result combination error: {e}")
            return []

    def _calculate_combined_score(
        self,
        result: SearchResult,
        query: str,
        intent_filter: Optional[str]
    ) -> float:
        """Calculate combined score using weighted ranking algorithm"""
        try:
            # Vector similarity component
            vector_component = result.vector_score * self.ranking_weights["vector_similarity"]
            
            # Graph centrality component (based on graph distance and connections)
            graph_component = 0.0
            if result.graph_score > 0:
                # Inverse distance weighting: closer nodes score higher
                distance_weight = 1.0 / max(result.graph_distance, 1)
                graph_component = (result.graph_score * distance_weight) * self.ranking_weights["graph_centrality"]
            
            # Intent matching component
            intent_component = 0.0
            if intent_filter and result.intent_name == intent_filter:
                intent_component = 1.0 * self.ranking_weights["intent_match"]
            elif result.intent_name:
                intent_component = 0.5 * self.ranking_weights["intent_match"]
            
            # Language confidence component (placeholder - can be enhanced)
            language_component = 0.8 * self.ranking_weights["language_confidence"]
            
            # Combine all components
            combined_score = (
                vector_component + 
                graph_component + 
                intent_component + 
                language_component
            )
            
            return min(combined_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Score calculation error: {e}")
            return 0.0

    async def graph_walk(
        self,
        start_node_id: str,
        max_depth: int = 3,
        intent_filter: Optional[List[str]] = None
    ) -> List[GraphPath]:
        """
        🕸️ Dynamic knowledge graph traversal
        
        Finds meaningful paths through the knowledge graph starting from a given node.
        Useful for exploring related concepts and building context.
        
        Args:
            start_node_id: Starting node (chunk hash)
            max_depth: Maximum path depth
            intent_filter: Filter paths by specific intents
            
        Returns:
            List of GraphPath objects representing meaningful connections
        """
        try:
            logger.info(f"🕸️ Graph walk from {start_node_id} (depth={max_depth})")
            
            cypher_query = """
            MATCH (start:ContextChunk {chunk_hash: $start_id})
            
            // Find paths of varying lengths
            CALL {
                WITH start
                MATCH path = (start)-[:DETAILS|LEADS_TO|SIMILAR_TO*1..{max_depth}]-(end)
                WHERE start <> end
                AND ($intent_filter IS NULL OR 
                     ANY(intent IN $intent_filter WHERE 
                         (start)-[:DETAILS]->(:Intent {name: intent}) OR
                         (end)-[:DETAILS]->(:Intent {name: intent})))
                RETURN path, length(path) as path_length
                ORDER BY path_length ASC
                LIMIT 20
            }
            
            // Extract path information
            WITH path, path_length,
                 [node in nodes(path) | {
                     id: COALESCE(node.chunk_hash, node.name, toString(id(node))),
                     type: head(labels(node)),
                     content: COALESCE(node.content, node.name, node.description)
                 }] as path_nodes,
                 [rel in relationships(path) | {
                     type: type(rel),
                     properties: properties(rel)
                 }] as relationships
            
            RETURN 
                path_nodes,
                relationships,
                path_length,
                // Calculate path confidence based on relationship strengths
                reduce(confidence = 1.0, rel in relationships(path) | 
                    confidence * COALESCE(rel.confidence, 0.8)) as confidence
            ORDER BY confidence DESC, path_length ASC
            """
            
            params = {
                "start_id": start_node_id,
                "max_depth": max_depth,
                "intent_filter": intent_filter
            }
            
            result = await self.neo4j.execute_query(
                cypher_query.format(max_depth=max_depth), **params
            )
            records = await result.data()
            
            # Convert to GraphPath objects
            paths = []
            for record in records:
                path_nodes = record['path_nodes']
                if not path_nodes:
                    continue
                
                graph_path = GraphPath(
                    start_node_id=start_node_id,
                    end_node_id=path_nodes[-1]['id'],
                    path_nodes=path_nodes,
                    relationships=record['relationships'],
                    path_length=record['path_length'],
                    confidence=record['confidence']
                )
                paths.append(graph_path)
            
            logger.info(f"✅ Found {len(paths)} meaningful paths from {start_node_id}")
            return paths
            
        except Exception as e:
            logger.error(f"❌ Graph walk failed: {e}")
            return []

    async def get_search_suggestions(
        self,
        partial_query: str,
        language: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """
        💡 Generate search suggestions based on partial query
        
        Uses Intent and frequently searched terms to provide autocomplete suggestions.
        """
        try:
            # Search in Intent names and descriptions
            cypher_query = """
            MATCH (i:Intent)
            WHERE ($language IS NULL OR i.lang = $language)
            AND (i.name CONTAINS $query OR i.description CONTAINS $query)
            
            UNION
            
            // Search in chunk content for common phrases
            MATCH (c:ContextChunk)
            WHERE ($language IS NULL OR c.language = $language)
            AND c.content CONTAINS $query
            
            WITH DISTINCT 
                CASE 
                    WHEN i.name IS NOT NULL THEN i.name
                    ELSE substring(c.content, 0, 50)
                END as suggestion
            
            RETURN suggestion
            ORDER BY length(suggestion) ASC
            LIMIT $limit
            """
            
            params = {
                "query": partial_query.lower(),
                "language": language,
                "limit": limit
            }
            
            result = await self.neo4j.execute_query(cypher_query, **params)
            records = await result.data()
            
            suggestions = [record['suggestion'] for record in records]
            return suggestions
            
        except Exception as e:
            logger.error(f"Suggestion generation error: {e}")
            return []

    async def get_search_facets(
        self,
        query: str,
        language: Optional[str] = None
    ) -> SearchFacets:
        """
        📊 Generate search facets for filtering
        
        Provides aggregated statistics about search results for building
        filtering UI components.
        """
        try:
            cypher_query = """
            // Get language distribution
            MATCH (c:ContextChunk)
            WHERE ($language IS NULL OR c.language = $language)
            AND c.content CONTAINS $query
            
            WITH c
            OPTIONAL MATCH (c)-[:DETAILS]->(i:Intent)
            OPTIONAL MATCH (i)-[:LEADS_TO]->(p:Phase)
            
            RETURN 
                c.language as language,
                c.source_doc as source,
                i.name as intent,
                p.name as phase,
                count(*) as count
            """
            
            params = {"query": query.lower(), "language": language}
            
            result = await self.neo4j.execute_query(cypher_query, **params)
            records = await result.data()
            
            facets = SearchFacets()
            for record in records:
                count = record['count']
                
                if record['language']:
                    facets.languages[record['language']] = facets.languages.get(
                        record['language'], 0
                    ) + count
                
                if record['intent']:
                    facets.intents[record['intent']] = facets.intents.get(
                        record['intent'], 0
                    ) + count
                
                if record['phase']:
                    facets.phases[record['phase']] = facets.phases.get(
                        record['phase'], 0
                    ) + count
                
                if record['source']:
                    facets.sources[record['source']] = facets.sources.get(
                        record['source'], 0
                    ) + count
            
            return facets
            
        except Exception as e:
            logger.error(f"Facet generation error: {e}")
            return SearchFacets()

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query for full-text search"""
        # Simple keyword extraction - can be enhanced with NLP
        import re
        
        # Remove common stop words (basic version)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'це', 'в', 'на', 'з', 'до', 'від', 'для', 'як', 'що', 'і', 'та', 'або'
        }
        
        # Extract words (3+ characters, not stop words)
        words = re.findall(r'\b\w{3,}\b', query.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return keywords[:5]  # Limit to 5 keywords

    async def _get_cached_results(
        self,
        query: str,
        language: Optional[str],
        intent_filter: Optional[str],
        phase_filter: Optional[str],
        k: int
    ) -> Optional[List[SearchResult]]:
        """Get cached search results from Redis"""
        if not self.redis:
            return None
        
        try:
            cache_key = self._generate_cache_key(query, language, intent_filter, phase_filter, k)
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                # Deserialize results
                data = json.loads(cached_data)
                results = []
                for item in data:
                    result = SearchResult(**item)
                    results.append(result)
                return results
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    async def _cache_results(
        self,
        query: str,
        language: Optional[str],
        intent_filter: Optional[str],
        phase_filter: Optional[str],
        k: int,
        results: List[SearchResult]
    ):
        """Cache search results in Redis"""
        if not self.redis:
            return
        
        try:
            cache_key = self._generate_cache_key(query, language, intent_filter, phase_filter, k)
            
            # Serialize results (convert dataclass to dict)
            data = []
            for result in results:
                result_dict = {
                    "id": result.id,
                    "content": result.content,
                    "language": result.language,
                    "source_doc": result.source_doc,
                    "vector_score": result.vector_score,
                    "graph_score": result.graph_score,
                    "intent_score": result.intent_score,
                    "language_score": result.language_score,
                    "combined_score": result.combined_score,
                    "result_type": result.result_type,
                    "intent_name": result.intent_name,
                    "phase_name": result.phase_name,
                    "graph_distance": result.graph_distance,
                    "related_intents": result.related_intents,
                    "metadata": result.metadata
                }
                data.append(result_dict)
            
            # Cache for 5 minutes
            await self.redis.setex(
                cache_key,
                300,  # 5 minutes TTL
                json.dumps(data, ensure_ascii=False)
            )
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    def _generate_cache_key(
        self,
        query: str,
        language: Optional[str],
        intent_filter: Optional[str],
        phase_filter: Optional[str],
        k: int
    ) -> str:
        """Generate cache key for search parameters"""
        key_data = f"{query}:{language}:{intent_filter}:{phase_filter}:{k}"
        return f"search:{hashlib.md5(key_data.encode()).hexdigest()}"

    def _update_search_stats(self, search_type: str, search_time: float):
        """Update search performance statistics"""
        self.search_stats["total_searches"] += 1
        
        if search_type == "hybrid":
            self.search_stats["hybrid_searches"] += 1
        elif search_type == "vector":
            self.search_stats["vector_only_searches"] += 1
        elif search_type == "graph":
            self.search_stats["graph_only_searches"] += 1
        
        # Update average search time
        total = self.search_stats["total_searches"]
        current_avg = self.search_stats["avg_search_time"]
        self.search_stats["avg_search_time"] = (current_avg * (total - 1) + search_time) / total

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        stats = self.search_stats.copy()
        
        # Add cache statistics if Redis is available
        if self.redis:
            try:
                info = await self.redis.info('stats')
                stats["cache_stats"] = {
                    "keyspace_hits": info.get('keyspace_hits', 0),
                    "keyspace_misses": info.get('keyspace_misses', 0),
                    "hit_rate": (info.get('keyspace_hits', 0) / 
                               max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1))
                }
            except Exception as e:
                logger.error(f"Redis stats error: {e}")
        
        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for semantic search"""
        health = {
            "service": "SemanticSearchService",
            "status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Check vector service
            vector_health = await self.vector_service.health_check()
            health["components"]["vector_service"] = vector_health
            
            # Check Neo4j connectivity
            neo4j_healthy = await self.neo4j.verify_connectivity()
            health["components"]["neo4j"] = {
                "status": "healthy" if neo4j_healthy else "unhealthy"
            }
            
            # Check Redis connectivity (if available)
            if self.redis:
                try:
                    await self.redis.ping()
                    health["components"]["redis"] = {"status": "healthy"}
                except:
                    health["components"]["redis"] = {"status": "unhealthy"}
            else:
                health["components"]["redis"] = {"status": "not_configured"}
            
            # Overall health
            unhealthy_components = [
                comp for comp in health["components"].values()
                if comp.get("status") not in ["healthy", "not_configured"]
            ]
            
            if unhealthy_components:
                health["status"] = "degraded"
            
            return health
            
        except Exception as e:
            health["status"] = "unhealthy"
            health["error"] = str(e)
            return health

    async def close(self):
        """Cleanup resources"""
        try:
            if self.redis:
                await self.redis.close()
            logger.info("✅ SemanticSearchService closed")
        except Exception as e:
            logger.error(f"❌ SemanticSearchService close error: {e}")

# Convenience functions for easy usage
async def create_semantic_search_service(
    vector_service: GraphVectorService = None,
    redis_url: str = "redis://localhost:6379"
) -> SemanticSearchService:
    """Create and initialize SemanticSearchService with default settings"""
    from .graph_vector_service import create_graph_vector_service
    
    # Create vector service if not provided
    if not vector_service:
        vector_service = await create_graph_vector_service()
    
    # Create Redis client
    redis_client = None
    try:
        redis_client = redis.from_url(redis_url)
        await redis_client.ping()  # Test connection
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without cache.")
        redis_client = None
    
    # Create service
    service = SemanticSearchService(
        vector_service=vector_service,
        neo4j_connection=vector_service.neo4j,
        embedding_service=vector_service.embedding_service,
        redis_client=redis_client
    )
    
    return service 