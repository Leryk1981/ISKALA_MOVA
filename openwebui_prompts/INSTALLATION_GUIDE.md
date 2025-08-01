# 🚀 Инструкция по установке промптов MOVA в Open WebUI

## 📋 Проблема и решение

### ❌ Проблема:
При попытке загрузить JSON файлы с промптами в Open WebUI ничего не происходит - файлы не импортируются.

### ✅ Причина:
По умолчанию в Open WebUI **отключен доступ к Workspace Prompts** через переменную окружения `USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS=False`.

### 🔧 Решение:
Добавить необходимые переменные окружения в `docker-compose.yml`.

---

## 🛠️ Пошаговая инструкция:

### 1. Остановите контейнеры:
```bash
docker-compose down
```

### 2. Проверьте, что в `docker-compose.yml` добавлены переменные:
```yaml
# Разрешения для Workspace (включая загрузку промптов)
- USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS=true
- USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS=true
- USER_PERMISSIONS_WORKSPACE_KNOWLEDGE_ACCESS=true
- USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=true

# Разрешения для публичного шаринга промптов
- USER_PERMISSIONS_WORKSPACE_PROMPTS_ALLOW_PUBLIC_SHARING=true

# Настройки RAG (загрузка знаний)
- ENABLE_RAG=true
- RAG_EMBEDDING_ENGINE=openai
- RAG_EMBEDDING_MODEL=text-embedding-3-small
- RAG_TOP_K=3
- RAG_RELEVANCE_THRESHOLD=0.7
- CHUNK_SIZE=1000
- CHUNK_OVERLAP=100
- RAG_FILE_MAX_SIZE=50
- RAG_FILE_MAX_COUNT=10
- RAG_ALLOWED_FILE_EXTENSIONS=["pdf","docx","txt","md","json","csv"]

# Настройки загрузки файлов
- USER_PERMISSIONS_CHAT_FILE_UPLOAD=true
- ENABLE_RAG_LOCAL_WEB_FETCH=true

# Настройки инструментов и API
- ENABLE_DIRECT_CONNECTIONS=true
- USER_PERMISSIONS_FEATURES_DIRECT_TOOL_SERVERS=true
- USER_PERMISSIONS_FEATURES_CODE_INTERPRETER=true
- USER_PERMISSIONS_FEATURES_WEB_SEARCH=true
- USER_PERMISSIONS_FEATURES_IMAGE_GENERATION=true

# Настройки веб-поиска
- ENABLE_RAG_WEB_SEARCH=true
- RAG_WEB_SEARCH_RESULT_COUNT=3
- RAG_WEB_SEARCH_CONCURRENT_REQUESTS=5

# Настройки ISKALA OpenAPI Tools
- CUSTOM_TOOLS_ENABLED=true
- CUSTOM_TOOLS_BASE_URL=http://iskala-openapi:8003
```

### 3. Перезапустите контейнеры:
```bash
docker-compose up -d
```

### 4. Дождитесь полной загрузки:
```bash
docker-compose logs -f open-webui
```

---

## 📁 Загрузка промптов:

### Способ 1: Через File Upload (рекомендуется)

1. **Откройте Open WebUI:**
   ```
   http://localhost:3000
   ```

2. **Перейдите в Workspace:**
   ```
   Workspace → Prompts
   ```

3. **Нажмите "Import Prompts":**
   - Выберите один из JSON файлов:
     - `machine_mova_prompts.json`
     - `philosophy_mova_prompts.json`
     - `synthetic_mova_prompts.json`
   - Подтвердите импорт

4. **Проверьте результат:**
   - Промпты должны появиться в списке
   - Каждый промпт будет иметь свой ID и label

### Способ 2: Через создание Prompt Template

1. **Создайте новый промпт:**
   - Нажмите "Create Prompt"
   - Заполните метадани:
     - **Name**: "Machine MOVA System"
     - **Description**: "Машинный подход MOVA"
     - **Tags**: "mova", "system", "ukrainian"

2. **Вставьте содержимое:**
   - Откройте JSON файл
   - Скопируйте содержимое поля `value` нужного промпта
   - Вставьте в поле "Content"

3. **Сохраните промпт**

---

## 🧠 Загрузка знаний (RAG):

### Настройки RAG:
После обновления `docker-compose.yml` у вас будут доступны:

- **Загрузка файлов**: PDF, DOCX, TXT, MD, JSON, CSV
- **Максимальный размер**: 50 МБ
- **Максимальное количество**: 10 файлов за раз
- **Embedding модель**: OpenAI text-embedding-3-small
- **Чанкинг**: 1000 символов с перекрытием 100

### Как использовать:

1. **Загрузите документы:**
   ```
   Workspace → Knowledge
   ```

2. **Создайте коллекцию знаний:**
   - Нажмите "Create Knowledge"
   - Добавьте файлы
   - Настройте параметры индексации

3. **Используйте в чате:**
   - Выберите коллекцию знаний
   - Задайте вопрос
   - Система найдет релевантную информацию

---

## 🔧 Инструменты и API:

### Настройки инструментов:
После обновления будут доступны:

- **Direct Tool Servers**: Подключение к внешним API
- **Code Interpreter**: Выполнение Python кода
- **Web Search**: Поиск в интернете
- **Image Generation**: Генерация изображений
- **ISKALA Tools**: Ваши кастомные инструменты

### Подключение ISKALA Tools:

1. **Проверьте статус ISKALA OpenAPI Server:**
   ```bash
   docker-compose logs iskala-openapi
   ```

2. **В Open WebUI:**
   ```
   Admin Settings → Tools → Direct Connections
   ```

3. **Добавьте подключение:**
   - **Name**: "ISKALA Tools"
   - **URL**: `http://iskala-openapi:8003`
   - **Type**: OpenAPI

4. **Проверьте доступность:**
   - Инструменты должны появиться в списке
   - Можно использовать в чатах

---

## 🎯 Использование промптов:

### В чате:

1. **Создайте новый чат:**
   - Нажмите "New Chat"
   - Выберите модель (рекомендуется GPT-4 или Claude)

2. **Настройте System Prompt:**
   - Перейдите в настройки чата (⚙️)
   - Найдите поле "System Prompt"
   - Вставьте один из промптов MOVA

3. **Настройте температуру:**
   - **Машинный подход**: 0.5-0.7
   - **Философский подход**: 0.8-0.9
   - **Синтетический подход**: 0.7-0.8

### Через API:

```bash
curl -X POST http://localhost:3000/api/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "system",
        "content": "[Вставьте промпт MOVA здесь]"
      },
      {
        "role": "user",
        "content": "Привіт! Як справи?"
      }
    ],
    "temperature": 0.7
  }'
```

---

## 🔍 Проверка установки:

### 1. Проверьте логи:
```bash
docker-compose logs open-webui | grep -i "workspace\|prompt\|rag\|tools"
```

### 2. Проверьте переменные окружения:
```bash
docker exec open-webui env | grep -i "workspace\|prompt\|rag\|tools"
```

### 3. Проверьте доступность функций:
- **Workspace Prompts**: http://localhost:3000 → Workspace → Prompts
- **Knowledge Base**: http://localhost:3000 → Workspace → Knowledge
- **Tools**: http://localhost:3000 → Admin Settings → Tools

### 4. Проверьте ISKALA Tools:
```bash
curl http://localhost:8003/docs
```

---

## 🚨 Возможные проблемы:

### Проблема: "Import Prompts" не появляется
**Решение:** Проверьте, что переменная `USER_PERMISSIONS_WORKSPACE_PROMPTS_ACCESS=true` добавлена в docker-compose.yml

### Проблема: Файлы не импортируются
**Решение:** 
1. Проверьте формат JSON файлов
2. Убедитесь, что файлы не повреждены
3. Проверьте права доступа к файлам

### Проблема: RAG не работает
**Решение:**
1. Проверьте, что `ENABLE_RAG=true`
2. Убедитесь, что OpenAI API ключ настроен
3. Проверьте логи на ошибки embedding

### Проблема: ISKALA Tools не подключаются
**Решение:**
1. Проверьте статус `iskala-openapi` контейнера
2. Убедитесь, что URL правильный: `http://iskala-openapi:8003`
3. Проверьте логи на ошибки подключения

### Проблема: Промпты не работают
**Решение:**
1. Проверьте, что модель поддерживает системные промпты
2. Убедитесь, что температура настроена правильно
3. Проверьте, что промпт вставлен в поле "System Prompt"

---

## 📞 Поддержка:

Если проблемы остаются:

1. **Проверьте логи:**
   ```bash
   docker-compose logs open-webui
   docker-compose logs iskala-openapi
   ```

2. **Перезапустите контейнеры:**
   ```bash
   docker-compose restart open-webui
   docker-compose restart iskala-openapi
   ```

3. **Проверьте версию Open WebUI:**
   ```bash
   docker exec open-webui cat /app/backend/version.txt
   ```

4. **Проверьте сеть:**
   ```bash
   docker network ls
   docker network inspect iskala_iskala-network
   ```

---

## ✅ Готово!

После выполнения всех шагов вы сможете:
- ✅ Загружать JSON файлы с промптами
- ✅ Использовать промпты MOVA в чатах
- ✅ Создавать Prompt Templates
- ✅ Загружать документы в Knowledge Base
- ✅ Использовать RAG для поиска информации
- ✅ Подключать ISKALA Tools
- ✅ Использовать Code Interpreter
- ✅ Выполнять веб-поиск
- ✅ Генерировать изображения
- ✅ Интегрировать промпты через API

**Важно:** Все промпты поддерживают мультиязычность и автоматически адаптируются к языку пользователя.

---

## 🔗 Полезные ссылки:

- **Open WebUI Documentation**: https://docs.openwebui.com
- **RAG Configuration**: https://docs.openwebui.com/getting-started/env-configuration
- **Tools Integration**: https://docs.openwebui.com/openapi-servers
- **API Reference**: https://docs.openwebui.com/getting-started/api-endpoints 