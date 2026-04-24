# ============================================
# ENERGO Project Startup Script (PowerShell)
# Запуск всех сервисов проекта одним скриптом
# ============================================

$projectRoot = $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 ENERGO Project Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 Проверка зависимостей..." -ForegroundColor Yellow
Write-Host ""

# Проверка Node.js
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    Write-Host "✅ Node.js найден" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js НЕ УСТАНОВЛЕН" -ForegroundColor Red
}

# Проверка Python
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "✅ Python найден" -ForegroundColor Green
} else {
    Write-Host "❌ Python НЕ УСТАНОВЛЕН" -ForegroundColor Red
}

# Проверка PHP
$php = Get-Command php -ErrorAction SilentlyContinue
if ($php) {
    Write-Host "✅ PHP найден" -ForegroundColor Green
} else {
    Write-Host "❌ PHP НЕ УСТАНОВЛЕН" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📋 Запуск сервисов..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. Backend (Node.js)
# ============================================
Write-Host "▶️  Запуск Backend (Fastify)..." -ForegroundColor Magenta
$backendCmd = "cd /d `"$projectRoot\MainPage\backend`" && echo ⚙️  Проверка зависимостей... && if not exist `"node_modules`" npm install && if not exist `.env` (if exist `.env.example` copy .env.example .env) && echo 🔄 Запуск миграций БД... && npx prisma migrate deploy 2>nul || echo Миграции уже применены && npx prisma db seed 2>nul || echo Seed уже выполнен && echo 🚀 Запуск Backend на порту 4000... && npm run dev"
Start-Process cmd -ArgumentList "/k $backendCmd"
Start-Sleep -Seconds 2

# ============================================
# 2. Frontend (React + Vite)
# ============================================
Write-Host "▶️  Запуск Frontend (React + Vite)..." -ForegroundColor Green
$frontendCmd = "cd /d `"$projectRoot\MainPage\frontend`" && echo ⚙️  Проверка зависимостей... && if not exist `"node_modules`" npm install && if not exist `.env` (if exist `.env.example` copy .env.example .env) && echo 🚀 Запуск Frontend на порту 8000... && npm run dev"
Start-Process cmd -ArgumentList "/k $frontendCmd"
Start-Sleep -Seconds 2

# ============================================
# 3. PHP Laravel
# ============================================
Write-Host "▶️  Запуск PHP Laravel Server..." -ForegroundColor Yellow
$laravelCmd = "cd /d `"$projectRoot\php-server`" && echo ⚙️  Проверка зависимостей... && if not exist `"vendor`" composer install && if not exist `"node_modules`" npm install && if not exist `.env` (if exist `.env.example` copy .env.example .env) && php artisan key:generate 2>nul || echo Ключ уже сгенерирован && php artisan migrate 2>nul || echo Миграции уже применены && echo 🚀 Запуск PHP Laravel на порту 3333... && composer run dev"
Start-Process cmd -ArgumentList "/k $laravelCmd"
Start-Sleep -Seconds 2

# ============================================
# 4. Telegram Bot
# ============================================
Write-Host "▶️  Запуск Telegram Bot..." -ForegroundColor Cyan
$telegramCmd = "cd /d `"$projectRoot\telegramBOT`" && echo ⚙️  Подготовка Python... && if not exist `.venv` python -m venv .venv && call .venv\Scripts\activate.bat && pip install -q -r requirements.txt && if not exist `.env` echo ⚠️  .env не найден! && echo 🤖 Запуск Telegram Bot... && python main.py"
Start-Process cmd -ArgumentList "/k $telegramCmd"
Start-Sleep -Seconds 2

# ============================================
# 5. Camera Monitor
# ============================================
Write-Host "▶️  Запуск Camera Monitor Server..." -ForegroundColor Gray
$cameraCmd = "cd /d `"$projectRoot\CameraMonitor_Python`" && echo ⚙️  Подготовка Python... && if not exist `.venv` python -m venv .venv && call .venv\Scripts\activate.bat && pip install -q -r requirements.txt && if not exist `"config\settings.ini`" (if exist `"config\settings.ini.example`" copy config\settings.ini.example config\settings.ini) && echo 🎥 Запуск Camera Monitor Server... && python run.py"
Start-Process cmd -ArgumentList "/k $cameraCmd"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📌 АДРЕСА ДОСТУПА:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend:        http://localhost:8000" -ForegroundColor Green
Write-Host "   🔗 Backend API:     http://localhost:4000/api/v1" -ForegroundColor Green
Write-Host "   🏛️  PHP/Laravel:     http://localhost:3333" -ForegroundColor Green
Write-Host "   🤖 Telegram Bot:    @AiCam228_bot" -ForegroundColor Green
Write-Host "   🎥 Camera Server:   localhost:8888" -ForegroundColor Green
Write-Host ""
Write-Host "⏹️  ДЛЯ ОСТАНОВКИ:" -ForegroundColor Yellow
Write-Host "   • Закройте каждое окно терминала" -ForegroundColor Yellow
Write-Host ""
