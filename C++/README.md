# C++ Camera Monitoring System

## Описание проекта

Это Qt-based приложение для мониторинга кабинетов с использованием компьютерного зрения. Система включает:

- **Мониторинг камер**: Live поток с детекцией людей через YOLOv11/YOLOv8 модели
- **Система поиска кабинетов**: Поиск свободных аудиторий по корпусу, времени и длительности
- **Интеграция с базами данных**: Поддержка SQL Server для хранения информации о камерах и бронях
- **Сетевые возможности**: UDP/TCP коммуникация с Python/Java серверами и ESP устройствами

## Структура проекта

```
C++/
├── settings.ini              # Конфигурационный файл
├── win.exe                   # Основной исполняемый файл
├── win (1).exe              # Альтернативная версия
├── YOLOv11/                 # Нейронные модели
│   ├── yolo11n.onnx
│   └── yolov8n.onnx
├── qml/                     # QML интерфейсы
│   ├── CameraCheckerWindow.qml
│   ├── RequestWindow.qml
│   ├── QtQml/
│   └── QtQuick/
├── translations/            # Qt переводы (.qm файлы)
├── platforms/               # Qt платформенные плагины
├── imageformats/            # Qt плагины форматов изображений
├── sqldrivers/              # Qt драйверы баз данных
└── [другие Qt плагины и DLL]
```

## Зависимости

### Системные требования
- Windows 10/11
- Qt 6.x
- OpenCV 4.x
- FFmpeg
- Tesseract OCR
- ONNX Runtime

### Библиотеки (DLL файлы включены)
- Qt6Core, Qt6Gui, Qt6Widgets, Qt6Quick, Qt6Qml, etc.
- OpenCV (opencv_*.dll)
- FFmpeg (avcodec, avformat, etc.)
- Tesseract (tesseract55.dll)
- ONNX Runtime (onnxruntime.dll - предполагается в зависимостях)

## Конфигурация

Отредактируйте `settings.ini`:

```ini
[Database]
dbName=your_database
host=your_server\\SQLEXPRESS
user=your_user
password=your_password

[Camera]
startRtcp=rtsp://user:pass@camera_ip
endRtcp=/stream
cameraIndex=0

[UDP]
IP_PythonServer=127.0.0.1
IP_Port_Listen=5000
IP_Port_Send=5001
IP_Port_Remote=5002

[NEUROMODEL]
WeightsPath=YOLOv11/yolov8n.onnx
CocoNamesPath=path/to/coco.names

[TCP_Servers]
IP_Java=java_server_ip
PORT_Java=2222
IP_ESP=esp_device_ip
PORT_ESP=44444
```

## Запуск

1. Убедитесь, что все DLL файлы находятся в той же директории, что и exe
2. Настройте `settings.ini` с правильными параметрами
3. Запустите `win.exe`

## Функциональность

### CameraCheckerWindow
- Отображение live видео с камеры
- Детекция людей через YOLO модель
- Индикатор занятости кабинета
- Темная тема интерфейса

### RequestWindow
- Поиск свободных кабинетов
- Фильтрация по корпусу, времени, длительности
- Очистка временных броней

## Архитектура

- **Frontend**: QML (Qt Quick) для пользовательского интерфейса
- **Backend**: C++ с Qt для бизнес-логики
- **Computer Vision**: YOLOv11/v8 через ONNX Runtime
- **Database**: SQL Server через Qt SQL
- **Networking**: UDP/TCP для коммуникации с внешними сервисами

## Разработка

Проект использует Qt Creator для разработки. Основные компоненты:

- QML для UI
- C++ для логики
- ImageProvider для отображения видео в QML
- QObject для связи C++/QML

## Переводы

Приложение поддерживает множественные языки через Qt Linguist. Переводы находятся в папке `translations/`.