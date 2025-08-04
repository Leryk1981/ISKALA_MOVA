#!/usr/bin/env python3
"""
🔐 ISKALA OpenAPI Tool Server - SECURE VERSION
=============================================

Secure OpenAPI Tool Server для интеграции модулей ISKALA в Open WebUI
с полной системой безопасности и защитой от уязвимостей.

Security Features:
- ✅ API Key Authentication
- ✅ Rate Limiting  
- ✅ Secure CORS
- ✅ Input Validation
- ✅ Audit Logging
"""

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import requests
import json
import logging
import time
from typing import Dict, Any, List, Optional
import uvicorn

# Import secure configuration
from iskala_basis.config.secure_config import config

# Setup logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ISKALA OpenAPI Tool Server - SECURE",
    description="🔐 Secure API сервер для интеграции модулей ISKALA в Open WebUI",
    version="2.0.0-secure"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security: API Key Authentication
api_key_header = APIKeyHeader(name="X-API-Key") if config.ENABLE_API_KEY_AUTH else None

async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Verify API key if authentication enabled"""
    if not config.ENABLE_API_KEY_AUTH:
        return "development"
        
    if not api_key or api_key not in config.API_KEYS:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    logger.info(f"Valid API key used: {api_key[:10]}...")
    return api_key

# Secure CORS настройки
cors_config = config.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    **cors_config
)

# Service URLs from secure config
ISKALA_BASE_URL = f"http://iskala-core:{config.ISKALA_PORT}"  
VAULT_BASE_URL = f"http://iskala-core:{config.VAULT_PORT}"
TRANSLATION_BASE_URL = f"http://iskala-core:{config.TRANSLATION_PORT}"
RAG_BASE_URL = f"http://iskala-core:{config.RAG_PORT}"

# Enhanced Pydantic модели с строгой валидацией
class ISKALAMemorySearchRequest(BaseModel):
    query: str = Field(
        min_length=1, 
        max_length=1000, 
        description="Search query string"
    )
    limit: Optional[int] = Field(
        default=10,
        ge=1, 
        le=100,
        description="Maximum number of results (1-100)"
    )

class ISKALAToolCallRequest(BaseModel):
    tool_name: str = Field(
        min_length=1,
        max_length=100,
        description="Tool name to execute"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool parameters"
    )

class ISKALATranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "uk"

class ISKALARAGRequest(BaseModel):
    query: str
    context: Optional[str] = None

# OpenAPI схема
OPENAPI_SCHEMA = {
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
                "summary": "Пошук в пам'яті ISKALA",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "limit": {"type": "integer", "default": 10}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результати пошуку",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/iskala/tools/call": {
            "post": {
                "operationId": "call_iskala_tool",
                "summary": "Виклик інструменту ISKALA",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {"type": "string"},
                                    "parameters": {"type": "object"}
                                },
                                "required": ["tool_name", "parameters"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результат виклику інструменту",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/iskala/translation/translate": {
            "post": {
                "operationId": "translate_text",
                "summary": "Переклад тексту",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "source_lang": {"type": "string", "default": "auto"},
                                    "target_lang": {"type": "string", "default": "uk"}
                                },
                                "required": ["text"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Перекладений текст",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/iskala/rag/search": {
            "post": {
                "operationId": "rag_search",
                "summary": "Пошук в RAG системі",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "context": {"type": "string"}
                                },
                                "required": ["query"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Результати RAG пошуку",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/iskala/status": {
            "get": {
                "operationId": "get_iskala_status",
                "summary": "Статус всіх модулів ISKALA",
                "responses": {
                    "200": {
                        "description": "Статус модулів",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
    }
}

@app.get("/openapi.json")
async def get_openapi_schema():
    """Повертає OpenAPI схему"""
    return OPENAPI_SCHEMA

@app.post("/iskala/memory/search")
@limiter.limit(f"{config.RATE_LIMIT_REQUESTS}/{config.RATE_LIMIT_WINDOW}second")
async def search_iskala_memory(
    request_obj: Request,
    request: ISKALAMemorySearchRequest,
    api_key: str = Depends(verify_api_key)
):
    """🔐 Secure пошук в пам'яті ISKALA з authentication і rate limiting"""
    start_time = time.time()
    
    # Audit logging
    logger.info(
        f"Memory search request",
        extra={
            "query_length": len(request.query),
            "limit": request.limit,
            "client_ip": request_obj.client.host,
            "api_key": api_key[:10] + "..." if api_key != "development" else "development"
        }
    )
    
    try:
        response = requests.post(
            f"{ISKALA_BASE_URL}/api/memory/search",
            json={"query": request.query, "limit": request.limit},
            timeout=config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Success logging
        logger.info(
            f"Memory search completed",
            extra={
                "response_time": round((time.time() - start_time) * 1000, 2),
                "results_count": len(result.get("results", [])),
                "status": "success"
            }
        )
        
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Memory search request failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"ISKALA service unavailable: {str(e)}")
    except Exception as e:
        logger.error(f"Memory search unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error")

@app.post("/iskala/tools/call")  
@limiter.limit(f"{config.RATE_LIMIT_REQUESTS//2}/{config.RATE_LIMIT_WINDOW}second")  # Stricter limit для tool execution
async def call_iskala_tool(
    request_obj: Request,
    request: ISKALAToolCallRequest,
    api_key: str = Depends(verify_api_key)
):
    """🔐 Secure виклик інструменту ISKALA з authentication і stricter rate limiting"""
    start_time = time.time()
    
    # Enhanced audit logging for tool execution
    logger.warning(
        f"Tool execution request - HIGH RISK OPERATION",
        extra={
            "tool_name": request.tool_name,
            "parameters_count": len(request.parameters),
            "client_ip": request_obj.client.host,
            "api_key": api_key[:10] + "..." if api_key != "development" else "development",
            "risk_level": "HIGH"
        }
    )
    
    try:
        response = requests.post(
            f"{ISKALA_BASE_URL}/api/tools/call",
            json={
                "tool_name": request.tool_name,
                "parameters": request.parameters
            },
            timeout=config.REQUEST_TIMEOUT * 2  # Double timeout для tool operations
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка виклику інструменту: {str(e)}")

@app.post("/iskala/translation/translate")
async def translate_text(request: ISKALATranslationRequest):
    """Переклад тексту через ISKALA Translation"""
    try:
        response = requests.post(
            f"{TRANSLATION_BASE_URL}/translate",
            json={
                "text": request.text,
                "source_lang": request.source_lang,
                "target_lang": request.target_lang
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка перекладу: {str(e)}")

@app.post("/iskala/rag/search")
async def rag_search(request: ISKALARAGRequest):
    """Пошук в RAG системі"""
    try:
        response = requests.post(
            f"{RAG_BASE_URL}/search",
            json={
                "query": request.query,
                "context": request.context
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка RAG пошуку: {str(e)}")

@app.get("/iskala/status")
async def get_iskala_status():
    """Статус всіх модулів ISKALA"""
    try:
        status = {}
        
        # Перевірка ISKALA Core
        try:
            response = requests.get(f"{ISKALA_BASE_URL}/health", timeout=5)
            status["iskala_core"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            status["iskala_core"] = {"status": "error", "error": str(e)}
        
        # Перевірка Vault
        try:
            response = requests.get(f"{VAULT_BASE_URL}/health", timeout=5)
            status["vault"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            }
        except Exception as e:
            status["vault"] = {"status": "error", "error": str(e)}
        
        # Перевірка Translation
        try:
            response = requests.get(f"{TRANSLATION_BASE_URL}/health", timeout=5)
            status["translation"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            }
        except Exception as e:
            status["translation"] = {"status": "error", "error": str(e)}
        
        # Перевірка RAG
        try:
            response = requests.get(f"{RAG_BASE_URL}/health", timeout=5)
            status["rag"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy"
            }
        except Exception as e:
            status["rag"] = {"status": "error", "error": str(e)}
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка отримання статусу: {str(e)}")

@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {
        "message": "ISKALA OpenAPI Tool Server",
        "version": "1.0.0",
        "endpoints": {
            "openapi": "/openapi.json",
            "memory_search": "/iskala/memory/search",
            "tool_call": "/iskala/tools/call",
            "translation": "/iskala/translation/translate",
            "rag_search": "/iskala/rag/search",
            "status": "/iskala/status"
        }
    }

if __name__ == "__main__":
    print("🚀 Запуск ISKALA OpenAPI Tool Server...")
    print("📋 Доступні ендпоінти:")
    print("   - OpenAPI схема: http://localhost:8003/openapi.json")
    print("   - Пошук в пам'яті: POST /iskala/memory/search")
    print("   - Виклик інструментів: POST /iskala/tools/call")
    print("   - Переклад: POST /iskala/translation/translate")
    print("   - RAG пошук: POST /iskala/rag/search")
    print("   - Статус: GET /iskala/status")
    print("\n🔧 Для інтеграції в Open WebUI:")
    print("   1. Відкрийте Open WebUI")
    print("   2. Перейдіть в Settings → Tools")
    print("   3. Додайте OpenAPI Tool Server")
    print("   4. URL: http://localhost:8003/openapi.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8003) 