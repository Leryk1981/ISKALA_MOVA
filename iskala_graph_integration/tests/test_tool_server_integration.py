"""
🧪 Tool Server Integration Tests
Comprehensive tests for ISKALA Graph Search integration with Tool Server

Tests cover:
- Endpoint functionality
- Request/response validation  
- Error handling
- Performance requirements
- OpenAPI schema validation
"""

import asyncio
import pytest
import json
import time
from pathlib import Path
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

# Test framework imports
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import components to test
from iskala_graph_integration.adapters.tool_server_extension import (
    GraphSearchToolServerExtension,
    get_graph_search_openapi_extensions
)
from iskala_graph_integration.handlers.integration_handler import (
    ToolServerIntegrationHandler,
    quick_integrate_graph_search
)
from iskala_graph_integration.schemas.requests import (
    GraphHybridSearchRequest,
    GraphVectorSearchRequest,
    GraphWalkRequest,
    GraphSuggestionsRequest
)
from iskala_graph_integration.schemas.responses import (
    GraphSearchResponse,
    GraphWalkResponse,
    GraphSuggestionsResponse,
    GraphStatusResponse
)

# Test data
SAMPLE_SEARCH_REQUEST = {
    "query": "штучний інтелект машинне навчання",
    "language": "uk",
    "k": 5,
    "intent_filter": "learning",
    "include_facets": True
}

SAMPLE_SEARCH_RESPONSE = {
    "query": "штучний інтелект машинне навчання",
    "results": [
        {
            "id": "chunk_001",
            "content": "Штучний інтелект - це галузь інформатики...",
            "language": "uk",
            "source_doc": "ai_intro_uk.md",
            "combined_score": 0.95,
            "result_type": "hybrid",
            "intent_name": "learning"
        }
    ],
    "total_results": 1,
    "search_time_ms": 125.5,
    "cache_hit": False
}

SAMPLE_WALK_REQUEST = {
    "start_node_id": "chunk_abc123",
    "max_depth": 3,
    "intent_filter": ["learning", "research"]
}

SAMPLE_WALK_RESPONSE = {
    "start_node_id": "chunk_abc123",
    "paths": [
        {
            "start_node_id": "chunk_abc123",
            "end_node_id": "chunk_def456",
            "path_length": 2,
            "confidence": 0.9,
            "nodes": [
                {"id": "chunk_abc123", "type": "ContextChunk"},
                {"id": "chunk_def456", "type": "ContextChunk"}
            ],
            "relationships": [
                {"type": "LEADS_TO", "properties": {}}
            ],
            "path_summary": "ContextChunk → ContextChunk (distance: 2)"
        }
    ],
    "total_paths": 1,
    "walk_time_ms": 45.2
}

class TestGraphSearchExtension:
    """Test GraphSearchToolServerExtension functionality"""
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client for testing"""
        client = AsyncMock()
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_response.raise_for_status.return_value = None
        
        client.request.return_value = mock_response
        client.get.return_value = mock_response
        client.post.return_value = mock_response
        
        return client
    
    @pytest.fixture
    async def graph_extension(self, mock_http_client):
        """Create GraphSearchToolServerExtension with mocked client"""
        extension = GraphSearchToolServerExtension()
        extension.client = mock_http_client
        yield extension
        await extension.close()
    
    @pytest.mark.asyncio
    async def test_hybrid_search(self, graph_extension):
        """Test hybrid search functionality"""
        request = GraphHybridSearchRequest(**SAMPLE_SEARCH_REQUEST)
        
        result = await graph_extension.hybrid_search(request)
        
        # Verify response structure
        assert "success" in result
        assert result["success"] is True
        assert "query" in result
        assert result["query"] == SAMPLE_SEARCH_REQUEST["query"]
        assert "results" in result
        assert len(result["results"]) > 0
        assert "metadata" in result
        assert result["metadata"]["service"] == "ISKALA Graph Search"
    
    @pytest.mark.asyncio
    async def test_vector_search(self, graph_extension):
        """Test vector search functionality"""
        request = GraphVectorSearchRequest(
            query="нейронні мережі",
            language="uk",
            k=10
        )
        
        result = await graph_extension.vector_search(request)
        
        assert "success" in result
        assert result["success"] is True
        assert "query" in result
    
    @pytest.mark.asyncio
    async def test_graph_walk(self, graph_extension):
        """Test graph walk functionality"""
        # Mock graph walk response
        graph_extension.client.request.return_value.json.return_value = SAMPLE_WALK_RESPONSE
        
        request = GraphWalkRequest(**SAMPLE_WALK_REQUEST)
        
        result = await graph_extension.graph_walk(request)
        
        assert "success" in result
        assert result["success"] is True
        assert "start_node_id" in result
        assert result["start_node_id"] == SAMPLE_WALK_REQUEST["start_node_id"]
        assert "paths" in result
    
    @pytest.mark.asyncio
    async def test_search_suggestions(self, graph_extension):
        """Test search suggestions functionality"""
        # Mock suggestions response
        suggestions_response = {
            "partial_query": "машин",
            "suggestions": ["машинне навчання", "машинний переклад"],
            "suggestion_count": 2,
            "generation_time_ms": 15.8
        }
        graph_extension.client.request.return_value.json.return_value = suggestions_response
        
        request = GraphSuggestionsRequest(
            partial_query="машин",
            language="uk",
            limit=5
        )
        
        result = await graph_extension.search_suggestions(request)
        
        assert "success" in result
        assert result["success"] is True
        assert "suggestions" in result
        assert len(result["suggestions"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_status(self, graph_extension):
        """Test status check functionality"""
        # Mock status response
        status_response = {
            "service": "ISKALA Graph Search",
            "status": "healthy",
            "components": {
                "semantic_search": {"status": "healthy"},
                "neo4j": {"status": "healthy"},
                "redis": {"status": "healthy"}
            }
        }
        graph_extension.client.request.return_value.json.return_value = status_response
        
        result = await graph_extension.get_status()
        
        assert "service" in result
        assert result["service"] == "ISKALA Graph Search"
        assert "status" in result
        assert "components" in result
    
    @pytest.mark.asyncio
    async def test_error_handling(self, graph_extension):
        """Test error handling in extension"""
        # Mock HTTP error
        import httpx
        graph_extension.client.request.side_effect = httpx.HTTPStatusError(
            "500 Server Error", request=MagicMock(), response=MagicMock(status_code=500, text="Internal Error")
        )
        
        request = GraphHybridSearchRequest(**SAMPLE_SEARCH_REQUEST)
        
        # Should raise HTTPException
        with pytest.raises(Exception):  # FastAPI HTTPException
            await graph_extension.hybrid_search(request)
    
    def test_performance_stats(self, graph_extension):
        """Test performance statistics collection"""
        stats = graph_extension.get_performance_stats()
        
        assert "total_requests" in stats
        assert "avg_response_time_ms" in stats
        assert "service_url" in stats
        assert "auth_enabled" in stats
        assert isinstance(stats["total_requests"], int)
        assert isinstance(stats["avg_response_time_ms"], float)

class TestIntegrationHandler:
    """Test ToolServerIntegrationHandler functionality"""
    
    @pytest.fixture
    def mock_fastapi_app(self):
        """Mock FastAPI application"""
        app = MagicMock(spec=FastAPI)
        return app
    
    @pytest.fixture
    def sample_openapi_schema(self):
        """Sample OpenAPI schema for testing"""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "ISKALA Modules API",
                "description": "API для доступу к модулям ISKALA",
                "version": "1.0.0"
            },
            "paths": {
                "/iskala/memory/search": {
                    "post": {
                        "operationId": "search_iskala_memory",
                        "summary": "Пошук в пам'яті ISKALA"
                    }
                }
            }
        }
    
    def test_integration_handler_initialization(self):
        """Test integration handler initialization"""
        handler = ToolServerIntegrationHandler()
        
        assert handler.is_integrated is False
        assert isinstance(handler.openapi_schema, dict)
    
    def test_openapi_schema_extension(self, mock_fastapi_app, sample_openapi_schema):
        """Test OpenAPI schema extension"""
        handler = ToolServerIntegrationHandler()
        
        success = handler.integrate_graph_search_endpoints(mock_fastapi_app, sample_openapi_schema)
        
        assert success is True
        assert handler.is_integrated is True
        
        # Check that new paths were added
        assert "/iskala/graph/search_hybrid" in sample_openapi_schema["paths"]
        assert "/iskala/graph/search_vector" in sample_openapi_schema["paths"]
        assert "/iskala/graph/walk" in sample_openapi_schema["paths"]
        assert "/iskala/graph/suggestions" in sample_openapi_schema["paths"]
        assert "/iskala/graph/status" in sample_openapi_schema["paths"]
        
        # Check operation IDs
        hybrid_op = sample_openapi_schema["paths"]["/iskala/graph/search_hybrid"]["post"]
        assert hybrid_op["operationId"] == "graph_search_hybrid"
    
    def test_schema_info_update(self, mock_fastapi_app, sample_openapi_schema):
        """Test that schema info is properly updated"""
        handler = ToolServerIntegrationHandler()
        
        original_description = sample_openapi_schema["info"]["description"]
        original_version = sample_openapi_schema["info"]["version"]
        
        handler.integrate_graph_search_endpoints(mock_fastapi_app, sample_openapi_schema)
        
        # Check description was enhanced
        new_description = sample_openapi_schema["info"]["description"]
        assert "Graph Search" in new_description
        assert original_description in new_description
        
        # Check version was updated
        new_version = sample_openapi_schema["info"]["version"]
        assert "graph" in new_version.lower()
    
    def test_generate_integration_code(self):
        """Test integration code generation"""
        handler = ToolServerIntegrationHandler()
        
        code = handler.generate_integration_code()
        
        assert isinstance(code, str)
        assert "Graph Search Integration" in code
        assert "integrate_graph_search_endpoints" in code
        assert "import" in code
        assert "@app." in code  # Should contain endpoint decorators
    
    def test_verification(self, mock_fastapi_app, sample_openapi_schema):
        """Test integration verification"""
        handler = ToolServerIntegrationHandler()
        
        # Before integration
        results_before = handler.verify_integration()
        assert results_before["integration_status"] is False
        
        # After integration
        handler.integrate_graph_search_endpoints(mock_fastapi_app, sample_openapi_schema)
        results_after = handler.verify_integration()
        assert results_after["integration_status"] is True
        assert results_after["endpoints_count"] > 0
        assert results_after["schema_extended"] is True

class TestRequestResponseSchemas:
    """Test Pydantic request/response schemas"""
    
    def test_hybrid_search_request_validation(self):
        """Test hybrid search request validation"""
        # Valid request
        valid_request = GraphHybridSearchRequest(**SAMPLE_SEARCH_REQUEST)
        assert valid_request.query == SAMPLE_SEARCH_REQUEST["query"]
        assert valid_request.language == SAMPLE_SEARCH_REQUEST["language"]
        assert valid_request.k == SAMPLE_SEARCH_REQUEST["k"]
        
        # Test weight validation
        with pytest.raises(ValueError):  # Weights don't sum to 1.0
            GraphHybridSearchRequest(
                query="test",
                vector_weight=0.5,
                graph_weight=0.5,
                intent_weight=0.5,
                language_weight=0.5
            )
        
        # Test empty query validation
        with pytest.raises(ValueError):
            GraphHybridSearchRequest(query="")
    
    def test_graph_walk_request_validation(self):
        """Test graph walk request validation"""
        valid_request = GraphWalkRequest(**SAMPLE_WALK_REQUEST)
        assert valid_request.start_node_id == SAMPLE_WALK_REQUEST["start_node_id"]
        assert valid_request.max_depth == SAMPLE_WALK_REQUEST["max_depth"]
        
        # Test empty node ID validation
        with pytest.raises(ValueError):
            GraphWalkRequest(start_node_id="")
    
    def test_suggestions_request_validation(self):
        """Test suggestions request validation"""
        valid_request = GraphSuggestionsRequest(
            partial_query="машин",
            language="uk",
            limit=5
        )
        assert valid_request.partial_query == "машин"
        assert valid_request.language == "uk"
        assert valid_request.limit == 5
        
        # Test empty partial query validation
        with pytest.raises(ValueError):
            GraphSuggestionsRequest(partial_query="")

class TestOpenAPISchemaExtensions:
    """Test OpenAPI schema extensions"""
    
    def test_openapi_extensions_structure(self):
        """Test that OpenAPI extensions have correct structure"""
        extensions = get_graph_search_openapi_extensions()
        
        assert isinstance(extensions, dict)
        assert len(extensions) == 5  # 5 endpoints
        
        # Check each endpoint has required fields
        for path, spec in extensions.items():
            assert isinstance(spec, dict)
            
            # Check for POST endpoints
            if path != "/iskala/graph/status":  # status is GET
                assert "post" in spec
                post_spec = spec["post"]
                assert "operationId" in post_spec
                assert "summary" in post_spec
                assert "description" in post_spec
                assert "requestBody" in post_spec
                assert "responses" in post_spec
            else:  # status endpoint
                assert "get" in spec
                get_spec = spec["get"]
                assert "operationId" in get_spec
                assert get_spec["operationId"] == "graph_status"
    
    def test_operation_ids_unique(self):
        """Test that all operation IDs are unique"""
        extensions = get_graph_search_openapi_extensions()
        
        operation_ids = []
        for path, spec in extensions.items():
            method = "post" if path != "/iskala/graph/status" else "get"
            operation_id = spec[method]["operationId"]
            operation_ids.append(operation_id)
        
        # Check uniqueness
        assert len(operation_ids) == len(set(operation_ids))
        
        # Check expected operation IDs
        expected_ids = [
            "graph_search_hybrid",
            "graph_search_vector", 
            "graph_walk",
            "graph_suggestions",
            "graph_status"
        ]
        
        for expected_id in expected_ids:
            assert expected_id in operation_ids

class TestPerformanceRequirements:
    """Test performance requirements for integration"""
    
    @pytest.mark.asyncio
    async def test_endpoint_response_time(self):
        """Test that endpoints meet response time requirements (<150ms)"""
        # This would require actual service running for real performance test
        # For now, we'll test the performance tracking mechanism
        
        extension = GraphSearchToolServerExtension()
        
        # Simulate some requests
        extension.request_count = 10
        extension.total_response_time = 1.2  # 1.2 seconds total
        
        stats = extension.get_performance_stats()
        avg_time_ms = stats["avg_response_time_ms"]
        
        # Average should be 120ms (1.2s / 10 requests * 1000)
        assert avg_time_ms == 120.0
        
        await extension.close()
    
    def test_concurrent_request_handling(self):
        """Test concurrent request handling capabilities"""
        # This test verifies that the extension can handle multiple requests
        # In a real scenario, this would involve actual concurrent HTTP requests
        
        extension = GraphSearchToolServerExtension()
        
        # Verify that extension uses async HTTP client
        assert hasattr(extension, '_get_client')
        assert asyncio.iscoroutinefunction(extension._get_client)

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors"""
        extension = GraphSearchToolServerExtension()
        
        # Mock network error
        mock_client = AsyncMock()
        import httpx
        mock_client.request.side_effect = httpx.ConnectError("Connection failed")
        extension.client = mock_client
        
        request = GraphHybridSearchRequest(query="test query")
        
        # Should raise HTTPException with 503 status
        with pytest.raises(Exception) as exc_info:
            await extension.hybrid_search(request)
        
        # In real FastAPI, this would be HTTPException with status_code 503
        await extension.close()
    
    @pytest.mark.asyncio  
    async def test_timeout_handling(self):
        """Test handling of request timeouts"""
        extension = GraphSearchToolServerExtension()
        
        # Mock timeout error
        mock_client = AsyncMock()
        import httpx
        mock_client.request.side_effect = httpx.TimeoutException("Request timeout")
        extension.client = mock_client
        
        request = GraphHybridSearchRequest(query="test query")
        
        with pytest.raises(Exception):
            await extension.hybrid_search(request)
        
        await extension.close()

# Integration test utility functions

def test_quick_integrate_function():
    """Test quick integration convenience function"""
    app = MagicMock(spec=FastAPI)
    schema = {"paths": {}}
    
    result = quick_integrate_graph_search(app, schema)
    
    assert result is True
    assert len(schema["paths"]) > 0

# Test fixtures and utilities

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def cleanup_clients():
    """Cleanup HTTP clients after tests"""
    yield
    
    # Cleanup any open clients
    try:
        # This would clean up any remaining HTTP clients
        pass
    except Exception as e:
        print(f"Cleanup warning: {e}")

# Performance test utilities

def measure_execution_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Log execution time
        print(f"Function {func.__name__} executed in {execution_time:.3f}s")
        return result
    
    return wrapper

# Test execution

if __name__ == "__main__":
    # Run specific test groups
    pytest.main([
        __file__ + "::TestGraphSearchExtension::test_hybrid_search",
        "-v", "--tb=short"
    ]) 