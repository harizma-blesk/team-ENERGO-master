# 📋 Подробный план миграции C++ → Python

## 1. Обзор проекта

### Текущая архитектура (C++/Qt):
- **GUI**: QML + Qt Quick Controls 2 → Темная тема, live видео
- **Видео**: OpenCV + ImageProvider (custom renderer) 
- **ML**: YOLOv11/v8 через ONNX Runtime
- **БД**: SQL Server (ODBC драйвер)
- **Сеть**: Qt UDP/TCP сокеты
- **Конфиг**: settings.ini файл
- **Платформа**: Windows, встроенные DLL, exe файлы

### Целевая архитектура (Python):
- **GUI**: PyQt6 (widget-based, замена QML)
- **Видео**: OpenCV + прямое отображение через QImage/QPixmap
- **ML**: ultralytics YOLO (нативная, более проста)
- **БД**: SQLite (file-based, как указано)
- **Сеть**: Python sockets + threading
- **Конфиг**: configparser + .ini файл (совместимый формат)
- **Платформа**: Windows + Linux/Mac поддержка

---

## 2. Компоненты для миграции

### 2.1 GUI компоненты

| C++ (QML) | Python (PyQt6) | Сложность | Заметки |
|-----------|---|---|---|
| CameraCheckerWindow | CameraWindow widget | ⭐⭐ | Live видео + детекция + индикатор |
| RequestWindow | RequestWindow widget | ⭐⭐ | Форма поиска + таблица результатов |
| Темная тема (CSS) | QPalette + stylesheets | ⭐ | Одинаковая темная тема |
| ImageProvider | QLabel + QPixmap | ⭐ | Обновление frame через timer |
| Анимации (мигание) | QPropertyAnimation или timers | ⭐⭐ | Анимация индикатора занятости |

### 2.2 Бизнес-логика компоненты

| Компонент | Исходный формат | Целевой формат | Сложность | Файл |
|-----------|---|---|---|---|
| Конфигурация | settings.ini (Qt) | configparser .ini | ⭐ | src/core/config.py |
| БД операции | SQL Server ORM | SQLAlchemy + SQLite | ⭐⭐ | src/core/database.py |
| Захват видео | OpenCV + Qt threads | OpenCV + Python threading | ⭐⭐ | src/core/camera.py |
| YOLO детекция | ONNX Runtime | ultralytics YOLO | ⭐⭐ | src/core/detector.py |
| UDP/TCP сеть | Qt Networking | Python sockets | ⭐⭐ | src/core/network.py |

### 2.3 Утилиты и вспомогательные

| Функция | Исходный | Целевой | Файл |
|---------|---------|--------|------|
| Конвертация изображений | Qt Image conversion | OpenCV + PIL | src/utils/image_utils.py |
| Логирование | qDebug() | logging module | src/utils/logger.py |
| Валидация данных | Custom validators | Pydantic или custom | src/utils/validators.py |

---

## 3. Фаза 1: Подготовка окружения

### Цель
Настроить виртуальное окружение и базовую структуру проекта

### Что нужно сделать
1. **Создать virtual environment**
   - Файл: `venv/` (локальное окружение)
   - Команда: `python -m venv venv`

2. **Установить зависимости**
   - Файл: `requirements.txt`
   - Содержит: PyQt6, opencv-python, ultralytics, sqlalchemy, pillow и т.д.

3. **Создать структуру папок** ✓ (уже создано)
   ```
   CameraMonitor_Python/
   ├── src/
   │   ├── gui/
   │   ├── core/
   │   └── utils/
   ├── config/
   ├── models/
   ├── tests/
   └── README.md
   ```

4. **Инициализировать Git**
   - `.gitignore` (исключить venv, __pycache__, *.db и т.д.)

### Артефакты
- `requirements.txt`
- `.gitignore`
- `README.md` (Getting Started)
- Все папки структуры

### Время: 0.5 дня

---

## 4. Фаза 2: Базовая инфраструктура

### Цель
Создать основные системы конфигурации, БД и логирования

### 4.1 Конфигурация (config.py)

**Исходный файл C++**: `settings.ini` (Qt ConfigParser)

**Что нужно сделать**:
- Прочитать существующий `settings.ini` из папки C++
- Создать `config/settings.ini` (совместимый с configparser)
- Реализовать `src/core/config.py` класс для парсинга конфига
- Поддержать все секции:
  - [Database] - path к SQLite
  - [Camera] - RTSP URL, индекс камеры
  - [UDP] - IP/порты для сетевых операций
  - [NEUROMODEL] - пути к YOLO моделям
  - [TCP_Servers] - Java, ESP параметры

**Файлы**:
- `config/settings.ini` (новый)
- `src/core/config.py` (новый)

### 4.2 База данных (database.py)

**Исходный формат**: SQL Server + ODBC

**Что нужно сделать**:
- Создать SQLAlchemy ORM модели для таблиц:
  - Cameras (camera_id, name, rtsp_url, status)
  - CabinetBookings (cabinet_id, corpus, start_time, end_time, people_count)
  - Notifications (message, type, read_status)
- Реализовать `src/core/database.py` DatabaseManager класс
- Настроить SQLite путь из конфига
- Включить автоматическое создание таблиц при первом запуске

**Файлы**:
- `src/core/database.py` (новый)
- `config/schema.sql` (опционально, для документации)

### 4.3 Логирование (logger.py)

**Что нужно сделать**:
- Создать `src/utils/logger.py` утилиту
- Настроить логирование в файл и консоль
- Ротация файлов логов (max 10MB)
- Уровни: DEBUG, INFO, WARNING, ERROR

**Файлы**:
- `src/utils/logger.py` (новый)

### Артефакты
- `config/settings.ini`
- `src/core/config.py`
- `src/core/database.py`
- `src/utils/logger.py`
- SQLite БД файл: `camera_monitor.db` (будет создан при запуске)

### Время: 1 день

---

## 5. Фаза 3: Обработка видео и компьютерное зрение

### Цель
Реализовать захват видео и детекцию людей

### 5.1 Захват видео (camera.py)

**Исходный код**: C++ OpenCV + Qt threads + ImageProvider

**Что нужно сделать**:
- Реализовать `src/core/camera.py` CameraManager класс
- Поддержать два режима:
  1. RTSP поток (из config.camera_rtsp)
  2. Локальная вебкамера (camera_index)
- Использовать Python threading для неблокирующего захвата
- Очередь frames (Queue) для синхронизации с GUI потоком
- Обработка ошибок соединения (retry logic)
- Методы: start(), stop(), get_frame()

**Файлы**:
- `src/core/camera.py` (новый)

### 5.2 Конвертация изображений (image_utils.py)

**Исходный код**: Qt Image conversion + OpenCV rendering

**Что нужно сделать**:
- Реализовать `src/utils/image_utils.py` ImageConverter класс
- Функции конверсии:
  1. OpenCV BGR → PyQt6 QImage (RGB)
  2. OpenCV ndarray → QPixmap с масштабированием
  3. Рисование bounding boxes на frame
  4. Resize/crop операции

**Файлы**:
- `src/utils/image_utils.py` (новый)

### 5.3 YOLO детекция (detector.py)

**Исходный код**: ONNX Runtime + YOLOv11/v8

**Что нужно сделать**:
- Реализовать `src/core/detector.py` PersonDetector класс
- Использовать ultralytics YOLO (yolov8n.pt - нано версия)
- Фильтрация результатов: только класс "person" (COCO class 0)
- Постобработка:
  1. Вычисление количества людей
  2. Координаты bounding boxes
  3. Confidence scores
- Методы: detect_people(frame) → (detections, count)
- Опционально: GPU ускорение если доступна CUDA

**Файлы**:
- `src/core/detector.py` (новый)

### 5.4 Скачивание моделей

**Что нужно сделать**:
- Скрипт скачивания YOLO моделей в папку `models/`
- Два варианта:
  1. yolov8n.pt (nano - быстро)
  2. yolov11n.pt (более новая, если нужна)

**Файлы**:
- `scripts/download_models.py` (новый)

### Артефакты
- `src/core/camera.py`
- `src/utils/image_utils.py`
- `src/core/detector.py`
- `models/yolov8n.pt` (скачивается автоматически)

### Время: 1.5 дня

---

## 6. Фаза 4: Сетевая коммуникация

### Цель
Реализовать UDP/TCP коммуникацию

### Что нужно сделать
- Реализовать `src/core/network.py` с классами:
  1. **UDPServer** - слушать входящие UDP сообщения от Python backend
  2. **UDPClient** - отправлять сообщения к Python backend
  3. **TCPClient** - подключаться к Java/ESP серверам

- Функциональность:
  1. Асинхронный приём сообщений (threading)
  2. JSON формат обмена данными
  3. Reconnect logic при разрыве соединения
  4. Callback обработчики для входящих сообщений

- Интеграция:
  1. Отправить данные о занятости кабинета (people_count)
  2. Получить результаты поиска кабинетов
  3. Обработка команд от backend

**Файлы**:
- `src/core/network.py` (новый)

### Время: 1 день

---

## 7. Фаза 5: GUI интерфейс

### Цель
Реализовать пользовательский интерфейс на PyQt6

### 7.1 Главное окно (main_window.py)

**Исходный**: QML Window + Tab Container

**Что нужно сделать**:
- Создать `src/gui/main_window.py` MainWindow класс (QMainWindow)
- Таб-интерфейс (QTabWidget):
  1. Первый таб: "Мониторинг камеры" → CameraWindow
  2. Второй таб: "Поиск кабинетов" → RequestWindow
- Status bar внизу
- Темная тема (QSS stylesheets)

**Файлы**:
- `src/gui/main_window.py` (новый)
- `src/gui/styles.qss` (новый, опционально)

### 7.2 Окно камеры (camera_window.py)

**Исходный**: CameraCheckerWindow.qml

**Что нужно сделать**:
- Создать `src/gui/camera_window.py` CameraWindow виджет
- Компоненты:
  1. **Заголовок**: "Live Поток: Камера ноутбука"
  2. **Основная область**: QLabel для отображения видео
  3. **Индикатор детекции**: красная точка в углу (мигает при обнаружении)
  4. **Статус панель**: 
     - Левая часть: Прямоугольник с ЗАНО/СВОБОДНО + количество
     - Правая часть: "Статус: Система активна"

- Функциональность:
  1. Timer (30 FPS) для обновления frames
  2. Интеграция CameraManager для захвата
  3. Интеграция PersonDetector для детекции
  4. Анимация мигания индикатора
  5. Подсчёт и отображение людей в реальном времени

- Цвета:
  - Фон: тёмная (#121212)
  - Статус ЗАНЯТО: красный (#b71c1c)
  - Статус СВОБОДНО: зелёный (#1b5e20)
  - Текст: белый/серый

**Файлы**:
- `src/gui/camera_window.py` (новый)

### 7.3 Окно поиска кабинетов (request_window.py)

**Исходный**: RequestWindow.qml

**Что нужно сделать**:
- Создать `src/gui/request_window.py` RequestWindow виджет
- Компоненты:
  1. **Форма ввода**:
     - TextField "Корпус" (A, B, C...)
     - TextField "Время" (HH:mm format)
     - SpinBox "Длительность" (15-300 мин, шаг 15)
  2. **Кнопки**:
     - "Найти" - поиск свободных кабинетов
     - "Очистить бронь" - очистить временные брони
  3. **Статус сообщение** - error/success feedback
  4. **Таблица результатов** - показать найденные кабинеты

- Функциональность:
  1. Валидация входных данных
  2. Запрос к БД для поиска свободных
  3. Отправка запроса через UDP к backend
  4. Отображение результатов в таблице
  5. Обработка ошибок

**Файлы**:
- `src/gui/request_window.py` (новый)

### 7.4 Общие компоненты (widgets.py)

**Что нужно сделать**:
- Создать `src/gui/widgets.py` для переиспользуемых компонентов:
  1. StatusPanel - виджет статуса
  2. IndicatorLight - индикатор (мигающий/статичный)
  3. StyledButton - стилизованная кнопка
  4. Другие общие элементы

**Файлы**:
- `src/gui/widgets.py` (новый)

### Артефакты
- `src/gui/main_window.py`
- `src/gui/camera_window.py`
- `src/gui/request_window.py`
- `src/gui/widgets.py` (опционально)
- `src/gui/styles.qss` (опционально)

### Время: 2 дня

---

## 8. Фаза 6: Интеграция и запуск

### Цель
Собрать все компоненты в единое приложение

### Что нужно сделать

**8.1 Главный файл приложения (main.py)**
- Создать `src/main.py`
- Инициализация:
  1. Парсинг конфига
  2. Инициализация БД
  3. Запуск логирования
  4. Создание главного окна
  5. Обработка ошибок запуска

**8.2 Скрипт запуска (run.py)**
- Создать `run.py` - точка входа
- Команда: `python run.py`

**8.3 setup.py**
- Конфигурация setuptools
- Зависимости
- Entry point для установки

**8.4 .env файлы**
- `.env.example` - пример переменных окружения
- Параметры для девелопмента/продакшена

### Артефакты
- `src/main.py`
- `run.py`
- `setup.py`
- `.env.example`

### Время: 0.5 дня

---

## 9. Фаза 7: Тестирование

### Цель
Убедиться что все компоненты работают корректно

### Что нужно тестировать

| Компонент | Тип теста | Файл |
|-----------|-----------|------|
| Config | Unit test | tests/test_config.py |
| Database | Unit test | tests/test_database.py |
| Camera | Integration test | tests/test_camera.py |
| Detector | Unit test | tests/test_detector.py |
| Network | Unit test | tests/test_network.py |
| GUI | Manual test | tests/manual_gui_test.md |

### Что нужно сделать
- Написать unit тесты для критических функций
- Интеграционные тесты для взаимодействия компонентов
- Ручное тестирование GUI
- Тестирование производительности (FPS, CPU/RAM)

### Артефакты
- `tests/test_config.py`
- `tests/test_database.py`
- `tests/test_camera.py`
- `tests/test_detector.py`
- `tests/test_network.py`
- `tests/manual_gui_test.md`

### Время: 1 день

---

## 10. Фаза 8: Документация и миграция данных

### Что нужно сделать

**10.1 Миграция данных (если нужна)**
- Создать `scripts/migrate_from_sqlserver.py` (если раньше были данные в SQL Server)
- Экспорт → CSV → Импорт в SQLite

**10.2 Документация**
- `README.md` - главная документация
- `INSTALL.md` - инструкция установки
- `USAGE.md` - инструкция использования
- `ARCHITECTURE.md` - описание архитектуры
- Docstrings в коде

**10.3 Конфигурация для production**
- `config/settings.prod.ini` - production конфиг
- `config/settings.dev.ini` - dev конфиг

### Артефакты
- `README.md` (дополнить)
- `INSTALL.md`
- `USAGE.md`
- `ARCHITECTURE.md`
- `scripts/migrate_from_sqlserver.py` (опционально)

### Время: 1 день

---

## 11. Что НЕ переводить / Оставить в C++

Некоторые компоненты могут остаться в C++:
- ESP/Java интеграция - обратная совместимость через TCP/UDP
- Очень тяжелые ML операции - переиспользовать через REST API
- Real-time обработка видео 4K+ - использовать C++ компоненты через subprocess

Но в этом плане предполагается полный переход на Python.

---

## 12. График разработки

```
Week 1:
  ├─ Phase 1: Подготовка (0.5 дня) ✓
  ├─ Phase 2: Инфраструктура (1 день)
  └─ Phase 3: Видео + детекция (1.5 дня)

Week 2:
  ├─ Phase 4: Сеть (1 день)
  └─ Phase 5: GUI (2 дня)

Week 3:
  ├─ Phase 6: Интеграция (0.5 дня)
  ├─ Phase 7: Тестирование (1 день)
  └─ Phase 8: Документация (1 день)
```

**Всего: ~9 дней активной разработки (2 недели calendar time)**

---

## 13. Зависимости проекта

```
PyQt6>=6.5.0              # GUI framework
opencv-python>=4.8.0      # Видео/обработка изображений
ultralytics>=8.0.0        # YOLO детекция
sqlalchemy>=2.0.0         # ORM БД
numpy>=1.24.0             # Матрицы
pillow>=10.0.0            # Обработка изображений
requests>=2.31.0          # HTTP запросы
configparser>=6.0.0       # Парсинг конфига
python-dotenv>=1.0.0      # .env файлы
```

---

## 14. Структура файлов итоговая

```
CameraMonitor_Python/
├── src/
│   ├── __init__.py
│   ├── main.py                        # Точка входа приложения
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py             # QMainWindow
│   │   ├── camera_window.py           # Таб камеры
│   │   ├── request_window.py          # Таб поиска
│   │   ├── widgets.py                 # Общие компоненты
│   │   └── styles.qss                 # Стили
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Конфигурация
│   │   ├── database.py                # SQLAlchemy ORM
│   │   ├── camera.py                  # Захват видео
│   │   ├── detector.py                # YOLO детекция
│   │   └── network.py                 # UDP/TCP сеть
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                  # Логирование
│       ├── image_utils.py             # Конверсия изображений
│       └── validators.py              # Валидация
│
├── config/
│   ├── settings.ini                   # Конфиг (dev)
│   ├── settings.prod.ini              # Конфиг (prod)
│   ├── schema.sql                     # SQLite схема (docs)
│   └── coco.names                     # YOLO класс имена
│
├── models/
│   └── yolov8n.pt                     # YOLO модель (скачивается)
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_camera.py
│   ├── test_detector.py
│   ├── test_network.py
│   └── manual_gui_test.md
│
├── scripts/
│   ├── download_models.py             # Скачивание YOLO
│   └── migrate_from_sqlserver.py      # Миграция БД (если нужна)
│
├── requirements.txt                   # Зависимости
├── setup.py                           # setuptools конфиг
├── run.py                             # Скрипт запуска
├── .env.example                       # Пример переменных
├── .gitignore                         # Git ignore rules
├── README.md                          # Документация
├── INSTALL.md                         # Инструкция установки
├── USAGE.md                           # Инструкция использования
├── ARCHITECTURE.md                    # Архитектура
└── MIGRATION_PLAN.md                  # Этот файл
```

---

## 15. Ключевые различия C++ vs Python

| Аспект | C++ | Python |
|--------|-----|--------|
| Компиляция | Нужна | Не нужна |
| Скорость разработки | Медленнее | Быстрее |
| Производительность | Высокая | Средняя (достаточно для этого) |
| ML библиотеки | Сложнее интеграция | Простая (ultralytics) |
| Кроссплатформенность | Qt помогает | Нативная |
| Поддержка | Зависит от Qt версии | Всегда актуальна |
| Зависимости | Много DLL | Pip пакеты |
| Размер бинаря | ~100+ MB (с Qt) | ~50-100 MB (venv) |

---

## 16. Возможные проблемы и решения

### Проблема: Низкий FPS при детекции
**Решение**: 
- Использовать меньшую модель (nano вместо small)
- Обработка каждого N-го фрейма для детекции
- GPU ускорение через CUDA (если доступна)
- Multi-threading обработка

### Проблема: RTSP поток разрывается
**Решение**:
- Reconnect logic с exponential backoff
- Fallback на локальную камеру
- Логирование всех ошибок
- Healthcheck пингов

### Проблема: SQLite блокировка
**Решение**:
- Использовать WAL mode
- Очень короткие транзакции
- Thread-safe операции (SessionLocal)

### Проблема: Утечка памяти в потоках
**Решение**:
- Правильное завершение потоков (join)
- Очистка ресурсов в finally блоках
- Профилирование памяти

---

## 17. Примеры кода (структура, без реализации)

Все файлы будут содержать:
1. Docstrings для всех функций
2. Type hints для параметров
3. Обработка ошибок
4. Логирование важных событий
5. Тесты

Примеры будут включены при начале разработки.

---

## 📌 ИТОГОВЫЙ ЧЕКЛИСТ

### Before Development ✓
- [x] Создана структура папок
- [x] Написан подробный план
- [x] Определены зависимости
- [x] Описаны все компоненты

### Ready to Start
- [ ] requirements.txt создан
- [ ] Virtual environment готов
- [ ] Git репо инициализирован
- [ ] Первый commit с планом

---

**Статус**: План завершён. Готов к разработке в соответствии с этапами.

