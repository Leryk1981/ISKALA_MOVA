@echo off
REM ISKALA + Open WebUI Integration Startup Script

echo 🌺 Запуск ISKALA + Open WebUI Integration...

REM Перевірка Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker не встановлений
    pause
    exit /b 1
)

REM Запуск ISKALA
echo 🚀 Запуск ISKALA...
docker-compose -f docker-compose.iskala.yml up -d

REM Очікування запуску ISKALA
echo ⏳ Очікування запуску ISKALA...
timeout /t 10 /nobreak >nul

REM Перевірка Open WebUI
echo 🔍 Перевірка Open WebUI...
docker ps | findstr open-webui >nul
if errorlevel 1 (
    echo 🚀 Запуск Open WebUI...
    docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
) else (
    echo ✅ Open WebUI вже запущений
)

REM Очікування запуску Open WebUI
echo ⏳ Очікування запуску Open WebUI...
timeout /t 15 /nobreak >nul

REM Відкриття інтерфейсу
echo 🌐 Відкриття інтерфейсу інтеграції...
start "" "openwebui_integration/iskala_openwebui_integration.html"

echo ✅ Інтеграція готова!
echo 🌺 ISKALA: http://localhost:8001
echo 🤖 Open WebUI: http://localhost:3000
echo 🔗 Інтеграція: openwebui_integration/iskala_openwebui_integration.html
pause
