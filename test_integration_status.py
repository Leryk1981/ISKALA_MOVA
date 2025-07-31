#!/usr/bin/env python3
"""
Тест статуса интеграции ISKALA + Open WebUI
"""

import requests
import time
import json

def check_service(url, name):
    """Проверка статуса сервиса"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: ONLINE")
            return True
        else:
            print(f"⚠️ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: OFFLINE - {e}")
        return False

def main():
    print("🌺 Проверка статуса интеграции ISKALA + Open WebUI")
    print("=" * 50)
    
    services = [
        ("http://localhost:8001/health", "ISKALA Core"),
        ("http://localhost:3000/api/health", "Open WebUI"),
        ("http://localhost:5000", "ISKALA Viewer"),
        ("http://localhost:8081/vault/health", "Vault API"),
        ("http://localhost:8082/translation/health", "Translation API"),
        ("http://localhost:8002/rag/health", "RAG API")
    ]
    
    results = []
    for url, name in services:
        result = check_service(url, name)
        results.append((name, result))
        time.sleep(1)
    
    print("\n📊 Результаты:")
    print("-" * 30)
    
    online_count = sum(1 for _, status in results if status)
    total_count = len(results)
    
    for name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}")
    
    print(f"\n🎯 Итого: {online_count}/{total_count} сервисов онлайн")
    
    if online_count == total_count:
        print("🎉 Вся интеграция работает!")
    elif online_count >= 2:
        print("👍 Основные сервисы работают")
    else:
        print("⚠️ Требуется проверка конфигурации")
    
    # Проверка интеграционного интерфейса
    print("\n🔗 Интеграционный интерфейс:")
    integration_file = "openwebui_integration/iskala_openwebui_integration.html"
    try:
        with open(integration_file, 'r', encoding='utf-8') as f:
            print(f"✅ Файл интеграции найден: {integration_file}")
    except FileNotFoundError:
        print(f"❌ Файл интеграции не найден: {integration_file}")

if __name__ == "__main__":
    main() 