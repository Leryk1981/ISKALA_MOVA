#!/usr/bin/env python3
"""
Unit Tests for Memory Service
Comprehensive test coverage for memory search business logic
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime
from typing import Dict, Any

from iskala_basis.services.memory_service import MemoryService, MemoryServiceError
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
from iskala_basis.repositories.memory_repository import MockMemoryRepository


class TestMemoryService:
    """Test suite for MemoryService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository for testing"""
        return MockMemoryRepository()
    
    @pytest.fixture
    def memory_service(self, mock_repository):
        """Create MemoryService with mock repository"""
        return MemoryService(mock_repository)
    
    @pytest.fixture
    def valid_search_request(self):
        """Create valid search request for testing"""
        return SearchRequest(
            query="як навчити нейронну мережу",
            language="uk",
            strategy=SearchStrategy.HYBRID,
            intent_filter="learning",
            k=5,
            min_similarity=0.7
        )
    
    @pytest.mark.asyncio
    async def test_search_memory_success(self, memory_service, valid_search_request):
        """Test successful memory search"""
        result = await memory_service.search_memory(valid_search_request)
        
        assert isinstance(result, SearchResponse)
        assert len(result.patterns) > 0
        assert result.query_processed == valid_search_request.query.lower()
        assert result.strategy_used == valid_search_request.strategy
        assert result.search_time_ms > 0
        assert isinstance(result.patterns[0], MemoryPattern)
    
    @pytest.mark.asyncio
    async def test_search_memory_query_too_short(self, memory_service):
        """Test search with query too short"""
        request = SearchRequest(
            query="x",  # Too short
            strategy=SearchStrategy.VECTOR_ONLY,
            k=5
        )
        
        with pytest.raises(MemoryServiceError) as exc_info:
            await memory_service.search_memory(request)
        
        assert exc_info.value.error_code == "QUERY_TOO_SHORT"
        assert "too short" in exc_info.value.message
    
    @pytest.mark.asyncio
    async def test_search_memory_query_too_long(self, memory_service):
        """Test search with query too long - Pydantic validation"""
        from pydantic import ValidationError
        
        long_query = "a" * 1001  # Exceeds maximum length
        
        # Pydantic should catch this at model validation level
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(
                query=long_query,
                strategy=SearchStrategy.VECTOR_ONLY,
                k=5
            )
        
        assert "string_too_long" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_search_memory_different_strategies(self, memory_service):
        """Test search with different strategies"""
        strategies = [
            SearchStrategy.VECTOR_ONLY,
            SearchStrategy.GRAPH_ONLY,
            SearchStrategy.HYBRID,
            SearchStrategy.INTENT_MATCH
        ]
        
        for strategy in strategies:
            request = SearchRequest(
                query="test query",
                strategy=strategy,
                k=3
            )
            
            result = await memory_service.search_memory(request)
            assert result.strategy_used == strategy
            assert len(result.patterns) <= 3
    
    @pytest.mark.asyncio
    async def test_search_memory_with_filters(self, memory_service):
        """Test search with phase and intent filters"""
        request = SearchRequest(
            query="test query",
            strategy=SearchStrategy.HYBRID,
            phase_filter=MemoryPhase.PROCESSING,
            intent_filter="learning",
            k=5
        )
        
        result = await memory_service.search_memory(request)
        assert isinstance(result, SearchResponse)
        # Mock repository should handle filters appropriately
    
    @pytest.mark.asyncio
    async def test_get_memory_pattern_success(self, memory_service):
        """Test successful pattern retrieval"""
        # First index a pattern
        index_request = MemoryIndexRequest(
            content="Test pattern content",
            phase=MemoryPhase.INPUT,
            language="en",
            tags=["test"]
        )
        
        index_response = await memory_service.index_memory_content(index_request)
        pattern_id = index_response.pattern_id
        
        # Then retrieve it
        pattern = await memory_service.get_memory_pattern(pattern_id)
        
        assert pattern is not None
        assert pattern.id == pattern_id
        assert pattern.content == "Test pattern content"
        assert pattern.phase == MemoryPhase.INPUT
    
    @pytest.mark.asyncio
    async def test_get_memory_pattern_not_found(self, memory_service):
        """Test pattern retrieval when pattern doesn't exist"""
        pattern = await memory_service.get_memory_pattern("nonexistent_id")
        assert pattern is None
    
    @pytest.mark.asyncio
    async def test_get_memory_pattern_empty_id(self, memory_service):
        """Test pattern retrieval with empty ID"""
        with pytest.raises(MemoryServiceError) as exc_info:
            await memory_service.get_memory_pattern("")
        
        assert exc_info.value.error_code == "INVALID_PATTERN_ID"
    
    @pytest.mark.asyncio
    async def test_traverse_memory_graph_success(self, memory_service):
        """Test successful graph traversal"""
        request = GraphTraversalRequest(
            start_patterns=["pattern_1", "pattern_2"],
            max_depth=3,
            max_paths=10,
            min_path_score=0.5
        )
        
        result = await memory_service.traverse_memory_graph(request)
        
        assert isinstance(result, GraphTraversalResponse)
        assert result.total_paths >= 0
        assert result.traversal_time_ms > 0
        assert result.max_depth_reached >= 0
    
    @pytest.mark.asyncio
    async def test_traverse_memory_graph_empty_start_patterns(self, memory_service):
        """Test graph traversal with empty start patterns"""
        request = GraphTraversalRequest(
            start_patterns=[],  # Empty
            max_depth=3,
            max_paths=10
        )
        
        with pytest.raises(MemoryServiceError) as exc_info:
            await memory_service.traverse_memory_graph(request)
        
        assert exc_info.value.error_code == "EMPTY_START_PATTERNS"
    
    @pytest.mark.asyncio
    async def test_traverse_memory_graph_invalid_max_depth(self, memory_service):
        """Test graph traversal with invalid max depth - Pydantic validation"""
        from pydantic import ValidationError
        
        # Pydantic should catch this at model validation level
        with pytest.raises(ValidationError) as exc_info:
            GraphTraversalRequest(
                start_patterns=["pattern_1"],
                max_depth=15,  # Too high
                max_paths=10
            )
        
        assert "less_than_equal" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_index_memory_content_success(self, memory_service):
        """Test successful memory content indexing"""
        request = MemoryIndexRequest(
            content="This is test content for indexing",
            phase=MemoryPhase.PROCESSING,
            language="en",
            tags=["test", "indexing"],
            connect_to=[]
        )
        
        result = await memory_service.index_memory_content(request)
        
        assert isinstance(result, MemoryIndexResponse)
        assert result.pattern_id is not None
        assert isinstance(result.indexed_at, datetime)
        assert result.processing_time_ms > 0
        assert result.connections_created >= 0
    
    @pytest.mark.asyncio
    async def test_index_memory_content_empty_content(self, memory_service):
        """Test indexing with empty content"""
        request = MemoryIndexRequest(
            content="   ",  # Only whitespace
            phase=MemoryPhase.INPUT,
            language="en"
        )
        
        with pytest.raises(MemoryServiceError) as exc_info:
            await memory_service.index_memory_content(request)
        
        assert exc_info.value.error_code == "EMPTY_CONTENT"
    
    @pytest.mark.asyncio
    async def test_index_memory_content_too_long(self, memory_service):
        """Test indexing with content too long - Pydantic validation"""
        from pydantic import ValidationError
        
        long_content = "a" * 10001  # Exceeds maximum length
        
        # Pydantic should catch this at model validation level
        with pytest.raises(ValidationError) as exc_info:
            MemoryIndexRequest(
                content=long_content,
                phase=MemoryPhase.INPUT,
                language="en"
            )
        
        assert "string_too_long" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_index_memory_content_with_connections(self, memory_service):
        """Test indexing with connections to existing patterns"""
        # First create a pattern to connect to
        first_request = MemoryIndexRequest(
            content="First pattern",
            phase=MemoryPhase.INPUT,
            language="en"
        )
        first_response = await memory_service.index_memory_content(first_request)
        
        # Then create second pattern with connection
        second_request = MemoryIndexRequest(
            content="Second pattern connected to first",
            phase=MemoryPhase.PROCESSING,
            language="en",
            connect_to=[first_response.pattern_id]
        )
        
        second_response = await memory_service.index_memory_content(second_request)
        
        assert second_response.connections_created == 1
    
    @pytest.mark.asyncio
    async def test_get_memory_health_success(self, memory_service):
        """Test memory health check"""
        # Perform some operations to generate metrics
        search_request = SearchRequest(
            query="test query",
            strategy=SearchStrategy.HYBRID,
            k=3
        )
        await memory_service.search_memory(search_request)
        
        health = await memory_service.get_memory_health()
        
        assert isinstance(health, MemoryHealthResponse)
        assert health.status in ["healthy", "degraded", "unhealthy"]
        assert health.total_patterns >= 0
        assert health.total_connections >= 0
        assert isinstance(health.languages_supported, list)
        assert health.avg_search_time_ms >= 0
        assert 0 <= health.cache_hit_ratio <= 1
        assert isinstance(health.timestamp, datetime)
    
    @pytest.mark.asyncio
    async def test_service_metrics_tracking(self, memory_service, valid_search_request):
        """Test that service correctly tracks metrics"""
        initial_searches = memory_service.service_metrics["total_searches"]
        initial_successful = memory_service.service_metrics["successful_searches"]
        
        # Perform successful search
        await memory_service.search_memory(valid_search_request)
        
        assert memory_service.service_metrics["total_searches"] == initial_searches + 1
        assert memory_service.service_metrics["successful_searches"] == initial_successful + 1
        assert memory_service.service_metrics["avg_response_time_ms"] >= 0  # Can be 0 for very fast operations
    
    @pytest.mark.asyncio
    async def test_service_error_metrics_tracking(self, memory_service):
        """Test that service correctly tracks error metrics"""
        initial_failed = memory_service.service_metrics["failed_searches"]
        
        # Cause an error
        invalid_request = SearchRequest(
            query="x",  # Too short
            strategy=SearchStrategy.VECTOR_ONLY,
            k=5
        )
        
        with pytest.raises(MemoryServiceError):
            await memory_service.search_memory(invalid_request)
        
        assert memory_service.service_metrics["failed_searches"] == initial_failed + 1
    
    @pytest.mark.asyncio
    async def test_strategy_usage_tracking(self, memory_service):
        """Test that service tracks strategy usage"""
        initial_hybrid = memory_service.service_metrics["strategy_usage"]["hybrid"]
        
        request = SearchRequest(
            query="test query for hybrid search",
            strategy=SearchStrategy.HYBRID,
            k=3
        )
        
        await memory_service.search_memory(request)
        
        assert memory_service.service_metrics["strategy_usage"]["hybrid"] == initial_hybrid + 1
    
    @pytest.mark.asyncio
    async def test_query_preprocessing(self, memory_service):
        """Test query preprocessing and optimization"""
        # Test with query that should trigger strategy auto-selection
        request = SearchRequest(
            query="  Як навчити нейронну мережу розпізнавати українську мову  ",  # Long query with whitespace
            strategy=SearchStrategy.HYBRID,
            k=5
        )
        
        result = await memory_service.search_memory(request)
        
        # Query should be trimmed and processed
        assert result.query_processed.strip() == request.query.strip().lower()
    
    @pytest.mark.asyncio
    async def test_different_memory_phases(self, memory_service):
        """Test indexing and searching across different memory phases"""
        phases = [MemoryPhase.INPUT, MemoryPhase.PROCESSING, MemoryPhase.OUTPUT, MemoryPhase.REFLECTION]
        
        for phase in phases:
            request = MemoryIndexRequest(
                content=f"Content for {phase.value} phase",
                phase=phase,
                language="en",
                tags=[phase.value]
            )
            
            result = await memory_service.index_memory_content(request)
            assert result.pattern_id is not None
    
    @pytest.mark.asyncio
    async def test_language_detection_and_processing(self, memory_service):
        """Test language detection in content processing"""
        # Test with Ukrainian content
        ukrainian_request = MemoryIndexRequest(
            content="Це український текст для тестування",
            phase=MemoryPhase.INPUT,
            language="auto"  # Should auto-detect
        )
        
        result = await memory_service.index_memory_content(ukrainian_request)
        assert result.pattern_id is not None
        
        # Test with English content
        english_request = MemoryIndexRequest(
            content="This is English text for testing",
            phase=MemoryPhase.INPUT,
            language="auto"  # Should auto-detect
        )
        
        result = await memory_service.index_memory_content(english_request)
        assert result.pattern_id is not None
    
    @pytest.mark.asyncio
    async def test_close_service(self, memory_service):
        """Test service cleanup"""
        await memory_service.close()
        # Should not raise any exceptions
    
    def test_memory_service_error_creation(self):
        """Test MemoryServiceError creation"""
        error = MemoryServiceError(
            message="Test error",
            error_code="TEST_ERROR",
            details={"key": "value"}
        )
        
        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {"key": "value"}
        assert str(error) == "Test error"


# Integration-style tests
class TestMemoryServiceIntegration:
    """Integration-style tests for MemoryService"""
    
    @pytest.fixture
    def memory_service(self):
        """Create service with mock repository for integration tests"""
        mock_repo = MockMemoryRepository()
        return MemoryService(mock_repo)
    
    @pytest.mark.asyncio
    async def test_complete_memory_workflow(self, memory_service):
        """Test complete memory management workflow"""
        # 1. Check system health
        health = await memory_service.get_memory_health()
        assert health.status in ["healthy", "degraded", "unhealthy"]
        
        # 2. Index some content
        index_request = MemoryIndexRequest(
            content="Neural networks are computational models inspired by biological neural networks",
            phase=MemoryPhase.PROCESSING,
            language="en",
            tags=["ai", "neural-networks", "machine-learning"]
        )
        index_response = await memory_service.index_memory_content(index_request)
        assert index_response.pattern_id is not None
        
        # 3. Search for the indexed content
        search_request = SearchRequest(
            query="neural networks computational models",
            strategy=SearchStrategy.HYBRID,
            k=5,
            min_similarity=0.5
        )
        search_response = await memory_service.search_memory(search_request)
        assert len(search_response.patterns) > 0
        
        # 4. Retrieve specific pattern
        pattern = await memory_service.get_memory_pattern(index_response.pattern_id)
        assert pattern is not None
        assert pattern.content == index_request.content
        
        # 5. Perform graph traversal
        traversal_request = GraphTraversalRequest(
            start_patterns=[index_response.pattern_id],
            max_depth=2,
            max_paths=5
        )
        traversal_response = await memory_service.traverse_memory_graph(traversal_request)
        assert isinstance(traversal_response, GraphTraversalResponse)
        
        # 6. Final health check
        final_health = await memory_service.get_memory_health()
        assert final_health.total_patterns >= 1


if __name__ == "__main__":
    pytest.main([__file__]) 