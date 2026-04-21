# 📋 Контрольный список подготовки проекта

## ✅ Завершено

### Структура проекта
- [x] Создана папка `CameraMonitor_Python/`
- [x] Созданы папки: `src/`, `config/`, `models/`, `tests/`, `scripts/`
- [x] Созданы подпапки: `src/gui/`, `src/core/`, `src/utils/`

### Документация
- [x] `README.md` - обзор проекта
- [x] `MIGRATION_PLAN.md` - полный план миграции (8 фаз + 17 разделов)
- [x] `requirements.txt` - список зависимостей
- [x] `.gitignore` - правила Git

### План содержит

**Фаза 1: Подготовка (0.5 дня)**
- Virtual environment setup
- Установка зависимостей
- Структура проекта (✓ уже создана)

**Фаза 2: Инфраструктура (1 день)**
- Config system (configparser)
- Database layer (SQLAlchemy + SQLite)
- Logging system

**Фаза 3: Видео & ML (1.5 дня)**
- Camera manager (OpenCV + threading)
- Image utilities (конверсия QImage/QPixmap)
- Person detector (ultralytics YOLO)

**Фаза 4: Сеть (1 день)**
- UDP Server/Client
- TCP Client
- JSON messaging

**Фаза 5: GUI (2 дня)**
- Main window (PyQt6)
- Camera window (live видео + детекция)
- Request window (поиск кабинетов)
- Shared widgets

**Фаза 6: Интеграция (0.5 дня)**
- main.py (точка входа)
- run.py (скрипт запуска)
- setup.py (setuptools конфиг)

**Фаза 7: Тестирование (1 день)**
- Unit тесты для всех компонентов
- Integration тесты
- Manual GUI тестирование

**Фаза 8: Документация (1 день)**
- INSTALL.md
- USAGE.md
- ARCHITECTURE.md
- Code documentation

---

## ⏳ К тому чтобы начать

### Перед началом разработки
- [ ] Убедиться что Python 3.10+ установлен
- [ ] Клонировать репо в новую ветку `develop`
- [ ] Прочитать MIGRATION_PLAN.md полностью

### День 1 (Фаза 1-2)
- [ ] `python -m venv venv`
- [ ] `venv\Scripts\activate`
- [ ] `pip install -r requirements.txt`
- [ ] Скачать YOLO модель: `python -c "from ultralytics import YOLO; YOLO('models/yolov8n.pt')"`
- [ ] Создать `src/core/config.py`
- [ ] Создать `src/core/database.py`
- [ ] Создать `src/utils/logger.py`
- [ ] Создать `config/settings.ini`

### День 2 (Фаза 3)
- [ ] Создать `src/core/camera.py`
- [ ] Создать `src/utils/image_utils.py`
- [ ] Создать `src/core/detector.py`
- [ ] Скачать YOLO модели

### День 3 (Фаза 4)
- [ ] Создать `src/core/network.py`

### День 4-5 (Фаза 5)
- [ ] Создать `src/gui/main_window.py`
- [ ] Создать `src/gui/camera_window.py`
- [ ] Создать `src/gui/request_window.py`
- [ ] Создать `src/gui/widgets.py`

### День 6 (Фаза 6)
- [ ] Создать `src/main.py`
- [ ] Создать `run.py`
- [ ] Создать `setup.py`

### День 7 (Фаза 7)
- [ ] Написать тесты в `tests/`

### День 8-9 (Фаза 8)
- [ ] Написать `INSTALL.md`
- [ ] Написать `USAGE.md`
- [ ] Написать `ARCHITECTURE.md`

---

## 📊 Сравнение компонентов

### GUI
| C++ (QML) | Python (PyQt6) |
|-----------|---|
| CameraCheckerWindow.qml | src/gui/camera_window.py |
| RequestWindow.qml | src/gui/request_window.py |
| QML layouts | PyQt6 layouts |
| QML animations | PyQt6 QPropertyAnimation |

### Core
| C++ | Python |
|-----|--------|
| Settings.ini (Qt) | config.py + settings.ini |
| ODBC SQL Server | SQLAlchemy + SQLite |
| OpenCV + Qt threads | OpenCV + threading |
| ONNX Runtime | ultralytics YOLO |
| Qt Networking | Python sockets |

### Файлы что нужно создать

**src/core/** (5 файлов)
- config.py
- database.py
- camera.py
- detector.py
- network.py

**src/gui/** (4-5 файлов)
- main_window.py
- camera_window.py
- request_window.py
- widgets.py (опционально)
- styles.qss (опционально)

**src/utils/** (3 файла)
- logger.py
- image_utils.py
- validators.py (опционально)

**config/** (2 файла)
- settings.ini
- schema.sql (опционально)

**scripts/** (2 файла)
- download_models.py
- migrate_from_sqlserver.py (если нужна)

**tests/** (6+ файлов)
- test_config.py
- test_database.py
- test_camera.py
- test_detector.py
- test_network.py
- manual_gui_test.md

**Корневые файлы** (3 файла)
- src/main.py
- run.py
- setup.py

**Итого: ~30+ файлов для полной реализации**

---

## 🎯 Ключевые моменты

1. **Работа ещё НЕ начата** - это только план
2. **SQLite уже используется** - нет миграции от SQL Server
3. **Dockers не требуется** - простое приложение
4. **Все конфиги в .ini формате** - совместимо с оригиналом
5. **Модели скачиваются автоматически** - через ultralytics
6. **Python 3.10+** - минимально требуемая версия
7. **PyQt6, не PyQt5** - более современная версия

---

## 📞 Вопросы перед началом?

Смотрите `MIGRATION_PLAN.md` для подробностей по каждой фазе!
