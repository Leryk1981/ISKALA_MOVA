# 🌺 ПРАВИЛЬНА ІНТЕГРАЦІЯ МОДУЛІВ ISKALA В OPEN WEBUI

## ✅ Розуміння архітектури

**Модулі ISKALA** - це **НЕ LLM моделі**, а **окремі функціональні сервіси**, доступні через API:

- **ISKALA Core** (порт 8001) - основна логіка та пам'ять
- **Vault** (порт 8081) - безпечне зберігання
- **Translation** (порт 8082) - система перекладу  
- **RAG** (порт 8002) - пошук по документах

## 🚀 Запуск OpenAPI Tool Server

### 1. Запустіть ISKALA OpenAPI Tool Server:

```bash
python iskala_openapi_server.py
```

Сервер запуститься на порту **8003** і надасть OpenAPI схему.

### 2. Перевірте доступність:

```bash
curl http://localhost:8003/openapi.json
```

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
- **Description**: `Модулі ISKALA для роботи з пам'яттю, перекладом та RAG`

### Крок 4: Збережіть налаштування

## 📋 Доступні функції ISKALA

### 1. **Пошук в пам'яті ISKALA**
- **Функція**: `search_iskala_memory`
- **Параметри**: 
  - `query` (string) - пошуковий запит
  - `limit` (integer, опціонально) - кількість результатів

### 2. **Виклик інструментів ISKALA**
- **Функція**: `call_iskala_tool`
- **Параметри**:
  - `tool_name` (string) - назва інструменту
  - `parameters` (object) - параметри виклику

### 3. **Переклад тексту**
- **Функція**: `translate_text`
- **Параметри**:
  - `text` (string) - текст для перекладу
  - `source_lang` (string, опціонально) - мова джерела
  - `target_lang` (string, опціонально) - мова призначення

### 4. **RAG пошук**
- **Функція**: `rag_search`
- **Параметри**:
  - `query` (string) - пошуковий запит
  - `context` (string, опціонально) - додатковий контекст

### 5. **Статус модулів**
- **Функція**: `get_iskala_status`
- **Параметри**: немає

## 🧪 Приклади використання

### Приклад 1: Пошук в пам'яті
```
Користувач: "Знайди інформацію про українську мову"
AI: Використаю функцію пошуку в пам'яті ISKALA
```

### Приклад 2: Переклад тексту
```
Користувач: "Переклади 'Hello world' на українську"
AI: Використаю функцію перекладу ISKALA
```

### Приклад 3: RAG пошук
```
Користувач: "Знайди документи про ISKALA"
AI: Використаю RAG пошук для пошуку в документах
```

## 🔍 Перевірка статусу

### Перевірте статус всіх модулів:

```bash
curl http://localhost:8003/iskala/status
```

Очікуваний результат:
```json
{
  "iskala_core": {"status": "healthy"},
  "vault": {"status": "healthy"},
  "translation": {"status": "healthy"},
  "rag": {"status": "healthy"}
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

3. **Перевірте логи OpenAPI сервера**:
   ```bash
   # В терміналі де запущений сервер
   ```

4. **Перевірте налаштування в Open WebUI**:
   - Settings → Tools → ISKALA Modules
   - Переконайтеся що URL правильний
   - Перевірте що сервер активний

## 📝 Важливі зауваження

1. **Модулі ISKALA** - це **API функції**, а не LLM моделі
2. **OpenAPI Tool Server** працює як **проксі** між Open WebUI та модулями ISKALA
3. **Всі модулі** повинні бути запущені для повної функціональності
4. **Функції** доступні через **Tools** в Open WebUI, а не через вибір моделі

## 🚀 Швидкий старт

1. Запустіть OpenAPI сервер: `python iskala_openapi_server.py`
2. Відкрийте Open WebUI: `http://localhost:3000`
3. Додайте OpenAPI Tool Server: Settings → Tools → Add Tool
4. URL: `http://localhost:8003/openapi.json`
5. Почніть використовувати функції ISKALA в чаті!

## 🔗 Корисні посилання

- **OpenAPI схема**: `http://localhost:8003/openapi.json`
- **Статус модулів**: `http://localhost:8003/iskala/status`
- **ISKALA Core**: `http://localhost:8001/health`
- **Open WebUI**: `http://localhost:3000` 