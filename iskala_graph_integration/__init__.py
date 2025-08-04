"""
🔍 ISKALA Graph Integration Package
Enterprise-grade integration of ISKALA Graph Search with ISKALA Tool Server

This package provides seamless integration between:
- ISKALA Graph Search Service (Semantic Search + Vector Search)
- ISKALA OpenAPI Tool Server (Open WebUI compatibility)
- Open WebUI Tools ecosystem

Components:
- adapters: FastAPI adapters for Tool Server integration
- handlers: Registration and authentication handlers
- schemas: Pydantic models for API requests/responses
- tests: Comprehensive integration testing
"""

__version__ = "1.0.0"
__title__ = "ISKALA Graph Integration"
__description__ = "Integration layer for ISKALA Graph Search with Tool Server"

__all__ = [
    "adapters",
    "handlers", 
    "schemas",
    "tests"
] 