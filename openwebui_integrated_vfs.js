/**
 * Интегрированная виртуальная файловая система для Open Web UI
 * Использует встроенные API: Storage, Workspace, Settings, Templates
 */

// =============================================================================
// АДАПТЕР ДЛЯ STORAGE API
// =============================================================================

class OpenWebUIStorageAdapter {
    constructor() {
        this.storage = typeof openWebUI !== 'undefined' ? openWebUI.storage : null;
        this.prefix = 'vfs_projects/';
        this.metaPrefix = 'vfs_meta/';
        
        // Fallback для тестирования без Open Web UI
        if (!this.storage) {
            this.storage = {
                items: new Map(),
                async setItem(key, value) {
                    this.items.set(key, JSON.stringify(value));
                    return true;
                },
                async getItem(key) {
                    const value = this.items.get(key);
                    return value ? JSON.parse(value) : null;
                },
                async removeItem(key) {
                    return this.items.delete(key);
                },
                async keys(prefix = '') {
                    return Array.from(this.items.keys()).filter(key => key.startsWith(prefix));
                },
                async clear() {
                    this.items.clear();
                }
            };
        }
    }

    async saveProject(name, projectData) {
        const key = `${this.prefix}${name}`;
        const metaKey = `${this.metaPrefix}${name}`;
        
        // Сохраняем данные проекта
        await this.storage.setItem(key, {
            name,
            files: projectData.files || {},
            settings: projectData.settings || {},
            created: projectData.created || Date.now(),
            modified: Date.now(),
            version: '1.0'
        });
        
        // Сохраняем метаданные
        await this.storage.setItem(metaKey, {
            name,
            type: projectData.type || 'python',
            template: projectData.template || 'default',
            filesCount: Object.keys(projectData.files || {}).length,
            size: JSON.stringify(projectData).length,
            lastAccessed: Date.now()
        });
        
        return true;
    }

    async loadProject(name) {
        const key = `${this.prefix}${name}`;
        const project = await this.storage.getItem(key);
        
        if (project) {
            // Обновляем время последнего доступа
            const metaKey = `${this.metaPrefix}${name}`;
            const meta = await this.storage.getItem(metaKey);
            if (meta) {
                meta.lastAccessed = Date.now();
                await this.storage.setItem(metaKey, meta);
            }
        }
        
        return project;
    }

    async deleteProject(name) {
        const key = `${this.prefix}${name}`;
        const metaKey = `${this.metaPrefix}${name}`;
        
        await this.storage.removeItem(key);
        await this.storage.removeItem(metaKey);
        
        return true;
    }

    async listProjects() {
        const keys = await this.storage.keys(this.prefix);
        const projects = [];
        
        for (const key of keys) {
            const name = key.replace(this.prefix, '');
            const meta = await this.storage.getItem(`${this.metaPrefix}${name}`);
            projects.push(meta || { name, type: 'unknown' });
        }
        
        return projects.sort((a, b) => b.lastAccessed - a.lastAccessed);
    }

    async searchProjects(query) {
        const projects = await this.listProjects();
        return projects.filter(project => 
            project.name.toLowerCase().includes(query.toLowerCase()) ||
            (project.type && project.type.toLowerCase().includes(query.toLowerCase()))
        );
    }
}

// =============================================================================
// ИНТЕГРИРОВАННАЯ ВФС
// =============================================================================

class IntegratedVFS {
    constructor() {
        this.storage = new OpenWebUIStorageAdapter();
        this.activeProject = null;
        this.templates = this._initTemplates();
        this.settings = this._initSettings();
    }

    _initTemplates() {
        return {
            'default': {
                name: 'Стандартный проект',
                description: 'Базовая структура Python проекта',
                type: 'python',
                files: {
                    'main.py': `#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной скрипт проекта
"""

def main():
    print("Hello from Open Web UI Integrated VFS!")
    
if __name__ == "__main__":
    main()
`,
                    'requirements.txt': `# Зависимости проекта
requests>=2.28.0
beautifulsoup4>=4.11.0
`,
                    'config.json': `{
    "project": {
        "name": "{{PROJECT_NAME}}",
        "version": "1.0.0",
        "description": "Проект, созданный в Open Web UI"
    },
    "settings": {
        "debug": true,
        "timeout": 30
    }
}`,
                    'README.md': `# {{PROJECT_NAME}}

Проект, созданный в Open Web UI с интегрированной ВФС.

## Установка

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Использование

\`\`\`bash
python main.py
\`\`\`
`
                },
                settings: {
                    pythonVersion: '3.9',
                    autoSave: true
                }
            },

            'instagram_parser': {
                name: 'Instagram Parser',
                description: 'Шаблон для парсинга Instagram',
                type: 'python',
                files: {
                    'instagram_parser.py': `import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List, Optional

class InstagramParser:
    """Парсер для Instagram через Open Web UI"""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session = requests.Session()
        self.base_url = "https://www.instagram.com"
        
        # Заголовки для имитации браузера
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        if session_id:
            self.session.cookies.set('sessionid', session_id)
    
    def get_user_info(self, username: str) -> Dict:
        """Получить информацию о пользователе"""
        url = f"{self.base_url}/{username}/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            # Простой парсинг через BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Извлекаем данные (упрощенный пример)
            return {
                'username': username,
                'url': url,
                'status': 'success',
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'username': username,
                'error': str(e),
                'status': 'error',
                'timestamp': time.time()
            }
    
    def parse_posts(self, username: str, limit: int = 10) -> List[Dict]:
        """Парсинг постов пользователя"""
        posts = []
        
        # Здесь будет логика парсинга постов
        # Пока возвращаем mock-данные
        for i in range(min(limit, 5)):
            posts.append({
                'id': f'post_{i}',
                'username': username,
                'caption': f'Post caption {i}',
                'likes': 100 + i * 10,
                'timestamp': time.time() - i * 3600
            })
        
        return posts

if __name__ == "__main__":
    parser = InstagramParser()
    
    # Пример использования
    username = "test_user"
    user_info = parser.get_user_info(username)
    print(f"User info: {json.dumps(user_info, indent=2)}")
    
    posts = parser.parse_posts(username, 3)
    print(f"Posts: {json.dumps(posts, indent=2)}")
`,
                    'config.json': `{
    "instagram": {
        "delay_between_requests": 2,
        "max_retries": 3,
        "timeout": 30,
        "user_agents": [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
    },
    "output": {
        "format": "json",
        "save_to_file": true,
        "filename_template": "instagram_{username}_{timestamp}.json"
    }
}`,
                    'requirements.txt': `requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
`,
                    'utils.py': `import time
import json
from datetime import datetime

def save_data(data, filename=None):
    """Сохранить данные в JSON файл"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"instagram_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Данные сохранены в {filename}")
    return filename

def rate_limit(delay=2):
    """Ограничение скорости запросов"""
    time.sleep(delay)

def format_timestamp(timestamp):
    """Форматирование timestamp в читаемый вид"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
`
                },
                settings: {
                    pythonVersion: '3.9',
                    packages: ['requests', 'beautifulsoup4', 'selenium'],
                    autoSave: true
                }
            },

            'api_client': {
                name: 'API Client',
                description: 'Универсальный клиент для работы с API',
                type: 'python',
                files: {
                    'api_client.py': `import requests
import json
from typing import Dict, Any, Optional
from urllib.parse import urljoin

class APIClient:
    """Универсальный клиент для работы с REST API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Настройка аутентификации
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        # Базовые заголовки
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'OpenWebUI-VFS-Client/1.0'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполнить HTTP запрос"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json() if response.content else None,
                'status_code': response.status_code
            }
            
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None)
            }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET запрос"""
        return self._make_request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST запрос"""
        return self._make_request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PUT запрос"""
        return self._make_request('PUT', endpoint, json=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """DELETE запрос"""
        return self._make_request('DELETE', endpoint)

if __name__ == "__main__":
    # Пример использования
    client = APIClient('https://api.example.com')
    
    # GET запрос
    result = client.get('/users')
    if result['success']:
        print(f"Users: {result['data']}")
    else:
        print(f"Error: {result['error']}")
`
                },
                settings: {
                    pythonVersion: '3.9',
                    packages: ['requests'],
                    autoSave: true
                }
            }
        };
    }

    _initSettings() {
        return {
            python: {
                version: '3.9',
                defaultPackages: ['requests', 'beautifulsoup4', 'lxml', 'selenium'],
                virtualEnv: true
            },
            editor: {
                autoSave: true,
                autoIndent: true,
                fontSize: 14,
                theme: 'dark'
            },
            compilation: {
                outputFormat: 'app',
                includeRequirements: true,
                optimize: false
            }
        };
    }

    // =============================================================================
    // УПРАВЛЕНИЕ ПРОЕКТАМИ
    // =============================================================================

    async createProject(name, templateName = 'default') {
        if (!this.templates[templateName]) {
            throw new Error(`Template '${templateName}' not found`);
        }

        const template = this.templates[templateName];
        const files = {};

        // Обработка шаблонов файлов (замена переменных)
        for (const [filePath, content] of Object.entries(template.files)) {
            files[filePath] = content.replace(/\{\{PROJECT_NAME\}\}/g, name);
        }

        const projectData = {
            name,
            type: template.type,
            template: templateName,
            files,
            settings: { ...template.settings },
            created: Date.now()
        };

        await this.storage.saveProject(name, projectData);
        this.activeProject = name;

        return {
            success: true,
            project: name,
            template: templateName,
            filesCreated: Object.keys(files).length,
            message: `Проект '${name}' создан успешно`
        };
    }

    async deleteProject(name) {
        const project = await this.storage.loadProject(name);
        if (!project) {
            throw new Error(`Project '${name}' not found`);
        }

        await this.storage.deleteProject(name);

        if (this.activeProject === name) {
            this.activeProject = null;
        }

        return {
            success: true,
            message: `Проект '${name}' удален`
        };
    }

    async switchProject(name) {
        const project = await this.storage.loadProject(name);
        if (!project) {
            throw new Error(`Project '${name}' not found`);
        }

        this.activeProject = name;

        return {
            success: true,
            activeProject: name,
            project: project,
            message: `Переключились на проект '${name}'`
        };
    }

    async listProjects() {
        const projects = await this.storage.listProjects();

        return {
            success: true,
            projects: projects.map(p => ({
                ...p,
                isActive: p.name === this.activeProject
            })),
            activeProject: this.activeProject,
            totalCount: projects.length
        };
    }

    async getProjectInfo(name = null) {
        const projectName = name || this.activeProject;
        if (!projectName) {
            throw new Error('No active project');
        }

        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        return {
            success: true,
            project: {
                ...project,
                isActive: projectName === this.activeProject,
                filesCount: Object.keys(project.files).length,
                size: JSON.stringify(project).length
            }
        };
    }

    // =============================================================================
    // УПРАВЛЕНИЕ ФАЙЛАМИ
    // =============================================================================

    async createFile(projectName, filePath, content = '') {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        project.files[filePath] = content;
        project.modified = Date.now();

        await this.storage.saveProject(projectName, project);

        return {
            success: true,
            path: filePath,
            size: content.length,
            message: `Файл '${filePath}' создан в проекте '${projectName}'`
        };
    }

    async readFile(projectName, filePath) {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        if (!project.files[filePath]) {
            throw new Error(`File '${filePath}' not found in project '${projectName}'`);
        }

        const content = project.files[filePath];

        return {
            success: true,
            path: filePath,
            content: content,
            size: content.length,
            lines: content.split('\n').length
        };
    }

    async updateFile(projectName, filePath, content) {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        if (!project.files[filePath]) {
            throw new Error(`File '${filePath}' not found in project '${projectName}'`);
        }

        const oldSize = project.files[filePath].length;
        project.files[filePath] = content;
        project.modified = Date.now();

        await this.storage.saveProject(projectName, project);

        return {
            success: true,
            path: filePath,
            oldSize: oldSize,
            newSize: content.length,
            sizeDiff: content.length - oldSize,
            message: `Файл '${filePath}' обновлен`
        };
    }

    async deleteFile(projectName, filePath) {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        if (!project.files[filePath]) {
            throw new Error(`File '${filePath}' not found in project '${projectName}'`);
        }

        delete project.files[filePath];
        project.modified = Date.now();

        await this.storage.saveProject(projectName, project);

        return {
            success: true,
            path: filePath,
            message: `Файл '${filePath}' удален из проекта '${projectName}'`
        };
    }

    async listFiles(projectName) {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        const files = Object.entries(project.files).map(([path, content]) => ({
            path: path,
            size: content.length,
            extension: path.split('.').pop() || '',
            lines: content.split('\n').length
        }));

        const stats = {
            totalFiles: files.length,
            totalSize: files.reduce((sum, f) => sum + f.size, 0),
            extensions: files.reduce((acc, f) => {
                acc[f.extension] = (acc[f.extension] || 0) + 1;
                return acc;
            }, {})
        };

        return {
            success: true,
            project: projectName,
            files: files,
            stats: stats
        };
    }

    // =============================================================================
    // СИСТЕМНЫЕ ФУНКЦИИ
    // =============================================================================

    async exportProject(projectName, format = 'json') {
        const project = await this.storage.loadProject(projectName);
        if (!project) {
            throw new Error(`Project '${projectName}' not found`);
        }

        if (format === 'json') {
            return {
                success: true,
                format: 'json',
                data: JSON.stringify(project, null, 2),
                filename: `${projectName}_export.json`
            };
        }

        if (format === 'zip') {
            // Здесь будет логика создания ZIP архива
            return {
                success: true,
                format: 'zip',
                message: 'ZIP export будет реализован в следующей версии',
                files: Object.keys(project.files)
            };
        }

        throw new Error(`Unsupported export format: ${format}`);
    }

    async importProject(projectData, format = 'json') {
        let project;

        if (format === 'json') {
            project = typeof projectData === 'string' ? JSON.parse(projectData) : projectData;
        } else {
            throw new Error(`Unsupported import format: ${format}`);
        }

        if (!project.name) {
            throw new Error('Project name is required');
        }

        await this.storage.saveProject(project.name, project);

        return {
            success: true,
            project: project.name,
            filesImported: Object.keys(project.files || {}).length,
            message: `Проект '${project.name}' импортирован успешно`
        };
    }

    async getSystemStats() {
        const projects = await this.storage.listProjects();
        let totalFiles = 0;
        let totalSize = 0;

        for (const projectMeta of projects) {
            const project = await this.storage.loadProject(projectMeta.name);
            if (project) {
                totalFiles += Object.keys(project.files).length;
                totalSize += JSON.stringify(project).length;
            }
        }

        return {
            success: true,
            stats: {
                projectsCount: projects.length,
                totalFiles: totalFiles,
                totalSize: totalSize,
                activeProject: this.activeProject,
                availableTemplates: Object.keys(this.templates),
                storageType: 'OpenWebUI Storage API'
            },
            projects: projects
        };
    }

    async saveSystemState() {
        const projects = await this.storage.listProjects();
        const state = {
            version: '1.0',
            savedAt: Date.now(),
            activeProject: this.activeProject,
            projects: projects,
            settings: this.settings
        };

        // Сохраняем состояние в специальный ключ
        await this.storage.storage.setItem('vfs_system_state', state);

        return {
            success: true,
            message: 'Состояние системы сохранено',
            projectsCount: projects.length,
            stateSize: JSON.stringify(state).length
        };
    }

    async loadSystemState() {
        const state = await this.storage.storage.getItem('vfs_system_state');
        
        if (!state) {
            throw new Error('No saved system state found');
        }

        this.activeProject = state.activeProject;
        if (state.settings) {
            this.settings = { ...this.settings, ...state.settings };
        }

        return {
            success: true,
            message: 'Состояние системы восстановлено',
            projectsLoaded: state.projects.length,
            activeProject: this.activeProject,
            savedAt: state.savedAt
        };
    }
}

// =============================================================================
// ЭКСПОРТ ДЛЯ ИСПОЛЬЗОВАНИЯ
// =============================================================================

// Для использования в браузере
if (typeof window !== 'undefined') {
    window.IntegratedVFS = IntegratedVFS;
}

// Для использования в Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { IntegratedVFS, OpenWebUIStorageAdapter };
}

// =============================================================================
// ДЕМОНСТРАЦИЯ ИСПОЛЬЗОВАНИЯ
// =============================================================================

async function demonstrateVFS() {
    console.log('🚀 Демонстрация интегрированной ВФС для Open Web UI');
    console.log('=' * 60);

    const vfs = new IntegratedVFS();

    try {
        // 1. Создание проекта Instagram Parser
        console.log('\n1. Создаем проект Instagram Parser:');
        const createResult = await vfs.createProject('InstagramParser', 'instagram_parser');
        console.log('✅', createResult.message);
        console.log(`📁 Создано файлов: ${createResult.filesCreated}`);

        // 2. Список проектов
        console.log('\n2. Список проектов:');
        const listResult = await vfs.listProjects();
        listResult.projects.forEach(project => {
            const status = project.isActive ? '🟢 (активный)' : '⚪';
            console.log(`  ${status} ${project.name} - тип: ${project.type}, файлов: ${project.filesCount || 0}`);
        });

        // 3. Создание дополнительного файла
        console.log('\n3. Создаем дополнительный файл:');
        const fileContent = `# Дополнительные утилиты для парсера Instagram

import json
from datetime import datetime

def log_activity(action, details):
    """Логирование активности парсера"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'action': action,
        'details': details
    }
    print(f"[{timestamp}] {action}: {details}")
    return log_entry

def validate_username(username):
    """Валидация имени пользователя Instagram"""
    if not username or len(username) < 1:
        return False
    
    # Простая валидация
    return username.replace('_', '').replace('.', '').isalnum()
`;

        const fileResult = await vfs.createFile('InstagramParser', 'instagram_utils.py', fileContent);
        console.log('✅', fileResult.message);

        // 4. Чтение созданного файла
        console.log('\n4. Читаем созданный файл:');
        const readResult = await vfs.readFile('InstagramParser', 'instagram_utils.py');
        console.log(`📖 Файл: ${readResult.path}`);
        console.log(`📊 Размер: ${readResult.size} байт, строк: ${readResult.lines}`);
        console.log('─' * 50);
        console.log(readResult.content.substring(0, 200) + '...');
        console.log('─' * 50);

        // 5. Список файлов проекта
        console.log('\n5. Структура проекта:');
        const filesResult = await vfs.listFiles('InstagramParser');
        console.log(`📁 Проект: ${filesResult.project}`);
        filesResult.files.forEach(file => {
            console.log(`  📄 ${file.path} (${file.extension}) - ${file.size} байт`);
        });

        // 6. Статистика системы
        console.log('\n6. Статистика системы:');
        const statsResult = await vfs.getSystemStats();
        console.log(`📊 Проектов: ${statsResult.stats.projectsCount}`);
        console.log(`📄 Файлов: ${statsResult.stats.totalFiles}`);
        console.log(`💾 Размер: ${statsResult.stats.totalSize} байт`);
        console.log(`🎯 Активный проект: ${statsResult.stats.activeProject}`);
        console.log(`🎨 Шаблоны: ${statsResult.stats.availableTemplates.join(', ')}`);

        // 7. Экспорт проекта
        console.log('\n7. Экспорт проекта:');
        const exportResult = await vfs.exportProject('InstagramParser');
        console.log('✅ Проект экспортирован в JSON');
        console.log(`📦 Размер экспорта: ${exportResult.data.length} символов`);

        console.log('\n✅ Демонстрация завершена успешно!');
        console.log('🎉 Интегрированная ВФС готова к использованию в Open Web UI');

        return vfs;

    } catch (error) {
        console.error('❌ Ошибка во время демонстрации:', error.message);
        throw error;
    }
}

// Автоматический запуск демонстрации при загрузке
if (typeof window !== 'undefined') {
    // В браузере
    window.addEventListener('load', () => {
        console.log('🌐 Интегрированная ВФС загружена в браузере');
    });
} else if (typeof require !== 'undefined' && require.main === module) {
    // В Node.js
    demonstrateVFS().catch(console.error);
} 