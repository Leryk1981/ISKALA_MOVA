#!/usr/bin/env python3
"""
ISKALA FastAPI Application with Layered Architecture
Production-ready API with Dependency Injection
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging
from datetime import datetime
from pathlib import Path
import json
import subprocess

# Import layered architecture components
from iskala_basis.services import TranslationService, MemoryService, TranslationServiceError, MemoryServiceError
from iskala_basis.repositories import MockTranslationRepository, MockMemoryRepository
from iskala_basis.models import (
    TranslationRequest,
    TranslationResponse,
    UniversalSenseRequest,
    UniversalSenseResponse,
    SearchRequest,
    SearchResponse,
    MemoryHealthResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ISKALA API",
    description="Layered Architecture API with Translation and Memory Services",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# DEPENDENCY INJECTION SETUP
# ============================

async def get_translation_service() -> TranslationService:
    """
    Dependency injection for TranslationService
    
    Returns:
        TranslationService: Configured translation service
    """
    # TODO: In Task 2.1, replace with real repository
    repository = MockTranslationRepository()
    return TranslationService(repository)

async def get_memory_service() -> MemoryService:
    """
    Dependency injection for MemoryService
    
    Returns:
        MemoryService: Configured memory service
    """
    # TODO: In Task 2.1, replace with Neo4jMemoryRepository
    repository = MockMemoryRepository()
    return MemoryService(repository)

# ============================
# TRANSLATION API ROUTES
# ============================

@app.post("/api/v1/translation/translate", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    service: TranslationService = Depends(get_translation_service)
):
    """
    🌐 Translate text using layered architecture
    
    Features:
    - Business logic validation through TranslationService
    - Repository pattern for data access
    - Comprehensive error handling
    - Performance metrics tracking
    """
    try:
        logger.info(f"Translation request: {request.source_lang} -> {request.target_lang}")
        result = await service.translate(request)
        logger.info(f"Translation completed successfully")
        return result
        
    except TranslationServiceError as e:
        logger.error(f"Translation service error: {e.error_code} - {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected translation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during translation"
        )

@app.post("/api/v1/translation/universal-sense", response_model=UniversalSenseResponse)
async def create_universal_sense(
    request: UniversalSenseRequest,
    service: TranslationService = Depends(get_translation_service)
):
    """
    🧠 Create universal semantic representation
    
    Features:
    - Semantic analysis through service layer
    - Context-aware processing
    - Multi-language support
    """
    try:
        logger.info(f"Universal sense creation for: {request.source_lang}")
        result = await service.create_universal_sense(request)
        logger.info(f"Universal sense created successfully")
        return result
        
    except TranslationServiceError as e:
        logger.error(f"Universal sense error: {e.error_code} - {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected universal sense error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during universal sense creation"
        )

@app.get("/api/v1/translation/languages")
async def get_supported_languages(
    service: TranslationService = Depends(get_translation_service)
):
    """
    📋 Get supported languages
    
    Returns:
        List of supported language codes
    """
    try:
        result = await service.get_supported_languages()
        return {"languages": result}
        
    except Exception as e:
        logger.error(f"Error getting supported languages: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting supported languages"
        )

# ============================
# MEMORY API ROUTES
# ============================

@app.post("/api/v1/memory/search", response_model=SearchResponse)
async def search_memory(
    request: SearchRequest,
    service: MemoryService = Depends(get_memory_service)
):
    """
    🔍 Advanced memory search using layered architecture
    
    Features:
    - Multi-strategy search (Vector/Graph/Hybrid/Intent)
    - Graph traversal algorithms
    - Performance optimization
    - Faceted search results
    """
    try:
        logger.info(f"Memory search request: strategy={request.strategy}, k={request.k}")
        result = await service.search_memory(request)
        logger.info(f"Memory search completed: {len(result.patterns)} patterns found")
        return result
        
    except MemoryServiceError as e:
        logger.error(f"Memory service error: {e.error_code} - {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected memory search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during memory search"
        )

@app.get("/api/v1/memory/pattern/{pattern_id}")
async def get_memory_pattern(
    pattern_id: str,
    service: MemoryService = Depends(get_memory_service)
):
    """
    📄 Get specific memory pattern by ID
    
    Args:
        pattern_id: Unique pattern identifier
        
    Returns:
        MemoryPattern object or 404 if not found
    """
    try:
        logger.info(f"Retrieving memory pattern: {pattern_id}")
        result = await service.get_memory_pattern(pattern_id)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Memory pattern not found: {pattern_id}"
            )
        
        logger.info(f"Memory pattern retrieved successfully: {pattern_id}")
        return result
        
    except MemoryServiceError as e:
        logger.error(f"Memory service error: {e.error_code} - {e.message}")
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message,
                "details": e.details
            }
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error retrieving pattern: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving memory pattern"
        )

@app.get("/api/v1/memory/health", response_model=MemoryHealthResponse)
async def get_memory_health(
    service: MemoryService = Depends(get_memory_service)
):
    """
    ❤️ Get memory system health status
    
    Returns:
        Comprehensive system health metrics
    """
    try:
        logger.info("Memory health check requested")
        result = await service.get_memory_health()
        logger.info(f"Memory health check completed: status={result.status}")
        return result
        
    except Exception as e:
        logger.error(f"Memory health check error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during health check"
        )

# ============================
# SYSTEM ROUTES
# ============================

@app.get("/")
async def root():
    """
    🏠 API Root endpoint
    
    Returns:
        Welcome message with architecture info
    """
    return {
        "message": "ISKALA API - Layered Architecture",
        "version": "1.1.0",
        "architecture": "Models → Repositories → Services → Routes",
        "features": [
            "Translation Service with Universal Sense",
            "Memory Service with Graph Search",
            "Dependency Injection via FastAPI",
            "Comprehensive Error Handling",
            "Performance Monitoring"
        ],
        "endpoints": {
            "translation": "/api/v1/translation/",
            "memory": "/api/v1/memory/",
            "docs": "/docs",
            "health": "/api/v1/memory/health"
        }
    }

@app.get("/health")
async def system_health():
    """
    🔧 System health check
    
    Returns:
        Overall system status
    """
    try:
        # Get service health
        translation_service = await get_translation_service()
        memory_service = await get_memory_service()
        
        translation_health = await translation_service.get_service_health()
        memory_health = await memory_service.get_memory_health()
        
        return {
            "status": "healthy",
            "timestamp": memory_health.timestamp.isoformat(),
            "services": {
                "translation": {
                    "status": translation_health.get("status", "unknown"),
                    "total_requests": translation_health.get("total_requests", 0),
                    "success_rate": translation_health.get("success_rate", 0.0)
                },
                "memory": {
                    "status": memory_health.status,
                    "total_patterns": memory_health.total_patterns,
                    "total_connections": memory_health.total_connections
                }
            }
        }
        
    except Exception as e:
        logger.error(f"System health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# VFS Backup endpoints
@app.post("/api/v1/vfs/backup")
async def backup_vfs_data(
    backup_data: dict,
    background_tasks: BackgroundTasks
):
    """
    Автоматический backup VFS данных в Git репозиторий
    """
    try:
        timestamp = datetime.now().isoformat()
        backup_filename = f"vfs-backup-{timestamp.replace(':', '-')}.json"
        backup_path = Path("vfs-backups") / backup_filename
        
        # Создаем директорию если не существует
        backup_path.parent.mkdir(exist_ok=True)
        
        # Сохраняем backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": timestamp,
                "backup_data": backup_data,
                "metadata": {
                    "version": "1.0",
                    "source": "vfs-auto-backup"
                }
            }, f, indent=2, ensure_ascii=False)
        
        # Добавляем в фоновую задачу Git commit
        background_tasks.add_task(commit_vfs_backup, backup_path)
        
        return {
            "status": "success",
            "message": "VFS backup created successfully",
            "backup_file": str(backup_path),
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"VFS backup failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Backup failed: {str(e)}"
        )

@app.get("/api/v1/vfs/backups")
async def list_vfs_backups():
    """
    Список всех VFS backup файлов
    """
    try:
        backup_dir = Path("vfs-backups")
        if not backup_dir.exists():
            return {"backups": []}
        
        backups = []
        for backup_file in backup_dir.glob("vfs-backup-*.json"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return {
            "backups": sorted(backups, key=lambda x: x["created"], reverse=True)
        }
        
    except Exception as e:
        logger.error(f"Failed to list VFS backups: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list backups: {str(e)}"
        )

async def commit_vfs_backup(backup_path: Path):
    """
    Фоновая задача для Git commit VFS backup
    """
    try:
        import subprocess
        
        # Git add
        subprocess.run([
            "git", "add", str(backup_path)
        ], check=True)
        
        # Git commit
        commit_message = f"🔄 VFS auto-backup {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run([
            "git", "commit", "-m", commit_message
        ], check=True)
        
        logger.info(f"VFS backup committed to Git: {backup_path}")
        
    except subprocess.CalledProcessError as e:
        logger.warning(f"Git commit failed for VFS backup: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during Git commit: {e}")

# ============================
# APPLICATION LIFECYCLE
# ============================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 ISKALA API starting up with layered architecture")
    logger.info("✅ TranslationService initialized")
    logger.info("✅ MemoryService initialized")
    logger.info("✅ Dependency Injection configured")
    logger.info("🎯 Ready for production traffic")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 ISKALA API shutting down")
    
    try:
        # Close services gracefully
        translation_service = await get_translation_service()
        memory_service = await get_memory_service()
        
        await translation_service.close()
        await memory_service.close()
        
        logger.info("✅ Services closed gracefully")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    
    logger.info("👋 ISKALA API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 