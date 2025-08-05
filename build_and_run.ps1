# ISKALA MOVA - Production Build and Run Script (PowerShell)
# ==========================================================

param(
    [Parameter(Position=0)]
    [ValidateSet("build", "up", "down", "restart", "logs", "status", "clean", "test", "full", "help")]
    [string]$Action = "help"
)

# Configuration
$ComposeFile = "docker-compose.production.yml"
$EnvFile = "env.production.template"
$ProjectName = "iskala-mova"

Write-Host "🚀 ISKALA MOVA - Production Build Script" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
    exit 1
}

# Determine docker-compose command
$DockerCompose = if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    "docker-compose"
} else {
    Write-Host "⚠️  docker-compose not found, using 'docker compose'" -ForegroundColor Yellow
    "docker compose"
}

function Show-Help {
    Write-Host ""
    Write-Host "Usage: .\build_and_run.ps1 [ACTION]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Cyan
    Write-Host "  build     - Build all containers" -ForegroundColor White
    Write-Host "  up        - Start all services" -ForegroundColor White
    Write-Host "  down      - Stop all services" -ForegroundColor White
    Write-Host "  restart   - Restart all services" -ForegroundColor White
    Write-Host "  logs      - Show logs" -ForegroundColor White
    Write-Host "  status    - Show service status" -ForegroundColor White
    Write-Host "  clean     - Clean up containers and volumes" -ForegroundColor White
    Write-Host "  test      - Run health checks" -ForegroundColor White
    Write-Host "  full      - Build + Start + Test" -ForegroundColor White
    Write-Host "  help      - Show this help" -ForegroundColor White
    Write-Host ""
}

function Build-Containers {
    Write-Host "🔨 Building ISKALA containers..." -ForegroundColor Blue
    
    & $DockerCompose -f $ComposeFile -p $ProjectName build --no-cache
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build completed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Build failed" -ForegroundColor Red
        exit 1
    }
}

function Start-Services {
    Write-Host "🚀 Starting ISKALA services..." -ForegroundColor Blue
    
    & $DockerCompose -f $ComposeFile -p $ProjectName up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Services started successfully" -ForegroundColor Green
        Write-Host "📊 Access points:" -ForegroundColor Yellow
        Write-Host "  • ISKALA API:     http://localhost:8000" -ForegroundColor White
        Write-Host "  • API Docs:       http://localhost:8000/docs" -ForegroundColor White
        Write-Host "  • Neo4j Browser:  http://localhost:7474" -ForegroundColor White
        Write-Host "  • Grafana:        http://localhost:3000" -ForegroundColor White
        Write-Host "  • Prometheus:     http://localhost:9090" -ForegroundColor White
    } else {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        exit 1
    }
}

function Stop-Services {
    Write-Host "🛑 Stopping ISKALA services..." -ForegroundColor Blue
    & $DockerCompose -f $ComposeFile -p $ProjectName down
    Write-Host "✅ Services stopped" -ForegroundColor Green
}

function Restart-Services {
    Write-Host "🔄 Restarting ISKALA services..." -ForegroundColor Blue
    Stop-Services
    Start-Services
}

function Show-Logs {
    Write-Host "📋 ISKALA Service Logs" -ForegroundColor Blue
    & $DockerCompose -f $ComposeFile -p $ProjectName logs -f --tail=100
}

function Show-Status {
    Write-Host "📊 ISKALA Service Status" -ForegroundColor Blue
    & $DockerCompose -f $ComposeFile -p $ProjectName ps
    
    Write-Host ""
    Write-Host "🔍 Container Health Checks:" -ForegroundColor Blue
    docker ps --filter "name=$ProjectName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

function Clean-Up {
    Write-Host "⚠️  This will remove all containers, networks, and volumes" -ForegroundColor Yellow
    $confirmation = Read-Host "Are you sure? (y/N)"
    
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Write-Host "🧹 Cleaning up ISKALA resources..." -ForegroundColor Blue
        & $DockerCompose -f $ComposeFile -p $ProjectName down -v --remove-orphans
        docker system prune -f
        Write-Host "✅ Cleanup completed" -ForegroundColor Green
    } else {
        Write-Host "Cleanup cancelled" -ForegroundColor Yellow
    }
}

function Test-HealthChecks {
    Write-Host "🏥 Running ISKALA Health Checks..." -ForegroundColor Blue
    
    # Wait for services to be ready
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check ISKALA API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ ISKALA API is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ ISKALA API returned status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ ISKALA API is not responding" -ForegroundColor Red
    }
    
    # Check Neo4j
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:7474" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Neo4j is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Neo4j returned status: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Neo4j is not responding" -ForegroundColor Red
    }
    
    # Check Redis
    try {
        $redisCheck = docker exec "$ProjectName-iskala-redis-1" redis-cli ping 2>$null
        if ($redisCheck -eq "PONG") {
            Write-Host "✅ Redis is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Redis is not responding" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Redis check failed" -ForegroundColor Red
    }
    
    # Run API tests
    Write-Host "🧪 Running API tests..." -ForegroundColor Blue
    try {
        docker exec "$ProjectName-iskala-api-1" python -m pytest tests/integration/ -v --tb=short
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ API tests passed" -ForegroundColor Green
        } else {
            Write-Host "❌ API tests failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Could not run API tests" -ForegroundColor Red
    }
}

# Check for environment file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item $EnvFile ".env"
    Write-Host "📝 Please edit .env file with your actual configuration" -ForegroundColor Yellow
    Write-Host "   Especially update API keys and passwords!" -ForegroundColor Yellow
}

# Main script logic
switch ($Action) {
    "build" {
        Build-Containers
    }
    "up" {
        Start-Services
    }
    "down" {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "logs" {
        Show-Logs
    }
    "status" {
        Show-Status
    }
    "clean" {
        Clean-Up
    }
    "test" {
        Test-HealthChecks
    }
    "full" {
        Write-Host "🚀 Full deployment: Build + Start + Test" -ForegroundColor Blue
        Build-Containers
        Start-Services
        Test-HealthChecks
    }
    default {
        Show-Help
    }
}

Write-Host "================================" -ForegroundColor Blue
Write-Host "✅ Script completed successfully" -ForegroundColor Green 