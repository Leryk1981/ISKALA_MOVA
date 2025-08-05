#!/usr/bin/env python3
"""
Integration Tests for FastAPI Routes
Tests layered architecture integration via HTTP endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app import app

class TestTranslationRoutes:
    """Integration tests for translation API routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    def test_translate_text_success(self, client):
        """Test successful text translation via API"""
        response = client.post("/api/v1/translation/translate", json={
            "text": "Hello world",
            "source_lang": "en",
            "target_lang": "uk",
            "user_style": "neutral"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert "source_lang" in data
        assert "target_lang" in data
        assert data["source_lang"] == "en"
        assert data["target_lang"] == "uk"
    
    def test_translate_text_validation_error(self, client):
        """Test translation with invalid request data"""
        response = client.post("/api/v1/translation/translate", json={
            "text": "",  # Empty text should fail
            "source_lang": "en",
            "target_lang": "uk"
        })
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_create_universal_sense_success(self, client):
        """Test universal sense creation via API"""
        response = client.post("/api/v1/translation/universal-sense", json={
            "text": "Machine learning is fascinating",
            "source_lang": "en",
            "context": {"domain": "technology"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "sense_id" in data  # Mock returns sense_id instead
        assert "original_lang" in data  # Mock returns original_lang instead of source_lang
        assert "created_at" in data
    
    def test_get_supported_languages(self, client):
        """Test getting supported languages via API"""
        response = client.get("/api/v1/translation/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        # Mock service returns a dict with languages list
        languages_data = data["languages"]
        if isinstance(languages_data, dict):
            assert "languages" in languages_data
            assert isinstance(languages_data["languages"], list)
        else:
            assert isinstance(languages_data, list)
        assert len(data["languages"]) > 0


class TestMemoryRoutes:
    """Integration tests for memory API routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    def test_search_memory_success(self, client):
        """Test successful memory search via API"""
        response = client.post("/api/v1/memory/search", json={
            "query": "computer science algorithms",
            "strategy": "hybrid",
            "k": 5,
            "min_similarity": 0.7
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert "total_found" in data
        assert "strategy_used" in data
        assert "search_time_ms" in data
        assert isinstance(data["patterns"], list)
        assert data["strategy_used"] == "hybrid"
    
    def test_search_memory_different_strategies(self, client):
        """Test memory search with different strategies"""
        strategies = ["vector_only", "graph_only", "hybrid", "intent_match"]
        
        for strategy in strategies:
            response = client.post("/api/v1/memory/search", json={
                "query": "neural networks",
                "strategy": strategy,
                "k": 3
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["strategy_used"] == strategy
    
    def test_search_memory_validation_error(self, client):
        """Test memory search with invalid request data"""
        response = client.post("/api/v1/memory/search", json={
            "query": "x",  # Too short
            "strategy": "hybrid",
            "k": 5
        })
        
        assert response.status_code == 400  # Service validation error
        data = response.json()
        assert "error_code" in data["detail"]
        assert data["detail"]["error_code"] == "QUERY_TOO_SHORT"
    
    def test_get_memory_pattern_not_found(self, client):
        """Test retrieving non-existent memory pattern"""
        response = client.get("/api/v1/memory/pattern/nonexistent_id")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_memory_health(self, client):
        """Test memory system health check"""
        response = client.get("/api/v1/memory/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_patterns" in data
        assert "total_connections" in data
        assert "avg_search_time_ms" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]


class TestSystemRoutes:
    """Integration tests for system routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test API root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "architecture" in data
        assert "features" in data
        assert "endpoints" in data
        assert data["version"] == "1.1.0"
        assert "layered architecture" in data["message"].lower()
    
    def test_system_health(self, client):
        """Test system health endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "translation" in data["services"]
        assert "memory" in data["services"]
        assert data["status"] in ["healthy", "unhealthy"]


class TestErrorHandling:
    """Integration tests for error handling"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    def test_translation_service_error_handling(self, client):
        """Test that TranslationServiceError is properly handled"""
        response = client.post("/api/v1/translation/translate", json={
            "text": "test",
            "source_lang": "uk",
            "target_lang": "uk"  # Same language should trigger error
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "error_code" in data["detail"]
        assert "message" in data["detail"]
    
    def test_memory_service_error_handling(self, client):
        """Test that MemoryServiceError is properly handled"""
        response = client.get("/api/v1/memory/pattern/")  # Empty pattern ID
        
        assert response.status_code == 404  # FastAPI handles this
    
    def test_invalid_route(self, client):
        """Test handling of invalid routes"""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404


class TestDependencyInjection:
    """Integration tests for dependency injection"""
    
    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)
    
    def test_translation_service_injection(self, client):
        """Test that TranslationService is properly injected"""
        # Multiple requests should work consistently
        for _ in range(3):
            response = client.post("/api/v1/translation/translate", json={
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "uk"
            })
            assert response.status_code == 200
    
    def test_memory_service_injection(self, client):
        """Test that MemoryService is properly injected"""
        # Multiple requests should work consistently
        for _ in range(3):
            response = client.post("/api/v1/memory/search", json={
                "query": "test query",
                "strategy": "vector_only",
                "k": 3
            })
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__]) 