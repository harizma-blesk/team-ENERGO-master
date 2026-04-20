# Camera Monitor - Python Version (В разработке)

Переведенная с C++/Qt на Python версия системы мониторинга кабинетов с использованием компьютерного зрения (YOLO).

## 📋 Статус проекта

**Текущий статус**: 🏗️ Фаза 1 - Базовая структура (завершена)

**Завершено**:
- ✅ Создана структура проекта (src/core, src/gui, src/utils, tests)
- ✅ Реализована система конфигурации (Config класс)
- ✅ Реализована система логирования (LoggerManager)
- ✅ Создана базовая структура БД (DatabaseManager с SQLAlchemy)
- ✅ Написаны базовые тесты

**Следующий шаг**: Фаза 2 - Core модули (камера, детекция, сеть)

## 🎯 Цель проекта

Полностью переписать систему мониторинга с C++/Qt на Python с сохранением функциональности:
- Live мониторинг видео потока с камеры
- Детекция людей через YOLO11/v8
- Поиск свободных кабинетов по расписанию
- Интеграция с SQLite БД
- Сетевая коммуникация (UDP/TCP)

## 📦 Технологический стек

- **GUI**: PyQt6 (вместо QML)
- **Видео**: OpenCV (как было, но без Qt интеграции)
- **ML**: ultralytics YOLO (вместо ONNX Runtime)
- **БД**: SQLite (вместо SQL Server)
- **Сеть**: Python sockets (вместо Qt Networking)
- **Конфиг**: configparser (совместимо с .ini)

## 📚 Документация

- **[MIGRATION_PLAN.md](MIGRATION_PLAN.md)** - Полный план миграции (8 фаз)
- **[INSTALL.md](INSTALL.md)** - Инструкция установки (будет)
- **[USAGE.md](USAGE.md)** - Руководство использования (будет)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Архитектура проекта (будет)

## 🚀 Быстрый старт (после разработки)

```bash
# Клонировать репо
git clone <repo_url>
cd CameraMonitor_Python

# Создать virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# или source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python -m src.main
```

## 🏗️ Структура проекта

```
CameraMonitor_Python/
├── src/                    # Исходный код
│   ├── core/              # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py      # Конфигурация
│   │   └── database.py    # Работа с БД
│   ├── gui/               # Графический интерфейс
│   │   └── __init__.py
│   └── utils/             # Утилиты
│       ├── __init__.py
│       └── logger.py      # Логирование
├── tests/                 # Тесты
│   ├── __init__.py
│   ├── test_config.py
│   └── test_database.py
├── config/                # Конфигурационные файлы
│   ├── settings.ini       # Основные настройки
│   └── settings.ini.example
├── models/                # ML модели
├── requirements.txt       # Зависимости Python
└── README.md
```

## 🎯 Цель проекта

Полностью переписать систему мониторинга с C++/Qt на Python с сохранением функциональности:
- Live мониторинг видео потока с камеры
- Детекция людей через YOLO11/v8
- Поиск свободных кабинетов по расписанию
- Интеграция с SQLite БД
- Сетевая коммуникация (UDP/TCP)

## 📦 Технологический стек

- **GUI**: PyQt6 (вместо QML)
- **Видео**: OpenCV (как было, но без Qt интеграции)
- **ML**: ultralytics YOLO (вместо ONNX Runtime)
- **БД**: SQLite (вместо SQL Server)
- **Сеть**: Python sockets (вместо Qt Networking)
- **Конфиг**: configparser (совместимо с .ini)

## 📚 Документация

- **[MIGRATION_PLAN.md](MIGRATION_PLAN.md)** - Полный план миграции (8 фаз)
- **[INSTALL.md](INSTALL.md)** - Инструкция установки (будет)
- **[USAGE.md](USAGE.md)** - Руководство использования (будет)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Архитектура проекта (будет)

## 🚀 Быстрый старт (после разработки)

```bash
# Клонировать репо
git clone <repo_url>
cd CameraMonitor_Python

# Создать virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# или source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
python run.py
```

## 📁 Структура проекта

```
CameraMonitor_Python/
├── src/               # Исходный код
│   ├── gui/          # PyQt6 интерфейсы
│   ├── core/         # Бизнес-логика
│   └── utils/        # Утилиты
├── config/           # Конфигурационные файлы
├── models/           # YOLO модели (скачиваются автоматически)
├── tests/            # Тесты
├── scripts/          # Вспомогательные скрипты
├── requirements.txt  # Зависимости
├── run.py           # Точка входа
└── MIGRATION_PLAN.md # План разработки
```

## ⏱️ График разработки

| Фаза | Описание | Время | Статус |
|------|---------|-------|--------|
| 1 | Подготовка окружения | 0.5 дня | ⏳ |
| 2 | Инфраструктура (config, БД, логирование) | 1 день | ⏳ |
| 3 | Видео + детекция (camera, YOLO) | 1.5 дня | ⏳ |
| 4 | Сетевая коммуникация (UDP/TCP) | 1 день | ⏳ |
| 5 | GUI интерфейсы (PyQt6) | 2 дня | ⏳ |
| 6 | Интеграция всех компонентов | 0.5 дня | ⏳ |
| 7 | Тестирование | 1 день | ⏳ |
| 8 | Документация + миграция данных | 1 день | ⏳ |

**Всего**: ~9 дней активной разработки (2 недели календарного времени)

## 🔄 Сравнение C++ vs Python

| Параметр | C++ | Python |
|----------|-----|--------|
| Язык | C++17 + QML | Python 3.10+ |
| GUI Framework | Qt 6 | PyQt6 |
| ML Framework | ONNX Runtime | ultralytics |
| БД | SQL Server | SQLite |
| Строк кода | ~2000+ | ~1500 |
| Скорость разработки | ⭐⭐ | ⭐⭐⭐⭐ |
| Кроссплатформенность | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Production ready | ✓ | ⏳ |

## 📝 План действий

### Перед началом
- [ ] Прочитать MIGRATION_PLAN.md полностью
- [ ] Убедиться что Python 3.10+ установлен
- [ ] Клонировать репо и создать новую ветку `develop`

### Фаза 1-2: Инфраструктура
- [ ] Создать virtual environment
- [ ] Установить зависимости (pip install -r requirements.txt)
- [ ] Реализовать config.py (парсинг settings.ini)
- [ ] Реализовать database.py (SQLAlchemy ORM)
- [ ] Реализовать logger.py

### Фаза 3-4: Core функциональность
- [ ] Реализовать camera.py (OpenCV + threading)
- [ ] Реализовать detector.py (ultralytics YOLO)
- [ ] Реализовать network.py (UDP/TCP)
- [ ] Создать image_utils.py (конверсия изображений)

### Фаза 5-6: GUI и интеграция
- [ ] Реализовать main_window.py (QMainWindow + tabs)
- [ ] Реализовать camera_window.py (live видео + детекция)
- [ ] Реализовать request_window.py (поиск кабинетов)
- [ ] Создать main.py (точка входа)

### Фаза 7-8: Тестирование и документация
- [ ] Написать unit тесты
- [ ] Провести интеграционное тестирование
- [ ] Написать документацию
- [ ] Подготовить релиз

## ⚠️ Важные моменты

1. **Работа НЕ начата** - это только план
2. **SQLite уже используется** - нет миграции с SQL Server
3. **Docker не требуется** - простое Python приложение
4. **Совместимость конфига** - settings.ini формат сохранён
5. **CUDA опционально** - для GPU ускорения YOLO

## 🤝 Контрибьюторы

- Начало разработки: TBD

## 📞 Контакты

Для вопросов по плану - смотрите MIGRATION_PLAN.md
