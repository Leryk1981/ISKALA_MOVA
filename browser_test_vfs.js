// Тестирование ВФС прямо в браузере Open Web UI
// Скопируйте этот код и вставьте как сообщение в чат

console.log("🚀 Запуск тестирования ВФС...");

// Проверка загрузки ВФС
try {
    // Попытка загрузить ВФС из файла
    if (typeof IntegratedVFS !== 'undefined') {
        console.log("✅ IntegratedVFS класс найден!");
        
        // Инициализация ВФС
        window.testVFS = new IntegratedVFS();
        console.log("✅ ВФС инициализирована");
        
        // Тест 1: Проверка системной статистики
        window.testVFS.getSystemStats().then(stats => {
            console.log("📊 Статистика ВФС:", stats);
        }).catch(err => {
            console.error("❌ Ошибка получения статистики:", err);
        });
        
        // Тест 2: Создание проекта
        window.testVFS.createProject("BrowserTestProject", "default").then(result => {
            console.log("✅ Проект создан:", result);
            
            // Тест 3: Добавление файла
            return window.testVFS.createFile("BrowserTestProject", "test.py", "print('Hello from Browser VFS!')");
        }).then(result => {
            console.log("✅ Файл создан:", result);
            
            // Тест 4: Чтение файла
            return window.testVFS.readFile("BrowserTestProject", "test.py");
        }).then(result => {
            console.log("✅ Содержимое файла:", result);
            
            // Тест 5: Список проектов
            return window.testVFS.listProjects();
        }).then(result => {
            console.log("✅ Список проектов:", result);
            
            console.log("🎉 Все тесты ВФС пройдены успешно!");
            
        }).catch(err => {
            console.error("❌ Ошибка во время тестирования:", err);
        });
        
    } else {
        console.log("⚠️ IntegratedVFS не найден, попробуем создать минимальную версию...");
        
        // Минимальная версия ВФС для тестирования
        window.testVFS = {
            projects: {},
            activeProject: null,
            
            createProject: function(name, template = 'default') {
                this.projects[name] = {
                    name: name,
                    files: {},
                    created: new Date().toISOString(),
                    template: template
                };
                
                // Добавляем базовые файлы для шаблона
                if (template === 'default') {
                    this.projects[name].files['main.py'] = `# ${name} - проект\nprint("Hello from ${name}!")`;
                    this.projects[name].files['README.md'] = `# ${name}\n\nПроект создан в ВФС браузера`;
                }
                
                this.activeProject = name;
                console.log(`✅ Проект "${name}" создан (${template})`);
                return this.projects[name];
            },
            
            createFile: function(projectName, fileName, content) {
                if (!this.projects[projectName]) {
                    console.error(`❌ Проект "${projectName}" не найден`);
                    return false;
                }
                
                this.projects[projectName].files[fileName] = content;
                console.log(`✅ Файл "${fileName}" добавлен в "${projectName}"`);
                return true;
            },
            
            readFile: function(projectName, fileName) {
                const project = this.projects[projectName];
                if (!project || !project.files[fileName]) {
                    console.error(`❌ Файл "${fileName}" не найден в проекте "${projectName}"`);
                    return null;
                }
                
                return {
                    path: fileName,
                    content: project.files[fileName],
                    size: project.files[fileName].length
                };
            },
            
            listProjects: function() {
                return Object.keys(this.projects).map(name => ({
                    name: name,
                    isActive: name === this.activeProject,
                    filesCount: Object.keys(this.projects[name].files).length
                }));
            },
            
            showProject: function(projectName) {
                const project = this.projects[projectName];
                if (!project) {
                    console.error(`❌ Проект "${projectName}" не найден`);
                    return;
                }
                
                console.log(`📂 Проект: ${project.name}`);
                console.log(`📅 Создан: ${project.created}`);
                console.log(`📄 Файлы:`);
                
                Object.keys(project.files).forEach(fileName => {
                    const size = project.files[fileName].length;
                    console.log(`  📄 ${fileName} (${size} символов)`);
                });
            },
            
            exportProject: function(projectName) {
                const project = this.projects[projectName];
                if (!project) {
                    console.error(`❌ Проект "${projectName}" не найден`);
                    return;
                }
                
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
                
                return exportData;
            }
        };
        
        console.log("✅ Минимальная ВФС создана для тестирования");
        
        // Запуск тестов с минимальной ВФС
        console.log("🧪 Запуск тестов...");
        
        // Создание тестового проекта
        window.testVFS.createProject("TestProject", "default");
        
        // Добавление файла
        window.testVFS.createFile("TestProject", "calculator.py", `
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

if __name__ == "__main__":
    print("Calculator ready!")
    print("2 + 3 =", add(2, 3))
    print("5 - 2 =", subtract(5, 2))
`);
        
        // Просмотр проекта
        window.testVFS.showProject("TestProject");
        
        // Чтение файла
        const fileContent = window.testVFS.readFile("TestProject", "calculator.py");
        console.log("📖 Содержимое calculator.py:", fileContent);
        
        // Список проектов
        const projects = window.testVFS.listProjects();
        console.log("📋 Проекты:", projects);
        
        console.log("🎉 Тестирование завершено!");
    }
    
    // Вывод доступных команд
    console.log(`
🆘 Доступные команды для тестирования:
- testVFS.createProject(name, template)
- testVFS.createFile(project, filename, content)  
- testVFS.readFile(project, filename)
- testVFS.showProject(project)
- testVFS.listProjects()
- testVFS.exportProject(project)

📚 Примеры использования:
testVFS.createProject("MyParser", "default");
testVFS.createFile("MyParser", "main.py", "print('Hello!')");
testVFS.showProject("MyParser");
testVFS.exportProject("MyParser");
`);
    
} catch (error) {
    console.error("💥 Ошибка при загрузке ВФС:", error);
    console.log("📋 Попробуйте перезагрузить страницу или проверить установку плагина");
} 