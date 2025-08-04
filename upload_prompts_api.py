#!/usr/bin/env python3
"""
Скрипт для загрузки промптов MOVA через API Open WebUI
"""

import requests
import json
import sys
from pathlib import Path

# Конфигурация
OPENWEBUI_URL = "http://localhost:3000"
API_BASE = f"{OPENWEBUI_URL}/api/v1"

def load_json_file(file_path):
    """Загружает JSON файл"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки файла {file_path}: {e}")
        return None

def get_auth_token():
    """Получает токен аутентификации"""
    try:
        # Попробуем получить токен через API
        response = requests.get(f"{OPENWEBUI_URL}/api/config")
        if response.status_code == 200:
            print("✅ Open WebUI доступен")
            return None  # Возможно, аутентификация не требуется
        else:
            print(f"⚠️ Статус Open WebUI: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка подключения к Open WebUI: {e}")
        return None

def upload_prompts_via_api(prompts_data, category="MOVA"):
    """Загружает промпты через API"""

    # Получаем токен аутентификации
    token = get_auth_token()
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Загружаем каждый промпт
    success_count = 0
    for prompt in prompts_data:
        title = prompt.get('title', 'Untitled')
        content = prompt.get('content', '')
        tags = prompt.get('tags', [])

        # Создаем промпт через API
        prompt_data = {
            "name": title,
            "content": content,
            "category": category,
            "tags": tags
        }

        try:
            response = requests.post(f"{API_BASE}/prompts/", json=prompt_data, headers=headers)
            if response.status_code in [200, 201]:
                print(f"✅ Загружен промпт: {title}")
                success_count += 1
            else:
                print(f"❌ Ошибка загрузки промпта '{title}': {response.status_code}")
                print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка загрузки промпта '{title}': {e}")

    return success_count

def test_api_endpoints():
    """Тестирует доступные API endpoints"""
    print("🔍 Тестирование API endpoints...")
    
    endpoints = [
        "/api/config",
        "/api/v1/prompts/",
        "/api/v1/models/",
        "/api/v1/auths/signin"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{OPENWEBUI_URL}{endpoint}")
            print(f"  {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"  {endpoint}: ERROR - {e}")

def main():
    """Основная функция"""
    print("🚀 Загрузка промптов MOVA через API Open WebUI")
    print("=" * 50)

    # Тестируем API endpoints
    test_api_endpoints()
    print()

    # Проверяем доступность Open WebUI
    try:
        response = requests.get(f"{OPENWEBUI_URL}/api/config")
        if response.status_code != 200:
            print(f"❌ Open WebUI недоступен: {response.status_code}")
            return
        print("✅ Open WebUI доступен")
    except Exception as e:
        print(f"❌ Ошибка подключения к Open WebUI: {e}")
        return

    # Загружаем ультра простой тест
    prompts_file = Path("openwebui_prompts/ultra_simple_test.json")
    if not prompts_file.exists():
        print(f"❌ Файл {prompts_file} не найден")
        return

    prompts_data = load_json_file(prompts_file)
    if not prompts_data:
        return

    print(f"📁 Загружено {len(prompts_data)} промптов из файла")

    # Загружаем через API
    success_count = upload_prompts_via_api(prompts_data, "Test")

    print("=" * 50)
    print(f"✅ Успешно загружено: {success_count}/{len(prompts_data)} промптов")

    if success_count > 0:
        print(f"\n🌐 Проверьте результат в Open WebUI: {OPENWEBUI_URL}/workspace/prompts")

if __name__ == "__main__":
    main() 