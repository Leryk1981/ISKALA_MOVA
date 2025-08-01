#!/usr/bin/env python3
"""
Тест інтегрованої системи інструментів
Перевіряє роботу APIResolverV2 + UniversalToolConnector
"""

import asyncio
import sys
from pathlib import Path

# Додаємо шлях до src
sys.path.append(str(Path(__file__).parent / "src"))

from integrated_tool_system import IntegratedToolSystem, process_intent, get_available_tools

async def test_integration():
    """Тестування інтегрованої системи"""
    print("🧪 Тестування Integrated Tool System")
    print("=" * 50)
    
    # Ініціалізація системи
    print("\n1. Ініціалізація системи...")
    try:
        tool_system = IntegratedToolSystem()
        print("✅ Система ініціалізована успішно")
    except Exception as e:
        print(f"❌ Помилка ініціалізації: {e}")
        return
    
    # Тест 1: Отримання доступних інструментів
    print("\n2. Отримання доступних інструментів...")
    try:
        tools = await get_available_tools()
        print(f"✅ Каталог: {tools.get('total_catalog', 0)} інструментів")
        print(f"✅ Коннектор: {tools.get('total_connector', 0)} інструментів")
        
        if tools.get('connector_tools'):
            print("\n   Доступні інструменти в коннекторі:")
            for tool in tools['connector_tools'][:3]:  # Показуємо перші 3
                print(f"   - {tool.get('id', 'N/A')}: {tool.get('description', 'N/A')}")
    except Exception as e:
        print(f"❌ Помилка отримання інструментів: {e}")
    
    # Тест 2: Обробка наміру (переклад)
    print("\n3. Тест обробки наміру (переклад)...")
    try:
        result = await process_intent(
            intent_text="Перекласти текст на англійську мову",
            context={
                "text": "Привіт, світ!",
                "target_language": "en"
            },
            user_id="test_user",
            session_id="test_session",
            graph_context="translation"
        )
        
        print(f"✅ Успіх: {result.get('success')}")
        print(f"✅ Інструмент: {result.get('tool_used', 'N/A')}")
        print(f"✅ Рейтинг: {result.get('tool_rating', 'N/A')}")
        print(f"✅ Походження: {result.get('selection_origin', 'N/A')}")
        
        if result.get('execution_details', {}).get('error'):
            print(f"⚠️  Помилка виконання: {result['execution_details']['error']}")
            
    except Exception as e:
        print(f"❌ Помилка обробки наміру: {e}")
    
    # Тест 3: Обробка наміру (створення задачі)
    print("\n4. Тест обробки наміру (створення задачі)...")
    try:
        result = await process_intent(
            intent_text="Створити нову задачу",
            context={
                "content": "Тестова задача",
                "project_id": "test_project"
            },
            user_id="test_user",
            session_id="test_session",
            graph_context="task_management"
        )
        
        print(f"✅ Успіх: {result.get('success')}")
        print(f"✅ Інструмент: {result.get('tool_used', 'N/A')}")
        print(f"✅ Рейтинг: {result.get('tool_rating', 'N/A')}")
        
        if result.get('execution_details', {}).get('error'):
            print(f"⚠️  Помилка виконання: {result['execution_details']['error']}")
            
    except Exception as e:
        print(f"❌ Помилка обробки наміру: {e}")
    
    # Тест 4: Статистика
    print("\n5. Отримання статистики...")
    try:
        from integrated_tool_system import get_tool_statistics
        stats = await get_tool_statistics()
        print(f"✅ Статус системи: {stats.get('system_status', 'N/A')}")
        
        if 'api_statistics' in stats:
            api_stats = stats['api_statistics']
            print(f"✅ Загальна кількість API: {api_stats.get('total_apis', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Помилка отримання статистики: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестування завершено!")

if __name__ == "__main__":
    asyncio.run(test_integration()) 