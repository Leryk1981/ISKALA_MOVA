#!/bin/bash

echo "🌺 Запуск ISKALA з OpenAPI Tool Server"
echo "======================================"

# Остановка существующих контейнеров
echo "🛑 Остановка існуючих контейнерів..."
docker-compose down

# Удаление старых образов
echo "🗑️ Видалення старих образів..."
docker-compose build --no-cache

# Запуск всех сервисов
echo "🚀 Запуск всіх сервісів..."
docker-compose up -d

# Ожидание запуска
echo "⏳ Очікування запуску сервісів..."
sleep 10

# Проверка статуса
echo "🔍 Перевірка статусу сервісів..."

# ISKALA Core
echo "📋 ISKALA Core:"
if curl -s http://localhost:8001/health > /dev/null; then
    echo "   ✅ Працює (http://localhost:8001)"
else
    echo "   ❌ Не працює"
fi

# OpenAPI Tool Server
echo "📋 ISKALA OpenAPI Tool Server:"
if curl -s http://localhost:8003/ > /dev/null; then
    echo "   ✅ Працює (http://localhost:8003)"
    echo "   📄 OpenAPI схема: http://localhost:8003/openapi.json"
else
    echo "   ❌ Не працює"
fi

# Open WebUI
echo "📋 Open WebUI:"
if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Працює (http://localhost:3000)"
else
    echo "   ❌ Не працює"
fi

echo ""
echo "🎯 Інтеграція в Open WebUI:"
echo "1. Відкрийте: http://localhost:3000"
echo "2. Settings → Tools → Add Tool"
echo "3. OpenAPI Tool Server"
echo "4. URL: http://localhost:8003/openapi.json"
echo "5. Name: ISKALA Modules"
echo ""
echo "📖 Документація: FINAL_ISKALA_API_INTEGRATION.md"
echo "🚀 Швидкий старт: QUICK_START_ISKALA_API.md" 