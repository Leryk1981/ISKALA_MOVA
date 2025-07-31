#!/usr/bin/env python3
"""
Скрипт для добавления моделей ISKALA в Open WebUI
"""

import requests
import json
import time

def get_iskala_models():
    """Получить список моделей ISKALA"""
    try:
        response = requests.get("http://localhost:8001/api/openwebui/models", timeout=5)
        if response.status_code == 200:
            return response.json().get("models", [])
        else:
            print(f"❌ Ошибка получения моделей ISKALA: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Ошибка подключения к ISKALA: {e}")
        return []

def create_iskala_model_config(model):
    """Создать конфигурацию модели ISKALA для Open WebUI"""
    return {
        "name": model["name"],
        "model": model["id"],
        "base_url": "http://localhost:8001",
        "api_key": "",  # ISKALA не требует API ключ
        "context_length": model.get("context_length", 8192),
        "temperature": 0.7,
        "max_tokens": 4096,
        "provider": "Custom"
    }

def show_iskala_models_setup():
    """Показать инструкцию по настройке моделей ISKALA"""
    print("\n🎯 Настройка моделей ISKALA в Open WebUI:")
    print("=" * 50)
    
    models = get_iskala_models()
    
    if not models:
        print("❌ Не удалось получить модели ISKALA")
        return
    
    print("✅ Найдены модели ISKALA:")
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['name']} ({model['id']})")
        print(f"   Описание: {model.get('description', 'Нет описания')}")
        
        # Показать конфигурацию для Open WebUI
        config = create_iskala_model_config(model)
        print(f"   Конфигурация для Open WebUI:")
        print(f"   - Provider: {config['provider']}")
        print(f"   - Base URL: {config['base_url']}")
        print(f"   - Model Name: {config['model']}")
        print(f"   - API Key: (оставьте пустым)")
        print(f"   - Context Length: {config['context_length']}")

def show_manual_setup_steps():
    """Показать пошаговую инструкцию"""
    print("\n📋 Пошаговая инструкция добавления ISKALA:")
    print("=" * 50)
    
    steps = [
        "1. Откройте http://localhost:3000",
        "2. Войдите в систему Open WebUI",
        "3. Перейдите в Settings → Models",
        "4. Нажмите 'Add Model'",
        "5. Заполните форму для каждой модели ISKALA:",
        "",
        "   Для ISKALA MOVA v2:",
        "   - Provider: Custom",
        "   - Base URL: http://localhost:8001",
        "   - Model Name: iskala-mova-v2",
        "   - API Key: (оставьте пустым)",
        "   - Context Length: 8192",
        "",
        "   Для ISKALA RAG:",
        "   - Provider: Custom",
        "   - Base URL: http://localhost:8001",
        "   - Model Name: iskala-rag",
        "   - API Key: (оставьте пустым)",
        "   - Context Length: 16384",
        "",
        "   Для ISKALA Translation:",
        "   - Provider: Custom",
        "   - Base URL: http://localhost:8001",
        "   - Model Name: iskala-translation",
        "   - API Key: (оставьте пустым)",
        "   - Context Length: 4096",
        "",
        "6. Нажмите 'Save' для каждой модели",
        "7. Модели появятся в списке доступных"
    ]
    
    for step in steps:
        print(f"   {step}")

def show_quick_test():
    """Показать быстрый тест моделей"""
    print("\n🧪 Быстрый тест моделей ISKALA:")
    print("=" * 50)
    
    test_models = [
        {
            "name": "ISKALA MOVA v2",
            "id": "iskala-mova-v2",
            "test_message": "Привіт! Як справи?"
        },
        {
            "name": "ISKALA RAG",
            "id": "iskala-rag",
            "test_message": "Розкажи про ISKALA RAG систему"
        },
        {
            "name": "ISKALA Translation",
            "id": "iskala-translation",
            "test_message": "Переклади 'Hello world' на українську"
        }
    ]
    
    for model in test_models:
        print(f"\n📌 Тест {model['name']}:")
        print(f"   ID: {model['id']}")
        print(f"   Тестовое сообщение: '{model['test_message']}'")
        print(f"   API: POST http://localhost:8001/api/openwebui/chat")
        print(f"   Body: {{\"message\": \"{model['test_message']}\", \"model_id\": \"{model['id']}\"}}")

def show_troubleshooting():
    """Показать устранение неполадок"""
    print("\n🔧 Устранение неполадок:")
    print("=" * 50)
    
    problems = [
        {
            "problem": "Модели ISKALA не появляются в списке",
            "solution": "1. Проверьте, что ISKALA Core запущен\n2. Убедитесь, что Base URL правильный: http://localhost:8001\n3. Проверьте логи ISKALA: docker logs iskala-core"
        },
        {
            "problem": "Ошибка подключения к ISKALA",
            "solution": "1. Проверьте статус контейнера: docker ps\n2. Перезапустите ISKALA: docker restart iskala-core\n3. Проверьте порт 8001: curl http://localhost:8001/health"
        },
        {
            "problem": "Open WebUI не сохраняет модели",
            "solution": "1. Убедитесь, что вы вошли в систему\n2. Проверьте права доступа\n3. Попробуйте другой браузер\n4. Очистите кэш браузера"
        }
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. {problem['problem']}")
        print(f"   Решение: {problem['solution']}")

def main():
    print("🌺 Добавление моделей ISKALA в Open WebUI")
    print("=" * 50)
    
    # Проверка моделей ISKALA
    models = get_iskala_models()
    if models:
        print(f"✅ Найдено {len(models)} моделей ISKALA")
    else:
        print("❌ Модели ISKALA недоступны")
        return
    
    # Показать инструкции
    show_iskala_models_setup()
    show_manual_setup_steps()
    show_quick_test()
    show_troubleshooting()
    
    print("\n" + "=" * 50)
    print("💡 Важные замечания:")
    print("1. Модели ISKALA уже работают и готовы к использованию")
    print("2. Их нужно только добавить в интерфейс Open WebUI")
    print("3. Используйте Provider: Custom для всех моделей ISKALA")
    print("4. Base URL всегда: http://localhost:8001")
    print("5. API Key оставляйте пустым")
    
    print("\n🚀 Рекомендуемый порядок:")
    print("1. Сначала добавьте ISKALA MOVA v2 (основная модель)")
    print("2. Затем ISKALA RAG (для документов)")
    print("3. Потом ISKALA Translation (для перевода)")
    print("4. В последнюю очередь добавьте OpenRouter модели")

if __name__ == "__main__":
    main() 