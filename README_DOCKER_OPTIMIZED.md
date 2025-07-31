# ISKALA - Оптимизированная Docker структура

## 🚀 Быстрый запуск

### Запуск ISKALA Core:
```bash
docker-compose up -d
```

### Запуск с Open WebUI:
```bash
# Запуск ISKALA
docker-compose up -d

# Запуск Open WebUI
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

## 📁 Структура контейнеров

### Оптимизированная версия (2 контейнера):

1. **iskala-core** - Объединенный сервис
   - Основной API: `http://localhost:8001`
   - Vault API: `http://localhost:8081`
   - Translation API: `http://localhost:8082`
   - RAG API: `http://localhost:8002`

2. **iskala-viewer** - Веб-интерфейс
   - MOVA Viewer: `http://localhost:5000`

## 🔧 Конфигурация

### Основные файлы:
- `Dockerfile` - Оптимизированный образ ISKALA Core
- `docker-compose.yml` - Конфигурация контейнеров
- `src/main.py` - Объединенный сервер

### Переменные окружения:
```yaml
ISKALA_ENV: production
ISKALA_PORT: 8001
VAULT_PORT: 8081
TRANSLATION_PORT: 8082
RAG_PORT: 8002
SHIELD_ENABLED: true
```

## 🌐 Доступные сервисы

### ISKALA Core API:
- **Health Check**: `GET /health`
- **LLM Processing**: `POST /api/llm/process`
- **WebSocket Chat**: `WS /ws`

### Vault API:
- **Health**: `GET /vault/health`
- **Encrypt**: `POST /vault/encrypt`

### Translation API:
- **Health**: `GET /translation/health`
- **Translate**: `POST /translation/translate`

### RAG API:
- **Health**: `GET /rag/health`
- **Search**: `POST /rag/search`

### Shield API:
- **Health**: `GET /shield/health`
- **Validate**: `POST /shield/validate`

## 📊 Мониторинг

### Проверка статуса:
```bash
# Статус контейнеров
docker-compose ps

# Логи ISKALA Core
docker-compose logs iskala-core

# Логи Viewer
docker-compose logs iskala-viewer
```

### Health Checks:
```bash
# ISKALA Core
curl http://localhost:8001/health

# Vault
curl http://localhost:8081/vault/health

# Translation
curl http://localhost:8082/translation/health

# RAG
curl http://localhost:8002/rag/health
```

## 🔄 Обновление

### Пересборка и перезапуск:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Обновление только кода:
```bash
docker-compose restart iskala-core
```

## 🛠️ Разработка

### Локальная разработка:
```bash
# Запуск без Docker
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

### Отладка:
```bash
# Логи в реальном времени
docker-compose logs -f iskala-core

# Вход в контейнер
docker-compose exec iskala-core bash
```

## 📈 Преимущества оптимизации

- **67% меньше контейнеров** (6 → 2)
- **Быстрее запуск** и развертывание
- **Меньше потребление ресурсов**
- **Проще управление** и мониторинг
- **Общие зависимости** и процессы

## 🔗 Интеграция с Open WebUI

Скрипт интеграции: `integrate_openwebui.py`

```bash
python integrate_openwebui.py
```

Создает:
- Конфигурацию интеграции
- Веб-интерфейс интеграции
- Скрипты запуска 