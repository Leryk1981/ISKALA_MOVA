#!/bin/bash

# ISKALA Docker Runner - за прикладом Agent Zero
# Запускає всі сервіси ISKALA в зручному форматі

echo "🌺 ISKALA Docker Runner - запускаємо систему..."
echo "=================================================="

# Перевірка наявності Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не встановлено. Будь ласка, встановіть Docker спочатку."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не встановлено. Будь ласка, встановіть Docker Compose."
    exit 1
fi

# Зупинка попередніх контейнерів
echo "🛑 Зупиняємо попередні контейнери..."
docker-compose down 2>/dev/null || true

# Оновлення зображень
echo "🔄 Оновлюємо Docker образи..."
docker-compose pull 2>/dev/null || true

# Запуск всіх сервісів
echo "🚀 Запускаємо ISKALA систему..."
docker-compose up --build -d

# Очікування запуску
echo "⏳ Очікуємо запуску сервісів..."
sleep 5

# Перевірка статусу
echo "📊 Перевірка статусу сервісів:"
docker-compose ps

echo ""
echo "✅ ISKALA система запущена!"
echo ""
echo "🔗 Доступні сервіси:"
echo "   • ISKALA Core:    http://localhost:50081"
echo "   • Translation:    http://localhost:50082"
echo "   • Vault:         http://localhost:50083"
echo "   • Agent Zero:    http://localhost:50080"
echo ""
echo "📋 Команди для управління:"
echo "   • Перегляд логів: docker-compose logs -f"
echo "   • Зупинка:        docker-compose down"
echo "   • Перезапуск:     docker-compose restart"
echo ""
echo "🌺 Ласкаво просимо до ISKALA!"
