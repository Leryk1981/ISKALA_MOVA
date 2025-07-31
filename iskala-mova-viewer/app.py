from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Шлях до директорії з файлами
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Головна сторінка - перенаправляє на переглядач"""
    return send_from_directory(BASE_DIR, 'layered_viewer.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Обслуговування статичних файлів"""
    return send_from_directory(BASE_DIR, filename)

@app.route('/api/capsule/latest', methods=['GET'])
def get_latest_capsule():
    """Отримати останню капсулу"""
    try:
        capsule_path = os.path.join(BASE_DIR, 'example_capsule.json')
        with open(capsule_path, 'r', encoding='utf-8') as f:
            capsule = json.load(f)
        
        logger.info("Отримано запит на останню капсулу")
        return jsonify(capsule)
    except Exception as e:
        logger.error(f"Помилка читання капсули: {e}")
        return jsonify({"error": "Помилка сервера"}), 500

def validate_capsule_data(data):
    """Валідація даних капсули"""
    if not isinstance(data, dict):
        return False, "Дані повинні бути об'єктом"
    
    required_layers = ['mova', 'jalm', 'code', 'log', 'error']
    for layer in required_layers:
        if layer not in data:
            return False, f"Відсутній обов'язковий шар: {layer}"
        
        layer_data = data[layer]
        if not isinstance(layer_data, dict):
            return False, f"Дані шару {layer} повинні бути об'єктом"
        
        if 'short' not in layer_data or 'full' not in layer_data:
            return False, f"Шар {layer} повинен містити поля 'short' та 'full'"
        
        if not isinstance(layer_data['short'], str) or not isinstance(layer_data['full'], str):
            return False, f"Поля 'short' та 'full' шару {layer} повинні бути рядками"
    
    return True, "OK"

@app.route('/api/capsule', methods=['POST'])
def save_capsule():
    """Зберегти нову капсулу"""
    try:
        capsule_data = request.get_json()
        
        # Валідація даних
        is_valid, message = validate_capsule_data(capsule_data)
        if not is_valid:
            return jsonify({"error": f"Помилка валідації: {message}"}), 400
        
        # Створюємо ім'я файлу з timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"capsule_{timestamp}.json"
        filepath = os.path.join(BASE_DIR, filename)
        
        # Зберігаємо файл
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(capsule_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Збережено капсулу: {filename}")
        return jsonify({
            "success": True,
            "filename": filename,
            "message": "Капсула збережена успішно"
        })
    except Exception as e:
        logger.error(f"Помилка збереження капсули: {e}")
        return jsonify({"error": "Помилка збереження"}), 500

@app.route('/api/capsules', methods=['GET'])
def get_capsules_list():
    """Отримати список всіх капсул"""
    try:
        capsules = []
        
        # Шукаємо всі файли капсул
        for filename in os.listdir(BASE_DIR):
            if filename.startswith('capsule_') and filename.endswith('.json'):
                filepath = os.path.join(BASE_DIR, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        capsule = json.load(f)
                    
                    capsules.append({
                        "filename": filename,
                        "timestamp": filename.replace('capsule_', '').replace('.json', ''),
                        "preview": {
                            "mova": capsule.get('mova', {}).get('short', 'Немає даних MOVA'),
                            "jalm": capsule.get('jalm', {}).get('short', 'Немає даних JALM')
                        }
                    })
                except Exception as e:
                    logger.warning(f"Помилка читання файлу {filename}: {e}")
                    continue
        
        # Сортуємо за timestamp (новіші спочатку)
        capsules.sort(key=lambda x: x['timestamp'], reverse=True)
        
        logger.info(f"Отримано список капсул: {len(capsules)} файлів")
        return jsonify(capsules)
    except Exception as e:
        logger.error(f"Помилка читання списку капсул: {e}")
        return jsonify({"error": "Помилка сервера"}), 500

@app.route('/api/capsule/<filename>', methods=['GET'])
def get_capsule_by_filename(filename):
    """Отримати конкретну капсулу за ім'ям файлу"""
    try:
        filepath = os.path.join(BASE_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "Капсула не знайдена"}), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            capsule = json.load(f)
        
        logger.info(f"Отримано капсулу: {filename}")
        return jsonify(capsule)
    except Exception as e:
        logger.error(f"Помилка читання капсули {filename}: {e}")
        return jsonify({"error": "Помилка сервера"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Перевірка стану сервера"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("🚀 Запуск ISKALA/MOVA Viewer сервера...")
    print(f"📁 Робоча директорія: {BASE_DIR}")
    print("🌐 Сервер буде доступний на http://localhost:5000")
    print("📖 API документація: http://localhost:5000/api/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 