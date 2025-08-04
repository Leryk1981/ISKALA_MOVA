# 🌳 Примеры визуализации дерева ВФС

**Коллекция примеров вывода команд древовидной структуры**  
*Версия: 1.1.0 | Создано: 2024-08-03*

---

## 🎯 Команда `/vfs tree` - Все проекты

### Базовый вывод:
```
🌳 Virtual File System Tree
├── 📂 InstagramParser (instagram_parser) - 4 файла | 5.4 KB
│   ├── 🐍 instagram_parser.py (3.2 KB) ⭐ Основной файл
│   ├── ⚙️ config.json (189 B) 🔧 Конфигурация
│   ├── 🔧 utils.py (1.8 KB) 🛠️ Утилиты
│   └── 📦 requirements.txt (87 B) 📋 Зависимости
├── 📂 VFS_Docs (default) - 3 файла | 7.9 KB
│   ├── 📖 README.md (3.8 KB) 📚 Документация
│   ├── 📜 COMMANDS.md (2.9 KB) ⚡ Справочник
│   └── 💡 EXAMPLES.md (1.2 KB) 🎯 Примеры
├── 📂 WeatherAPI (api_client) - 2 файла | 2.1 KB
│   ├── 🌐 client.py (1.8 KB) 🔌 API клиент
│   └── 📦 requirements.txt (87 B) 📋 Зависимости
└── 📂 DataAnalysis (default) - 5 файлов | 12.3 KB
    ├── 🐍 analyzer.py (4.5 KB) 📊 Главный анализатор
    ├── 📊 data.csv (3.2 KB) 📈 Данные
    ├── 📋 config.yaml (245 B) ⚙️ Настройки
    ├── 📈 charts.py (2.8 KB) 📊 Графики
    └── 📝 report.md (1.5 KB) 📄 Отчет

📊 Итого: 4 проекта | 14 файлов | 27.7 KB
```

---

## 📁 Команда `/vfs tree [проект]` - Конкретный проект

### Пример: Instagram Parser
```bash
/vfs tree InstagramParser
```

```
📁 Проект: InstagramParser (instagram_parser)
├── 🐍 instagram_parser.py (3.2 KB)
├── ⚙️ config.json (189 B)
├── 🔧 utils.py (1.8 KB)
└── 📦 requirements.txt (87 B)

💾 Размер проекта: 5.4 KB | Файлов: 4 | Создан: 2024-08-03
```

### Пример: Веб-приложение
```bash
/vfs tree WebApp
```

```
📁 Проект: WebApp (default)
├── 🌐 app.py (5.2 KB)
├── 🎨 templates/
│   ├── 🌐 index.html (2.1 KB)
│   ├── 🌐 login.html (1.8 KB)
│   └── 🌐 dashboard.html (3.4 KB)
├── 🎨 static/
│   ├── 🎨 style.css (2.8 KB)
│   ├── 🟨 script.js (1.9 KB)
│   └── 🖼️ logo.png (15.2 KB)
├── ⚙️ config.py (845 B)
├── 📦 requirements.txt (156 B)
└── 🗃️ database.sql (3.1 KB)

💾 Размер проекта: 36.6 KB | Файлов: 9 | Создан: 2024-08-01
```

---

## 🔍 Команда `/vfs tree [проект] --detail` - Детальная информация

### Подробный анализ проекта:
```bash
/vfs tree InstagramParser --detail
```

```
📁 Проект: InstagramParser (instagram_parser)
├── 🐍 instagram_parser.py (3.2 KB) - Изменен: 2024-08-03 15:30
│   ├── 📋 Описание: Основной парсер Instagram профилей
│   ├── 📊 Функции: parse_profile(), get_posts(), extract_data()
│   ├── 🔗 Импорты: requests, beautifulsoup4, json
│   ├── 📝 Строк кода: 127
│   └── 🎯 Статус: ✅ Готов к использованию
├── ⚙️ config.json (189 B) - Изменен: 2024-08-03 14:45
│   ├── 🎯 Цель: visitkorea_pl
│   ├── 📅 Период: 30 дней
│   ├── 📊 Лимит: 100 постов
│   ├── ⚙️ Параметров: 8
│   └── ✅ Статус: 🟢 Валидный JSON
├── 🔧 utils.py (1.8 KB) - Изменен: 2024-08-03 16:20
│   ├── 🛠️ Функции: format_data(), save_to_csv(), export_sheets()
│   ├── 📦 Зависимости: pandas, gspread
│   ├── 📝 Строк кода: 68
│   └── 🎯 Назначение: Обработка и экспорт данных
└── 📦 requirements.txt (87 B) - Изменен: 2024-08-03 13:15
    ├── 📦 requests>=2.28.0
    ├── 📦 beautifulsoup4>=4.11.0
    ├── 📦 pandas>=1.5.0
    ├── 🔢 Зависимостей: 3
    └── ✅ Статус: 🟢 Актуальные версии

💾 Размер проекта: 5.4 KB | Файлов: 4 | Создан: 2024-08-03
🚀 Готовность: 95% | Тестирование: ⚠️ Требуется | Документация: ✅ Есть
```

---

## 🎨 Команда `/vfs tree --icons` - Расширенные иконки

### Полная коллекция иконок файлов:
```
🌳 Расширенная визуализация файлов:

📁 Frontend проект:
├── 🌐 index.html (2.1 KB) 🏠 Главная страница
├── 🎨 styles.css (3.4 KB) 🎭 Стили
├── 🟨 app.js (5.2 KB) ⚡ JavaScript
├── 🟦 script.ts (4.1 KB) 📘 TypeScript
├── ⚛️ component.jsx (2.8 KB) ⚛️ React компонент
└── 🖼️ logo.svg (1.2 KB) 🎨 Векторная графика

📁 Backend проект:
├── 🐍 main.py (4.5 KB) 🚀 Python приложение
├── 🟨 server.js (3.8 KB) 🌐 Node.js сервер
├── ♨️ App.java (6.2 KB) ☕ Java приложение
├── 🔷 Program.cs (3.1 KB) 🔹 C# код
├── 🦀 main.rs (2.9 KB) 🦀 Rust приложение
└── 🐹 main.go (2.2 KB) 🐹 Go приложение

📁 Конфигурация:
├── ⚙️ config.json (456 B) 🔧 JSON конфигурация
├── 📄 config.yaml (612 B) 📋 YAML настройки
├── 🔧 .env (234 B) 🌍 Переменные среды
├── 📦 package.json (892 B) 📦 Node.js пакет
├── 🐍 requirements.txt (145 B) 📋 Python зависимости
└── 🔒 .gitignore (98 B) 🚫 Git исключения

📁 Данные:
├── 📊 data.csv (15.2 KB) 📈 CSV данные
├── 📈 sales.xlsx (45.8 KB) 📊 Excel таблица
├── 🗃️ database.sql (8.9 KB) 🛢️ SQL база
├── 📋 report.xml (3.4 KB) 📄 XML отчет
└── 🔗 api.json (2.1 KB) 🌐 API схема

📁 Документация:
├── 📝 README.md (4.2 KB) 📚 Основная документация
├── 📖 GUIDE.md (8.7 KB) 🎯 Руководство
├── 📋 CHANGELOG.md (2.3 KB) 📅 История изменений
├── 📄 LICENSE (1.1 KB) ⚖️ Лицензия
└── 💡 EXAMPLES.md (3.6 KB) 🎨 Примеры

📁 Медиа:
├── 🖼️ image.png (234 KB) 🎨 PNG изображение
├── 📷 photo.jpg (156 KB) 📸 JPEG фото
├── 🎵 audio.mp3 (3.2 MB) 🎶 MP3 аудио
├── 🎬 video.mp4 (15.8 MB) 📹 MP4 видео
└── 📁 archive.zip (892 KB) 🗜️ ZIP архив
```

---

## 📊 Команда `/vfs tree --stats` - Статистическая информация

### Детальная статистика проектов:
```
🌳 VFS Tree с расширенной статистикой:

📊 СТАТИСТИКА ПО ТИПАМ ФАЙЛОВ:
┌─────────────────┬─────────┬─────────┬──────────┐
│ Тип файла       │ Кол-во  │ Размер  │ Процент  │
├─────────────────┼─────────┼─────────┼──────────┤
│ 🐍 Python       │    8    │ 24.1 KB │   45.2%  │
│ 📝 Markdown     │    6    │ 12.8 KB │   24.0%  │
│ ⚙️ JSON         │    4    │  8.9 KB │   16.7%  │
│ 🌐 HTML         │    3    │  4.2 KB │    7.9%  │
│ 🟨 JavaScript   │    2    │  2.1 KB │    3.9%  │
│ 📦 Requirements │    3    │  1.2 KB │    2.3%  │
└─────────────────┴─────────┴─────────┴──────────┘

📊 СТАТИСТИКА ПО ПРОЕКТАМ:
┌──────────────────┬─────────┬─────────┬───────────┬─────────┐
│ Проект           │ Файлов  │ Размер  │ Создан    │ Статус  │
├──────────────────┼─────────┼─────────┼───────────┼─────────┤
│ InstagramParser  │    4    │  5.4 KB │ 03.08.24  │ ✅ Готов │
│ VFS_Docs         │    6    │ 12.8 KB │ 02.08.24  │ 📝 Редак │
│ WeatherAPI       │    2    │  2.1 KB │ 01.08.24  │ 🔄 Разр  │
│ DataAnalysis     │    5    │ 12.3 KB │ 31.07.24  │ ⚠️ Тест  │
└──────────────────┴─────────┴─────────┴───────────┴─────────┘

📊 ОБЩАЯ СТАТИСТИКА:
├── 📂 Проектов: 4
├── 📄 Файлов: 17
├── 💾 Общий размер: 32.6 KB
├── 📅 Активность: 3 проекта за неделю
├── 🎯 Завершено: 1 проект (25%)
├── 🔄 В разработке: 2 проекта (50%)
├── 📝 Документируется: 1 проект (25%)
└── ⚡ Средний размер проекта: 8.2 KB

🏆 ТОП ФАЙЛЫ ПО РАЗМЕРУ:
1. 📊 data_analysis.py (4.5 KB) - DataAnalysis
2. 📖 GUIDE.md (4.2 KB) - VFS_Docs
3. 🐍 instagram_parser.py (3.2 KB) - InstagramParser
4. 📈 charts.py (2.8 KB) - DataAnalysis
5. 📜 COMMANDS.md (2.9 KB) - VFS_Docs

⏰ ПОСЛЕДНЯЯ АКТИВНОСТЬ:
├── 15:30 - Обновлен instagram_parser.py
├── 14:45 - Изменен config.json
├── 13:20 - Создан новый файл utils.py
└── 12:15 - Добавлена документация README.md
```

---

## 🎯 Команда `/vfs tree --search [keyword]` - Поиск в дереве

### Поиск по ключевому слову:
```bash
/vfs tree --search "parser"
```

```
🔍 Поиск в VFS Tree: "parser"

📁 Найдено в проектах:
├── 📂 InstagramParser (instagram_parser)
│   ├── 🐍 instagram_parser.py (3.2 KB) ⭐ Найдено в названии
│   │   └── 💡 Строка 15: "class InstagramParser:"
│   │   └── 💡 Строка 28: "def parse_profile(self, url):"
│   │   └── 💡 Строка 45: "# Основной парсер профиля"
│   └── 📝 README.md (1.2 KB)
│       └── 💡 Строка 3: "# Instagram Parser Tool"
└── 📂 DataAnalysis (default)
    └── 🐍 data_parser.py (2.1 KB) ⭐ Найдено в названии
        └── 💡 Строка 8: "class DataParser:"
        └── 💡 Строка 22: "def parse_csv(self, filename):"

📊 Результаты поиска:
├── 📂 Проектов найдено: 2
├── 📄 Файлов найдено: 3
├── 💬 Совпадений в коде: 6
└── 🎯 Точность поиска: 85%
```

---

## 🌿 Команда `/vfs tree --branch [проект]` - Ветвление проекта

### Показать "ветви" файлов по типам:
```bash
/vfs tree --branch WebApp
```

```
🌿 Ветвление проекта: WebApp

📁 WebApp (web_app_template)
├── 🌐 Frontend ветвь:
│   ├── 🌐 templates/
│   │   ├── 🏠 index.html (2.1 KB)
│   │   ├── 🔐 login.html (1.8 KB)
│   │   └── 📊 dashboard.html (3.4 KB)
│   └── 🎨 static/
│       ├── 🎨 style.css (2.8 KB)
│       ├── 🟨 script.js (1.9 KB)
│       └── 🖼️ logo.png (15.2 KB)
├── 🐍 Backend ветвь:
│   ├── 🚀 app.py (5.2 KB) ⭐ Главный модуль
│   ├── ⚙️ config.py (845 B) 🔧 Настройки
│   └── 🗃️ database.sql (3.1 KB) 🛢️ Схема БД
└── 📦 Конфигурация ветвь:
    ├── 📦 requirements.txt (156 B) 📋 Зависимости
    ├── 🔧 .env (89 B) 🌍 Переменные
    └── 📝 README.md (2.4 KB) 📚 Документация

🎯 Анализ ветвей:
├── 🌐 Frontend: 6 файлов, 27.2 KB (74% от проекта)
├── 🐍 Backend: 3 файла, 9.2 KB (25% от проекта)
└── 📦 Config: 3 файла, 2.6 KB (7% от проекта)

💡 Рекомендации:
└── Frontend доминирует - рассмотрите оптимизацию изображений
```

---

## 🔄 Команда `/vfs tree --timeline [проект]` - Временная линия

### История изменений проекта:
```bash
/vfs tree --timeline InstagramParser
```

```
⏰ Временная линия проекта: InstagramParser

📅 2024-08-03 (Сегодня):
├── 16:20 🔧 utils.py - Добавлена функция export_sheets()
├── 15:30 🐍 instagram_parser.py - Исправлен баг с обработкой URL
├── 14:45 ⚙️ config.json - Обновлены параметры парсинга
└── 13:15 📦 requirements.txt - Добавлена зависимость pandas

📅 2024-08-02 (Вчера):
├── 18:45 🐍 instagram_parser.py - Добавлен метод get_posts()
├── 17:20 🔧 utils.py - Создан модуль утилит
├── 16:10 ⚙️ config.json - Настроен таргет аккаунта
└── 15:00 📦 requirements.txt - Базовые зависимости

📅 2024-08-01 (2 дня назад):
├── 14:30 🐍 instagram_parser.py - Создан основной класс
├── 14:15 ⚙️ config.json - Начальная конфигурация
└── 14:00 📂 InstagramParser - Создан проект

📊 Статистика активности:
├── 📅 Дней разработки: 3
├── 🔄 Общих изменений: 11
├── 📊 Изменений в день: ~3.7
├── 🎯 Самый активный день: 2024-08-03 (4 изменения)
└── ⏰ Время последней активности: 3 часа назад

🏆 Топ файлы по изменениям:
1. 🐍 instagram_parser.py - 4 изменения
2. ⚙️ config.json - 3 изменения  
3. 🔧 utils.py - 2 изменения
4. 📦 requirements.txt - 2 изменения
```

---

## 🎨 Цветовая схема иконок

### Справочник иконок по типам файлов:

```
📁 ИКОНКИ ФАЙЛОВ ВФС:

🔤 Программирование:
├── 🐍 .py     - Python файлы
├── 🟨 .js     - JavaScript
├── 🟦 .ts     - TypeScript  
├── ⚛️ .jsx    - React JSX
├── ♨️ .java   - Java
├── 🔷 .cs     - C#
├── 🦀 .rs     - Rust
├── 🐹 .go     - Go
├── 💎 .rb     - Ruby
└── 🐘 .php    - PHP

🌐 Веб:
├── 🌐 .html   - HTML страницы
├── 🎨 .css    - CSS стили
├── 🎭 .scss   - SASS стили
├── 🟣 .vue    - Vue.js
├── 🔺 .angular- Angular
└── ⚛️ .react  - React

⚙️ Конфигурация:
├── ⚙️ .json   - JSON файлы
├── 📄 .yaml   - YAML конфигурация
├── 🔧 .env    - Environment переменные
├── 📦 package - Package файлы
├── 🔒 .gitignore - Git исключения
└── 📋 .config - Конфигурация

📊 Данные:
├── 📊 .csv    - CSV таблицы
├── 📈 .xlsx   - Excel файлы
├── 🗃️ .sql    - SQL скрипты
├── 📋 .xml    - XML документы
├── 🔗 .api    - API схемы
└── 📄 .txt    - Текстовые файлы

📝 Документация:
├── 📝 .md     - Markdown документы
├── 📖 README  - Readme файлы
├── 📋 CHANGELOG - История изменений
├── 💡 EXAMPLES - Примеры
├── 📄 LICENSE - Лицензии
└── 📚 .docs   - Документация

🎵 Медиа:
├── 🖼️ .png/.jpg - Изображения
├── 🎵 .mp3/.wav - Аудио
├── 🎬 .mp4/.avi - Видео
├── 📁 .zip/.tar - Архивы
└── 🔗 .link    - Ссылки

🛠️ Системные:
├── 💻 .sh/.bat - Скрипты
├── 🐳 Dockerfile - Docker
├── 🔧 Makefile - Make файлы
├── 📦 .lock   - Lock файлы
└── 🚫 .ignore - Ignore файлы
```

---

**🌳 Теперь у вас есть полная коллекция примеров для красивой визуализации ВФС!**

*Примеры визуализации ВФС v1.1.0*  
*© 2024 Open Web UI VFS Tree Examples* 