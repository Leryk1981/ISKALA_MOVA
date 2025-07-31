"""
ISKALA Launcher
Запуск повної системи для першого зерна
"""

import os
import sys
import subprocess
import webbrowser
import time

def start_system():
    print("🌱 Запуск ISKALA - Перше Зерно")
    print("=" * 50)

    # Start the API server
    print("📡 Запуск API сервера...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "api_server:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ], cwd="/a0/instruments/custom/iskala")

    time.sleep(2)

    # Open the interface
    print("🌺 Відкриття інтерфейсу...")
    interface_url = "file:///a0/instruments/custom/iskala/index.html"

    print("✅ Система готова!")
    print("🌟 Відкрийте в браузері:")
    print(f"   Інтерфейс: {interface_url}")
    print("   API: http://localhost:8000")
    print("   API docs: http://localhost:8000/docs")

    # Keep the process running
    try:
        api_process.wait()
    except KeyboardInterrupt:
        print("
🛑 Зупинка системи...")
        api_process.terminate()
        api_process.wait()

if __name__ == "__main__":
    start_system()
