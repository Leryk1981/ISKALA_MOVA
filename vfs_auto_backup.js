/**
 * VFS Auto Backup Integration
 * Автоматически сохраняет VFS данные в Git репозиторий через API
 */

class VFSAutoBackup {
    constructor(options = {}) {
        this.apiEndpoint = options.apiEndpoint || '/api/v1/vfs/backup';
        this.backupInterval = options.backupInterval || 30 * 60 * 1000; // 30 минут
        this.autoBackupEnabled = options.autoBackupEnabled || true;
        this.debug = options.debug || false;
        
        this.init();
    }
    
    init() {
        this.log('VFS Auto Backup initialized');
        
        if (this.autoBackupEnabled) {
            this.setupAutoBackup();
        }
        
        this.setupEventListeners();
    }
    
    setupAutoBackup() {
        // Периодический backup
        setInterval(() => {
            this.createBackup('scheduled');
        }, this.backupInterval);
        
        this.log(`Auto backup scheduled every ${this.backupInterval / 1000 / 60} minutes`);
    }
    
    setupEventListeners() {
        // Backup при закрытии страницы
        window.addEventListener('beforeunload', () => {
            this.createBackup('page_close');
        });
        
        // Backup при потере фокуса (переключение вкладки)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.createBackup('focus_lost');
            }
        });
        
        // Backup при изменении VFS данных (если есть события)
        if (window.vfs && window.vfs.addEventListener) {
            window.vfs.addEventListener('dataChanged', () => {
                this.debounceBackup('data_changed');
            });
        }
    }
    
    debounceBackup(reason) {
        // Предотвращаем слишком частые backup'ы
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.createBackup(reason);
        }, 5000); // 5 секунд задержки
    }
    
    async createBackup(reason = 'manual') {
        try {
            const vfsData = this.extractVFSData();
            
            if (!vfsData || Object.keys(vfsData).length === 0) {
                this.log('No VFS data to backup');
                return;
            }
            
            const backupPayload = {
                reason,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                url: window.location.href,
                vfs_data: vfsData
            };
            
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(backupPayload)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.log(`Backup successful: ${result.backup_file}`, result);
                
                // Показываем уведомление пользователю
                this.showNotification('VFS данные сохранены в репозиторий', 'success');
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
        } catch (error) {
            this.log(`Backup failed: ${error.message}`, error);
            this.showNotification('Ошибка сохранения VFS данных', 'error');
        }
    }
    
    extractVFSData() {
        const vfsData = {};
        
        // Извлекаем данные из localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('vfs_')) {
                try {
                    const value = localStorage.getItem(key);
                    vfsData[key] = JSON.parse(value);
                } catch (e) {
                    // Если не JSON, сохраняем как строку
                    vfsData[key] = localStorage.getItem(key);
                }
            }
        }
        
        // Добавляем метаданные
        vfsData._metadata = {
            extraction_time: new Date().toISOString(),
            browser: navigator.userAgent,
            url: window.location.href,
            storage_size: JSON.stringify(vfsData).length
        };
        
        return vfsData;
    }
    
    async listBackups() {
        try {
            const response = await fetch('/api/v1/vfs/backups');
            if (response.ok) {
                const result = await response.json();
                return result.backups;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        } catch (error) {
            this.log(`Failed to list backups: ${error.message}`, error);
            return [];
        }
    }
    
    showNotification(message, type = 'info') {
        // Простое уведомление через console
        if (this.debug) {
            console.log(`[VFS Backup] ${message}`);
        }
        
        // Можно добавить toast уведомления
        if (window.showToast) {
            window.showToast(message, type);
        }
    }
    
    log(message, data = null) {
        if (this.debug) {
            console.log(`[VFS Auto Backup] ${message}`, data);
        }
    }
    
    // Публичные методы
    async manualBackup() {
        return await this.createBackup('manual');
    }
    
    enableAutoBackup() {
        this.autoBackupEnabled = true;
        this.setupAutoBackup();
        this.log('Auto backup enabled');
    }
    
    disableAutoBackup() {
        this.autoBackupEnabled = false;
        this.log('Auto backup disabled');
    }
    
    setBackupInterval(minutes) {
        this.backupInterval = minutes * 60 * 1000;
        if (this.autoBackupEnabled) {
            this.setupAutoBackup();
        }
        this.log(`Backup interval set to ${minutes} minutes`);
    }
}

// Глобальная инициализация
window.VFSAutoBackup = VFSAutoBackup;

// Автоматический запуск если в Open Web UI
if (window.location.href.includes('open-webui') || window.localStorage.getItem('vfs_projects')) {
    window.vfsBackup = new VFSAutoBackup({
        debug: true,
        autoBackupEnabled: true,
        backupInterval: 15 * 60 * 1000 // 15 минут
    });
    
    // Добавляем команды в консоль
    window.vfsBackupNow = () => window.vfsBackup.manualBackup();
    window.vfsListBackups = () => window.vfsBackup.listBackups();
    
    console.log('🔄 VFS Auto Backup активирован');
    console.log('Команды: vfsBackupNow(), vfsListBackups()');
} 