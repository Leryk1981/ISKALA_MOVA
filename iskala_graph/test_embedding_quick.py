#!/usr/bin/env python3
"""
Швидкий тест EmbeddingService
============================

Простий тест для швидкої перевірки функціональності EmbeddingService
без залежності від Redis та інших external сервісів.
"""

import asyncio
import time
import sys
from pathlib import Path

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent))

async def quick_test():
    """Швидкий тест основної функціональності"""
    print("🧪 Швидкий тест ISKALA MOVA Embedding Service")
    print("=" * 50)
    
    try:
        from services.embedding_service import EmbeddingService, EmbeddingConfig
        
        # Конфігурація без Redis для швидкого тесту
        config = EmbeddingConfig(
            model_name="all-MiniLM-L6-v2",
            device="cpu",  # CPU для стабільності
            redis_host="nonexistent",  # Недоступний Redis
            redis_port=9999
        )
        
        service = EmbeddingService(config)
        
        print("🔄 Ініціалізація сервісу...")
        start_time = time.time()
        await service.initialize()
        init_time = time.time() - start_time
        print(f"✅ Ініціалізація завершена за {init_time:.2f}s")
        
        # Тест 1: Генерація embedding
        print("\n📊 Тест 1: Генерація embedding")
        test_text = "Привіт, ISKALA MOVA!"
        
        start_time = time.time()
        embedding = await service.get_embedding(test_text)
        duration = time.time() - start_time
        
        print(f"Текст: {test_text}")
        print(f"Розмірність: {len(embedding)}")
        print(f"Час генерації: {duration*1000:.2f}ms")
        print(f"Тип даних: {type(embedding[0])}")
        print(f"Перші 3 значення: {embedding[:3]}")
        
        # Перевірки
        assert len(embedding) == 384, f"Неправильна розмірність: {len(embedding)}"
        assert all(isinstance(x, float) for x in embedding), "Embedding містить не float"
        
        # Тест 2: Batch processing
        print("\n📦 Тест 2: Batch processing")
        texts = [
            "Перший тестовий текст",
            "Другий тестовий текст", 
            "Третій тестовий текст"
        ]
        
        start_time = time.time()
        embeddings = await service.get_embeddings_batch(texts)
        batch_duration = time.time() - start_time
        
        print(f"Кількість текстів: {len(texts)}")
        print(f"Кількість embeddings: {len(embeddings)}")
        print(f"Загальний час: {batch_duration*1000:.2f}ms")
        print(f"Час на текст: {batch_duration*1000/len(texts):.2f}ms")
        
        # Перевірки
        assert len(embeddings) == len(texts), "Кількість embeddings не співпадає"
        assert all(len(emb) == 384 for emb in embeddings), "Неправильні розмірності"
        
        # Тест 3: Similarity
        print("\n🔍 Тест 3: Similarity між текстами")
        text1 = "Програмування на Python"
        text2 = "Розробка на мові Python"
        text3 = "Приготування їжі"
        
        sim_12 = await service.get_similarity(text1, text2)
        sim_13 = await service.get_similarity(text1, text3)
        
        print(f"'{text1}' vs '{text2}': {sim_12:.4f}")
        print(f"'{text1}' vs '{text3}': {sim_13:.4f}")
        
        # Схожі тексти повинні мати вищий similarity
        assert sim_12 > sim_13, "Similarity працює неправильно"
        assert 0 <= sim_12 <= 1, "Similarity поза межами [0,1]"
        assert 0 <= sim_13 <= 1, "Similarity поза межами [0,1]"
        
        # Тест 4: Health check
        print("\n🩺 Тест 4: Health check")
        health = await service.health_check()
        
        print(f"Статус: {health['status']}")
        print(f"Модель завантажена: {health['model_loaded']}")
        print(f"Redis (очікується False): {health['redis_connected']}")
        
        assert health['status'] == 'healthy', "Сервіс нездоровий"
        assert health['model_loaded'] is True, "Модель не завантажена"
        assert health['redis_connected'] is False, "Redis не повинен бути підключений"
        
        # Тест 5: Статистика
        print("\n📈 Тест 5: Статистика")
        stats = await service.get_stats()
        
        print(f"Загальних запитів: {stats['performance']['total_requests']}")
        print(f"Cache enabled: {stats['cache']['enabled']}")
        print(f"Модель: {stats['model_info']['name']}")
        print(f"Пристрій: {stats['model_info']['device']}")
        
        # Cleanup
        await service.close()
        
        print("\n🎉 Всі тести пройдено успішно!")
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("Переконайтеся що встановлені залежності:")
        print("pip install sentence-transformers torch numpy redis zstd")
        return False
        
    except Exception as e:
        print(f"❌ Помилка під час тестування: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Головна функція"""
    success = await quick_test()
    
    if success:
        print("\n✅ Швидкий тест завершено успішно!")
        print("🚀 EmbeddingService готовий до використання!")
    else:
        print("\n❌ Тест не пройдено, перевірте конфігурацію")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 