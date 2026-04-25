@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo ============================================
echo   team-ENERGO — Установка и запуск
echo ============================================
echo.

:: ─────────────────────────────────────────────
:: 1. PHP Laravel
:: ─────────────────────────────────────────────
echo [1/5] PHP Laravel (порт 3333)...
cd /d "%ROOT%\php-server"

if not exist "vendor" (
    echo   Устанавливаем composer зависимости...
    composer install --no-interaction
    if errorlevel 1 ( echo [ОШИБКА] composer install & pause & exit /b 1 )
) else (
    echo   vendor/ есть — пропускаем
)

if not exist "node_modules" (
    echo   Устанавливаем npm зависимости...
    npm install
    if errorlevel 1 ( echo [ОШИБКА] npm install & pause & exit /b 1 )
) else (
    echo   node_modules/ есть — пропускаем
)

if not exist ".env" (
    copy .env.example .env >nul
    php artisan key:generate
)

php artisan migrate --force >nul 2>&1

start "PHP Laravel" cmd /k "cd /d "%ROOT%\php-server" && composer run dev"

echo   Ждём Laravel на порту 3333...
:wait_laravel
timeout /t 3 /nobreak >nul
curl -s http://127.0.0.1:3333 >nul 2>&1
if errorlevel 1 goto wait_laravel
echo   Laravel готов!
echo.

:: ─────────────────────────────────────────────
:: 2. Backend (Fastify)
:: ─────────────────────────────────────────────
echo [2/5] Backend Fastify (порт 4000)...
cd /d "%ROOT%\MainPage\backend"

if not exist "node_modules" (
    echo   Устанавливаем npm зависимости...
    npm install
    if errorlevel 1 ( echo [ОШИБКА] npm install & pause & exit /b 1 )
) else (
    echo   node_modules/ есть — пропускаем
)

start "Backend Fastify" cmd /k "cd /d "%ROOT%\MainPage\backend" && npm run dev"

echo   Ждём Backend на порту 4000...
:wait_backend
timeout /t 3 /nobreak >nul
curl -s http://127.0.0.1:4000 >nul 2>&1
if errorlevel 1 goto wait_backend
echo   Backend готов!
echo.

:: ─────────────────────────────────────────────
:: 3. Frontend (React + Vite)
:: ─────────────────────────────────────────────
echo [3/5] Frontend React (порт 8000)...
cd /d "%ROOT%\MainPage\frontend"

if not exist "node_modules" (
    echo   Устанавливаем npm зависимости...
    npm install
    if errorlevel 1 ( echo [ОШИБКА] npm install & pause & exit /b 1 )
) else (
    echo   node_modules/ есть — пропускаем
)

start "Frontend React" cmd /k "cd /d "%ROOT%\MainPage\frontend" && npm run dev"

echo   Ждём Frontend на порту 8000...
:wait_frontend
timeout /t 3 /nobreak >nul
curl -s http://127.0.0.1:8000 >nul 2>&1
if errorlevel 1 goto wait_frontend
echo   Frontend готов!
echo.

:: ─────────────────────────────────────────────
:: 4. Telegram Bot
:: ─────────────────────────────────────────────
echo [4/5] Telegram Bot...
cd /d "%ROOT%\telegramBOT"

if not exist "venv\Scripts\activate.bat" (
    echo   Создаём venv...
    python -m venv venv
    if errorlevel 1 ( echo [ОШИБКА] python -m venv & pause & exit /b 1 )
)

echo   Устанавливаем зависимости...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
if errorlevel 1 ( echo [ОШИБКА] pip install & pause & exit /b 1 )

start "Telegram Bot" cmd /k "cd /d "%ROOT%\telegramBOT" && call venv\Scripts\activate.bat && python main.py"
echo   Бот запущен!
echo.

:: ─────────────────────────────────────────────
:: 5. Camera Monitor
:: ─────────────────────────────────────────────
echo [5/5] Camera Monitor...
cd /d "%ROOT%\CameraMonitor_Python"

if not exist "venv\Scripts\activate.bat" (
    echo   Создаём venv...
    python -m venv venv
    if errorlevel 1 ( echo [ОШИБКА] python -m venv & pause & exit /b 1 )
)

echo   Устанавливаем зависимости...
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
if errorlevel 1 ( echo [ОШИБКА] pip install & pause & exit /b 1 )

start "Camera Monitor" cmd /k "cd /d "%ROOT%\CameraMonitor_Python" && call venv\Scripts\activate.bat && python run.py"
echo   Camera Monitor запущен!
echo.

echo ============================================
echo   Все сервисы запущены!
echo ============================================
echo   Frontend:   http://localhost:8000
echo   Backend:    http://localhost:4000/api/v1
echo   PHP:        http://localhost:3333
echo ============================================
pause