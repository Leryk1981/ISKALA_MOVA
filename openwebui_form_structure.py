#!/usr/bin/env python3
"""
Скрипт для анализа структуры формы добавления моделей в Open WebUI
"""

import requests
import json
import time

def analyze_openwebui_form():
    """Анализ структуры формы Open WebUI"""
    print("🔍 Анализ структуры формы Open WebUI")
    print("=" * 50)
    
    # Проверяем доступность Open WebUI
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Open WebUI доступен")
        else:
            print("❌ Open WebUI недоступен")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return

def show_form_fields():
    """Показать все поля формы"""
    print("\n📝 Поля формы 'Add Model' в Open WebUI:")
    print("-" * 30)
    
    fields = [
        {
            "name": "Provider",
            "type": "dropdown",
            "required": True,
            "options": ["OpenAI", "OpenRouter", "Anthropic", "Google", "Custom", "Ollama"],
            "description": "Выберите провайдера модели"
        },
        {
            "name": "Base URL", 
            "type": "text",
            "required": True,
            "default": "https://openrouter.ai/api/v1",
            "description": "Базовый URL API"
        },
        {
            "name": "Model Name",
            "type": "text", 
            "required": True,
            "examples": ["moonshotai/kimi-k2", "openai/gpt-4o-mini"],
            "description": "Точное название модели"
        },
        {
            "name": "API Key",
            "type": "password",
            "required": True,
            "format": "sk-or-v1-...",
            "description": "Ключ API для аутентификации"
        },
        {
            "name": "Context Length",
            "type": "number",
            "required": False,
            "default": 8192,
            "description": "Максимальная длина контекста в токенах"
        },
        {
            "name": "Temperature",
            "type": "number",
            "required": False,
            "default": 0.7,
            "range": "0.0 - 2.0",
            "description": "Температура генерации"
        },
        {
            "name": "Max Tokens",
            "type": "number",
            "required": False,
            "default": 4096,
            "description": "Максимальное количество токенов в ответе"
        }
    ]
    
    for i, field in enumerate(fields, 1):
        print(f"\n{i}. {field['name']}")
        print(f"   Тип: {field['type']}")
        print(f"   Обязательное: {'Да' if field['required'] else 'Нет'}")
        print(f"   Описание: {field['description']}")
        
        if 'options' in field:
            print(f"   Варианты: {', '.join(field['options'])}")
        if 'default' in field:
            print(f"   По умолчанию: {field['default']}")
        if 'examples' in field:
            print(f"   Примеры: {', '.join(field['examples'])}")
        if 'format' in field:
            print(f"   Формат: {field['format']}")
        if 'range' in field:
            print(f"   Диапазон: {field['range']}")

def show_openrouter_example():
    """Показать пример настройки OpenRouter"""
    print("\n🎯 Пример настройки OpenRouter:")
    print("-" * 30)
    
    example = {
        "Provider": "OpenRouter",
        "Base URL": "https://openrouter.ai/api/v1", 
        "Model Name": "moonshotai/kimi-k2",
        "API Key": "sk-or-v1-ваш_ключ_здесь",
        "Context Length": 8192,
        "Temperature": 0.7,
        "Max Tokens": 4096
    }
    
    for field, value in example.items():
        print(f"{field}: {value}")

def show_common_models():
    """Показать популярные модели"""
    print("\n📋 Популярные модели OpenRouter:")
    print("-" * 30)
    
    models = [
        {
            "name": "moonshotai/kimi-k2",
            "provider": "Moonshot AI",
            "context": 8192,
            "free_requests": 100,
            "description": "Хорошо подходит для кода и анализа"
        },
        {
            "name": "openai/gpt-4o-mini",
            "provider": "OpenAI",
            "context": 128000,
            "free_requests": 500,
            "description": "Универсальная модель"
        },
        {
            "name": "anthropic/claude-3-haiku",
            "provider": "Anthropic",
            "context": 200000,
            "free_requests": 100,
            "description": "Быстрая и эффективная"
        },
        {
            "name": "google/gemini-pro",
            "provider": "Google",
            "context": 32768,
            "free_requests": 100,
            "description": "Экономичная модель"
        }
    ]
    
    for i, model in enumerate(models, 1):
        print(f"\n{i}. {model['name']}")
        print(f"   Провайдер: {model['provider']}")
        print(f"   Контекст: {model['context']} токенов")
        print(f"   Бесплатно: {model['free_requests']} запросов/день")
        print(f"   Описание: {model['description']}")

def show_troubleshooting():
    """Показать решения проблем"""
    print("\n🔧 Решения частых проблем:")
    print("-" * 30)
    
    problems = [
        {
            "problem": "Не вижу поле 'Model Name'",
            "solution": "1. Выберите 'Custom' вместо 'OpenRouter'\n2. Проверьте правильность Base URL\n3. Обновите страницу"
        },
        {
            "problem": "Ошибка 'Invalid API key'",
            "solution": "1. Проверьте, что ключ начинается с 'sk-or-v1-'\n2. Убедитесь, что ключ активен\n3. Проверьте баланс на OpenRouter"
        },
        {
            "problem": "Ошибка 'Model not found'",
            "solution": "1. Проверьте точное название модели\n2. Убедитесь, что модель доступна\n3. Попробуйте другую модель"
        },
        {
            "problem": "Форма не открывается",
            "solution": "1. Обновите страницу (F5)\n2. Попробуйте другой браузер\n3. Проверьте логи Open WebUI"
        }
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. {problem['problem']}")
        print(f"   Решение: {problem['solution']}")

def main():
    print("🌺 Анализ формы Open WebUI")
    print("=" * 50)
    
    analyze_openwebui_form()
    show_form_fields()
    show_openrouter_example()
    show_common_models()
    show_troubleshooting()
    
    print("\n" + "=" * 50)
    print("📋 Пошаговая инструкция:")
    print("1. Откройте http://localhost:3000")
    print("2. Settings → Models → Add Model")
    print("3. Заполните поля согласно примеру выше")
    print("4. Нажмите 'Save'")
    
    print("\n💡 Важные замечания:")
    print("- Поле 'Model Name' появляется после выбора Provider")
    print("- Если 'OpenRouter' нет в списке, используйте 'Custom'")
    print("- Base URL должен быть точно: https://openrouter.ai/api/v1")
    print("- API ключ должен начинаться с 'sk-or-v1-'")

if __name__ == "__main__":
    main() 