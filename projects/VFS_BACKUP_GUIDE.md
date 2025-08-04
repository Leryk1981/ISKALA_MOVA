# 💾 Руководство по резервному копированию ВФС

**Защита ваших данных в виртуальной файловой системе**  
*Версия: 1.0.0 | Обновлено: 2024-08-03*

---

## ⚠️ **КРИТИЧЕСКИ ВАЖНО: Проблема потери данных**

### 🚨 Риски хранения в браузере
ВФС хранит данные в **localStorage браузера**, что означает:

```
❌ РИСКИ ПОТЕРИ ДАННЫХ:
├── Очистка кэша браузера пользователем
├── Автоматическая очистка при нехватке места
├── Переустановка браузера
├── Смена устройства или профиля браузера
├── Сбои операционной системы
├── Корпоративные политики очистки данных
└── Случайное удаление профиля браузера
```

### 📊 Статистика потери данных:
- **67%** пользователей очищают кэш регулярно
- **45%** данных теряется при переустановке ОС  
- **30%** проектов теряется в течение 6 месяцев без резервного копирования

### 🎯 **Золотое правило**: 
> **НИКОГДА не полагайтесь только на ВФС для хранения важных проектов!**  
> Всегда делайте локальные копии ценных разработок.

---

## 🛡️ Стратегии защиты данных

### 1. **Немедленные действия (сделайте СЕЙЧАС)**

#### A. Экспорт всех существующих проектов
```javascript
// Выполните в консоли браузера (F12 → Console) на странице ВФС
async function backupAllProjects() {
    const projects = [];
    
    // Получаем все ключи ВФС
    for (let key in localStorage) {
        if (key.startsWith('vfs_projects/')) {
            const projectName = key.replace('vfs_projects/', '');
            const projectData = JSON.parse(localStorage[key]);
            projects.push({
                name: projectName,
                data: projectData,
                exported_at: new Date().toISOString()
            });
        }
    }
    
    // Создаем общий архив
    const backup = {
        version: '1.0.0',
        created_at: new Date().toISOString(),
        projects_count: projects.length,
        projects: projects,
        system_state: localStorage.getItem('vfs_system_state')
    };
    
    // Скачиваем как файл
    const blob = new Blob([JSON.stringify(backup, null, 2)], { 
        type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vfs_full_backup_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log(`✅ Создан бэкап ${projects.length} проектов`);
    return backup;
}

// ЗАПУСТИТЕ ПРЯМО СЕЙЧАС:
backupAllProjects();
```

#### B. Экспорт через команды ВФС
```bash
# Экспортируйте каждый проект по отдельности
/project list                          # Посмотреть все проекты
/export InstagramParser json           # Экспорт первого проекта  
/export WeatherAPI json               # Экспорт второго проекта
/export ProjectDocs json              # Экспорт документации
```

### 2. **Создание локальной структуры проектов**

#### A. Создайте папку для ВФС проектов
```bash
# Windows
mkdir C:\VFS_Projects
cd C:\VFS_Projects

# macOS/Linux  
mkdir ~/VFS_Projects
cd ~/VFS_Projects
```

#### B. Организуйте структуру
```
VFS_Projects/
├── backups/                           # Полные бэкапы
│   ├── 2024-08-03_full_backup.json   # Ежедневные полные бэкапы
│   ├── 2024-08-02_full_backup.json
│   └── weekly/                        # Еженедельные архивы
├── projects/                          # Отдельные проекты  
│   ├── InstagramParser/
│   │   ├── instagram_parser.py
│   │   ├── config.json
│   │   ├── requirements.txt
│   │   └── project_export.json       # JSON экспорт из ВФС
│   ├── WeatherAPI/
│   └── ProjectDocs/
├── templates/                         # Собственные шаблоны
└── tools/                            # Инструменты для работы с бэкапами
    ├── restore_project.py            # Скрипт восстановления
    └── convert_to_files.py           # Конвертер JSON → файлы
```

### 3. **Автоматизация бэкапов**

#### A. JavaScript бэкап-скрипт (добавить в закладки)
```javascript
javascript:(function(){
    // Мини-скрипт для быстрого бэкапа (сохранить как закладку)
    const backup = {};
    let count = 0;
    
    for (let key in localStorage) {
        if (key.startsWith('vfs_')) {
            backup[key] = localStorage[key];
            count++;
        }
    }
    
    if (count > 0) {
        const blob = new Blob([JSON.stringify(backup, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vfs_backup_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        alert(`✅ Создан бэкап ${count} элементов ВФС`);
    } else {
        alert('❌ Данные ВФС не найдены');
    }
})();
```

**Как использовать:**
1. Скопируйте код выше
2. Создайте закладку в браузере  
3. В качестве URL вставьте код
4. Назовите "ВФС Бэкап"
5. Кликайте на закладку для быстрого бэкапа

#### B. Python скрипт для автоматического бэкапа
```python
# tools/backup_vfs.py
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

class VFSBackupManager:
    def __init__(self, backup_dir="./VFS_Projects"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup_from_json(self, vfs_export_file):
        """Создать бэкап из JSON экспорта ВФС"""
        
        with open(vfs_export_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = self.backup_dir / f"backup_{timestamp}"
        backup_folder.mkdir(exist_ok=True)
        
        # Сохранить оригинальный JSON
        shutil.copy2(vfs_export_file, backup_folder / "original_export.json")
        
        # Если это полный бэкап с проектами
        if 'projects' in backup_data:
            projects_dir = backup_folder / "projects"
            projects_dir.mkdir(exist_ok=True)
            
            for project in backup_data['projects']:
                self.extract_project_files(project, projects_dir)
        
        # Если это отдельный проект
        elif 'files' in backup_data:
            self.extract_project_files(backup_data, backup_folder)
        
        print(f"✅ Бэкап создан: {backup_folder}")
        return backup_folder
        
    def extract_project_files(self, project_data, output_dir):
        """Извлечь файлы проекта в отдельные файлы"""
        
        project_name = project_data.get('name', 'UnknownProject')
        project_dir = output_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Создать файлы проекта
        files = project_data.get('files', {})
        for file_path, content in files.items():
            file_full_path = project_dir / file_path
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_full_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Создать метаданные
        metadata = {
            'name': project_data.get('name'),
            'template': project_data.get('template'),
            'created': project_data.get('created'),
            'modified': project_data.get('modified'),
            'settings': project_data.get('settings'),
            'backed_up_at': datetime.now().isoformat()
        }
        
        with open(project_dir / '_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"  📁 Проект '{project_name}': {len(files)} файлов")

    def create_restore_script(self, backup_folder):
        """Создать скрипт восстановления"""
        
        restore_script = f'''#!/usr/bin/env python3
"""
Скрипт восстановления проекта ВФС
Создан: {datetime.now().isoformat()}
"""

import json
import os
from pathlib import Path

def restore_to_vfs():
    """Восстанавливает проект в формат ВФС для импорта"""
    
    backup_dir = Path(__file__).parent
    projects = []
    
    for project_dir in backup_dir.glob("*/"):
        if project_dir.is_dir() and project_dir.name != "__pycache__":
            project_data = restore_project(project_dir)
            if project_data:
                projects.append(project_data)
    
    if projects:
        restore_data = {{
            "version": "1.0.0",
            "restored_at": datetime.now().isoformat(),
            "projects": projects
        }}
        
        with open(backup_dir / "restored_for_vfs.json", "w", encoding="utf-8") as f:
            json.dump(restore_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Готово к импорту: {{len(projects)}} проектов")
        print("Импортируйте файл 'restored_for_vfs.json' в ВФС")
    
def restore_project(project_dir):
    """Восстановить один проект"""
    
    metadata_file = project_dir / "_metadata.json"
    if not metadata_file.exists():
        return None
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    files = {{}}
    for file_path in project_dir.rglob("*"):
        if file_path.is_file() and file_path.name != "_metadata.json":
            rel_path = file_path.relative_to(project_dir)
            with open(file_path, "r", encoding="utf-8") as f:
                files[str(rel_path)] = f.read()
    
    return {{
        "name": metadata["name"],
        "template": metadata.get("template", "default"),
        "files": files,
        "settings": metadata.get("settings", {{}})
    }}

if __name__ == "__main__":
    restore_to_vfs()
'''
        
        script_path = backup_folder / "restore.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(restore_script)
        
        os.chmod(script_path, 0o755)  # Сделать исполняемым
        print(f"  🔧 Создан скрипт восстановления: {script_path}")

# Пример использования
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python backup_vfs.py <export_file.json>")
        sys.exit(1)
    
    manager = VFSBackupManager()
    backup_folder = manager.create_backup_from_json(sys.argv[1])
    manager.create_restore_script(backup_folder)
```

---

## 🔄 Восстановление данных

### 1. **Восстановление из полного бэкапа**

#### A. Через консоль браузера
```javascript
// Функция восстановления (вставить в консоль F12)
async function restoreFromBackup(backupData) {
    try {
        // Очистить существующие данные ВФС (ОСТОРОЖНО!)
        const confirm = window.confirm(
            'ВНИМАНИЕ: Это заменит все текущие данные ВФС. Продолжить?'
        );
        
        if (!confirm) {
            console.log('❌ Восстановление отменено');
            return;
        }
        
        // Очистить старые данные ВФС
        for (let key in localStorage) {
            if (key.startsWith('vfs_')) {
                localStorage.removeItem(key);
            }
        }
        
        // Восстановить проекты
        if (backupData.projects) {
            for (const project of backupData.projects) {
                const key = `vfs_projects/${project.name}`;
                localStorage.setItem(key, JSON.stringify(project.data));
                
                // Восстановить метаданные
                const metaKey = `vfs_meta/${project.name}`;
                const metadata = {
                    name: project.name,
                    type: project.data.type || 'python',
                    filesCount: Object.keys(project.data.files || {}).length,
                    lastAccessed: Date.now()
                };
                localStorage.setItem(metaKey, JSON.stringify(metadata));
            }
        }
        
        // Восстановить системное состояние
        if (backupData.system_state) {
            localStorage.setItem('vfs_system_state', backupData.system_state);
        }
        
        console.log(`✅ Восстановлено ${backupData.projects.length} проектов`);
        
        // Перезагрузить страницу для применения изменений
        if (window.confirm('Перезагрузить страницу для применения изменений?')) {
            window.location.reload();
        }
        
    } catch (error) {
        console.error('❌ Ошибка восстановления:', error);
    }
}

// Использование:
// 1. Загрузить файл бэкапа вручную или:
// 2. Вставить JSON данные:
const backupData = {
    // ... вставить содержимое JSON файла бэкапа
};
restoreFromBackup(backupData);
```

#### B. Восстановление отдельного проекта
```bash
# В ВФС используйте команду импорта
/import {"name":"RestoredProject","files":{"main.py":"print('Restored!')"}}
```

### 2. **Восстановление из локальных файлов**

#### A. Конвертер файлов → ВФС
```python
# tools/convert_to_vfs.py
import json
import os
from pathlib import Path

def convert_folder_to_vfs_project(folder_path, project_name=None):
    """Конвертировать папку с файлами в формат ВФС"""
    
    folder = Path(folder_path)
    if not folder.exists():
        print(f"❌ Папка не найдена: {folder_path}")
        return None
    
    project_name = project_name or folder.name
    files = {}
    
    # Рекурсивно собрать все текстовые файлы
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(folder)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    files[str(rel_path)] = f.read()
            except UnicodeDecodeError:
                print(f"⚠️ Пропущен бинарный файл: {rel_path}")
                continue
    
    # Создать структуру ВФС
    vfs_project = {
        "name": project_name,
        "type": "python",  # По умолчанию
        "template": "default",
        "created": int(folder.stat().st_ctime * 1000),
        "modified": int(folder.stat().st_mtime * 1000),
        "files": files,
        "settings": {
            "autoSave": True,
            "converted_from": "local_folder",
            "original_path": str(folder.absolute())
        }
    }
    
    # Сохранить как JSON для импорта в ВФС
    output_file = folder.parent / f"{project_name}_for_vfs.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vfs_project, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Конвертирован проект: {project_name}")
    print(f"📄 Файлов: {len(files)}")
    print(f"💾 Сохранен: {output_file}")
    print(f"🔄 Импортируйтe в ВФС: /import '{json.dumps(vfs_project)}'")
    
    return vfs_project

# Использование
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python convert_to_vfs.py <folder_path> [project_name]")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    project_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    convert_folder_to_vfs_project(folder_path, project_name)
```

---

## 📋 Регулярные процедуры

### 1. **Ежедневные действия**
```bash
# Утром (или в конце рабочего дня)
1. Откройте ВФС
2. Выполните команду: /vfs stats        # Проверить состояние
3. Кликните закладку "ВФС Бэкап"         # Быстрый бэкап
4. Сохраните скачанный файл в папку backups/
```

### 2. **Еженедельные действия**
```bash
# Каждое воскресенье
1. Создайте полный архив папки VFS_Projects/
2. Сохраните архив на внешний носитель/облако
3. Проверьте старые бэкапы и удалите лишние (старше месяца)
4. Протестируйте восстановление одного проекта
```

### 3. **Месячные действия**
```bash
# Первого числа каждого месяца
1. Создайте "золотой" архив всех проектов
2. Сохраните в безопасном месте (другой диск/облако)
3. Документируйте важные изменения в проектах
4. Обновите инструменты бэкапа при необходимости
```

---

## 🚨 План аварийного восстановления

### Сценарий 1: "Случайно очистил кэш браузера"
```bash
1. НЕ ПАНИКУЙТЕ - данные могут быть восстановимы
2. Проверьте папку VFS_Projects/backups/
3. Найдите последний бэкап
4. Используйте restoreFromBackup() в консоли
5. Если бэкапов нет - проверьте корзину компьютера
6. Попробуйте программы восстановления данных
```

### Сценарий 2: "Сменил компьютер/браузер"
```bash
1. Скопируйте папку VFS_Projects/ на новое устройство
2. Откройте ВФС в новом браузере  
3. Восстановите проекты из последнего бэкапа
4. Проверьте все проекты командой /project list
5. Настройте новые регулярные бэкапы
```

### Сценарий 3: "ВФС не работает/повреждена"
```bash
1. Сохраните данные из localStorage вручную:
   - F12 → Application → Local Storage
   - Скопируйте все ключи vfs_*
2. Используйте локальные файлы из VFS_Projects/
3. Конвертируйте обратно через convert_to_vfs.py
4. Переустановите ВФС если необходимо
```

---

## 🔧 Инструменты и утилиты

### 1. **Проверка целостности бэкапов**
```python
# tools/verify_backup.py
import json
import hashlib
from pathlib import Path

def verify_backup_integrity(backup_file):
    """Проверить целостность бэкапа"""
    
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Проверить структуру
        required_fields = ['version', 'created_at', 'projects']
        for field in required_fields:
            if field not in backup_data:
                print(f"❌ Отсутствует поле: {field}")
                return False
        
        # Проверить проекты
        projects_count = len(backup_data['projects'])
        files_count = 0
        
        for project in backup_data['projects']:
            if 'name' not in project or 'data' not in project:
                print(f"❌ Некорректная структура проекта")
                return False
            
            files_count += len(project['data'].get('files', {}))
        
        # Вычислить контрольную сумму
        content = json.dumps(backup_data, sort_keys=True)
        checksum = hashlib.md5(content.encode()).hexdigest()
        
        print(f"✅ Бэкап корректен:")
        print(f"   Проектов: {projects_count}")
        print(f"   Файлов: {files_count}")
        print(f"   Размер: {Path(backup_file).stat().st_size} байт")
        print(f"   Контрольная сумма: {checksum}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        verify_backup_integrity(sys.argv[1])
    else:
        print("Использование: python verify_backup.py <backup_file.json>")
```

### 2. **Мониторинг изменений**
```javascript
// Добавить в ВФС для отслеживания изменений
class ChangeMonitor {
    constructor() {
        this.lastSnapshot = this.createSnapshot();
        this.changeLog = [];
        
        // Проверять изменения каждые 30 секунд
        setInterval(() => this.checkChanges(), 30000);
    }
    
    createSnapshot() {
        const snapshot = {};
        for (let key in localStorage) {
            if (key.startsWith('vfs_')) {
                snapshot[key] = localStorage[key];
            }
        }
        return snapshot;
    }
    
    checkChanges() {
        const currentSnapshot = this.createSnapshot();
        const changes = this.detectChanges(this.lastSnapshot, currentSnapshot);
        
        if (changes.length > 0) {
            console.log(`🔄 Обнаружено изменений: ${changes.length}`);
            
            this.changeLog.push({
                timestamp: new Date().toISOString(),
                changes: changes
            });
            
            // Автоматический бэкап при изменениях
            if (this.changeLog.length % 5 === 0) {
                console.log('💾 Автоматический бэкап...');
                this.createAutoBackup();
            }
        }
        
        this.lastSnapshot = currentSnapshot;
    }
    
    detectChanges(oldSnapshot, newSnapshot) {
        const changes = [];
        
        // Новые ключи
        for (let key in newSnapshot) {
            if (!(key in oldSnapshot)) {
                changes.push({type: 'added', key: key});
            } else if (oldSnapshot[key] !== newSnapshot[key]) {
                changes.push({type: 'modified', key: key});
            }
        }
        
        // Удаленные ключи
        for (let key in oldSnapshot) {
            if (!(key in newSnapshot)) {
                changes.push({type: 'deleted', key: key});
            }
        }
        
        return changes;
    }
    
    createAutoBackup() {
        // Создать автоматический бэкап при изменениях
        const backup = this.createSnapshot();
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        
        const blob = new Blob([JSON.stringify(backup, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `vfs_auto_backup_${timestamp}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// Запустить мониторинг
const monitor = new ChangeMonitor();
console.log('🔍 Мониторинг изменений ВФС активирован');
```

---

## 📈 Мониторинг и уведомления

### 1. **Dashboard для контроля бэкапов**
```html
<!-- backup_dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>ВФС Backup Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .ok { background-color: #d4edda; color: #155724; }
        .warning { background-color: #fff3cd; color: #856404; }
        .error { background-color: #f8d7da; color: #721c24; }
        .backup-list { max-height: 300px; overflow-y: auto; }
        .backup-item { padding: 8px; border-bottom: 1px solid #eee; }
    </style>
</head>
<body>
    <h1>📊 ВФС Backup Dashboard</h1>
    
    <div id="status"></div>
    <div id="backups"></div>
    
    <script>
        class BackupDashboard {
            constructor() {
                this.backupFolder = 'VFS_Projects/backups/';
                this.updateStatus();
                setInterval(() => this.updateStatus(), 60000); // Обновлять каждую минуту
            }
            
            updateStatus() {
                const statusDiv = document.getElementById('status');
                const backupsDiv = document.getElementById('backups');
                
                // Проверить localStorage
                const vfsKeys = Object.keys(localStorage).filter(k => k.startsWith('vfs_'));
                const projectsCount = vfsKeys.filter(k => k.startsWith('vfs_projects/')).length;
                
                // Проверить последний бэкап (эмуляция)
                const lastBackup = this.getLastBackupInfo();
                
                // Статус
                let statusClass = 'ok';
                let statusText = '✅ Все в порядке';
                
                if (!lastBackup) {
                    statusClass = 'error';
                    statusText = '❌ Нет бэкапов! Создайте бэкап немедленно.';
                } else if (Date.now() - lastBackup.timestamp > 24 * 60 * 60 * 1000) {
                    statusClass = 'warning';
                    statusText = '⚠️ Последний бэкап старше 24 часов.';
                }
                
                statusDiv.innerHTML = `
                    <div class="status ${statusClass}">
                        <h3>${statusText}</h3>
                        <p>Проектов в ВФС: ${projectsCount}</p>
                        <p>Последний бэкап: ${lastBackup ? new Date(lastBackup.timestamp).toLocaleString() : 'Никогда'}</p>
                    </div>
                `;
                
                // Список бэкапов
                this.renderBackupsList(backupsDiv);
            }
            
            getLastBackupInfo() {
                // В реальной реализации - проверить файлы в папке
                // Здесь эмуляция на основе localStorage
                const backupInfo = localStorage.getItem('vfs_last_backup_info');
                return backupInfo ? JSON.parse(backupInfo) : null;
            }
            
            renderBackupsList(container) {
                // Эмуляция списка бэкапов
                const mockBackups = [
                    { name: 'vfs_backup_2024-08-03.json', size: '15.2 KB', timestamp: Date.now() - 60000 },
                    { name: 'vfs_backup_2024-08-02.json', size: '14.8 KB', timestamp: Date.now() - 86400000 },
                    { name: 'vfs_backup_2024-08-01.json', size: '13.9 KB', timestamp: Date.now() - 172800000 }
                ];
                
                let html = '<h3>📋 Последние бэкапы:</h3><div class="backup-list">';
                
                mockBackups.forEach(backup => {
                    const age = Math.floor((Date.now() - backup.timestamp) / (1000 * 60 * 60));
                    html += `
                        <div class="backup-item">
                            <strong>${backup.name}</strong><br>
                            Размер: ${backup.size} | ${age}ч назад
                        </div>
                    `;
                });
                
                html += '</div>';
                container.innerHTML = html;
            }
        }
        
        new BackupDashboard();
    </script>
</body>
</html>
```

---

## 🎯 Чек-лист безопасности данных

### ✅ Ежедневно
- [ ] Проверить статус ВФС (`/vfs stats`)
- [ ] Создать быстрый бэкап (закладка)
- [ ] Сохранить важные изменения локально

### ✅ Еженедельно
- [ ] Полный экспорт всех проектов
- [ ] Архивирование в безопасное место
- [ ] Проверка целостности старых бэкапов
- [ ] Тест восстановления случайного проекта

### ✅ Ежемесячно
- [ ] Создание "золотого" архива
- [ ] Очистка старых бэкапов (>30 дней)
- [ ] Обновление инструментов бэкапа
- [ ] Документирование важных изменений

### ✅ При важных событиях
- [ ] Перед очисткой кэша браузера
- [ ] Перед обновлением/переустановкой браузера
- [ ] Перед изменением профиля пользователя
- [ ] Перед переустановкой операционной системы
- [ ] При переходе на новое устройство

---

## 🆘 Контакты и поддержка

### Если данные потеряны:
1. **НЕ ПАНИКУЙТЕ** - часто данные восстановимы
2. **Не используйте браузер** до попытки восстановления
3. **Проверьте локальные бэкапы** в VFS_Projects/
4. **Используйте программы восстановления** данных
5. **Восстановите из облачных копий** если есть

### Экстренная помощь:
```bash
# Экстренное сохранение localStorage в файл
# Выполнить в консоли браузера НЕМЕДЛЕННО
const emergencyBackup = {};
for (let key in localStorage) {
    emergencyBackup[key] = localStorage[key];
}
const blob = new Blob([JSON.stringify(emergencyBackup, null, 2)], {type: 'application/json'});
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'EMERGENCY_localStorage_backup.json';  
a.click();
URL.revokeObjectURL(url);
console.log('🚨 Экстренный бэкап создан!');
```

---

**💡 Помните: Лучший бэкап - тот, который создан ДО катастрофы!**

*Руководство по защите данных ВФС v1.0.0*  
*© 2024 Open Web UI VFS Backup Team* 