"""
🔍 Vector Search API Endpoints for ISKALA MOVA
FastAPI routes for semantic search, document indexing, and vector operations
"""

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ...services.graph_vector_service import (
    GraphVectorService, 
    SearchResult, 
    IndexingResult,
    create_graph_vector_service
)
from ...services.document_processor import LanguageCode

logger = logging.getLogger(__name__)

# ============================
# 📋 REQUEST/RESPONSE MODELS
# ============================

class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    language_filter: Optional[str] = Field(None, description="Language filter (uk, en, zh, etc.)")
    k: int = Field(5, ge=1, le=100, description="Number of results to return")
    confidence_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum confidence score")
    
    @validator('language_filter')
    def validate_language(cls, v):
        if v is not None:
            valid_languages = [lang.value for lang in LanguageCode]
            if v not in valid_languages:
                raise ValueError(f"Unsupported language: {v}. Valid options: {valid_languages}")
        return v

class SearchResponse(BaseModel):
    """Semantic search response"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    language_filter: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BatchIndexRequest(BaseModel):
    """Batch indexing request"""
    source_language: str = Field("auto", description="Source language hint or 'auto' for detection")
    chunk_size: int = Field(512, ge=100, le=2000, description="Chunk size for processing")
    chunk_overlap: int = Field(128, ge=0, le=500, description="Chunk overlap")

class BatchIndexResponse(BaseModel):
    """Batch indexing response"""
    results: List[IndexingResult]
    total_files: int
    successful_files: int
    failed_files: int
    total_chunks_created: int
    total_chunks_indexed: int
    processing_time_ms: float

class ChunkResponse(BaseModel):
    """Single chunk response"""
    chunk_hash: str
    content: str
    language: str
    source_doc: str
    confidence: float
    metadata: Dict[str, Any]

class StatsResponse(BaseModel):
    """Service statistics response"""
    service_stats: Dict[str, Any]
    neo4j_stats: Dict[str, Any]
    embedding_stats: Dict[str, Any]
    performance: Dict[str, Any]
    timestamp: str

# ============================
# 🔧 DEPENDENCY INJECTION
# ============================

async def get_vector_service() -> GraphVectorService:
    """Dependency injection for GraphVectorService"""
    try:
        service = await create_graph_vector_service()
        return service
    except Exception as e:
        logger.error(f"❌ Failed to create GraphVectorService: {e}")
        raise HTTPException(
            status_code=503, 
            detail="Vector search service unavailable"
        )

# ============================
# 🌍 API ROUTER
# ============================

router = APIRouter(prefix="/vector", tags=["Vector Search"])

@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    🔍 Perform semantic similarity search
    
    Executes vector-based semantic search across indexed documents with:
    - Multilingual support (auto language detection)
    - Configurable result count and confidence filtering
    - Language-specific filtering
    - Performance monitoring
    
    Example:
    ```json
    {
        "query": "штучный інтелект в Україні",
        "language_filter": "uk",
        "k": 10,
        "confidence_threshold": 0.7
    }
    ```
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"🔍 Semantic search: '{request.query[:50]}...' (lang={request.language_filter})")
        
        # Execute search
        results = await service.similarity_search(
            query=request.query,
            language_filter=request.language_filter,
            k=request.k,
            confidence_threshold=request.confidence_threshold
        )
        
        # Calculate response time
        search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Prepare response
        response = SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time,
            language_filter=request.language_filter,
            metadata={
                "timestamp": start_time.isoformat(),
                "service": "GraphVectorService",
                "version": "2.3.0"
            }
        )
        
        logger.info(f"✅ Search completed: {len(results)} results in {search_time:.1f}ms")
        return response
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        )
    finally:
        await service.close()

@router.post("/batch-index", response_model=BatchIndexResponse)
async def batch_index_files(
    files: List[UploadFile] = File(..., description="Documents to index"),
    source_language: str = Form("auto", description="Language hint"),
    chunk_size: int = Form(512, description="Chunk size"),
    chunk_overlap: int = Form(128, description="Chunk overlap"),
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    📁 Batch index multiple documents
    
    Processes and indexes multiple documents simultaneously:
    - Supports .txt, .pdf, .docx, .md formats
    - Multilingual processing with language detection
    - Configurable chunking parameters
    - Transactional storage in Neo4j with vector embeddings
    
    Returns detailed statistics for each processed file.
    """
    start_time = datetime.utcnow()
    
    try:
        logger.info(f"📁 Batch indexing {len(files)} files")
        
        # Validate files
        if len(files) > 50:  # Limit for safety
            raise HTTPException(
                status_code=400,
                detail="Maximum 50 files allowed per batch"
            )
        
        results = []
        successful_count = 0
        failed_count = 0
        total_chunks_created = 0
        total_chunks_indexed = 0
        
        # Process files
        for file in files:
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                    content = await file.read()
                    temp_file.write(content)
                    temp_path = Path(temp_file.name)
                
                # Process document
                result = await service.process_and_index_document(
                    temp_path, 
                    source_language
                )
                
                results.append(result)
                
                if result.success:
                    successful_count += 1
                    total_chunks_created += result.chunks_created
                    total_chunks_indexed += result.chunks_indexed
                else:
                    failed_count += 1
                
                # Cleanup
                temp_path.unlink()
                
            except Exception as e:
                logger.error(f"❌ File processing failed: {file.filename}: {e}")
                failed_count += 1
                results.append(IndexingResult(
                    success=False,
                    document_name=file.filename,
                    chunks_created=0,
                    chunks_indexed=0,
                    processing_time=0,
                    language_detected="error",
                    error_message=str(e)
                ))
        
        # Calculate total processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        response = BatchIndexResponse(
            results=results,
            total_files=len(files),
            successful_files=successful_count,
            failed_files=failed_count,
            total_chunks_created=total_chunks_created,
            total_chunks_indexed=total_chunks_indexed,
            processing_time_ms=processing_time
        )
        
        logger.info(f"✅ Batch indexing completed: {successful_count}/{len(files)} files successful")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch indexing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch indexing failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/chunk/{chunk_hash}", response_model=ChunkResponse)
async def get_chunk_by_hash(
    chunk_hash: str,
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    📄 Retrieve specific chunk by hash
    
    Returns detailed information about a specific document chunk
    including content, metadata, and processing statistics.
    """
    try:
        logger.info(f"📄 Retrieving chunk: {chunk_hash}")
        
        result = await service.get_chunk_by_hash(chunk_hash)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Chunk not found: {chunk_hash}"
            )
        
        response = ChunkResponse(
            chunk_hash=result.chunk_hash,
            content=result.content,
            language=result.language,
            source_doc=result.source_doc,
            confidence=result.score,  # Using score as confidence
            metadata=result.metadata
        )
        
        logger.info(f"✅ Chunk retrieved: {chunk_hash}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chunk retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chunk retrieval failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/stats", response_model=StatsResponse)
async def get_service_statistics(
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    📊 Get comprehensive service statistics
    
    Returns detailed statistics about:
    - Service performance metrics
    - Neo4j database statistics
    - Embedding service statistics
    - Search and indexing performance
    """
    try:
        stats = await service.get_statistics()
        
        response = StatsResponse(
            service_stats=stats.get("service_stats", {}),
            neo4j_stats=stats.get("neo4j_stats", {}),
            embedding_stats=stats.get("embedding_stats", {}),
            performance=stats.get("performance", {}),
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Statistics collection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Statistics collection failed: {str(e)}"
        )
    finally:
        await service.close()

@router.get("/health")
async def health_check(
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    💚 Service health check
    
    Returns health status of all components:
    - GraphVectorService
    - Neo4j connectivity
    - Embedding service
    - Vector index status
    """
    try:
        health = await service.health_check()
        
        # Determine HTTP status based on health
        status_code = 200
        if health.get("status") == "unhealthy":
            status_code = 503
        elif health.get("status") == "degraded":
            status_code = 206  # Partial Content
        
        return JSONResponse(content=health, status_code=status_code)
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return JSONResponse(
            content={
                "service": "GraphVectorService",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            status_code=503
        )
    finally:
        await service.close()

# ============================
# 🔧 UTILITY ENDPOINTS
# ============================

@router.delete("/chunk/{chunk_hash}")
async def delete_chunk(
    chunk_hash: str,
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    🗑️ Delete specific chunk by hash
    
    Removes chunk from Neo4j database and cleans up related relationships.
    Use with caution in production environments.
    """
    try:
        # This would need to be implemented in GraphVectorService
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Chunk deletion not implemented yet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chunk deletion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chunk deletion failed: {str(e)}"
        )
    finally:
        await service.close()

@router.post("/reindex-document")
async def reindex_document(
    document_name: str = Form(..., description="Document name to reindex"),
    service: GraphVectorService = Depends(get_vector_service)
):
    """
    🔄 Reindex existing document
    
    Reprocesses and reindexes an existing document with updated embeddings.
    Useful for updating documents after model improvements.
    """
    try:
        # This would need to be implemented in GraphVectorService
        # For now, return not implemented
        raise HTTPException(
            status_code=501,
            detail="Document reindexing not implemented yet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document reindexing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Document reindexing failed: {str(e)}"
        )
    finally:
        await service.close()

# Export router
__all__ = ["router"] 