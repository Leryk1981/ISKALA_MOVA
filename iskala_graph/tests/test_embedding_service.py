"""
Тести для EmbeddingService
==========================

Comprehensive тести для перевірки:
- Генерації embeddings та їх розмірності
- Redis кешування (hit/miss сценарії) 
- Batch processing та оптимізації
- Benchmark тести продуктивності
- Multi-process functionality
"""

import pytest
import asyncio
import time
import os
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock

# Імпорти тестового модуля
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.embedding_service import (
    EmbeddingService, 
    EmbeddingConfig, 
    get_embedding_service,
    close_embedding_service
)

class TestEmbeddingService:
    """Основні тести EmbeddingService"""
    
    @pytest.fixture
    async def embedding_service(self):
        """Fixture для створення EmbeddingService"""
        config = EmbeddingConfig(
            model_name="all-MiniLM-L6-v2",
            device="cpu",  # Використовуємо CPU для стабільних тестів
            cache_ttl=300,
            batch_size=16,
            redis_host="localhost",
            redis_port=6379
        )
        
        service = EmbeddingService(config)
        await service.initialize()
        
        yield service
        
        # Cleanup
        await service.clear_cache()
        await service.close()
    
    @pytest.fixture
    def sample_texts(self):
        """Fixture з тестовими текстами на українській мові"""
        return [
            "Привіт, як справи?",
            "Допоможи мені з програмуванням на Python",
            "Україна - прекрасна країна з багатою історією",
            "Машинне навчання змінює світ технологій",
            "Київ - столиця України та її культурний центр"
        ]
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, embedding_service):
        """Тест ініціалізації сервісу"""
        assert embedding_service._initialized is True
        assert embedding_service.model is not None
        assert embedding_service.config.model_name == "all-MiniLM-L6-v2"
        
        # Перевірка розмірності embedding
        dimension = embedding_service.model.get_sentence_embedding_dimension()
        assert dimension == 384  # all-MiniLM-L6-v2 має 384 розмірності
    
    @pytest.mark.asyncio
    async def test_single_embedding_generation(self, embedding_service, sample_texts):
        """Тест генерації одного embedding"""
        text = sample_texts[0]
        
        start_time = time.time()
        embedding = await embedding_service.get_embedding(text)
        duration_ms = (time.time() - start_time) * 1000
        
        # Перевірки
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # Розмірність all-MiniLM-L6-v2
        assert all(isinstance(x, float) for x in embedding)
        
        # Перевірка що embedding нормалізований (якщо normalize_embeddings=True)
        if embedding_service.config.normalize_embeddings:
            norm = np.linalg.norm(embedding)
            assert abs(norm - 1.0) < 1e-6, f"Embedding не нормалізований: norm={norm}"
        
        # Performance requirement: < 100ms для 512 токенів на CPU
        print(f"Single embedding generation: {duration_ms:.2f}ms")
        # Для CPU можемо бути більш терпимими
        assert duration_ms < 1000, f"Embedding generation занадто повільна: {duration_ms}ms"
    
    @pytest.mark.asyncio
    async def test_batch_embedding_generation(self, embedding_service, sample_texts):
        """Тест batch генерації embeddings"""
        
        start_time = time.time()
        embeddings = await embedding_service.get_embeddings_batch(sample_texts)
        duration_ms = (time.time() - start_time) * 1000
        
        # Перевірки
        assert len(embeddings) == len(sample_texts)
        assert all(len(emb) == 384 for emb in embeddings)
        assert all(isinstance(emb, list) for emb in embeddings)
        
        # Перевірка унікальності embeddings для різних текстів
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = np.dot(embeddings[i], embeddings[j])
                assert similarity < 0.95, "Embeddings занадто схожі для різних текстів"
        
        print(f"Batch embeddings ({len(sample_texts)} texts): {duration_ms:.2f}ms")
        
        # Batch повинен бути ефективнішим за послідовні виклики
        avg_per_text = duration_ms / len(sample_texts)
        assert avg_per_text < 500, f"Batch processing неефективний: {avg_per_text:.2f}ms/text"
    
    @pytest.mark.asyncio
    async def test_cache_hit_scenario(self, embedding_service):
        """Тест сценарію попадання в кеш"""
        text = "Тестовий текст для кешування"
        
        # Скидаємо статистику
        embedding_service.stats.cache_hits = 0
        embedding_service.stats.cache_misses = 0
        embedding_service.stats.total_requests = 0
        
        # Перший виклик - має бути cache miss
        start_time = time.time()
        embedding1 = await embedding_service.get_embedding(text)
        first_call_time = time.time() - start_time
        
        assert embedding_service.stats.cache_misses == 1
        assert embedding_service.stats.cache_hits == 0
        
        # Другий виклик - має бути cache hit
        start_time = time.time()
        embedding2 = await embedding_service.get_embedding(text)
        second_call_time = time.time() - start_time
        
        assert embedding_service.stats.cache_hits == 1
        assert embedding_service.stats.cache_misses == 1
        
        # Перевірка ідентичності embeddings
        assert embedding1 == embedding2, "Кешовані embeddings не співпадають"
        
        # Cache hit повинен бути швидшим
        assert second_call_time < first_call_time, "Cache hit не прискорює виконання"
        
        print(f"Cache miss: {first_call_time*1000:.2f}ms, Cache hit: {second_call_time*1000:.2f}ms")
        print(f"Hit rate: {embedding_service.stats.hit_rate:.2f}%")
    
    @pytest.mark.asyncio
    async def test_cache_compression(self, embedding_service):
        """Тест компресії в кеші"""
        if not embedding_service.redis_client:
            pytest.skip("Redis недоступний для тестування компресії")
        
        text = "Довгий текст для тестування компресії кешу embeddings"
        
        # Генеруємо embedding
        embedding = await embedding_service.get_embedding(text)
        
        # Перевіряємо що дані збережено в кеші
        cache_key = embedding_service._generate_cache_key(text)
        cached_data = await embedding_service.redis_client.get(cache_key)
        
        assert cached_data is not None, "Дані не збережено в кеші"
        
        # При використанні компресії, розмір повинен бути менший
        if embedding_service.config.use_compression:
            import json
            uncompressed_size = len(json.dumps(embedding).encode('utf-8'))
            compressed_size = len(cached_data)
            
            print(f"Uncompressed: {uncompressed_size} bytes, Compressed: {compressed_size} bytes")
            print(f"Compression ratio: {uncompressed_size/compressed_size:.2f}")
            
            # Компресія повинна зменшувати розмір (зазвичай 2-5x для JSON)
            assert compressed_size < uncompressed_size, "Компресія не зменшує розмір"
    
    @pytest.mark.asyncio
    async def test_similarity_calculation(self, embedding_service):
        """Тест обчислення similarity між текстами"""
        similar_texts = [
            "Програмування на Python",
            "Розробка програм на мові Python"
        ]
        
        different_texts = [
            "Програмування на Python", 
            "Приготування борщу"
        ]
        
        # Similarity для схожих текстів
        similar_score = await embedding_service.get_similarity(
            similar_texts[0], similar_texts[1]
        )
        
        # Similarity для різних текстів
        different_score = await embedding_service.get_similarity(
            different_texts[0], different_texts[1]
        )
        
        print(f"Similar texts similarity: {similar_score:.4f}")
        print(f"Different texts similarity: {different_score:.4f}")
        
        # Схожі тексти повинні мати вищий similarity
        assert similar_score > different_score
        assert similar_score > 0.5  # Досить схожі
        assert different_score < 0.5  # Не дуже схожі
        assert 0 <= similar_score <= 1
        assert 0 <= different_score <= 1
    
    @pytest.mark.asyncio
    async def test_most_similar_search(self, embedding_service, sample_texts):
        """Тест пошуку найбільш схожих текстів"""
        query = "Допомога з Python програмуванням"
        candidates = sample_texts
        
        results = await embedding_service.find_most_similar(
            query, candidates, top_k=3
        )
        
        # Перевірки структури результату
        assert len(results) == 3
        assert all("text" in result for result in results)
        assert all("similarity" in result for result in results)
        assert all("index" in result for result in results)
        
        # Перевірка сортування за спаданням similarity
        similarities = [result["similarity"] for result in results]
        assert similarities == sorted(similarities, reverse=True)
        
        # Найбільш схожий текст повинен бути про програмування
        top_result = results[0]
        print(f"Query: {query}")
        print(f"Most similar: {top_result['text']} (similarity: {top_result['similarity']:.4f})")
        
        assert "програмування" in top_result["text"].lower() or "python" in top_result["text"].lower()
    
    @pytest.mark.asyncio
    async def test_health_check(self, embedding_service):
        """Тест health check функціональності"""
        health = await embedding_service.health_check()
        
        # Перевірка структури відповіді
        required_fields = ["service", "status", "model_loaded", "redis_connected", "timestamp"]
        assert all(field in health for field in required_fields)
        
        # Перевірка значень
        assert health["service"] == "embedding_service"
        assert health["status"] in ["healthy", "unhealthy"]
        assert health["model_loaded"] is True
        assert isinstance(health["timestamp"], float)
        assert "embedding_test" in health
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, embedding_service, sample_texts):
        """Тест відстеження статистики"""
        # Скидаємо статистику
        embedding_service.stats.total_requests = 0
        embedding_service.stats.cache_hits = 0
        embedding_service.stats.cache_misses = 0
        
        # Виконуємо кілька операцій
        await embedding_service.get_embedding(sample_texts[0])  # cache miss
        await embedding_service.get_embedding(sample_texts[0])  # cache hit
        await embedding_service.get_embeddings_batch(sample_texts[1:3])  # batch
        
        stats = await embedding_service.get_stats()
        
        # Перевірка структури статистики
        assert "model_info" in stats
        assert "performance" in stats
        assert "cache" in stats
        
        # Перевірка значень
        perf_stats = stats["performance"]
        assert perf_stats["total_requests"] > 0
        assert "cache_hit_rate" in perf_stats
        assert "avg_processing_time_ms" in perf_stats
        
        print(f"Statistics: {stats['performance']}")
    
    @pytest.mark.asyncio
    async def test_empty_input_handling(self, embedding_service):
        """Тест обробки порожнього вводу"""
        # Порожній список
        embeddings = await embedding_service.get_embeddings_batch([])
        assert embeddings == []
        
        # Порожній рядок
        embedding = await embedding_service.get_embedding("")
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, embedding_service):
        """Тест генерації ключів кешу"""
        text1 = "Тестовий текст"
        text2 = "Тестовий текст"  # Ідентичний
        text3 = "Інший текст"
        
        key1 = embedding_service._generate_cache_key(text1)
        key2 = embedding_service._generate_cache_key(text2)
        key3 = embedding_service._generate_cache_key(text3)
        
        # Ідентичні тексти повинні давати ідентичні ключі
        assert key1 == key2
        
        # Різні тексти повинні давати різні ключі
        assert key1 != key3
        
        # Ключі повинні мати правильний формат
        assert key1.startswith("emb:")
        assert len(key1.split(":")) == 4  # emb:model:max_len:hash

class TestEmbeddingServiceBenchmarks:
    """Benchmark тести для оцінки продуктивності"""
    
    @pytest.fixture
    async def benchmark_service(self):
        """Fixture для benchmark тестів"""
        config = EmbeddingConfig(
            model_name="all-MiniLM-L6-v2",
            device="cpu",
            batch_size=32,
            normalize_embeddings=True
        )
        
        service = EmbeddingService(config)
        await service.initialize()
        
        yield service
        
        await service.close()
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_single_embedding_benchmark(self, benchmark_service, benchmark):
        """Benchmark тест для одного embedding"""
        text = "Тестовий текст для benchmark вимірювання продуктивності embedding generation"
        
        async def generate_embedding():
            return await benchmark_service.get_embedding(text)
        
        # Використовуємо pytest-benchmark
        result = benchmark(lambda: asyncio.run(generate_embedding()))
        
        assert len(result) == 384
        print(f"Single embedding benchmark completed")
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_batch_embedding_benchmark(self, benchmark_service, benchmark):
        """Benchmark тест для batch embedding"""
        texts = [f"Тестовий текст номер {i} для benchmark" for i in range(50)]
        
        async def generate_batch_embeddings():
            return await benchmark_service.get_embeddings_batch(texts)
        
        result = benchmark(lambda: asyncio.run(generate_batch_embeddings()))
        
        assert len(result) == 50
        assert all(len(emb) == 384 for emb in result)
        print(f"Batch embedding benchmark completed for {len(texts)} texts")
    
    @pytest.mark.benchmark
    @pytest.mark.asyncio
    async def test_cache_performance_benchmark(self, benchmark_service):
        """Benchmark тест для порівняння cache hit vs miss"""
        text = "Текст для benchmark кешування"
        
        # Прогрівання кешу
        await benchmark_service.get_embedding(text)
        
        # Benchmark cache miss (new text)
        start_time = time.time()
        await benchmark_service.get_embedding("Новий текст для cache miss")
        miss_time = time.time() - start_time
        
        # Benchmark cache hit
        start_time = time.time()
        await benchmark_service.get_embedding(text)
        hit_time = time.time() - start_time
        
        print(f"Cache miss: {miss_time*1000:.2f}ms")
        print(f"Cache hit: {hit_time*1000:.2f}ms")
        print(f"Speedup: {miss_time/hit_time:.2f}x")
        
        # Cache hit повинен бути мінімум в 5 разів швидшим
        assert miss_time / hit_time > 5, "Кеш не надає достатнього прискорення"

class TestEmbeddingServiceIntegration:
    """Інтеграційні тести з реальними компонентами"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_redis_integration(self):
        """Тест інтеграції з Redis"""
        config = EmbeddingConfig(
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_password=os.getenv("REDIS_PASSWORD")
        )
        
        service = EmbeddingService(config)
        await service.initialize()
        
        if not service.redis_client:
            pytest.skip("Redis не доступний для інтеграційного тестування")
        
        try:
            # Тест збереження та читання з Redis
            test_text = "Інтеграційний тест Redis"
            embedding = await service.get_embedding(test_text)
            
            # Перевіряємо що дані збережено
            cache_key = service._generate_cache_key(test_text)
            cached_data = await service.redis_client.get(cache_key)
            assert cached_data is not None
            
            # Другий виклик має бути з кешу
            embedding2 = await service.get_embedding(test_text)
            assert embedding == embedding2
            
            print("✅ Redis інтеграція успішна")
            
        finally:
            await service.close()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_global_service_singleton(self):
        """Тест глобального singleton сервісу"""
        # Отримуємо сервіс двічі
        service1 = await get_embedding_service()
        service2 = await get_embedding_service()
        
        # Повинен бути той самий instance
        assert service1 is service2
        
        # Тест функціональності
        embedding = await service1.get_embedding("Тест singleton")
        assert len(embedding) == 384
        
        # Cleanup
        await close_embedding_service()
        
        # Після закриття, новий виклик створює новий instance
        service3 = await get_embedding_service()
        assert service3 is not service1
        
        await close_embedding_service()

# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

if __name__ == "__main__":
    # Запуск тестів напряму
    pytest.main([__file__, "-v", "--tb=short"]) 