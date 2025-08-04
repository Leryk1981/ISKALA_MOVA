# 🔍 ISKALA Tool Server Architecture Analysis

## 📊 **Поточна архітектура системи**

### **Сервіси та порти:**
| Сервіс | Порт | URL | Призначення |
|--------|------|-----|-------------|
| ISKALA Core | 8001 | http://iskala-core:8001 | Основна логіка та пам'ять |
| Vault | 8081 | http://iskala-core:8081 | Безпечне зберігання |
| Translation | 8082 | http://iskala-core:8082 | Система перекладу |
| RAG System | 8002 | http://iskala-core:8002 | Пошук по документах |
| **OpenAPI Tool Server** | **8003** | **http://iskala-openapi:8003** | **API адаптер для Open WebUI** |
| Open WebUI | 3000 | http://localhost:3000 | Веб інтерфейс |

### **🏗️ Архітектурна схема:**
```
Open WebUI (3000)
    ↓ (consume OpenAPI schema)
ISKALA OpenAPI Tool Server (8003)
    ↓ (proxy requests to)
ISKALA Services:
    ├── Core (8001)
    ├── Vault (8081)  
    ├── Translation (8082)
    └── RAG (8002)
```

## 🔧 **Механізм реєстрації інструментів**

### **1. OpenAPI Schema Generation**
- **Файл:** `iskala_openapi_server.py`
- **Endpoint:** `GET /openapi.json`
- **Схема:** Вручну визначена в Python dictionary `OPENAPI_SCHEMA`

### **2. Інтеграція з Open WebUI**
```bash
# Ручна інтеграція:
1. Open WebUI → Settings → Tools → Add Tool
2. OpenAPI Tool Server
3. URL: http://localhost:8003/openapi.json
4. Name: ISKALA Modules
```

### **3. Структура OpenAPI Schema**
```json
{
    "openapi": "3.1.0",
    "info": {
        "title": "ISKALA Modules API",
        "description": "API для доступу к модулям ISKALA",
        "version": "1.0.0"
    },
    "paths": {
        "/iskala/memory/search": {
            "post": {
                "operationId": "search_iskala_memory",
                "summary": "Пошук в пам'яті ISKALA",
                ...
            }
        }
    }
}
```

## 📋 **Поточні інструменти**

| OperationId | Endpoint | Призначення |
|-------------|----------|-------------|
| `search_iskala_memory` | POST /iskala/memory/search | Пошук в пам'яті |
| `call_iskala_tool` | POST /iskala/tools/call | Виклик інструментів |
| `translate_text` | POST /iskala/translation/translate | Переклад тексту |
| `rag_search` | POST /iskala/rag/search | Пошук в RAG системі |
| `get_iskala_status` | GET /iskala/status | Статус модулів |

## 🔐 **Безпека та Аутентифікація**

### **Поточна реалізація:**
- **CORS:** Відкритий для всіх origins (`allow_origins=["*"]`)
- **Аутентифікація:** Не реалізована (відсутні Bearer tokens)
- **Rate Limiting:** Не реалізовано
- **Input Validation:** Через Pydantic models

### **Рівень безпеки:** ⚠️ **Базовий (не production-ready)**

## 🚀 **Паттерн інтеграції для Graph Search**

### **Необхідні кроки:**
1. **Створити окремий FastAPI адаптер** для ISKALA Graph Search
2. **Визначити нові endpoints** для семантичного пошуку
3. **Оновити OpenAPI schema** з новими operationId
4. **Інтегрувати з існуючим Tool Server** або створити окремий порт

### **Рекомендована архітектура:**
```
Open WebUI (3000)
    ↓
ISKALA OpenAPI Tool Server (8003) ← [EXISTING]
    ├── Core tools (memory, translate, etc.)
    └── Graph Search tools ← [NEW INTEGRATION]
         ↓
ISKALA Graph Search Service ← [OUR SERVICE]
    ├── SemanticSearchService
    ├── GraphVectorService  
    └── Neo4j + Redis
```

## 📊 **Технічні вимоги для інтеграції**

### **1. FastAPI Compatibility**
- **Framework:** FastAPI з CORS middleware
- **Models:** Pydantic для request/response validation
- **Schema:** OpenAPI 3.1.0 compliant

### **2. Endpoint Structure**
```python
# Рекомендовані endpoints:
POST /iskala/graph/search_hybrid     # operationId: graph_search_hybrid
POST /iskala/graph/search_vector     # operationId: graph_search_vector  
POST /iskala/graph/walk              # operationId: graph_walk
POST /iskala/graph/suggestions       # operationId: graph_suggestions
GET  /iskala/graph/status            # operationId: graph_status
```

### **3. Integration Options**

#### **Option A: Extend Existing Server** (Recommended)
- Додати endpoints до `iskala_openapi_server.py`
- Розширити `OPENAPI_SCHEMA`
- Використати існуючий порт 8003

#### **Option B: Separate Server**
- Створити `iskala_graph_openapi_server.py`
- Новий порт (наприклад, 8004)
- Окрема реєстрація в Open WebUI

### **4. Request/Response Patterns**
```python
# Request pattern (based on existing):
class GraphSearchRequest(BaseModel):
    query: str
    language: Optional[str] = None
    k: int = 5

# Response pattern:
{
    "results": [...],
    "total_results": 10,
    "search_time_ms": 150.5
}
```

## 🎯 **Рекомендований план імплементації**

### **Phase 1: Extension Approach** (3 дні)
1. **Розширити існуючий `iskala_openapi_server.py`:**
   - Додати graph search endpoints
   - Оновити OpenAPI schema
   - Додати Pydantic models

2. **Створити proxy логіку:**
   - Підключення до ISKALA Graph Search service
   - HTTP requests до наших FastAPI endpoints
   - Error handling та timeouts

3. **Тестування інтеграції:**
   - Перевірити OpenAPI schema в Swagger UI
   - Тестувати через Open WebUI
   - Валідувати всі endpoints

### **Phase 2: Production Enhancement** (2 дні)
1. **Додати безпеку:**
   - Bearer token authentication
   - Rate limiting
   - Input sanitization

2. **Performance optimization:**
   - Connection pooling
   - Retry mechanisms
   - Caching headers

## 📈 **Очікувані результати**

### **Нові інструменти в Open WebUI:**
- `graph_search_hybrid` - "Гібридний семантичний пошук"
- `graph_search_vector` - "Векторний пошук" 
- `graph_walk` - "Обхід графа знань"
- `graph_suggestions` - "Пошукові підказки"
- `graph_status` - "Статус Graph Search"

### **Користувацький досвід:**
```
User: "Знайди інформацію про машинне навчання українською"
Open WebUI → graph_search_hybrid → ISKALA Graph Search → Results
```

---

## ✅ **Висновки**

1. **Архітектура зрозуміла:** OpenAPI Tool Server як proxy/adapter
2. **Паттерн інтеграції визначений:** Розширення існуючого сервера
3. **Технічні вимоги ясні:** FastAPI + Pydantic + OpenAPI 3.1.0
4. **План реалізації готовий:** 3 дні для базової інтеграції

**🚀 Готовий до Phase 1: Розширення існуючого Tool Server!** 