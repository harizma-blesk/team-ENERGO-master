# 🚀 Быстрый старт разработки

Этот файл содержит пошаговые инструкции для начала разработки Python версии проекта.

## Предварительные требования

- **Python 3.10 или выше** - [скачать](https://www.python.org/downloads/)
- **Git** - для управления версиями
- **Текстовый редактор/IDE** - VS Code, PyCharm или другой

## Шаг 1: Подготовка

```bash
# Перейти в папку проекта
cd CameraMonitor_Python

# Создать virtual environment
python -m venv venv

# Активировать virtual environment
# На Windows:
venv\Scripts\activate
# На Linux/Mac:
source venv/bin/activate
```

## Шаг 2: Установка зависимостей

```bash
# Обновить pip
python -m pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt

# Проверить что всё установилось
pip list
```

## Шаг 3: Скачивание YOLO модели

```bash
# Скачать YOLOv8 nano модель (автоматически)
python -c "from ultralytics import YOLO; model = YOLO('models/yolov8n.pt')"

# Проверить что модель скачалась
ls models/  # или dir models\ на Windows
```

## Шаг 4: Конфигурация

```bash
# Скопировать пример конфига
cp config/settings.ini.example config/settings.ini
# На Windows: copy config\settings.ini.example config\settings.ini

# Скопировать .env пример
cp .env.example .env
# На Windows: copy .env.example .env

# Отредактировать config/settings.ini с вашими параметрами
# Отредактировать .env если нужно
```

## Шаг 5: Инициализация Git

```bash
# Инициализировать Git репо (если ещё не сделано)
git init

# Добавить все файлы
git add .

# Первый commit
git commit -m "Initial project setup with migration plan"

# Создать новую ветку для разработки
git checkout -b develop
```

## Шаг 6: Структура проекта готова!

```
✓ Virtual environment настроен
✓ Зависимости установлены
✓ YOLO модель скачана
✓ Конфиг готов
✓ Git инициализирован

Готово к разработке! 🎉
```

## Следующие шаги

1. **Прочитайте план**: Откройте `MIGRATION_PLAN.md`
2. **Начните фазу 1**: Следуйте инструкциям по этапам
3. **Следите за прогрессом**: Используйте `CHECKLIST.md`

## Команды для разработки

```bash
# Активировать окружение (каждый раз когда открываете терминал)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установить новые зависимости
pip install <package_name>

# Обновить requirements.txt
pip freeze > requirements.txt

# Запустить приложение (после реализации)
python run.py

# Запустить тесты (после написания)
python -m pytest tests/

# Деактивировать окружение
deactivate
```

## Решение проблем

### Проблема: "python: command not found"
**Решение**: Убедитесь что Python установлен и добавлен в PATH

### Проблема: "No module named venv"
**Решение**: Установите Python с разработческими инструментами

### Проблема: PyQt6 не устанавливается
**Решение**: 
```bash
pip install PyQt6 --upgrade --force-reinstall
```

### Проблема: YOLO модель долго скачивается
**Решение**: Скачайте вручную и положите в `models/yolov8n.pt`

## Структура для начала разработки

```
CameraMonitor_Python/
├── src/              # Начните отсюда! ← 
│   ├── gui/         
│   ├── core/        
│   └── utils/       
├── config/          
│   └── settings.ini.example  ← Скопируйте в settings.ini
├── models/          # Модели будут здесь
├── requirements.txt ✓ (готов)
├── README.md        ✓ (готов)
├── MIGRATION_PLAN.md ✓ (готов - читайте этот!)
└── CHECKLIST.md     ✓ (готов)
```

## Что дальше?

1. **День 1**: Реализуйте `src/core/config.py`, `src/core/database.py`, `src/utils/logger.py`
2. **День 2**: Реализуйте `src/core/camera.py`, `src/core/detector.py`
3. **День 3**: Реализуйте `src/core/network.py`
4. **День 4-5**: Реализуйте GUI компоненты в `src/gui/`
5. **День 6**: Создайте `src/main.py` и `run.py`
6. **День 7+**: Тестирование и документация

Для подробностей смотрите **MIGRATION_PLAN.md** - там всё расписано по фазам!

## Полезные ссылки

- [PyQt6 документация](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [OpenCV документация](https://docs.opencv.org/)
- [ultralytics YOLO](https://docs.ultralytics.com/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)

---

**Готовы начать разработку? 🚀**

Прочитайте `MIGRATION_PLAN.md` и следуйте фазам разработки!
