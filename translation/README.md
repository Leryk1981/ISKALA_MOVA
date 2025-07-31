# ISKALA Universal Translation Layer

## 🌐 Універсальний шар-перекладач для мультимовної підтримки

### Основний принцип
Кожен користувач працює у своїй мовній "бульбашці", бачачи весь простір рідною мовою, тоді як всі дані зберігаються універсально.

### Архітектура

#### 1. Структура зберігання сенсів
```json
{
  "payload": "універсальний зміст/намір",
  "original_lang": "мова оригіналу",
  "meta": "службова інформація",
  "embedding": "вектор змісту",
  "history": [
    {"lang": "ua", "text": "Оригінал"},
    {"lang": "de", "text": "Переклад"}
  ]
}
```

#### 2. Потік роботи
1. **Вхід**: Користувач створює намір рідною мовою
2. **Трансформація**: LLM перетворює на універсальний сенс
3. **Зберігання**: Зберігається універсальний зміст
4. **Вихід**: LLM перекладає на мову користувача
5. **Кешування**: Переклади зберігаються для ефективності

### API Використання

#### Створити універсальний сенс
```python
from translation.core.translator import ISKALATranslator

translator = ISKALATranslator()
sense = translator.create_universal_sense(
    original_text="Моя мова - це моя ідентичність",
    source_lang="uk",
    user_context={"user_id": "user123"}
)
```

#### Перекласти сенс
```python
translated = translator.translate_sense(
    sense=sense,
    target_lang="de",
    user_style="poetic"
)
# Результат: "Meine Sprache ist meine Identität"
```

#### Отримати мовну бульбашку
```python
bubble = translator.get_user_language_bubble(
    user_id="user123",
    preferred_lang="uk"
)
```

### Запуск API сервісу
```bash
cd /a0/instruments/custom/iskala/translation
python api/translation_api.py
```

API буде доступний на: http://localhost:8082

### Підтримувані мови
- Українська (uk)
- Англійська (en)
- Німецька (de)
- Польська (pl)
- Російська (ru)
- Французька (fr)
- Іспанська (es)

### Технології
- **LLM**: OpenAI GPT-4/3.5, Mistral, Claude, Ollama
- **Кеш**: Redis, SQLite, векторні бази
- **API**: FastAPI
- **Зберігання**: Neo4j, JSON

### Особливості
- Зберігається культурний контекст
- Адаптується стиль мовлення
- Кешує переклади для ефективності
- Підтримує професійний сленг
- Зберігає авторський стиль
