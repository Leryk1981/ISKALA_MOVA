#!/usr/bin/env python3
"""
ISKALA Cache Fix Script
Принудительное решение проблемы с кэшированием Open WebUI
"""

import subprocess
import time
import requests
import json
import os
from pathlib import Path

def run_command(command, shell=True):
    """Выполнить команду и вернуть результат"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_service(url, timeout=5):
    """Проверить доступность сервиса"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    print("🌺 ISKALA Cache Fix Script")
    print("=" * 50)
    
    # Шаг 1: Остановка Open WebUI
    print("\n1️⃣ Останавливаем Open WebUI...")
    success, stdout, stderr = run_command("docker-compose stop open-webui")
    if success:
        print("   ✅ Open WebUI остановлен")
    else:
        print("   ❌ Ошибка при остановке:", stderr)
    
    # Шаг 2: Удаление volume с данными
    print("\n2️⃣ Удаляем кэшированные данные...")
    success, stdout, stderr = run_command("docker volume rm iskala-mova_open-webui-data")
    if success:
        print("   ✅ Volume с данными удален")
    else:
        print("   ⚠️  Volume не найден или уже удален")
    
    # Шаг 3: Очистка Docker кэша
    print("\n3️⃣ Очищаем Docker кэш...")
    success, stdout, stderr = run_command("docker system prune -f")
    if success:
        print("   ✅ Docker кэш очищен")
    else:
        print("   ⚠️  Ошибка при очистке Docker кэша:", stderr)
    
    # Шаг 4: Обновление docker-compose.yml с правильными настройками кэша
    print("\n4️⃣ Обновляем конфигурацию...")
    
    # Добавляем переменные для отключения кэширования
    cache_vars = """
      # Отключение кэширования для решения проблем с JS файлами
      - DISABLE_CACHE=true
      - CACHE_CONTROL=no-cache
      - ETAG_DISABLED=true
      - MODELS_CACHE_TTL=0
      - WEBUI_SESSION_COOKIE_SAME_SITE=none
      - WEBUI_SESSION_COOKIE_SECURE=false
"""
    
    # Читаем текущий docker-compose.yml
    compose_file = "docker-compose.yml"
    if os.path.exists(compose_file):
        with open(compose_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем переменные кэширования после ENABLE_LOGGING
        if "ENABLE_LOGGING=true" in content and "DISABLE_CACHE=true" not in content:
            content = content.replace(
                "ENABLE_LOGGING=true",
                "ENABLE_LOGGING=true" + cache_vars
            )
            
            with open(compose_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   ✅ Конфигурация обновлена")
        else:
            print("   ⚠️  Конфигурация уже содержит настройки кэша")
    
    # Шаг 5: Перезапуск Open WebUI
    print("\n5️⃣ Запускаем Open WebUI с новыми настройками...")
    success, stdout, stderr = run_command("docker-compose up -d open-webui")
    if success:
        print("   ✅ Open WebUI запущен")
    else:
        print("   ❌ Ошибка при запуске:", stderr)
        return
    
    # Шаг 6: Ожидание запуска
    print("\n6️⃣ Ожидаем полного запуска...")
    for i in range(30):
        if check_service("http://localhost:3000"):
            print(f"   ✅ Open WebUI доступен через {i+1} секунд")
            break
        time.sleep(1)
        if i % 5 == 0:
            print(f"   ⏳ Ожидание... ({i+1}/30)")
    else:
        print("   ❌ Open WebUI не запустился за 30 секунд")
        return
    
    # Шаг 7: Проверка JavaScript файлов
    print("\n7️⃣ Проверяем JavaScript файлы...")
    js_files = [
        "/_app/immutable/entry/start.BD0sJqPm.js",
        "/_app/immutable/entry/app.DzAV6zKd.js",
        "/_app/immutable/chunks/CIUdcGrV.js"
    ]
    
    all_files_ok = True
    for js_file in js_files:
        if check_service(f"http://localhost:3000{js_file}"):
            print(f"   ✅ {js_file}")
        else:
            print(f"   ❌ {js_file}")
            all_files_ok = False
    
    # Шаг 8: Финальная проверка
    print("\n8️⃣ Финальная проверка...")
    if all_files_ok:
        print("   ✅ Все файлы доступны")
        print("\n🎉 Проблема с кэшированием решена!")
        print("\n📋 Рекомендации:")
        print("1. Очистите кэш браузера: Ctrl+Shift+Delete")
        print("2. Или используйте режим инкогнито")
        print("3. Откройте: http://localhost:3000")
        print("4. Если проблема остается, попробуйте другой браузер")
    else:
        print("   ❌ Некоторые файлы недоступны")
        print("\n🔧 Дополнительные шаги:")
        print("1. Проверьте логи: docker logs open-webui")
        print("2. Попробуйте другой браузер")
        print("3. Используйте режим инкогнито")
    
    print("\n📊 Статус сервисов:")
    services = [
        ("Open WebUI", "http://localhost:3000"),
        ("ISKALA Core", "http://localhost:8001/health"),
        ("OpenAPI Tool Server", "http://localhost:8003")
    ]
    
    for name, url in services:
        status = "✅" if check_service(url) else "❌"
        print(f"   {status} {name}")

if __name__ == "__main__":
    main() 