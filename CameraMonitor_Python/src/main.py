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

from src.core.config import Config
from src.utils.logger import get_logger_manager, get_logger


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

        # TODO: Инициализация компонентов
        # - База данных
        # - Камера
        # - Детекция
        # - GUI
        # - Сеть

        logger.info("Инициализация компонентов...")

        # Пока просто выводим информацию о конфигурации
        logger.info(f"Путь к БД: {config.db_path}")
        logger.info(f"RTSP URL камеры: {config.camera_rtsp_url}")
        logger.info(f"Порт UDP сервера: {config.udp_listen_port}")

        logger.info("Camera Monitor Python готов к работе")

        # TODO: Запуск основного цикла приложения
        # Пока просто завершаемся
        logger.info("Завершение работы")

    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()