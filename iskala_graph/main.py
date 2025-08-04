#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ISKALA Graph Search FastAPI Application
==========================================

Production-ready FastAPI application for Graph Search service with:
- Vector and hybrid search endpoints
- Health checks and monitoring
- Prometheus metrics
- Security and rate limiting
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil
import uvicorn

# Import API routes
from .api.routes.search import router as search_router
from .api.routes.vector import router as vector_router

# Import services for health checks
from .services.neo4j_driver import get_neo4j_connection, close_neo4j_connection
from .services.embedding_service import get_embedding_service, close_embedding_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP Request Duration')
SEARCH_REQUESTS = Counter('graph_search_requests_total', 'Total Graph Search Requests', ['search_type'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("🚀 Starting ISKALA Graph Search Service...")
    
    # Initialize services
    try:
        # Initialize Neo4j connection
        neo4j_conn = await get_neo4j_connection()
        logger.info("✅ Neo4j connection initialized")
        
        # Initialize embedding service  
        embedding_service = await get_embedding_service()
        logger.info("✅ Embedding service initialized")
        
        # Store start time
        app.state.start_time = datetime.utcnow()
        app.state.version = "1.0.0"
        
        logger.info("🎉 ISKALA Graph Search Service started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down ISKALA Graph Search Service...")
    try:
        await close_neo4j_connection()
        await close_embedding_service()
        logger.info("✅ Services closed successfully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="ISKALA Graph Search API",
    description="Production-ready Graph Search service with vector similarity and knowledge graph traversal",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if os.getenv("ENVIRONMENT") == "development" else [
        "localhost", 
        "127.0.0.1", 
        "graph-search",
        "*.iskala.ai"
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if os.getenv("ENVIRONMENT") == "development" else [
        "http://localhost:3000",
        "http://localhost:8003", 
        "https://iskala.ai"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# Request metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Collect request metrics"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    process_time = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(process_time)
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Include API routers
app.include_router(search_router, prefix="/api/v1")
app.include_router(vector_router, prefix="/api/v1")

# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Comprehensive health check with service status"""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": app.state.version,
        "uptime_seconds": (datetime.utcnow() - app.state.start_time).total_seconds(),
        "checks": {}
    }
    
    # Check Neo4j
    try:
        neo4j_conn = await get_neo4j_connection()
        neo4j_health = await neo4j_conn.health_check()
        health_status["checks"]["neo4j"] = neo4j_health
        if not neo4j_health.get("is_healthy", False):
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["neo4j"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Check Embedding Service
    try:
        embedding_service = await get_embedding_service()
        embedding_health = await embedding_service.health_check()
        health_status["checks"]["embedding_service"] = embedding_health
        if not embedding_health.get("is_healthy", False):
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["embedding_service"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # System resources
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    health_status["checks"]["system"] = {
        "memory_usage_percent": memory.percent,
        "disk_usage_percent": disk.percent,
        "cpu_count": psutil.cpu_count(),
        "status": "healthy" if memory.percent < 90 and disk.percent < 90 else "warning"
    }
    
    if health_status["checks"]["system"]["status"] == "warning":
        health_status["status"] = "degraded"
    
    # Response time
    health_status["response_time_ms"] = (time.time() - start_time) * 1000
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    
    return JSONResponse(content=health_status, status_code=status_code)

@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Quick service checks
        neo4j_conn = await get_neo4j_connection()
        embedding_service = await get_embedding_service()
        
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/live", tags=["Health"])
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}

@app.get("/metrics", tags=["Monitoring"])
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return generate_latest().decode('utf-8')

@app.get("/version", tags=["Info"])
async def version_info():
    """Service version and build information"""
    return {
        "version": app.state.version,
        "service": "iskala-graph-search",
        "build_time": app.state.start_time.isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with detailed logging"""
    logger.error(f"HTTP {exc.status_code} on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.utcnow().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Root endpoint
@app.get("/", tags=["Info"])
async def root():
    """API information and status"""
    return {
        "service": "ISKALA Graph Search API",
        "version": app.state.version,
        "status": "operational",
        "uptime_seconds": (datetime.utcnow() - app.state.start_time).total_seconds(),
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics", 
            "search": "/api/v1/search",
            "vector": "/api/v1/vector",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    ) 