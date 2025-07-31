#!/bin/bash

# ISKALA RAG System Startup Script

echo "=== ISKALA RAG System ==="
echo "Запуск RAG контейнера..."

# Перевірка наявності Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлено"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не встановлено"
    exit 1
fi

# Перехід до кореневої директорії проекту
cd "$(dirname "$0")/.."

# Запуск RAG контейнера
echo "🚀 Запуск контейнера iskala-rag..."
docker-compose up -d iskala-rag

# Очікування запуску
echo "⏳ Очікування запуску контейнера..."
sleep 10

# Перевірка стану
echo "🔍 Перевірка стану контейнера..."
if docker-compose ps iskala-rag | grep -q "Up"; then
    echo "✅ RAG контейнер успішно запущено"
    echo "🌐 API доступне за адресою: http://localhost:50084"
    echo "📖 Документація API: http://localhost:50084/docs"
    echo ""
    echo "Для тестування запустіть:"
    echo "cd rag_system && python test_docker.py"
else
    echo "❌ Помилка запуску контейнера"
    echo "Перевірте логи: docker-compose logs iskala-rag"
    exit 1
fi 