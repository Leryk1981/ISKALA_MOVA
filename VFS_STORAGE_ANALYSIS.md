# 🔍 Анализ физического расположения данных ВФС

## 📊 Результаты диагностики контейнера `iskala-core`

### ✅ **Установленные компоненты ВФС:**
```
/app/frontend/static/js/openwebui_integrated_vfs.js    ✅ (31 KB)
/app/plugins/vfs/openwebui_vfs_plugin.js              ✅ (29 KB)  
/app/backend/data/config/vfs_config.json              ✅ (5 KB)
/app/backend/data/vfs/projects/                       ✅ (пуста)
/app/backend/data/vfs/templates/                      ✅ (пуста)
/app/backend/data/vfs/cache/                          ✅ (пуста)
```

### 🏗️ **Архитектура хранения данных:**

#### **1. Код ВФС использует:**
```javascript
// Из openwebui_integrated_vfs.js (строки 10-15):
class OpenWebUIStorageAdapter {
    constructor() {
        this.storage = typeof openWebUI !== 'undefined' ? openWebUI.storage : null;
        this.prefix = 'vfs_projects/';
        this.metaPrefix = 'vfs_meta/';
        
        // Fallback для тестирования без Open Web UI
        if (!this.storage) {
            this.storage = {
                items: new Map(), // ← Хранение в памяти браузера
                async setItem(key, value) {
                    this.items.set(key, JSON.stringify(value));
                }
            };
        }
    }
}
```

#### **2. Физическое расположение зависит от реализации Storage API:**

**Вариант A: Стандартный Open Web UI**
```
/app/backend/data/db.sqlite3
└── storage_items table
    ├── vfs_projects/ProjectName → JSON data
    └── vfs_meta/ProjectName → Metadata
```

**Вариант B: Кастомный контейнер iskala-core (текущая ситуация)**
```
Браузер localStorage:
├── vfs_projects/VFS_Docs → JSON с файлами проекта
├── vfs_projects/InstagramParser → JSON с файлами проекта  
├── vfs_meta/VFS_Docs → Метаданные проекта
└── vfs_meta/InstagramParser → Метаданные проекта
```

**Вариант C: Файловая система (если реализовано)**
```
/app/backend/data/vfs/
├── projects/
│   ├── VFS_Docs/
│   │   ├── README.md
│   │   ├── COMMANDS.md
│   │   └── EXAMPLES.md
│   └── InstagramParser/
│       ├── instagram_parser.py
│       └── config.json
└── state.json (метаданные всех проектов)
```

### 🎯 **Реальное расположение в iskala-core:**

#### **Наиболее вероятный сценарий:**
```
🌐 Браузер (localStorage/sessionStorage)
├── Key: "vfs_projects/VFS_Docs"
│   Value: {
│     "name": "VFS_Docs",
│     "files": {
│       "README.md": "# ВФС документация...",
│       "COMMANDS.md": "# Справочник команд...",
│       "EXAMPLES.md": "# Примеры использования..."
│     },
│     "created": "2024-01-15T14:35:00Z",
│     "template": "default"
│   }
├── Key: "vfs_meta/VFS_Docs"  
│   Value: {
│     "name": "VFS_Docs",
│     "type": "python",
│     "filesCount": 3,
│     "lastAccessed": "2024-01-15T14:35:00Z"
│   }
└── Key: "vfs_system_state"
    Value: {
      "projects": ["VFS_Docs", "InstagramParser"],
      "activeProject": "VFS_Docs",
      "version": "1.0.0"
    }
```

### 🔍 **Проверка хранения (для пользователя):**

#### **1. В браузере (DevTools → Application → Storage):**
```javascript
// Откройте консоль браузера на http://localhost:8001
console.log("ВФС данные:");
for (let key in localStorage) {
    if (key.startsWith('vfs_')) {
        console.log(key, ":", localStorage[key]);
    }
}
```

#### **2. Через команды ВФС:**
```bash
/vfs diagnose     # Покажет расположение данных
/vfs stats        # Статистика хранилища  
/vfs save         # Создаст backup состояния
```

#### **3. В контейнере (если данные в файлах):**
```bash
docker exec iskala-core find /app -name "*vfs*" -newer /app/backend/data/config/vfs_config.json
```

### ⚠️ **Важные особенности:**

#### **Сохранность данных:**
- **localStorage**: Сохраняется между сессиями браузера ✅
- **sessionStorage**: Удаляется при закрытии вкладки ❌  
- **Memory (Map)**: Удаляется при перезагрузке страницы ❌

#### **Ограничения:**
- **localStorage**: ~5-10 МБ на домен
- **Файловая система**: Ограничена размером контейнера
- **База данных**: Зависит от конфигурации

### 🎯 **Рекомендации:**

1. **Проведите тест создания проекта** для точного определения
2. **Используйте `/export` для резервного копирования**
3. **Проверьте localStorage в браузере** после создания проектов

---
*Анализ выполнен: 2024-08-03 18:40* 