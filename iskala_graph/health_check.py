#!/usr/bin/env python3
"""
Health Check для ISKALA MOVA Neo4j Infrastructure
Перевіряє доступність Neo4j, Redis та базові операції
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Додаємо поточну директорію до PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from services.neo4j_driver import get_neo4j_connection, Neo4jConnection
from services.graph_models import CypherTemplates, Intent, Phase, ContextChunk

async def test_basic_connectivity() -> Dict[str, Any]:
    """Тест базового підключення до Neo4j"""
    print("🔍 Тестуємо базове підключення до Neo4j...")
    
    try:
        conn = await get_neo4j_connection()
        health_status = await conn.health_check()
        
        if health_status["neo4j"]:
            print("✅ Neo4j підключення успішне")
        else:
            print("❌ Neo4j недоступний")
            
        if health_status["redis"]:
            print("✅ Redis підключення успішне")
        else:
            print("⚠️ Redis недоступний (не критично)")
            
        return health_status
        
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return {"error": str(e)}

async def test_basic_query() -> bool:
    """Тест базового запиту"""
    print("🔍 Тестуємо базовий запит...")
    
    try:
        conn = await get_neo4j_connection()
        result = await conn.execute_query("RETURN 'Graph ready' as status")
        
        if result and len(result) > 0:
            status = result[0].get("status")
            print(f"✅ Базовий запит успішний: {status}")
            return True
        else:
            print("❌ Базовий запит повернув пустий результат")
            return False
            
    except Exception as e:
        print(f"❌ Помилка виконання запиту: {e}")
        return False

async def test_create_indexes() -> bool:
    """Створення індексів та constraints"""
    print("🔍 Створюємо індекси та constraints...")
    
    try:
        conn = await get_neo4j_connection()
        
        # Створюємо індекси
        for index_query in CypherTemplates.CREATE_INDEXES:
            try:
                await conn.execute_query(index_query)
                print(f"✅ Індекс створено")
            except Exception as e:
                print(f"⚠️ Індекс можливо вже існує: {e}")
        
        # Створюємо constraints
        for constraint_query in CypherTemplates.CREATE_CONSTRAINTS:
            try:
                await conn.execute_query(constraint_query)
                print(f"✅ Constraint створено")
            except Exception as e:
                print(f"⚠️ Constraint можливо вже існує: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення індексів: {e}")
        return False

async def test_crud_operations() -> bool:
    """Тест CRUD операцій"""
    print("🔍 Тестуємо CRUD операції...")
    
    try:
        conn = await get_neo4j_connection()
        
        # CREATE: Створюємо тестовий Intent
        test_intent = Intent(
            name="test_health_check",
            description="Тестовий намір для health check",
            confidence=0.9,
            lang="uk",
            category="system_test"
        )
        
        create_result = await conn.execute_query(
            """
            MERGE (i:Intent {name: $name, lang: $lang})
            ON CREATE SET i += $props, i.created_at = datetime()
            ON MATCH SET i.updated_at = datetime()
            RETURN i.id as id, i.name as name
            """,
            test_intent.to_cypher_params()
        )
        
        if create_result:
            intent_id = create_result[0]["id"]
            print(f"✅ CREATE: Intent створено з ID {intent_id}")
        else:
            print("❌ CREATE: Не вдалося створити Intent")
            return False
        
        # READ: Читаємо створений Intent
        read_result = await conn.execute_query(
            "MATCH (i:Intent {name: $name}) RETURN i.id as id, i.confidence as confidence",
            {"name": "test_health_check"}
        )
        
        if read_result:
            confidence = read_result[0]["confidence"]
            print(f"✅ READ: Intent прочитано, confidence = {confidence}")
        else:
            print("❌ READ: Не вдалося прочитати Intent")
            return False
        
        # UPDATE: Оновлюємо Intent
        await conn.execute_query(
            """
            MATCH (i:Intent {name: $name})
            SET i.confidence = $new_confidence, i.updated_at = datetime()
            RETURN i.confidence as confidence
            """,
            {"name": "test_health_check", "new_confidence": 0.95}
        )
        print("✅ UPDATE: Intent оновлено")
        
        # DELETE: Видаляємо тестовий Intent
        await conn.execute_query(
            "MATCH (i:Intent {name: $name}) DELETE i",
            {"name": "test_health_check"}
        )
        print("✅ DELETE: Тестовий Intent видалено")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка CRUD операцій: {e}")
        return False

async def test_performance() -> Dict[str, Any]:
    """Тест продуктивності"""
    print("🔍 Тестуємо продуктивність...")
    
    import time
    
    try:
        conn = await get_neo4j_connection()
        
        # Тест швидкості простого запиту
        start_time = time.time()
        await conn.execute_query("RETURN 1 as test")
        simple_query_time = time.time() - start_time
        
        # Тест кешування
        cache_key = "test_cache"
        start_time = time.time()
        await conn.execute_query(
            "RETURN 'cached_result' as result", 
            cache_key=cache_key
        )
        first_query_time = time.time() - start_time
        
        start_time = time.time()
        await conn.execute_query(
            "RETURN 'cached_result' as result", 
            cache_key=cache_key
        )
        cached_query_time = time.time() - start_time
        
        perf_results = {
            "simple_query_ms": round(simple_query_time * 1000, 2),
            "first_query_ms": round(first_query_time * 1000, 2),
            "cached_query_ms": round(cached_query_time * 1000, 2),
            "cache_speedup": round(first_query_time / cached_query_time, 2) if cached_query_time > 0 else "N/A"
        }
        
        print(f"✅ Продуктивність:")
        print(f"   - Простий запит: {perf_results['simple_query_ms']} мс")
        print(f"   - Перший запит: {perf_results['first_query_ms']} мс")
        print(f"   - Кешований запит: {perf_results['cached_query_ms']} мс")
        print(f"   - Прискорення кешу: {perf_results['cache_speedup']}x")
        
        return perf_results
        
    except Exception as e:
        print(f"❌ Помилка тесту продуктивності: {e}")
        return {"error": str(e)}

async def main():
    """Головна функція health check"""
    print("🚀 ISKALA MOVA Neo4j Infrastructure Health Check")
    print("=" * 50)
    
    results = {
        "timestamp": asyncio.get_event_loop().time(),
        "tests": {}
    }
    
    # Тест 1: Базове підключення
    connectivity_result = await test_basic_connectivity()
    results["tests"]["connectivity"] = connectivity_result
    
    # Тест 2: Базовий запит
    basic_query_result = await test_basic_query()
    results["tests"]["basic_query"] = basic_query_result
    
    # Тест 3: Створення індексів
    if basic_query_result:
        indexes_result = await test_create_indexes()
        results["tests"]["indexes"] = indexes_result
    
    # Тест 4: CRUD операції
    if basic_query_result:
        crud_result = await test_crud_operations()
        results["tests"]["crud"] = crud_result
    
    # Тест 5: Продуктивність
    if basic_query_result:
        perf_result = await test_performance()
        results["tests"]["performance"] = perf_result
    
    # Підсумок
    print("\n" + "=" * 50)
    print("📊 ПІДСУМОК HEALTH CHECK:")
    
    all_passed = True
    for test_name, test_result in results["tests"].items():
        if test_name == "performance":
            status = "✅ PASSED" if "error" not in test_result else "❌ FAILED"
        else:
            status = "✅ PASSED" if test_result else "❌ FAILED"
        
        print(f"   {test_name.upper()}: {status}")
        if not test_result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Всі тести пройдено успішно! Neo4j infrastructure готова до роботи.")
        exit_code = 0
    else:
        print("\n⚠️ Деякі тести не пройдено. Перевірте конфігурацію.")
        exit_code = 1
    
    # Закриваємо з'єднання
    try:
        from services.neo4j_driver import close_neo4j_connection
        await close_neo4j_connection()
        print("🔌 З'єднання закрито")
    except:
        pass
    
    # Зберігаємо результати
    with open("health_check_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"📄 Результати збережено в health_check_results.json")
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Health check перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Критична помилка: {e}")
        sys.exit(1) 