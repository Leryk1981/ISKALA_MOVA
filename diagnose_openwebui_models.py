#!/usr/bin/env python3
"""
Скрипт для диагностики проблемы с моделями в Open WebUI
"""

import requests
import json
import time

def check_openwebui_status():
    """Проверка статуса Open WebUI"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI доступен")
            return True
        else:
            print(f"❌ Open WebUI недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Open WebUI: {e}")
        return False

def check_iskala_models():
    """Проверка моделей ISKALA"""
    try:
        response = requests.get("http://localhost:8001/api/openwebui/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Модели ISKALA доступны:")
            for model in models.get("models", []):
                print(f"   - {model['name']} ({model['id']})")
            return True
        else:
            print(f"❌ Ошибка получения моделей ISKALA: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к ISKALA: {e}")
        return False

def check_openwebui_models_public():
    """Проверка публичных моделей Open WebUI"""
    try:
        # Пробуем разные эндпоинты
        endpoints = [
            "http://localhost:3000/api/models",
            "http://localhost:3000/api/v1/models/",
            "http://localhost:3000/api/v1/models"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                print(f"📡 {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Модели доступны!")
                    return True
                elif response.status_code == 401:
                    print("🔐 Требуется аутентификация")
                else:
                    print(f"⚠️ Неожиданный ответ: {response.status_code}")
            except Exception as e:
                print(f"❌ Ошибка {endpoint}: {e}")
        
        return False
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return False

def check_ollama_connection():
    """Проверка подключения к Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama доступен")
            return True
        else:
            print(f"❌ Ollama недоступен: {response.status_code}")
            return False
    except Exception as e:
        print("❌ Ollama не запущен (это нормально, если вы не используете Ollama)")
        return False

def show_solutions():
    """Показать решения проблемы"""
    print("\n🔧 Решения проблемы 'Нет моделей для выбора':")
    print("=" * 50)
    
    solutions = [
        {
            "step": 1,
            "title": "Войдите в Open WebUI",
            "description": "Откройте http://localhost:3000 и войдите в систему"
        },
        {
            "step": 2,
            "title": "Проверьте раздел Models",
            "description": "Settings → Models - здесь должны быть доступные модели"
        },
        {
            "step": 3,
            "title": "Добавьте модель вручную",
            "description": "Нажмите 'Add Model' и настройте OpenRouter"
        },
        {
            "step": 4,
            "title": "Проверьте права доступа",
            "description": "Убедитесь, что у вас есть права администратора"
        },
        {
            "step": 5,
            "title": "Перезапустите Open WebUI",
            "description": "docker restart open-webui"
        }
    ]
    
    for solution in solutions:
        print(f"\n{solution['step']}. {solution['title']}")
        print(f"   {solution['description']}")

def show_manual_setup():
    """Показать ручную настройку"""
    print("\n📋 Ручная настройка модели OpenRouter:")
    print("=" * 50)
    
    print("1. Откройте http://localhost:3000")
    print("2. Войдите в систему")
    print("3. Перейдите в Settings → Models")
    print("4. Нажмите 'Add Model'")
    print("5. Заполните форму:")
    print("   Provider: OpenRouter")
    print("   Base URL: https://openrouter.ai/api/v1")
    print("   Model Name: moonshotai/kimi-k2")
    print("   API Key: ваш_ключ_openrouter")
    print("   Context Length: 8192")
    print("6. Нажмите 'Save'")

def check_docker_logs():
    """Проверка логов Docker"""
    print("\n📋 Проверьте логи Open WebUI:")
    print("docker logs open-webui --tail 20")
    print("\n📋 Проверьте логи ISKALA:")
    print("docker logs iskala-core --tail 20")

def main():
    print("🔍 Диагностика проблемы с моделями Open WebUI")
    print("=" * 50)
    
    # Проверки
    check_openwebui_status()
    check_iskala_models()
    check_openwebui_models_public()
    check_ollama_connection()
    
    # Решения
    show_solutions()
    show_manual_setup()
    check_docker_logs()
    
    print("\n" + "=" * 50)
    print("💡 Основные причины отсутствия моделей:")
    print("1. Не вошли в систему Open WebUI")
    print("2. Нет настроенных моделей")
    print("3. Проблемы с правами доступа")
    print("4. Open WebUI не полностью загрузился")
    
    print("\n🚀 Следующие шаги:")
    print("1. Откройте http://localhost:3000")
    print("2. Войдите в систему")
    print("3. Добавьте модель OpenRouter вручную")
    print("4. Если не получается - перезапустите Open WebUI")

if __name__ == "__main__":
    main() 