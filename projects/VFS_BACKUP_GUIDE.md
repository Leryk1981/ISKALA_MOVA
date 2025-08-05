# 🔄 Руководство по автоматическому резервному копированию VFS

**Современная система автоматических backup'ов с Git интеграцией**  
*Версия: 2.0.0 | Обновлено: 2025-08-05*

---

## 🚀 **НОВАЯ VFS AUTO BACKUP СИСТЕМА**

### ✨ Революционные возможности:
```
🔄 АВТОМАТИЧЕСКИЕ BACKUP'Ы:
├── Периодические backup'ы каждые 15-30 минут
├── Backup при закрытии браузера
├── Backup при потере фокуса (переключение вкладки)
├── Backup при изменении данных (debounced)
└── Ручные backup'ы через API или консоль

🏗️ АРХИТЕКТУРНАЯ ИНТЕГРАЦИЯ:
├── RESTful API endpoints (/api/v1/vfs/backup, /api/v1/vfs/backups)
├── Автоматические Git коммиты с временными метками
├── Структурированное JSON хранение
├── Background tasks для Git операций
└── Comprehensive error handling и logging

🛡️ НАДЕЖНОСТЬ И БЕЗОПАСНОСТЬ:
├── Локальное хранение в Git репозитории
├── Нет передачи данных на внешние сервисы
├── Автоматическая валидация backup'ов
├── Метаданные для отслеживания изменений
└── Production-ready health monitoring
```

---

## ⚡ **БЫСТРЫЙ СТАРТ**

### 1. **Автоматическая активация**
VFS Auto Backup система **автоматически активируется** при наличии VFS данных в Open Web UI:

```javascript
// Система автоматически определяет VFS и запускается
if (window.localStorage.getItem('vfs_projects')) {
    window.vfsBackup = new VFSAutoBackup({
        debug: true,
        autoBackupEnabled: true,
        backupInterval: 15 * 60 * 1000 // 15 минут
    });
    
    console.log('🔄 VFS Auto Backup активирован');
}
```

### 2. **Мгновенные команды**
```javascript
// В консоли браузера (F12 → Console)
vfsBackupNow();           // Создать backup сейчас
vfsListBackups();         // Список всех backup'ов
```

### 3. **API Endpoints**
```bash
# Создать backup
curl -X POST http://localhost:8000/api/v1/vfs/backup \
  -H "Content-Type: application/json" \
  -d '{"reason":"manual","vfs_data":{"vfs_projects":{...}}}'

# Список backup'ов  
curl -X GET http://localhost:8000/api/v1/vfs/backups
```

---

## 🔧 **КОНФИГУРАЦИЯ СИСТЕМЫ**

### **Настройки в vfs_backup_config.json:**
```json
{
  "vfs_backup": {
    "enabled": true,
    "api_endpoint": "/api/v1/vfs/backup",
    "backup_interval_minutes": 15,
    "triggers": {
      "scheduled": true,
      "page_close": true,
      "focus_lost": true,
      "data_changed": true
    },
    "debounce_delay_seconds": 5,
    "max_backup_size_mb": 10,
    "retention": {
      "keep_daily": 30,
      "keep_weekly": 12,
      "keep_monthly": 12
    },
    "git": {
      "auto_commit": true,
      "commit_message_template": "🔄 VFS auto-backup {timestamp}",
      "branch": "main"
    },
    "notifications": {
      "show_success": false,
      "show_errors": true,
      "debug_mode": false
    }
  }
}
```

### **Триггеры backup'ов:**
- **⏰ Периодически**: каждые 15-30 минут (настраивается)
- **🚪 При закрытии страницы**: `beforeunload` event
- **🔄 При потере фокуса**: переключение вкладки  
- **✏️ При изменении данных**: debounced на 5 секунд
- **👆 Ручные backup'ы**: через API или консольные команды

---

## 📁 **СТРУКТУРА BACKUP'ОВ**

### **Директория vfs-backups/:**
```
vfs-backups/
├── README.md
├── vfs-backup-2025-08-05T12-30-00.json
├── vfs-backup-2025-08-05T13-00-00.json
├── vfs-backup-2025-08-05T13-30-00.json
└── ...
```

### **Формат backup файла:**
```json
{
  "timestamp": "2025-08-05T12:30:00.000Z",
  "backup_data": {
    "reason": "scheduled",
    "timestamp": "2025-08-05T12:30:00Z",
    "user_agent": "Mozilla/5.0...",
    "url": "http://localhost:3000",
    "vfs_data": {
      "vfs_projects": {
        "MyProject": {
          "name": "My Project",
          "files": {
            "main.py": "print('Hello VFS!')",
            "config.json": "{\"version\": \"1.0\"}"
          }
        }
      },
      "vfs_meta": {
        "version": "1.0",
        "created": "2025-08-05T12:30:00Z"
      },
      "_metadata": {
        "extraction_time": "2025-08-05T12:30:00.000Z",
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

---

## 🎯 **ИНТЕГРАЦИЯ С OPEN WEB UI**

### **1. Автоматическая интеграция**
Добавьте `vfs_auto_backup.js` в Open Web UI:

```html
<!-- В HTML Open Web UI -->
<script src="/static/vfs_auto_backup.js"></script>
```

### **2. Ручная активация**
```javascript
// Если автоматическая активация не сработала
const vfsBackup = new VFSAutoBackup({
    debug: true,
    autoBackupEnabled: true,
    backupInterval: 15 * 60 * 1000, // 15 минут
    apiEndpoint: '/api/v1/vfs/backup'
});

// Глобальные команды
window.vfsBackupNow = () => vfsBackup.manualBackup();
window.vfsListBackups = () => vfsBackup.listBackups();
```

### **3. Мониторинг в консоли**
```javascript
// Включить debug режим
vfsBackup.debug = true;

// Посмотреть статистику
console.log('VFS Backup активен:', vfsBackup.autoBackupEnabled);
console.log('Интервал backup:', vfsBackup.backupInterval / 1000 / 60, 'минут');
```

---

## 🔄 **GIT ИНТЕГРАЦИЯ**

### **Автоматические коммиты:**
```bash
# Система автоматически создает коммиты:
git log --oneline --grep="VFS auto-backup"

# Пример коммитов:
3366d4b 🔄 VFS auto-backup 2025-08-05 12:33
2847a1c 🔄 VFS auto-backup 2025-08-05 12:18
1659f2e 🔄 VFS auto-backup 2025-08-05 12:03
```

### **Структура коммитов:**
```bash
# Каждый backup создает:
1. JSON файл с данными VFS
2. Git add файла
3. Git commit с временной меткой
4. Логирование операции
```

### **Мониторинг Git истории:**
```bash
# Посмотреть последние backup'ы
git log --oneline --grep="VFS auto-backup" -10

# Размер backup'ов  
du -sh vfs-backups/

# Статистика backup'ов
ls -la vfs-backups/ | wc -l
```

---

## 🛡️ **БЕЗОПАСНОСТЬ И НАДЕЖНОСТЬ**

### **Принципы безопасности:**
```
✅ ЛОКАЛЬНОЕ ХРАНЕНИЕ:
├── Все данные остаются в вашем Git репозитории
├── Нет передачи на внешние сервисы
├── Полный контроль над backup'ами
└── Возможность шифрования репозитория

✅ ОТКАЗОУСТОЙЧИВОСТЬ:
├── Background tasks не блокируют UI
├── Graceful handling Git ошибок
├── Валидация данных перед сохранением
└── Логирование всех операций
```

### **Мониторинг системы:**
```bash
# Health check VFS backup системы
curl http://localhost:8000/health

# Статус последних backup'ов
curl http://localhost:8000/api/v1/vfs/backups | jq '.'

# Логи системы
docker logs iskala-new-api --tail 50 | grep "VFS"
```

---

## 🔧 **РАСШИРЕННАЯ НАСТРОЙКА**

### **1. Кастомные триггеры**
```javascript
// Добавить собственные триггеры
vfsBackup.setupCustomTriggers = function() {
    // Backup при сохранении файла
    document.addEventListener('vfs:fileSaved', () => {
        this.debounceBackup('file_saved');
    });
    
    // Backup при создании проекта
    document.addEventListener('vfs:projectCreated', () => {
        this.createBackup('project_created');
    });
};
```

### **2. Фильтрация данных**
```javascript
// Исключить определенные данные из backup
vfsBackup.filterVFSData = function(vfsData) {
    // Удалить временные файлы
    Object.keys(vfsData).forEach(key => {
        if (key.includes('_temp_') || key.includes('_cache_')) {
            delete vfsData[key];
        }
    });
    
    return vfsData;
};
```

### **3. Кастомные уведомления**
```javascript
// Собственная система уведомлений
vfsBackup.showNotification = function(message, type) {
    if (window.showToast) {
        window.showToast(message, type);
    } else if (type === 'error') {
        console.error(`[VFS Backup] ${message}`);
        // Показать в UI
        if (document.getElementById('vfs-status')) {
            document.getElementById('vfs-status').textContent = message;
        }
    }
};
```

---

## 📊 **МОНИТОРИНГ И АНАЛИТИКА**

### **Dashboard для контроля:**
```javascript
// Создать dashboard для мониторинга
class VFSBackupDashboard {
    async getBackupStats() {
        const response = await fetch('/api/v1/vfs/backups');
        const data = await response.json();
        
        return {
            total_backups: data.backups.length,
            latest_backup: data.backups[0]?.created,
            total_size: data.backups.reduce((sum, b) => sum + b.size, 0),
            avg_backup_size: data.backups.length > 0 ? 
                data.backups.reduce((sum, b) => sum + b.size, 0) / data.backups.length : 0
        };
    }
    
    async renderDashboard() {
        const stats = await this.getBackupStats();
        
        const dashboard = `
            <div class="vfs-backup-dashboard">
                <h3>📊 VFS Backup Statistics</h3>
                <div class="stats">
                    <div>Total Backups: ${stats.total_backups}</div>
                    <div>Latest: ${new Date(stats.latest_backup).toLocaleString()}</div>
                    <div>Total Size: ${(stats.total_size / 1024).toFixed(1)} KB</div>
                    <div>Avg Size: ${(stats.avg_backup_size / 1024).toFixed(1)} KB</div>
                </div>
            </div>
        `;
        
        document.getElementById('vfs-dashboard').innerHTML = dashboard;
    }
}
```

### **Алерты и предупреждения:**
```javascript
// Система предупреждений
class VFSBackupAlerts {
    checkBackupHealth() {
        const lastBackup = localStorage.getItem('vfs_last_backup_time');
        const now = Date.now();
        
        if (!lastBackup) {
            this.showAlert('⚠️ Нет backup\'ов! Создайте backup немедленно.', 'error');
            return;
        }
        
        const timeSinceBackup = now - parseInt(lastBackup);
        const hoursAgo = timeSinceBackup / (1000 * 60 * 60);
        
        if (hoursAgo > 24) {
            this.showAlert(`⚠️ Последний backup ${hoursAgo.toFixed(1)} часов назад`, 'warning');
        } else if (hoursAgo > 48) {
            this.showAlert('🚨 Критично! Backup старше 48 часов!', 'error');
        }
    }
    
    showAlert(message, type) {
        console.log(`[VFS Alert] ${message}`);
        // Интеграция с системой уведомлений Open Web UI
        if (window.showNotification) {
            window.showNotification(message, type);
        }
    }
}
```

---

## 🔄 **ВОССТАНОВЛЕНИЕ ДАННЫХ**

### **1. Восстановление из API**
```bash
# Получить список backup'ов
curl http://localhost:8000/api/v1/vfs/backups

# Скачать конкретный backup
curl http://localhost:8000/vfs-backups/vfs-backup-2025-08-05T12-30-00.json
```

### **2. Восстановление через консоль**
```javascript
// Функция восстановления в консоли браузера
async function restoreFromBackupFile(backupFileName) {
    try {
        // Загрузить backup с сервера
        const response = await fetch(`/vfs-backups/${backupFileName}`);
        const backup = await response.json();
        
        // Восстановить в localStorage
        const vfsData = backup.backup_data.vfs_data;
        Object.entries(vfsData).forEach(([key, value]) => {
            if (key.startsWith('vfs_') && key !== '_metadata') {
                localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value));
            }
        });
        
        console.log('✅ VFS данные восстановлены');
        
        // Перезагрузить страницу
        if (confirm('Перезагрузить страницу для применения изменений?')) {
            location.reload();
        }
        
    } catch (error) {
        console.error('❌ Ошибка восстановления:', error);
    }
}

// Использование:
// restoreFromBackupFile('vfs-backup-2025-08-05T12-30-00.json');
```

### **3. Автоматическое восстановление**
```javascript
// Функция для автоматического восстановления последнего backup'а
async function autoRestoreLatestBackup() {
    try {
        const response = await fetch('/api/v1/vfs/backups');
        const data = await response.json();
        
        if (data.backups.length === 0) {
            console.log('❌ Нет доступных backup\'ов');
            return;
        }
        
        const latestBackup = data.backups[0];
        await restoreFromBackupFile(latestBackup.filename);
        
    } catch (error) {
        console.error('❌ Ошибка автовосстановления:', error);
    }
}
```

---

## 📈 **ПРОИЗВОДИТЕЛЬНОСТЬ И ОПТИМИЗАЦИЯ**

### **Метрики производительности:**
```javascript
// Отслеживание производительности backup'ов
class VFSBackupMetrics {
    constructor() {
        this.metrics = {
            backup_count: 0,
            total_backup_time: 0,
            avg_backup_time: 0,
            largest_backup_size: 0,
            smallest_backup_size: Infinity,
            errors_count: 0
        };
    }
    
    recordBackup(duration, size, success) {
        this.metrics.backup_count++;
        
        if (success) {
            this.metrics.total_backup_time += duration;
            this.metrics.avg_backup_time = this.metrics.total_backup_time / this.metrics.backup_count;
            
            if (size > this.metrics.largest_backup_size) {
                this.metrics.largest_backup_size = size;
            }
            if (size < this.metrics.smallest_backup_size) {
                this.metrics.smallest_backup_size = size;
            }
        } else {
            this.metrics.errors_count++;
        }
    }
    
    getReport() {
        return {
            ...this.metrics,
            success_rate: ((this.metrics.backup_count - this.metrics.errors_count) / this.metrics.backup_count * 100).toFixed(1) + '%'
        };
    }
}
```

### **Оптимизация размера backup'ов:**
```javascript
// Сжатие данных перед backup'ом
vfsBackup.compressVFSData = function(vfsData) {
    // Удалить пустые проекты
    Object.keys(vfsData).forEach(key => {
        if (key.startsWith('vfs_projects/')) {
            const project = JSON.parse(vfsData[key]);
            if (!project.files || Object.keys(project.files).length === 0) {
                delete vfsData[key];
            }
        }
    });
    
    // Сжать повторяющиеся данные
    // (здесь можно добавить алгоритмы сжатия)
    
    return vfsData;
};
```

---

## 🎯 **ЧЕКЛИСТ МИГРАЦИИ**

### ✅ **Переход на новую систему:**
- [ ] Убедиться что FastAPI сервис запущен на порту 8000
- [ ] Проверить доступность `/api/v1/vfs/backup` endpoint'а
- [ ] Добавить `vfs_auto_backup.js` в Open Web UI
- [ ] Настроить `vfs_backup_config.json` под свои нужды
- [ ] Протестировать создание backup'а через `vfsBackupNow()`
- [ ] Проверить автоматические Git коммиты
- [ ] Настроить мониторинг и алерты

### ✅ **Проверка работоспособности:**
- [ ] Backup'ы создаются автоматически каждые 15-30 минут
- [ ] Git коммиты появляются в истории
- [ ] API endpoints отвечают корректно
- [ ] Восстановление работает через консоль
- [ ] Логи показывают успешные операции

---

## 🆘 **ЭКСТРЕННЫЕ ПРОЦЕДУРЫ**

### **Если автоматические backup'ы не работают:**
```javascript
// Экстренный backup через консоль
(function emergencyVFSBackup() {
    const vfsData = {};
    let count = 0;
    
    for (let key in localStorage) {
        if (key.startsWith('vfs_')) {
            vfsData[key] = localStorage[key];
            count++;
        }
    }
    
    if (count > 0) {
        const backup = {
            timestamp: new Date().toISOString(),
            emergency: true,
            vfs_data: vfsData,
            metadata: {
                source: 'emergency_console_backup',
                count: count
            }
        };
        
        const blob = new Blob([JSON.stringify(backup, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `EMERGENCY_vfs_backup_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        console.log(`🚨 Экстренный backup создан! Элементов: ${count}`);
    } else {
        console.log('❌ VFS данные не найдены');
    }
})();
```

### **Если Git коммиты не работают:**
```bash
# Ручное добавление backup'а в Git
git add vfs-backups/
git commit -m "🔄 Manual VFS backup $(date)"
git push origin main
```

---

## 📞 **ПОДДЕРЖКА И ОБНОВЛЕНИЯ**

### **Версии системы:**
- **v1.0.0**: Оригинальная ручная система backup'ов
- **v2.0.0**: Автоматическая система с API интеграцией ✅ **ТЕКУЩАЯ**

### **Планируемые обновления:**
- **v2.1.0**: Сжатие backup'ов и retention policies
- **v2.2.0**: Интеграция с облачными хранилищами
- **v2.3.0**: Инкрементальные backup'ы
- **v3.0.0**: Распределенная система backup'ов

### **Техническая поддержка:**
```bash
# Проверка статуса системы
curl http://localhost:8000/health

# Логи VFS backup системы  
docker logs iskala-new-api --tail 100 | grep VFS

# Git история backup'ов
git log --oneline --grep="VFS auto-backup" -20
```

---

**🎯 VFS Auto Backup v2.0.0 - Ваши данные под надежной защитой!**

*Автоматическое резервное копирование. Git интеграция. Production-ready.*  
*© 2025 ISKALA VFS Backup Team* 