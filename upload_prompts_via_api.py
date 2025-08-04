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

def upload_prompts_via_api(prompts_data, category="MOVA"):
    """Загружает промпты через API"""
    
    # Получаем список существующих промптов
    try:
        response = requests.get(f"{API_BASE}/prompts/")
        if response.status_code == 200:
            existing_prompts = response.json()
            print(f"✅ Найдено {len(existing_prompts)} существующих промптов")
        else:
            print(f"⚠️ Не удалось получить список промптов: {response.status_code}")
            existing_prompts = []
    except Exception as e:
        print(f"⚠️ Ошибка получения списка промптов: {e}")
        existing_prompts = []

    # Загружаем каждый промпт
    success_count = 0
    for prompt in prompts_data:
        prompt_id = prompt.get('id')
        label = prompt.get('label', prompt_id)
        value = prompt.get('value', '')
        
        # Проверяем, существует ли уже такой промпт
        if any(p.get('id') == prompt_id for p in existing_prompts):
            print(f"⚠️ Промпт '{label}' уже существует, пропускаем")
            continue
        
        # Создаем промпт через API
        prompt_data = {
            "id": prompt_id,
            "name": label,
            "content": value,
            "category": category,
            "tags": ["MOVA", "synthetic"]
        }
        
        try:
            response = requests.post(f"{API_BASE}/prompts/", json=prompt_data)
            if response.status_code == 200:
                print(f"✅ Загружен промпт: {label}")
                success_count += 1
            else:
                print(f"❌ Ошибка загрузки промпта '{label}': {response.status_code}")
                print(f"   Ответ: {response.text}")
        except Exception as e:
            print(f"❌ Ошибка загрузки промпта '{label}': {e}")
    
    return success_count

def main():
    """Основная функция"""
    print("🚀 Загрузка промптов MOVA через API Open WebUI")
    print("=" * 50)
    
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
    
    # Загружаем упрощенные промпты
    prompts_file = Path("openwebui_prompts/synthetic_mova_simple.json")
    if not prompts_file.exists():
        print(f"❌ Файл {prompts_file} не найден")
        return
    
    prompts_data = load_json_file(prompts_file)
    if not prompts_data:
        return
    
    print(f"📁 Загружено {len(prompts_data)} промптов из файла")
    
    # Загружаем через API
    success_count = upload_prompts_via_api(prompts_data, "Synthetic MOVA")
    
    print("=" * 50)
    print(f"✅ Успешно загружено: {success_count}/{len(prompts_data)} промптов")
    
    if success_count > 0:
        print(f"\n🌐 Проверьте результат в Open WebUI: {OPENWEBUI_URL}/workspace/prompts")

if __name__ == "__main__":
    main() 