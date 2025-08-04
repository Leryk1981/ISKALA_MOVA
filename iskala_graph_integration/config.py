"""
🔧 Configuration for ISKALA Graph Integration
Settings for Tool Server integration, authentication, and service URLs
"""

import os
from typing import Optional

# Fix for Pydantic v2 - BaseSettings moved to pydantic-settings
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for environments without pydantic-settings
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

from pydantic import Field

class GraphIntegrationConfig(BaseSettings):
    """Configuration settings for ISKALA Graph Integration"""
    
    # Service URLs
    TOOL_SERVER_URL: str = Field(
        default="http://localhost:8003",
        description="ISKALA OpenAPI Tool Server URL"
    )
    
    GRAPH_SEARCH_URL: str = Field(
        default="http://localhost:8004", 
        description="ISKALA Graph Search Service URL"
    )
    
    # Docker internal URLs (for containerized deployment)
    TOOL_SERVER_DOCKER_URL: str = Field(
        default="http://iskala-openapi:8003",
        description="Tool Server URL in Docker network"
    )
    
    GRAPH_SEARCH_DOCKER_URL: str = Field(
        default="http://iskala-graph:8004",
        description="Graph Search URL in Docker network"
    )
    
    # Authentication
    AUTH_TOKEN: Optional[str] = Field(
        default=None,
        description="Bearer token for API authentication"
    )
    
    # Security settings
    ENABLE_AUTH: bool = Field(
        default=False,
        description="Enable authentication for Graph Search endpoints"
    )
    
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit requests per minute per user"
    )
    
    # Performance settings
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="HTTP request timeout in seconds"
    )
    
    MAX_RETRIES: int = Field(
        default=3,
        description="Maximum number of retries for failed requests"
    )
    
    # Integration mode
    INTEGRATION_MODE: str = Field(
        default="extend",
        description="Integration mode: 'extend' (modify existing server) or 'separate' (new server)"
    )
    
    # Graph Search specific settings
    DEFAULT_SEARCH_LIMIT: int = Field(
        default=5,
        description="Default number of search results to return"
    )
    
    DEFAULT_LANGUAGE: str = Field(
        default="uk",
        description="Default language for search queries"
    )
    
    ENABLE_CACHING: bool = Field(
        default=True,
        description="Enable Redis caching for search results"
    )
    
    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Logging format"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "ISKALA_GRAPH_"
        case_sensitive = True

# Global configuration instance
config = GraphIntegrationConfig()

# Convenience functions
def get_tool_server_url() -> str:
    """Get appropriate Tool Server URL"""
    if os.getenv("DOCKER_ENV") == "true":
        return config.TOOL_SERVER_DOCKER_URL
    return config.TOOL_SERVER_URL

def get_graph_search_url() -> str:
    """Get appropriate Graph Search URL"""
    if os.getenv("DOCKER_ENV") == "true": 
        return config.GRAPH_SEARCH_DOCKER_URL
    return config.GRAPH_SEARCH_URL

def is_production() -> bool:
    """Check if running in production environment"""
    return os.getenv("ISKALA_ENV") == "production"

def get_auth_headers() -> dict:
    """Get authentication headers if configured"""
    if config.AUTH_TOKEN:
        return {"Authorization": f"Bearer {config.AUTH_TOKEN}"}
    return {}

# Integration constants
GRAPH_SEARCH_ENDPOINTS = {
    "hybrid_search": "/iskala/graph/search_hybrid",
    "vector_search": "/iskala/graph/search_vector", 
    "graph_walk": "/iskala/graph/walk",
    "suggestions": "/iskala/graph/suggestions",
    "status": "/iskala/graph/status"
}

OPENAPI_OPERATIONS = {
    "graph_search_hybrid": {
        "summary": "Гібридний семантичний пошук",
        "description": "Поєднує векторний пошук з обходом графа знань для інтелектуального пошуку"
    },
    "graph_search_vector": {
        "summary": "Векторний семантичний пошук", 
        "description": "Пошук на основі векторних embeddings з підтримкою мультимовності"
    },
    "graph_walk": {
        "summary": "Обхід графа знань",
        "description": "Динамічний обхід графа для пошуку пов'язаних концептів"
    },
    "graph_suggestions": {
        "summary": "Інтелектуальні підказки",
        "description": "Автодоповнення пошукових запитів на основі Intent графа"
    },
    "graph_status": {
        "summary": "Статус Graph Search",
        "description": "Статус сервісів семантичного пошуку та графа знань"
    }
}

# Export configuration
__all__ = [
    "GraphIntegrationConfig",
    "config",
    "get_tool_server_url", 
    "get_graph_search_url",
    "is_production",
    "get_auth_headers",
    "GRAPH_SEARCH_ENDPOINTS",
    "OPENAPI_OPERATIONS"
] 