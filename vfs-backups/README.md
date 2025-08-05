# 🔄 VFS Auto Backup System

Автоматическая система резервного копирования данных Virtual File System (VFS) в Git репозиторий.

## 📋 Описание

VFS Auto Backup автоматически сохраняет данные из localStorage браузера в JSON файлы и коммитит их в Git репозиторий для безопасного хранения.

## 🚀 Использование

### Автоматический режим
```javascript
// Инициализация (автоматически в Open Web UI)
const vfsBackup = new VFSAutoBackup({
    debug: true,
    autoBackupEnabled: true,
    backupInterval: 15 * 60 * 1000 // 15 минут
});
```

### Ручной backup
```javascript
// В консоли браузера
vfsBackupNow();           // Создать backup сейчас
vfsListBackups();         // Список всех backup'ов
```

### API Endpoints
```bash
# Создать backup
POST /api/v1/vfs/backup
Content-Type: application/json
{
  "reason": "manual",
  "timestamp": "2024-08-05T12:30:00Z",
  "vfs_data": { ... }
}

# Список backup'ов
GET /api/v1/vfs/backups
```

## 📁 Структура файлов

```
vfs-backups/
├── README.md
├── vfs-backup-2024-08-05T12-30-00.json
├── vfs-backup-2024-08-05T13-00-00.json
└── ...
```

## 📄 Формат backup файла

```json
{
  "timestamp": "2024-08-05T12:30:00.000Z",
  "backup_data": {
    "reason": "scheduled",
    "vfs_data": {
      "vfs_projects": { ... },
      "vfs_meta": { ... },
      "_metadata": {
        "extraction_time": "2024-08-05T12:30:00.000Z",
        "browser": "Mozilla/5.0...",
        "url": "http://localhost:3000",
        "storage_size": 1024
      }
    }
  },
  "metadata": {
    "version": "1.0",
    "source": "vfs-auto-backup"
  }
}
```

## ⚙️ Настройки

### Триггеры backup'а
- **Периодически**: каждые 15-30 минут
- **При закрытии страницы**: `beforeunload` event
- **При потере фокуса**: переключение вкладки
- **При изменении данных**: debounced на 5 секунд

### Конфигурация
```javascript
const config = {
    apiEndpoint: '/api/v1/vfs/backup',
    backupInterval: 30 * 60 * 1000,  // 30 минут
    autoBackupEnabled: true,
    debug: false
};
```

## 🔧 Интеграция с Open Web UI

1. Добавьте `vfs_auto_backup.js` в Open Web UI
2. Скрипт автоматически определит наличие VFS данных
3. Backup'ы будут создаваться автоматически

## 🛡️ Безопасность

- Данные сохраняются локально в репозитории
- Git коммиты автоматические с временными метками
- Нет передачи данных на внешние сервисы
- localStorage данные не покидают ваш контроль

## 📊 Мониторинг

```bash
# Посмотреть последние backup'ы
ls -la vfs-backups/ | tail -5

# Размер backup'ов
du -sh vfs-backups/

# Git история backup'ов
git log --oneline --grep="VFS auto-backup"
```

## 🔄 Восстановление данных

```javascript
// Загрузить backup в VFS (будущая функция)
async function restoreFromBackup(backupFile) {
    const response = await fetch(`/vfs-backups/${backupFile}`);
    const backup = await response.json();
    
    // Восстановить в localStorage
    Object.entries(backup.backup_data.vfs_data).forEach(([key, value]) => {
        if (key.startsWith('vfs_')) {
            localStorage.setItem(key, JSON.stringify(value));
        }
    });
    
    location.reload(); // Перезагрузить VFS
}
```

## 📈 Статистика

- **Частота backup'ов**: 15-30 минут
- **Размер файла**: обычно 1-10 KB
- **Хранение**: неограниченно (управляется Git)
- **Производительность**: минимальное влияние

---

**Автоматическое сохранение VFS данных обеспечивает надежность и переносимость ваших проектов!** 🚀 