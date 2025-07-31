"""
ISKALA Core - Объединенная версия
Запуск всех сервисов в одном приложении
"""

import asyncio
import logging
import os
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
import threading
import time

# Загрузка переменных окружения
load_dotenv()

# Импорт модулей
from llm_agent_v2 import LLMAgentV2

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="ISKALA Core",
    description="Объединенная система ISKALA с RAG, Vault, Translation и Shield",
    version="2.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы
app.mount("/static", StaticFiles(directory=".."), name="static")

# Глобальные переменные
llm_agent = LLMAgentV2()
active_connections: List[WebSocket] = []

# Pydantic модели
class UserRequest(BaseModel):
    request: str
    context: Dict[str, Any] = {}

class ExecutionRequest(BaseModel):
    request: str
    llm_response: str
    actions: List[Dict[str, Any]]

class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

# WebSocket менеджер
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Новое WebSocket соединение. Всего: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket соединение закрыто. Всего: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps({
                "type": "message",
                "content": message,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")

manager = ConnectionManager()

# Основные эндпоинты ISKALA
@app.get("/")
async def root():
    return {
        "message": "ISKALA Core - Объединенная система",
        "version": "2.0.0",
        "services": {
            "main": "http://localhost:8001",
            "vault": "http://localhost:8081",
            "translation": "http://localhost:8082",
            "rag": "http://localhost:8002",
            "viewer": "http://localhost:5000"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ISKALA Core",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "main": "online",
            "vault": "online",
            "translation": "online",
            "rag": "online"
        }
    }

# LLM API
@app.post("/api/llm/process")
async def process_llm_request(request: UserRequest):
    try:
        result = await llm_agent.process_request(request.request)
        return {
            "success": True,
            "llm_response": result["llm_response"],
            "needs_confirmation": result["needs_confirmation"],
            "suggested_actions": result["suggested_actions"]
        }
    except Exception as e:
        logger.error(f"Ошибка обработки LLM запроса: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket для чата
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_personal_message(
            "Добро пожаловать в ISKALA Core!", 
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "user_message":
                user_request = message_data.get("content", "")
                result = await llm_agent.process_request(user_request)
                
                response = {
                    "type": "llm_response",
                    "llm_response": result["llm_response"],
                    "needs_confirmation": result["needs_confirmation"],
                    "suggested_actions": result["suggested_actions"],
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Vault API (интегрированный)
@app.get("/vault/health")
async def vault_health():
    return {"status": "healthy", "service": "Vault"}

@app.post("/vault/encrypt")
async def vault_encrypt(data: Dict[str, Any]):
    # Здесь будет логика шифрования
    return {"encrypted": True, "data": "encrypted_data"}

# Translation API (интегрированный)
@app.get("/translation/health")
async def translation_health():
    return {"status": "healthy", "service": "Translation"}

@app.post("/translation/translate")
async def translate_text(request: Dict[str, Any]):
    # Здесь будет логика перевода
    return {"translated": True, "text": "translated_text"}

# RAG API (интегрированный)
@app.get("/rag/health")
async def rag_health():
    return {"status": "healthy", "service": "RAG"}

@app.post("/rag/search")
async def rag_search(request: Dict[str, Any]):
    # Здесь будет логика поиска
    return {"results": [], "query": request.get("query", "")}

# Shield API (интегрированный)
@app.get("/shield/health")
async def shield_health():
    return {"status": "healthy", "service": "Shield"}

@app.post("/shield/validate")
async def shield_validate(request: Dict[str, Any]):
    # Здесь будет логика валидации
    return {"valid": True, "message": "Validation passed"}

# Запуск дополнительных сервисов
def start_vault_service():
    """Запуск Vault сервиса на порту 8081"""
    import uvicorn
    from fastapi import FastAPI as VaultApp
    
    vault_app = VaultApp(title="ISKALA Vault")
    
    @vault_app.get("/")
    async def vault_root():
        return {"service": "Vault", "port": 8081}
    
    uvicorn.run(vault_app, host="0.0.0.0", port=8081)

def start_translation_service():
    """Запуск Translation сервиса на порту 8082"""
    import uvicorn
    from fastapi import FastAPI as TranslationApp
    
    translation_app = TranslationApp(title="ISKALA Translation")
    
    @translation_app.get("/")
    async def translation_root():
        return {"service": "Translation", "port": 8082}
    
    uvicorn.run(translation_app, host="0.0.0.0", port=8082)

def start_rag_service():
    """Запуск RAG сервиса на порту 8002"""
    import uvicorn
    from fastapi import FastAPI as RAGApp
    
    rag_app = RAGApp(title="ISKALA RAG")
    
    @rag_app.get("/")
    async def rag_root():
        return {"service": "RAG", "port": 8002}
    
    uvicorn.run(rag_app, host="0.0.0.0", port=8002)

# Запуск всех сервисов
def start_all_services():
    """Запуск всех сервисов в отдельных потоках"""
    services = [
        ("Vault", start_vault_service),
        ("Translation", start_translation_service),
        ("RAG", start_rag_service)
    ]
    
    threads = []
    for name, service_func in services:
        thread = threading.Thread(target=service_func, name=name)
        thread.daemon = True
        thread.start()
        threads.append(thread)
        logger.info(f"Запущен сервис: {name}")
        time.sleep(1)  # Небольшая задержка между запусками
    
    return threads

if __name__ == "__main__":
    # Запуск дополнительных сервисов
    service_threads = start_all_services()
    
    # Запуск основного приложения
    uvicorn.run(app, host="0.0.0.0", port=8001) 