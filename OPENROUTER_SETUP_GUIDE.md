# 🔧 Налаштування OpenRouter API в Open Web UI

**Інструкція по підключенню моделей після виправлення помилок Ollama**  
*Дата: 2024-08-04*

---

## ✅ **Проблема вирішена:**

### **ДО** (помилки в консолі):
```
❌ Failed to load resource: the server responded with a status of 500 (Internal Server Error)
❌ WebUI could not connect to Ollama
❌ TipTap warn: Duplicate extension names found
```

### **ПІСЛЯ** (виправлено):
```
✅ {"version":false} - Ollama правильно відключений
✅ Немає помилок 500 в /ollama/api/version
✅ TipTap редактор працює стабільно
```

---

## 🎯 **Покрокове налаштування:**

### **Крок 1: Відкрийте Web UI**
```
http://localhost:3001
```

### **Крок 2: Перейдіть в налаштування**
- Клікніть на іконку **профілю** (правий верхній кут)
- Виберіть **Settings** (Налаштування)
- Перейдіть на вкладку **Models** (Моделі)

### **Крок 3: Видаліть Ollama моделі (якщо є)**
- Якщо бачите будь-які моделі з типом "Ollama" - видаліть їх
- Клікніть **трішник** → **Delete** для кожної Ollama моделі

### **Крок 4: Додайте OpenRouter підключення**
1. Клікніть **"+ Add Model"**
2. Заповніть поля:
   - **Model Name**: `OpenRouter API`
   - **Base URL**: `https://openrouter.ai/api/v1`
   - **API Key**: `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`
3. Клікніть **Save**

### **Крок 5: Додайте популярні моделі**

#### **Claude 3.5 Sonnet (Рекомендовано):**
- **Model ID**: `anthropic/claude-3.5-sonnet`
- **Display Name**: `Claude 3.5 Sonnet`

#### **GPT-4o:**
- **Model ID**: `openai/gpt-4o`
- **Display Name**: `GPT-4o`

#### **Llama 3.1 8B:**
- **Model ID**: `meta-llama/llama-3.1-8b-instruct`
- **Display Name**: `Llama 3.1 8B`

#### **Gemini Pro:**
- **Model ID**: `google/gemini-pro`
- **Display Name**: `Gemini Pro`

---

## 🌟 **Рекомендовані моделі для різних задач:**

### **💡 Для розробки коду:**
```
anthropic/claude-3.5-sonnet     # Найкращий для коду
openai/gpt-4o                   # Універсальний
meta-llama/codellama-34b        # Спеціалізований на коді
```

### **📝 Для тексту та аналізу:**
```
anthropic/claude-3.5-sonnet     # Найкращий для тексту
openai/gpt-4o                   # Універсальний
cohere/command-r-plus           # Добрий для аналізу
```

### **🚀 Для швидких завдань:**
```
meta-llama/llama-3.1-8b-instruct  # Швидкий і дешевий
openai/gpt-3.5-turbo             # Класичний швидкий
anthropic/claude-3-haiku         # Швидкий Claude
```

---

## 🧪 **Тестування налаштувань:**

### **1. Перевірте підключення:**
- Створіть новий чат
- Виберіть одну з доданих моделей
- Надішліть тестове повідомлення: `"Привіт! Перевір чи працює ВФС команда /vfs status"`

### **2. Протестуйте ВФС:**
Після успішного підключення моделі, тестуйте команди ВФС:
```bash
/vfs status                     # Статус системи
/vfs tree                       # Структура проектів
/project create TestProject default  # Створити тестовий проект
/vfs gui                        # Інтерактивне меню
```

---

## 🎨 **Налаштування інтерфейсу:**

### **Відключення попереджень TipTap:**
1. **Settings** → **Interface**
2. Увімкніть **"Disable Warnings"**
3. Перезавантажте сторінку (`Ctrl+F5`)

### **Оптимізація продуктивності:**
1. **Settings** → **Advanced**
2. Увімкніть **"Cache Responses"**
3. Встановіть **"Max Tokens"**: `4000` (для більшості задач)

---

## 🔧 **Виправлені налаштування в docker-compose.yml:**

```yaml
# Додано для повного відключення Ollama:
- OLLAMA_AUTO_PULL=false
- OLLAMA_AUTO_PULL_DISABLED=true
- ENABLE_OLLAMA_API=false
- OLLAMA_CONNECTION_CHECK=false
- DEFAULT_MODELS_OLLAMA=
- AUTOMATIC_MODEL_INITIALIZATION=false
- ENABLE_MODEL_FILTER=false
- AUTO_UPDATE_DISABLED=true
```

---

## ❓ **Часті питання:**

### **Q: Все ще бачу помилки Ollama?**
**A:** Очистіть кеш браузера (`Ctrl+Shift+Del`) або спробуйте в режимі інкогніто.

### **Q: Моделі не з'являються в списку?**
**A:** Перевірте:
1. Правильність API ключа
2. Інтернет з'єднання  
3. Перезавантажте сторінку

### **Q: Команди ВФС не працюють?**
**A:** 
1. Переконайтеся що модель підключена
2. Перевірте що контейнер `iskala-core` запущений: `docker ps`
3. Тестуйте команду `/vfs status`

### **Q: Повільна робота інтерфейсу?**
**A:** 
1. Виберіть швидку модель (llama-3.1-8b)
2. Зменшіть Max Tokens до 2000
3. Перезапустіть контейнер: `docker-compose restart open-webui`

---

## 🎉 **Готово!**

Тепер ваш Open Web UI:
- ✅ **Працює без помилок Ollama**
- ✅ **Підключений до OpenRouter API**
- ✅ **Має доступ до найкращих моделей**
- ✅ **Підтримує ВФС команди візуалізації**
- 🌳 **Команди `/vfs tree` та `/vfs gui` готові до використання**

**🚀 Почніть з команди `/vfs status` для перевірки ВФС!**

---

*Інструкція по налаштуванню OpenRouter API*  
*© 2024 ISKALA MOVA Project* 