# 🚀 ШВИДКИЙ СТАРТ: ISKALA API ФУНКЦІЇ В OPEN WEBUI

## ✅ Що вже готово:

- **ISKALA Core** ✅ працює (порт 8001)
- **OpenAPI Tool Server** ✅ запущений (порт 8003)
- **Open WebUI** ✅ доступний (порт 3000)

## 🔧 3 кроки для інтеграції:

### 1. Відкрийте Open WebUI
```
http://localhost:3000
```

### 2. Додайте ISKALA Tools
- **Settings** → **Tools** → **Add Tool**
- **OpenAPI Tool Server**
- **URL**: `http://localhost:8003/openapi.json`
- **Name**: `ISKALA Modules`

### 3. Почніть використовувати!

## 🎯 Доступні функції:

### ✅ Працює зараз:
- **Пошук в пам'яті** - `search_iskala_memory`
- **Виклик інструментів** - `call_iskala_tool`
- **Перевірка статусу** - `get_iskala_status`

### 📋 Доступні інструменти ISKALA:
- `file` - робота з файлами
- `command` - виконання команд
- `api` - API запити
- `memory` - робота з пам'яттю

## 🧪 Приклади:

```
"Знайди інформацію про українську мову"
"Виконай команду ls"
"Який статус модулів ISKALA?"
```

## 🔗 Корисні посилання:

- **Open WebUI**: http://localhost:3000
- **OpenAPI схема**: http://localhost:8003/openapi.json
- **Статус модулів**: http://localhost:8003/iskala/status

---

**💡 Важливо**: Модулі ISKALA - це **API функції**, а не LLM моделі. Вони доступні через **Tools** в Open WebUI. 