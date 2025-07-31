/**
 * Iskala/MOVA - Веб-інтерфейс для живого простору сенсів
 * p5.js візуалізація графа капсул та зв'язків
 */

// Глобальні змінні
let graphData = { nodes: [], links: [] };
let selectedNode = null;
let hoveredNode = null;
let dragging = false;
let dragNode = null;
let offsetX, offsetY;

// Налаштування візуалізації
const NODE_RADIUS = 30;
const NODE_SPACING = 150;
const LINK_COLOR = '#4CAF50';
const NODE_COLORS = {
    default: '#2196F3',
    selected: '#FF5722',
    hovered: '#FF9800',
    new: '#4CAF50',
    llm: '#9C27B0'
};

// API налаштування
const API_BASE = 'http://localhost:8001';

// p5.js функції
function setup() {
    const canvas = createCanvas(windowWidth, windowHeight);
    canvas.parent('canvas-container');
    
    // Завантажуємо початкові дані
    loadGraph();
    checkLLMStatus();
    
    // Налаштовуємо початкові позиції вузлів
    arrangeNodes();
}

function draw() {
    background(30, 60, 114);
    
    // Малюємо зв'язки
    drawLinks();
    
    // Малюємо вузли
    drawNodes();
    
    // Малюємо tooltip
    drawTooltip();
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
    arrangeNodes();
}

// Функції візуалізації
function drawNodes() {
    graphData.nodes.forEach(node => {
        let color = NODE_COLORS.default;
        
        if (node.id === selectedNode) {
            color = NODE_COLORS.selected;
        } else if (node.id === hoveredNode) {
            color = NODE_COLORS.hovered;
        }
        
        // Малюємо вузол
        fill(color);
        stroke(255);
        strokeWeight(2);
        ellipse(node.x, node.y, NODE_RADIUS * 2);
        
        // Малюємо текст
        fill(255);
        noStroke();
        textAlign(CENTER, CENTER);
        textSize(12);
        text(node.name, node.x, node.y);
    });
}

function drawLinks() {
    stroke(LINK_COLOR);
    strokeWeight(2);
    noFill();
    
    graphData.links.forEach(link => {
        const sourceNode = graphData.nodes.find(n => n.id === link.source);
        const targetNode = graphData.nodes.find(n => n.id === link.target);
        
        if (sourceNode && targetNode) {
            // Обчислюємо точку на колі
            const angle = atan2(targetNode.y - sourceNode.y, targetNode.x - sourceNode.x);
            const startX = sourceNode.x + cos(angle) * NODE_RADIUS;
            const startY = sourceNode.y + sin(angle) * NODE_RADIUS;
            const endX = targetNode.x - cos(angle) * NODE_RADIUS;
            const endY = targetNode.y - sin(angle) * NODE_RADIUS;
            
            line(startX, startY, endX, endY);
            
            // Малюємо стрілку
            const arrowSize = 8;
            const arrowAngle = PI / 6;
            push();
            translate(endX, endY);
            rotate(angle);
            line(0, 0, -arrowSize, -arrowSize * tan(arrowAngle));
            line(0, 0, -arrowSize, arrowSize * tan(arrowAngle));
            pop();
        }
    });
}

function drawTooltip() {
    if (hoveredNode) {
        const node = graphData.nodes.find(n => n.id === hoveredNode);
        if (node) {
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `
                <strong>${node.name}</strong><br>
                ${node.summary}
            `;
            tooltip.style.display = 'block';
            tooltip.style.left = mouseX + 10 + 'px';
            tooltip.style.top = mouseY + 10 + 'px';
        }
    } else {
        document.getElementById('tooltip').style.display = 'none';
    }
}

// Обробка подій миші
function mousePressed() {
    const clickedNode = getNodeAt(mouseX, mouseY);
    
    if (clickedNode) {
        if (mouseButton === LEFT) {
            selectedNode = clickedNode.id;
            showCapsuleModal(clickedNode);
        } else if (mouseButton === RIGHT) {
            // Контекстне меню або інші дії
        }
    } else {
        selectedNode = null;
    }
}

function mouseDragged() {
    if (selectedNode && !dragging) {
        dragging = true;
        dragNode = graphData.nodes.find(n => n.id === selectedNode);
        if (dragNode) {
            offsetX = mouseX - dragNode.x;
            offsetY = mouseY - dragNode.y;
        }
    }
    
    if (dragging && dragNode) {
        dragNode.x = mouseX - offsetX;
        dragNode.y = mouseY - offsetY;
    }
}

function mouseReleased() {
    dragging = false;
    dragNode = null;
}

function mouseMoved() {
    hoveredNode = getNodeAt(mouseX, mouseY)?.id || null;
}

// Допоміжні функції
function getNodeAt(x, y) {
    return graphData.nodes.find(node => {
        const distance = dist(x, y, node.x, node.y);
        return distance <= NODE_RADIUS;
    });
}

function arrangeNodes() {
    const centerX = width / 2;
    const centerY = height / 2;
    
    if (graphData.nodes.length === 0) return;
    
    // Простий алгоритм розташування по колу
    const radius = min(width, height) * 0.3;
    const angleStep = TWO_PI / graphData.nodes.length;
    
    graphData.nodes.forEach((node, index) => {
        const angle = index * angleStep;
        node.x = centerX + cos(angle) * radius;
        node.y = centerY + sin(angle) * radius;
    });
}

// API функції
async function loadGraph() {
    try {
        updateStatus('Завантаження графа...');
        const response = await fetch(`${API_BASE}/graph`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        graphData = await response.json();
        updateStats();
        updateStatus(`Завантажено ${graphData.total_nodes} вузлів, ${graphData.total_links} зв'язків`);
        
        // Оновлюємо селекти для зв'язків
        updateLinkSelects();
        
    } catch (error) {
        console.error('Помилка завантаження графа:', error);
        updateStatus('Помилка завантаження графа');
    }
}

async function checkLLMStatus() {
    try {
        const response = await fetch(`${API_BASE}/llm/status`);
        const status = await response.json();
        
        const statusElement = document.getElementById('llm-status');
        if (status.available) {
            statusElement.innerHTML = `LLM: ${status.provider} (${status.model})`;
            statusElement.style.color = '#4CAF50';
        } else {
            statusElement.innerHTML = 'LLM: недоступний';
            statusElement.style.color = '#f44336';
        }
    } catch (error) {
        console.error('Помилка перевірки LLM:', error);
        document.getElementById('llm-status').innerHTML = 'LLM: помилка перевірки';
    }
}

async function createCapsule(name, content) {
    try {
        updateStatus('Створення капсули...');
        
        const formData = new FormData();
        formData.append('name', name);
        formData.append('content', content);
        
        const response = await fetch(`${API_BASE}/capsule`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        updateStatus('Капсула створена!');
        await loadGraph(); // Оновлюємо граф
        
    } catch (error) {
        console.error('Помилка створення капсули:', error);
        updateStatus('Помилка створення капсули');
    }
}

async function createLink(from, to, type) {
    try {
        updateStatus('Створення зв\'язку...');
        
        const formData = new FormData();
        formData.append('from_name', from);
        formData.append('to_name', to);
        formData.append('link_type', type);
        
        const response = await fetch(`${API_BASE}/link`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        updateStatus('Зв\'язок створено!');
        await loadGraph(); // Оновлюємо граф
        
    } catch (error) {
        console.error('Помилка створення зв\'язку:', error);
        updateStatus('Помилка створення зв\'язку');
    }
}

async function generateWithLLM(prompt, name = null) {
    try {
        updateStatus('Генерація капсули через LLM...');
        
        const formData = new FormData();
        formData.append('prompt', prompt);
        
        const response = await fetch(`${API_BASE}/llm/generate`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Створюємо капсулу з згенерованим контентом
        const capsuleName = name || generateNameFromPrompt(prompt);
        await createCapsule(capsuleName, result.content);
        
        updateStatus('Капсула згенерована та створена!');
        
    } catch (error) {
        console.error('Помилка LLM генерації:', error);
        updateStatus('Помилка LLM генерації');
    }
}

async function translateText(text, targetLang, sourceLang = null) {
    try {
        updateStatus('Переклад тексту...');
        
        const formData = new FormData();
        formData.append('text', text);
        formData.append('target_lang', targetLang);
        if (sourceLang) {
            formData.append('source_lang', sourceLang);
        }
        
        const response = await fetch(`${API_BASE}/llm/translate`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Показуємо результат
        const resultDiv = document.getElementById('translateResult');
        const contentDiv = document.getElementById('translateResultContent');
        
        contentDiv.innerHTML = `
            <strong>Оригінал (${result.source_lang}):</strong><br>
            ${result.original_text}<br><br>
            <strong>Переклад (${result.target_lang}):</strong><br>
            ${result.translated_text}<br><br>
            <em>Перекладено через: ${result.provider}</em>
        `;
        
        resultDiv.style.display = 'block';
        updateStatus('Переклад завершено!');
        
        return result;
        
    } catch (error) {
        console.error('Помилка перекладу:', error);
        updateStatus('Помилка перекладу');
        throw error;
    }
}

// UI функції
function showCapsuleModal(node) {
    const modal = document.getElementById('capsuleModal');
    const title = document.getElementById('capsule-title');
    const body = document.getElementById('capsule-body');
    
    title.textContent = node.name;
    body.textContent = node.content;
    
    modal.style.display = 'block';
}

function showAddCapsuleModal() {
    document.getElementById('addCapsuleModal').style.display = 'block';
}

function showLLMModal() {
    document.getElementById('llmModal').style.display = 'block';
}

function showLinkModal() {
    document.getElementById('linkModal').style.display = 'block';
}

function showTranslateModal() {
    document.getElementById('translateModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

function updateStats() {
    document.getElementById('node-count').textContent = graphData.total_nodes || 0;
    document.getElementById('link-count').textContent = graphData.total_links || 0;
}

function updateLinkSelects() {
    const fromSelect = document.getElementById('linkFrom');
    const toSelect = document.getElementById('linkTo');
    
    // Очищаємо селекти
    fromSelect.innerHTML = '<option value="">Оберіть капсулу-джерело</option>';
    toSelect.innerHTML = '<option value="">Оберіть капсулу-призначення</option>';
    
    // Додаємо опції
    graphData.nodes.forEach(node => {
        const option = document.createElement('option');
        option.value = node.id;
        option.textContent = node.name;
        
        fromSelect.appendChild(option.cloneNode(true));
        toSelect.appendChild(option);
    });
}

function refreshGraph() {
    loadGraph();
}

function generateNameFromPrompt(prompt) {
    // Простий алгоритм генерації назви з промпту
    const words = prompt.split(' ').slice(0, 3);
    return words.join('-').toLowerCase().replace(/[^a-zа-я-]/g, '');
}

function onLLMModeChange() {
    const mode = document.getElementById('llm-mode').value;
    const liveHint = document.getElementById('llm-live-hint');
    const genBtn = document.getElementById('llm-generate-btn');
    const transBtn = document.getElementById('llm-translate-btn');
    if (mode === 'live') {
        liveHint.style.display = 'block';
        genBtn.disabled = true;
        transBtn.disabled = true;
        updateStatus('Інтерактивний режим доступний лише у CLI');
    } else {
        liveHint.style.display = 'none';
        genBtn.disabled = false;
        transBtn.disabled = false;
        updateStatus('Готово до роботи через API');
    }
}

// Перевірка доступності API (healthcheck)
async function checkAPIHealth() {
    try {
        const resp = await fetch(`${API_BASE}/health`);
        if (!resp.ok) throw new Error('API недоступний');
        return true;
    } catch (e) {
        updateStatus('❌ API недоступний. Перевірте запуск бекенду!');
        document.getElementById('llm-generate-btn').disabled = true;
        document.getElementById('llm-translate-btn').disabled = true;
        return false;
    }
}

// Обробники подій форм
document.addEventListener('DOMContentLoaded', async function() {
    await checkAPIHealth();
    // Форма додавання капсули
    document.getElementById('addCapsuleForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('capsuleName').value;
        const content = document.getElementById('capsuleContent').value;
        
        createCapsule(name, content);
        closeModal('addCapsuleModal');
        
        // Очищаємо форму
        this.reset();
    });
    
    // Форма LLM генерації
    document.getElementById('llmForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const prompt = document.getElementById('llmPrompt').value;
        const name = document.getElementById('llmName').value || null;
        
        generateWithLLM(prompt, name);
        closeModal('llmModal');
        
        // Очищаємо форму
        this.reset();
    });
    
    // Форма створення зв'язку
    document.getElementById('linkForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const from = document.getElementById('linkFrom').value;
        const to = document.getElementById('linkTo').value;
        const type = document.getElementById('linkType').value;
        
        if (from && to && from !== to) {
            createLink(from, to, type);
            closeModal('linkModal');
        } else {
            alert('Оберіть різні капсули для зв\'язку');
        }
    });
    
    // Форма перекладу
    document.getElementById('translateForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const text = document.getElementById('translateText').value;
        const targetLang = document.getElementById('translateTargetLang').value;
        const sourceLang = document.getElementById('translateSourceLang').value || null;
        
        if (text && targetLang) {
            translateText(text, targetLang, sourceLang);
        } else {
            alert('Введіть текст та оберіть мову призначення');
        }
    });
    
    // Закриття модальних вікон при кліку поза ними
    window.addEventListener('click', function(e) {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
});

// Глобальні функції для виклику з HTML
window.showAddCapsuleModal = showAddCapsuleModal;
window.showLinkModal = showLinkModal;
window.showLLMModal = showLLMModal;
window.showTranslateModal = showTranslateModal;
window.closeModal = closeModal;
window.refreshGraph = refreshGraph; 
window.onLLMModeChange = onLLMModeChange; 