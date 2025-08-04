# 🚀 Посібник налаштування OpenRouter API в Open Web UI

## 📋 Передумови
- ✅ Діюча реєстрація на [OpenRouter.ai](https://openrouter.ai)
- ✅ API ключ з кредитами
- ✅ Запущений Open Web UI контейнер

## 🔑 Крок 1: Отримання API ключа

1. Зайдіть на [OpenRouter.ai](https://openrouter.ai)
2. Увійдіть в акаунт
3. Перейдіть в розділ **"API Keys"**
4. Створіть новий ключ або скопіюйте існуючий
5. Переконайтеся що на акаунті є кредити: [Credits](https://openrouter.ai/credits)

## ⚙️ Крок 2: Налаштування в Open Web UI

### Метод 1: Через веб-інтерфейс (Рекомендовано)

1. Відкрийте Open Web UI: http://localhost:3001
2. Увійдіть в систему
3. Натисніть на іконку **👤 профіля** (правий верхній кут)
4. Виберіть **⚙️ Settings**
5. Перейдіть в розділ **🔗 Connections**
6. В секції **OpenAI API** заповніть:
   - **API Base URL**: `https://openrouter.ai/api/v1`
   - **API Key**: ваш OpenRouter ключ (починається з `sk-or-v1-...`)
7. Натисніть **💾 Save**

### Метод 2: Через Docker Compose (Альтернативний)

Якщо метод 1 не працює, можна прописати в `docker-compose.yml`:

```yaml
services:
  open-webui:
    environment:
      - OPENAI_API_BASE_URL=https://openrouter.ai/api/v1
      - OPENAI_API_KEY=ваш_ключ_тут
```

## 🤖 Крок 3: Додавання моделей

1. В Open Web UI перейдіть в **⚙️ Settings → 🤖 Models**
2. Натисніть **➕ Add Models**
3. Додайте популярні OpenRouter моделі:

### 🎯 Рекомендовані моделі для початку:

```
openai/gpt-4o-mini
openai/gpt-4o
openai/gpt-3.5-turbo
anthropic/claude-3-haiku
anthropic/claude-3-sonnet
meta-llama/llama-3-8b-instruct
```

### 📝 Як додати модель:
1. Скопіюйте назву моделі з OpenRouter (наприклад: `openai/gpt-4o-mini`)
2. Вставте в поле **Model Name**
3. Натисніть **✅ Add Model**

## ✅ Крок 4: Тестування

1. Створіть новий чат
2. Виберіть додану модель зі списку
3. Відправте тестове повідомлення: "Привіт, ти працюєш?"
4. Модель повинна відповісти

## 🔧 Troubleshooting (Вирішення проблем)

### ❌ Помилка: "400 Bad Request" або "Model not found"

**Причина**: Система намагається використати неіснуючу модель (наприклад: `z-ai/glm-4.5`)

**Рішення**:
1. Перейдіть в **⚙️ Settings → 🤖 Models**
2. **Видаліть** некоректні моделі (наприклад: `z-ai/glm-4.5`)
3. Додайте **тільки перевірені** моделі з OpenRouter:
   - `openai/gpt-4o-mini`
   - `openai/gpt-3.5-turbo`
   - `anthropic/claude-3-haiku`
4. Перезапустіть контейнер:
   ```bash
   docker-compose restart open-webui
   ```

### ❌ Помилка: "401 Unauthorized"

**Причина**: Неправильний API ключ або закінчилися кредити

**Рішення**:
1. Перевірте API ключ на [OpenRouter.ai](https://openrouter.ai/keys)
2. Перевірте баланс: [Credits](https://openrouter.ai/credits)
3. При необхідності створіть новий ключ
4. Оновіть ключ в **⚙️ Settings → 🔗 Connections**

### ❌ Помилка: "Failed to fetch models"

**Причина**: Проблеми з підключенням до OpenRouter

**Рішення**:
1. Перевірте інтернет з'єднання
2. Перевірте що API Base URL: `https://openrouter.ai/api/v1`
3. Перезапустіть контейнер
4. Спробуйте через кілька хвилин

### 🔄 Скидання налаштувань

Якщо нічого не допомагає:

```bash
# Повна переустановка
docker-compose down
docker volume rm iskala-mova_open-webui-data
docker-compose up -d
```

## 📚 Корисні посилання

- [OpenRouter Models](https://openrouter.ai/models) - повний список доступних моделей
- [OpenRouter Pricing](https://openrouter.ai/models) - ціни на моделі
- [OpenRouter Credits](https://openrouter.ai/credits) - поповнення балансу
- [OpenRouter API Docs](https://openrouter.ai/docs) - документація API

## 🎯 Швидке налаштування (TL;DR)

1. **API Key**: Візьміть з [OpenRouter.ai/keys](https://openrouter.ai/keys)
2. **Settings**: `http://localhost:3001` → ⚙️ → 🔗 Connections
3. **API Base**: `https://openrouter.ai/api/v1`
4. **Models**: Додайте `openai/gpt-4o-mini` та `openai/gpt-3.5-turbo`
5. **Test**: Створіть чат і протестуйте

---

💡 **Порада**: Завжди використовуйте моделі з офіційного списку OpenRouter, а не кастомні назви типу `z-ai/glm-4.5` 