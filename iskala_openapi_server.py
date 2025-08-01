#!/usr/bin/env python3
"""
OpenAPI Tool Server для интеграции модулей ISKALA в Open WebUI
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from typing import Dict, Any, List, Optional
import uvicorn

app = FastAPI(
    title="ISKALA OpenAPI Tool Server",
    description="API сервер для интеграции модулей ISKALA в Open WebUI",
    version="1.0.0"
)

# CORS настройки для Open WebUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Конфигурация ISKALA
ISKALA_BASE_URL = "http://iskala-core:8001"
VAULT_BASE_URL = "http://iskala-core:8081"
TRANSLATION_BASE_URL = "http://iskala-core:8082"
RAG_BASE_URL = "http://iskala-core:8002"

# Pydantic модели
class ISKALAMemorySearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10

class ISKALAToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

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
async def search_iskala_memory(request: ISKALAMemorySearchRequest):
    """Пошук в пам'яті ISKALA"""
    try:
        response = requests.post(
            f"{ISKALA_BASE_URL}/api/memory/search",
            json={"query": request.query, "limit": request.limit},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка пошуку в пам'яті: {str(e)}")

@app.post("/iskala/tools/call")
async def call_iskala_tool(request: ISKALAToolCallRequest):
    """Виклик інструменту ISKALA"""
    try:
        response = requests.post(
            f"{ISKALA_BASE_URL}/api/tools/call",
            json={
                "tool_name": request.tool_name,
                "parameters": request.parameters
            },
            timeout=10
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