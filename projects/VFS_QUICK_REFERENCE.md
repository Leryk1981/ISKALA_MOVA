# ⚡ Быстрый справочник ВФС

**Шпаргалка по командам виртуальной файловой системы**  
*Версия: 1.0.0 | Обновлено: 2024-08-03*

---

## 🚀 Первые шаги

```bash
# Проверить статус системы
/vfs status

# Создать первый проект  
/project create MyFirstProject default

# Посмотреть что создалось
/project list
/file list MyFirstProject
```

---

## 📂 Команды проектов

| Команда | Описание | Пример |
|---------|----------|--------|
| `/project create <имя> [шаблон]` | Создать проект | `/project create MyBot instagram_parser` |
| `/project list` | Список всех проектов | `/project list` |  
| `/project switch <имя>` | Переключиться на проект | `/project switch MyBot` |
| `/project info [имя]` | Информация о проекте | `/project info MyBot` |
| `/project delete <имя>` | Удалить проект | `/project delete TestProject` |

---

## 📄 Команды файлов

| Команда | Описание | Пример |
|---------|----------|--------|
| `/file create <проект> <путь> [содержимое]` | Создать файл | `/file create MyBot utils.py "# Utilities"` |
| `/file read <проект> <путь>` | Прочитать файл | `/file read MyBot main.py` |
| `/file update <проект> <путь> <содержимое>` | Обновить файл | `/file update MyBot config.json '{...}'` |
| `/file list <проект>` | Список файлов проекта | `/file list MyBot` |
| `/file delete <проект> <путь>` | Удалить файл | `/file delete MyBot temp.py` |

---

## 🎨 Шаблоны

| Команда | Описание | Пример |
|---------|----------|--------|
| `/template list` | Список шаблонов | `/template list` |
| `/template info <имя>` | Информация о шаблоне | `/template info instagram_parser` |

**Доступные шаблоны:**
- `default` - базовый Python проект
- `instagram_parser` - парсер Instagram  
- `api_client` - REST API клиент

---

## 💾 Экспорт/импорт

| Команда | Описание | Пример |
|---------|----------|--------|
| `/export <проект> [формат]` | Экспорт проекта | `/export MyBot json` |
| `/import <данные>` | Импорт проекта | `/import '{"name":"Test","files":{}}'` |

---

## 🔧 Системные команды

| Команда | Описание | Результат |
|---------|----------|-----------|
| `/vfs status` | Статус системы | Общая информация о ВФС |
| `/vfs stats` | Подробная статистика | Количество проектов, файлов, размер |
| `/vfs help` | Справка по командам | Список всех команд |

## 🌳 Команды визуализации

| Команда | Описание | Пример |
|---------|----------|--------|
| `/vfs tree` | Древовидная структура всех проектов | `/vfs tree` |
| `/vfs tree <проект>` | Структура конкретного проекта | `/vfs tree InstagramBot` |
| `/vfs tree <проект> --detail` | Подробная информация о проекте | `/vfs tree InstagramBot --detail` |
| `/vfs gui` | Интерактивное главное меню | `/vfs gui` |
| `/vfs gui <проект>` | Меню конкретного проекта | `/vfs gui InstagramBot` |

---

## 🎯 Быстрые сценарии

### 🔥 Создать парсер Instagram за 2 минуты
```bash
/project create InstagramBot instagram_parser
/file update InstagramBot config.json '{"target":"username","limit":100}'
/file read InstagramBot instagram_parser.py
/vfs tree InstagramBot  # Посмотреть структуру
```

### 🌐 Создать API клиент за 1 минуту
```bash
/project create WeatherAPI api_client  
/file read WeatherAPI client.py
/vfs gui WeatherAPI     # Открыть меню проекта
```

### 📚 Создать документацию
```bash
/project create MyDocs default
/file update MyDocs README.md "# Моя документация\n\n## Обзор\n..."
/file create MyDocs CHANGELOG.md "# История изменений\n\n## v1.0.0\n- Первая версия"
/vfs tree MyDocs --detail  # Детальный обзор
```

### 🌳 Визуализация всех проектов
```bash
/vfs tree               # Древовидная структура
/vfs gui                # Интерактивное меню
/vfs tree --stats       # С подробной статистикой
```

---

## ❓ FAQ - Частые вопросы

### **Q: Где хранятся мои проекты?**
**A:** В localStorage браузера. Физически на диске в папке браузера:
- Windows: `C:\Users\[user]\AppData\Local\[browser]\User Data\Default\Local Storage\`
- macOS: `~/Library/Application Support/[browser]/Default/Local Storage/`
- Linux: `~/.config/[browser]/Default/Local Storage/`

### **Q: Что если я очищу кэш браузера?**
**A:** ⚠️ **ВСЕ ДАННЫЕ БУДУТ ПОТЕРЯНЫ!** Всегда делайте бэкапы:
```bash
/export MyProject json    # Экспорт отдельного проекта
```
Или используйте закладку для быстрого бэкапа (см. Backup Guide).

### **Q: Какой максимальный размер файла?**
**A:** По умолчанию 10 МБ на файл, ~5-10 МБ общий лимит localStorage.

### **Q: Можно ли выполнять код из ВФС?**
**A:** Нет, ВФС только для редактирования. Скопируйте код в локальную среду для выполнения.

### **Q: Как поделиться проектом?**
**A:** Экспортируйте проект и отправьте JSON файл:
```bash
/export MyProject json
```

### **Q: Как восстановить удаленный проект?**
**A:** Если есть бэкап - используйте `/import`. Без бэкапа - данные потеряны навсегда.

### **Q: Поддерживаются ли бинарные файлы?**
**A:** Нет, только текстовые файлы (код, документы, JSON, etc.).

### **Q: Можно ли работать оффлайн?**
**A:** Да, после загрузки ВФС работает полностью в браузере.

### **Q: Есть ли синхронизация между устройствами?**
**A:** Нет, данные привязаны к браузеру. Используйте экспорт для переноса.

### **Q: Как создать собственный шаблон?**
**A:** Пока не реализовано. Создайте проект и экспортируйте как образец.

---

## 🐛 Решение проблем

### **Проблема: Команды не работают**
```bash
# Проверьте статус
/vfs status

# Если не отвечает - обновите страницу
F5 или Ctrl+R
```

### **Проблема: Проект не создается**
```bash
# Проверьте имя проекта (только буквы, цифры, _, -)
/project create Test_Project_123 default

# Проверьте свободное место
/vfs stats
```

### **Проблема: Файл не сохраняется**
```bash
# Проверьте размер файла (не больше 10 МБ)
# Проверьте кодировку (только UTF-8)
# Убедитесь что проект существует
/project list
```

### **Проблема: Данные пропали**
```bash
# Проверьте localStorage в консоли браузера (F12)
for (let key in localStorage) {
    if (key.startsWith('vfs_')) {
        console.log(key);
    }
}

# Если пусто - данные действительно потеряны
# Восстановите из бэкапа
```

---

## ⚡ Горячие клавиши

| Действие | Клавиши | Описание |
|----------|---------|----------|
| Открыть консоль | `F12` | Для отладки ВФС |
| Обновить страницу | `F5` или `Ctrl+R` | При зависании ВФС |
| Найти в чате | `Ctrl+F` | Поиск по команд истории |

---

## 📊 Лимиты и ограничения

| Параметр | Лимит | Примечание |
|----------|-------|------------|
| Размер файла | 10 МБ | Настраивается в конфиге |
| Общий размер хранилища | 5-10 МБ | Лимит localStorage |
| Количество проектов | Не ограничено | В рамках размера хранилища |
| Длина имени проекта | 50 символов | Только латиница, цифры, _, - |
| Глубина вложенности | Без ограничений | Виртуальная структура |

---

## 🎨 Примеры файлов

### Python скрипт
```python
# main.py
import requests
import json

def main():
    print("Hello from VFS!")
    
if __name__ == "__main__":
    main()
```

### Конфигурация JSON
```json
{
  "api_key": "your-key-here",
  "timeout": 30,
  "retries": 3,
  "debug": true
}
```

### Requirements.txt
```
requests>=2.28.0
beautifulsoup4>=4.11.0
selenium>=4.5.0
pandas>=1.5.0
```

### README.md
```markdown
# Мой проект

## Описание
Краткое описание проекта

## Установка
```bash
pip install -r requirements.txt
```

## Использование
```python
python main.py
```
```

---

## 🔗 Полезные ссылки

- 📚 [Полная документация](VFS_FUNCTIONALITY_DOCS.md)
- 🏗️ [Архитектура системы](VFS_ARCHITECTURE_DOCS.md)
- 💾 [Руководство по бэкапам](VFS_BACKUP_GUIDE.md)
- 🐛 Баг-репорты: создайте issue в проекте

---

## 🎯 Советы профи

### 💡 Организация проектов
```bash
# Создавайте проекты с понятными именами
/project create Instagram_Parser_v2 instagram_parser
/project create Weather_API_Client api_client
/project create Project_Documentation default
```

### 💡 Структурирование файлов
```bash
# Используйте логическую структуру
/file create MyBot src/main.py "# Main module"
/file create MyBot src/utils.py "# Utilities"  
/file create MyBot config/settings.json "{}"
/file create MyBot docs/README.md "# Documentation"
```

### 💡 Управление версиями (вручную)
```bash
# Создавайте бэкапы при важных изменениях
/export MyBot json    # Перед большими изменениями

# Добавляйте версии в имена
/project create MyBot_v1_0 default
/project create MyBot_v1_1 default
```

### 💡 Резервное копирование
```javascript
// Создайте закладку для быстрого бэкапа
javascript:(function(){
  const backup = {};
  for (let key in localStorage) {
    if (key.startsWith('vfs_')) backup[key] = localStorage[key];
  }
  const blob = new Blob([JSON.stringify(backup, null, 2)], {type: 'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `vfs_backup_${new Date().toISOString().split('T')[0]}.json`;
  a.click();
  URL.revokeObjectURL(url);
})();
```

---

**📖 Для подробной информации см. полную документацию в папке `projects/`**

*Быстрый справочник ВФС v1.0.0*  
*© 2024 Open Web UI VFS Quick Reference* 