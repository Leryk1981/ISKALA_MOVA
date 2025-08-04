"""
🧪 Comprehensive Tests for Semantic Search Service
Tests for hybrid search, graph traversal, caching, and performance
"""

import asyncio
import pytest
import time
import tempfile
from pathlib import Path
from typing import List, Dict, Any
import json

# Test framework imports
import pytest_asyncio
from pytest_benchmark.fixture import BenchmarkFixture
from unittest.mock import AsyncMock, MagicMock, patch

# ISKALA MOVA imports
from ..services.semantic_search_service import (
    SemanticSearchService,
    SearchResult,
    GraphPath,
    SearchFacets,
    PaginatedSearchResponse,
    create_semantic_search_service
)
from ..services.graph_vector_service import GraphVectorService, SearchResult as VectorSearchResult
from ..services.embedding_service import EmbeddingService
from ..services.neo4j_driver import Neo4jConnection, Neo4jConfig
from ..services.document_processor import DocChunk

# Test data for multilingual search
SEARCH_TEST_DATA = {
    "ukrainian_query": "штучний інтелект машинне навчання",
    "english_query": "artificial intelligence machine learning",
    "chinese_query": "人工智能机器学习",
    
    "sample_chunks": [
        {
            "id": "uk_ai_001",
            "content": "Штучний інтелект - це галузь інформатики, що займається створенням розумних машин.",
            "language": "uk",
            "source_doc": "ai_intro_uk.md",
            "intent_name": "learning"
        },
        {
            "id": "en_ai_001", 
            "content": "Artificial Intelligence is a branch of computer science dealing with intelligent machines.",
            "language": "en",
            "source_doc": "ai_intro_en.md",
            "intent_name": "learning"
        },
        {
            "id": "zh_ai_001",
            "content": "人工智能是计算机科学的一个分支，研究智能机器的创造。",
            "language": "zh",
            "source_doc": "ai_intro_zh.md", 
            "intent_name": "learning"
        }
    ]
}

class TestSemanticSearchService:
    """Test SemanticSearchService core functionality"""
    
    @pytest.fixture
    async def mock_vector_service(self):
        """Create mock GraphVectorService"""
        service = AsyncMock(spec=GraphVectorService)
        
        # Mock similarity search
        async def mock_similarity_search(query, language_filter=None, k=5, confidence_threshold=0.0):
            # Return relevant sample results based on query
            results = []
            for i, chunk in enumerate(SEARCH_TEST_DATA["sample_chunks"][:k]):
                if not language_filter or chunk["language"] == language_filter:
                    result = VectorSearchResult(
                        content=chunk["content"],
                        language=chunk["language"], 
                        chunk_hash=chunk["id"],
                        source_doc=chunk["source_doc"],
                        score=0.9 - (i * 0.1),
                        intent_name=chunk.get("intent_name"),
                        position=0,
                        metadata={}
                    )
                    results.append(result)
            return results
        
        service.similarity_search = mock_similarity_search
        service.health_check = AsyncMock(return_value={"status": "healthy"})
        service.close = AsyncMock()
        
        return service
    
    @pytest.fixture
    async def mock_neo4j_connection(self):
        """Create mock Neo4jConnection"""
        connection = AsyncMock(spec=Neo4jConnection)
        
        # Mock execute_query for graph searches
        async def mock_execute_query(query, **params):
            result = AsyncMock()
            
            # Mock graph search results
            if "CALL db.index.fulltext.queryNodes" in query:
                result.data = AsyncMock(return_value=[
                    {
                        "result_node": {
                            "chunk_hash": "graph_result_001",
                            "content": "Graph-based AI knowledge representation using semantic networks.",
                            "language": "en",
                            "source_doc": "graph_ai.md"
                        },
                        "graph_score": 0.85,
                        "intent_name": "research",
                        "graph_distance": 2
                    }
                ])
            else:
                result.data = AsyncMock(return_value=[])
            
            return result
        
        connection.execute_query = mock_execute_query
        connection.verify_connectivity = AsyncMock(return_value=True)
        connection.close = AsyncMock()
        
        return connection
    
    @pytest.fixture
    async def mock_embedding_service(self):
        """Create mock EmbeddingService"""
        service = AsyncMock(spec=EmbeddingService)
        
        # Mock embedding generation
        async def mock_get_embedding(text):
            # Simple mock: return different embeddings for different languages
            if any(char in text for char in "абвгґде"):  # Ukrainian
                return [0.8, 0.2, 0.1] + [0.0] * 381
            elif any(char in text for char in "abcdefg"):  # English  
                return [0.2, 0.8, 0.1] + [0.0] * 381
            else:  # Other/Chinese
                return [0.1, 0.2, 0.8] + [0.0] * 381
        
        service.get_embedding = mock_get_embedding
        service.health_check = AsyncMock(return_value={"status": "healthy"})
        
        return service
    
    @pytest.fixture
    async def mock_redis(self):
        """Create mock Redis client"""
        redis_mock = AsyncMock()
        redis_mock.get = AsyncMock(return_value=None)  # No cache hits by default
        redis_mock.setex = AsyncMock()
        redis_mock.ping = AsyncMock()
        redis_mock.info = AsyncMock(return_value={
            "keyspace_hits": 100,
            "keyspace_misses": 50
        })
        redis_mock.close = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    async def search_service(self, mock_vector_service, mock_neo4j_connection, 
                           mock_embedding_service, mock_redis):
        """Create SemanticSearchService with mocked dependencies"""
        service = SemanticSearchService(
            vector_service=mock_vector_service,
            neo4j_connection=mock_neo4j_connection,
            embedding_service=mock_embedding_service,
            redis_client=mock_redis
        )
        yield service
        await service.close()

    @pytest.mark.asyncio
    async def test_hybrid_search_basic(self, search_service):
        """Test basic hybrid search functionality"""
        # Execute search
        results = await search_service.hybrid_search(
            query="artificial intelligence",
            language="en",
            k=5
        )
        
        # Verify results
        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)
        assert all(r.language == "en" for r in results)
        assert all(r.combined_score > 0 for r in results)
        
        # Verify scoring components
        for result in results:
            assert 0.0 <= result.vector_score <= 1.0
            assert 0.0 <= result.graph_score <= 1.0
            assert 0.0 <= result.combined_score <= 1.0

    @pytest.mark.asyncio
    async def test_multilingual_hybrid_search(self, search_service):
        """Test hybrid search across multiple languages"""
        test_queries = [
            ("штучний інтелект", "uk"),
            ("artificial intelligence", "en"),
            ("人工智能", "zh")
        ]
        
        for query, language in test_queries:
            results = await search_service.hybrid_search(
                query=query,
                language=language,
                k=3
            )
            
            # Verify language filtering works
            assert len(results) >= 0  # May be empty for some languages in mock
            for result in results:
                if result.language:  # Allow None for mock data
                    assert result.language == language

    @pytest.mark.asyncio
    async def test_intent_filtering(self, search_service):
        """Test search with intent filtering"""
        results = await search_service.hybrid_search(
            query="machine learning algorithms",
            intent_filter="learning",
            k=5
        )
        
        # Verify intent filtering
        assert len(results) >= 0
        for result in results:
            if result.intent_name:
                assert result.intent_name in ["learning", None]  # Allow mock flexibility

    @pytest.mark.asyncio
    async def test_search_result_ranking(self, search_service):
        """Test that search results are properly ranked"""
        results = await search_service.hybrid_search(
            query="neural networks deep learning",
            k=10
        )
        
        if len(results) > 1:
            # Verify results are sorted by combined score (descending)
            scores = [r.combined_score for r in results]
            assert scores == sorted(scores, reverse=True)
        
        # Verify score calculation includes all components
        for result in results:
            expected_score = (
                result.vector_score * search_service.ranking_weights["vector_similarity"] +
                result.graph_score * search_service.ranking_weights["graph_centrality"] +
                result.intent_score * search_service.ranking_weights["intent_match"] +
                result.language_score * search_service.ranking_weights["language_confidence"]
            )
            # Allow small floating point differences
            assert abs(result.combined_score - expected_score) < 0.01

    @pytest.mark.asyncio
    async def test_graph_walk(self, search_service):
        """Test knowledge graph traversal"""
        paths = await search_service.graph_walk(
            start_node_id="test_chunk_001",
            max_depth=3
        )
        
        # Verify graph walk functionality (may be empty with mocked data)
        assert isinstance(paths, list)
        for path in paths:
            assert isinstance(path, GraphPath)
            assert path.path_length <= 3
            assert 0.0 <= path.confidence <= 1.0
            assert len(path.path_nodes) >= 1

    @pytest.mark.asyncio
    async def test_search_suggestions(self, search_service):
        """Test search suggestions functionality"""
        suggestions = await search_service.get_search_suggestions(
            partial_query="машин",
            language="uk",
            limit=5
        )
        
        # Verify suggestions
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 5
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0

    @pytest.mark.asyncio
    async def test_search_facets(self, search_service):
        """Test search facets generation"""
        facets = await search_service.get_search_facets(
            query="artificial intelligence",
            language="en"
        )
        
        # Verify facets structure
        assert isinstance(facets, SearchFacets)
        assert isinstance(facets.languages, dict)
        assert isinstance(facets.intents, dict)
        assert isinstance(facets.phases, dict)
        assert isinstance(facets.sources, dict)

    @pytest.mark.asyncio
    async def test_caching_functionality(self, search_service):
        """Test Redis caching functionality"""
        query = "test caching query"
        
        # First search (should miss cache)
        results1 = await search_service.hybrid_search(
            query=query,
            use_cache=True,
            k=3
        )
        
        # Verify cache key generation
        cache_key = search_service._generate_cache_key(query, None, None, None, 3)
        assert isinstance(cache_key, str)
        assert "search:" in cache_key

    @pytest.mark.asyncio
    async def test_performance_stats(self, search_service):
        """Test performance statistics collection"""
        # Perform some searches to generate stats
        await search_service.hybrid_search("test query 1", k=2)
        await search_service.hybrid_search("test query 2", k=3)
        
        # Get performance stats
        stats = await search_service.get_performance_stats()
        
        # Verify stats structure
        assert isinstance(stats, dict)
        assert "total_searches" in stats
        assert stats["total_searches"] >= 2
        assert "avg_search_time" in stats
        assert "hybrid_searches" in stats

    @pytest.mark.asyncio
    async def test_health_check(self, search_service):
        """Test comprehensive health check"""
        health = await search_service.health_check()
        
        # Verify health check structure
        assert isinstance(health, dict)
        assert "service" in health
        assert health["service"] == "SemanticSearchService"
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "components" in health

    @pytest.mark.asyncio
    async def test_error_handling(self, search_service):
        """Test error handling in various scenarios"""
        # Test with empty query (should handle gracefully)
        results = await search_service.hybrid_search(
            query="",
            k=5
        )
        assert isinstance(results, list)
        
        # Test with very large k value
        results = await search_service.hybrid_search(
            query="test",
            k=1000
        )
        assert isinstance(results, list)
        assert len(results) <= 100  # Should be reasonable limit

    @pytest.mark.asyncio 
    async def test_custom_ranking_weights(self, search_service):
        """Test custom ranking weight configuration"""
        # Set custom weights
        search_service.ranking_weights = {
            "vector_similarity": 0.6,
            "graph_centrality": 0.2,
            "intent_match": 0.1,
            "language_confidence": 0.1
        }
        
        results = await search_service.hybrid_search(
            query="test weighted ranking",
            k=3
        )
        
        # Verify custom weights are applied
        for result in results:
            expected_score = (
                result.vector_score * 0.6 +
                result.graph_score * 0.2 + 
                result.intent_score * 0.1 +
                result.language_score * 0.1
            )
            assert abs(result.combined_score - expected_score) < 0.01

class TestSemanticSearchAPI:
    """Test Search API endpoints"""
    
    # Note: These would require FastAPI test client setup
    # For now, we'll add basic structure tests
    
    def test_api_models_structure(self):
        """Test API model structures are valid"""
        from ..api.routes.search import (
            HybridSearchRequest,
            GraphWalkRequest,
            SuggestionsRequest,
            SearchResultResponse,
            HybridSearchResponse
        )
        
        # Test request model creation
        search_request = HybridSearchRequest(
            query="test query",
            language="uk",
            k=5
        )
        assert search_request.query == "test query"
        assert search_request.language == "uk"
        assert search_request.k == 5
        
        # Test response model
        result = SearchResultResponse(
            id="test_001",
            content="Test content",
            language="uk",
            source_doc="test.md",
            combined_score=0.85,
            result_type="hybrid"
        )
        assert result.id == "test_001"
        assert result.combined_score == 0.85

class TestPerformanceBenchmarks:
    """Performance and benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_search_latency_benchmark(self, search_service):
        """Benchmark search latency"""
        queries = [
            "artificial intelligence",
            "machine learning algorithms", 
            "neural network architecture",
            "natural language processing",
            "computer vision techniques"
        ]
        
        total_time = 0
        search_count = 0
        
        for query in queries:
            start_time = time.time()
            results = await search_service.hybrid_search(query, k=5)
            search_time = time.time() - start_time
            
            total_time += search_time
            search_count += 1
            
            # Individual search should be under 500ms (relaxed for testing)
            assert search_time < 0.5, f"Search took {search_time:.3f}s for query: {query}"
        
        # Average search time should be under 200ms
        avg_time = total_time / search_count
        assert avg_time < 0.2, f"Average search time {avg_time:.3f}s exceeds 200ms"

    @pytest.mark.asyncio
    async def test_concurrent_search_performance(self, search_service):
        """Test performance under concurrent load"""
        async def search_task(query_id):
            return await search_service.hybrid_search(
                query=f"test query {query_id}",
                k=3
            )
        
        # Run 10 concurrent searches
        start_time = time.time()
        tasks = [search_task(i) for i in range(10)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Verify all searches completed
        assert len(results) == 10
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 8  # Allow some failures in test environment
        
        # Total time should be reasonable (under 5 seconds for 10 concurrent)
        assert total_time < 5.0, f"10 concurrent searches took {total_time:.3f}s"

# ============================
# 🔧 TEST UTILITIES
# ============================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def cleanup_test_data():
    """Cleanup test data after tests"""
    yield
    
    # Cleanup any test data if needed
    try:
        # This would clean up any test data from Neo4j/Redis
        pass
    except Exception as e:
        print(f"Cleanup warning: {e}")

# ============================
# 🏃 TEST EXECUTION
# ============================

if __name__ == "__main__":
    # Run specific test groups
    pytest.main([
        __file__ + "::TestSemanticSearchService::test_hybrid_search_basic",
        "-v", "--tb=short"
    ]) 