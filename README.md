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

## Быстрый старт

Из-за того, что это монорепозиторий из нескольких независимых сервисов, обычно запускают не всё сразу, а нужный модуль.

### 1. Основной веб-модуль `MainPage`

Требования:

- Node.js 20+
- Docker / Docker Compose
- PostgreSQL через compose

Запуск:

```bash
cd MainPage
npm install
copy frontend\.env.example frontend\.env
cd backend
docker compose up -d
npx prisma migrate dev
npm run prisma:seed
npm run dev
```

Отдельно frontend:

```bash
cd MainPage
npm run dev:frontend
```

Отдельно backend:

```bash
cd MainPage
npm run dev:backend
```

Полезные адреса:

- frontend: `http://localhost:5173`
- backend API: `http://localhost:4000/api/v1`

Для `MainPage/backend/.env` шаблон в репозитории сейчас не найден, поэтому файл нужно создать вручную. Минимально понадобятся:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/DB_NAME
JWT_ACCESS_SECRET=change-me-to-a-long-secret
PORT=4000
ALLOWED_ORIGINS=http://localhost:5173
SCHEDULE_PROVIDER_MODE=http
SCHEDULE_PROVIDER_HTTP_URL=http://localhost:8080/api/schedule/subjects
```

Дополнительно backend поддерживает:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `ROOM_FINDER_PHP_URL`
- `ROOM_FINDER_API_KEY`
- TCP/PUSH-настройки для расписания

### 2. Laravel сервис `php-server`

Требования:

- PHP 8.3+
- Composer
- Node.js

Запуск:

```bash
cd php-server
cp .env.example .env
composer install
npm install
php artisan key:generate
php artisan migrate
composer run dev
```

Основные API-маршруты:

- `POST /api/bridge`
- `GET /api/bridge`
- `POST /api/bridge/cancel`
- `POST /api/schedule/upload`
- `GET /api/schedule/auditories`
- `GET /api/schedule/journal`
- `GET /api/schedule/subjects`
- `POST /api/schedule/subjects/push`

### 3. Telegram-бот `telegramBOT`

Требования:

- Python 3.11+

Запуск:

```bash
cd telegramBOT
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

В текущем состоянии репозитория `.env.example` для бота не закоммичен, поэтому `.env` нужно создать вручную. Минимально нужны:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
JAVA_BASE_URL=http://localhost:8080
LOG_LEVEL=INFO
STORAGE_PATH=data/users.json
LOG_PATH=logs/bot.log
```

Полный пример переменных и форматов можно взять из [telegramBOT/README.md](</c:/team-ENERGO-master/telegramBOT/README.md>).

### 4. Camera server `MuitCameraServer-CameraServer/CameraServer`

Требования:

- Python 3.10+ желательно
- OpenCV / PyQt5 / ultralytics

Запуск:

```bash
cd MuitCameraServer-CameraServer/CameraServer
pip install -r requirements.txt
copy settings.ini.example settings.ini
python quick_check.py
python run_tests.py
python Server/main.py
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
