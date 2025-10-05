#!/bin/bash

# Скрипт для быстрого запуска Server Monitor Bot

set -e

echo "🚀 Server Monitor Bot - Запуск"
echo "================================"

# Проверка наличия .env файла
if [ ! -f .env ]; then
    echo "⚠️  Файл .env не найден!"
    echo "📝 Создайте .env файл из env.example:"
    echo "   cp env.example .env"
    echo "   nano .env"
    exit 1
fi

# Проверка TELEGRAM_TOKEN
source .env
if [ -z "$TELEGRAM_TOKEN" ] || [ "$TELEGRAM_TOKEN" = "your_bot_token_here" ]; then
    echo "❌ TELEGRAM_TOKEN не установлен в .env файле!"
    echo "📝 Получите токен у @BotFather и добавьте в .env"
    exit 1
fi

echo "✅ Конфигурация найдена"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "📥 Установите Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    echo "📥 Установите Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker установлен"

# Создание директории для логов
mkdir -p logs

echo ""
echo "🔨 Сборка Docker образа..."
docker-compose build

echo ""
echo "🚀 Запуск сервисов..."
docker-compose up -d

echo ""
echo "⏳ Ожидание запуска базы данных..."
sleep 5

echo ""
echo "✅ Server Monitor Bot успешно запущен!"
echo ""
echo "📊 Adminer (управление БД): http://localhost:8080"
echo "   Сервер: db"
echo "   Пользователь: postgres"
echo "   Пароль: postgres"
echo "   База данных: metrics"
echo ""
echo "📝 Просмотр логов: docker-compose logs -f app"
echo "🛑 Остановка: docker-compose down"
echo ""
echo "💬 Откройте вашего бота в Telegram и отправьте /start"

