#!/usr/bin/env python3
"""
Memory Repository for ISKALA
Data access layer for memory search and graph operations using Neo4j
"""

import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod

import neo4j
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, RoutingControl

from iskala_basis.models.memory_models import (
    SearchRequest,
    SearchResponse,
    MemoryPattern,
    SearchFacets,
    SearchStrategy,
    MemoryPhase,
    GraphPath,
    GraphTraversalRequest,
    GraphTraversalResponse,
    MemoryIndexRequest,
    MemoryIndexResponse
)


# Configure logging
logger = logging.getLogger(__name__)


class MemoryRepositoryInterface(ABC):
    """Abstract interface for memory repository operations"""
    
    @abstractmethod
    async def search_memory_patterns(self, request: SearchRequest) -> SearchResponse:
        """Search for memory patterns using various strategies"""
        pass
    
    @abstractmethod
    async def get_pattern_by_id(self, pattern_id: str) -> Optional[MemoryPattern]:
        """Get specific memory pattern by ID"""
        pass
    
    @abstractmethod
    async def traverse_graph(self, request: GraphTraversalRequest) -> GraphTraversalResponse:
        """Perform graph traversal operations"""
        pass
    
    @abstractmethod
    async def index_memory_content(self, request: MemoryIndexRequest) -> MemoryIndexResponse:
        """Index new memory content"""
        pass
    
    @abstractmethod
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close repository connections"""
        pass


class Neo4jMemoryRepository(MemoryRepositoryInterface):
    """
    Neo4j implementation of memory repository
    
    Handles:
    - Vector similarity search
    - Graph traversal algorithms
    - Hybrid search strategies
    - Memory pattern indexing
    - Performance optimization
    """
    
    def __init__(self, driver: AsyncDriver, database: str = "neo4j"):
        self.driver = driver
        self.database = database
        self.logger = logger
        
        # Performance metrics
        self.search_stats = {
            "total_searches": 0,
            "vector_searches": 0,
            "graph_searches": 0,
            "hybrid_searches": 0,
            "cache_hits": 0,
            "avg_search_time_ms": 0.0
        }
        
        # Search weights for hybrid strategy
        self.ranking_weights = {
            "vector_similarity": 0.40,
            "graph_centrality": 0.30,
            "intent_match": 0.20,
            "language_confidence": 0.10
        }
        
        self.logger.info("🧠 Neo4jMemoryRepository initialized")
    
    async def search_memory_patterns(self, request: SearchRequest) -> SearchResponse:
        """
        Search for memory patterns using specified strategy
        
        Implements:
        - Vector similarity search
        - Graph-based search
        - Hybrid search with re-ranking
        - Intent-based filtering
        """
        start_time = time.time()
        
        try:
            # Update statistics
            self.search_stats["total_searches"] += 1
            
            # Choose search strategy
            if request.strategy == SearchStrategy.VECTOR_ONLY:
                patterns = await self._vector_search(request)
                self.search_stats["vector_searches"] += 1
                
            elif request.strategy == SearchStrategy.GRAPH_ONLY:
                patterns = await self._graph_search(request)
                self.search_stats["graph_searches"] += 1
                
            elif request.strategy == SearchStrategy.HYBRID:
                patterns = await self._hybrid_search(request)
                self.search_stats["hybrid_searches"] += 1
                
            else:  # INTENT_MATCH
                patterns = await self._intent_search(request)
            
            # Apply filters
            patterns = self._apply_filters(patterns, request)
            
            # Limit results
            patterns = patterns[:request.k]
            
            # Calculate search time
            search_time_ms = (time.time() - start_time) * 1000
            self._update_avg_search_time(search_time_ms)
            
            # Build facets if requested
            facets = None
            if request.include_metadata:
                facets = self._build_facets(patterns)
            
            self.logger.info(
                f"Memory search completed: {len(patterns)} patterns found in {search_time_ms:.2f}ms"
            )
            
            return SearchResponse(
                patterns=patterns,
                total_found=len(patterns),
                query_processed=self._normalize_query(request.query),
                strategy_used=request.strategy,
                search_time_ms=search_time_ms,
                cache_hit=False,  # TODO: Implement caching
                facets=facets,
                detected_language=self._detect_language(request.query),
                extracted_intents=self._extract_intents(request.query)
            )
            
        except Exception as e:
            error_msg = f"Memory search failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    async def _vector_search(self, request: SearchRequest) -> List[MemoryPattern]:
        """Perform vector similarity search"""
        async with self.driver.session(database=self.database) as session:
            # Cypher query for vector search
            cypher = """
            CALL db.index.vector.queryNodes('memory_embeddings', $k, $query_vector)
            YIELD node, score
            WHERE score >= $min_similarity
            RETURN 
                node.id as id,
                node.content as content,
                node.phase as phase,
                node.language as language,
                node.created_at as created_at,
                node.tags as tags,
                score as similarity_score
            ORDER BY score DESC
            """
            
            # TODO: Get actual query vector from embedding service
            query_vector = await self._get_query_embedding(request.query)
            
            result = await session.run(
                cypher,
                k=request.k * 2,  # Get more for filtering
                query_vector=query_vector,
                min_similarity=request.min_similarity,
                routing_=RoutingControl.READ
            )
            
            patterns = []
            async for record in result:
                pattern = MemoryPattern(
                    id=record["id"],
                    content=record["content"],
                    similarity_score=record["similarity_score"],
                    combined_score=record["similarity_score"],
                    phase=MemoryPhase(record["phase"]) if record["phase"] else None,
                    language=record["language"],
                    created_at=datetime.fromisoformat(record["created_at"]) if record["created_at"] else None,
                    tags=record["tags"] or []
                )
                patterns.append(pattern)
            
            return patterns
    
    async def _graph_search(self, request: SearchRequest) -> List[MemoryPattern]:
        """Perform graph-based search using centrality algorithms"""
        async with self.driver.session(database=self.database) as session:
            # Cypher query for graph search with centrality scoring
            cypher = """
            MATCH (start:MemoryPattern)
            WHERE start.content CONTAINS $query_term
            
            CALL {
                WITH start
                MATCH (start)-[*1..3]-(connected:MemoryPattern)
                RETURN connected, count(*) as connection_count
                ORDER BY connection_count DESC
                LIMIT $k
            }
            
            RETURN 
                connected.id as id,
                connected.content as content,
                connected.phase as phase,
                connected.language as language,
                connected.created_at as created_at,
                connected.tags as tags,
                connection_count,
                (connection_count * 1.0 / 10.0) as centrality_score
            ORDER BY centrality_score DESC
            """
            
            result = await session.run(
                cypher,
                query_term=request.query.lower(),
                k=request.k,
                routing_=RoutingControl.READ
            )
            
            patterns = []
            async for record in result:
                pattern = MemoryPattern(
                    id=record["id"],
                    content=record["content"],
                    similarity_score=0.8,  # Default for graph search
                    graph_centrality=record["centrality_score"],
                    combined_score=record["centrality_score"],
                    phase=MemoryPhase(record["phase"]) if record["phase"] else None,
                    language=record["language"],
                    created_at=datetime.fromisoformat(record["created_at"]) if record["created_at"] else None,
                    tags=record["tags"] or [],
                    connections=[],  # TODO: Get actual connections
                    path_length=1
                )
                patterns.append(pattern)
            
            return patterns
    
    async def _hybrid_search(self, request: SearchRequest) -> List[MemoryPattern]:
        """Perform hybrid search combining vector and graph approaches"""
        # Get results from both strategies
        vector_patterns = await self._vector_search(request)
        graph_patterns = await self._graph_search(request)
        
        # Combine and re-rank results
        combined_patterns = {}
        
        # Add vector results
        for pattern in vector_patterns:
            combined_patterns[pattern.id] = pattern
        
        # Merge graph results
        for pattern in graph_patterns:
            if pattern.id in combined_patterns:
                # Combine scores
                existing = combined_patterns[pattern.id]
                existing.graph_centrality = pattern.graph_centrality
                existing.combined_score = self._calculate_hybrid_score(existing)
            else:
                combined_patterns[pattern.id] = pattern
        
        # Sort by combined score
        result_patterns = list(combined_patterns.values())
        result_patterns.sort(key=lambda p: p.combined_score, reverse=True)
        
        return result_patterns
    
    async def _intent_search(self, request: SearchRequest) -> List[MemoryPattern]:
        """Perform intent-based search"""
        # TODO: Implement intent matching algorithm
        # For now, fallback to vector search
        return await self._vector_search(request)
    
    async def get_pattern_by_id(self, pattern_id: str) -> Optional[MemoryPattern]:
        """Get specific memory pattern by ID"""
        async with self.driver.session(database=self.database) as session:
            cypher = """
            MATCH (p:MemoryPattern {id: $pattern_id})
            OPTIONAL MATCH (p)-[r]-(connected)
            RETURN 
                p.id as id,
                p.content as content,
                p.phase as phase,
                p.language as language,
                p.created_at as created_at,
                p.tags as tags,
                collect(connected.id) as connections
            """
            
            result = await session.run(
                cypher,
                pattern_id=pattern_id,
                routing_=RoutingControl.READ
            )
            
            record = await result.single()
            if not record:
                return None
            
            return MemoryPattern(
                id=record["id"],
                content=record["content"],
                similarity_score=1.0,
                combined_score=1.0,
                phase=MemoryPhase(record["phase"]) if record["phase"] else None,
                language=record["language"],
                created_at=datetime.fromisoformat(record["created_at"]) if record["created_at"] else None,
                tags=record["tags"] or [],
                connections=record["connections"] or []
            )
    
    async def traverse_graph(self, request: GraphTraversalRequest) -> GraphTraversalResponse:
        """Perform graph traversal operations"""
        start_time = time.time()
        
        async with self.driver.session(database=self.database) as session:
            # Cypher for graph traversal
            cypher = """
            MATCH (start:MemoryPattern)
            WHERE start.id IN $start_patterns
            
            CALL {
                WITH start
                MATCH path = (start)-[*1..$max_depth]-(end:MemoryPattern)
                WHERE length(path) <= $max_depth
                RETURN path, length(path) as path_length
                ORDER BY path_length
                LIMIT $max_paths
            }
            
            RETURN 
                [node in nodes(path) | node.id] as node_ids,
                [rel in relationships(path) | type(rel)] as relationship_types,
                path_length,
                nodes(path)[0].id as start_node,
                nodes(path)[-1].id as end_node
            """
            
            result = await session.run(
                cypher,
                start_patterns=request.start_patterns,
                max_depth=request.max_depth,
                max_paths=request.max_paths,
                routing_=RoutingControl.READ
            )
            
            paths = []
            async for record in result:
                path = GraphPath(
                    path_id=hashlib.md5(str(record["node_ids"]).encode()).hexdigest(),
                    nodes=record["node_ids"],
                    relationships=record["relationship_types"],
                    path_length=record["path_length"],
                    path_score=max(0.1, 1.0 / (record["path_length"] + 1)),  # Simple scoring
                    start_node=record["start_node"],
                    end_node=record["end_node"]
                )
                paths.append(path)
            
            traversal_time_ms = (time.time() - start_time) * 1000
            
            return GraphTraversalResponse(
                paths=paths,
                total_paths=len(paths),
                traversal_time_ms=traversal_time_ms,
                max_depth_reached=max([p.path_length for p in paths], default=0)
            )
    
    async def index_memory_content(self, request: MemoryIndexRequest) -> MemoryIndexResponse:
        """Index new memory content"""
        start_time = time.time()
        pattern_id = hashlib.md5(f"{request.content}{datetime.now()}".encode()).hexdigest()
        
        async with self.driver.session(database=self.database) as session:
            # Create memory pattern node
            cypher = """
            CREATE (p:MemoryPattern {
                id: $pattern_id,
                content: $content,
                phase: $phase,
                language: $language,
                tags: $tags,
                created_at: $created_at
            })
            RETURN p.id as id
            """
            
            await session.run(
                cypher,
                pattern_id=pattern_id,
                content=request.content,
                phase=request.phase.value,
                language=request.language,
                tags=request.tags,
                created_at=datetime.now().isoformat(),
                routing_=RoutingControl.WRITE
            )
            
            # Create connections if specified
            connections_created = 0
            if request.connect_to:
                connect_cypher = """
                MATCH (p1:MemoryPattern {id: $pattern_id})
                MATCH (p2:MemoryPattern {id: $target_id})
                CREATE (p1)-[:RELATED_TO]->(p2)
                """
                
                for target_id in request.connect_to:
                    await session.run(
                        connect_cypher,
                        pattern_id=pattern_id,
                        target_id=target_id,
                        routing_=RoutingControl.WRITE
                    )
                    connections_created += 1
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return MemoryIndexResponse(
                pattern_id=pattern_id,
                indexed_at=datetime.now(),
                connections_created=connections_created,
                processing_time_ms=processing_time_ms
            )
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        async with self.driver.session(database=self.database) as session:
            stats_cypher = """
            MATCH (p:MemoryPattern)
            OPTIONAL MATCH (p)-[r]-()
            RETURN 
                count(DISTINCT p) as total_patterns,
                count(r) as total_connections,
                collect(DISTINCT p.language) as languages,
                collect(DISTINCT p.phase) as phases
            """
            
            result = await session.run(stats_cypher, routing_=RoutingControl.READ)
            record = await result.single()
            
            return {
                "total_patterns": record["total_patterns"],
                "total_connections": record["total_connections"],
                "languages_supported": [lang for lang in record["languages"] if lang],
                "phases_available": [phase for phase in record["phases"] if phase],
                "search_stats": self.search_stats.copy()
            }
    
    async def close(self) -> None:
        """Close Neo4j driver connection"""
        if self.driver:
            await self.driver.close()
            self.logger.info("Neo4j driver connection closed")
    
    # Helper methods
    
    def _calculate_hybrid_score(self, pattern: MemoryPattern) -> float:
        """Calculate hybrid ranking score"""
        score = 0.0
        
        if pattern.similarity_score:
            score += self.ranking_weights["vector_similarity"] * pattern.similarity_score
        
        if pattern.graph_centrality:
            score += self.ranking_weights["graph_centrality"] * pattern.graph_centrality
        
        if pattern.intent_match:
            score += self.ranking_weights["intent_match"] * pattern.intent_match
        
        # Language confidence (simple heuristic)
        if pattern.language:
            score += self.ranking_weights["language_confidence"] * 0.8
        
        return min(1.0, score)
    
    def _apply_filters(self, patterns: List[MemoryPattern], request: SearchRequest) -> List[MemoryPattern]:
        """Apply filters to search results"""
        filtered = patterns
        
        if request.intent_filter:
            # TODO: Implement intent filtering
            pass
        
        if request.phase_filter:
            filtered = [p for p in filtered if p.phase == request.phase_filter]
        
        return filtered
    
    def _build_facets(self, patterns: List[MemoryPattern]) -> SearchFacets:
        """Build search facets from results"""
        languages = {}
        phases = {}
        tags = {}
        
        for pattern in patterns:
            # Language distribution
            if pattern.language:
                languages[pattern.language] = languages.get(pattern.language, 0) + 1
            
            # Phase distribution
            if pattern.phase:
                phases[pattern.phase.value] = phases.get(pattern.phase.value, 0) + 1
            
            # Tag frequency
            for tag in pattern.tags:
                tags[tag] = tags.get(tag, 0) + 1
        
        return SearchFacets(
            languages=languages,
            phases=phases,
            tags=tags
        )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize search query"""
        return query.lower().strip()
    
    def _detect_language(self, query: str) -> Optional[str]:
        """Detect query language (simple heuristic)"""
        # TODO: Implement proper language detection
        if any(char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" for char in query.lower()):
            return "uk" if "і" in query.lower() else "ru"
        return "en"
    
    def _extract_intents(self, query: str) -> List[str]:
        """Extract intent categories from query"""
        # TODO: Implement intent extraction
        intents = []
        
        learning_keywords = ["навчити", "вивчити", "learn", "study", "teach"]
        if any(keyword in query.lower() for keyword in learning_keywords):
            intents.append("learning")
        
        return intents
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """Get embedding vector for query"""
        # TODO: Integrate with actual embedding service
        # For now, return dummy vector
        return [0.1] * 384  # Common embedding dimension
    
    def _update_avg_search_time(self, search_time_ms: float) -> None:
        """Update average search time metric"""
        current_avg = self.search_stats["avg_search_time_ms"]
        total_searches = self.search_stats["total_searches"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_searches - 1)) + search_time_ms) / total_searches
        self.search_stats["avg_search_time_ms"] = new_avg


class MockMemoryRepository(MemoryRepositoryInterface):
    """Mock implementation for testing"""
    
    def __init__(self):
        self.patterns = {}
        self.search_count = 0
    
    async def search_memory_patterns(self, request: SearchRequest) -> SearchResponse:
        """Mock search returning dummy patterns"""
        self.search_count += 1
        
        # Create mock patterns
        patterns = [
            MemoryPattern(
                id=f"mock_pattern_{i}",
                content=f"Mock pattern {i} matching '{request.query}'",
                similarity_score=0.9 - (i * 0.1),
                combined_score=0.9 - (i * 0.1),
                phase=MemoryPhase.PROCESSING,
                language="en",
                created_at=datetime.now(),
                tags=["mock", "test"]
            )
            for i in range(min(request.k, 3))
        ]
        
        return SearchResponse(
            patterns=patterns,
            total_found=len(patterns),
            query_processed=request.query.lower(),
            strategy_used=request.strategy,
            search_time_ms=10.0,
            cache_hit=False,
            detected_language="en",
            extracted_intents=["mock"]
        )
    
    async def get_pattern_by_id(self, pattern_id: str) -> Optional[MemoryPattern]:
        """Mock pattern retrieval"""
        return self.patterns.get(pattern_id)
    
    async def traverse_graph(self, request: GraphTraversalRequest) -> GraphTraversalResponse:
        """Mock graph traversal"""
        return GraphTraversalResponse(
            paths=[],
            total_paths=0,
            traversal_time_ms=5.0,
            max_depth_reached=0
        )
    
    async def index_memory_content(self, request: MemoryIndexRequest) -> MemoryIndexResponse:
        """Mock indexing"""
        pattern_id = f"mock_{len(self.patterns)}"
        
        pattern = MemoryPattern(
            id=pattern_id,
            content=request.content,
            similarity_score=1.0,
            combined_score=1.0,
            phase=request.phase,
            language=request.language,
            created_at=datetime.now(),
            tags=request.tags
        )
        
        self.patterns[pattern_id] = pattern
        
        return MemoryIndexResponse(
            pattern_id=pattern_id,
            indexed_at=datetime.now(),
            connections_created=len(request.connect_to),
            processing_time_ms=5.0
        )
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Mock statistics"""
        return {
            "total_patterns": len(self.patterns),
            "total_connections": 0,
            "languages_supported": ["en", "uk"],
            "search_count": self.search_count
        }
    
    async def close(self) -> None:
        """Mock close"""
        pass 