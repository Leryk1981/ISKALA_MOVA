# ISKALA Docker запуск з OpenAPI Tool Server
Write-Host "🌺 Запуск ISKALA з OpenAPI Tool Server" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Остановка существующих контейнеров
Write-Host "🛑 Остановка існуючих контейнерів..." -ForegroundColor Yellow
docker-compose down

# Удаление старых образов
Write-Host "🗑️ Видалення старих образів..." -ForegroundColor Yellow
docker-compose build --no-cache

# Запуск всех сервисов
Write-Host "🚀 Запуск всіх сервісів..." -ForegroundColor Green
docker-compose up -d

# Ожидание запуска
Write-Host "⏳ Очікування запуску сервісів..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Проверка статуса
Write-Host "🔍 Перевірка статусу сервісів..." -ForegroundColor Cyan

# ISKALA Core
Write-Host "📋 ISKALA Core:" -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method GET -TimeoutSec 5
    Write-Host "   ✅ Працює (http://localhost:8001)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Не працює" -ForegroundColor Red
}

# OpenAPI Tool Server
Write-Host "📋 ISKALA OpenAPI Tool Server:" -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8003/" -Method GET -TimeoutSec 5
    Write-Host "   ✅ Працює (http://localhost:8003)" -ForegroundColor Green
    Write-Host "   📄 OpenAPI схема: http://localhost:8003/openapi.json" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Не працює" -ForegroundColor Red
}

# Open WebUI
Write-Host "📋 Open WebUI:" -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
    Write-Host "   ✅ Працює (http://localhost:3000)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Не працює" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Інтеграція в Open WebUI:" -ForegroundColor Yellow
Write-Host "1. Відкрийте: http://localhost:3000" -ForegroundColor White
Write-Host "2. Settings → Tools → Add Tool" -ForegroundColor White
Write-Host "3. OpenAPI Tool Server" -ForegroundColor White
Write-Host "4. URL: http://localhost:8003/openapi.json" -ForegroundColor White
Write-Host "5. Name: ISKALA Modules" -ForegroundColor White
Write-Host ""
Write-Host "📖 Документація: FINAL_ISKALA_API_INTEGRATION.md" -ForegroundColor Cyan
Write-Host "🚀 Швидкий старт: QUICK_START_ISKALA_API.md" -ForegroundColor Cyan 