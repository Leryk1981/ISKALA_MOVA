#!/usr/bin/env python3
"""
Скрипт проверки интеграции ISKALA + Open WebUI
"""

import requests
import json
import time

def check_iskala_status():
    """Проверка статуса ISKALA"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ ISKALA Core: ОНЛАЙН")
            return True
        else:
            print("❌ ISKALA Core: ОФЛАЙН")
            return False
    except Exception as e:
        print(f"❌ ISKALA Core: ОШИБКА - {e}")
        return False

def check_openwebui_status():
    """Проверка статуса Open WebUI"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI: ОНЛАЙН")
            return True
        else:
            print("❌ Open WebUI: ОФЛАЙН")
            return False
    except Exception as e:
        print(f"❌ Open WebUI: ОШИБКА - {e}")
        return False

def check_iskala_models():
    """Проверка моделей ISKALA"""
    try:
        response = requests.get("http://localhost:8001/api/openwebui/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Модели ISKALA:")
            for model in models.get("models", []):
                print(f"   - {model['name']} ({model['id']})")
            return True
        else:
            print("❌ Не удалось получить модели ISKALA")
            return False
    except Exception as e:
        print(f"❌ Ошибка получения моделей: {e}")
        return False

def test_iskala_chat():
    """Тест чата с ISKALA"""
    try:
        data = {
            "message": "Привіт! Як справи?",
            "model_id": "iskala-mova-v2"
        }
        response = requests.post(
            "http://localhost:8001/api/openwebui/chat",
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Чат ISKALA: РАБОТАЕТ")
            print(f"   Ответ: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"❌ Ошибка чата: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка теста чата: {e}")
        return False

def check_openrouter_key():
    """Проверка ключа OpenRouter"""
    try:
        # Проверяем через ISKALA API
        response = requests.get("http://localhost:8001/api/openwebui/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print("✅ Статус интеграции ISKALA:")
            for component, status_val in status.get("components", {}).items():
                status_icon = "✅" if status_val else "❌"
                print(f"   {status_icon} {component}")
            return True
        else:
            print("❌ Не удалось проверить статус")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

def main():
    print("🌺 Проверка интеграции ISKALA + Open WebUI")
    print("=" * 50)
    
    # Проверки
    iskala_ok = check_iskala_status()
    openwebui_ok = check_openwebui_status()
    
    if iskala_ok:
        check_iskala_models()
        check_openrouter_key()
        test_iskala_chat()
    
    print("\n" + "=" * 50)
    print("📋 Инструкции по настройке:")
    print("1. Откройте http://localhost:3000")
    print("2. Войдите в Open WebUI")
    print("3. Перейдите в Settings → Models")
    print("4. Добавьте модели ISKALA:")
    print("   - Provider: Custom")
    print("   - Base URL: http://localhost:8001")
    print("   - Model Name: iskala-mova-v2")
    print("   - API Key: (оставьте пустым)")
    print("\n5. Для OpenRouter добавьте:")
    print("   - Provider: OpenRouter")
    print("   - Base URL: https://openrouter.ai/api/v1")
    print("   - Model Name: moonshotai/kimi-k2")
    print("   - API Key: ваш_ключ_openrouter")
    
    print("\n🌐 Доступные интерфейсы:")
    print("- Open WebUI: http://localhost:3000")
    print("- ISKALA API: http://localhost:8001")
    print("- ISKALA Viewer: http://localhost:5000")

if __name__ == "__main__":
    main() 