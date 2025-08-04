"""
🔍 Advanced Search API Endpoints for ISKALA MOVA
FastAPI routes for hybrid semantic search, graph traversal, and intelligent query processing

Features:
- Hybrid search (vector + graph)
- Graph walk exploration
- Search suggestions and autocomplete
- Faceted search with aggregations
- Performance optimization and caching
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ...services.semantic_search_service import (
    SemanticSearchService,
    SearchResult,
    GraphPath,
    SearchFacets,
    PaginatedSearchResponse,
    create_semantic_search_service
)

logger = logging.getLogger(__name__)

# ============================
# 📋 REQUEST/RESPONSE MODELS
# ============================

class HybridSearchRequest(BaseModel):
    """Advanced hybrid search request"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    language: Optional[str] = Field(None, description="Language filter (uk, en, zh, etc.)")
    intent_filter: Optional[str] = Field(None, description="Filter by specific intent")
    phase_filter: Optional[str] = Field(None, description="Filter by thinking phase")
    k: int = Field(5, ge=1, le=50, description="Number of results to return")
    use_cache: bool = Field(True, description="Enable Redis caching")
    include_facets: bool = Field(False, description="Include search facets in response")
    
    # Advanced search options
    vector_weight: float = Field(0.4, ge=0.0, le=1.0, description="Vector similarity weight")
    graph_weight: float = Field(0.3, ge=0.0, le=1.0, description="Graph centrality weight")
    intent_weight: float = Field(0.2, ge=0.0, le=1.0, description="Intent matching weight")
    language_weight: float = Field(0.1, ge=0.0, le=1.0, description="Language confidence weight")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

class GraphWalkRequest(BaseModel):
    """Graph traversal request"""
    start_node_id: str = Field(..., description="Starting chunk hash or node ID")
    max_depth: int = Field(3, ge=1, le=5, description="Maximum traversal depth")
    intent_filter: Optional[List[str]] = Field(None, description="Filter paths by intents")
    include_confidence: bool = Field(True, description="Include confidence scores")

class SuggestionsRequest(BaseModel):
    """Search suggestions request"""
    partial_query: str = Field(..., min_length=1, max_length=100, description="Partial search query")
    language: Optional[str] = Field(None, description="Language filter")
    limit: int = Field(10, ge=1, le=20, description="Maximum suggestions count")

class SearchResultResponse(BaseModel):
    """Enhanced search result response"""
    id: str
    content: str
    language: str
    source_doc: str
    
    # Detailed scoring breakdown
    scores: Dict[str, float] = Field(default_factory=dict)
    combined_score: float
    
    # Result metadata
    result_type: str  # vector, graph, hybrid
    intent_name: Optional[str] = None
    phase_name: Optional[str] = None
    graph_distance: int = 0
    related_intents: List[str] = Field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    highlight: Optional[str] = None  # Query highlighting in content

class HybridSearchResponse(BaseModel):
    """Comprehensive hybrid search response"""
    query: str
    results: List[SearchResultResponse]
    total_results: int
    
    # Performance metrics
    search_time_ms: float
    cache_hit: bool = False
    
    # Search strategy breakdown
    vector_results_count: int = 0
    graph_results_count: int = 0
    hybrid_results_count: int = 0
    
    # Optional facets
    facets: Optional[SearchFacets] = None
    
    # Query analysis
    query_analysis: Dict[str, Any] = Field(default_factory=dict)

class GraphPathResponse(BaseModel):
    """Graph path response"""
    start_node_id: str
    end_node_id: str
    path_summary: str
    path_length: int
    confidence: float
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]

class GraphWalkResponse(BaseModel):
    """Graph walk response"""
    start_node_id: str
    paths: List[GraphPathResponse]
    total_paths: int
    max_depth_reached: int
    walk_time_ms: float

class SuggestionsResponse(BaseModel):
    """Search suggestions response"""
    partial_query: str
    suggestions: List[str]
    suggestion_count: int
    generation_time_ms: float

class SearchStatsResponse(BaseModel):
    """Search performance statistics"""
    total_searches: int
    cache_hit_rate: float
    avg_search_time_ms: float
    search_type_distribution: Dict[str, int]
    cache_stats: Optional[Dict[str, Any]] = None

# ============================
# 🔧 DEPENDENCY INJECTION
# ============================

async def get_search_service() -> SemanticSearchService:
    """Dependency injection for SemanticSearchService"""
    try:
        service = await create_semantic_search_service()
        return service
    except Exception as e:
        logger.error(f"❌ Failed to create SemanticSearchService: {e}")
        raise HTTPException(
            status_code=503,
            detail="Semantic search service unavailable"
        )

# ============================
# 🔍 SEARCH API ROUTER
# ============================

router = APIRouter(prefix="/search", tags=["Semantic Search"])

@router.post("/hybrid", response_model=HybridSearchResponse)
async def hybrid_search(
    request: HybridSearchRequest,
    background_tasks: BackgroundTasks,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    🎯 Advanced Hybrid Semantic Search
    
    Combines vector similarity search with knowledge graph traversal for
    intelligent, context-aware search results. Uses machine learning
    embeddings and graph algorithms to find the most relevant content.
    
    Features:
    - Multi-strategy search (vector + graph + intent matching)
    - Configurable ranking weights
    - Redis caching for performance
    - Multilingual support (50+ languages)
    - Search facets and aggregations
    - Query analysis and highlighting
    
    Example:
    ```json
    {
        "query": "як навчити нейронну мережу розпізнавати українську мову",
        "language": "uk",
        "intent_filter": "learning",
        "k": 10,
        "include_facets": true
    }
    ```
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔍 Hybrid search API: '{request.query[:50]}...'")
        
        # Update service ranking weights if provided
        if any([request.vector_weight, request.graph_weight, request.intent_weight, request.language_weight]):
            total_weight = request.vector_weight + request.graph_weight + request.intent_weight + request.language_weight
            if abs(total_weight - 1.0) > 0.01:
                raise HTTPException(
                    status_code=400,
                    detail=f"Ranking weights must sum to 1.0, got {total_weight}"
                )
            
            service.ranking_weights = {
                "vector_similarity": request.vector_weight,
                "graph_centrality": request.graph_weight,
                "intent_match": request.intent_weight,
                "language_confidence": request.language_weight
            }
        
        # Execute hybrid search
        search_results = await service.hybrid_search(
            query=request.query,
            language=request.language,
            intent_filter=request.intent_filter,
            phase_filter=request.phase_filter,
            k=request.k,
            use_cache=request.use_cache
        )
        
        # Get facets if requested
        facets = None
        if request.include_facets:
            facets = await service.get_search_facets(
                query=request.query,
                language=request.language
            )
        
        # Convert results to API format
        api_results = []
        vector_count = graph_count = hybrid_count = 0
        
        for result in search_results:
            # Count result types
            if result.result_type == "vector":
                vector_count += 1
            elif result.result_type == "graph":
                graph_count += 1
            elif result.result_type == "hybrid":
                hybrid_count += 1
            
            # Create API response object
            api_result = SearchResultResponse(
                id=result.id,
                content=result.content,
                language=result.language,
                source_doc=result.source_doc,
                scores={
                    "vector": result.vector_score,
                    "graph": result.graph_score,
                    "intent": result.intent_score,
                    "language": result.language_score
                },
                combined_score=result.combined_score,
                result_type=result.result_type,
                intent_name=result.intent_name,
                phase_name=result.phase_name,
                graph_distance=result.graph_distance,
                related_intents=result.related_intents,
                metadata=result.metadata,
                highlight=_highlight_query_in_content(result.content, request.query)
            )
            api_results.append(api_result)
        
        # Calculate performance metrics
        search_time = (time.time() - start_time) * 1000
        
        # Create response
        response = HybridSearchResponse(
            query=request.query,
            results=api_results,
            total_results=len(api_results),
            search_time_ms=search_time,
            cache_hit=False,  # TODO: Implement cache hit detection
            vector_results_count=vector_count,
            graph_results_count=graph_count,
            hybrid_results_count=hybrid_count,
            facets=facets,
            query_analysis=_analyze_query(request.query)
        )
        
        # Schedule background task for analytics
        background_tasks.add_task(
            _log_search_analytics,
            request.query,
            request.language,
            len(api_results),
            search_time
        )
        
        logger.info(f"✅ Hybrid search completed: {len(api_results)} results in {search_time:.1f}ms")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Hybrid search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        )
    finally:
        await service.close()

@router.post("/graph-walk", response_model=GraphWalkResponse)
async def graph_walk(
    request: GraphWalkRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    🕸️ Knowledge Graph Traversal
    
    Explores connections in the knowledge graph starting from a specific node.
    Useful for understanding relationships between concepts and building
    contextual understanding of topics.
    
    Features:
    - Dynamic graph traversal with configurable depth
    - Intent-based path filtering
    - Confidence scoring for path relevance
    - Multiple traversal strategies
    
    Example:
    ```json
    {
        "start_node_id": "chunk_hash_abc123",
        "max_depth": 3,
        "intent_filter": ["learning", "programming"],
        "include_confidence": true
    }
    ```
    """
    start_time = time.time()
    
    try:
        logger.info(f"🕸️ Graph walk API: from {request.start_node_id} (depth={request.max_depth})")
        
        # Execute graph walk
        paths = await service.graph_walk(
            start_node_id=request.start_node_id,
            max_depth=request.max_depth,
            intent_filter=request.intent_filter
        )
        
        # Convert paths to API format
        api_paths = []
        max_depth_reached = 0
        
        for path in paths:
            api_path = GraphPathResponse(
                start_node_id=path.start_node_id,
                end_node_id=path.end_node_id,
                path_summary=path.path_summary,
                path_length=path.path_length,
                confidence=path.confidence,
                nodes=path.path_nodes,
                relationships=path.relationships
            )
            api_paths.append(api_path)
            max_depth_reached = max(max_depth_reached, path.path_length)
        
        # Calculate performance metrics
        walk_time = (time.time() - start_time) * 1000
        
        response = GraphWalkResponse(
            start_node_id=request.start_node_id,
            paths=api_paths,
            total_paths=len(api_paths),
            max_depth_reached=max_depth_reached,
            walk_time_ms=walk_time
        )
        
        logger.info(f"✅ Graph walk completed: {len(api_paths)} paths in {walk_time:.1f}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Graph walk failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Graph traversal failed: {str(e)}"
        )
    finally:
        await service.close()

@router.post("/suggestions", response_model=SuggestionsResponse)
async def get_search_suggestions(
    request: SuggestionsRequest,
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    💡 Intelligent Search Suggestions
    
    Provides autocomplete suggestions based on partial queries using
    Intent names, common search patterns, and content analysis.
    
    Features:
    - Intent-based suggestions
    - Language-specific filtering
    - Frequency-based ranking
    - Real-time suggestion generation
    
    Example:
    ```json
    {
        "partial_query": "нейрон",
        "language": "uk",
        "limit": 5
    }
    ```
    """
    start_time = time.time()
    
    try:
        logger.info(f"💡 Suggestions API: '{request.partial_query}'")
        
        # Get suggestions
        suggestions = await service.get_search_suggestions(
            partial_query=request.partial_query,
            language=request.language,
            limit=request.limit
        )
        
        # Calculate performance metrics
        generation_time = (time.time() - start_time) * 1000
        
        response = SuggestionsResponse(
            partial_query=request.partial_query,
            suggestions=suggestions,
            suggestion_count=len(suggestions),
            generation_time_ms=generation_time
        )
        
        logger.info(f"✅ Generated {len(suggestions)} suggestions in {generation_time:.1f}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Suggestions generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Suggestions generation failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/facets")
async def get_search_facets(
    query: str = Query(..., description="Search query for facet generation"),
    language: Optional[str] = Query(None, description="Language filter"),
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    📊 Search Facets and Aggregations
    
    Provides aggregated statistics about search results for building
    advanced filtering interfaces and search analytics.
    
    Returns distribution by:
    - Languages
    - Intents
    - Phases
    - Source documents
    - Result types
    """
    try:
        facets = await service.get_search_facets(query=query, language=language)
        return facets
        
    except Exception as e:
        logger.error(f"❌ Facets generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Facets generation failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/stats", response_model=SearchStatsResponse)
async def get_search_statistics(
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    📈 Search Service Performance Statistics
    
    Provides comprehensive performance metrics including:
    - Total search count
    - Cache hit rates
    - Average search times
    - Search type distribution
    - Redis cache statistics
    """
    try:
        stats = await service.get_performance_stats()
        
        response = SearchStatsResponse(
            total_searches=stats["total_searches"],
            cache_hit_rate=stats["cache_hits"] / max(stats["total_searches"], 1),
            avg_search_time_ms=stats["avg_search_time"] * 1000,
            search_type_distribution={
                "hybrid": stats.get("hybrid_searches", 0),
                "vector": stats.get("vector_only_searches", 0),
                "graph": stats.get("graph_only_searches", 0)
            },
            cache_stats=stats.get("cache_stats")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Stats collection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Statistics collection failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/health")
async def search_health_check(
    service: SemanticSearchService = Depends(get_search_service)
):
    """
    💚 Search Service Health Check
    
    Returns comprehensive health status of all search components:
    - SemanticSearchService
    - GraphVectorService
    - Neo4j connectivity
    - Redis cache status
    - Embedding service status
    """
    try:
        health = await service.health_check()
        
        # Determine HTTP status based on service health
        status_code = 200
        if health.get("status") == "unhealthy":
            status_code = 503
        elif health.get("status") == "degraded":
            status_code = 206  # Partial Content
        
        return JSONResponse(content=health, status_code=status_code)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            content={
                "service": "SemanticSearchService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )
    finally:
        await service.close()

# ============================
# 🔧 UTILITY FUNCTIONS
# ============================

def _highlight_query_in_content(content: str, query: str, max_length: int = 200) -> str:
    """Highlight query terms in content snippet"""
    try:
        import re
        
        # Find query position in content
        query_lower = query.lower()
        content_lower = content.lower()
        
        match = re.search(re.escape(query_lower), content_lower)
        if not match:
            # Return snippet from beginning if no match
            return content[:max_length] + ("..." if len(content) > max_length else "")
        
        # Extract snippet around match
        start = max(0, match.start() - 50)
        end = min(len(content), match.end() + 150)
        snippet = content[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
        
    except Exception as e:
        logger.error(f"Highlighting error: {e}")
        return content[:max_length] + ("..." if len(content) > max_length else "")

def _analyze_query(query: str) -> Dict[str, Any]:
    """Analyze query for metadata (language detection, intent classification, etc.)"""
    try:
        import re
        
        analysis = {
            "word_count": len(query.split()),
            "character_count": len(query),
            "has_cyrillic": bool(re.search(r'[а-яё]', query.lower())),
            "has_latin": bool(re.search(r'[a-z]', query.lower())),
            "has_numbers": bool(re.search(r'\d', query)),
            "is_question": query.strip().endswith('?'),
            "query_type": "question" if query.strip().endswith('?') else "statement",
            "estimated_language": "uk" if bool(re.search(r'[а-яё]', query.lower())) else "en"
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Query analysis error: {e}")
        return {}

async def _log_search_analytics(
    query: str,
    language: Optional[str],
    result_count: int,
    search_time_ms: float
):
    """Background task for search analytics logging"""
    try:
        # This could log to analytics database, monitoring system, etc.
        logger.info(f"📊 Search analytics: query='{query[:30]}...', lang={language}, "
                   f"results={result_count}, time={search_time_ms:.1f}ms")
    except Exception as e:
        logger.error(f"Analytics logging error: {e}")

# Export router
__all__ = ["router"] 