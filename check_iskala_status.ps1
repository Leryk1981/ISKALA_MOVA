# ISKALA Status Check Script
# Проверка статуса всех сервисов ISKALA

Write-Host "🌺 ISKALA Status Check" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

# Проверка Docker контейнеров
Write-Host "📋 Docker Containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "iskala|open-webui"

Write-Host ""

# Проверка портов
Write-Host "🔌 Port Status:" -ForegroundColor Yellow

$ports = @(
    @{Port=3000; Service="Open WebUI"; URL="http://localhost:3000"},
    @{Port=8001; Service="ISKALA Core"; URL="http://localhost:8001/health"},
    @{Port=8003; Service="OpenAPI Tool Server"; URL="http://localhost:8003"},
    @{Port=8081; Service="Vault"; URL="http://localhost:8081/health"},
    @{Port=8082; Service="Translation"; URL="http://localhost:8082/health"}
)

foreach ($port in $ports) {
    try {
        $response = Invoke-WebRequest -Uri $port.URL -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ $($port.Service) (Port $($port.Port))" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  $($port.Service) (Port $($port.Port)) - Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ $($port.Service) (Port $($port.Port)) - Не отвечает" -ForegroundColor Red
    }
}

Write-Host ""

# Проверка использования ресурсов
Write-Host "💾 Resource Usage:" -ForegroundColor Yellow
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

Write-Host ""

# Проверка JavaScript файлов Open WebUI
Write-Host "🔧 Open WebUI JavaScript Files:" -ForegroundColor Yellow
try {
    $html = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing
    $jsFiles = $html.Content | Select-String "_app/immutable.*\.js" -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Value }
    
    foreach ($file in $jsFiles | Select-Object -First 5) {
        try {
            $fileUrl = "http://localhost:3000$file"
            $fileResponse = Invoke-WebRequest -Uri $fileUrl -TimeoutSec 3 -UseBasicParsing
            if ($fileResponse.StatusCode -eq 200) {
                Write-Host "   ✅ $file" -ForegroundColor Green
            } else {
                Write-Host "   ❌ $file - Status: $($fileResponse.StatusCode)" -ForegroundColor Red
            }
        } catch {
            Write-Host "   ❌ $file - Не найден" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "   ❌ Не удалось проверить JavaScript файлы" -ForegroundColor Red
}

Write-Host ""

# Рекомендации
Write-Host "💡 Recommendations:" -ForegroundColor Cyan
Write-Host "1. Если Open WebUI не работает, очистите кэш браузера" -ForegroundColor White
Write-Host "2. Откройте iskala_clear_cache.html для инструкций" -ForegroundColor White
Write-Host "3. Используйте режим инкогнито для тестирования" -ForegroundColor White
Write-Host "4. URL: http://localhost:3000" -ForegroundColor White

Write-Host ""
Write-Host "🌺 ISKALA Status Check Complete" -ForegroundColor Cyan 