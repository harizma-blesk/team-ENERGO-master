#!/bin/bash

# ============================================
# ENERGO Project Startup Script (Mac/Linux)
# Запуск всех сервисов проекта одним скриптом
# ============================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "========================================"
echo "🚀 ENERGO Project Startup"
echo "========================================"
echo ""

echo "🔍 Проверка зависимостей..."
echo ""

if command -v node &> /dev/null; then
    echo "✅ Node.js найден"
else
    echo "❌ Node.js НЕ УСТАНОВЛЕН"
fi

if command -v python3 &> /dev/null; then
    echo "✅ Python найден"
else
    echo "❌ Python НЕ УСТАНОВЛЕН"
fi

if command -v php &> /dev/null; then
    echo "✅ PHP найден"
else
    echo "❌ PHP НЕ УСТАНОВЛЕН"
fi

echo ""
echo "========================================"
echo "📋 Запуск сервисов..."
echo "========================================"
echo ""

# Функция для открытия нового терминала и запуска команды
open_terminal() {
    local name="$1"
    local cmd="$2"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - открываем новое окно Terminal
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_ROOT' && $cmd"
end tell
EOF
    else
        # Linux - используем gnome-terminal
        gnome-terminal --tab -- bash -c "cd '$PROJECT_ROOT' && $cmd; bash" &
    fi
    sleep 1
}

# ============================================
# 1. Backend (Node.js)
# ============================================
echo "▶️  Запуск Backend (Fastify)..."
open_terminal "Backend" "cd MainPage/backend && echo '⚙️  Проверка зависимостей...' && [ ! -d 'node_modules' ] && npm install || true && [ ! -f '.env' ] && [ -f '.env.example' ] && cp .env.example .env || true && echo '🔄 Запуск миграций БД...' && npx prisma migrate deploy 2>/dev/null || echo 'Миграции уже применены' && npx prisma db seed 2>/dev/null || echo 'Seed уже выполнен' && echo '🚀 Запуск Backend на порту 4000...' && npm run dev"

sleep 2

# ============================================
# 2. Frontend (React + Vite)
# ============================================
echo "▶️  Запуск Frontend (React + Vite)..."
open_terminal "Frontend" "cd MainPage/frontend && echo '⚙️  Проверка зависимостей...' && [ ! -d 'node_modules' ] && npm install || true && [ ! -f '.env' ] && [ -f '.env.example' ] && cp .env.example .env || true && echo '🚀 Запуск Frontend на порту 8000...' && npm run dev"

sleep 2

# ============================================
# 3. PHP Laravel
# ============================================
echo "▶️  Запуск PHP Laravel Server..."
open_terminal "Laravel" "cd php-server && echo '⚙️  Проверка зависимостей...' && [ ! -d 'vendor' ] && composer install || true && [ ! -d 'node_modules' ] && npm install || true && [ ! -f '.env' ] && [ -f '.env.example' ] && cp .env.example .env || true && php artisan key:generate 2>/dev/null || echo 'Ключ уже сгенерирован' && php artisan migrate 2>/dev/null || echo 'Миграции уже применены' && echo '🚀 Запуск PHP Laravel на порту 3333...' && composer run dev"

sleep 2

# ============================================
# 4. Telegram Bot
# ============================================
echo "▶️  Запуск Telegram Bot..."
open_terminal "Telegram" "cd telegramBOT && echo '⚙️  Подготовка Python...' && [ ! -d '.venv' ] && python3 -m venv .venv || true && source .venv/bin/activate && pip install -q -r requirements.txt && [ ! -f '.env' ] && echo '⚠️  .env не найден!' || true && echo '🤖 Запуск Telegram Bot...' && python main.py"

sleep 2

# ============================================
# 5. Camera Monitor
# ============================================
echo "▶️  Запуск Camera Monitor Server..."
open_terminal "Camera" "cd CameraMonitor_Python && echo '⚙️  Подготовка Python...' && [ ! -d '.venv' ] && python3 -m venv .venv || true && source .venv/bin/activate && pip install -q -r requirements.txt && [ ! -f 'config/settings.ini' ] && [ -f 'config/settings.ini.example' ] && cp config/settings.ini.example config/settings.ini || true && echo '🎥 Запуск Camera Monitor Server...' && python run.py"

echo ""
echo "========================================"
echo "✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================================"
echo ""
echo "📌 АДРЕСА ДОСТУПА:"
echo "   🌐 Frontend:        http://localhost:8000"
echo "   🔗 Backend API:     http://localhost:4000/api/v1"
echo "   🏛️  PHP/Laravel:     http://localhost:3333"
echo "   🤖 Telegram Bot:    @AiCam228_bot"
echo "   🎥 Camera Server:   localhost:8888"
echo ""
echo "⏹️  ДЛЯ ОСТАНОВКИ:"
echo "   • Закройте каждое окно терминала"
echo ""
echo "========================================"
echo ""
