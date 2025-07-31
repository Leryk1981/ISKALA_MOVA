#!/usr/bin/env python3
"""
Open WebUI Setup Script for ISKALA Integration
Автоматична налаштування Open WebUI для роботи з ISKALA
"""

import os
import sys
import json
import requests
import time
import subprocess
from pathlib import Path

class OpenWebUISetup:
    def __init__(self):
        self.openwebui_url = "http://localhost:3000"
        self.iskala_url = "http://localhost:8001"
        self.config_dir = Path("./openwebui_integration")
        self.setup_dir = Path("./openwebui_setup")
        self.setup_dir.mkdir(exist_ok=True)
        
    def check_docker(self):
        """Перевірка наявності Docker"""
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker встановлений")
                return True
        except Exception as e:
            print(f"❌ Docker не знайдений: {e}")
        return False
    
    def start_openwebui(self):
        """Запуск Open WebUI"""
        try:
            print("🚀 Запуск Open WebUI...")
            
            # Перевіряємо чи вже запущений
            result = subprocess.run(["docker", "ps", "--filter", "name=open-webui"], 
                                  capture_output=True, text=True)
            
            if "open-webui" in result.stdout:
                print("✅ Open WebUI вже запущений")
                return True
            
            # Запускаємо Open WebUI
            cmd = [
                "docker", "run", "-d",
                "-p", "3000:8080",
                "--add-host=host.docker.internal:host-gateway",
                "-v", "open-webui:/app/backend/data",
                "--name", "open-webui",
                "--restart", "always",
                "ghcr.io/open-webui/open-webui:main"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Open WebUI запущений")
                return True
            else:
                print(f"❌ Помилка запуску Open WebUI: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Помилка запуску Open WebUI: {e}")
            return False
    
    def wait_for_openwebui(self, timeout=60):
        """Очікування запуску Open WebUI"""
        print("⏳ Очікування запуску Open WebUI...")
        
        for i in range(timeout):
            try:
                response = requests.get(f"{self.openwebui_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Open WebUI готовий")
                    return True
            except:
                pass
            
            time.sleep(1)
            if i % 10 == 0:
                print(f"⏳ Очікування... ({i}/{timeout})")
        
        print("❌ Open WebUI не запустився за відведений час")
        return False
    
    def configure_openwebui(self):
        """Налаштування Open WebUI для роботи з ISKALA"""
        try:
            print("🔧 Налаштування Open WebUI...")
            
            # Завантажуємо конфігурацію
            config_file = self.config_dir / "openwebui_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Створюємо конфігурацію для Open WebUI
            openwebui_config = {
                "custom_models": config["iskala_integration"]["models"],
                "custom_endpoints": {
                    "iskala": {
                        "base_url": self.iskala_url,
                        "api_key": "",
                        "models": config["iskala_integration"]["models"]
                    }
                },
                "default_model": "iskala-mova-v2",
                "enable_custom_models": True,
                "iskala_integration": config["iskala_integration"]
            }
            
            # Зберігаємо конфігурацію
            setup_config_file = self.setup_dir / "openwebui_iskala_config.json"
            with open(setup_config_file, 'w', encoding='utf-8') as f:
                json.dump(openwebui_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Конфігурація збережена: {setup_config_file}")
            
            # Створюємо інструкції для ручного налаштування
            instructions = self.create_setup_instructions()
            
            return True
            
        except Exception as e:
            print(f"❌ Помилка налаштування: {e}")
            return False
    
    def create_setup_instructions(self):
        """Створення інструкцій для налаштування"""
        instructions = f"""
# Інструкції для налаштування Open WebUI з ISKALA

## 1. Доступ до Open WebUI
Відкрийте браузер і перейдіть до: {self.openwebui_url}

## 2. Налаштування моделей
1. Увійдіть в Open WebUI
2. Перейдіть до Settings -> Models
3. Додайте нові моделі:

### ISKALA MOVA v2
- Provider: Custom
- Base URL: {self.iskala_url}
- Model Name: iskala-mova-v2
- API Key: (залиште порожнім)

### ISKALA RAG
- Provider: Custom  
- Base URL: {self.iskala_url}
- Model Name: iskala-rag
- API Key: (залиште порожнім)

### ISKALA Translation
- Provider: Custom
- Base URL: {self.iskala_url}
- Model Name: iskala-translation
- API Key: (залиште порожнім)

## 3. Налаштування API Endpoints
Додайте наступні endpoints:

### Chat Endpoint
- URL: {self.iskala_url}/api/openwebui/chat
- Method: POST
- Headers: Content-Type: application/json

### Models Endpoint
- URL: {self.iskala_url}/api/openwebui/models
- Method: GET

### Status Endpoint
- URL: {self.iskala_url}/api/openwebui/status
- Method: GET

## 4. Тестування
1. Виберіть модель "ISKALA MOVA v2"
2. Надішліть повідомлення: "Привіт, як справи?"
3. Перевірте відповідь

## 5. Додаткові можливості
- RAG система: {self.iskala_url}/api/memory/search
- Інструменти: {self.iskala_url}/api/tools
- WebSocket: ws://localhost:8001/ws

## 6. Інтеграційний інтерфейс
Відкрийте: {self.config_dir}/iskala_openwebui_integration.html

---
Згенеровано автоматично: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        instructions_file = self.setup_dir / "setup_instructions.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)
        
        print(f"✅ Інструкції збережені: {instructions_file}")
        return instructions_file
    
    def create_quick_start_script(self):
        """Створення швидкого старту"""
        script_content = f"""#!/bin/bash
# Quick Start Script для ISKALA + Open WebUI

echo "🌺 Швидкий старт ISKALA + Open WebUI"

# Перевірка ISKALA
echo "🔍 Перевірка ISKALA..."
if curl -s {self.iskala_url}/health > /dev/null; then
    echo "✅ ISKALA працює"
else
    echo "❌ ISKALA не працює. Запустіть: docker-compose up -d"
    exit 1
fi

# Перевірка Open WebUI
echo "🔍 Перевірка Open WebUI..."
if curl -s {self.openwebui_url}/api/health > /dev/null; then
    echo "✅ Open WebUI працює"
else
    echo "❌ Open WebUI не працює. Запустіть: docker start open-webui"
    exit 1
fi

# Відкриття інтерфейсів
echo "🌐 Відкриття інтерфейсів..."

if command -v xdg-open > /dev/null; then
    xdg-open {self.openwebui_url}
    xdg-open {self.config_dir}/iskala_openwebui_integration.html
elif command -v open > /dev/null; then
    open {self.openwebui_url}
    open {self.config_dir}/iskala_openwebui_integration.html
else
    echo "📋 Відкрийте в браузері:"
    echo "  Open WebUI: {self.openwebui_url}"
    echo "  Інтеграція: {self.config_dir}/iskala_openwebui_integration.html"
fi

echo "✅ Готово! Інтеграція активна."
"""
        
        script_file = self.setup_dir / "quick_start.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        os.chmod(script_file, 0o755)
        print(f"✅ Скрипт швидкого старту створений: {script_file}")
        return script_file
    
    def run_setup(self):
        """Запуск повного налаштування"""
        print("🌺 Налаштування Open WebUI для роботи з ISKALA")
        print("=" * 60)
        
        # Перевірка Docker
        if not self.check_docker():
            print("❌ Docker не встановлений. Встановіть Docker і спробуйте знову.")
            return False
        
        # Запуск Open WebUI
        if not self.start_openwebui():
            print("❌ Не вдалося запустити Open WebUI")
            return False
        
        # Очікування запуску
        if not self.wait_for_openwebui():
            print("❌ Open WebUI не запустився")
            return False
        
        # Налаштування
        if not self.configure_openwebui():
            print("❌ Помилка налаштування")
            return False
        
        # Створення додаткових файлів
        self.create_quick_start_script()
        
        print("\n✅ Налаштування завершено!")
        print("\n📋 Наступні кроки:")
        print("1. Відкрийте Open WebUI: http://localhost:3000")
        print("2. Налаштуйте моделі згідно з інструкціями")
        print("3. Протестуйте інтеграцію")
        print(f"4. Використовуйте інтеграційний інтерфейс: {self.config_dir}/iskala_openwebui_integration.html")
        
        return True

def main():
    setup = OpenWebUISetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 