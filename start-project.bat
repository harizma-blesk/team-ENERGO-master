@echo off
REM ============================================
REM ENERGO Project Startup Script (Windows Batch)
REM Запуск всех сервисов проекта одним скриптом
REM ============================================

setlocal enabledelayedexpansion
set projectRoot=%~dp0

echo.
echo ========================================
echo 🚀 ENERGO Project Startup
echo ========================================
echo.

REM Проверка зависимостей
echo 🔍 Проверка зависимостей...
echo.

where node >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✅ Node.js найден
) else (
    echo ❌ Node.js НЕ УСТАНОВЛЕН
)

where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✅ Python найден
) else (
    echo ❌ Python НЕ УСТАНОВЛЕН
)

where docker >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✅ Docker найден
) else (
    echo ❌ Docker НЕ УСТАНОВЛЕН
)

where php >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo ✅ PHP найден
) else (
    echo ❌ PHP НЕ УСТАНОВЛЕН
)

echo.
echo ========================================
echo 📋 Запуск сервисов...
echo ========================================
echo.



REM 1. Backend (Node.js)
echo ▶️  Запуск Backend (Fastify)...
start "Backend (Fastify)" cmd /k "cd /d "%projectRoot%MainPage\backend" && echo ⚙️  Проверка зависимостей... && if not exist "node_modules" npm install && if not exist ".env" (if exist ".env.example" copy .env.example .env) && echo 🔄 Запуск миграций БД... && npx prisma migrate deploy 2>nul || echo Миграции уже применены && npx prisma db seed 2>nul || echo Seed уже выполнен && echo 🚀 Запуск Backend на порту 4000... && npm run dev"

timeout /t 2 >nul

REM 2. Frontend (React + Vite)
echo ▶️  Запуск Frontend (React + Vite)...
start "Frontend (React + Vite)" cmd /k "cd /d "%projectRoot%MainPage\frontend" && echo ⚙️  Проверка зависимостей... && if not exist "node_modules" npm install && if not exist ".env" (if exist ".env.example" copy .env.example .env) && echo 🚀 Запуск Frontend на порту 8000... && npm run dev"

timeout /t 2 >nul

REM 3. PHP Laravel
echo ▶️  Запуск PHP Laravel Server...
start "PHP Laravel Server" cmd /k "cd /d "%projectRoot%php-server" && echo ⚙️  Проверка зависимостей... && if not exist "vendor" composer install && if not exist "node_modules" npm install && if not exist ".env" (if exist ".env.example" copy .env.example .env) && php artisan key:generate 2>nul || echo Ключ уже сгенерирован && php artisan migrate 2>nul || echo Миграции уже применены && echo 🚀 Запуск PHP Laravel на порту 3333... && composer run dev"

timeout /t 2 >nul

REM 4. Telegram Bot
echo ▶️  Запуск Telegram Bot...
start "Telegram Bot (Python)" cmd /k "cd /d "%projectRoot%telegramBOT" && echo ⚙️  Подготовка Python... && if not exist ".venv" python -m venv .venv && call .venv\Scripts\activate.bat && pip install -q -r requirements.txt && if not exist ".env" echo ⚠️  .env не найден! && echo 🤖 Запуск Telegram Bot... && python main.py"

timeout /t 2 >nul

REM 5. Camera Monitor
echo ▶️  Запуск Camera Monitor Server...
start "Camera Monitor Server (Python)" cmd /k "cd /d "%projectRoot%CameraMonitor_Python" && echo ⚙️  Подготовка Python... && if not exist ".venv" python -m venv .venv && call .venv\Scripts\activate.bat && pip install -q -r requirements.txt && if not exist "config\settings.ini" (if exist "config\settings.ini.example" copy config\settings.ini.example config\settings.ini) && echo 🎥 Запуск Camera Monitor Server... && python run.py"

echo.
echo ========================================
echo ✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!
echo ========================================
echo.
echo 📌 АДРЕСА ДОСТУПА:
echo    🌐 Frontend:        http://localhost:8000
echo    🔗 Backend API:     http://localhost:4000/api/v1
echo    🏛️  PHP/Laravel:     http://localhost:3333
echo    🤖 Telegram Bot:    @AiCam228_bot
echo    🎥 Camera Server:   localhost:8888
echo.
echo ⏹️  ДЛЯ ОСТАНОВКИ:
echo    • Закройте каждое окно терминала
echo.
pause
