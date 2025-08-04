# 🏗️ **STAGE 1: АРХИТЕКТУРНАЯ СТАБИЛИЗАЦИЯ**
**Branch:** `feature/architecture-stabilization`  
**Timeline:** 3 дня (Day 1-3)  
**Goal:** Преобразование монолитной архитектуры в layered service architecture  

---

## 📋 **ОБЩАЯ АРХИТЕКТУРНАЯ СТРАТЕГИЯ**

### **🎯 Целевая архитектура:**
```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FastAPI       │  │   OpenAPI       │  │   WebUI      │ │
│  │   Routes        │  │   Documentation │  │   Interface  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Translation     │  │ Memory          │  │ Graph        │ │
│  │ Service         │  │ Service         │  │ Service      │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   REPOSITORY LAYER                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Translation     │  │ Memory          │  │ Graph        │ │
│  │ Repository      │  │ Repository      │  │ Repository   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Neo4j         │  │   Redis         │  │   File       │ │
│  │   Database      │  │   Cache         │  │   Storage    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 **ДЕТАЛЬНЫЙ ПЛАН ПО ДНЯМ**

### **🌅 ДЕНЬ 1: SERVICE LAYER EXTRACTION**

#### **Morning Session (4 hours):**
```bash
# 1. Create directory structure
mkdir -p iskala_basis/{services,repositories,models}
mkdir -p iskala_basis/services/{__init__.py,translation_service.py,memory_service.py}
mkdir -p iskala_basis/repositories/{__init__.py,translation_repository.py}
mkdir -p iskala_basis/models/{__init__.py,translation_models.py}

# 2. Install additional dependencies
pip install sqlalchemy flask-migrate pytest pytest-asyncio pytest-cov httpx
```

#### **TranslationService Implementation:**
```python
# iskala_basis/services/translation_service.py
from typing import Optional
from iskala_basis.models.translation_models import TranslationRequest, TranslationResponse
from iskala_basis.repositories.translation_repository import TranslationRepository

class TranslationService:
    def __init__(self, translation_repo: TranslationRepository):
        self.translation_repo = translation_repo
    
    async def translate(
        self, 
        request: TranslationRequest
    ) -> TranslationResponse:
        """Business logic for translation"""
        # Validate input
        if not request.text.strip():
            raise ValueError("Text cannot be empty")
        
        # Check cache first
        cached_result = await self.translation_repo.get_cached_translation(
            request.text, request.source_lang, request.target_lang
        )
        if cached_result:
            return cached_result
        
        # Perform translation
        translated_text = await self.translation_repo.translate_text(
            request.text, request.source_lang, request.target_lang
        )
        
        # Cache result
        await self.translation_repo.cache_translation(
            request.text, translated_text, request.source_lang, request.target_lang
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
```

#### **Afternoon Session (4 hours):**
```python
# MemoryService Implementation
class MemoryService:
    def __init__(self, memory_repo: MemoryRepository):
        self.memory_repo = memory_repo
    
    async def search_memory(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[MemoryResult]:
        """Business logic for memory search"""
        # Input validation
        if not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        # Perform search with caching
        results = await self.memory_repo.search(
            query=query,
            limit=limit,
            use_cache=True
        )
        
        return [MemoryResult.from_repository(r) for r in results]
```

#### **Evening: Testing & Integration (2 hours):**
```python
# tests/services/test_translation_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from iskala_basis.services.translation_service import TranslationService

@pytest.mark.asyncio
async def test_translation_service_translate():
    # Arrange
    mock_repo = AsyncMock()
    service = TranslationService(mock_repo)
    request = TranslationRequest(text="Hello", source_lang="en", target_lang="uk")
    
    # Act
    result = await service.translate(request)
    
    # Assert
    assert result.translated_text == "Привіт"
    mock_repo.translate_text.assert_called_once()
```

### **🌅 ДЕНЬ 2: DATABASE LAYER & MIGRATIONS**

#### **Morning: SQLAlchemy Models (4 hours):**
```python
# iskala_basis/models/database_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Translation(Base):
    __tablename__ = 'translations'
    
    id = Column(Integer, primary_key=True)
    original_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_translation_lookup', 'original_text', 'source_lang', 'target_lang'),
        Index('idx_translation_created', 'created_at'),
    )

class MemoryChunk(Base):
    __tablename__ = 'memory_chunks'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    language = Column(String(10), nullable=False)
    chunk_hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_memory_content', 'content'),
        Index('idx_memory_language', 'language'),
        Index('idx_memory_hash', 'chunk_hash'),
    )
```

#### **Afternoon: Repository Pattern (4 hours):**
```python
# iskala_basis/repositories/translation_repository.py
from sqlalchemy.orm import Session
from iskala_basis.models.database_models import Translation
from redis import Redis
import hashlib

class TranslationRepository:
    def __init__(self, db_session: Session, redis_client: Redis):
        self.db = db_session
        self.redis = redis_client
    
    async def get_cached_translation(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Optional[TranslationResponse]:
        """Get cached translation from Redis"""
        cache_key = self._generate_cache_key(text, source_lang, target_lang)
        cached = self.redis.get(cache_key)
        
        if cached:
            return TranslationResponse.from_json(cached)
        return None
    
    async def translate_text(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> str:
        """Perform actual translation"""
        # Call external translation API
        # This is the business logic that was in the route
        pass
    
    async def cache_translation(
        self, 
        original: str, 
        translated: str, 
        source_lang: str, 
        target_lang: str
    ):
        """Cache translation result"""
        cache_key = self._generate_cache_key(original, source_lang, target_lang)
        response = TranslationResponse(
            original_text=original,
            translated_text=translated,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        self.redis.setex(cache_key, 3600, response.to_json())  # 1 hour TTL
```

### **🌅 ДЕНЬ 3: API VERSIONING & DOCUMENTATION**

#### **Morning: API Versioning (4 hours):**
```python
# iskala_openapi_server.py - Updated with versioning
from fastapi import APIRouter, Depends
from iskala_basis.services.translation_service import TranslationService
from iskala_basis.services.memory_service import MemoryService

# Version 1 API Router
api_v1_router = APIRouter(prefix="/api/v1")

@api_v1_router.post("/translation/translate")
async def translate_text_v1(
    request: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service)
):
    """Version 1 translation endpoint"""
    return await translation_service.translate(request)

@api_v1_router.post("/memory/search")
async def search_memory_v1(
    request: MemorySearchRequest,
    memory_service: MemoryService = Depends(get_memory_service)
):
    """Version 1 memory search endpoint"""
    return await memory_service.search_memory(request.query, request.limit)

# Legacy endpoints for backward compatibility
@api_v1_router.post("/iskala/translation/translate")
async def translate_text_legacy(request: TranslationRequest):
    """Legacy endpoint - redirects to v1"""
    return await translate_text_v1(request, get_translation_service())

# Include routers
app.include_router(api_v1_router)
```

#### **Afternoon: Documentation & Testing (4 hours):**
```python
# Enhanced OpenAPI documentation
app = FastAPI(
    title="ISKALA API - Version 1",
    description="""
    ## ISKALA Multilingual AI Platform API
    
    ### Version 1.0.0
    - Service layer architecture
    - Repository pattern implementation
    - Comprehensive input validation
    - Rate limiting and authentication
    
    ### Migration Guide
    - Legacy endpoints: `/iskala/*` (deprecated)
    - New endpoints: `/api/v1/*` (recommended)
    - Backward compatibility maintained until v2.0
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

---

## 🧪 **TESTING STRATEGY**

### **Unit Tests (80% coverage target):**
```python
# tests/services/test_translation_service.py
# tests/repositories/test_translation_repository.py
# tests/models/test_translation_models.py

# Coverage command:
pytest --cov=iskala_basis --cov-report=html --cov-report=term
```

### **Integration Tests:**
```python
# tests/integration/test_service_integration.py
@pytest.mark.integration
async def test_translation_service_integration():
    """Test service with real repository"""
    # Setup real database connection
    # Test end-to-end translation flow
    # Verify caching works
```

### **Performance Tests:**
```python
# tests/performance/test_translation_performance.py
@pytest.mark.performance
async def test_translation_performance():
    """Ensure performance within 10% of current"""
    start_time = time.time()
    # Perform translation
    end_time = time.time()
    
    assert (end_time - start_time) < 0.1  # 100ms threshold
```

---

## 📊 **SUCCESS METRICS**

### **Day 1 Metrics:**
- ✅ Service layer extracted and tested
- ✅ Dependency injection working
- ✅ Unit test coverage >80%
- ✅ No breaking changes to existing functionality

### **Day 2 Metrics:**
- ✅ SQLAlchemy models created
- ✅ Migrations run successfully
- ✅ Repository pattern implemented
- ✅ Performance within 10% of current

### **Day 3 Metrics:**
- ✅ API versioning implemented
- ✅ OpenAPI documentation complete
- ✅ Backward compatibility maintained
- ✅ All integration tests passing

---

## 🚨 **RISK MITIGATION**

### **Data Safety:**
```bash
# Before any database changes
pg_dump iskala_mova > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Rollback Strategy:**
```bash
# If issues occur
git checkout main
git reset --hard HEAD~1
docker-compose down
docker-compose up -d
```

### **Feature Flags:**
```python
# Use environment variables for gradual rollout
ENABLE_NEW_ARCHITECTURE=true
ENABLE_API_V1=true
ENABLE_DATABASE_MIGRATIONS=true
```

---

## 🎯 **DELIVERABLES**

### **Code Deliverables:**
- ✅ Service layer with dependency injection
- ✅ Repository pattern implementation
- ✅ SQLAlchemy models and migrations
- ✅ API versioning with backward compatibility
- ✅ Comprehensive test suite

### **Documentation Deliverables:**
- ✅ Architecture decision records
- ✅ API documentation (OpenAPI/Swagger)
- ✅ Migration guide for existing clients
- ✅ Performance benchmarks

### **Quality Deliverables:**
- ✅ 80%+ test coverage
- ✅ Security scan clean
- ✅ Performance within 10% of current
- ✅ Zero breaking changes

---

**🎯 STAGE 1 READY FOR EXECUTION**

**Branch:** `feature/architecture-stabilization`  
**Start Date:** Tomorrow 9:00  
**Daily Demos:** 18:00 each day  
**Completion Target:** 3 days 