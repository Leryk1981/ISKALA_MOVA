const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// API endpoint для отримання останньої капсули
app.get('/api/capsule/latest', async (req, res) => {
    try {
        // Читаємо приклад капсули з файлу
        const capsuleData = await fs.readFile('example_capsule.json', 'utf8');
        const capsule = JSON.parse(capsuleData);
        
        res.json(capsule);
    } catch (error) {
        console.error('Помилка читання капсули:', error);
        res.status(500).json({ error: 'Помилка сервера' });
    }
});

// API endpoint для збереження нової капсули
app.post('/api/capsule', async (req, res) => {
    try {
        const capsuleData = req.body;
        
        // Зберігаємо в файл з timestamp
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `capsule_${timestamp}.json`;
        
        await fs.writeFile(filename, JSON.stringify(capsuleData, null, 2));
        
        res.json({ 
            success: true, 
            filename: filename,
            message: 'Капсула збережена успішно' 
        });
    } catch (error) {
        console.error('Помилка збереження капсули:', error);
        res.status(500).json({ error: 'Помилка збереження' });
    }
});

// API endpoint для отримання списку всіх капсул
app.get('/api/capsules', async (req, res) => {
    try {
        const files = await fs.readdir('.');
        const capsuleFiles = files.filter(file => file.startsWith('capsule_') && file.endsWith('.json'));
        
        const capsules = [];
        for (const file of capsuleFiles) {
            const content = await fs.readFile(file, 'utf8');
            const capsule = JSON.parse(content);
            capsules.push({
                filename: file,
                timestamp: file.replace('capsule_', '').replace('.json', ''),
                preview: {
                    mova: capsule.mova?.short || 'Немає даних MOVA',
                    jalm: capsule.jalm?.short || 'Немає даних JALM'
                }
            });
        }
        
        res.json(capsules);
    } catch (error) {
        console.error('Помилка читання списку капсул:', error);
        res.status(500).json({ error: 'Помилка сервера' });
    }
});

// API endpoint для отримання конкретної капсули
app.get('/api/capsule/:filename', async (req, res) => {
    try {
        const filename = req.params.filename;
        const content = await fs.readFile(filename, 'utf8');
        const capsule = JSON.parse(content);
        
        res.json(capsule);
    } catch (error) {
        console.error('Помилка читання капсули:', error);
        res.status(404).json({ error: 'Капсула не знайдена' });
    }
});

app.listen(PORT, () => {
    console.log(`Сервер запущено на http://localhost:${PORT}`);
    console.log(`API доступне на http://localhost:${PORT}/api/`);
}); 