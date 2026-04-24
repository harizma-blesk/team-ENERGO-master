#!/bin/bash

# ============================================
# ENERGO Project Startup Script (Mac/Linux)
# ============================================

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "========================================"
echo "🚀 ENERGO Project Startup"
echo "========================================"
echo ""

# Проверка зависимостей
echo "🔍 Проверка зависимостей..."
command -v node &>/dev/null && echo "✅ Node.js найден" || echo "❌ Node.js НЕ УСТАНОВЛЕН"
command -v python3 &>/dev/null && echo "✅ Python найден" || echo "❌ Python НЕ УСТАНОВЛЕН"
command -v php &>/dev/null && echo "✅ PHP найден" || echo "❌ PHP НЕ УСТАНОВЛЕН"
echo ""

# Функция открытия терминала
open_terminal() {
    local cmd="$2"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$PROJECT_ROOT' && $cmd"
end tell
EOF
    else
        gnome-terminal --tab -- bash -c "cd '$PROJECT_ROOT' && $cmd; bash" &
    fi
    sleep 1
}

echo "📋 Запуск сервисов..."
echo ""

# 1. Backend
echo "▶️  Запуск Backend (Fastify)..."
open_terminal "Backend" "cd MainPage/backend && npm run dev"
sleep 3

# 2. Frontend
echo "▶️  Запуск Frontend (React + Vite)..."
open_terminal "Frontend" "cd MainPage/frontend && npm run dev"
sleep 3

# 3. PHP Laravel
echo "▶️  Запуск PHP Laravel..."
open_terminal "Laravel" "cd php-server && composer run dev"
sleep 3

# 4. Telegram Bot
echo "▶️  Запуск Telegram Bot..."
open_terminal "Telegram" "cd telegramBOT && source venv/bin/activate && python main.py"
sleep 2

# 5. Camera Monitor
echo "▶️  Запуск Camera Monitor..."
open_terminal "Camera" "cd CameraMonitor_Python && source venv/bin/activate && python run.py"

# 6. Admin Panel
echo "▶️  Запуск Admin Panel..."
open_terminal "AdminPanel" "cd adminPanel && php -S localhost:8080"
sleep 2

echo ""
echo "========================================"
echo "✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!"
echo "========================================"
echo ""
echo "📌 АДРЕСА ДОСТУПА:"
echo "   🌐 Frontend:    http://localhost:8000"
echo "   🔗 Backend API: http://localhost:4000/api/v1"
echo "   🏛️  PHP/Laravel: http://localhost:3333"
echo "   🤖 Telegram:    @AiCam228_bot"
echo "   🛠️  Admin Panel: http://localhost:8080"
echo ""