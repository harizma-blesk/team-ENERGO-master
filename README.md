# 🚀 team-ENERGO

**Интегрированная система для управления аудиториями, расписанием и учебными активностями.**

Монорепозиторий, объединяющий:
- 🌐 Веб-приложение (React + Fastify)
- 🤖 Telegram-бот для поиска аудиторий
- 📹 Сервер компьютерного зрения для мониторинга
- 🏛️ Backend интеграции (Laravel)
- 📱 Мобильные приложения и прошивка ESP-устройств

---

## ⚡ БЫСТРЫЙ СТАРТ (5 минут)

### Требования
- **Node.js** 20+
- **Python** 3.11+
- **PHP** 8.3+ + Composer
- **Git**

### Установка и запуск

**. Клонируй репозиторий:**
```bash
git clone <repo-url>
cd team-ENERGO-master
```


## 📊 Архитектура

| Компонент | Адрес | Описание |
|-----------|-------|---------|
| 🌐 Frontend | `http://localhost:8000` | React 19 + Vite интерфейс |
| 🔗 Backend API | `http://localhost:4000/api/v1` | Fastify + Prisma + PostgreSQL |
| 🏛️ PHP Backend | `http://localhost:3333` | Laravel 13 (интеграции) |
| 🤖 Telegram Bot | Telegram: `/find`, `/status` | Python + aiogram |
| 🎥 Camera Server | `localhost:8888` | Python + YOLO мониторинг |

---

## 📂 Структура проекта

```
team-ENERGO-master/
├── MainPage/                 # Основное веб-приложение
│   ├── frontend/            # React + Vite интерфейс (порт 8000)
│   ├── backend/             # Fastify API (порт 4000)
│   └── tools/              # Утилиты
│
├── php-server/              # Laravel 13 (порт 3333)
│   ├── app/                # Контроллеры и модели
│   ├── routes/             # API маршруты
│   └── config/             # Конфигурация
│
├── telegramBOT/             # Telegram-бот (Python)
│   ├── app/                # Обработчики команд
│   └── handlers/           # /find, /status, /logs
│
├── CameraMonitor_Python/    # Сервер видеомониторинга
│   ├── src/                # YOLO-детекция
│   ├── models/             # Предобученные модели
│   └── tests/              # Unit-тесты
│
├── start-project.bat        # Запуск всех сервисов (Windows)
├── start-project.sh         # Запуск (Mac/Linux)
└── README.md               # Этот файл
```

---

## 🔧 Детальный запуск (если скрипт не сработал)

### Шаг 1: Backend (Node.js + Fastify)
```bash
cd MainPage/backend
npm install
cp .env.example .env
npx prisma generate
npm run dev
# Открыть: http://localhost:4000/docs
```

### Шаг 2: Frontend (React + Vite)
```bash
cd MainPage/frontend
npm install
cp .env.example .env
npm run dev
# Открыть: http://localhost:8000
```

### Шаг 3: PHP Laravel (опционально)
```bash
cd php-server
composer install
npm install
cp .env.example .env
php artisan migrate --seed
composer run dev
# Открыть: http://localhost:3333
```

### Шаг 4: Telegram-бот (опционально)
```bash
cd telegramBOT
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

### Шаг 5: Camera Server (опционально)
```bash
cd CameraMonitor_Python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

## 🛠️ Решение проблем

### ❌ Порты уже заняты
```powershell
# Windows: завершить процессы
taskkill /IM node.exe /F
taskkill /IM python.exe /F
taskkill /IM php.exe /F
```

### ❌ npm install не работает
```bash
cd MainPage/backend
rm -rf node_modules package-lock.json
npm install
```

### ❌ Python модули не найдены
```bash
cd telegramBOT
pip install --upgrade pip
pip install -r requirements.txt
```

### ❌ Нет прав на запуск скрипта (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\start-project.ps1
```

---

## 📋 Переменные окружения (.env)

### MainPage/backend/.env
```env
PORT=4000
JWT_ACCESS_SECRET=your-secret-key
ALLOWED_ORIGINS=http://localhost:8000
SCHEDULE_PROVIDER_MODE=http
SCHEDULE_PROVIDER_HTTP_URL=http://localhost:3333/api/schedule
```

### MainPage/frontend/.env
```env
VITE_API_URL=http://localhost:4000/api/v1
```

### php-server/.env
```env
APP_NAME=ENERGO
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:3333
DB_CONNECTION=sqlite
```

### telegramBOT/.env
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
JAVA_BASE_URL=http://localhost:3333
LOG_LEVEL=INFO
```

### CameraMonitor_Python/config/settings.ini
```ini
[server]
host=0.0.0.0
port=8888

[camera]
enabled=true
source=0
```

---

## 📝 Технологии

| Слой | Стек |
|------|------|
| **Frontend** | React 19, Vite, Ant Design |
| **Backend** | Node.js, Fastify, Prisma ORM |
| **Secondary** | PHP 8.3, Laravel 13 |
| **Bot/CV** | Python, aiogram, OpenCV, YOLO |
| **Database** | SQLite |

---

## ✅ Проверка: всё ли работает?

После запуска проверь в браузере:

1. **http://localhost:8000** — должен открыться главный интерфейс ✓
2. **http://localhost:4000/docs** — API документация ✓
3. **http://localhost:3333** — Laravel запущен ✓
4. **Telegram** — бот слушает команды ✓

---

## 🔄 Остановка всех сервисов

**Вариант 1:** Нажми `Ctrl+C` в каждом окне терминала

**Вариант 2:** Выполни в PowerShell:
```powershell
taskkill /IM node.exe /F
taskkill /IM python.exe /F
taskkill /IM php.exe /F
```

---

### Запуск в режиме разработки с hot-reload:

```bash
# Terminal 1: Backend
cd MainPage/backend && npm run dev

# Terminal 2: Frontend  
cd MainPage/frontend && npm run dev

# Terminal 3: PHP Laravel
cd php-server && composer run dev
```

