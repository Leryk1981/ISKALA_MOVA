"""
📊 Response Models for ISKALA Graph Integration
Pydantic models for Tool Server API responses
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class GraphSearchResult(BaseModel):
    """Individual search result item"""
    
    id: str = Field(
        ...,
        description="Унікальний ідентифікатор результату",
        example="chunk_abc123"
    )
    
    content: str = Field(
        ...,
        description="Текстовий контент результату",
        example="Штучний інтелект - це галузь інформатики..."
    )
    
    language: str = Field(
        ...,
        description="Мова контенту",
        example="uk"
    )
    
    source_doc: str = Field(
        ...,
        description="Джерельний документ",
        example="ai_intro_uk.md"
    )
    
    # Scoring breakdown
    vector_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Оцінка векторної схожості"
    )
    
    graph_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Оцінка графової близькості"
    )
    
    intent_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Оцінка відповідності наміру"
    )
    
    combined_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Загальна оцінка результату",
        example=0.85
    )
    
    # Result metadata
    result_type: str = Field(
        default="hybrid",
        description="Тип результату: vector, graph, hybrid",
        example="hybrid"
    )
    
    intent_name: Optional[str] = Field(
        None,
        description="Пов'язаний намір",
        example="learning"
    )
    
    graph_distance: int = Field(
        default=0,
        ge=0,
        description="Відстань в графі знань від джерела"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Додаткові метадані результату"
    )
    
    highlight: Optional[str] = Field(
        None,
        description="Підсвічений фрагмент тексту з запитом"
    )

class SearchFacets(BaseModel):
    """Search result facets and aggregations"""
    
    languages: Dict[str, int] = Field(
        default_factory=dict,
        description="Розподіл за мовами",
        example={"uk": 15, "en": 10, "ru": 5}
    )
    
    intents: Dict[str, int] = Field(
        default_factory=dict,
        description="Розподіл за намірами",
        example={"learning": 12, "reference": 8}
    )
    
    sources: Dict[str, int] = Field(
        default_factory=dict,
        description="Розподіл за джерелами",
        example={"ai_intro.md": 5, "ml_guide.pdf": 3}
    )
    
    result_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Розподіл за типами результатів",
        example={"hybrid": 10, "vector": 5, "graph": 5}
    )

class GraphSearchResponse(BaseModel):
    """Response model for search operations"""
    
    query: str = Field(
        ...,
        description="Оригінальний пошуковий запит",
        example="штучний інтелект"
    )
    
    results: List[GraphSearchResult] = Field(
        ...,
        description="Список результатів пошуку"
    )
    
    total_results: int = Field(
        ...,
        ge=0,
        description="Загальна кількість знайдених результатів",
        example=15
    )
    
    # Performance metrics
    search_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Час виконання пошуку в мілісекундах",
        example=125.5
    )
    
    cache_hit: bool = Field(
        default=False,
        description="Чи було використано кешування",
        example=False
    )
    
    # Search strategy breakdown
    vector_results_count: int = Field(
        default=0,
        ge=0,
        description="Кількість векторних результатів"
    )
    
    graph_results_count: int = Field(
        default=0,
        ge=0,
        description="Кількість графових результатів"
    )
    
    hybrid_results_count: int = Field(
        default=0,
        ge=0,
        description="Кількість гібридних результатів"
    )
    
    # Optional facets
    facets: Optional[SearchFacets] = Field(
        None,
        description="Агрегації результатів пошуку"
    )
    
    # Query analysis
    query_analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Аналіз пошукового запиту"
    )
    
    # Response metadata
    language_filter: Optional[str] = Field(
        None,
        description="Застосований мовний фільтр"
    )
    
    intent_filter: Optional[str] = Field(
        None,
        description="Застосований фільтр наміру"
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Час генерації відповіді"
    )

class GraphPathNode(BaseModel):
    """Node in a graph path"""
    
    id: str = Field(..., description="Ідентифікатор вузла")
    type: str = Field(..., description="Тип вузла", example="ContextChunk")
    content: Optional[str] = Field(None, description="Контент вузла")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphPathRelationship(BaseModel):
    """Relationship in a graph path"""
    
    type: str = Field(..., description="Тип зв'язку", example="LEADS_TO")
    properties: Dict[str, Any] = Field(default_factory=dict)

class GraphPath(BaseModel):
    """Individual path through the knowledge graph"""
    
    start_node_id: str = Field(..., description="Початковий вузол")
    end_node_id: str = Field(..., description="Кінцевий вузол")
    path_length: int = Field(..., ge=1, description="Довжина шляху")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Впевненість шляху")
    
    nodes: List[GraphPathNode] = Field(..., description="Вузли в шляху")
    relationships: List[GraphPathRelationship] = Field(..., description="Зв'язки в шляху")
    
    path_summary: str = Field(..., description="Опис шляху")

class GraphWalkResponse(BaseModel):
    """Response model for graph walk operations"""
    
    start_node_id: str = Field(
        ...,
        description="Початковий вузол обходу",
        example="chunk_abc123"
    )
    
    paths: List[GraphPath] = Field(
        ...,
        description="Знайдені шляхи в графі"
    )
    
    total_paths: int = Field(
        ...,
        ge=0,
        description="Загальна кількість знайдених шляхів",
        example=8
    )
    
    max_depth_reached: int = Field(
        ...,
        ge=1,
        description="Максимальна досягнута глибина",
        example=3
    )
    
    walk_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Час виконання обходу в мілісекундах",
        example=45.2
    )

class GraphSuggestionsResponse(BaseModel):
    """Response model for search suggestions"""
    
    partial_query: str = Field(
        ...,
        description="Оригінальний частковий запит",
        example="машин"
    )
    
    suggestions: List[str] = Field(
        ...,
        description="Список підказок",
        example=["машинне навчання", "машинний переклад", "машинне бачення"]
    )
    
    suggestion_count: int = Field(
        ...,
        ge=0,
        description="Кількість підказок",
        example=5
    )
    
    generation_time_ms: float = Field(
        ...,
        ge=0.0,
        description="Час генерації підказок в мілісекундах",
        example=15.8
    )
    
    language_filter: Optional[str] = Field(
        None,
        description="Застосований мовний фільтр"
    )

class ComponentStatus(BaseModel):
    """Status of individual service component"""
    
    status: str = Field(
        ...,
        description="Статус компоненту",
        example="healthy"
    )
    
    response_time_ms: Optional[float] = Field(
        None,
        description="Час відгуку компоненту"
    )
    
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Деталі статусу"
    )
    
    last_check: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Час останньої перевірки"
    )

class GraphStatusResponse(BaseModel):
    """Response model for service status"""
    
    service: str = Field(
        default="ISKALA Graph Search",
        description="Назва сервісу"
    )
    
    status: str = Field(
        ...,
        description="Загальний статус",
        example="healthy"
    )
    
    components: Dict[str, ComponentStatus] = Field(
        ...,
        description="Статус окремих компонентів"
    )
    
    # Performance statistics
    performance: Dict[str, Any] = Field(
        default_factory=dict,
        description="Статистика продуктивності"
    )
    
    # System info
    uptime_seconds: Optional[float] = Field(
        None,
        description="Час роботи системи в секундах"
    )
    
    version: str = Field(
        default="1.0.0",
        description="Версія сервісу"
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Час генерації статусу"
    )

# Base response model with common fields
class BaseGraphResponse(BaseModel):
    """Base response model with common fields"""
    
    success: bool = Field(
        default=True,
        description="Успішність операції"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Повідомлення про помилку (якщо є)"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Ідентифікатор запиту для відстеження"
    )

# Export all response models
__all__ = [
    "GraphSearchResult",
    "SearchFacets",
    "GraphSearchResponse",
    "GraphPath",
    "GraphPathNode", 
    "GraphPathRelationship",
    "GraphWalkResponse",
    "GraphSuggestionsResponse",
    "ComponentStatus",
    "GraphStatusResponse",
    "BaseGraphResponse"
] 