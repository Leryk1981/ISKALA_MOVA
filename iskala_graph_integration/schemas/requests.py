"""
📋 Request Models for ISKALA Graph Integration
Pydantic models for Tool Server API requests
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

class GraphHybridSearchRequest(BaseModel):
    """Request model for hybrid semantic search"""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Пошуковий запит",
        example="штучний інтелект машинне навчання"
    )
    
    language: Optional[str] = Field(
        None,
        description="Мова для фільтрації результатів (uk, en, zh, ru, etc.)",
        example="uk"
    )
    
    k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Кількість результатів для повернення",
        example=5
    )
    
    intent_filter: Optional[str] = Field(
        None,
        description="Фільтр за конкретним наміром",
        example="learning"
    )
    
    include_facets: bool = Field(
        default=False,
        description="Включити агрегації в відповідь",
        example=False
    )
    
    # Advanced search parameters
    vector_weight: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Вага векторної схожості в гібридному рейтингу"
    )
    
    graph_weight: float = Field(
        default=0.3, 
        ge=0.0,
        le=1.0,
        description="Вага графової близькості в рейтингу"
    )
    
    intent_weight: float = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="Вага відповідності наміру"
    )
    
    language_weight: float = Field(
        default=0.1,
        ge=0.0, 
        le=1.0,
        description="Вага мовної впевненості"
    )
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Запит не може бути порожнім")
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        if v is not None:
            valid_languages = ['uk', 'en', 'ru', 'zh', 'de', 'fr', 'es', 'it', 'pl']
            if v not in valid_languages:
                raise ValueError(f"Непідтримувана мова: {v}. Доступні: {valid_languages}")
        return v
    
    @validator('vector_weight', 'graph_weight', 'intent_weight', 'language_weight')
    def validate_weights_sum(cls, v, values):
        # Validate that weights approximately sum to 1.0
        weights = [v]
        if 'vector_weight' in values:
            weights.append(values['vector_weight'])
        if 'graph_weight' in values:
            weights.append(values['graph_weight'])
        if 'intent_weight' in values:
            weights.append(values['intent_weight'])
        if 'language_weight' in values:
            weights.append(values['language_weight'])
        
        if len(weights) == 4:  # All weights are set
            total = sum(weights)
            if abs(total - 1.0) > 0.01:
                raise ValueError(f"Сума ваг повинна дорівнювати 1.0, отримано: {total}")
        
        return v

class GraphVectorSearchRequest(BaseModel):
    """Request model for vector-only semantic search"""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Пошуковий запит для векторного пошуку",
        example="нейронні мережі глибоке навчання"
    )
    
    language: Optional[str] = Field(
        None,
        description="Мова для фільтрації результатів",
        example="uk"
    )
    
    k: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Кількість результатів",
        example=10
    )
    
    confidence_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Мінімальний поріг впевненості",
        example=0.3
    )
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Запит не може бути порожнім")
        return v.strip()

class GraphWalkRequest(BaseModel):
    """Request model for knowledge graph traversal"""
    
    start_node_id: str = Field(
        ...,
        description="Ідентифікатор початкового вузла (chunk hash)",
        example="chunk_abc123"
    )
    
    max_depth: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Максимальна глибина обходу графа",
        example=3
    )
    
    intent_filter: Optional[List[str]] = Field(
        None,
        description="Фільтр шляхів за конкретними намірами",
        example=["learning", "research"]
    )
    
    include_confidence: bool = Field(
        default=True,
        description="Включити оцінки впевненості для шляхів",
        example=True
    )
    
    @validator('start_node_id')
    def validate_start_node_id(cls, v):
        if not v.strip():
            raise ValueError("Ідентифікатор вузла не може бути порожнім")
        return v.strip()

class GraphSuggestionsRequest(BaseModel):
    """Request model for search suggestions"""
    
    partial_query: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Частковий пошуковий запит для підказок",
        example="машин"
    )
    
    language: Optional[str] = Field(
        None,
        description="Мова для фільтрації підказок",
        example="uk"
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=20,
        description="Максимальна кількість підказок",
        example=5
    )
    
    @validator('partial_query')
    def validate_partial_query(cls, v):
        if not v.strip():
            raise ValueError("Частковий запит не може бути порожнім")
        return v.strip()

# Base request model for common parameters
class BaseGraphRequest(BaseModel):
    """Base request model with common parameters"""
    
    user_id: Optional[str] = Field(
        None,
        description="Ідентифікатор користувача для персоналізації"
    )
    
    session_id: Optional[str] = Field(
        None,
        description="Ідентифікатор сесії для контексту"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Додаткові метадані запиту"
    )

# Export all request models
__all__ = [
    "GraphHybridSearchRequest",
    "GraphVectorSearchRequest",
    "GraphWalkRequest", 
    "GraphSuggestionsRequest",
    "BaseGraphRequest"
] 