# ISKALA MOVA - Интеллектуальная система кодирования и анализа языка

## 🎯 Описание проекта

ISKALA MOVA - это комплексная система для работы с украинским языком, включающая:
- **LLM-агенты** для обработки естественного языка
- **RAG-систему** для поиска и анализа документов
- **Vault** для безопасного хранения данных
- **Translation API** для перевода
- **Shield** для безопасности
- **Web UI** для взаимодействия с пользователем

## 🏗️ Архитектура

### Основные компоненты:
- **iskala-core** - объединенный основной сервис (API, Vault, Translation, RAG, Shield)
- **iskala-viewer** - веб-интерфейс для просмотра данных
- **Open WebUI** - современный веб-интерфейс для LLM

### Порты:
- `8001` - Основной API ISKALA
- `8081` - Vault API
- `8082` - Translation API
- `8002` - RAG API
- `5000` - ISKALA Viewer
- `3000` - Open WebUI

## 🚀 Быстрый старт

### Предварительные требования:
- Docker и Docker Compose
- Python 3.11+
- Git

### Установка:

1. **Клонирование репозитория:**
```bash
git clone <repository-url>
cd iskala
```

2. **Запуск с Docker:**
```bash
docker-compose up -d
```

3. **Проверка статуса:**
```bash
docker-compose ps
```

4. **Проверка health check:**
```bash
curl http://localhost:8001/health
```

## 📁 Структура проекта

```
iskala/
├── src/                    # Основной код
│   ├── main.py            # Главный API сервер
│   ├── llm_agent_v2.py    # LLM агент
│   └── ...
├── system_prompts/        # Системные промпты
├── data/                  # Данные и капсулы
├── state/                 # Состояние системы
├── trees/                 # Деревья мови
├── vault/                 # Безопасное хранилище
├── rag_system/           # RAG система
├── translation/          # API перевода
├── shield/               # Система безопасности
├── iskala-mova-viewer/   # Веб-интерфейс
├── openwebui_integration/ # Интеграция с Open WebUI
└── docker-compose.yml    # Docker конфигурация
```

## 🔧 Конфигурация

### Переменные окружения:
- `ISKALA_ENV` - окружение (production/development)
- `ISKALA_PORT` - порт основного API
- `VAULT_PORT` - порт Vault API
- `TRANSLATION_PORT` - порт Translation API
- `RAG_PORT` - порт RAG API
- `SHIELD_ENABLED` - включение Shield

### Файлы конфигурации:
- `docker-compose.yml` - Docker сервисы
- `Dockerfile` - образ для iskala-core
- `requirements.txt` - Python зависимости

## 🌐 API Endpoints

### Основной API (порт 8001):
- `GET /health` - проверка состояния
- `POST /chat` - чат с LLM
- `GET /api/v1/...` - основные API endpoints

### Vault API (порт 8081):
- `POST /vault/encrypt` - шифрование данных
- `POST /vault/decrypt` - расшифровка данных

### Translation API (порт 8082):
- `POST /translate` - перевод текста

### RAG API (порт 8002):
- `POST /rag/query` - поиск в документах

## 🔒 Безопасность

- **Shield** - система безопасности и контроля доступа
- **Vault** - шифрованное хранилище данных
- **Environment variables** - конфигурация через переменные окружения

## 📊 Мониторинг

### Health checks:
```bash
# Основной API
curl http://localhost:8001/health

# Vault
curl http://localhost:8081/health

# Translation
curl http://localhost:8082/health

# RAG
curl http://localhost:8002/health
```

### Логи:
```bash
# Просмотр логов контейнеров
docker-compose logs iskala-core
docker-compose logs iskala-viewer
```

## 🛠️ Разработка

### Локальная разработка:
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск основного сервера
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001

# Запуск Vault
python vault/main.py

# Запуск Translation
python translation/main.py

# Запуск RAG
python rag_system/main.py
```

### Тестирование:
```bash
# Проверка интеграции
python test_integration_status.py

# Тестирование API
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Привіт, світ!"}'
```

## 🔄 Интеграция с Open WebUI

1. **Запуск Open WebUI:**
```bash
docker run -d --name open-webui \
  -p 3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

2. **Настройка интеграции:**
```bash
python integrate_openwebui.py
```

3. **Доступ к интерфейсу:**
- Open WebUI: http://localhost:3000
- ISKALA Viewer: http://localhost:5000

## 📝 Лицензия

Проект разработан для исследовательских целей.

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Создайте Pull Request

## 📞 Поддержка

Для вопросов и предложений создавайте Issues в репозитории.

---

**ISKALA MOVA** - Интеллектуальная система кодирования и анализа украинского языка 