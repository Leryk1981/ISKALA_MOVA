#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import sys

# Додаємо шлях до модулів
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import rag_system

app = FastAPI(
    title="ISKALA RAG System API",
    description="API для індексації та пошуку знань з чатів з ШІ",
    version="1.0.0"
)

class SearchRequest(BaseModel):
    query: str
    search_type: str = "both"  # "qa", "capsules", "both"
    n_results: int = 5

class ProcessFileRequest(BaseModel):
    theme: Optional[str] = None

@app.get("/")
async def root():
    """Кореневий endpoint"""
    return {
        "message": "ISKALA RAG System API",
        "version": "1.0.0",
        "endpoints": {
            "process_file": "/process-file",
            "search": "/search",
            "capsules": "/capsules",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Перевірка стану системи"""
    try:
        # Перевіряємо доступність векторної БД
        capsules = rag_system.list_capsules()
        return {
            "status": "healthy",
            "capsules_count": len(capsules),
            "vector_db": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System error: {str(e)}")

@app.post("/process-file")
async def process_chat_file(
    file: UploadFile = File(...),
    theme: Optional[str] = None
):
    """Обробка чат файлу та створення індексу"""
    try:
        # Зберігаємо файл
        upload_path = os.path.join("uploads", file.filename)
        os.makedirs("uploads", exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Обробляємо файл
        result = rag_system.process_chat_file(upload_path, theme)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Файл успішно оброблено",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/search")
async def search_knowledge(request: SearchRequest):
    """Пошук знань"""
    try:
        results = rag_system.search_knowledge(
            query=request.query,
            search_type=request.search_type,
            n_results=request.n_results
        )
        
        return {
            "success": True,
            "query": request.query,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/capsules")
async def list_capsules():
    """Список всіх капсул знань"""
    try:
        capsules = rag_system.list_capsules()
        return {
            "success": True,
            "capsules": capsules,
            "count": len(capsules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing capsules: {str(e)}")

@app.get("/capsules/{capsule_id}")
async def get_capsule_details(capsule_id: str):
    """Деталі конкретної капсули"""
    try:
        details = rag_system.get_capsule_details(capsule_id)
        
        if "error" in details:
            raise HTTPException(status_code=404, detail=details["error"])
        
        return {
            "success": True,
            "capsule": details
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting capsule: {str(e)}")

@app.delete("/capsules/{capsule_id}")
async def delete_capsule(capsule_id: str):
    """Видалення капсули"""
    try:
        capsule_file = os.path.join("capsules", f"{capsule_id}.json")
        if os.path.exists(capsule_file):
            os.remove(capsule_file)
            return {
                "success": True,
                "message": f"Капсула {capsule_id} видалена"
            }
        else:
            raise HTTPException(status_code=404, detail="Капсула не знайдена")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting capsule: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    ) 