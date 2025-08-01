# 🌺 ISKALA MOVA - Українська AI система

## 🚀 Швидкий старт

### Docker (рекомендовано)

```bash
# Запуск всіх сервісів
./start_iskala_docker.sh

# Або для Windows PowerShell
./start_iskala_docker.ps1
```

### Ручний запуск

```bash
# ISKALA Core
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001

# OpenAPI Tool Server
python iskala_openapi_server.py

# Open WebUI (окремо)
docker run -d --name open-webui -p 3000:8080 ghcr.io/open-webui/open-webui:main
```

## 🏗️ Архітектура

### Сервіси

- **ISKALA Core** (порт 8001) - основна логіка та пам'ять
- **ISKALA OpenAPI Tool Server** (порт 8003) - API функції для Open WebUI
- **Open WebUI** (порт 3000) - веб інтерфейс з інтегрованими інструментами

### Модулі

- **Vault** - безпечне зберігання
- **Translation** - система перекладу
- **RAG** - пошук по документах
- **Shield** - система безпеки

## 🔧 Інтеграція з Open WebUI

### Автоматична інтеграція

При запуску через Docker всі сервіси автоматично налаштовуються.

### Ручна інтеграція

1. Відкрийте Open WebUI: `http://localhost:3000`
2. Settings → Tools → Add Tool
3. OpenAPI Tool Server
4. URL: `http://localhost:8003/openapi.json`
5. Name: `ISKALA Modules`

## 📋 Доступні API функції

### ISKALA Core
- `search_iskala_memory` - пошук в пам'яті
- `call_iskala_tool` - виклик інструментів
- `get_iskala_status` - статус модулів

### Доступні інструменти
- `file` - робота з файлами
- `command` - виконання команд
- `api` - API запити
- `memory` - робота з пам'яттю

## 🌐 API Endpoints

### ISKALA Core
- `GET /health` - статус сервісу
- `GET /api/openwebui/models` - список моделей
- `POST /api/openwebui/chat` - чат API
- `GET /api/openwebui/status` - статус інтеграції

### OpenAPI Tool Server
- `GET /openapi.json` - OpenAPI схема
- `POST /iskala/memory/search` - пошук в пам'яті
- `POST /iskala/tools/call` - виклик інструментів
- `GET /iskala/status` - статус модулів

## 🔗 Корисні посилання

- **Open WebUI**: http://localhost:3000
- **ISKALA Core**: http://localhost:8001
- **OpenAPI Tool Server**: http://localhost:8003
- **OpenAPI схема**: http://localhost:8003/openapi.json

## 📖 Документація

- [Повна інтеграція](FINAL_ISKALA_API_INTEGRATION.md)
- [Швидкий старт](QUICK_START_ISKALA_API.md)
- [Руководство по інтеграції](ISKALA_API_INTEGRATION_GUIDE.md)

## 🛠️ Розробка

### Структура проекту

```
iskala/
├── src/                    # Основний код
├── system_prompts/         # Системні промпти
├── data/                   # Дані
├── state/                  # Стан системи
├── vault/                  # Модуль безпеки
├── translation/            # Модуль перекладу
├── rag_system/            # RAG система
├── shield/                # Система захисту
├── iskala_openapi_server.py  # OpenAPI Tool Server
└── docker-compose.yml     # Docker конфігурація
```

### Залежності

```bash
pip install -r requirements.txt
```

## 🚀 Можливості

- **Українська мова** - повна підтримка української мови
- **Модульна архітектура** - гнучка система модулів
- **API інтеграція** - легка інтеграція з іншими системами
- **Open WebUI** - сучасний веб інтерфейс
- **Docker** - простий розгортання
- **Безпека** - вбудована система захисту

## 📄 Ліцензія

MIT License 