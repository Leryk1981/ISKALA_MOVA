"""
🔧 ISKALA Tool Server Extension for Graph Search
Extension module that adds Graph Search capabilities to existing ISKALA OpenAPI Tool Server

This module provides:
- New endpoints for Graph Search integration
- OpenAPI schema extensions  
- Request/response handling
- Error management and logging
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

# Import our schemas
from ..schemas.requests import (
    GraphHybridSearchRequest,
    GraphVectorSearchRequest,
    GraphWalkRequest,
    GraphSuggestionsRequest
)
from ..schemas.responses import (
    GraphSearchResponse,
    GraphWalkResponse,
    GraphSuggestionsResponse,
    GraphStatusResponse,
    GraphSearchResult,
    ComponentStatus
)
from ..config import (
    config,
    get_graph_search_url,
    get_auth_headers,
    GRAPH_SEARCH_ENDPOINTS,
    OPENAPI_OPERATIONS
)

logger = logging.getLogger(__name__)

class GraphSearchToolServerExtension:
    """
    🔍 Extension class for integrating Graph Search into ISKALA Tool Server
    
    This class provides methods to:
    - Handle Graph Search API requests
    - Proxy requests to ISKALA Graph Search Service
    - Convert responses to Tool Server format
    - Manage errors and logging
    """
    
    def __init__(self):
        self.graph_search_url = get_graph_search_url()
        self.auth_headers = get_auth_headers()
        self.client = None
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.last_health_check = None
        
        logger.info(f"🔍 Graph Search Extension initialized - URL: {self.graph_search_url}")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for Graph Search requests"""
        if self.client is None:
            timeout = httpx.Timeout(config.REQUEST_TIMEOUT)
            self.client = httpx.AsyncClient(
                timeout=timeout,
                headers=self.auth_headers,
                follow_redirects=True
            )
        return self.client
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Graph Search service with error handling"""
        start_time = time.time()
        
        try:
            client = await self._get_client()
            url = f"{self.graph_search_url}{endpoint}"
            
            # Make request with retries
            for attempt in range(config.MAX_RETRIES):
                try:
                    if method.upper() == "GET":
                        response = await client.get(url, params=data or {})
                    else:
                        response = await client.request(method, url, json=data)
                    
                    response.raise_for_status()
                    
                    # Update performance metrics
                    response_time = time.time() - start_time
                    self.request_count += 1
                    self.total_response_time += response_time
                    
                    logger.info(f"✅ Graph Search request: {method} {endpoint} - {response.status_code} ({response_time:.3f}s)")
                    return response.json()
                
                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500 and attempt < config.MAX_RETRIES - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"⚠️ Retry {attempt + 1}/{config.MAX_RETRIES} after {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise
                
                except (httpx.RequestError, httpx.TimeoutException) as e:
                    if attempt < config.MAX_RETRIES - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"⚠️ Network retry {attempt + 1}/{config.MAX_RETRIES} after {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        raise
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Graph Search HTTP error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Graph Search service error: {e.response.text}"
            )
        
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"❌ Graph Search connection error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Graph Search service unavailable: {str(e)}"
            )
        
        except Exception as e:
            logger.error(f"❌ Graph Search unexpected error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Internal Graph Search error: {str(e)}"
            )
    
    # Graph Search endpoint handlers
    
    async def hybrid_search(self, request: GraphHybridSearchRequest) -> Dict[str, Any]:
        """Handle hybrid semantic search requests"""
        logger.info(f"🔍 Hybrid search: '{request.query[:50]}...', lang={request.language}")
        
        # Convert request to Graph Search format
        search_data = {
            "query": request.query,
            "language": request.language,
            "k": request.k,
            "intent_filter": request.intent_filter,
            "include_facets": request.include_facets,
            "vector_weight": request.vector_weight,
            "graph_weight": request.graph_weight,
            "intent_weight": request.intent_weight,
            "language_weight": request.language_weight
        }
        
        # Make request to Graph Search service
        response = await self._make_request("POST", "/search/hybrid", search_data)
        
        # Transform response for Tool Server compatibility
        return self._transform_search_response(response, request.query)
    
    async def vector_search(self, request: GraphVectorSearchRequest) -> Dict[str, Any]:
        """Handle vector-only search requests"""
        logger.info(f"🔍 Vector search: '{request.query[:50]}...', lang={request.language}")
        
        search_data = {
            "query": request.query,
            "language_filter": request.language,
            "k": request.k,
            "confidence_threshold": request.confidence_threshold
        }
        
        # Use vector endpoint from GraphVectorService
        response = await self._make_request("POST", "/vector/search", search_data)
        
        return self._transform_search_response(response, request.query)
    
    async def graph_walk(self, request: GraphWalkRequest) -> Dict[str, Any]:
        """Handle knowledge graph traversal requests"""
        logger.info(f"🕸️ Graph walk from: {request.start_node_id}, depth={request.max_depth}")
        
        walk_data = {
            "start_node_id": request.start_node_id,
            "max_depth": request.max_depth,
            "intent_filter": request.intent_filter,
            "include_confidence": request.include_confidence
        }
        
        response = await self._make_request("POST", "/search/graph-walk", walk_data)
        
        return self._transform_walk_response(response)
    
    async def search_suggestions(self, request: GraphSuggestionsRequest) -> Dict[str, Any]:
        """Handle search suggestions requests"""
        logger.info(f"💡 Suggestions for: '{request.partial_query}', lang={request.language}")
        
        suggestions_data = {
            "partial_query": request.partial_query,
            "language": request.language,
            "limit": request.limit
        }
        
        response = await self._make_request("POST", "/search/suggestions", suggestions_data)
        
        return self._transform_suggestions_response(response)
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Graph Search service status"""
        logger.info("📊 Getting Graph Search status")
        
        try:
            response = await self._make_request("GET", "/search/health")
            self.last_health_check = datetime.utcnow()
            
            return self._transform_status_response(response)
        
        except Exception as e:
            logger.error(f"❌ Status check failed: {e}")
            return {
                "service": "ISKALA Graph Search",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "components": {
                    "graph_search_service": {
                        "status": "error",
                        "error": str(e)
                    }
                }
            }
    
    # Response transformation methods
    
    def _transform_search_response(self, response: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Transform Graph Search response to Tool Server format"""
        try:
            # Ensure compatibility with Tool Server expectations
            transformed = {
                "success": True,
                "query": original_query,
                "results": response.get("results", []),
                "total_results": response.get("total_results", 0),
                "search_time_ms": response.get("search_time_ms", 0.0),
                "metadata": {
                    "service": "ISKALA Graph Search",
                    "response_type": "search",
                    "cache_hit": response.get("cache_hit", False),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # Add facets if present
            if "facets" in response:
                transformed["facets"] = response["facets"]
            
            # Add search strategy breakdown if present
            if "vector_results_count" in response:
                transformed["search_breakdown"] = {
                    "vector_results": response.get("vector_results_count", 0),
                    "graph_results": response.get("graph_results_count", 0),
                    "hybrid_results": response.get("hybrid_results_count", 0)
                }
            
            return transformed
            
        except Exception as e:
            logger.error(f"❌ Response transformation error: {e}")
            return {
                "success": False,
                "error": f"Response transformation failed: {str(e)}",
                "query": original_query,
                "results": [],
                "total_results": 0
            }
    
    def _transform_walk_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Graph Walk response"""
        try:
            return {
                "success": True,
                "start_node_id": response.get("start_node_id"),
                "paths": response.get("paths", []),
                "total_paths": response.get("total_paths", 0),
                "walk_time_ms": response.get("walk_time_ms", 0.0),
                "metadata": {
                    "service": "ISKALA Graph Search",
                    "response_type": "graph_walk",
                    "max_depth_reached": response.get("max_depth_reached", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ Walk response transformation error: {e}")
            return {
                "success": False,
                "error": f"Walk response transformation failed: {str(e)}",
                "paths": [],
                "total_paths": 0
            }
    
    def _transform_suggestions_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Suggestions response"""
        try:
            return {
                "success": True,
                "partial_query": response.get("partial_query"),
                "suggestions": response.get("suggestions", []),
                "suggestion_count": response.get("suggestion_count", 0),
                "generation_time_ms": response.get("generation_time_ms", 0.0),
                "metadata": {
                    "service": "ISKALA Graph Search",
                    "response_type": "suggestions",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ Suggestions response transformation error: {e}")
            return {
                "success": False,
                "error": f"Suggestions transformation failed: {str(e)}",
                "suggestions": [],
                "suggestion_count": 0
            }
    
    def _transform_status_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Status response"""
        try:
            # Add extension-specific metrics
            avg_response_time = (
                self.total_response_time / self.request_count 
                if self.request_count > 0 else 0.0
            )
            
            transformed = response.copy()
            transformed.update({
                "metadata": {
                    "integration_layer": "ISKALA Tool Server Extension",
                    "total_requests": self.request_count,
                    "avg_response_time_ms": avg_response_time * 1000,
                    "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
                }
            })
            
            return transformed
            
        except Exception as e:
            logger.error(f"❌ Status response transformation error: {e}")
            return response  # Return original if transformation fails
    
    # Utility methods
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the extension"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        return {
            "total_requests": self.request_count,
            "avg_response_time_ms": avg_response_time * 1000,
            "service_url": self.graph_search_url,
            "auth_enabled": bool(self.auth_headers),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None
        }
    
    async def close(self):
        """Cleanup HTTP client"""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("✅ Graph Search extension HTTP client closed")

# OpenAPI Schema Extensions
def get_graph_search_openapi_extensions() -> Dict[str, Any]:
    """
    Generate OpenAPI schema extensions for Graph Search endpoints
    
    Returns the paths to be added to the existing OPENAPI_SCHEMA
    """
    
    return {
        "/iskala/graph/search_hybrid": {
            "post": {
                "operationId": "graph_search_hybrid",
                "summary": OPENAPI_OPERATIONS["graph_search_hybrid"]["summary"],
                "description": OPENAPI_OPERATIONS["graph_search_hybrid"]["description"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": "Пошуковий запит",
                                        "example": "штучний інтелект машинне навчання"
                                    },
                                    "language": {
                                        "type": "string",
                                        "description": "Мова для фільтрації (uk, en, ru, zh, etc.)",
                                        "example": "uk"
                                    },
                                    "k": {
                                        "type": "integer",
                                        "default": 5,
                                        "description": "Кількість результатів"
                                    },
                                    "intent_filter": {
                                        "type": "string",
                                        "description": "Фільтр за наміром"
                                    },
                                    "include_facets": {
                                        "type": "boolean",
                                        "default": False,
                                        "description": "Включити агрегації"
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результати гібридного пошуку",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/iskala/graph/search_vector": {
            "post": {
                "operationId": "graph_search_vector",
                "summary": OPENAPI_OPERATIONS["graph_search_vector"]["summary"],
                "description": OPENAPI_OPERATIONS["graph_search_vector"]["description"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Пошуковий запит"},
                                    "language": {"type": "string", "description": "Мова фільтрації"},
                                    "k": {"type": "integer", "default": 5, "description": "Кількість результатів"},
                                    "confidence_threshold": {"type": "number", "default": 0.0, "description": "Поріг впевненості"}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результати векторного пошуку",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/iskala/graph/walk": {
            "post": {
                "operationId": "graph_walk",
                "summary": OPENAPI_OPERATIONS["graph_walk"]["summary"],
                "description": OPENAPI_OPERATIONS["graph_walk"]["description"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "start_node_id": {"type": "string", "description": "Початковий вузол"},
                                    "max_depth": {"type": "integer", "default": 3, "description": "Максимальна глибина"},
                                    "intent_filter": {"type": "array", "items": {"type": "string"}, "description": "Фільтр намірів"}
                                },
                                "required": ["start_node_id"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Шляхи обходу графа",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/iskala/graph/suggestions": {
            "post": {
                "operationId": "graph_suggestions",
                "summary": OPENAPI_OPERATIONS["graph_suggestions"]["summary"],
                "description": OPENAPI_OPERATIONS["graph_suggestions"]["description"],
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "partial_query": {"type": "string", "description": "Частковий запит"},
                                    "language": {"type": "string", "description": "Мова підказок"},
                                    "limit": {"type": "integer", "default": 10, "description": "Кількість підказок"}
                                },
                                "required": ["partial_query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Пошукові підказки",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        },
        "/iskala/graph/status": {
            "get": {
                "operationId": "graph_status",
                "summary": OPENAPI_OPERATIONS["graph_status"]["summary"],
                "description": OPENAPI_OPERATIONS["graph_status"]["description"],
                "responses": {
                    "200": {
                        "description": "Статус Graph Search сервісу",
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                }
            }
        }
    }

# Global extension instance
graph_extension = GraphSearchToolServerExtension()

# Export main components
__all__ = [
    "GraphSearchToolServerExtension",
    "get_graph_search_openapi_extensions",
    "graph_extension"
] 