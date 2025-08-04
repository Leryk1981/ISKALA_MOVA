# 🚀 ISKALA Graph Infrastructure

**Neo4j Graph Database + Sentence-Transformers Embedding Service** для української AI системи ISKALA MOVA.

## 📦 Компоненти

### 🗄️ **Neo4j Graph Database**
- Production-ready Neo4j 5.13 з APOC плагінами
- Async connection pool з retry logic
- Graph models для Intent, Phase, ContextChunk
- Vector indexing для semantic search

### 🧠 **Embedding Service** 
- sentence-transformers (all-MiniLM-L6-v2) оптимізований для української мови
- Redis кешування з zstd компресією
- Batch processing та multi-GPU підтримка
- Async/await API з детальною статистикою

## 🚀 Швидкий старт

### 1. Встановлення залежностей

```bash
cd iskala_graph
pip install -r requirements.txt
```

### 2. Запуск Neo4j infrastructure

```bash
# З основної директорії
docker-compose -f docker-compose.neo4j.yml up -d
```

### 3. Швидкий тест

```bash
cd iskala_graph
python test_embedding_quick.py
```

### 4. Health check

```bash
python health_check.py
```

## 💻 Використання

### EmbeddingService

```python
from iskala_graph import EmbeddingService, EmbeddingConfig

# Базове використання
service = EmbeddingService()
await service.initialize()

# Одне embedding
embedding = await service.get_embedding("Привіт, ISKALA MOVA!")
print(f"Розмірність: {len(embedding)}")  # 384

# Batch processing
texts = ["Перший текст", "Другий текст", "Третій текст"]
embeddings = await service.get_embeddings_batch(texts)

# Пошук схожості
similarity = await service.get_similarity("Python", "програмування")
print(f"Similarity: {similarity:.4f}")

# Пошук найбільш схожих
results = await service.find_most_similar(
    "допомога з кодуванням", 
    ["Python туторіал", "рецепт борщу", "JavaScript гід"],
    top_k=2
)

await service.close()
```

### Neo4j Graph

```python
from iskala_graph import get_neo4j_connection, Intent

# Підключення до Neo4j
conn = await get_neo4j_connection()

# Створення Intent
intent = Intent(
    name="допомога_з_python",
    description="Користувач потребує допомоги з Python",
    confidence=0.9,
    lang="uk"
)

# Збереження в граф
result = await conn.execute_query(
    """
    MERGE (i:Intent {name: $name, lang: $lang})
    ON CREATE SET i += $props
    RETURN i
    """,
    intent.to_cypher_params()
)
```

### Комбінований RAG пошук

```python
from iskala_graph import get_embedding_service, get_neo4j_connection

# Ініціалізація сервісів
embedding_service = await get_embedding_service()
neo4j_conn = await get_neo4j_connection()

# Генерація embedding для запиту
query = "як навчитися програмувати Python?"
query_embedding = await embedding_service.get_embedding(query)

# Пошук схожих ContextChunk в Neo4j
result = await neo4j_conn.execute_query(
    """
    CALL db.index.vector.queryNodes('chunk_embedding_idx', 5, $embedding)
    YIELD node as chunk, score
    RETURN chunk.content, score
    ORDER BY score DESC
    """,
    {"embedding": query_embedding}
)
```

## 🏗️ Архітектура

```
iskala_graph/
├── services/
│   ├── neo4j_driver.py      # Neo4j async driver
│   ├── graph_models.py      # Graph data models
│   └── embedding_service.py # Sentence-transformers service
├── cypher/
│   ├── intent_create.cypher # Intent CRUD operations
│   ├── phase_link.cypher    # Phase relationships
│   └── rag_chunk_add.cypher # RAG context chunks
├── tests/
│   └── test_embedding_service.py # Comprehensive tests
├── examples/
│   └── embedding_service_demo.py # Usage examples
├── health_check.py          # System health monitoring
└── test_embedding_quick.py  # Quick functionality test
```

## ⚙️ Конфігурація

### Environment Variables

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=iskala-neo4j-2024-secure
NEO4J_DATABASE=iskala-mova

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=iskala-redis-2024

# Embedding Service
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_CACHE_TTL=3600
```

### EmbeddingConfig

```python
config = EmbeddingConfig(
    model_name="all-MiniLM-L6-v2",           # Модель
    device="auto",                           # auto/cpu/cuda/mps
    normalize_embeddings=True,               # Нормалізація
    cache_ttl=3600,                         # TTL кешу (сек)
    batch_size=32,                          # Розмір batch
    use_compression=True,                   # zstd компресія
    multi_process_devices=["cuda:0", "cuda:1"]  # Multi-GPU
)
```

## 🧪 Тестування

### Основні тести

```bash
# Швидкий тест (без залежностей)
python test_embedding_quick.py

# Повні тести
pytest tests/ -v

# Benchmark тести
pytest tests/test_embedding_service.py::TestEmbeddingServiceBenchmarks -v

# Інтеграційні тести
pytest tests/test_embedding_service.py::TestEmbeddingServiceIntegration -v
```

### Benchmark результати

```
Single embedding: ~50-100ms (CPU), ~10-20ms (GPU)
Batch processing: ~15-30ms per text
Cache hit: ~1-5ms
Cache speedup: 10-50x
Compression ratio: 2-5x
```

## 📊 Моніторинг

### Health Check

```python
health = await service.health_check()
# {
#   "service": "embedding_service",
#   "status": "healthy", 
#   "model_loaded": true,
#   "redis_connected": true,
#   "embedding_test": true
# }
```

### Статистика

```python
stats = await service.get_stats()
# {
#   "performance": {
#     "total_requests": 1234,
#     "cache_hit_rate": "85.3%",
#     "avg_processing_time_ms": "45.2"
#   },
#   "model_info": {
#     "name": "all-MiniLM-L6-v2", 
#     "device": "cuda:0",
#     "dimension": 384
#   }
# }
```

## 🐳 Docker

### Neo4j + Redis

```bash
# Запуск infrastructure
docker-compose -f docker-compose.neo4j.yml up -d

# Перевірка статусу
docker ps | grep iskala
```

### Production deployment

```yaml
# docker-compose.prod.yml
services:
  neo4j:
    environment:
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
    volumes:
      - /data/neo4j:/data

  redis:
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## 🚨 Troubleshooting

### Помилка: "Model not found"

```bash
# Перевірка доступних моделей
python -c "from sentence_transformers import SentenceTransformer; print('OK')"

# Ручне завантаження
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Redis connection refused

```bash
# Перевірка Redis
docker logs iskala-redis
redis-cli ping

# Запуск без кешування
export REDIS_HOST=nonexistent
python test_embedding_quick.py
```

### Повільна обробка

```python
# Перевірка пристрою
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"MPS available: {torch.backends.mps.is_available()}")

# Встановлення GPU
config = EmbeddingConfig(device="cuda")  # або "mps"
```

## 🔗 Integration

### ISKALA Tool Server

```python
# В iskala_openapi_server.py
from iskala_graph import get_embedding_service

@app.post("/embedding/search")
async def semantic_search(query: str):
    service = await get_embedding_service()
    embedding = await service.get_embedding(query)
    return {"embedding": embedding, "dimension": len(embedding)}
```

### Open WebUI Plugin

```javascript
// Використання в openwebui_vfs_plugin.js
async function getEmbedding(text) {
    const response = await fetch('/iskala/embedding/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({query: text})
    });
    return response.json();
}
```

## 📚 Документація

- [Neo4j Setup Guide](../docs/NEO4J_SETUP.md)
- [Embedding Service API](./services/embedding_service.py)
- [Graph Models](./services/graph_models.py)
- [Examples](./examples/)

## 🆕 Changelog

### v0.2.0 (RAG + Graph Integration)
- ✅ EmbeddingService з sentence-transformers
- ✅ Redis кешування з zstd компресією  
- ✅ Batch processing та multi-GPU
- ✅ Comprehensive тести та benchmarks
- ✅ Ukrainian language optimization

### v0.1.0 (Neo4j Infrastructure)
- ✅ Neo4j 5.13 production setup
- ✅ Graph models та Cypher templates
- ✅ Async connection pool
- ✅ Health check система

---

**Статус**: ✅ Production Ready  
**Версія**: 0.2.0  
**Підтримка**: Ukrainian AI Community 