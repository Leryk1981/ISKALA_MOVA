#!/bin/bash
# Quick Start Script для ISKALA + Open WebUI

echo "🌺 Швидкий старт ISKALA + Open WebUI"

# Перевірка ISKALA
echo "🔍 Перевірка ISKALA..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ ISKALA працює"
else
    echo "❌ ISKALA не працює. Запустіть: docker-compose up -d"
    exit 1
fi

# Перевірка Open WebUI
echo "🔍 Перевірка Open WebUI..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Open WebUI працює"
else
    echo "❌ Open WebUI не працює. Запустіть: docker start open-webui"
    exit 1
fi

# Відкриття інтерфейсів
echo "🌐 Відкриття інтерфейсів..."

if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:3000
    xdg-open openwebui_integration/iskala_openwebui_integration.html
elif command -v open > /dev/null; then
    open http://localhost:3000
    open openwebui_integration/iskala_openwebui_integration.html
else
    echo "📋 Відкрийте в браузері:"
    echo "  Open WebUI: http://localhost:3000"
    echo "  Інтеграція: openwebui_integration/iskala_openwebui_integration.html"
fi

echo "✅ Готово! Інтеграція активна."
