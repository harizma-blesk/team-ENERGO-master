@echo off
chcp 65001 >nul
set projectRoot=%~dp0

echo Запуск PHP Laravel (первым - нужен для камер и бота)...
start "PHP Laravel" cmd /k "cd /d "%projectRoot%php-server" && composer run dev"
timeout /t 10 >nul

echo Запуск Backend...
start "Backend" cmd /k "cd /d "%projectRoot%MainPage\backend" && npm run dev"
timeout /t 5 >nul

echo Запуск Frontend...
start "Frontend" cmd /k "cd /d "%projectRoot%MainPage\frontend" && npm run dev"
timeout /t 5 >nul

echo Запуск Admin Panel...
start "Admin Panel" cmd /k "cd /d "%projectRoot%adminPanel" && php -S localhost:8080"
timeout /t 2 >nul

echo Запуск Telegram Bot...
start "Telegram Bot" cmd /k "cd /d "%projectRoot%telegramBOT" && call venv\Scripts\activate.bat && pip install -q -r requirements.txt && python main.py"
timeout /t 3 >nul

echo Запуск Camera Monitor...
start "Camera Monitor" cmd /k "cd /d "%projectRoot%CameraMonitor_Python" && call venv\Scripts\activate.bat && python run.py"

echo.
echo Все сервисы запущены!
echo Frontend:    http://localhost:8000
echo Backend:     http://localhost:4000/api/v1
echo PHP:         http://localhost:3333
echo Admin Panel: http://localhost:8080
pause