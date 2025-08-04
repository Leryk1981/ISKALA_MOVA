# 🔌 Плагиновая интеграция ВФС с Open Web UI

## 🎯 О подходе

**Плагиновая интеграция** — это установка ВФС как расширения для существующего контейнера Open Web UI **без пересборки**. Система работает через встроенную плагиновую архитектуру.

---

## ⚡ Быстрая установка (5 минут)

### Шаг 1: Определите тип установки Open Web UI

```bash
# Для Docker установки
docker ps | grep open-web-ui

# Для локальной установки
ps aux | grep open-web-ui

# Для systemd сервиса
systemctl status open-web-ui
```

### Шаг 2: Скопируйте файлы ВФС

#### Для Docker установки:
```bash
# Найдите ID контейнера
CONTAINER_ID=$(docker ps | grep open-web-ui | awk '{print $1}')

# Скопируйте плагины
docker cp openwebui_integrated_vfs.js $CONTAINER_ID:/app/static/js/
docker cp openwebui_vfs_plugin.js $CONTAINER_ID:/app/plugins/
docker cp vfs_config.json $CONTAINER_ID:/app/backend/data/config/

# Создайте директории для ВФС
docker exec $CONTAINER_ID mkdir -p /app/backend/data/vfs/{projects,templates,cache}
```

#### Для локальной установки:
```bash
# Найдите директорию Open Web UI
OPENWEBUI_PATH="/path/to/open-web-ui"  # Замените на ваш путь

# Скопируйте файлы
cp openwebui_integrated_vfs.js $OPENWEBUI_PATH/static/js/
cp openwebui_vfs_plugin.js $OPENWEBUI_PATH/plugins/
cp vfs_config.json $OPENWEBUI_PATH/backend/data/config/

# Создайте директории
mkdir -p $OPENWEBUI_PATH/backend/data/vfs/{projects,templates,cache}
```

### Шаг 3: Перезапустите Open Web UI

```bash
# Для Docker
docker restart $CONTAINER_ID

# Для systemd
sudo systemctl restart open-web-ui

# Для локальной установки
# Ctrl+C в терминале и затем
npm run dev  # или python -m uvicorn main:app
```

### Шаг 4: Проверьте интеграцию

Откройте Open Web UI и выполните:
```bash
/vfs status
```

Если команда работает — **интеграция успешна!** 🎉

---

## 🛠️ Детальная установка по типам

### Docker установка (Docker Compose)

```bash
# 1. Остановите сервис
docker-compose down

# 2. Добавьте volume для плагинов в docker-compose.yml
echo "
services:
  open-webui:
    volumes:
      - ./vfs_plugins:/app/plugins/vfs:ro
      - ./vfs_config.json:/app/backend/data/config/vfs_config.json:ro
" >> docker-compose.yml

# 3. Создайте директорию плагинов
mkdir -p vfs_plugins
cp openwebui_integrated_vfs.js vfs_plugins/
cp openwebui_vfs_plugin.js vfs_plugins/

# 4. Запустите
docker-compose up -d
```

### Docker установка (простой контейнер)

```bash
# Для существующего контейнера
docker exec -it open-web-ui bash

# Внутри контейнера:
mkdir -p /app/plugins/vfs /app/backend/data/vfs/{projects,templates,cache}

# Выйдите и скопируйте файлы
docker cp openwebui_integrated_vfs.js open-web-ui:/app/plugins/vfs/
docker cp openwebui_vfs_plugin.js open-web-ui:/app/plugins/vfs/
docker cp vfs_config.json open-web-ui:/app/backend/data/config/

# Перезапустите
docker restart open-web-ui
```

### Локальная установка

```bash
# 1. Перейдите в директорию Open Web UI
cd /path/to/open-web-ui

# 2. Создайте директории плагинов
mkdir -p static/js plugins backend/data/{config,vfs/{projects,templates,cache}}

# 3. Скопируйте файлы
cp /path/to/openwebui_integrated_vfs.js static/js/
cp /path/to/openwebui_vfs_plugin.js plugins/
cp /path/to/vfs_config.json backend/data/config/

# 4. Перезапустите сервер
# Нажмите Ctrl+C в терминале где запущен сервер
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

---

## 🔍 Проверка успешной установки

### Базовая проверка
```bash
# В чате Open Web UI выполните:
/vfs help
# Должен показать список команд ВФС
```

### Расширенная проверка
```bash
# Проверьте статус системы
/vfs status

# Создайте тестовый проект
/project create TestProject default

# Проверьте список проектов
/project list

# Создайте файл
/file create TestProject test.py "print('VFS работает!')"

# Прочитайте файл
/file read TestProject test.py

# Посмотрите статистику
/vfs stats
```

---

## 🐛 Решение проблем

### Команды ВФС не работают

**Проблема**: `/vfs help` возвращает "Unknown command"

**Решение**:
```bash
# 1. Проверьте, что файлы скопированы
docker exec open-web-ui ls -la /app/plugins/
docker exec open-web-ui ls -la /app/static/js/ | grep vfs

# 2. Проверьте логи
docker logs open-web-ui

# 3. Перезапустите с принудительной перезагрузкой
docker restart open-web-ui

# 4. Если не помогает - удалите кэш браузера
# Откройте Developer Tools (F12) → Application → Clear Storage
```

### Файлы не сохраняются

**Проблема**: Проекты создаются, но не сохраняются между сессиями

**Решение**:
```bash
# 1. Проверьте права доступа
docker exec open-web-ui ls -la /app/backend/data/vfs/

# 2. Создайте директории с правильными правами
docker exec open-web-ui chown -R user:user /app/backend/data/vfs/

# 3. Проверьте конфигурацию Storage API
docker exec open-web-ui cat /app/backend/data/config/vfs_config.json
```

### Низкая производительность

**Проблема**: ВФС работает медленно

**Решение**:
```bash
# 1. Включите кэширование в vfs_config.json
{
  "performance": {
    "cache_enabled": true,
    "cache_size": "50MB"
  }
}

# 2. Очистите кэш ВФС
docker exec open-web-ui rm -rf /app/backend/data/vfs/cache/*

# 3. Перезапустите с новой конфигурацией
docker restart open-web-ui
```

---

## 📦 Альтернативный подход: Execution в чате

Если плагиновая интеграция недоступна, можно использовать **код напрямую в чате**:

```javascript
// Вставьте этот код как сообщение в Open Web UI
// ВФС будет работать в рамках сессии чата

// 1. Определите объект для хранения данных
if (!window.vfsData) {
    window.vfsData = {
        projects: {},
        activeProject: null
    };
}

// 2. Создайте проект
function createProject(name, template = 'default') {
    window.vfsData.projects[name] = {
        name: name,
        files: {},
        created: new Date().toISOString(),
        template: template
    };
    
    // Добавьте базовые файлы для шаблона
    if (template === 'default') {
        window.vfsData.projects[name].files['main.py'] = `
def main():
    print("Hello from ${name}!")

if __name__ == "__main__":
    main()
`;
        window.vfsData.projects[name].files['README.md'] = `# ${name}\n\nПроект создан в Open Web UI`;
    }
    
    window.vfsData.activeProject = name;
    console.log(`✅ Проект "${name}" создан`);
    return window.vfsData.projects[name];
}

// 3. Добавьте файл в проект
function addFile(projectName, fileName, content) {
    if (!window.vfsData.projects[projectName]) {
        console.error(`❌ Проект "${projectName}" не найден`);
        return false;
    }
    
    window.vfsData.projects[projectName].files[fileName] = content;
    console.log(`✅ Файл "${fileName}" добавлен в проект "${projectName}"`);
    return true;
}

// 4. Просмотр проекта
function showProject(projectName) {
    const project = window.vfsData.projects[projectName];
    if (!project) {
        console.error(`❌ Проект "${projectName}" не найден`);
        return;
    }
    
    console.log(`📂 Проект: ${project.name}`);
    console.log(`📅 Создан: ${project.created}`);
    console.log(`📄 Файлы:`);
    
    Object.keys(project.files).forEach(fileName => {
        console.log(`  - ${fileName} (${project.files[fileName].length} символов)`);
    });
}

// 5. Просмотр содержимого файла
function showFile(projectName, fileName) {
    const project = window.vfsData.projects[projectName];
    if (!project || !project.files[fileName]) {
        console.error(`❌ Файл "${fileName}" не найден в проекте "${projectName}"`);
        return;
    }
    
    console.log(`📄 ${fileName}:`);
    console.log('─'.repeat(50));
    console.log(project.files[fileName]);
    console.log('─'.repeat(50));
}

// 6. Экспорт проекта
function exportProject(projectName, format = 'json') {
    const project = window.vfsData.projects[projectName];
    if (!project) {
        console.error(`❌ Проект "${projectName}" не найден`);
        return;
    }
    
    if (format === 'json') {
        const exportData = JSON.stringify(project, null, 2);
        console.log(`📦 Экспорт проекта "${projectName}":`);
        console.log(exportData);
        
        // Создать ссылку для скачивания
        const blob = new Blob([exportData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${projectName}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// ИСПОЛЬЗОВАНИЕ:
console.log('🚀 ВФС инициализирована в браузере!');
console.log('Доступные команды:');
console.log('- createProject(name, template)');
console.log('- addFile(projectName, fileName, content)');
console.log('- showProject(projectName)');
console.log('- showFile(projectName, fileName)');
console.log('- exportProject(projectName)');

// Создайте тестовый проект
createProject('InstagramParser', 'default');
addFile('InstagramParser', 'parser.py', `
import requests
from bs4 import BeautifulSoup

class InstagramParser:
    def __init__(self):
        self.session = requests.Session()
        
    def parse_profile(self, username):
        url = f"https://www.instagram.com/{username}/"
        response = self.session.get(url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Логика парсинга...
        
        return {
            'username': username,
            'status': 'parsed'
        }

if __name__ == "__main__":
    parser = InstagramParser()
    result = parser.parse_profile('test_user')
    print(result)
`);

console.log('✅ Тестовый проект создан! Используйте showProject("InstagramParser") для просмотра');
```

---

## 🎉 Результат

После успешной интеграции вы получите:

### ✅ Что работает:
- **Командный интерфейс**: `/vfs`, `/project`, `/file`, `/template`, `/export`
- **Управление проектами**: Создание, удаление, переключение
- **Файловые операции**: Создание, чтение, обновление, удаление файлов
- **Шаблоны**: 3 готовых шаблона (default, instagram_parser, api_client)
- **Экспорт/импорт**: JSON формат для проектов
- **Интеграция с Storage API**: Постоянное хранение данных

### 🎯 Первые команды для тестирования:
```bash
/vfs status                                    # Статус системы
/project create MyParser instagram_parser     # Создать проект парсера
/file list MyParser                           # Список файлов
/file read MyParser instagram_parser.py       # Читать код парсера
/vfs stats                                    # Статистика ВФС
```

**🎊 Поздравляем! ВФС интегрирована с Open Web UI через плагиновую систему!** 