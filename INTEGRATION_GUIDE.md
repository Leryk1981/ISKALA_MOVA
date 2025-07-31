# 🌺 Руководство по интеграции ISKALA с Open WebUI

## 📋 Обзор интеграции

ISKALA MOVA теперь полностью интегрирована с Open WebUI, предоставляя:
- **Украинские языковые модели** для обработки естественного языка
- **RAG систему** для поиска и анализа документов
- **Систему перевода** для локализации
- **Безопасное хранилище** (Vault) и систему безопасности (Shield)
- **Инструменты и функции** для расширенной функциональности

## 🚀 Быстрый старт

### 1. Запуск сервисов

```bash
# Запуск ISKALA
docker-compose up -d

# Запуск Open WebUI
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### 2. Проверка статуса

```bash
# Проверка ISKALA
curl http://localhost:8001/health

# Проверка Open WebUI
curl http://localhost:3000/api/health
```

### 3. Автоматическая настройка

```bash
# Запуск скрипта настройки
python openwebui_integration/setup_openwebui.py

# Или использование готового скрипта
./openwebui_integration/start_integration.sh
```

## 🔧 Ручная настройка Open WebUI

### Шаг 1: Доступ к Open WebUI
1. Откройте браузер: http://localhost:3000
2. Создайте аккаунт или войдите в систему

### Шаг 2: Настройка моделей ISKALA

#### ISKALA MOVA v2 (Основная модель)
- **Provider**: Custom
- **Base URL**: `http://localhost:8001`
- **Model Name**: `iskala-mova-v2`
- **API Key**: (оставьте пустым)
- **Context Length**: 8192
- **Features**: chat, tools, memory, rag

#### ISKALA RAG (Система документов)
- **Provider**: Custom
- **Base URL**: `http://localhost:8001`
- **Model Name**: `iskala-rag`
- **API Key**: (оставьте пустым)
- **Context Length**: 16384
- **Features**: rag, search, documents

#### ISKALA Translation (Перевод)
- **Provider**: Custom
- **Base URL**: `http://localhost:8001`
- **Model Name**: `iskala-translation`
- **API Key**: (оставьте пустым)
- **Context Length**: 4096
- **Features**: translation, localization

### Шаг 3: Настройка API Endpoints

Добавьте следующие endpoints в Open WebUI:

#### Chat Endpoint
```
URL: http://localhost:8001/api/openwebui/chat
Method: POST
Headers: Content-Type: application/json
```

#### Models Endpoint
```
URL: http://localhost:8001/api/openwebui/models
Method: GET
```

#### Status Endpoint
```
URL: http://localhost:8001/api/openwebui/status
Method: GET
```

## 🌟 Возможности интеграции

### 1. Украинский язык и контекст
- Обработка украинского языка
- Понимание контекста и намерений
- Создание деревьев смыслов (MOVA Trees)

### 2. RAG система
- Поиск в документах
- Анализ и извлечение информации
- Контекстные ответы

### 3. Система перевода
- Перевод между языками
- Локализация контента
- Поддержка украинского языка

### 4. Безопасность
- Vault для безопасного хранения
- Shield для валидации и контроля
- Шифрование данных

### 5. Инструменты
- Todoist интеграция
- Универсальный API коннектор
- Пользовательские функции

## 🔍 API Endpoints

### Основные endpoints ISKALA

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/health` | GET | Проверка состояния |
| `/api/openwebui/chat` | POST | Чат с LLM |
| `/api/openwebui/models` | GET | Список моделей |
| `/api/openwebui/config` | GET | Конфигурация |
| `/api/openwebui/status` | GET | Статус интеграции |
| `/api/tools` | GET | Доступные инструменты |
| `/api/memory` | GET | Управление памятью |
| `/ws` | WebSocket | Real-time коммуникация |

### Примеры использования

#### Чат с ISKALA
```bash
curl -X POST http://localhost:8001/api/openwebui/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привіт, як справи?",
    "model_id": "iskala-mova-v2"
  }'
```

#### Получение списка моделей
```bash
curl http://localhost:8001/api/openwebui/models
```

#### Проверка статуса
```bash
curl http://localhost:8001/api/openwebui/status
```

## 🛠️ Устранение неполадок

### Проблема: Open WebUI не подключается к ISKALA

**Решение:**
1. Проверьте, что ISKALA запущена: `curl http://localhost:8001/health`
2. Убедитесь, что Open WebUI запущен: `curl http://localhost:3000/api/health`
3. Проверьте настройки моделей в Open WebUI
4. Убедитесь, что Base URL указан правильно: `http://localhost:8001`

### Проблема: Модели не отображаются

**Решение:**
1. Перезапустите Open WebUI: `docker restart open-webui`
2. Проверьте логи: `docker logs open-webui`
3. Убедитесь, что API endpoints настроены правильно

### Проблема: Ошибки в ответах

**Решение:**
1. Проверьте логи ISKALA: `docker-compose logs iskala-core`
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию в `src/main.py`

## 📊 Мониторинг

### Health Checks
```bash
# ISKALA
curl http://localhost:8001/health

# Open WebUI
curl http://localhost:3000/api/health

# Интеграция
curl http://localhost:8001/api/openwebui/status
```

### Логи
```bash
# ISKALA логи
docker-compose logs iskala-core

# Open WebUI логи
docker logs open-webui
```

## 🔄 Обновление интеграции

### Обновление ISKALA
```bash
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Обновление Open WebUI
```bash
docker stop open-webui
docker rm open-webui
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

## 📞 Поддержка

- **Документация**: README.md
- **Issues**: GitHub Issues
- **Конфигурация**: `openwebui_integration/openwebui_config.json`
- **Скрипты**: `openwebui_integration/`

## 🎯 Следующие шаги

1. **Тестирование**: Протестируйте все функции интеграции
2. **Настройка**: Настройте пользовательские промпты и конфигурации
3. **Развертывание**: Разверните в продакшн среде
4. **Мониторинг**: Настройте мониторинг и алерты

---

**ISKALA MOVA + Open WebUI** - Интегрированная система для работы с украинским языком и контекстом 