"""
API Resolver v2 - модуль для вибору найбільш релевантного API для реалізації наміру користувача

Цей модуль відповідає за:
- Шар 1: Базовий каталог + аналітична оцінка (перплексіті, рейтинги, відгуки)
- Шар 2: Графова модель (контекстуальна пам'ять про ефективність API в подібних ситуаціях)
- Логування та прозорість вибору API
- Підтримка мультимодальності та безпеки
"""

import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib
import re

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIMetadata:
    """Метадані API"""
    name: str
    source: str
    endpoint: str
    functions: List[str]
    keywords: List[str]
    rating: float
    reliability: float
    speed: float
    popularity: int
    license: str
    limits: Dict[str, Any]
    multimodal: bool = False
    whitelisted: bool = True

@dataclass
class APISelection:
    """Результат вибору API"""
    api_tool: str
    endpoint: str
    params: Dict[str, Any]
    preferred_score: float
    origin: str  # "graph_context" або "catalog_search"
    metadata: Optional[APIMetadata] = None
    explanation: str = ""

@dataclass
class Intent:
    """Структура наміру"""
    text: str
    semantic_description: str
    constraints: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    graph_context: Optional[str] = None

class APICatalog:
    """Каталог API з метаданими"""
    
    def __init__(self, catalog_path: str = "./tool_api_catalog"):
        self.catalog_path = Path(catalog_path)
        self.catalog_path.mkdir(parents=True, exist_ok=True)
        self.apis: Dict[str, APIMetadata] = {}
        self._load_catalog()
    
    def _load_catalog(self):
        """Завантажує каталог API"""
        catalog_file = self.catalog_path / "api_catalog.json"
        if catalog_file.exists():
            try:
                with open(catalog_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for api_data in data.get("apis", []):
                    api = APIMetadata(**api_data)
                    self.apis[api.name] = api
                    
                logger.info(f"Завантажено {len(self.apis)} API з каталогу")
            except Exception as e:
                logger.error(f"Помилка завантаження каталогу: {e}")
        else:
            self._create_default_catalog()
    
    def _create_default_catalog(self):
        """Створює каталог за замовчуванням"""
        default_apis = [
            {
                "name": "google_translate_api",
                "source": "Google",
                "endpoint": "/translate",
                "functions": ["translate", "detect_language"],
                "keywords": ["переклад", "translate", "language", "мова", "текст"],
                "rating": 0.95,
                "reliability": 0.98,
                "speed": 0.9,
                "popularity": 1000,
                "license": "commercial",
                "limits": {"requests_per_day": 1000000, "characters_per_request": 5000},
                "multimodal": False,
                "whitelisted": True
            },
            {
                "name": "deepl_api",
                "source": "DeepL",
                "endpoint": "/translate",
                "functions": ["translate", "detect_language"],
                "keywords": ["переклад", "translate", "language", "мова", "текст", "deepl"],
                "rating": 0.92,
                "reliability": 0.95,
                "speed": 0.85,
                "popularity": 500,
                "license": "commercial",
                "limits": {"requests_per_day": 500000, "characters_per_request": 5000},
                "multimodal": False,
                "whitelisted": True
            },
            {
                "name": "openai_gpt_api",
                "source": "OpenAI",
                "endpoint": "/chat/completions",
                "functions": ["text_generation", "conversation", "analysis"],
                "keywords": ["генерація", "текст", "розмова", "аналіз", "gpt", "openai"],
                "rating": 0.88,
                "reliability": 0.92,
                "speed": 0.8,
                "popularity": 2000,
                "license": "commercial",
                "limits": {"requests_per_minute": 60, "tokens_per_request": 4000},
                "multimodal": False,
                "whitelisted": True
            },
            {
                "name": "image_processing_api",
                "source": "Custom",
                "endpoint": "/process_image",
                "functions": ["image_analysis", "ocr", "object_detection"],
                "keywords": ["зображення", "image", "фото", "аналіз", "розпізнавання"],
                "rating": 0.85,
                "reliability": 0.88,
                "speed": 0.75,
                "popularity": 200,
                "license": "open",
                "limits": {"requests_per_day": 10000, "file_size_mb": 10},
                "multimodal": True,
                "whitelisted": True
            }
        ]
        
        for api_data in default_apis:
            api = APIMetadata(**api_data)
            self.apis[api.name] = api
        
        self._save_catalog()
        logger.info(f"Створено каталог з {len(self.apis)} API за замовчуванням")
    
    def _save_catalog(self):
        """Зберігає каталог"""
        try:
            catalog_file = self.catalog_path / "api_catalog.json"
            data = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "apis": [asdict(api) for api in self.apis.values()]
            }
            
            with open(catalog_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Помилка збереження каталогу: {e}")
    
    def search_relevant_apis(self, intent: str, constraints: Dict[str, Any]) -> List[Tuple[APIMetadata, float]]:
        """
        Шукає релевантні API для наміру
        
        Args:
            intent: семантичний опис наміру
            constraints: додаткові параметри
            
        Returns:
            Список (API, релевантність) відсортований за релевантністю
        """
        intent_lower = intent.lower()
        relevant_apis = []
        
        for api in self.apis.values():
            if not api.whitelisted:
                continue
            
            # Перевіряємо мультимодальність
            if constraints.get("multimodal") and not api.multimodal:
                continue
            
            # Розрахунок релевантності
            relevance = 0.0
            
            # Ключові слова
            for keyword in api.keywords:
                if keyword.lower() in intent_lower:
                    relevance += 0.3
            
            # Функції
            for function in api.functions:
                if function.lower() in intent_lower:
                    relevance += 0.4
            
            # Рейтинг API
            relevance += api.rating * 0.2
            
            # Популярність
            relevance += min(api.popularity / 1000, 1.0) * 0.1
            
            if relevance > 0:
                relevant_apis.append((api, relevance))
        
        # Сортуємо за релевантністю
        relevant_apis.sort(key=lambda x: x[1], reverse=True)
        return relevant_apis

class GraphMemory:
    """Графова пам'ять для контекстуальних виборів API"""
    
    def __init__(self, graph_path: str = "./graph_memory"):
        self.graph_path = Path(graph_path)
        self.graph_path.mkdir(parents=True, exist_ok=True)
        self.executions: Dict[str, List[Dict]] = {}
        self._load_memory()
    
    def _load_memory(self):
        """Завантажує графову пам'ять"""
        memory_file = self.graph_path / "api_executions.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    self.executions = json.load(f)
                logger.info(f"Завантажено {len(self.executions)} контекстів з графової пам'яті")
            except Exception as e:
                logger.error(f"Помилка завантаження графової пам'яті: {e}")
    
    def _save_memory(self):
        """Зберігає графову пам'ять"""
        try:
            memory_file = self.graph_path / "api_executions.json"
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.executions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Помилка збереження графової пам'яті: {e}")
    
    def find_similar_executions(self, intent: str, graph_context: str) -> List[Dict]:
        """
        Знаходить подібні виконання в графі
        
        Args:
            intent: намір
            graph_context: контекст графа
            
        Returns:
            Список подібних виконань
        """
        context_key = f"{graph_context}_{self._hash_intent(intent)}"
        return self.executions.get(context_key, [])
    
    def _hash_intent(self, intent: str) -> str:
        """Хешує намір для пошуку"""
        return hashlib.md5(intent.encode()).hexdigest()[:8]
    
    def record_execution(self, intent: str, graph_context: str, api_selection: APISelection, 
                        success: bool, user_rating: Optional[float] = None):
        """
        Записує виконання в графову пам'ять
        
        Args:
            intent: намір
            graph_context: контекст графа
            api_selection: вибраний API
            success: успішність виконання
            user_rating: оцінка користувача
        """
        context_key = f"{graph_context}_{self._hash_intent(intent)}"
        
        if context_key not in self.executions:
            self.executions[context_key] = []
        
        execution = {
            "timestamp": datetime.now().isoformat(),
            "api_tool": api_selection.api_tool,
            "endpoint": api_selection.endpoint,
            "preferred_score": api_selection.preferred_score,
            "success": success,
            "user_rating": user_rating,
            "origin": api_selection.origin
        }
        
        self.executions[context_key].append(execution)
        
        # Зберігаємо тільки останні 10 виконань для кожного контексту
        if len(self.executions[context_key]) > 10:
            self.executions[context_key] = self.executions[context_key][-10:]
        
        self._save_memory()
    
    def get_api_rating_in_context(self, api_tool: str, graph_context: str) -> float:
        """
        Отримує рейтинг API в конкретному контексті
        
        Args:
            api_tool: назва API
            graph_context: контекст графа
            
        Returns:
            Рейтинг API (0.0 - 1.0)
        """
        total_rating = 0.0
        total_executions = 0
        
        for context_key, executions in self.executions.items():
            if graph_context in context_key:
                for execution in executions:
                    if execution["api_tool"] == api_tool:
                        # Розрахунок рейтингу на основі успішності та оцінки користувача
                        rating = 0.5  # базова оцінка
                        
                        if execution["success"]:
                            rating += 0.3
                        
                        if execution.get("user_rating"):
                            rating += execution["user_rating"] * 0.2
                        
                        total_rating += rating
                        total_executions += 1
        
        if total_executions == 0:
            return 0.5  # нейтральний рейтинг
        
        return total_rating / total_executions

class APILogger:
    """Логер для API виборів"""
    
    def __init__(self, log_path: str = "./logs"):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
    
    def log_selection(self, intent: Intent, api_selection: APISelection, 
                     graph_context: Optional[str] = None):
        """
        Логує вибір API
        
        Args:
            intent: намір
            api_selection: вибраний API
            graph_context: контекст графа
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent.text,
            "semantic_description": intent.semantic_description,
            "constraints": intent.constraints,
            "user_id": intent.user_id,
            "session_id": intent.session_id,
            "graph_context": graph_context,
            "api_tool": api_selection.api_tool,
            "endpoint": api_selection.endpoint,
            "preferred_score": api_selection.preferred_score,
            "origin": api_selection.origin,
            "explanation": api_selection.explanation
        }
        
        log_file = self.log_path / f"api_resolver_log_{datetime.now().strftime('%Y%m%d')}.json"
        
        try:
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(log_entry)
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Помилка логування: {e}")

class APIResolverV2:
    """API Resolver v2 з двома шарами та графовою пам'яттю"""
    
    def __init__(self, catalog_path: str = "./tool_api_catalog", 
                 graph_path: str = "./graph_memory",
                 log_path: str = "./logs"):
        self.catalog = APICatalog(catalog_path)
        self.graph_memory = GraphMemory(graph_path)
        self.logger = APILogger(log_path)
    
    async def resolve_api(self, intent: Intent) -> APISelection:
        """
        Вирішує який API використовувати для наміру
        
        Args:
            intent: намір користувача
            
        Returns:
            Вибраний API з параметрами
        """
        # Шар 2: Графова пам'ять (якщо є контекст)
        if intent.graph_context:
            graph_selection = await self._resolve_from_graph(intent)
            if graph_selection:
                self.logger.log_selection(intent, graph_selection, intent.graph_context)
                return graph_selection
        
        # Шар 1: Каталог + аналітична оцінка
        catalog_selection = await self._resolve_from_catalog(intent)
        
        # Записуємо в графову пам'ять, якщо є контекст
        if intent.graph_context:
            self.graph_memory.record_execution(
                intent.text, 
                intent.graph_context, 
                catalog_selection, 
                success=True
            )
        
        self.logger.log_selection(intent, catalog_selection, intent.graph_context)
        return catalog_selection
    
    async def _resolve_from_graph(self, intent: Intent) -> Optional[APISelection]:
        """
        Шар 2: Вирішення з графової пам'яті
        
        Args:
            intent: намір
            
        Returns:
            Вибраний API або None
        """
        similar_executions = self.graph_memory.find_similar_executions(
            intent.text, intent.graph_context
        )
        
        if not similar_executions:
            return None
        
        # Знаходимо найкращий API на основі історії
        api_ratings = {}
        for execution in similar_executions:
            api_tool = execution["api_tool"]
            if api_tool not in api_ratings:
                api_ratings[api_tool] = []
            
            # Розрахунок рейтингу виконання
            rating = 0.5
            if execution["success"]:
                rating += 0.3
            if execution.get("user_rating"):
                rating += execution["user_rating"] * 0.2
            
            api_ratings[api_tool].append(rating)
        
        # Знаходимо API з найвищим середнім рейтингом
        best_api = None
        best_rating = 0.0
        
        for api_tool, ratings in api_ratings.items():
            avg_rating = sum(ratings) / len(ratings)
            if avg_rating > best_rating:
                best_rating = avg_rating
                best_api = api_tool
        
        if best_api and best_rating > 0.7:  # Поріг для використання з пам'яті
            api_metadata = self.catalog.apis.get(best_api)
            if api_metadata:
                return APISelection(
                    api_tool=best_api,
                    endpoint=api_metadata.endpoint,
                    params=self._build_params(intent),
                    preferred_score=best_rating,
                    origin="graph_context",
                    metadata=api_metadata,
                    explanation=f"Вибрано з графової пам'яті (рейтинг: {best_rating:.2f})"
                )
        
        return None
    
    async def _resolve_from_catalog(self, intent: Intent) -> APISelection:
        """
        Шар 1: Вирішення з каталогу + аналітична оцінка
        
        Args:
            intent: намір
            
        Returns:
            Вибраний API
        """
        # Пошук релевантних API
        relevant_apis = self.catalog.search_relevant_apis(
            intent.semantic_description, intent.constraints
        )
        
        if not relevant_apis:
            # Fallback до базового API
            fallback_api = self.catalog.apis.get("openai_gpt_api")
            return APISelection(
                api_tool="openai_gpt_api",
                endpoint=fallback_api.endpoint,
                params=self._build_params(intent),
                preferred_score=0.5,
                origin="catalog_search",
                metadata=fallback_api,
                explanation="Вибрано fallback API (немає релевантних варіантів)"
            )
        
        # Вибір найкращого API
        best_api, relevance = relevant_apis[0]
        
        # Додаткова аналітична оцінка (можна інтегрувати зовнішні сервіси)
        final_score = self._calculate_final_score(best_api, relevance, intent)
        
        return APISelection(
            api_tool=best_api.name,
            endpoint=best_api.endpoint,
            params=self._build_params(intent),
            preferred_score=final_score,
            origin="catalog_search",
            metadata=best_api,
            explanation=f"Вибрано з каталогу (релевантність: {relevance:.2f}, фінальний рейтинг: {final_score:.2f})"
        )
    
    def _build_params(self, intent: Intent) -> Dict[str, Any]:
        """Будує параметри для API виклику"""
        params = {
            "text": intent.text,
            "intent": intent.semantic_description
        }
        
        # Додаємо обмеження
        params.update(intent.constraints)
        
        return params
    
    def _calculate_final_score(self, api: APIMetadata, relevance: float, intent: Intent) -> float:
        """
        Розраховує фінальний рейтинг API
        
        Args:
            api: метадані API
            relevance: релевантність
            intent: намір
            
        Returns:
            Фінальний рейтинг (0.0 - 1.0)
        """
        # Базова релевантність
        score = relevance * 0.4
        
        # Рейтинг API
        score += api.rating * 0.2
        
        # Надійність
        score += api.reliability * 0.15
        
        # Швидкість
        score += api.speed * 0.15
        
        # Популярність (нормалізована)
        popularity_score = min(api.popularity / 2000, 1.0)
        score += popularity_score * 0.1
        
        return min(score, 1.0)
    
    def add_api_to_catalog(self, api_metadata: APIMetadata):
        """Додає новий API до каталогу"""
        self.catalog.apis[api_metadata.name] = api_metadata
        self.catalog._save_catalog()
        logger.info(f"Додано новий API до каталогу: {api_metadata.name}")
    
    def get_api_statistics(self) -> Dict[str, Any]:
        """Отримує статистику API"""
        return {
            "total_apis": len(self.catalog.apis),
            "whitelisted_apis": len([api for api in self.catalog.apis.values() if api.whitelisted]),
            "multimodal_apis": len([api for api in self.catalog.apis.values() if api.multimodal]),
            "graph_contexts": len(self.graph_memory.executions),
            "total_executions": sum(len(executions) for executions in self.graph_memory.executions.values())
        }

# Глобальний екземпляр
api_resolver_v2 = APIResolverV2()

async def resolve_api(intent: str, constraints: Dict[str, Any] = None, 
                     user_id: str = None, session_id: str = None, 
                     graph_context: str = None) -> APISelection:
    """
    Зручна функція для вирішення API
    
    Args:
        intent: намір користувача
        constraints: обмеження
        user_id: ID користувача
        session_id: ID сесії
        graph_context: контекст графа
        
    Returns:
        Вибраний API
    """
    intent_obj = Intent(
        text=intent,
        semantic_description=intent,
        constraints=constraints or {},
        user_id=user_id,
        session_id=session_id,
        graph_context=graph_context
    )
    
    return await api_resolver_v2.resolve_api(intent_obj)

if __name__ == "__main__":
    # Тестовий запуск
    async def test_resolver():
        # Тест 1: Переклад
        intent = "перекласти текст з української на англійську"
        selection = await resolve_api(intent, {"output_format": "text"})
        print(f"Тест 1 - Переклад:")
        print(f"API: {selection.api_tool}")
        print(f"Рейтинг: {selection.preferred_score}")
        print(f"Джерело: {selection.origin}")
        print(f"Пояснення: {selection.explanation}")
        print("-" * 50)
        
        # Тест 2: З графовим контекстом
        selection2 = await resolve_api(
            intent, 
            {"output_format": "text"}, 
            user_id="test_user",
            graph_context="translation_node"
        )
        print(f"Тест 2 - З графовим контекстом:")
        print(f"API: {selection2.api_tool}")
        print(f"Рейтинг: {selection2.preferred_score}")
        print(f"Джерело: {selection2.origin}")
        print(f"Пояснення: {selection2.explanation}")
        print("-" * 50)
        
        # Тест 3: Статистика
        stats = api_resolver_v2.get_api_statistics()
        print(f"Статистика: {stats}")
    
    asyncio.run(test_resolver()) 