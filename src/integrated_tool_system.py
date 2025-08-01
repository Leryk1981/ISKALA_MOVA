"""
Integrated Tool System - объединение APIResolverV2 и UniversalToolConnector

Эта система объединяет:
- APIResolverV2: умный выбор инструментов с графовой памятью
- UniversalToolConnector: надежное выполнение с валидацией и безопасностью

Архитектура:
1. APIResolverV2 выбирает лучший инструмент
2. UniversalToolConnector выполняет выбранный инструмент
3. Результаты сохраняются в графовую память для будущих решений
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Добавляем путь к tool_api для импорта UniversalToolConnector
sys.path.append(str(Path(__file__).parent.parent / "tool_api"))

from api_resolver_v2 import APIResolverV2, Intent, APISelection
from tool_api.connectors.universal_connector import UniversalToolConnector

logger = logging.getLogger(__name__)

class IntegratedToolSystem:
    """Интегрированная система выбора и выполнения инструментов"""
    
    def __init__(self, 
                 catalog_path: str = "./tool_api_catalog",
                 graph_path: str = "./graph_memory",
                 log_path: str = "./logs",
                 tools_dir: str = "./tool_api/tools"):
        """
        Инициализация интегрированной системы
        
        Args:
            catalog_path: путь к каталогу API
            graph_path: путь к графовой памяти
            log_path: путь к логам
            tools_dir: путь к JSON конфигурациям инструментов
        """
        # Система выбора инструментов
        self.resolver = APIResolverV2(
            catalog_path=catalog_path,
            graph_path=graph_path,
            log_path=log_path
        )
        
        # Система выполнения инструментов
        self.executor = UniversalToolConnector(tools_dir=tools_dir)
        
        # Загружаем секреты
        self.executor.load_secrets()
        
        logger.info("✅ Integrated Tool System инициализирована")
    
    async def process_intent(self, 
                           intent_text: str, 
                           context: Dict[str, Any] = None,
                           user_id: str = None,
                           session_id: str = None,
                           graph_context: str = None) -> Dict[str, Any]:
        """
        Обработка намерения: выбор + выполнение
        
        Args:
            intent_text: текст намерения
            context: контекст с параметрами
            user_id: ID пользователя
            session_id: ID сессии
            graph_context: контекст графа
            
        Returns:
            Результат выполнения с метаданными
        """
        try:
            # 1. Создаем объект намерения
            intent = Intent(
                text=intent_text,
                semantic_description=intent_text,
                constraints=context or {},
                user_id=user_id,
                session_id=session_id,
                graph_context=graph_context
            )
            
            # 2. Выбираем лучший инструмент
            logger.info(f"🔍 Выбор инструмента для: {intent_text}")
            api_selection = await self.resolver.resolve_api(intent)
            
            logger.info(f"✅ Выбран инструмент: {api_selection.api_tool} "
                       f"(рейтинг: {api_selection.preferred_score:.2f})")
            
            # 3. Выполняем выбранный инструмент
            logger.info(f"🚀 Выполнение инструмента: {api_selection.api_tool}")
            execution_result = self.executor.execute_tool_api(
                tool_api=self._build_tool_api_from_selection(api_selection),
                context=api_selection.params
            )
            
            # 4. Записываем результат в графовую память
            if graph_context:
                self.resolver.graph_memory.record_execution(
                    intent=intent_text,
                    graph_context=graph_context,
                    api_selection=api_selection,
                    success=execution_result.get('success', False),
                    user_rating=self._calculate_user_rating(execution_result)
                )
            
            # 5. Формируем итоговый результат
            return {
                "success": execution_result.get('success', False),
                "data": execution_result.get('data'),
                "tool_used": api_selection.api_tool,
                "tool_rating": api_selection.preferred_score,
                "selection_origin": api_selection.origin,
                "explanation": api_selection.explanation,
                "execution_details": {
                    "status_code": execution_result.get('status_code'),
                    "tool_id": execution_result.get('tool_id'),
                    "error": execution_result.get('error')
                },
                "metadata": {
                    "user_id": user_id,
                    "session_id": session_id,
                    "graph_context": graph_context,
                    "timestamp": asyncio.get_event_loop().time()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки намерения: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_used": None,
                "data": None
            }
    
    def _build_tool_api_from_selection(self, api_selection: APISelection) -> Dict[str, Any]:
        """
        Строит конфигурацию инструмента из выбора APIResolverV2
        
        Args:
            api_selection: результат выбора API
            
        Returns:
            Конфигурация инструмента для UniversalToolConnector
        """
        # Пытаемся загрузить полную конфигурацию из JSON файла
        try:
            tool_id = api_selection.api_tool
            return self.executor.load_tool_api(tool_id)
        except:
            # Если не удалось, создаем базовую конфигурацию
            return {
                "id": api_selection.api_tool,
                "url": api_selection.endpoint,
                "method": "POST",  # По умолчанию
                "headers": {},
                "input_schema": {},
                "output_schema": {}
            }
    
    def _calculate_user_rating(self, execution_result: Dict[str, Any]) -> Optional[float]:
        """
        Вычисляет пользовательский рейтинг на основе результата выполнения
        
        Args:
            execution_result: результат выполнения
            
        Returns:
            Рейтинг от 0.0 до 1.0 или None
        """
        if not execution_result.get('success'):
            return 0.0
        
        # Простая эвристика: успешное выполнение = высокий рейтинг
        status_code = execution_result.get('status_code', 0)
        if 200 <= status_code < 300:
            return 0.9
        elif 300 <= status_code < 400:
            return 0.7
        else:
            return 0.5
    
    async def get_available_tools(self) -> Dict[str, Any]:
        """
        Получает список доступных инструментов
        
        Returns:
            Информация о доступных инструментах
        """
        try:
            # Получаем инструменты из каталога
            catalog_tools = []
            for api_name, api_metadata in self.resolver.catalog.apis.items():
                catalog_tools.append({
                    "name": api_name,
                    "source": api_metadata.source,
                    "endpoint": api_metadata.endpoint,
                    "rating": api_metadata.rating,
                    "reliability": api_metadata.reliability,
                    "functions": api_metadata.functions,
                    "keywords": api_metadata.keywords
                })
            
            # Получаем инструменты из UniversalToolConnector
            connector_tools = []
            tools_dir = Path(self.executor.tools_dir)
            for tool_file in tools_dir.glob("*.json"):
                try:
                    tool_config = self.executor.load_tool_api(tool_file.stem)
                    connector_tools.append({
                        "id": tool_config.get("id"),
                        "description": tool_config.get("description"),
                        "intent": tool_config.get("intent"),
                        "method": tool_config.get("method"),
                        "url": tool_config.get("url")
                    })
                except Exception as e:
                    logger.warning(f"Не удалось загрузить {tool_file}: {e}")
            
            return {
                "catalog_tools": catalog_tools,
                "connector_tools": connector_tools,
                "total_catalog": len(catalog_tools),
                "total_connector": len(connector_tools)
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения инструментов: {e}")
            return {"error": str(e)}
    
    async def get_tool_statistics(self) -> Dict[str, Any]:
        """
        Получает статистику использования инструментов
        
        Returns:
            Статистика использования
        """
        try:
            # Статистика из APIResolverV2
            api_stats = self.resolver.get_api_statistics()
            
            # Статистика из графовой памяти
            graph_stats = {
                "total_executions": len(self.resolver.graph_memory.executions),
                "contexts": list(self.resolver.graph_memory.executions.keys())
            }
            
            return {
                "api_statistics": api_stats,
                "graph_statistics": graph_stats,
                "system_status": "operational"
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"error": str(e)}

# Глобальный экземпляр для использования в других модулях
integrated_tool_system = IntegratedToolSystem()

# Удобные функции для быстрого доступа
async def process_intent(intent_text: str, 
                        context: Dict[str, Any] = None,
                        user_id: str = None,
                        session_id: str = None,
                        graph_context: str = None) -> Dict[str, Any]:
    """Удобная функция для обработки намерения"""
    return await integrated_tool_system.process_intent(
        intent_text, context, user_id, session_id, graph_context
    )

async def get_available_tools() -> Dict[str, Any]:
    """Удобная функция для получения инструментов"""
    return await integrated_tool_system.get_available_tools()

async def get_tool_statistics() -> Dict[str, Any]:
    """Удобная функция для получения статистики"""
    return await integrated_tool_system.get_tool_statistics()

if __name__ == "__main__":
    # Тестовый запуск
    async def test_integration():
        print("🧪 Тестирование Integrated Tool System...")
        
        # Тест 1: Получение доступных инструментов
        print("\n1. Доступные инструменты:")
        tools = await get_available_tools()
        print(f"   Каталог: {tools.get('total_catalog', 0)} инструментов")
        print(f"   Коннектор: {tools.get('total_connector', 0)} инструментов")
        
        # Тест 2: Обработка намерения
        print("\n2. Обработка намерения:")
        result = await process_intent(
            intent_text="Переведи текст на английский",
            context={"text": "Привет, мир!"},
            user_id="test_user",
            session_id="test_session",
            graph_context="translation"
        )
        
        print(f"   Успех: {result.get('success')}")
        print(f"   Инструмент: {result.get('tool_used')}")
        print(f"   Рейтинг: {result.get('tool_rating')}")
        
        # Тест 3: Статистика
        print("\n3. Статистика:")
        stats = await get_tool_statistics()
        print(f"   Статус: {stats.get('system_status')}")
        
        print("\n✅ Тестирование завершено!")
    
    # Запуск тестов
    asyncio.run(test_integration()) 