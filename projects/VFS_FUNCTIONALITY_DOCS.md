# 📚 Документация по функционалу ВФС

**Виртуальная файловая система для Open Web UI**  
*Версия: 1.0.0 | Обновлено: 2024-08-03*

---

## 🎯 Обзор системы

Виртуальная файловая система (ВФС) - это интегрированное решение для управления проектами и кодом прямо в интерфейсе Open Web UI. Система позволяет создавать, редактировать и организовывать файлы проектов без выхода из чата.

### ✨ Ключевые возможности:
- 🗂️ **Управление проектами** - создание, переключение, удаление
- 📄 **Операции с файлами** - создание, чтение, редактирование, удаление
- 🎨 **Шаблоны проектов** - готовые структуры для типовых задач
- 💾 **Экспорт/импорт** - резервное копирование и перенос проектов
- 📊 **Аналитика** - статистика использования и диагностика

---

## 🛠️ Команды управления проектами

### `/project create <имя> [шаблон]`
**Создание нового проекта**

```bash
# Создать проект с базовым шаблоном
/project create MyFirstProject default

# Создать парсер Instagram
/project create InstagramBot instagram_parser

# Создать API клиент
/project create MyAPI api_client
```

**Результат:**
```
✅ Проект "InstagramBot" создан
📦 Шаблон: instagram_parser
📄 Файлов создано: 4
🎯 Статус: Активный проект
```

### `/project list`
**Просмотр всех проектов**

```bash
/project list
```

**Результат:**
```
📋 Список проектов:
🟢 InstagramBot (instagram_parser) - 4 файла - Активный
⚪ MyAPI (api_client) - 2 файла
⚪ TestProject (default) - 3 файла

Всего проектов: 3
```

### `/project switch <имя>`
**Переключение между проектами**

```bash
/project switch MyAPI
```

**Результат:**
```
🔄 Переключились на проект "MyAPI"
📁 Тип: api_client
📄 Файлов: 2
```

### `/project info [имя]`
**Подробная информация о проекте**

```bash
/project info InstagramBot
```

**Результат:**
```
📂 Проект: InstagramBot
├── 📦 Шаблон: instagram_parser
├── 📅 Создан: 2024-08-03 15:30:00
├── 📝 Изменен: 2024-08-03 16:45:00
├── 📄 Файлов: 4
├── 💾 Размер: 8.5 КБ
└── 🎯 Статус: Активный
```

### `/project delete <имя>`
**Удаление проекта**

```bash
/project delete TestProject
```

**Результат:**
```
🗑️ Проект "TestProject" удален
📊 Оставшихся проектов: 2
```

---

## 📄 Команды работы с файлами

### `/file create <проект> <путь> [содержимое]`
**Создание нового файла**

```bash
# Создать простой файл
/file create InstagramBot utils.py "# Утилиты для парсера"

# Создать файл с кодом
/file create InstagramBot auth.py """
import requests

class InstagramAuth:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
    
    def login(self):
        # Логика авторизации
        pass
"""
```

### `/file read <проект> <путь>`
**Чтение содержимого файла**

```bash
/file read InstagramBot instagram_parser.py
```

**Результат:**
```
📖 Содержимое файла: instagram_parser.py

import requests
from bs4 import BeautifulSoup

class InstagramParser:
    def __init__(self):
        self.session = requests.Session()
    
    def parse_profile(self, username):
        # Код парсера...
        return data

📊 Размер: 1.2 КБ | Строк: 45
```

### `/file update <проект> <путь> <новое_содержимое>`
**Обновление файла**

```bash
/file update InstagramBot config.json '{"target": "new_account", "limit": 100}'
```

**Результат:**
```
✏️ Файл "config.json" обновлен
📊 Было: 85 байт → Стало: 95 байт (+10)
```

### `/file list <проект>`
**Список файлов проекта**

```bash
/file list InstagramBot
```

**Результат:**
```
📁 Проект: InstagramBot
├── 📄 instagram_parser.py (1.2 КБ) - Python
├── 📄 config.json (95 байт) - JSON
├── 📄 requirements.txt (128 байт) - Text
├── 📄 utils.py (256 байт) - Python
└── 📄 auth.py (512 байт) - Python

📊 Всего: 5 файлов | 2.2 КБ
```

### `/file delete <проект> <путь>`
**Удаление файла**

```bash
/file delete InstagramBot temp.py
```

**Результат:**
```
🗑️ Файл "temp.py" удален из проекта "InstagramBot"
```

---

## 🎨 Работа с шаблонами

### `/template list`
**Список доступных шаблонов**

```bash
/template list
```

**Результат:**
```
🎨 Доступные шаблоны:

📦 default
   Базовый Python проект
   📄 Файлов: 3 (main.py, requirements.txt, README.md)

📦 instagram_parser  
   Парсер для Instagram
   📄 Файлов: 4 (parser.py, config.json, utils.py, requirements.txt)

📦 api_client
   Универсальный REST API клиент
   📄 Файлов: 2 (client.py, requirements.txt)
```

### `/template info <имя>`
**Подробности шаблона**

```bash
/template info instagram_parser
```

**Результат:**
```
🎨 Шаблон: instagram_parser

📋 Описание: Готовый шаблон для парсинга Instagram
🔧 Тип: Python проект
📄 Содержимое:
  ├── instagram_parser.py - Основной класс парсера
  ├── config.json - Конфигурация парсинга
  ├── utils.py - Вспомогательные функции
  └── requirements.txt - Зависимости

📦 Зависимости: requests, beautifulsoup4, lxml, selenium
```

---

## 🔄 Экспорт и импорт

### `/export <проект> [формат]`
**Экспорт проекта**

```bash
# Экспорт в JSON (рекомендуется)
/export InstagramBot json

# Экспорт в ZIP (если поддерживается)
/export InstagramBot zip
```

**Результат:**
```
📦 Экспорт проекта "InstagramBot"
┌─────────────────────────────────────┐
│ Формат: JSON                        │
│ Размер: 8.5 КБ                      │
│ Файлов: 5                           │
│ Экспортировано: 2024-08-03 16:45    │
└─────────────────────────────────────┘

[JSON данные проекта...]
```

### `/import <данные> [формат]`
**Импорт проекта**

```bash
/import '{"name":"ImportedProject","files":{"main.py":"print(\"Hello!\")"}}'
```

**Результат:**
```
📥 Проект "ImportedProject" импортирован
📄 Файлов импортировано: 1
✅ Готов к использованию
```

---

## 📊 Системные команды

### `/vfs status`
**Статус виртуальной файловой системы**

**Результат:**
```
🔧 Статус ВФС v1.0.0
┌─────────────────────────────────────┐
│ ✅ Система активна                  │
│ 🔌 Плагин: openwebui_vfs_plugin     │
│ 💾 Storage: localStorage            │
│ 📊 Проектов: 3                     │
│ 📄 Файлов: 12                      │
│ 🎯 Активный: InstagramBot          │
└─────────────────────────────────────┘
```

### `/vfs stats`
**Подробная статистика**

**Результат:**
```
📊 Статистика ВФС
┌─────────────────────────────────────┐
│ Проекты:                            │
│ ├── InstagramBot: 5 файлов (2.2 КБ) │
│ ├── MyAPI: 2 файла (1.1 КБ)         │
│ └── TestDocs: 3 файла (0.8 КБ)      │
│                                     │
│ Общее:                              │
│ ├── Всего проектов: 3               │
│ ├── Всего файлов: 10                │
│ ├── Общий размер: 4.1 КБ            │
│ └── Использовано хранилища: 0.04%   │
│                                     │
│ Активность:                         │
│ ├── Создано сегодня: 3 проекта      │
│ ├── Изменено сегодня: 5 файлов      │
│ └── Последняя активность: 2 мин назад│
└─────────────────────────────────────┘
```

### `/vfs help`
**Справка по командам**

**Результат:**
```
🆘 Справка по ВФС

📂 Проекты:
  /project create <имя> [шаблон] - создать проект
  /project list                  - список проектов
  /project switch <имя>          - переключить проект
  /project info [имя]            - информация о проекте
  /project delete <имя>          - удалить проект

📄 Файлы:
  /file create <проект> <путь> [контент] - создать файл
  /file read <проект> <путь>             - прочитать файл
  /file update <проект> <путь> <контент> - обновить файл
  /file list <проект>                    - список файлов
  /file delete <проект> <путь>           - удалить файл

🎨 Шаблоны:
  /template list       - список шаблонов
  /template info <имя> - информация о шаблоне

🔄 Экспорт:
  /export <проект> [формат] - экспорт проекта
  /import <данные>          - импорт проекта

🔧 Система:
  /vfs status    - статус системы
  /vfs stats     - подробная статистика  
  /vfs help      - эта справка
```

---

## 💡 Примеры типовых сценариев

### 🎨 Создание парсера Instagram
```bash
# 1. Создание проекта
/project create InstagramBot instagram_parser

# 2. Настройка конфигурации
/file update InstagramBot config.json '{
  "target_account": "example_user",
  "collect_posts": true,
  "collect_stories": false,
  "limit": 50
}'

# 3. Добавление дополнительного модуля
/file create InstagramBot database.py """
import sqlite3

class InstagramDB:
    def __init__(self, db_path='instagram.db'):
        self.connection = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            username TEXT,
            caption TEXT,
            likes INTEGER,
            created_at TIMESTAMP
        )
        ''')
        self.connection.commit()
"""

# 4. Проверка результата
/file list InstagramBot
```

### 🔧 Создание API клиента
```bash
# 1. Создание проекта
/project create WeatherAPI api_client

# 2. Кастомизация клиента
/file update WeatherAPI client.py """
import requests
from typing import Dict, Optional

class WeatherAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.openweathermap.org/data/2.5'
        
    def get_weather(self, city: str) -> Dict:
        url = f'{self.base_url}/weather'
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        return response.json()
        
    def get_forecast(self, city: str, days: int = 5) -> Dict:
        url = f'{self.base_url}/forecast'
        params = {
            'q': city,
            'appid': self.api_key,
            'cnt': days * 8,  # 8 прогнозов в день (каждые 3 часа)
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        return response.json()

# Пример использования
if __name__ == '__main__':
    client = WeatherAPIClient('YOUR_API_KEY')
    weather = client.get_weather('London')
    print(f"Температура в Лондоне: {weather['main']['temp']}°C")
"""

# 3. Добавление примера использования
/file create WeatherAPI example.py """
from client import WeatherAPIClient

# Инициализация клиента
api = WeatherAPIClient('your-api-key-here')

# Получение текущей погоды
cities = ['London', 'Paris', 'Tokyo', 'New York']

for city in cities:
    try:
        weather = api.get_weather(city)
        temp = weather['main']['temp']
        description = weather['weather'][0]['description']
        print(f'{city}: {temp}°C, {description}')
    except Exception as e:
        print(f'Ошибка для {city}: {e}')
"""
```

### 📚 Создание документации проекта
```bash
# 1. Создание проекта документации
/project create ProjectDocs default

# 2. Основная документация
/file update ProjectDocs README.md """
# Документация проекта

## Обзор
Этот проект содержит...

## Установка
```bash
pip install -r requirements.txt
```

## Использование
```python
from main import MainClass
app = MainClass()
app.run()
```

## API
- `MainClass.run()` - запуск приложения
- `MainClass.stop()` - остановка

## Примеры
См. файл examples.py
"""

# 3. Добавление changelog
/file create ProjectDocs CHANGELOG.md """
# Changelog

## [1.0.0] - 2024-08-03
### Добавлено
- Основная функциональность
- Документация
- Примеры использования

### Изменено
- Улучшена производительность

### Исправлено
- Баг с загрузкой конфигурации
"""

# 4. Экспорт документации
/export ProjectDocs json
```

---

## ⚠️ Важные ограничения

### 💾 Хранение данных
- **Местоположение**: localStorage браузера
- **Лимит размера**: ~5-10 МБ на домен
- **Сохранность**: между сессиями браузера ✅, при очистке кэша ❌

### 📄 Файлы
- **Поддерживаемые типы**: только текстовые файлы
- **Максимальный размер файла**: зависит от настроек (по умолчанию 10 МБ)
- **Кодировка**: UTF-8

### 🔧 Функциональность
- **Прямое выполнение кода**: не поддерживается
- **Работа с бинарными файлами**: не поддерживается
- **Интеграция с Git**: не реализована
- **Совместная работа**: не поддерживается (только локальное использование)

---

## 🎯 Рекомендации по использованию

### ✅ Лучшие практики
1. **Регулярно экспортируйте проекты** - используйте `/export` для резервного копирования
2. **Используйте осмысленные имена** - для проектов и файлов
3. **Структурируйте код** - разбивайте большие файлы на модули
4. **Документируйте проекты** - добавляйте README.md и комментарии
5. **Следите за размером** - не превышайте лимиты хранилища

### 🚫 Чего избегать
1. **Не храните пароли** в открытом виде в файлах
2. **Не создавайте слишком много файлов** в одном проекте
3. **Не полагайтесь только на ВФС** - делайте локальные копии важных проектов
4. **Не используйте для больших данных** - ограничения localStorage

---

*Документация по функционалу ВФС v1.0.0*  
*© 2024 Open Web UI VFS Project* 