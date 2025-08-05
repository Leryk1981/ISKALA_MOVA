#!/usr/bin/env python3
"""
Memory Models for ISKALA
Pydantic models for memory search and graph operations
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum


class SearchStrategy(str, Enum):
    """Search strategy options"""
    VECTOR_ONLY = "vector_only"
    GRAPH_ONLY = "graph_only"
    HYBRID = "hybrid"
    INTENT_MATCH = "intent_match"


class MemoryPhase(str, Enum):
    """Memory phase categories"""
    INPUT = "input"
    PROCESSING = "processing"
    OUTPUT = "output"
    REFLECTION = "reflection"
    DECISION = "decision"


class SearchRequest(BaseModel):
    """Request model for memory search"""
    query: str = Field(min_length=1, max_length=1000, description="Search query")
    language: Optional[str] = Field(default="auto", description="Query language hint")
    strategy: SearchStrategy = SearchStrategy.HYBRID
    intent_filter: Optional[str] = Field(default=None, description="Intent category filter")
    phase_filter: Optional[MemoryPhase] = Field(default=None, description="Memory phase filter")
    k: int = Field(default=5, ge=1, le=100, description="Number of results to return")
    min_similarity: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum similarity threshold")
    include_metadata: bool = Field(default=True, description="Include result metadata")
    use_cache: bool = Field(default=True, description="Use cached results if available")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "як навчити нейронну мережу",
                "language": "uk",
                "strategy": "hybrid",
                "intent_filter": "learning",
                "k": 10,
                "min_similarity": 0.8
            }
        }
    }


class MemoryPattern(BaseModel):
    """Individual memory pattern result"""
    id: str = Field(description="Unique pattern identifier")
    content: str = Field(description="Pattern content/text")
    similarity_score: float = Field(ge=0.0, le=1.0, description="Similarity score")
    graph_centrality: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Graph centrality score")
    intent_match: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Intent matching score")
    combined_score: float = Field(ge=0.0, le=1.0, description="Final combined ranking score")
    
    # Metadata
    phase: Optional[MemoryPhase] = Field(default=None, description="Memory phase")
    language: Optional[str] = Field(default=None, description="Content language")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    tags: List[str] = Field(default_factory=list, description="Associated tags")
    
    # Graph relationships
    connections: List[str] = Field(default_factory=list, description="Connected pattern IDs")
    path_length: Optional[int] = Field(default=None, ge=0, description="Graph path length from query")


class SearchFacets(BaseModel):
    """Search result facets and aggregations"""
    languages: Dict[str, int] = Field(default_factory=dict, description="Language distribution")
    phases: Dict[str, int] = Field(default_factory=dict, description="Phase distribution")
    intents: Dict[str, int] = Field(default_factory=dict, description="Intent distribution")
    tags: Dict[str, int] = Field(default_factory=dict, description="Tag frequency")
    similarity_ranges: Dict[str, int] = Field(default_factory=dict, description="Similarity score ranges")


class SearchResponse(BaseModel):
    """Response model for memory search"""
    patterns: List[MemoryPattern] = Field(description="Found memory patterns")
    total_found: int = Field(ge=0, description="Total patterns found")
    query_processed: str = Field(description="Processed/normalized query")
    strategy_used: SearchStrategy = Field(description="Search strategy applied")
    
    # Performance metrics
    search_time_ms: float = Field(ge=0.0, description="Search execution time in milliseconds")
    cache_hit: bool = Field(default=False, description="Whether result was cached")
    
    # Aggregations
    facets: Optional[SearchFacets] = Field(default=None, description="Search facets")
    
    # Query analysis
    detected_language: Optional[str] = Field(default=None, description="Detected query language")
    extracted_intents: List[str] = Field(default_factory=list, description="Extracted intent categories")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patterns": [
                    {
                        "id": "pattern_123",
                        "content": "Навчання нейронної мережі потребує великих даних",
                        "similarity_score": 0.95,
                        "combined_score": 0.92,
                        "phase": "processing",
                        "language": "uk"
                    }
                ],
                "total_found": 1,
                "query_processed": "навчання нейронної мережі",
                "strategy_used": "hybrid",
                "search_time_ms": 45.2,
                "cache_hit": False
            }
        }
    }


class GraphPath(BaseModel):
    """Graph traversal path result"""
    path_id: str = Field(description="Unique path identifier")
    nodes: List[str] = Field(description="Node IDs in the path")
    relationships: List[str] = Field(description="Relationship types in the path")
    path_length: int = Field(ge=0, description="Path length")
    path_score: float = Field(ge=0.0, le=1.0, description="Path relevance score")
    start_node: str = Field(description="Starting node ID")
    end_node: str = Field(description="Ending node ID")


class GraphTraversalRequest(BaseModel):
    """Request for graph traversal operations"""
    start_patterns: List[str] = Field(description="Starting pattern IDs")
    max_depth: int = Field(default=3, ge=1, le=10, description="Maximum traversal depth")
    relationship_types: Optional[List[str]] = Field(default=None, description="Allowed relationship types")
    min_path_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum path score")
    max_paths: int = Field(default=10, ge=1, le=100, description="Maximum paths to return")


class GraphTraversalResponse(BaseModel):
    """Response for graph traversal operations"""
    paths: List[GraphPath] = Field(description="Found graph paths")
    total_paths: int = Field(ge=0, description="Total paths found")
    traversal_time_ms: float = Field(ge=0.0, description="Traversal time in milliseconds")
    max_depth_reached: int = Field(ge=0, description="Maximum depth actually reached")


class MemoryIndexRequest(BaseModel):
    """Request for indexing new memory content"""
    content: str = Field(min_length=1, max_length=10000, description="Content to index")
    phase: MemoryPhase = Field(description="Memory phase category")
    language: Optional[str] = Field(default="auto", description="Content language")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    connect_to: List[str] = Field(default_factory=list, description="Pattern IDs to connect to")


class MemoryIndexResponse(BaseModel):
    """Response for memory indexing"""
    pattern_id: str = Field(description="Created pattern ID")
    indexed_at: datetime = Field(default_factory=datetime.now)
    connections_created: int = Field(ge=0, description="Number of connections created")
    processing_time_ms: float = Field(ge=0.0, description="Indexing time in milliseconds")


class MemoryHealthResponse(BaseModel):
    """Health status of memory system"""
    status: str = Field(description="System status")
    total_patterns: int = Field(ge=0, description="Total indexed patterns")
    total_connections: int = Field(ge=0, description="Total graph connections")
    languages_supported: List[str] = Field(description="Supported languages")
    
    # Performance metrics
    avg_search_time_ms: float = Field(ge=0.0, description="Average search time")
    cache_hit_ratio: float = Field(ge=0.0, le=1.0, description="Cache hit ratio")
    index_size_mb: float = Field(ge=0.0, description="Index size in MB")
    
    timestamp: datetime = Field(default_factory=datetime.now) 