#!/usr/bin/env python3
"""
Memory Service for ISKALA
Business logic layer for memory search and graph operations
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from iskala_basis.models.memory_models import (
    SearchRequest,
    SearchResponse,
    MemoryPattern,
    SearchStrategy,
    MemoryPhase,
    GraphTraversalRequest,
    GraphTraversalResponse,
    MemoryIndexRequest,
    MemoryIndexResponse,
    MemoryHealthResponse
)
from iskala_basis.repositories.memory_repository import MemoryRepositoryInterface


# Configure logging
logger = logging.getLogger(__name__)


class MemoryServiceError(Exception):
    """Custom exception for memory service errors"""
    
    def __init__(self, message: str, error_code: str = "MEMORY_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class MemoryService:
    """
    Memory Service - Business Logic Layer
    
    Handles all memory operations with:
    - Query optimization and validation
    - Search strategy selection
    - Result filtering and ranking
    - Performance monitoring
    - Error handling and logging
    - Caching coordination
    """
    
    def __init__(self, repository: MemoryRepositoryInterface):
        self.repository = repository
        self.logger = logger
        
        # Performance metrics
        self.service_metrics = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "avg_response_time_ms": 0.0,
            "cache_efficiency": 0.0,
            "strategy_usage": {
                "vector_only": 0,
                "graph_only": 0,
                "hybrid": 0,
                "intent_match": 0
            }
        }
        
        # Query optimization settings
        self.optimization_config = {
            "min_query_length": 2,
            "max_query_length": 1000,
            "auto_strategy_threshold": 0.8,
            "similarity_boost_factor": 1.2,
            "graph_weight_factor": 1.1
        }
        
        self.logger.info("🧠 MemoryService initialized with advanced search capabilities")
    
    async def search_memory(self, request: SearchRequest) -> SearchResponse:
        """
        Main memory search method with comprehensive business logic
        
        Features:
        - Query preprocessing and optimization
        - Automatic strategy selection
        - Result post-processing
        - Performance monitoring
        - Error recovery
        """
        start_time = datetime.now()
        
        try:
            # Update metrics
            self.service_metrics["total_searches"] += 1
            
            # Validate and preprocess request
            optimized_request = await self._preprocess_search_request(request)
            
            # Log search attempt
            self.logger.info(
                f"Memory search initiated: query='{optimized_request.query[:50]}...', "
                f"strategy={optimized_request.strategy}, k={optimized_request.k}"
            )
            
            # Perform search through repository
            raw_response = await self.repository.search_memory_patterns(optimized_request)
            
            # Post-process results
            enhanced_response = await self._postprocess_search_response(raw_response, optimized_request)
            
            # Update success metrics
            self.service_metrics["successful_searches"] += 1
            self.service_metrics["strategy_usage"][optimized_request.strategy.value] += 1
            
            # Calculate and log performance
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._update_avg_response_time(response_time_ms)
            
            self.logger.info(
                f"Memory search completed: {len(enhanced_response.patterns)} patterns, "
                f"{response_time_ms:.2f}ms, strategy={optimized_request.strategy}"
            )
            
            return enhanced_response
            
        except MemoryServiceError:
            # Re-raise service errors without wrapping
            self.service_metrics["failed_searches"] += 1
            raise
        except Exception as e:
            self.service_metrics["failed_searches"] += 1
            error_msg = f"Memory search failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise MemoryServiceError(
                message=error_msg,
                error_code="SEARCH_FAILED",
                details={
                    "query": request.query,
                    "strategy": request.strategy.value,
                    "response_time_ms": (datetime.now() - start_time).total_seconds() * 1000
                }
            )
    
    async def get_memory_pattern(self, pattern_id: str) -> Optional[MemoryPattern]:
        """
        Get specific memory pattern with validation
        
        Args:
            pattern_id: Unique pattern identifier
            
        Returns:
            MemoryPattern or None if not found
        """
        try:
            # Validate pattern ID
            if not pattern_id or not pattern_id.strip():
                raise MemoryServiceError(
                    "Pattern ID cannot be empty",
                    "INVALID_PATTERN_ID"
                )
            
            self.logger.debug(f"Retrieving memory pattern: {pattern_id}")
            
            pattern = await self.repository.get_pattern_by_id(pattern_id.strip())
            
            if pattern:
                self.logger.debug(f"Pattern found: {pattern_id}")
            else:
                self.logger.debug(f"Pattern not found: {pattern_id}")
            
            return pattern
            
        except MemoryServiceError:
            # Re-raise service errors without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve pattern {pattern_id}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise MemoryServiceError(
                message=error_msg,
                error_code="PATTERN_RETRIEVAL_FAILED",
                details={"pattern_id": pattern_id}
            )
    
    async def traverse_memory_graph(self, request: GraphTraversalRequest) -> GraphTraversalResponse:
        """
        Perform graph traversal with business logic validation
        
        Args:
            request: Graph traversal request
            
        Returns:
            GraphTraversalResponse with found paths
        """
        try:
            # Validate traversal request
            await self._validate_traversal_request(request)
            
            self.logger.info(
                f"Graph traversal initiated: {len(request.start_patterns)} start points, "
                f"max_depth={request.max_depth}, max_paths={request.max_paths}"
            )
            
            # Perform traversal
            response = await self.repository.traverse_graph(request)
            
            # Filter paths by minimum score
            filtered_paths = [
                path for path in response.paths 
                if path.path_score >= request.min_path_score
            ]
            
            # Update response with filtered results
            response.paths = filtered_paths
            response.total_paths = len(filtered_paths)
            
            self.logger.info(
                f"Graph traversal completed: {len(filtered_paths)} paths found, "
                f"max_depth_reached={response.max_depth_reached}"
            )
            
            return response
            
        except MemoryServiceError:
            # Re-raise service errors without wrapping
            raise
        except Exception as e:
            error_msg = f"Graph traversal failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise MemoryServiceError(
                message=error_msg,
                error_code="TRAVERSAL_FAILED",
                details={
                    "start_patterns": request.start_patterns,
                    "max_depth": request.max_depth
                }
            )
    
    async def index_memory_content(self, request: MemoryIndexRequest) -> MemoryIndexResponse:
        """
        Index new memory content with validation and preprocessing
        
        Args:
            request: Memory indexing request
            
        Returns:
            MemoryIndexResponse with indexing results
        """
        try:
            # Validate indexing request
            await self._validate_indexing_request(request)
            
            # Preprocess content
            processed_request = await self._preprocess_indexing_request(request)
            
            self.logger.info(
                f"Memory indexing initiated: content_length={len(processed_request.content)}, "
                f"phase={processed_request.phase}, tags={len(processed_request.tags)}"
            )
            
            # Perform indexing
            response = await self.repository.index_memory_content(processed_request)
            
            self.logger.info(
                f"Memory indexing completed: pattern_id={response.pattern_id}, "
                f"connections={response.connections_created}, time={response.processing_time_ms:.2f}ms"
            )
            
            return response
            
        except MemoryServiceError:
            # Re-raise service errors without wrapping
            raise
        except Exception as e:
            error_msg = f"Memory indexing failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            raise MemoryServiceError(
                message=error_msg,
                error_code="INDEXING_FAILED",
                details={
                    "content_length": len(request.content),
                    "phase": request.phase.value
                }
            )
    
    async def get_memory_health(self) -> MemoryHealthResponse:
        """
        Get comprehensive memory system health status
        
        Returns:
            MemoryHealthResponse with system metrics
        """
        try:
            # Get repository statistics
            repo_stats = await self.repository.get_memory_statistics()
            
            # Calculate service-level metrics
            total_requests = self.service_metrics["total_searches"]
            success_rate = (
                self.service_metrics["successful_searches"] / max(total_requests, 1)
            )
            
            # Determine system status
            status = "healthy"
            if success_rate < 0.95:
                status = "degraded"
            elif success_rate < 0.8:
                status = "unhealthy"
            
            return MemoryHealthResponse(
                status=status,
                total_patterns=repo_stats.get("total_patterns", 0),
                total_connections=repo_stats.get("total_connections", 0),
                languages_supported=repo_stats.get("languages_supported", []),
                avg_search_time_ms=self.service_metrics["avg_response_time_ms"],
                cache_hit_ratio=self.service_metrics["cache_efficiency"],
                index_size_mb=0.0,  # TODO: Calculate actual index size
                timestamp=datetime.now()
            )
            
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            return MemoryHealthResponse(
                status="unhealthy",
                total_patterns=0,
                total_connections=0,
                languages_supported=[],
                avg_search_time_ms=0.0,
                cache_hit_ratio=0.0,
                index_size_mb=0.0,
                timestamp=datetime.now()
            )
    
    async def close(self) -> None:
        """Close service and repository connections"""
        try:
            await self.repository.close()
            self.logger.info("MemoryService closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing MemoryService: {str(e)}")
    
    # Private helper methods
    
    async def _preprocess_search_request(self, request: SearchRequest) -> SearchRequest:
        """Preprocess and optimize search request"""
        # Validate query length
        if len(request.query) < self.optimization_config["min_query_length"]:
            raise MemoryServiceError(
                f"Query too short (minimum {self.optimization_config['min_query_length']} characters)",
                "QUERY_TOO_SHORT"
            )
        
        if len(request.query) > self.optimization_config["max_query_length"]:
            raise MemoryServiceError(
                f"Query too long (maximum {self.optimization_config['max_query_length']} characters)",
                "QUERY_TOO_LONG"
            )
        
        # Keep original strategy unless explicitly auto-optimizing
        optimized_strategy = request.strategy
        
        # Create optimized request
        return SearchRequest(
            query=request.query.strip(),
            language=request.language,
            strategy=optimized_strategy,
            intent_filter=request.intent_filter,
            phase_filter=request.phase_filter,
            k=min(request.k, 100),  # Limit maximum results
            min_similarity=max(request.min_similarity, 0.1),  # Ensure minimum threshold
            include_metadata=request.include_metadata,
            use_cache=request.use_cache
        )
    
    async def _postprocess_search_response(self, response: SearchResponse, request: SearchRequest) -> SearchResponse:
        """Post-process search response with business logic"""
        # Apply additional filtering
        filtered_patterns = []
        
        for pattern in response.patterns:
            # Skip patterns with very low scores
            if pattern.combined_score < 0.1:
                continue
            
            # Apply phase filtering if specified
            if request.phase_filter and pattern.phase != request.phase_filter:
                continue
            
            # Boost scores for exact matches
            if request.query.lower() in pattern.content.lower():
                pattern.combined_score = min(1.0, pattern.combined_score * self.optimization_config["similarity_boost_factor"])
            
            filtered_patterns.append(pattern)
        
        # Sort by combined score
        filtered_patterns.sort(key=lambda p: p.combined_score, reverse=True)
        
        # Update response
        response.patterns = filtered_patterns
        response.total_found = len(filtered_patterns)
        
        return response
    
    async def _validate_traversal_request(self, request: GraphTraversalRequest) -> None:
        """Validate graph traversal request"""
        if not request.start_patterns:
            raise MemoryServiceError(
                "Start patterns cannot be empty",
                "EMPTY_START_PATTERNS"
            )
        
        if request.max_depth <= 0 or request.max_depth > 10:
            raise MemoryServiceError(
                "Max depth must be between 1 and 10",
                "INVALID_MAX_DEPTH"
            )
        
        if request.max_paths <= 0 or request.max_paths > 1000:
            raise MemoryServiceError(
                "Max paths must be between 1 and 1000",
                "INVALID_MAX_PATHS"
            )
    
    async def _validate_indexing_request(self, request: MemoryIndexRequest) -> None:
        """Validate memory indexing request"""
        if not request.content.strip():
            raise MemoryServiceError(
                "Content cannot be empty",
                "EMPTY_CONTENT"
            )
        
        if len(request.content) > 10000:
            raise MemoryServiceError(
                "Content too long (maximum 10000 characters)",
                "CONTENT_TOO_LONG"
            )
    
    async def _preprocess_indexing_request(self, request: MemoryIndexRequest) -> MemoryIndexRequest:
        """Preprocess indexing request"""
        # Clean content
        cleaned_content = request.content.strip()
        
        # Auto-detect language if needed
        language = request.language
        if language == "auto":
            language = self._detect_content_language(cleaned_content)
        
        # Auto-generate tags if none provided
        tags = request.tags
        if not tags:
            tags = self._extract_content_tags(cleaned_content)
        
        return MemoryIndexRequest(
            content=cleaned_content,
            phase=request.phase,
            language=language,
            tags=tags,
            metadata=request.metadata,
            connect_to=request.connect_to
        )
    
    def _detect_content_language(self, content: str) -> str:
        """Detect content language (simple heuristic)"""
        # TODO: Implement proper language detection
        if any(char in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" for char in content.lower()):
            return "uk" if "і" in content.lower() else "ru"
        return "en"
    
    def _extract_content_tags(self, content: str) -> List[str]:
        """Extract tags from content"""
        # TODO: Implement proper tag extraction
        tags = []
        
        # Simple keyword-based tagging
        keywords_map = {
            "навчання": ["learning", "education"],
            "нейронна": ["neural", "ai"],
            "мережа": ["network", "system"],
            "алгоритм": ["algorithm", "computation"],
            "дані": ["data", "information"]
        }
        
        content_lower = content.lower()
        for keyword, tag_list in keywords_map.items():
            if keyword in content_lower:
                tags.extend(tag_list)
        
        return list(set(tags))  # Remove duplicates
    
    def _update_avg_response_time(self, response_time_ms: float) -> None:
        """Update average response time metric"""
        current_avg = self.service_metrics["avg_response_time_ms"]
        total_requests = self.service_metrics["total_searches"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_requests - 1)) + response_time_ms) / total_requests
        self.service_metrics["avg_response_time_ms"] = new_avg 