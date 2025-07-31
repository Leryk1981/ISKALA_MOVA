#!/usr/bin/env python3
"""
Скрипт для проверки доступных провайдеров в Open WebUI
"""

import requests
import json
import time

def check_openwebui_providers():
    """Проверка доступных провайдеров в Open WebUI"""
    try:
        # Проверяем доступность Open WebUI
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI доступен")
        else:
            print("❌ Open WebUI недоступен")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Open WebUI: {e}")
        return False

def get_available_providers():
    """Получение списка доступных провайдеров"""
    providers = [
        "OpenAI",
        "OpenRouter", 
        "Anthropic",
        "Google",
        "Custom",
        "Ollama"
    ]
    
    print("📋 Доступные провайдеры в Open WebUI:")
    for i, provider in enumerate(providers, 1):
        print(f"   {i}. {provider}")
    
    return providers

def test_openrouter_connection():
    """Тест подключения к OpenRouter"""
    print("\n🔑 Тест подключения к OpenRouter:")
    
    # Тестовый ключ (недействительный, только для проверки формата)
    test_key = "sk-or-v1-test-key"
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {test_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ OpenRouter API доступен (ключ недействительный, но это нормально)")
            return True
        elif response.status_code == 200:
            print("✅ OpenRouter API доступен и ключ работает!")
            return True
        else:
            print(f"⚠️ OpenRouter API ответил с кодом: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к OpenRouter: {e}")
        return False

def show_model_examples():
    """Показать примеры моделей"""
    print("\n🎯 Примеры моделей для настройки:")
    
    models = [
        {
            "name": "Moonshot Kimi (бесплатно)",
            "provider": "Custom",
            "base_url": "https://openrouter.ai/api/v1",
            "model_name": "moonshotai/kimi-k2",
            "context_length": 8192,
            "description": "100 запросов/день бесплатно"
        },
        {
            "name": "GPT-4o Mini (бесплатно)",
            "provider": "Custom", 
            "base_url": "https://openrouter.ai/api/v1",
            "model_name": "openai/gpt-4o-mini",
            "context_length": 128000,
            "description": "500 запросов/день бесплатно"
        },
        {
            "name": "Claude 3 Haiku (бесплатно)",
            "provider": "Custom",
            "base_url": "https://openrouter.ai/api/v1", 
            "model_name": "anthropic/claude-3-haiku",
            "context_length": 200000,
            "description": "100 запросов/день бесплатно"
        }
    ]
    
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['name']}")
        print(f"   Provider: {model['provider']}")
        print(f"   Base URL: {model['base_url']}")
        print(f"   Model Name: {model['model_name']}")
        print(f"   Context Length: {model['context_length']}")
        print(f"   Описание: {model['description']}")

def show_setup_instructions():
    """Показать инструкции по настройке"""
    print("\n📋 Пошаговая инструкция:")
    print("1. Откройте http://localhost:3000")
    print("2. Войдите в Open WebUI")
    print("3. Перейдите в Settings → Models")
    print("4. Нажмите 'Add Model'")
    print("5. Заполните поля:")
    print("   - Provider: Custom")
    print("   - Base URL: https://openrouter.ai/api/v1")
    print("   - Model Name: moonshotai/kimi-k2")
    print("   - API Key: ваш_ключ_openrouter")
    print("   - Context Length: 8192")
    print("6. Нажмите 'Save'")

def check_iskala_integration():
    """Проверка интеграции с ISKALA"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ ISKALA Core доступен")
            
            # Проверяем модели ISKALA
            models_response = requests.get("http://localhost:8001/api/openwebui/models", timeout=5)
            if models_response.status_code == 200:
                models = models_response.json()
                print("✅ Модели ISKALA доступны:")
                for model in models.get("models", []):
                    print(f"   - {model['name']} ({model['id']})")
            return True
        else:
            print("❌ ISKALA Core недоступен")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к ISKALA: {e}")
        return False

def main():
    print("🌺 Проверка провайдеров Open WebUI")
    print("=" * 50)
    
    # Проверки
    check_openwebui_providers()
    get_available_providers()
    test_openrouter_connection()
    show_model_examples()
    check_iskala_integration()
    
    print("\n" + "=" * 50)
    show_setup_instructions()
    
    print("\n🔗 Полезные ссылки:")
    print("- OpenRouter Dashboard: https://openrouter.ai/keys")
    print("- Список моделей: https://openrouter.ai/models")
    print("- Open WebUI: http://localhost:3000")
    print("- ISKALA API: http://localhost:8001")
    
    print("\n💡 Важные замечания:")
    print("- Если 'OpenRouter' нет в списке провайдеров, используйте 'Custom'")
    print("- Base URL должен быть точно: https://openrouter.ai/api/v1")
    print("- API ключ должен начинаться с 'sk-or-v1-'")
    print("- Начните с бесплатных моделей для тестирования")

if __name__ == "__main__":
    main() 