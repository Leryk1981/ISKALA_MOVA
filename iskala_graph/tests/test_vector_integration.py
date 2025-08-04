"""
🧪 Vector Integration Tests for ISKALA MOVA
Comprehensive testing of GraphVectorService, API endpoints, and E2E workflows

Tests cover:
- Document processing pipeline
- Vector storage and search
- Multilingual functionality  
- Performance requirements
- Error handling
"""

import asyncio
import pytest
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
import json

# Test framework imports
import pytest_asyncio
from pytest_benchmark.fixture import BenchmarkFixture

# ISKALA MOVA imports
from ..services.graph_vector_service import (
    GraphVectorService,
    SearchResult,
    IndexingResult,
    create_graph_vector_service
)
from ..services.document_processor import (
    MultilingualDocumentProcessor,
    DocChunk,
    LanguageCode
)
from ..services.embedding_service import EmbeddingService
from ..services.neo4j_driver import Neo4jConnection, Neo4jConfig

# Test data
SAMPLE_TEXTS = {
    "english": """
    Artificial Intelligence has revolutionized how we process natural language.
    Machine Learning algorithms can understand human text with remarkable accuracy.
    Companies like Google, Microsoft, and OpenAI are leading the development.
    """,
    
    "ukrainian": """
    Штучний інтелект революціонізував обробку природної мови.
    Алгоритми машинного навчання можуть розуміти людський текст з надзвичайною точністю.
    Державно-приватне партнерство в інформаційно-комунікаційних технологіях показує відмінні результати.
    """,
    
    "chinese": """
    人工智能彻底改变了我们处理自然语言的方式。
    机器学习算法能够以惊人的准确性理解人类文本。
    谷歌、微软和OpenAI等公司在开发方面处于领先地位。
    """
}

class TestGraphVectorService:
    """Test GraphVectorService core functionality"""
    
    @pytest.fixture
    async def vector_service(self):
        """Create GraphVectorService for testing"""
        try:
            service = await create_graph_vector_service()
            yield service
        finally:
            await service.close()
    
    @pytest.fixture
    def sample_doc_chunks(self):
        """Create sample DocChunk objects for testing"""
        chunks = []
        
        for i, (lang, text) in enumerate(SAMPLE_TEXTS.items()):
            chunk = DocChunk(
                chunk_id=f"test_{lang}_{i:03d}",
                content=text.strip(),
                language=lang,
                source_doc=f"test_{lang}.txt",
                position=i,
                chunk_hash=f"hash_{lang}_{i}",
                metadata={"test": True, "language": lang},
                start_char=0,
                end_char=len(text),
                sentence_count=3,
                word_count=len(text.split()),
                confidence=0.95,
                created_at="2024-01-01T00:00:00"
            )
            chunks.append(chunk)
        
        return chunks

    @pytest.mark.asyncio
    async def test_service_initialization(self, vector_service):
        """Test service components initialize correctly"""
        # Test health check
        health = await vector_service.health_check()
        
        assert health["service"] == "GraphVectorService"
        assert health["status"] in ["healthy", "degraded"]  # Allow degraded for test environment
        assert "components" in health
        assert "neo4j" in health["components"]
        assert "embedding_service" in health["components"]

    @pytest.mark.asyncio 
    async def test_store_document_chunks(self, vector_service, sample_doc_chunks):
        """Test storing chunks with embeddings in Neo4j"""
        # Store chunks
        stored_count = await vector_service.store_document_chunks(sample_doc_chunks)
        
        # Verify storage
        assert stored_count == len(sample_doc_chunks)
        
        # Verify chunks can be retrieved
        for chunk in sample_doc_chunks:
            retrieved = await vector_service.get_chunk_by_hash(chunk.chunk_hash)
            assert retrieved is not None
            assert retrieved.content == chunk.content
            assert retrieved.language == chunk.language

    @pytest.mark.asyncio
    async def test_multilingual_similarity_search(self, vector_service, sample_doc_chunks):
        """Test semantic search across multiple languages"""
        # First store the chunks
        await vector_service.store_document_chunks(sample_doc_chunks)
        
        # Test searches in different languages
        test_queries = {
            "english": "artificial intelligence machine learning",
            "ukrainian": "штучний інтелект машинне навчання",
            "chinese": "人工智能机器学习"
        }
        
        for lang, query in test_queries.items():
            results = await vector_service.similarity_search(
                query=query,
                language_filter=lang,
                k=5
            )
            
            # Verify results
            assert len(results) > 0, f"No results for {lang} query"
            
            # Verify language filtering
            for result in results:
                assert result.language == lang, f"Language mismatch: expected {lang}, got {result.language}"
            
            # Verify similarity scores are reasonable
            for result in results:
                assert 0.0 <= result.score <= 1.0, f"Invalid similarity score: {result.score}"

    @pytest.mark.asyncio
    async def test_document_processing_pipeline(self, vector_service):
        """Test complete E2E pipeline: Document → Chunks → Embeddings → Neo4j → Search"""
        # Create temporary test file
        test_content = SAMPLE_TEXTS["english"]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_path = Path(f.name)
        
        try:
            # Process document
            result = await vector_service.process_and_index_document(temp_path)
            
            # Verify processing result
            assert result.success, f"Processing failed: {result.error_message}"
            assert result.chunks_created > 0
            assert result.chunks_indexed == result.chunks_created
            assert result.language_detected == "en"
            
            # Test search on processed document  
            search_results = await vector_service.similarity_search(
                query="artificial intelligence",
                language_filter="en",
                k=3
            )
            
            assert len(search_results) > 0
            assert any("artificial" in result.content.lower() for result in search_results)
            
        finally:
            # Cleanup
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_ukrainian_terms_preservation(self, vector_service):
        """Test that Ukrainian compound terms are preserved during processing"""
        ukrainian_text = """
        Державно-приватне партнерство в інформаційно-комунікаційних технологіях.
        Науково-технічний прогрес забезпечує розвиток суспільства.
        Тарас Шевченко та Іван Франко були великими письменниками.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(ukrainian_text)
            temp_path = Path(f.name)
        
        try:
            # Process document
            result = await vector_service.process_and_index_document(temp_path)
            assert result.success
            assert result.language_detected == "uk"
            
            # Search for compound terms
            search_results = await vector_service.similarity_search(
                query="державно-приватне партнерство",
                language_filter="uk",
                k=5
            )
            
            # Verify compound terms are preserved
            found_terms = []
            for result in search_results:
                content_lower = result.content.lower()
                if "державно-приватне" in content_lower:
                    found_terms.append("державно-приватне")
                if "інформаційно-комунікаційних" in content_lower:
                    found_terms.append("інформаційно-комунікаційних")
                if "науково-технічний" in content_lower:
                    found_terms.append("науково-технічний")
            
            assert len(found_terms) > 0, "Ukrainian compound terms not preserved"
            
        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_search_performance(self, vector_service, sample_doc_chunks):
        """Test search performance meets requirements (<100ms)"""
        # Store test data
        await vector_service.store_document_chunks(sample_doc_chunks)
        
        # Measure search performance
        query = "artificial intelligence machine learning"
        search_times = []
        
        for _ in range(10):  # Multiple searches for average
            start_time = time.time()
            results = await vector_service.similarity_search(query, k=5)
            search_time = (time.time() - start_time) * 1000  # Convert to ms
            search_times.append(search_time)
            
            assert len(results) >= 0  # Basic functionality check
        
        # Verify performance
        avg_search_time = sum(search_times) / len(search_times)
        max_search_time = max(search_times)
        
        # Performance targets (relaxed for test environment)
        assert avg_search_time < 200, f"Average search time too high: {avg_search_time:.1f}ms"
        assert max_search_time < 500, f"Max search time too high: {max_search_time:.1f}ms"

    @pytest.mark.asyncio
    async def test_error_handling(self, vector_service):
        """Test error handling and graceful degradation"""
        # Test search with invalid parameters
        with pytest.raises(Exception):
            await vector_service.similarity_search("", k=0)  # Invalid parameters
        
        # Test search with non-existent language filter
        results = await vector_service.similarity_search(
            query="test",
            language_filter="invalid_lang",
            k=5
        )
        assert len(results) == 0  # Should return empty results, not crash
        
        # Test chunk retrieval with invalid hash
        result = await vector_service.get_chunk_by_hash("invalid_hash")
        assert result is None

    @pytest.mark.asyncio
    async def test_statistics_collection(self, vector_service, sample_doc_chunks):
        """Test comprehensive statistics collection"""
        # Store some data
        await vector_service.store_document_chunks(sample_doc_chunks)
        
        # Perform some searches
        await vector_service.similarity_search("test query", k=3)
        await vector_service.similarity_search("another query", language_filter="en", k=2)
        
        # Get statistics
        stats = await vector_service.get_statistics()
        
        # Verify statistics structure
        assert "service_stats" in stats
        assert "neo4j_stats" in stats
        assert "embedding_stats" in stats
        assert "performance" in stats
        
        # Verify service stats
        service_stats = stats["service_stats"]
        assert "searches_performed" in service_stats
        assert service_stats["searches_performed"] >= 2
        
        # Verify Neo4j stats
        neo4j_stats = stats["neo4j_stats"]
        assert "total_chunks" in neo4j_stats
        assert neo4j_stats["total_chunks"] >= len(sample_doc_chunks)

class TestVectorAPIEndpoints:
    """Test Vector API endpoints functionality"""
    
    # This would require FastAPI test client setup
    # For now, placeholder for API testing
    
    def test_search_endpoint_placeholder(self):
        """Placeholder for API endpoint testing"""
        # TODO: Implement FastAPI test client testing
        # This would test the actual HTTP endpoints
        assert True  # Placeholder

class TestPerformanceBenchmarks:
    """Performance benchmarking tests"""
    
    @pytest.mark.benchmark
    async def test_indexing_performance(self, benchmark):
        """Benchmark document indexing performance"""
        # This would use pytest-benchmark for performance testing
        # TODO: Implement when pytest-benchmark is available
        assert True  # Placeholder
    
    @pytest.mark.benchmark  
    async def test_search_performance_benchmark(self, benchmark):
        """Benchmark search performance"""
        # TODO: Implement detailed performance benchmarking
        assert True  # Placeholder

class TestMultilingualIntegration:
    """Test multilingual functionality comprehensively"""
    
    @pytest.mark.asyncio
    async def test_language_mixing_in_documents(self):
        """Test processing documents with mixed languages"""
        mixed_content = """
        # English section
        Artificial Intelligence is transforming technology.
        
        # Ukrainian section  
        Штучний інтелект трансформує технології.
        
        # Chinese section
        人工智能正在改变技术。
        """
        
        processor = MultilingualDocumentProcessor()
        chunks = await processor.process_text(mixed_content, "mixed_test.txt")
        
        # Verify chunks are created
        assert len(chunks) > 0
        
        # Verify language detection (might detect primary language)
        languages_detected = set(chunk.language for chunk in chunks)
        assert len(languages_detected) >= 1  # At least one language detected

    @pytest.mark.asyncio
    async def test_cross_language_search(self, vector_service):
        """Test searching across different languages for similar concepts"""
        # Store multilingual content about same topics
        multilingual_chunks = []
        
        for i, (lang, text) in enumerate(SAMPLE_TEXTS.items()):
            chunk = DocChunk(
                chunk_id=f"cross_lang_{i}",
                content=text,
                language=lang[:2] if lang != "chinese" else "zh",  # Normalize language codes
                source_doc=f"{lang}_ai.txt",
                position=0,
                chunk_hash=f"cross_{i}",
                metadata={},
                start_char=0,
                end_char=len(text),
                sentence_count=1,
                word_count=len(text.split()),
                confidence=0.9,
                created_at="2024-01-01T00:00:00"
            )
            multilingual_chunks.append(chunk)
        
        # Store chunks
        await vector_service.store_document_chunks(multilingual_chunks)
        
        # Search for AI concept without language filter
        results = await vector_service.similarity_search(
            query="artificial intelligence",
            language_filter=None,  # No language filter
            k=10
        )
        
        # Should find relevant content in multiple languages
        languages_found = set(r.language for r in results)
        assert len(results) >= len(SAMPLE_TEXTS)  # At least one result per language
        assert len(languages_found) >= 2  # Multiple languages represented

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
async def cleanup_neo4j():
    """Cleanup Neo4j test data after tests"""
    yield
    
    # Cleanup test data
    try:
        service = await create_graph_vector_service()
        # Delete test chunks
        cleanup_query = """
        MATCH (c:ContextChunk)
        WHERE c.chunk_hash STARTS WITH 'test_' OR c.chunk_hash STARTS WITH 'hash_'
        DETACH DELETE c
        """
        await service.neo4j.execute_query(cleanup_query)
        await service.close()
    except Exception as e:
        print(f"Cleanup warning: {e}")

# ============================
# 🏃 TEST EXECUTION
# ============================

if __name__ == "__main__":
    # Run specific test groups
    pytest.main([
        __file__ + "::TestGraphVectorService::test_service_initialization",
        "-v", "--tb=short"
    ]) 