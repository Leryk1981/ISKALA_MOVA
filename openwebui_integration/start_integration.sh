#!/bin/bash
# ISKALA + Open WebUI Startup Script

echo "🌺 Запуск ISKALA + Open WebUI Integration..."

# Перевірка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлений"
    exit 1
fi

# Запуск ISKALA
echo "🚀 Запуск ISKALA..."
docker-compose -f docker-compose.iskala.yml up -d

# Очікування запуску ISKALA
echo "⏳ Очікування запуску ISKALA..."
sleep 10

# Перевірка Open WebUI
echo "🔍 Перевірка Open WebUI..."
if docker ps | grep -q open-webui; then
    echo "✅ Open WebUI вже запущений"
else
    echo "🚀 Запуск Open WebUI..."
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
fi

# Очікування запуску Open WebUI
echo "⏳ Очікування запуску Open WebUI..."
sleep 15

# Відкриття інтерфейсу
echo "🌐 Відкриття інтерфейсу інтеграції..."
if command -v xdg-open &> /dev/null; then
    xdg-open "openwebui_integration/iskala_openwebui_integration.html"
elif command -v open &> /dev/null; then
    open "openwebui_integration/iskala_openwebui_integration.html"
else
    echo "📋 Відкрийте в браузері: openwebui_integration/iskala_openwebui_integration.html"
fi

echo "✅ Інтеграція готова!"
echo "🌺 ISKALA: http://localhost:8001"
echo "🤖 Open WebUI: http://localhost:3000"
echo "🔗 Інтеграція: openwebui_integration/iskala_openwebui_integration.html"
