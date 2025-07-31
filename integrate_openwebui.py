#!/usr/bin/env python3
"""
ISKALA Open WebUI Integration Script
Інтеграція ISKALA з Open WebUI
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

class ISKALAOpenWebUIIntegration:
    def __init__(self):
        self.openwebui_url = "http://localhost:3000"
        self.iskala_url = "http://localhost:8001"
        self.config_dir = Path("./openwebui_integration")
        self.config_dir.mkdir(exist_ok=True)
        
    def check_openwebui_status(self):
        """Перевірка статусу Open WebUI"""
        try:
            response = requests.get(f"{self.openwebui_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Open WebUI доступний")
                return True
        except Exception as e:
            print(f"❌ Open WebUI недоступний: {e}")
        return False
    
    def check_iskala_status(self):
        """Перевірка статусу ISKALA"""
        try:
            response = requests.get(f"{self.iskala_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ ISKALA доступний")
                return True
        except Exception as e:
            print(f"❌ ISKALA недоступний: {e}")
        return False
    
    def create_openwebui_config(self):
        """Створення конфігурації для Open WebUI"""
        config = {
            "iskala_integration": {
                "enabled": True,
                "iskala_url": self.iskala_url,
                "api_endpoints": {
                    "health": f"{self.iskala_url}/health",
                    "llm_process": f"{self.iskala_url}/api/llm/process",
                    "tools": f"{self.iskala_url}/api/tools",
                    "memory": f"{self.iskala_url}/api/memory",
                    "websocket": f"{self.iskala_url.replace('http', 'ws')}/ws"
                },
                "features": {
                    "mova_trees": True,
                    "rag_system": True,
                    "translation": True,
                    "vault": True,
                    "shield": True
                }
            }
        }
        
        config_file = self.config_dir / "openwebui_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Конфігурація збережена: {config_file}")
        return config_file
    
    def create_iskala_webui_interface(self):
        """Створення веб-інтерфейсу для інтеграції"""
        html_content = f"""
<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ISKALA + Open WebUI Integration</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 2rem;
            text-align: center;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .container {{
            flex: 1;
            display: flex;
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
            width: 100%;
        }}
        
        .panel {{
            flex: 1;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .panel h2 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .status {{
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            font-weight: bold;
        }}
        
        .status.online {{
            background: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #c8e6c9;
        }}
        
        .status.offline {{
            background: #ffebee;
            color: #c62828;
            border: 1px solid #ffcdd2;
        }}
        
        .button {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin: 0.5rem;
            transition: all 0.3s ease;
        }}
        
        .button:hover {{
            background: #5a6fd8;
            transform: translateY(-2px);
        }}
        
        .iframe-container {{
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 10px;
            margin-top: 1rem;
        }}
        
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .feature {{
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
        }}
        
        .feature h3 {{
            color: #333;
            margin-bottom: 0.5rem;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌺 ISKALA + Open WebUI</h1>
        <p>Інтегрована система розумних контекстів та LLM агентів</p>
    </div>
    
    <div class="container">
        <div class="panel">
            <h2>🔧 Статус систем</h2>
            <div id="iskala-status" class="status offline">Перевірка ISKALA...</div>
            <div id="openwebui-status" class="status offline">Перевірка Open WebUI...</div>
            
            <h2>🚀 Швидкий доступ</h2>
            <a href="{self.openwebui_url}" target="_blank" class="button">Open WebUI</a>
            <a href="{self.iskala_url}" target="_blank" class="button">ISKALA API</a>
            <a href="{self.iskala_url}/docs" target="_blank" class="button">API Docs</a>
            
            <h2>🌟 Можливості ISKALA</h2>
            <div class="features">
                <div class="feature">
                    <h3>🌳 MOVA Trees</h3>
                    <p>Створення дерев сенсів</p>
                </div>
                <div class="feature">
                    <h3>🔍 RAG System</h3>
                    <p>Пошук та аналіз документів</p>
                </div>
                <div class="feature">
                    <h3>🌐 Translation</h3>
                    <p>Переклад та локалізація</p>
                </div>
                <div class="feature">
                    <h3>🔐 Vault</h3>
                    <p>Безпечне зберігання</p>
                </div>
                <div class="feature">
                    <h3>🛡️ Shield</h3>
                    <p>Безпека та валідація</p>
                </div>
            </div>
        </div>
        
        <div class="panel">
            <h2>💬 Інтегрований чат</h2>
            <iframe src="{self.openwebui_url}" class="iframe-container"></iframe>
        </div>
    </div>

    <script>
        // Перевірка статусу сервісів
        async function checkStatus() {{
            // Перевірка ISKALA
            try {{
                const iskalaResponse = await fetch('{self.iskala_url}/health');
                const iskalaStatus = document.getElementById('iskala-status');
                if (iskalaResponse.ok) {{
                    iskalaStatus.textContent = '✅ ISKALA онлайн';
                    iskalaStatus.className = 'status online';
                }} else {{
                    iskalaStatus.textContent = '❌ ISKALA офлайн';
                    iskalaStatus.className = 'status offline';
                }}
            }} catch (e) {{
                document.getElementById('iskala-status').textContent = '❌ ISKALA недоступний';
                document.getElementById('iskala-status').className = 'status offline';
            }}
            
            // Перевірка Open WebUI
            try {{
                const webuiResponse = await fetch('{self.openwebui_url}/api/health');
                const webuiStatus = document.getElementById('openwebui-status');
                if (webuiResponse.ok) {{
                    webuiStatus.textContent = '✅ Open WebUI онлайн';
                    webuiStatus.className = 'status online';
                }} else {{
                    webuiStatus.textContent = '❌ Open WebUI офлайн';
                    webuiStatus.className = 'status offline';
                }}
            }} catch (e) {{
                document.getElementById('openwebui-status').textContent = '❌ Open WebUI недоступний';
                document.getElementById('openwebui-status').className = 'status offline';
            }}
        }}
        
        // Перевірка при завантаженні та кожні 30 секунд
        checkStatus();
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
"""
        
        interface_file = self.config_dir / "iskala_openwebui_integration.html"
        with open(interface_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Інтерфейс інтеграції створений: {interface_file}")
        return interface_file
    
    def create_startup_script(self):
        """Створення скрипту запуску"""
        script_content = f"""#!/bin/bash
# ISKALA + Open WebUI Startup Script

echo "🌺 Запуск ISKALA + Open WebUI Integration..."

# Перевірка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлений"
    exit 1
fi

# Запуск ISKALA
echo "🚀 Запуск ISKALA..."
docker-compose -f docker-compose.iskala.yml up -d

# Очікування запуску ISKALA
echo "⏳ Очікування запуску ISKALA..."
sleep 10

# Перевірка Open WebUI
echo "🔍 Перевірка Open WebUI..."
if docker ps | grep -q open-webui; then
    echo "✅ Open WebUI вже запущений"
else
    echo "🚀 Запуск Open WebUI..."
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
fi

# Очікування запуску Open WebUI
echo "⏳ Очікування запуску Open WebUI..."
sleep 15

# Відкриття інтерфейсу
echo "🌐 Відкриття інтерфейсу інтеграції..."
if command -v xdg-open &> /dev/null; then
    xdg-open "{self.config_dir}/iskala_openwebui_integration.html"
elif command -v open &> /dev/null; then
    open "{self.config_dir}/iskala_openwebui_integration.html"
else
    echo "📋 Відкрийте в браузері: {self.config_dir}/iskala_openwebui_integration.html"
fi

echo "✅ Інтеграція готова!"
echo "🌺 ISKALA: http://localhost:8001"
echo "🤖 Open WebUI: http://localhost:3000"
echo "🔗 Інтеграція: {self.config_dir}/iskala_openwebui_integration.html"
"""
        
        script_file = self.config_dir / "start_integration.sh"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Робимо скрипт виконуваним
        os.chmod(script_file, 0o755)
        
        print(f"✅ Скрипт запуску створений: {script_file}")
        return script_file
    
    def create_windows_batch(self):
        """Створення batch файлу для Windows"""
        batch_content = f"""@echo off
REM ISKALA + Open WebUI Integration Startup Script

echo 🌺 Запуск ISKALA + Open WebUI Integration...

REM Перевірка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не встановлений
    pause
    exit /b 1
)

REM Запуск ISKALA
echo 🚀 Запуск ISKALA...
docker-compose -f docker-compose.iskala.yml up -d

REM Очікування запуску ISKALA
echo ⏳ Очікування запуску ISKALA...
timeout /t 10 /nobreak >nul

REM Перевірка Open WebUI
echo 🔍 Перевірка Open WebUI...
docker ps | findstr open-webui >nul
if errorlevel 1 (
    echo 🚀 Запуск Open WebUI...
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
) else (
    echo ✅ Open WebUI вже запущений
)

REM Очікування запуску Open WebUI
echo ⏳ Очікування запуску Open WebUI...
timeout /t 15 /nobreak >nul

REM Відкриття інтерфейсу
echo 🌐 Відкриття інтерфейсу інтеграції...
start "" "{self.config_dir}/iskala_openwebui_integration.html"

echo ✅ Інтеграція готова!
echo 🌺 ISKALA: http://localhost:8001
echo 🤖 Open WebUI: http://localhost:3000
echo 🔗 Інтеграція: {self.config_dir}/iskala_openwebui_integration.html
pause
"""
        
        batch_file = self.config_dir / "start_integration.bat"
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(batch_content)
        
        print(f"✅ Batch файл створений: {batch_file}")
        return batch_file
    
    def run_integration(self):
        """Запуск інтеграції"""
        print("🌺 Запуск інтеграції ISKALA + Open WebUI")
        print("=" * 50)
        
        # Створення конфігурації
        self.create_openwebui_config()
        
        # Створення інтерфейсу
        interface_file = self.create_iskala_webui_interface()
        
        # Створення скриптів запуску
        self.create_startup_script()
        self.create_windows_batch()
        
        # Перевірка статусу
        print("\n🔍 Перевірка статусу сервісів:")
        iskala_online = self.check_iskala_status()
        openwebui_online = self.check_openwebui_status()
        
        print("\n📋 Інструкції:")
        print("1. Запустіть ISKALA: docker-compose -f docker-compose.iskala.yml up -d")
        print("2. Запустіть Open WebUI: docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main")
        print(f"3. Відкрийте інтерфейс інтеграції: {interface_file}")
        
        if iskala_online and openwebui_online:
            print("\n✅ Обидва сервіси онлайн! Інтеграція готова до використання.")
        else:
            print("\n⚠️ Деякі сервіси офлайн. Перевірте їх статус перед використанням.")
        
        return interface_file

def main():
    integration = ISKALAOpenWebUIIntegration()
    integration.run_integration()

if __name__ == "__main__":
    main() 