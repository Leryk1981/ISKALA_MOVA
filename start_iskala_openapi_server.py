#!/usr/bin/env python3
"""
Скрипт для запуску та перевірки ISKALA OpenAPI Tool Server
"""

import subprocess
import time
import requests
import json
import sys
import os

def check_port_available(port):
    """Перевіряє чи порт доступний"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0
    except:
        return False

def check_iskala_modules():
    """Перевіряє статус модулів ISKALA"""
    print("🔍 Перевірка статусу модулів ISKALA...")
    
    modules = {
        "ISKALA Core": "http://localhost:8001/health",
        "Vault": "http://localhost:8081/health", 
        "Translation": "http://localhost:8082/health",
        "RAG": "http://localhost:8002/health"
    }
    
    status = {}
    for name, url in modules.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: працює")
                status[name] = "healthy"
            else:
                print(f"⚠️ {name}: відповідає з кодом {response.status_code}")
                status[name] = "unhealthy"
        except Exception as e:
            print(f"❌ {name}: недоступний ({str(e)})")
            status[name] = "error"
    
    return status

def start_openapi_server():
    """Запускає OpenAPI Tool Server"""
    print("🚀 Запуск ISKALA OpenAPI Tool Server...")
    
    if not check_port_available(8003):
        print("❌ Порт 8003 вже зайнятий")
        return False
    
    try:
        # Запускаємо сервер в фоновому режимі
        process = subprocess.Popen([
            sys.executable, "iskala_openapi_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Чекаємо поки сервер запуститься
        time.sleep(3)
        
        # Перевіряємо чи сервер відповідає
        try:
            response = requests.get("http://localhost:8003/", timeout=5)
            if response.status_code == 200:
                print("✅ OpenAPI Tool Server запущений успішно")
                return True
            else:
                print(f"❌ Сервер відповідає з кодом {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Не вдалося підключитися до сервера: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка запуску сервера: {str(e)}")
        return False

def test_openapi_endpoints():
    """Тестує OpenAPI ендпоінти"""
    print("\n🧪 Тестування OpenAPI ендпоінтів...")
    
    base_url = "http://localhost:8003"
    
    # Тест 1: OpenAPI схема
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            print("✅ OpenAPI схема доступна")
        else:
            print(f"❌ OpenAPI схема недоступна: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка отримання OpenAPI схеми: {str(e)}")
    
    # Тест 2: Статус модулів
    try:
        response = requests.get(f"{base_url}/iskala/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Статус модулів отримано:")
            for module, info in status.items():
                print(f"   - {module}: {info.get('status', 'unknown')}")
        else:
            print(f"❌ Статус модулів недоступний: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка отримання статусу: {str(e)}")

def show_integration_instructions():
    """Показує інструкції по інтеграції"""
    print("\n🔧 ІНСТРУКЦІЇ ПО ІНТЕГРАЦІЇ В OPEN WEBUI:")
    print("=" * 50)
    print("1. Відкрийте Open WebUI: http://localhost:3000")
    print("2. Перейдіть в Settings → Tools")
    print("3. Натисніть 'Add Tool'")
    print("4. Виберіть 'OpenAPI Tool Server'")
    print("5. Заповніть поля:")
    print("   - Name: ISKALA Modules")
    print("   - URL: http://localhost:8003/openapi.json")
    print("   - Description: Модулі ISKALA для роботи з пам'яттю, перекладом та RAG")
    print("6. Збережіть налаштування")
    print("\n📋 Доступні функції:")
    print("- search_iskala_memory - пошук в пам'яті")
    print("- call_iskala_tool - виклик інструментів")
    print("- translate_text - переклад тексту")
    print("- rag_search - RAG пошук")
    print("- get_iskala_status - статус модулів")

def main():
    """Головна функція"""
    print("🌺 ISKALA OpenAPI Tool Server - Запуск та перевірка")
    print("=" * 60)
    
    # Перевіряємо модулі ISKALA
    module_status = check_iskala_modules()
    
    # Запускаємо OpenAPI сервер
    if start_openapi_server():
        # Тестуємо ендпоінти
        test_openapi_endpoints()
        
        # Показуємо інструкції
        show_integration_instructions()
        
        print("\n" + "=" * 60)
        print("✅ ISKALA OpenAPI Tool Server готовий до використання!")
        print("🌐 URL: http://localhost:8003/openapi.json")
        print("📖 Документація: ISKALA_API_INTEGRATION_GUIDE.md")
        
    else:
        print("\n❌ Не вдалося запустити OpenAPI Tool Server")
        print("🔧 Перевірте:")
        print("   - Чи запущені модулі ISKALA")
        print("   - Чи не зайнятий порт 8003")
        print("   - Чи є файл iskala_openapi_server.py")

if __name__ == "__main__":
    main() 