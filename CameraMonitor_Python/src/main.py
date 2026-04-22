#!/usr/bin/env python3
"""
Camera Monitor Python - Точка входа в приложение
"""

import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon

from src.core.config import Config
from src.core.database import DatabaseManager
from src.core.camera import CameraManager, CameraConfig
from src.core.detector import PersonDetector
from src.core.network import NetworkManager
from src.utils.logger import get_logger_manager, get_logger
from src.core.laravel_sync import LaravelSyncClient
from src.gui.main_window import MainWindow


def setup_application() -> QApplication:
    """Настройка Qt приложения"""
    app = QApplication(sys.argv)

    # Устанавливаем атрибуты приложения
    app.setApplicationName("Camera Monitor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CameraMonitor")
    app.setOrganizationDomain("cameramonitor.local")

    # Устанавливаем иконку приложения (если есть)
    # app.setWindowIcon(QIcon("resources/icons/app.png"))

    # Настройка локализации (если нужно)
    # translator = QTranslator()
    # if translator.load(QLocale.system(), "qt", "_", "translations"):
    #     app.installTranslator(translator)

    return app


def initialize_components(config: Config) -> tuple:
    """Инициализация всех компонентов приложения"""
    logger = get_logger(__name__)

    try:
        # Инициализация базы данных
        logger.info("Initializing database manager...")
        db_manager = DatabaseManager(config.db_path)

        logger.info("Initializing camera manager...")
        cameras = []
        for section in ['Camera1', 'Camera2']:
            if not config.parser.has_section(section):
                continue
            rtsp = config.parser.get(section, 'rtspUrl', fallback='')
            auditory_name = config.parser.get(section, 'auditoryName', fallback='')
            camera_name = config.parser.get(section, 'cameraName', fallback='')
            cam_cfg = CameraConfig(rtsp_url=rtsp or None, fps_target=config.fps_target)

            laravel_client = LaravelSyncClient(
                base_url=config.parser.get('Laravel', 'baseUrl', fallback=''),
                auditory_name=auditory_name,
                camera_name=camera_name,
                camera_address=rtsp,
                sync_interval_seconds=config.parser.getint('Laravel', 'syncIntervalSeconds', fallback=2),
                timeout_seconds=config.parser.getint('Laravel', 'timeoutSeconds', fallback=3),
                enabled=config.parser.getboolean('Laravel', 'enabled', fallback=True),
            )

            cameras.append({
                'manager': CameraManager(cam_cfg),
                'auditory_name': auditory_name,
                'camera_name': camera_name,
                'laravel_client': laravel_client,
            })
        camera_manager = cameras[0]['manager']  # для обратной совместимости

        # Инициализация детектора
        logger.info("Initializing person detector...")
        detector = PersonDetector(config.yolo_weights_path, config.yolo_conf_threshold)
        detector.load_model()

        # Инициализация сетевого менеджера
        logger.info("Initializing network manager...")
        network_manager = NetworkManager(config)

        logger.info("All components initialized successfully")
        return db_manager, camera_manager, detector, network_manager, cameras

    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise


def main():
    """Главная функция приложения"""
    try:
        # Определяем пути
        config_path = project_root / "config" / "settings.ini"

        # Загружаем конфигурацию
        config = Config(str(config_path))

        # Настраиваем логирование
        logger_manager = get_logger_manager(config)
        logger = get_logger(__name__)

        logger.info("Camera Monitor Python запущен")
        logger.info(f"Версия Python: {sys.version}")
        logger.info(f"Рабочая директория: {os.getcwd()}")

        # Настройка Qt приложения
        app = setup_application()

        # Инициализация компонентов
        db_manager, camera_manager, detector, network_manager, cameras = initialize_components(config)

        # Создание главного окна
        logger.info("Creating main window...")
        main_window = MainWindow(
            config=config,
            db_manager=db_manager,
            camera_manager=camera_manager,
            detector=detector,
            network_manager=network_manager,
            cameras=cameras
        )

        # Запуск сетевых компонентов
        logger.info("Starting network components...")
        network_manager.start()

        # Показываем окно
        main_window.show()

        # Запуск основного цикла приложения
        logger.info("Application started successfully")
        exit_code = app.exec()

        # Очистка ресурсов
        logger.info("Shutting down application...")
        network_manager.stop()
        camera_manager.stop_all_cameras()
        if hasattr(detector, 'unload_model'):
            detector.unload_model()

        logger.info("Application shutdown complete")
        return exit_code

    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())