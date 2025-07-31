#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации Open WebUI и создания тестовой модели
"""

import requests
import json
import time

def check_openwebui_health():
    """Проверка здоровья Open WebUI"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI доступен")
            return True
        else:
            print(f"❌ Open WebUI недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def check_openwebui_usage():
    """Проверка использования Open WebUI"""
    try:
        response = requests.get("http://localhost:3000/api/usage", timeout=5)
        if response.status_code == 200:
            print("✅ API usage доступен")
            return True
        else:
            print(f"❌ API usage недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка API usage: {e}")
        return False

def check_iskala_integration():
    """Проверка интеграции с ISKALA"""
    try:
        response = requests.get("http://localhost:8001/api/openwebui/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print("✅ Модели ISKALA доступны:")
            for model in models.get("models", []):
                print(f"   - {model['name']} ({model['id']})")
            return True
        else:
            print(f"❌ Ошибка ISKALA: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка ISKALA: {e}")
        return False

def show_openwebui_setup_guide():
    """Показать руководство по настройке Open WebUI"""
    print("\n📋 Руководство по настройке Open WebUI:")
    print("=" * 50)
    
    print("1. Откройте браузер: http://localhost:3000")
    print("2. Создайте аккаунт (если первый раз)")
    print("3. Войдите в систему")
    print("4. Перейдите в Settings → Models")
    print("5. Нажмите 'Add Model'")
    print("6. Заполните форму:")
    print("   Provider: OpenRouter")
    print("   Base URL: https://openrouter.ai/api/v1")
    print("   Model Name: moonshotai/kimi-k2")
    print("   API Key: ваш_ключ_openrouter")
    print("   Context Length: 8192")
    print("7. Нажмите 'Save'")

def show_alternative_solutions():
    """Показать альтернативные решения"""
    print("\n🔧 Альтернативные решения:")
    print("=" * 50)
    
    solutions = [
        {
            "title": "Использовать ISKALA модели",
            "description": "Модели ISKALA уже работают и доступны",
            "action": "Используйте ISKALA MOVA v2 вместо OpenRouter"
        },
        {
            "title": "Перезапустить Open WebUI",
            "description": "Полный перезапуск контейнера",
            "action": "docker-compose restart open-webui"
        },
        {
            "title": "Проверить права доступа",
            "description": "Убедиться, что у пользователя есть права администратора",
            "action": "Создайте нового пользователя с правами администратора"
        },
        {
            "title": "Использовать Custom провайдер",
            "description": "Вместо OpenRouter использовать Custom",
            "action": "Provider: Custom, Base URL: https://openrouter.ai/api/v1"
        }
    ]
    
    for i, solution in enumerate(solutions, 1):
        print(f"\n{i}. {solution['title']}")
        print(f"   {solution['description']}")
        print(f"   Действие: {solution['action']}")

def show_iskala_models_info():
    """Показать информацию о моделях ISKALA"""
    print("\n🎯 Модели ISKALA (уже работают):")
    print("=" * 50)
    
    models = [
        {
            "name": "ISKALA MOVA v2",
            "id": "iskala-mova-v2",
            "description": "Основная украинская модель",
            "features": ["Чат", "Анализ", "Контекст"]
        },
        {
            "name": "ISKALA RAG",
            "id": "iskala-rag",
            "description": "Система поиска в документах",
            "features": ["RAG", "Документы", "Поиск"]
        },
        {
            "name": "ISKALA Translation",
            "id": "iskala-translation",
            "description": "Система перевода",
            "features": ["Перевод", "Локализация"]
        }
    ]
    
    for model in models:
        print(f"\n📌 {model['name']}")
        print(f"   ID: {model['id']}")
        print(f"   Описание: {model['description']}")
        print(f"   Возможности: {', '.join(model['features'])}")

def show_troubleshooting_steps():
    """Показать шаги устранения неполадок"""
    print("\n🔍 Шаги устранения неполадок:")
    print("=" * 50)
    
    steps = [
        "1. Проверьте, что вы вошли в систему Open WebUI",
        "2. Убедитесь, что интерфейс полностью загрузился",
        "3. Проверьте, что у вас есть права администратора",
        "4. Попробуйте создать нового пользователя",
        "5. Проверьте логи: docker logs open-webui --tail 20",
        "6. Попробуйте другой браузер",
        "7. Очистите кэш браузера"
    ]
    
    for step in steps:
        print(f"   {step}")

def main():
    print("🔍 Проверка конфигурации Open WebUI")
    print("=" * 50)
    
    # Проверки
    check_openwebui_health()
    check_openwebui_usage()
    check_iskala_integration()
    
    # Информация
    show_iskala_models_info()
    show_openwebui_setup_guide()
    show_alternative_solutions()
    show_troubleshooting_steps()
    
    print("\n" + "=" * 50)
    print("💡 Рекомендации:")
    print("1. Сначала попробуйте использовать модели ISKALA")
    print("2. Если нужен OpenRouter - следуйте руководству выше")
    print("3. Если ничего не работает - перезапустите Open WebUI")
    
    print("\n🚀 Быстрый старт:")
    print("1. Откройте http://localhost:3000")
    print("2. Войдите в систему")
    print("3. Используйте ISKALA MOVA v2 для начала")

if __name__ == "__main__":
    main() 