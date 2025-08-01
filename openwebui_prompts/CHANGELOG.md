# 📋 Changelog - Настройки Open WebUI для ISKALA

## 🔄 Версия 1.1.0 - Полная интеграция

### ✅ Добавлено:

#### 🎯 Workspace Permissions (Разрешения рабочего пространства):
- `USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS=true` - Доступ к загрузке промптов
- `USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS=true` - Доступ к управлению моделями
- `USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS=true` - Доступ к базе знаний
- `USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=true` - Доступ к инструментам
- `USER_PERMISSIONS_WORKSPACE_PROMPTS_ALLOW_PUBLIC_SHARING=true` - Публичный шаринг промптов

#### 🧠 RAG (Retrieval Augmented Generation):
- `ENABLE_RAG=true` - Включение RAG системы
- `RAG_EMBEDDING_ENGINE=openai` - Использование OpenAI для embeddings
- `RAG_EMBEDDING_MODEL=text-embedding-3-small` - Модель для embeddings
- `RAG_TOP_K=3` - Количество результатов для поиска
- `RAG_RELEVANCE_THRESHOLD=0.7` - Порог релевантности
- `CHUNK_SIZE=1000` - Размер чанков документов
- `CHUNK_OVERLAP=100` - Перекрытие чанков
- `RAG_FILE_MAX_SIZE=50` - Максимальный размер файла (МБ)
- `RAG_FILE_MAX_COUNT=10` - Максимальное количество файлов
- `RAG_ALLOWED_FILE_EXTENSIONS=["pdf","docx","txt","md","json","csv"]` - Разрешенные форматы

#### 📁 File Upload (Загрузка файлов):
- `USER_PERMISSIONS_CHAT_FILE_UPLOAD=true` - Разрешение загрузки файлов в чат
- `ENABLE_RAG_LOCAL_WEB_FETCH=true` - Локальная загрузка веб-страниц

#### 🔧 Tools & API (Инструменты и API):
- `ENABLE_DIRECT_CONNECTIONS=true` - Прямые подключения к API
- `USER_PERMISSIONS_FEATURES_DIRECT_TOOL_SERVERS=true` - Доступ к внешним инструментам
- `USER_PERMISSIONS_FEATURES_CODE_INTERPRETER=true` - Code Interpreter
- `USER_PERMISSIONS_FEATURES_WEB_SEARCH=true` - Веб-поиск
- `USER_PERMISSIONS_FEATURES_IMAGE_GENERATION=true` - Генерация изображений

#### 🌐 Web Search (Веб-поиск):
- `ENABLE_RAG_WEB_SEARCH=true` - Включение веб-поиска
- `RAG_WEB_SEARCH_RESULT_COUNT=3` - Количество результатов поиска
- `RAG_WEB_SEARCH_CONCURRENT_REQUESTS=5` - Количество одновременных запросов

#### 🚀 ISKALA Integration (Интеграция ISKALA):
- `CUSTOM_TOOLS_ENABLED=true` - Включение кастомных инструментов
- `CUSTOM_TOOLS_BASE_URL=http://iskala-openapi:8003` - URL ISKALA OpenAPI сервера

---

## 🔄 Версия 1.0.0 - Базовая настройка

### ✅ Добавлено:

#### 🔐 Безопасность:
- `WEBUI_SECRET_KEY=iskala-secret-key-2024` - Секретный ключ
- `DEFAULT_USER_ROLE=admin` - Роль по умолчанию
- `ENABLE_SIGNUP=true` - Разрешение регистрации
- `ENABLE_LOGIN_FORM=true` - Форма входа

#### 🌐 Веб-сервер:
- `WEBUI_HOST=0.0.0.0` - Хост
- `WEBUI_PORT=8080` - Порт
- `DISABLE_UI=false` - UI включен
- `DISABLE_API=false` - API включен
- `DISABLE_AUTH=false` - Аутентификация включена

#### 🤖 Модели:
- `OPENAI_API_BASE_URL=https://openrouter.ai/api/v1` - OpenRouter API
- `OPENAI_API_KEY=sk-or-v1-...` - API ключ OpenRouter
- `DEFAULT_MODELS=moonshotai/kimi-k2,openai/gpt-4,anthropic/claude-3.5-sonnet` - Модели по умолчанию
- `DEFAULT_MODELS_OPENAI=moonshotai/kimi-k2,openai/gpt-4` - OpenAI модели
- `DEFAULT_MODELS_ANTHROPIC=anthropic/claude-3.5-sonnet` - Anthropic модели

#### 🔧 Инструменты:
- `ENABLE_TOOLS=true` - Включение инструментов
- `TOOLS_ENABLED=true` - Инструменты активны
- `CUSTOM_MODELS_ENABLED=true` - Кастомные модели
- `CUSTOM_MODELS_BASE_URL=http://iskala-core:8001` - URL ISKALA Core

---

## 📊 Сравнение версий:

| Функция | v1.0.0 | v1.1.0 |
|---------|--------|--------|
| Загрузка промптов | ❌ | ✅ |
| RAG система | ❌ | ✅ |
| Загрузка файлов | ❌ | ✅ |
| Code Interpreter | ❌ | ✅ |
| Веб-поиск | ❌ | ✅ |
| Генерация изображений | ❌ | ✅ |
| ISKALA Tools | ❌ | ✅ |
| Knowledge Base | ❌ | ✅ |
| Direct Connections | ❌ | ✅ |

---

## 🚀 Что изменилось:

### До обновления:
- ❌ Нельзя загружать промпты
- ❌ Нет RAG системы
- ❌ Нет загрузки файлов
- ❌ Нет Code Interpreter
- ❌ Нет веб-поиска
- ❌ Нет ISKALA Tools

### После обновления:
- ✅ Можно загружать промпты MOVA
- ✅ Полноценная RAG система
- ✅ Загрузка документов (PDF, DOCX, TXT, MD, JSON, CSV)
- ✅ Code Interpreter для выполнения Python
- ✅ Веб-поиск с интеграцией
- ✅ Генерация изображений
- ✅ ISKALA Tools через OpenAPI
- ✅ Knowledge Base для документов
- ✅ Прямые подключения к API

---

## 🔧 Команды для применения:

### 1. Остановить контейнеры:
```bash
docker-compose down
```

### 2. Перезапустить с новыми настройками:
```bash
docker-compose up -d
```

### 3. Проверить логи:
```bash
docker-compose logs -f open-webui
```

### 4. Проверить переменные:
```bash
docker exec open-webui env | grep -i "workspace\|rag\|tools"
```

---

## 📝 Примечания:

- **Все настройки** применяются автоматически при перезапуске
- **RAG система** использует OpenAI embeddings (требует API ключ)
- **ISKALA Tools** доступны через OpenAPI сервер на порту 8003
- **Knowledge Base** поддерживает множество форматов файлов
- **Веб-поиск** интегрирован с RAG системой

---

## 🔗 Ссылки:

- [Инструкция по установке](INSTALLATION_GUIDE.md)
- [Документация Open WebUI](https://docs.openwebui.com)
- [RAG Configuration](https://docs.openwebui.com/getting-started/env-configuration)
- [Tools Integration](https://docs.openwebui.com/openapi-servers) 