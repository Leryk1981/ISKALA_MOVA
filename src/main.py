"""
MOVA ISKALA SRC Module
Нова архітектура на основі Agent Zero
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

# Завантаження змінних середовища
load_dotenv()

# Імпорт нової архітектури
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from llm_agent_v2 import LLMAgentV2

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення FastAPI додатку
app = FastAPI(
    title="MOVA ISKALA SRC",
    description="Система розумних контекстів та LLM агентів",
    version="2.0.0"
)

# CORS налаштування
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статичні файли
app.mount("/static", StaticFiles(directory=".."), name="static")

# Глобальні змінні
llm_agent = LLMAgentV2()
active_connections: List[WebSocket] = []

# Pydantic моделі
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
        logger.info(f"Нове WebSocket з'єднання. Всього: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket з'єднання закрито. Всього: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps({
                "type": "message",
                "content": message,
                "timestamp": datetime.now().isoformat()
            }))
        except Exception as e:
            logger.error(f"Помилка відправки повідомлення: {e}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps({
                    "type": "broadcast",
                    "content": message,
                    "timestamp": datetime.now().isoformat()
                }))
            except Exception as e:
                logger.error(f"Помилка broadcast: {e}")

manager = ConnectionManager()

# API Endpoints

@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {
        "message": "MOVA ISKALA SRC Module v2.0",
        "status": "active",
        "architecture": "Agent Zero based"
    }

@app.get("/chat")
async def chat_interface():
    """Чат інтерфейс"""
    response = FileResponse("../frontend/chat.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/frontend")
async def frontend_index():
    """Головна сторінка фронтенду"""
    return FileResponse("../frontend/index.html")

@app.get("/health")
async def health_check():
    """Перевірка стану сервісу"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "llm_agent": "active" if llm_agent else "inactive",
        "available_tools": llm_agent.get_available_tools() if llm_agent else [],
        "active_connections": len(manager.active_connections)
    }

@app.post("/api/llm/process")
async def process_llm_request(request: UserRequest):
    """Обробити запит через LLM агента"""
    try:
        result = await llm_agent.process_request(request.request)
        
        return {
            "success": True,
            "llm_response": result["llm_response"],
            "needs_confirmation": result["needs_confirmation"],
            "suggested_actions": result["suggested_actions"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка обробки LLM запиту: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/execute")
async def execute_llm_request(request: ExecutionRequest):
    """Виконати підтверджений запит"""
    try:
        result = await llm_agent.execute_confirmed_request(
            request.request,
            request.llm_response,
            request.actions
        )
        
        return {
            "success": result["success"],
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка виконання запиту: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tools/call")
async def call_tool(request: ToolCallRequest):
    """Викликати інструмент напряму"""
    try:
        result = await llm_agent.call_tool(request.tool_name, **request.parameters)
        
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка виклику інструменту: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tools")
async def get_tools():
    """Отримати список доступних інструментів"""
    try:
        tools = {}
        for tool_name in llm_agent.get_available_tools():
            tools[tool_name] = llm_agent.get_tool_info(tool_name)
        
        return {
            "success": True,
            "tools": tools,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка отримання інструментів: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory")
async def get_memory():
    """Отримати інформацію про пам'ять"""
    try:
        result = await llm_agent.call_tool("memory", action="list")
        
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка отримання пам'яті: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/memory/search")
async def search_memory(request: Dict[str, Any]):
    """Пошук в пам'яті"""
    try:
        key = request.get("key", "")
        if not key:
            raise HTTPException(status_code=400, detail="Search key is required")
        
        result = await llm_agent.call_tool("memory", action="load", key=key)
        
        return {
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Помилка пошуку в пам'яті: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoints

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для real-time комунікації"""
    await manager.connect(websocket)
    try:
        await manager.send_personal_message(
            "Ласкаво просимо до MOVA ISKALA SRC v2.0!", 
            websocket
        )
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "user_message":
                user_request = message_data.get("content", "")
                
                # Обробляємо через LLM агента
                result = await llm_agent.process_request(user_request)
                
                # Відправляємо відповідь
                response = {
                    "type": "llm_response",
                    "llm_response": result["llm_response"],
                    "needs_confirmation": result["needs_confirmation"],
                    "suggested_actions": result["suggested_actions"],
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(response))
                
            elif message_data.get("type") == "confirm_execution":
                # Виконуємо підтверджений запит
                user_request = message_data.get("request", "")
                llm_response = message_data.get("llm_response", "")
                actions = message_data.get("actions", [])
                
                result = await llm_agent.execute_confirmed_request(
                    user_request, llm_response, actions
                )
                
                response = {
                    "type": "execution_result",
                    "success": result["success"],
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
                await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Помилка WebSocket: {e}")
        await manager.send_personal_message(f"Помилка: {e}", websocket)

# Запуск додатку
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 