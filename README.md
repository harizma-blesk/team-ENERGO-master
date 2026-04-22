# team-ENERGO

Монорепозиторий системы для управления аудиториями и учебными активностями. Внутри объединены веб-интерфейсы, backend-сервисы, Telegram-бот, сервер компьютерного зрения для камер и прошивка для ESP-устройств.

## Что находится в репозитории

### `MainPage/`
Основной веб-продукт.

- `frontend/` - React 19 + Vite + TypeScript интерфейс.
- `backend/` - Fastify + TypeScript API, Prisma и интеграция с внешним сервером расписания.
- `docker-compose.yml` и `backend/docker-compose.yml` - локальная инфраструктура для разработки.

Функционально этот модуль покрывает:

- аутентификацию и роли;
- тесты и результаты;
- историю попыток;
- AI-активности;
- поиск аудиторий;
- интеграцию с внешним сервером расписания по HTTP/TCP/PUSH.

### `php-server/`
Laravel 13 сервис, который работает как мост для расписания и интеграций.

- REST API для загрузки расписания и работы с журналом аудиторий;
- bridge-эндпоинты для внешних клиентов;
- TCP-клиенты/отправители для связи с Python/другими сервисами.

### `telegramBOT/`
Telegram-бот на `aiogram`, который помогает искать свободные аудитории через внешнее API.

- сценарии `/find`, `/status`, `/logs`;
- хранение локальных пользовательских данных;
- логирование в файл и stdout;
- Dockerfile для контейнерного запуска.

### `MuitCameraServer-CameraServer/`
Подсистема камер и детекции занятости аудитории.

- Python-реализация camera server;
- исходники C++/Qt версии;
- тесты, mock-серверы и конфигурация;
- `Muit-Firmware/BookingServerESP` для ESP/PlatformIO.

### `C++/`
Собранные бинарные зависимости, Qt runtime, модели YOLO и desktop-артефакты. Судя по содержимому, это скорее подготовленный runtime/дистрибутив, а не папка с исходниками.

### `adminPanel/`
Небольшая статическая админ-страница на HTML/CSS/JS.

### Прочее

- `mock_server.py` - вспомогательный mock-сервер.
- `schedule_template.xlsx` - шаблон расписания.
- `scripts/` - утилиты для очистки и обслуживания репозитория.

## Технологии

- Frontend: React, TypeScript, Vite, Ant Design
- Backend: Node.js, Fastify, Prisma
- Secondary backend: PHP 8.3, Laravel 13
- Bot / CV services: Python, aiogram, PyQt5, OpenCV, ultralytics
- Desktop / embedded: C++, Qt, PlatformIO, ESP32
- Data: PostgreSQL и локальные SQLite/runtime storage

## Полный пошаговый запуск проекта

Это монорепозиторий из четырёх независимых сервисов. Запуск можно организовать по-разному:
- **Минимальный** - только MainPage (веб-приложение)
- **Полный** - все сервисы (требует больше ресурсов)

Каждый сервис можно запускать отдельно в своём терминале.

---

## Предварительные требования (для всех)

Установите на машину:

1. **Node.js 20+** - https://nodejs.org/
2. **Python 3.11+** - https://www.python.org/
3. **Docker + Docker Compose** - https://www.docker.com/
4. **PHP 8.3+** + **Composer** - https://www.php.net/, https://getcomposer.org/
5. **Git** - для клонирования репозитория

Проверьте установку:

```bash
node --version
python --version
docker --version
php --version
composer --version
```

---

## Шаг 0: Подготовка (для всех сервисов)

Перейдите в корень репозитория:

```bash
cd team-ENERGO-master
```

---

## Шаг 1: MainPage (веб-приложение) - обязательный

Это основной сервис. Работает на `Node.js + React + Fastify`.

### 1.1 Инициализация backend

Откройте **первый терминал** и выполните:

```bash
cd MainPage/backend

# Установить зависимости
npm install

# Создать .env файл
copy .env.example .env
# Если .env.example не существует, создайте .env вручную с содержимым:
```

**Для первого запуска** отредактируйте `MainPage/backend/.env`:

```env
DATABASE_URL=postgresql://energo_user:energo_password@localhost:5432/energo_db
JWT_ACCESS_SECRET=your-super-secret-jwt-key-change-this-in-production
PORT=4000
ALLOWED_ORIGINS=http://localhost:5173
SCHEDULE_PROVIDER_MODE=http
SCHEDULE_PROVIDER_HTTP_URL=http://localhost:8080/api/schedule/subjects
```

### 1.2 Запуск Docker для PostgreSQL

Из папки `MainPage/backend` запустите:

```bash
docker compose up -d
```

Это поднимет PostgreSQL на `localhost:5432`. Дождитесь, пока БД будет готова (～20 секунд).

### 1.3 Инициализация БД

В том же терминале запустите миграции:

```bash
npx prisma migrate dev
npm run prisma:seed
```

### 1.4 Запуск backend

```bash
npm run dev
```

Backend будет доступен на `http://localhost:4000/api/v1`

Должны увидеть примерно:
```
Server running on port 4000
```

### 1.5 Инициализация frontend

Откройте **второй терминал** и выполните:

```bash
cd MainPage/frontend

npm install

# Создать .env если нужно
copy .env.example .env
```

### 1.6 Запуск frontend

```bash
npm run dev
```

Frontend будет доступен на `http://localhost:5173`

### ✅ MainPage готов!

- Откройте в браузере: `http://localhost:5173`
- API backend: `http://localhost:4000/api/v1`

---

## Шаг 2: PHP Laravel сервис - опционально (для интеграций)

Этот сервис работает как мост для расписания и нужен, если используются интеграции или Telegram-бот.

Откройте **третий терминал**:

```bash
cd php-server

# Копируем .env
copy .env.example .env
# или создайте вручную с минимальным содержимым

# Установить PHP зависимости
composer install

# Установить Node зависимости
npm install

# Генерировать приложение ключ
php artisan key:generate

# Запустить миграции БД
php artisan migrate

# Запустить dev-сервер
composer run dev
```

PHP-сервер будет доступен на `http://localhost:8000`

Основные эндпоинты:
- `GET /api/schedule/subjects` - получить расписание
- `GET /api/schedule/auditories` - список аудиторий
- `POST /api/bridge` - мост для интеграций

---

## Шаг 3: Telegram-бот - опционально (для поиска аудиторий)

Откройте **четвёртый терминал**:

```bash
cd telegramBOT

# Создать виртуальное окружение
python -m venv .venv

# Активировать окружение (Windows)
.venv\Scripts\activate

# или на Mac/Linux:
# source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
# Минимально нужны:
```

**Отредактируйте `.env` в папке `telegramBOT`:**

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
JAVA_BASE_URL=http://localhost:8000
LOG_LEVEL=INFO
STORAGE_PATH=data/users.json
LOG_PATH=logs/bot.log
```

Получить `TELEGRAM_BOT_TOKEN`:
1. Напишите `@BotFather` в Telegram
2. Команда `/newbot` и следуйте инструкциям
3. Скопируйте полученный токен

**Запуск бота:**

```bash
python main.py
```

Бот будет слушать входящие сообщения в Telegram. Доступные команды:
- `/find` - поиск свободной аудитории
- `/status` - статус аудиторий
- `/logs` - логи

---

## Шаг 4: Camera Server - опционально (для мониторинга камер)

Откройте **пятый терминал**:

```bash
cd CameraMonitor_Python

# Создать виртуальное окружение
python -m venv .venv

# Активировать (Windows)
.venv\Scripts\activate

# или Mac/Linux:
# source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Создать config
copy config/settings.ini.example config/settings.ini
```

**Отредактируйте `CameraMonitor_Python/config/settings.ini`** с параметрами камер и сервера.

**Тестирование (рекомендуется сначала):**

```bash
python validate.py
python -m pytest tests/
```

**Запуск сервера камер:**

```bash
python run.py
```

Camera server будет слушать входящие подключения для обработки видеопотока.

---

## Проверка: все ли запущено?

| Сервис | URL | Статус |
|--------|-----|--------|
| Frontend | `http://localhost:5173` | ✅ открыть в браузер |
| Backend API | `http://localhost:4000/api/v1` | ✅ /health или /docs |
| PHP/Laravel | `http://localhost:8000` | ✅ /api/schedule/subjects |
| Telegram Bot | Telegram App | ✅ отправить `/find` |
| Camera Server | `localhost:8888` (если включен) | ✅ проверить логи |
| PostgreSQL | `localhost:5432` | ✅ docker ps |

---

## Остановка всего

Когда захотите остановить все сервисы:

**В каждом терминале нажмите:** `Ctrl+C`

**Чтобы остановить Docker PostgreSQL:**

```bash
cd MainPage/backend
docker compose down
```

---

## Быстрый запуск (если уже всё настроено)

После первоначальной настройки, чтобы запустить всё снова:

```bash
# Терминал 1: Backend
cd MainPage/backend
npm run dev

# Терминал 2: Frontend
cd MainPage/frontend
npm run dev

# Терминал 3 (опционально): PHP
cd php-server
composer run dev

# Терминал 4 (опционально): Telegram Bot
cd telegramBOT
.venv\Scripts\activate
python main.py

# Терминал 5 (опционально): Camera Server
cd CameraMonitor_Python
.venv\Scripts\activate
python run.py
```

---

## Решение проблем

### ❌ Docker не запускается
```bash
docker compose up -d
# Проверить логи:
docker compose logs -f
```

### ❌ Node.js ошибка версии
```bash
node --version
# Должна быть 20+. Если нет, переустановите Node.js
```

### ❌ Python: модули не найдены
```bash
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### ❌ Prisma ошибка
```bash
cd MainPage/backend
npx prisma migrate reset
npm run prisma:seed
```

### ❌ Порты занято
Если ошибка "Address already in use":
- Измените PORT в `.env`
- Или завершите процесс: `netstat -ano | findstr :4000` (Windows)

---

## Архитектура сервисов

```
┌─────────────────────────────────────────────────────┐
│         Frontend (React + Vite)                      │
│         http://localhost:5173                        │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│      Backend (Fastify + Prisma)                     │
│      http://localhost:4000/api/v1                   │
│   ├─ Аутентификация                                 │
│   ├─ Тесты и результаты                             │
│   ├─ AI-активности                                  │
│   └─ Поиск аудиторий                                │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬─────────────┐
    │              │              │             │
┌───▼───┐   ┌─────▼──────┐   ┌──▼──────┐   ┌──▼──────┐
│PostgreSQL│   │ PHP Bridge │   │Telegram Bot│  │Camera  │
│         │   │ :8000      │   │ Server  │  │Server  │
└─────────┘   └────────────┘   └─────────┘  └────────┘
```

## Архитектура на уровне модулей

В проекте прослеживаются две основные цепочки:

1. Пользовательский контур:
`MainPage/frontend` -> `MainPage/backend` -> внешний сервер расписания / AI-сервисы

2. Контур аудиторий:
`telegramBOT` / `php-server` / `CameraServer` / ESP-устройства

То есть проект не является одним приложением с единым entrypoint. Это набор связанных сервисов под общую предметную область: расписание, поиск свободных аудиторий, тестирование и мониторинг занятости помещений.

## Что стоит учитывать при работе с репозиторием

- В репозитории уже есть крупные бинарные файлы, модели и runtime-библиотеки.
- `.gitignore` теперь настроен на локальные артефакты разработки: `.env`, `node_modules`, `vendor`, `.venv`, логи, временные файлы и локальные базы.
- `.gitignore` не удаляет уже отслеживаемые Git файлы. Если нужно убрать из индекса уже добавленные временные или бинарные файлы, это делается отдельной чисткой истории или `git rm --cached`.
- Для `MainPage/backend` сейчас в папке есть локальный `.env`, а для `telegramBOT` и `php-server` тоже присутствуют реальные секреты/локальные настройки, поэтому их нельзя коммитить.

## Рекомендации по следующему шагу

Если захотите, следующим сообщением могу:

1. подготовить отдельный документ с картой зависимостей между сервисами;
2. предложить чистку репозитория от лишних бинарников и временных файлов;
3. привести `README` к формату для публичного GitHub-репозитория с красивой структурой и инструкциями для команды.
