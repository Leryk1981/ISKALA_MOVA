# 🚀 Integrated Tool System - Руководство по интеграции

## 📋 Обзор

Интегрированная система инструментов объединяет две мощные компоненты:

- **APIResolverV2** - умный выбор инструментов с графовой памятью
- **UniversalToolConnector** - надежное выполнение с валидацией и безопасностью

## 🏗️ Архитектура

```
Пользователь → LLM Agent → Integrated Tool System
                                    ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                   ↓
            APIResolverV2                        UniversalToolConnector
            (Мозг выбора)                        (Исполнитель)
                    ↓                                   ↓
            - Графовая память                    - Валидация данных
            - Аналитическая оценка               - Подстановка секретов
            - Поиск релевантных API              - HTTP запросы
            - Логирование выбора                 - Обработка ответов
```

## 🔧 Установка и настройка

### 1. Структура файлов

```
src/
├── integrated_tool_system.py    # Основная интегрированная система
├── api_resolver_v2.py          # Система выбора API
├── llm_agent_v2.py             # LLM Agent с интеграцией
└── ...

tool_api/
├── connectors/
│   └── universal_connector.py   # Система выполнения API
├── tools/                       # JSON конфигурации инструментов
│   ├── todoist.create_task.json
│   ├── todoist.get_tasks.json
│   └── ...
└── catalogs/
    └── tool_api.catalog.json    # Каталог инструментов

tool_api_catalog/
└── api_catalog.json            # Каталог API для APIResolverV2
```

### 2. Конфигурация

#### Настройка путей в `integrated_tool_system.py`:

```python
tool_system = IntegratedToolSystem(
    catalog_path="./tool_api_catalog",    # Путь к каталогу API
    graph_path="./graph_memory",          # Путь к графовой памяти
    log_path="./logs",                    # Путь к логам
    tools_dir="./tool_api/tools"          # Путь к JSON конфигурациям
)
```

#### Настройка секретов в `.env`:

```env
# API ключи для инструментов
todoist_token=your_todoist_token_here
google_translate_key=your_google_key_here
openai_api_key=your_openai_key_here
```

## 🎯 Использование

### 1. Базовое использование

```python
from src.integrated_tool_system import process_intent

# Обработка намерения
result = await process_intent(
    intent_text="Перевести текст на английский",
    context={"text": "Привет, мир!", "target_language": "en"},
    user_id="user123",
    session_id="session456",
    graph_context="translation"
)

print(f"Успех: {result['success']}")
print(f"Инструмент: {result['tool_used']}")
print(f"Рейтинг: {result['tool_rating']}")
```

### 2. Использование в LLM Agent

```python
from src.llm_agent_v2 import LLMAgentV2

# Создание агента с интегрированными инструментами
agent = LLMAgentV2()

# Обработка запроса пользователя
response = await agent.process_request(
    "Создай задачу в Todoist: Подготовить отчет до завтра"
)
```

### 3. Прямое использование системы

```python
from src.integrated_tool_system import IntegratedToolSystem

# Создание системы
tool_system = IntegratedToolSystem()

# Получение доступных инструментов
tools = await tool_system.get_available_tools()
print(f"Доступно инструментов: {tools['total_connector']}")

# Получение статистики
stats = await tool_system.get_tool_statistics()
print(f"Статус: {stats['system_status']}")
```

## 📊 Мониторинг и логирование

### 1. Логи выбора инструментов

Логи сохраняются в `./logs/` и содержат:
- Выбранный инструмент
- Рейтинг выбора
- Контекст графа
- Время выполнения

### 2. Логи выполнения

Логи сохраняются в `./tool_api/logs/action_log.json`:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "tool_id": "tool_api.todoist.create_task",
  "input": {"content": "Тестовая задача"},
  "result": {"success": true, "data": {...}}
}
```

### 3. Графовая память

Сохраняется в `./graph_memory/`:
- Контекстные решения
- Рейтинги успешности
- История использования API

## 🔍 Отладка

### 1. Тестирование системы

```bash
python test_integration.py
```

### 2. Проверка конфигурации

```python
# Проверка доступных инструментов
tools = await get_available_tools()
print(f"Каталог: {tools['total_catalog']}")
print(f"Коннектор: {tools['total_connector']}")

# Проверка статистики
stats = await get_tool_statistics()
print(f"Статус: {stats['system_status']}")
```

### 3. Частые проблемы

#### Проблема: "No tool found for intent"
**Решение**: Проверьте каталог `tool_api/catalogs/tool_api.catalog.json`

#### Проблема: "Secrets file not found"
**Решение**: Создайте файл `.env` с необходимыми API ключами

#### Проблема: "Module not found"
**Решение**: Убедитесь, что пути в `sys.path.append()` корректны

## 🚀 Расширение системы

### 1. Добавление нового инструмента

#### Шаг 1: Создание JSON конфигурации

```json
// tool_api/tools/my_new_tool.json
{
  "id": "tool_api.my_new_tool",
  "description": "Описание нового инструмента",
  "intent": "my_intent",
  "method": "POST",
  "url": "https://api.example.com/endpoint",
  "headers": {
    "Authorization": "Bearer {{secrets.my_api_key}}"
  },
  "input_schema": {
    "param1": "string",
    "param2": "number?"
  },
  "output_schema": {
    "result": "string"
  }
}
```

#### Шаг 2: Добавление в каталог

```json
// tool_api/catalogs/tool_api.catalog.json
{
  "tools": [
    {
      "id": "tool_api.my_new_tool",
      "intent": "my_intent",
      "service": "my_service",
      "description": "Описание нового инструмента"
    }
  ]
}
```

#### Шаг 3: Добавление секрета

```env
# .env
my_api_key=your_api_key_here
```

### 2. Настройка APIResolverV2

Добавьте метаданные API в `tool_api_catalog/api_catalog.json`:

```json
{
  "apis": [
    {
      "name": "my_new_tool",
      "source": "My Service",
      "endpoint": "/my_endpoint",
      "functions": ["my_function"],
      "keywords": ["my", "new", "tool"],
      "rating": 0.9,
      "reliability": 0.95,
      "speed": 0.8,
      "popularity": 100,
      "license": "MIT",
      "limits": {"requests_per_minute": 60}
    }
  ]
}
```

## 📈 Производительность

### 1. Оптимизация

- **Кэширование**: Графовая память кэширует успешные решения
- **Параллелизм**: Асинхронное выполнение запросов
- **Таймауты**: Настройка таймаутов для HTTP запросов

### 2. Мониторинг

```python
# Получение статистики производительности
stats = await get_tool_statistics()
print(f"Общее количество API: {stats['api_statistics']['total_apis']}")
print(f"Контекстов в памяти: {len(stats['graph_statistics']['contexts'])}")
```

## 🔒 Безопасность

### 1. Управление секретами

- Секреты хранятся в `.env` файле
- Подстановка через `{{secrets.key}}`
- Никогда не логируются в открытом виде

### 2. Валидация входных данных

- Проверка по `input_schema`
- Типизация параметров
- Санитизация данных

### 3. Ограничения

- Таймауты на HTTP запросы
- Лимиты на количество запросов
- Валидация URL и методов

## 🎉 Заключение

Интегрированная система инструментов предоставляет:

✅ **Умный выбор** инструментов на основе опыта и анализа  
✅ **Надежное выполнение** с валидацией и безопасностью  
✅ **Графовую память** для контекстных решений  
✅ **Полное логирование** для отладки и мониторинга  
✅ **Простое расширение** новыми инструментами  

Система готова к использованию в продакшене! 🚀 