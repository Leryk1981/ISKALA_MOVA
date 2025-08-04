#!/usr/bin/env python3
"""
Демонстрація EmbeddingService для ISKALA MOVA
============================================

Приклад використання embedding service з українськими текстами,
кешуванням та batch processing.
"""

import asyncio
import sys
import time
from pathlib import Path

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.embedding_service import EmbeddingService, EmbeddingConfig

async def demo_basic_embedding():
    """Демо базового використання embedding service"""
    print("🚀 Демонстрація ISKALA MOVA Embedding Service")
    print("=" * 50)
    
    # Конфігурація сервісу
    config = EmbeddingConfig(
        model_name="all-MiniLM-L6-v2",
        device="auto",  # Автоматичний вибір пристрою
        normalize_embeddings=True,
        cache_ttl=1800,  # 30 хвилин
        batch_size=16
    )
    
    # Ініціалізація сервісу
    service = EmbeddingService(config)
    await service.initialize()
    
    try:
        # Демо 1: Генерація одного embedding
        print("\n📊 Демо 1: Генерація embedding для одного тексту")
        text = "Програмування на Python - це цікаво і корисно"
        
        start_time = time.time()
        embedding = await service.get_embedding(text)
        duration = time.time() - start_time
        
        print(f"Текст: {text}")
        print(f"Розмірність embedding: {len(embedding)}")
        print(f"Перші 5 значень: {embedding[:5]}")
        print(f"Час генерації: {duration*1000:.2f}ms")
        
        # Демо 2: Кешування
        print("\n💾 Демо 2: Тестування кешування")
        print("Перший виклик (cache miss):")
        start_time = time.time()
        embedding1 = await service.get_embedding(text)
        miss_time = time.time() - start_time
        print(f"Час: {miss_time*1000:.2f}ms")
        
        print("Другий виклик (cache hit):")
        start_time = time.time()
        embedding2 = await service.get_embedding(text)
        hit_time = time.time() - start_time
        print(f"Час: {hit_time*1000:.2f}ms")
        
        print(f"Прискорення кешу: {miss_time/hit_time:.1f}x")
        print(f"Embeddings ідентичні: {embedding1 == embedding2}")
        
        # Демо 3: Batch processing
        print("\n📦 Демо 3: Batch processing")
        ukrainian_texts = [
            "Штучний інтелект змінює світ",
            "Машинне навчання допомагає розв'язувати складні задачі",
            "Україна має великий потенціал у сфері IT",
            "Київ - центр технологічних інновацій",
            "Python - популярна мова програмування"
        ]
        
        start_time = time.time()
        embeddings = await service.get_embeddings_batch(ukrainian_texts)
        batch_time = time.time() - start_time
        
        print(f"Оброблено {len(ukrainian_texts)} текстів")
        print(f"Загальний час: {batch_time*1000:.2f}ms")
        print(f"Середній час на текст: {batch_time*1000/len(ukrainian_texts):.2f}ms")
        
        # Демо 4: Пошук схожості
        print("\n🔍 Демо 4: Пошук найбільш схожих текстів")
        query = "Розробка програмного забезпечення"
        
        similar_results = await service.find_most_similar(
            query, ukrainian_texts, top_k=3
        )
        
        print(f"Запит: {query}")
        print("Найбільш схожі тексти:")
        for i, result in enumerate(similar_results, 1):
            print(f"{i}. {result['text']}")
            print(f"   Similarity: {result['similarity']:.4f}")
        
        # Демо 5: Статистика
        print("\n📈 Демо 5: Статистика роботи сервісу")
        stats = await service.get_stats()
        
        print(f"Модель: {stats['model_info']['name']}")
        print(f"Пристрій: {stats['model_info']['device']}")
        print(f"Загальних запитів: {stats['performance']['total_requests']}")
        print(f"Відсоток попадань у кеш: {stats['performance']['cache_hit_rate']}")
        print(f"Середній час обробки: {stats['performance']['avg_processing_time_ms']}ms")
        
        # Демо 6: Health check
        print("\n🩺 Демо 6: Health check")
        health = await service.health_check()
        print(f"Статус сервісу: {health['status']}")
        print(f"Модель завантажена: {health['model_loaded']}")
        print(f"Redis підключено: {health['redis_connected']}")
        
    finally:
        await service.close()
        print("\n✅ Демонстрацію завершено")

async def demo_similarity_search():
    """Демо семантичного пошуку українською мовою"""
    print("\n🇺🇦 Демо семантичного пошуку українською мовою")
    print("=" * 50)
    
    service = EmbeddingService()
    await service.initialize()
    
    try:
        # База знань українською
        knowledge_base = [
            "Київ - столиця України, розташована на річці Дніпро",
            "Львів - культурна столиця України з багатою історією",
            "Одеса - портове місто на березі Чорного моря",
            "Харків - важливий освітній та промисловий центр",
            "Дніпро - місто металургії та важкої промисловості",
            "Python - об'єктно-орієнтована мова програмування",
            "JavaScript використовується для веб-розробки",
            "Машинне навчання базується на алгоритмах і даних",
            "Штучний інтелект імітує людське мислення"
        ]
        
        # Тестові запити
        queries = [
            "Розкажи про столицю України",
            "Яке місто знаходиться на Дніпрі?",
            "Що таке програмування?",
            "Як працює машинне навчання?"
        ]
        
        for query in queries:
            print(f"\n🔍 Запит: {query}")
            results = await service.find_most_similar(
                query, knowledge_base, top_k=2
            )
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['text'][:60]}...")
                print(f"     Similarity: {result['similarity']:.4f}")
    
    finally:
        await service.close()

async def demo_performance_comparison():
    """Демо порівняння продуктивності"""
    print("\n⚡ Демо порівняння продуктивності")
    print("=" * 40)
    
    service = EmbeddingService()
    await service.initialize()
    
    try:
        # Генеруємо тестові дані
        test_texts = [
            f"Тестовий текст номер {i} для вимірювання продуктивності embedding service"
            for i in range(50)
        ]
        
        # Тест 1: Послідовна обробка
        print("📊 Послідовна обробка:")
        start_time = time.time()
        for text in test_texts:
            await service.get_embedding(text)
        sequential_time = time.time() - start_time
        print(f"Час: {sequential_time:.2f}s")
        
        # Очищуємо кеш для чесного порівняння
        await service.clear_cache()
        
        # Тест 2: Batch обробка
        print("📦 Batch обробка:")
        start_time = time.time()
        await service.get_embeddings_batch(test_texts)
        batch_time = time.time() - start_time
        print(f"Час: {batch_time:.2f}s")
        
        # Порівняння
        speedup = sequential_time / batch_time
        print(f"\n🚀 Прискорення batch processing: {speedup:.1f}x")
        
        # Тест кешу
        print("\n💾 Тест ефективності кешу:")
        cached_start = time.time()
        await service.get_embeddings_batch(test_texts)  # Всі мають бути в кеші
        cached_time = time.time() - cached_start
        
        cache_speedup = batch_time / cached_time
        print(f"Час з кешу: {cached_time:.2f}s")
        print(f"Прискорення кешу: {cache_speedup:.1f}x")
        
    finally:
        await service.close()

async def main():
    """Головна функція демонстрації"""
    try:
        await demo_basic_embedding()
        await demo_similarity_search()
        await demo_performance_comparison()
        
    except KeyboardInterrupt:
        print("\n⏹️ Демонстрацію перервано користувачем")
    except Exception as e:
        print(f"\n❌ Помилка під час демонстрації: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Запуск демонстрації
    asyncio.run(main()) 