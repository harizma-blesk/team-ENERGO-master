#!/usr/bin/env python3
"""
Скрипт для скачивания YOLO моделей
Скачивает модели YOLOv8/v11 в папку models/
"""

import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path
import argparse
import logging

# Добавляем корневую директорию в путь
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Доступные модели для скачивания
AVAILABLE_MODELS = {
    'yolov8n': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt',
        'size': '6.2 MB',
        'description': 'YOLOv8 Nano - самый быстрый, наименее точный'
    },
    'yolov8s': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8s.pt',
        'size': '21.5 MB',
        'description': 'YOLOv8 Small - баланс скорости и точности'
    },
    'yolov8m': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8m.pt',
        'size': '49.7 MB',
        'description': 'YOLOv8 Medium - хорошая точность'
    },
    'yolov8l': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8l.pt',
        'size': '83.7 MB',
        'description': 'YOLOv8 Large - высокая точность'
    },
    'yolov8x': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8x.pt',
        'size': '130.5 MB',
        'description': 'YOLOv8 XLarge - максимальная точность'
    },
    'yolov11n': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolo11n.pt',
        'size': '5.9 MB',
        'description': 'YOLOv11 Nano - новейшая архитектура, очень быстрый'
    },
    'yolov11s': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolo11s.pt',
        'size': '19.4 MB',
        'description': 'YOLOv11 Small - новейшая архитектура, баланс'
    }
}


def download_file(url: str, destination: Path, show_progress: bool = True) -> bool:
    """
    Скачать файл с отображением прогресса

    Args:
        url: URL для скачивания
        destination: Путь назначения
        show_progress: Показывать прогресс

    Returns:
        True если скачивание успешно
    """
    try:
        logger.info(f"Downloading from: {url}")
        logger.info(f"Saving to: {destination}")

        # Создаем директорию если не существует
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Скачиваем файл
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))

            with open(destination, 'wb') as f:
                downloaded = 0
                chunk_size = 8192

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    f.write(chunk)
                    downloaded += len(chunk)

                    if show_progress and total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(".1f", end='\r', flush=True)

        if show_progress:
            print()  # Новая строка после прогресса

        logger.info(f"Download completed: {destination}")
        return True

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return False


def verify_model(model_path: Path) -> bool:
    """
    Проверить что модель корректна

    Args:
        model_path: Путь к модели

    Returns:
        True если модель корректна
    """
    try:
        # Проверяем размер файла (минимум 1MB)
        if model_path.stat().st_size < 1024 * 1024:
            logger.error(f"Model file too small: {model_path}")
            return False

        # Проверяем расширение
        if model_path.suffix != '.pt':
            logger.error(f"Invalid model extension: {model_path}")
            return False

        logger.info(f"Model verification passed: {model_path}")
        return True

    except Exception as e:
        logger.error(f"Model verification failed: {e}")
        return False


def download_model(model_name: str, models_dir: Path = None,
                  force: bool = False) -> bool:
    """
    Скачать конкретную модель

    Args:
        model_name: Имя модели (yolov8n, yolov8s, etc.)
        models_dir: Директория для моделей (по умолчанию models/)
        force: Перезаписать существующую модель

    Returns:
        True если скачивание успешно
    """
    if model_name not in AVAILABLE_MODELS:
        logger.error(f"Unknown model: {model_name}")
        logger.info(f"Available models: {', '.join(AVAILABLE_MODELS.keys())}")
        return False

    # Определяем директорию
    if models_dir is None:
        models_dir = script_dir / "models"

    models_dir.mkdir(parents=True, exist_ok=True)

    model_info = AVAILABLE_MODELS[model_name]
    model_path = models_dir / f"{model_name}.pt"

    # Проверяем существует ли уже
    if model_path.exists() and not force:
        logger.info(f"Model already exists: {model_path}")
        if verify_model(model_path):
            logger.info("Model is valid, skipping download")
            return True
        else:
            logger.warning("Model exists but invalid, re-downloading")

    # Скачиваем
    logger.info(f"Downloading {model_name} ({model_info['size']})")
    logger.info(f"Description: {model_info['description']}")

    success = download_file(model_info['url'], model_path)

    if success and verify_model(model_path):
        logger.info(f"✅ Model {model_name} downloaded successfully")
        return True
    else:
        # Удаляем поврежденный файл
        if model_path.exists():
            model_path.unlink()
        logger.error(f"❌ Failed to download {model_name}")
        return False


def list_available_models():
    """Показать список доступных моделей"""
    print("\n📦 Available YOLO models:")
    print("-" * 60)

    for name, info in AVAILABLE_MODELS.items():
        print("12")
        print(f"   📏 Size: {info['size']}")
        print(f"   📝 {info['description']}")
        print()


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Download YOLO models for Camera Monitor")
    parser.add_argument("models", nargs="*", help="Model names to download (default: yolov8n)")
    parser.add_argument("-d", "--dir", help="Models directory (default: models/)")
    parser.add_argument("-f", "--force", action="store_true", help="Force re-download existing models")
    parser.add_argument("-l", "--list", action="store_true", help="List available models")
    parser.add_argument("-a", "--all", action="store_true", help="Download all available models")

    args = parser.parse_args()

    # Настраиваем логирование
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Показываем список моделей
    if args.list:
        list_available_models()
        return

    # Определяем модели для скачивания
    if args.all:
        models_to_download = list(AVAILABLE_MODELS.keys())
    elif args.models:
        models_to_download = args.models
    else:
        models_to_download = ["yolov8n"]  # По умолчанию

    # Определяем директорию
    models_dir = Path(args.dir) if args.dir else script_dir / "models"

    logger.info(f"Models directory: {models_dir}")
    logger.info(f"Models to download: {', '.join(models_to_download)}")

    # Скачиваем модели
    success_count = 0
    for model_name in models_to_download:
        if download_model(model_name, models_dir, args.force):
            success_count += 1

    # Итог
    total = len(models_to_download)
    if success_count == total:
        logger.info(f"✅ All {total} models downloaded successfully")
    else:
        logger.error(f"❌ Downloaded {success_count}/{total} models")
        sys.exit(1)


if __name__ == "__main__":
    main()