# 🌺 ПРАВИЛЬНА ІНТЕГРАЦІЯ МОДУЛІВ ISKALA В OPEN WEBUI

## ✅ Розуміння архітектури

**Модулі ISKALA** - це **НЕ LLM моделі**, а **окремі функціональні сервіси**, доступні через API:

- **ISKALA Core** (порт 8001) - основна логіка та пам'ять ✅ **ПРАЦЮЄ**
- **Vault** (порт 8081) - безпечне зберігання ❌ Не запущений
- **Translation** (порт 8082) - система перекладу ❌ Не запущений  
- **RAG** (порт 8002) - пошук по документах ❌ Не запущений

## 🚀 Поточний статус

### ✅ Що працює:
- **ISKALA Core** - повністю функціональний
- **OpenAPI Tool Server** - запущений на порту 8003
- **Open WebUI** - доступний на порту 3000

### ❌ Що не працює:
- **Vault** - не запущений
- **Translation** - не запущений
- **RAG** - не запущений

## 🔧 Інтеграція в Open WebUI

### Крок 1: Відкрийте Open WebUI
```
http://localhost:3000
```

### Крок 2: Перейдіть в налаштування інструментів
1. **Settings** → **Tools**
2. Натисніть **"Add Tool"**
3. Виберіть **"OpenAPI Tool Server"**

### Крок 3: Налаштуйте підключення
- **Name**: `ISKALA Modules`
- **URL**: `http://localhost:8003/openapi.json`
- **Description**: `Модулі ISKALA для роботи з пам'яттю та інструментами`

### Крок 4: Збережіть налаштування

## 📋 Доступні функції (зараз працюють)

### 1. **Пошук в пам'яті ISKALA** ✅
- **Функція**: `search_iskala_memory`
- **Параметри**: 
  - `query` (string) - пошуковий запит
  - `limit` (integer, опціонально) - кількість результатів

### 2. **Виклик інструментів ISKALA** ✅
- **Функція**: `call_iskala_tool`
- **Параметри**:
  - `tool_name` (string) - назва інструменту
  - `parameters` (object) - параметри виклику

### 3. **Статус модулів** ✅
- **Функція**: `get_iskala_status`
- **Параметри**: немає

## 🧪 Приклади використання

### Приклад 1: Пошук в пам'яті
```
Користувач: "Знайди інформацію про українську мову"
AI: Використаю функцію пошуку в пам'яті ISKALA
```

### Приклад 2: Виклик інструменту
```
Користувач: "Виконай команду ls"
AI: Використаю функцію виклику інструментів ISKALA
```

### Приклад 3: Перевірка статусу
```
Користувач: "Який статус модулів ISKALA?"
AI: Використаю функцію перевірки статусу
```

## 🔍 Перевірка статусу

### Перевірте статус всіх модулів:

```bash
curl http://localhost:8003/iskala/status
```

Поточний результат:
```json
{
  "iskala_core": {
    "status": "healthy",
    "response": {
      "status": "healthy",
      "llm_agent": "active",
      "available_tools": ["file", "command", "api", "memory"]
    }
  },
  "vault": {"status": "error"},
  "translation": {"status": "error"},
  "rag": {"status": "error"}
}
```

## 🛠️ Діагностика

### Якщо функції не працюють:

1. **Перевірте статус OpenAPI сервера**:
   ```bash
   curl http://localhost:8003/
   ```

2. **Перевірте статус модулів ISKALA**:
   ```bash
   curl http://localhost:8003/iskala/status
   ```

3. **Перевірте налаштування в Open WebUI**:
   - Settings → Tools → ISKALA Modules
   - Переконайтеся що URL правильний: `http://localhost:8003/openapi.json`

## 📝 Важливі зауваження

1. **Модулі ISKALA** - це **API функції**, а не LLM моделі
2. **OpenAPI Tool Server** працює як **проксі** між Open WebUI та модулями ISKALA
3. **Зараз працює тільки ISKALA Core** - основна логіка та пам'ять
4. **Функції** доступні через **Tools** в Open WebUI, а не через вибір моделі
5. **Доступні інструменти ISKALA Core**: file, command, api, memory

## 🚀 Швидкий старт

1. ✅ OpenAPI сервер вже запущений: `http://localhost:8003/openapi.json`
2. ✅ Open WebUI доступний: `http://localhost:3000`
3. 🔧 Додайте OpenAPI Tool Server: Settings → Tools → Add Tool
4. 🔧 URL: `http://localhost:8003/openapi.json`
5. 🎯 Почніть використовувати функції ISKALA в чаті!

## 🔗 Корисні посилання

- **OpenAPI схема**: `http://localhost:8003/openapi.json`
- **Статус модулів**: `http://localhost:8003/iskala/status`
- **ISKALA Core**: `http://localhost:8001/health`
- **Open WebUI**: `http://localhost:3000`

## 🎯 Що можна робити зараз

### ✅ Працює:
- Пошук в пам'яті ISKALA
- Виклик інструментів (file, command, api, memory)
- Перевірка статусу модулів

### ❌ Не працює (потребує запуску додаткових сервісів):
- Переклад тексту (Translation модуль)
- RAG пошук (RAG модуль)
- Безпечне зберігання (Vault модуль)

## 🔧 Для запуску додаткових модулів

Якщо потрібні додаткові функції, запустіть відповідні сервіси:

```bash
# Vault (безпечне зберігання)
cd vault && python main.py

# Translation (переклад)
cd translation && python main.py

# RAG (пошук по документах)
cd rag_system && python main.py
```

Але **основна функціональність ISKALA вже доступна** через ISKALA Core! 