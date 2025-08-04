/**
 * Плагин виртуальной файловой системы для Open Web UI
 * Добавляет команды для управления проектами и файлами
 * 
 * Установка: поместить в папку plugins/ Open Web UI
 */

// Импорт интегрированной ВФС
// В реальной среде это будет: import { IntegratedVFS } from './openwebui_integrated_vfs.js'

class VFSPlugin {
    constructor() {
        this.name = 'Virtual File System';
        this.version = '1.0.0';
        this.description = 'Интегрированная виртуальная файловая система для Open Web UI';
        this.author = 'Open Web UI Community';
        
        // Инициализация ВФС
        this.vfs = null;
        this.initialized = false;
        
        // Регистрация команд
        this.commands = {
            '/vfs': this.handleVFSCommand.bind(this),
            '/project': this.handleProjectCommand.bind(this),
            '/file': this.handleFileCommand.bind(this),
            '/template': this.handleTemplateCommand.bind(this),
            '/export': this.handleExportCommand.bind(this),
            '/import': this.handleImportCommand.bind(this)
        };
    }

    /**
     * Инициализация плагина
     */
    async initialize(openWebUI) {
        this.openWebUI = openWebUI;
        
        try {
            // Создание экземпляра ВФС
            const { IntegratedVFS } = await import('./openwebui_integrated_vfs.js');
            this.vfs = new IntegratedVFS();
            this.initialized = true;
            
            // Регистрация команд в Open Web UI
            for (const [command, handler] of Object.entries(this.commands)) {
                openWebUI.registerCommand(command, {
                    handler: handler,
                    description: this.getCommandDescription(command),
                    usage: this.getCommandUsage(command)
                });
            }
            
            // Добавление UI элементов
            this.addUIElements();
            
            console.log('✅ VFS Plugin initialized successfully');
            return true;
            
        } catch (error) {
            console.error('❌ Failed to initialize VFS Plugin:', error);
            return false;
        }
    }

    /**
     * Основной обработчик команды /vfs
     */
    async handleVFSCommand(args, context) {
        if (!this.initialized) {
            return this.errorResponse('VFS Plugin not initialized');
        }

        if (args.length === 0) {
            return this.helpResponse();
        }

        const subcommand = args[0].toLowerCase();

        switch (subcommand) {
            case 'stats':
                return await this.handleStats();
            
            case 'status':
                return await this.handleStatus();
            
            case 'help':
                return this.helpResponse();
            
            case 'save':
                return await this.handleSaveState();
            
            case 'load':
                return await this.handleLoadState();
            
            default:
                return this.errorResponse(`Unknown VFS command: ${subcommand}`);
        }
    }

    /**
     * Обработчик команд проектов /project
     */
    async handleProjectCommand(args, context) {
        if (!this.initialized) {
            return this.errorResponse('VFS Plugin not initialized');
        }

        if (args.length === 0) {
            return await this.handleProjectList();
        }

        const action = args[0].toLowerCase();

        switch (action) {
            case 'create':
                return await this.handleProjectCreate(args.slice(1));
            
            case 'delete':
            case 'remove':
                return await this.handleProjectDelete(args.slice(1));
            
            case 'switch':
            case 'activate':
                return await this.handleProjectSwitch(args.slice(1));
            
            case 'list':
                return await this.handleProjectList();
            
            case 'info':
                return await this.handleProjectInfo(args.slice(1));
            
            default:
                return this.errorResponse(`Unknown project action: ${action}`);
        }
    }

    /**
     * Обработчик команд файлов /file
     */
    async handleFileCommand(args, context) {
        if (!this.initialized) {
            return this.errorResponse('VFS Plugin not initialized');
        }

        if (args.length === 0) {
            return this.errorResponse('File command requires arguments');
        }

        const action = args[0].toLowerCase();

        switch (action) {
            case 'create':
                return await this.handleFileCreate(args.slice(1), context);
            
            case 'read':
            case 'show':
                return await this.handleFileRead(args.slice(1));
            
            case 'update':
            case 'edit':
                return await this.handleFileUpdate(args.slice(1), context);
            
            case 'delete':
            case 'remove':
                return await this.handleFileDelete(args.slice(1));
            
            case 'list':
                return await this.handleFileList(args.slice(1));
            
            default:
                return this.errorResponse(`Unknown file action: ${action}`);
        }
    }

    /**
     * Обработчик команд шаблонов /template
     */
    async handleTemplateCommand(args, context) {
        if (args.length === 0) {
            return this.listTemplatesResponse();
        }

        const action = args[0].toLowerCase();

        switch (action) {
            case 'list':
                return this.listTemplatesResponse();
            
            case 'info':
                return this.templateInfoResponse(args[1]);
            
            default:
                return this.errorResponse(`Unknown template action: ${action}`);
        }
    }

    // =============================================================================
    // РЕАЛИЗАЦИЯ КОМАНД ПРОЕКТОВ
    // =============================================================================

    async handleProjectCreate(args) {
        if (args.length === 0) {
            return this.errorResponse('Project name is required');
        }

        const projectName = args[0];
        const template = args[1] || 'default';

        try {
            const result = await this.vfs.createProject(projectName, template);
            
            return {
                type: 'success',
                title: '✅ Проект создан',
                content: `**Проект:** ${result.project}\n**Шаблон:** ${result.template}\n**Файлов создано:** ${result.filesCreated}`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to create project: ${error.message}`);
        }
    }

    async handleProjectDelete(args) {
        if (args.length === 0) {
            return this.errorResponse('Project name is required');
        }

        const projectName = args[0];

        try {
            const result = await this.vfs.deleteProject(projectName);
            
            return {
                type: 'success',
                title: '🗑️ Проект удален',
                content: result.message,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to delete project: ${error.message}`);
        }
    }

    async handleProjectSwitch(args) {
        if (args.length === 0) {
            return this.errorResponse('Project name is required');
        }

        const projectName = args[0];

        try {
            const result = await this.vfs.switchProject(projectName);
            
            return {
                type: 'success',
                title: '🔄 Проект активирован',
                content: `Переключились на проект: **${result.activeProject}**`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to switch project: ${error.message}`);
        }
    }

    async handleProjectList() {
        try {
            const result = await this.vfs.listProjects();
            
            let content = '## 📋 Список проектов:\n\n';
            
            if (result.projects.length === 0) {
                content += '*Проекты не найдены. Создайте проект командой `/project create <название>`*';
            } else {
                result.projects.forEach(project => {
                    const status = project.isActive ? '🟢' : '⚪';
                    const filesInfo = project.filesCount ? ` (${project.filesCount} файлов)` : '';
                    content += `${status} **${project.name}** - ${project.type}${filesInfo}\n`;
                });
                
                content += `\n**Всего проектов:** ${result.totalCount}`;
                if (result.activeProject) {
                    content += `\n**Активный:** ${result.activeProject}`;
                }
            }

            return {
                type: 'info',
                title: '📂 Проекты',
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to list projects: ${error.message}`);
        }
    }

    async handleProjectInfo(args) {
        const projectName = args[0] || null;

        try {
            const result = await this.vfs.getProjectInfo(projectName);
            const project = result.project;
            
            let content = `## 📋 Информация о проекте\n\n`;
            content += `**Название:** ${project.name}\n`;
            content += `**Тип:** ${project.type || 'не указан'}\n`;
            content += `**Создан:** ${new Date(project.created).toLocaleString()}\n`;
            content += `**Изменен:** ${new Date(project.modified).toLocaleString()}\n`;
            content += `**Файлов:** ${project.filesCount}\n`;
            content += `**Размер:** ${project.size} байт\n`;
            content += `**Статус:** ${project.isActive ? '🟢 Активный' : '⚪ Неактивный'}\n`;
            
            if (project.template) {
                content += `**Шаблон:** ${project.template}\n`;
            }

            return {
                type: 'info',
                title: `📂 ${project.name}`,
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to get project info: ${error.message}`);
        }
    }

    // =============================================================================
    // РЕАЛИЗАЦИЯ КОМАНД ФАЙЛОВ
    // =============================================================================

    async handleFileCreate(args, context) {
        if (args.length < 2) {
            return this.errorResponse('Usage: /file create <project> <filepath> [content]');
        }

        const [projectName, filePath] = args;
        const content = args.slice(2).join(' ') || '';

        try {
            const result = await this.vfs.createFile(projectName, filePath, content);
            
            return {
                type: 'success',
                title: '📄 Файл создан',
                content: `**Проект:** ${projectName}\n**Путь:** ${result.path}\n**Размер:** ${result.size} байт`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to create file: ${error.message}`);
        }
    }

    async handleFileRead(args) {
        if (args.length < 2) {
            return this.errorResponse('Usage: /file read <project> <filepath>');
        }

        const [projectName, filePath] = args;

        try {
            const result = await this.vfs.readFile(projectName, filePath);
            
            let content = `## 📖 ${result.path}\n\n`;
            content += `**Размер:** ${result.size} байт  \n`;
            content += `**Строк:** ${result.lines}\n\n`;
            content += '```\n' + result.content + '\n```';

            return {
                type: 'info',
                title: `📄 ${filePath}`,
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to read file: ${error.message}`);
        }
    }

    async handleFileUpdate(args, context) {
        if (args.length < 3) {
            return this.errorResponse('Usage: /file update <project> <filepath> <content>');
        }

        const [projectName, filePath] = args;
        const content = args.slice(2).join(' ');

        try {
            const result = await this.vfs.updateFile(projectName, filePath, content);
            
            return {
                type: 'success',
                title: '✏️ Файл обновлен',
                content: `**Проект:** ${projectName}\n**Путь:** ${result.path}\n**Изменение размера:** ${result.sizeDiff > 0 ? '+' : ''}${result.sizeDiff} байт`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to update file: ${error.message}`);
        }
    }

    async handleFileDelete(args) {
        if (args.length < 2) {
            return this.errorResponse('Usage: /file delete <project> <filepath>');
        }

        const [projectName, filePath] = args;

        try {
            const result = await this.vfs.deleteFile(projectName, filePath);
            
            return {
                type: 'success',
                title: '🗑️ Файл удален',
                content: `**Проект:** ${projectName}\n**Путь:** ${result.path}`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to delete file: ${error.message}`);
        }
    }

    async handleFileList(args) {
        if (args.length === 0) {
            return this.errorResponse('Usage: /file list <project>');
        }

        const projectName = args[0];

        try {
            const result = await this.vfs.listFiles(projectName);
            
            let content = `## 📁 Файлы проекта ${projectName}\n\n`;
            
            if (result.files.length === 0) {
                content += '*Файлы не найдены*';
            } else {
                result.files.forEach(file => {
                    const ext = file.extension ? `(${file.extension})` : '';
                    content += `📄 **${file.path}** ${ext} - ${file.size} байт, ${file.lines} строк\n`;
                });
                
                content += `\n**Статистика:**\n`;
                content += `- Всего файлов: ${result.stats.totalFiles}\n`;
                content += `- Общий размер: ${result.stats.totalSize} байт\n`;
                
                if (Object.keys(result.stats.extensions).length > 0) {
                    content += `- Расширения: ${Object.entries(result.stats.extensions)
                        .map(([ext, count]) => `${ext || 'без расширения'}(${count})`)
                        .join(', ')}\n`;
                }
            }

            return {
                type: 'info',
                title: `📂 ${projectName}`,
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to list files: ${error.message}`);
        }
    }

    // =============================================================================
    // СИСТЕМНЫЕ КОМАНДЫ
    // =============================================================================

    async handleStats() {
        try {
            const result = await this.vfs.getSystemStats();
            const stats = result.stats;
            
            let content = `## 📊 Статистика ВФС\n\n`;
            content += `**Проектов:** ${stats.projectsCount}\n`;
            content += `**Файлов:** ${stats.totalFiles}\n`;
            content += `**Размер:** ${this.formatBytes(stats.totalSize)}\n`;
            content += `**Активный проект:** ${stats.activeProject || 'нет'}\n`;
            content += `**Тип хранилища:** ${stats.storageType}\n`;
            content += `**Доступные шаблоны:** ${stats.availableTemplates.join(', ')}\n`;

            if (result.projects.length > 0) {
                content += `\n**Детали проектов:**\n`;
                result.projects.forEach(project => {
                    const status = project.name === stats.activeProject ? '🟢' : '⚪';
                    content += `${status} ${project.name} - ${project.filesCount || 0} файлов\n`;
                });
            }

            return {
                type: 'info',
                title: '📊 Статистика',
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to get stats: ${error.message}`);
        }
    }

    async handleStatus() {
        const status = {
            initialized: this.initialized,
            version: this.version,
            activeProject: this.vfs ? (await this.vfs.getSystemStats()).stats.activeProject : null
        };

        let content = `## 🔧 Статус ВФС\n\n`;
        content += `**Плагин:** ${this.initialized ? '🟢 Активен' : '🔴 Неактивен'}\n`;
        content += `**Версия:** ${this.version}\n`;
        content += `**Активный проект:** ${status.activeProject || 'нет'}\n`;

        return {
            type: 'info',
            title: '🔧 Статус',
            content: content,
            data: status
        };
    }

    async handleSaveState() {
        try {
            const result = await this.vfs.saveSystemState();
            
            return {
                type: 'success',
                title: '💾 Состояние сохранено',
                content: `${result.message}\n**Проектов:** ${result.projectsCount}\n**Размер состояния:** ${this.formatBytes(result.stateSize)}`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to save state: ${error.message}`);
        }
    }

    async handleLoadState() {
        try {
            const result = await this.vfs.loadSystemState();
            
            return {
                type: 'success',
                title: '📂 Состояние восстановлено',
                content: `${result.message}\n**Проектов загружено:** ${result.projectsLoaded}\n**Активный проект:** ${result.activeProject || 'нет'}`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to load state: ${error.message}`);
        }
    }

    // =============================================================================
    // ОБРАБОТЧИКИ ЭКСПОРТА/ИМПОРТА
    // =============================================================================

    async handleExportCommand(args, context) {
        if (args.length === 0) {
            return this.errorResponse('Usage: /export <project> [format]');
        }

        const projectName = args[0];
        const format = args[1] || 'json';

        try {
            const result = await this.vfs.exportProject(projectName, format);
            
            let content = `## 📦 Экспорт проекта ${projectName}\n\n`;
            content += `**Формат:** ${result.format}\n`;
            
            if (result.format === 'json') {
                content += `**Размер:** ${this.formatBytes(result.data.length)}\n\n`;
                content += '```json\n' + result.data.substring(0, 500) + '...\n```\n\n';
                content += '*Полный экспорт доступен в data объекте ответа*';
            }

            return {
                type: 'success',
                title: '📦 Экспорт',
                content: content,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to export project: ${error.message}`);
        }
    }

    async handleImportCommand(args, context) {
        if (args.length === 0) {
            return this.errorResponse('Usage: /import <json_data> [format]');
        }

        const jsonData = args.join(' ');
        const format = 'json';

        try {
            const result = await this.vfs.importProject(jsonData, format);
            
            return {
                type: 'success',
                title: '📥 Импорт',
                content: `${result.message}\n**Файлов импортировано:** ${result.filesImported}`,
                data: result
            };
        } catch (error) {
            return this.errorResponse(`Failed to import project: ${error.message}`);
        }
    }

    // =============================================================================
    // ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    // =============================================================================

    listTemplatesResponse() {
        const templates = this.vfs ? Object.keys(this.vfs.templates) : [];
        
        let content = `## 🎨 Доступные шаблоны:\n\n`;
        
        if (this.vfs) {
            Object.entries(this.vfs.templates).forEach(([key, template]) => {
                content += `**${key}** - ${template.description}\n`;
                content += `  *Тип:* ${template.type}, *Файлов:* ${Object.keys(template.files).length}\n\n`;
            });
        } else {
            content += '*ВФС не инициализирована*';
        }

        return {
            type: 'info',
            title: '🎨 Шаблоны',
            content: content
        };
    }

    templateInfoResponse(templateName) {
        if (!this.vfs || !templateName) {
            return this.errorResponse('Template name is required');
        }

        const template = this.vfs.templates[templateName];
        if (!template) {
            return this.errorResponse(`Template '${templateName}' not found`);
        }

        let content = `## 🎨 Шаблон: ${templateName}\n\n`;
        content += `**Название:** ${template.name}\n`;
        content += `**Описание:** ${template.description}\n`;
        content += `**Тип:** ${template.type}\n`;
        content += `**Файлов:** ${Object.keys(template.files).length}\n\n`;
        
        content += `**Файлы в шаблоне:**\n`;
        Object.keys(template.files).forEach(filePath => {
            content += `- ${filePath}\n`;
        });

        return {
            type: 'info',
            title: `🎨 ${templateName}`,
            content: content,
            data: template
        };
    }

    helpResponse() {
        const content = `## 🆘 Справка по ВФС

### Команды проектов:
- \`/project create <name> [template]\` - создать проект
- \`/project list\` - список проектов  
- \`/project switch <name>\` - переключиться на проект
- \`/project info [name]\` - информация о проекте
- \`/project delete <name>\` - удалить проект

### Команды файлов:
- \`/file create <project> <path> [content]\` - создать файл
- \`/file read <project> <path>\` - прочитать файл
- \`/file update <project> <path> <content>\` - обновить файл
- \`/file delete <project> <path>\` - удалить файл
- \`/file list <project>\` - список файлов

### Системные команды:
- \`/vfs stats\` - статистика системы
- \`/vfs status\` - статус плагина
- \`/vfs save\` - сохранить состояние
- \`/vfs load\` - загрузить состояние

### Шаблоны:
- \`/template list\` - список шаблонов
- \`/template info <name>\` - информация о шаблоне

### Экспорт/Импорт:
- \`/export <project> [format]\` - экспорт проекта
- \`/import <json_data>\` - импорт проекта`;

        return {
            type: 'info',
            title: '🆘 Справка',
            content: content
        };
    }

    errorResponse(message) {
        return {
            type: 'error',
            title: '❌ Ошибка',
            content: message
        };
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 байт';
        const k = 1024;
        const sizes = ['байт', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getCommandDescription(command) {
        const descriptions = {
            '/vfs': 'Основные команды виртуальной файловой системы',
            '/project': 'Управление проектами',
            '/file': 'Управление файлами',
            '/template': 'Работа с шаблонами проектов',
            '/export': 'Экспорт проектов',
            '/import': 'Импорт проектов'
        };
        return descriptions[command] || 'ВФС команда';
    }

    getCommandUsage(command) {
        const usages = {
            '/vfs': '/vfs [stats|status|help|save|load]',
            '/project': '/project [create|list|switch|info|delete] [args...]',
            '/file': '/file [create|read|update|delete|list] [args...]',
            '/template': '/template [list|info] [name]',
            '/export': '/export <project> [format]',
            '/import': '/import <json_data>'
        };
        return usages[command] || command + ' [args...]';
    }

    /**
     * Добавление UI элементов в интерфейс Open Web UI
     */
    addUIElements() {
        // Это будет реализовано в зависимости от API Open Web UI
        // Примерный код:
        
        /*
        this.openWebUI.addSidebarButton({
            id: 'vfs-projects',
            icon: '📂',
            title: 'Проекты ВФС',
            onClick: () => this.showProjectManager()
        });

        this.openWebUI.addQuickAction({
            id: 'vfs-new-project',
            label: 'Новый проект',
            command: '/project create'
        });
        */
    }
}

// =============================================================================
// ЭКСПОРТ И РЕГИСТРАЦИЯ ПЛАГИНА
// =============================================================================

// Для использования в Open Web UI
if (typeof window !== 'undefined') {
    window.VFSPlugin = VFSPlugin;
    
    // Автоматическая регистрация при наличии Open Web UI
    if (typeof openWebUI !== 'undefined') {
        const vfsPlugin = new VFSPlugin();
        openWebUI.registerPlugin(vfsPlugin);
    }
}

// Для использования в Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VFSPlugin;
}

// Экспорт по умолчанию
export default VFSPlugin; 