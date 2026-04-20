"""
Модуль детекции людей с использованием YOLO
Использует ultralytics YOLO для обнаружения людей на изображениях
"""

import os
import time
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import logging

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DetectionResult:
    """Результат детекции"""
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    confidence: float
    class_id: int
    class_name: str

    def to_dict(self) -> Dict:
        """Конвертировать в словарь"""
        return {
            'bbox': self.bbox,
            'confidence': self.confidence,
            'class_id': self.class_id,
            'class_name': self.class_name
        }


@dataclass
class DetectionStats:
    """Статистика детекции"""
    total_detections: int
    person_count: int
    avg_confidence: float
    processing_time: float
    model_name: str


class PersonDetector:
    """
    Детектор людей на основе YOLO

    Использует ultralytics YOLO для обнаружения людей
    Поддерживает различные модели YOLOv8/v11
    """

    # COCO классы
    COCO_CLASSES = {
        0: 'person',
        1: 'bicycle',
        2: 'car',
        3: 'motorcycle',
        4: 'airplane',
        5: 'bus',
        6: 'train',
        7: 'truck',
        8: 'boat',
        9: 'traffic light',
        10: 'fire hydrant',
        11: 'stop sign',
        12: 'parking meter',
        13: 'bench',
        14: 'bird',
        15: 'cat',
        16: 'dog',
        17: 'horse',
        18: 'sheep',
        19: 'cow',
        20: 'elephant',
        21: 'bear',
        22: 'zebra',
        23: 'giraffe',
        24: 'backpack',
        25: 'umbrella',
        26: 'handbag',
        27: 'tie',
        28: 'suitcase',
        29: 'frisbee',
        30: 'skis',
        31: 'snowboard',
        32: 'sports ball',
        33: 'kite',
        34: 'baseball bat',
        35: 'baseball glove',
        36: 'skateboard',
        37: 'surfboard',
        38: 'tennis racket',
        39: 'bottle',
        40: 'wine glass',
        41: 'cup',
        42: 'fork',
        43: 'knife',
        44: 'spoon',
        45: 'bowl',
        46: 'banana',
        47: 'apple',
        48: 'sandwich',
        49: 'orange',
        50: 'broccoli',
        51: 'carrot',
        52: 'hot dog',
        53: 'pizza',
        54: 'donut',
        55: 'cake',
        56: 'chair',
        57: 'couch',
        58: 'potted plant',
        59: 'bed',
        60: 'dining table',
        61: 'toilet',
        62: 'tv',
        63: 'laptop',
        64: 'mouse',
        65: 'remote',
        66: 'keyboard',
        67: 'cell phone',
        68: 'microwave',
        69: 'oven',
        70: 'toaster',
        71: 'sink',
        72: 'refrigerator',
        73: 'book',
        74: 'clock',
        75: 'vase',
        76: 'scissors',
        77: 'teddy bear',
        78: 'hair drier',
        79: 'toothbrush'
    }

    def __init__(self, model_path: str = "models/yolov8n.pt",
                 conf_threshold: float = 0.5, device: str = "cpu"):
        """
        Инициализация детектора

        Args:
            model_path: Путь к YOLO модели
            conf_threshold: Порог уверенности (0.0-1.0)
            device: Устройство ('cpu', 'cuda', '0', '1', etc.)
        """
        if not YOLO_AVAILABLE:
            raise ImportError("ultralytics not available. Install with: pip install ultralytics")

        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.device = device
        self.model = None
        self.is_loaded = False

        # Статистика
        self.total_processed = 0
        self.total_detections = 0
        self.avg_processing_time = 0.0

        logger.info(f"PersonDetector initialized: model={model_path}, conf={conf_threshold}, device={device}")

    def load_model(self) -> bool:
        """
        Загрузить YOLO модель

        Returns:
            True если модель загружена успешно
        """
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model file not found: {self.model_path}")
                return False

            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)

            # Настраиваем параметры
            self.model.conf = self.conf_threshold

            # Проверяем загрузку
            if hasattr(self.model, 'names'):
                logger.info(f"Model loaded successfully. Classes: {len(self.model.names)}")
                self.is_loaded = True
                return True
            else:
                logger.error("Model loaded but no class names found")
                return False

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            return False

    def detect_people(self, image: np.ndarray,
                     classes: Optional[List[int]] = None) -> Tuple[List[DetectionResult], DetectionStats]:
        """
        Обнаружить людей на изображении

        Args:
            image: Изображение в формате OpenCV (BGR)
            classes: Список классов для детекции (по умолчанию только 'person')

        Returns:
            Кортеж (список детекций, статистика)
        """
        if not self.is_loaded or self.model is None:
            logger.warning("Model not loaded")
            return [], DetectionStats(0, 0, 0.0, 0.0, "not_loaded")

        # По умолчанию детектируем только людей
        if classes is None:
            classes = [0]  # person class

        start_time = time.time()

        try:
            # Запускаем детекцию
            results = self.model(image, device=self.device, classes=classes, verbose=False)

            processing_time = time.time() - start_time
            self.total_processed += 1

            # Обрабатываем результаты
            detections = []
            person_count = 0

            if results and len(results) > 0:
                result = results[0]

                if result.boxes is not None:
                    for box in result.boxes:
                        # Координаты
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                        # Уверенность
                        conf = float(box.conf[0].cpu().numpy())

                        # Класс
                        cls_id = int(box.cls[0].cpu().numpy())
                        cls_name = self.COCO_CLASSES.get(cls_id, f'class_{cls_id}')

                        # Создаем результат детекции
                        detection = DetectionResult(
                            bbox=(x1, y1, x2, y2),
                            confidence=conf,
                            class_id=cls_id,
                            class_name=cls_name
                        )

                        detections.append(detection)

                        if cls_id == 0:  # person
                            person_count += 1

            # Вычисляем среднюю уверенность
            avg_confidence = 0.0
            if detections:
                avg_confidence = sum(d.confidence for d in detections) / len(detections)

            # Обновляем статистику
            self.total_detections += len(detections)
            self.avg_processing_time = (self.avg_processing_time * (self.total_processed - 1) +
                                      processing_time) / self.total_processed

            stats = DetectionStats(
                total_detections=len(detections),
                person_count=person_count,
                avg_confidence=avg_confidence,
                processing_time=processing_time,
                model_name=os.path.basename(self.model_path)
            )

            logger.debug(f"Detection completed: {person_count} people, {processing_time:.3f}s")
            return detections, stats

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Detection error: {e}")

            stats = DetectionStats(
                total_detections=0,
                person_count=0,
                avg_confidence=0.0,
                processing_time=processing_time,
                model_name=os.path.basename(self.model_path)
            )

            return [], stats

    def detect_all_objects(self, image: np.ndarray) -> Tuple[List[DetectionResult], DetectionStats]:
        """
        Обнаружить все объекты на изображении

        Args:
            image: Изображение в формате OpenCV (BGR)

        Returns:
            Кортеж (список всех детекций, статистика)
        """
        return self.detect_people(image, classes=None)

    def get_supported_classes(self) -> Dict[int, str]:
        """
        Получить список поддерживаемых классов

        Returns:
            Словарь {class_id: class_name}
        """
        if self.is_loaded and self.model and hasattr(self.model, 'names'):
            return self.model.names
        return self.COCO_CLASSES

    def get_model_info(self) -> Dict[str, Any]:
        """
        Получить информацию о модели

        Returns:
            Словарь с информацией о модели
        """
        return {
            'model_path': self.model_path,
            'is_loaded': self.is_loaded,
            'conf_threshold': self.conf_threshold,
            'device': self.device,
            'supported_classes': len(self.get_supported_classes()),
            'total_processed': self.total_processed,
            'total_detections': self.total_detections,
            'avg_processing_time': self.avg_processing_time
        }

    def unload_model(self):
        """Выгрузить модель из памяти"""
        if self.model:
            del self.model
            self.model = None
            self.is_loaded = False
            logger.info("Model unloaded")


class MockPersonDetector(PersonDetector):
    """
    Mock детектор для тестирования

    Генерирует случайные детекции без реальной модели
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_detections = [
            {'bbox': (100, 100, 200, 300), 'confidence': 0.85, 'class_id': 0, 'class_name': 'person'},
            {'bbox': (300, 150, 400, 350), 'confidence': 0.72, 'class_id': 0, 'class_name': 'person'},
        ]

    def load_model(self) -> bool:
        """Мок загрузка - всегда успешна"""
        self.is_loaded = True
        logger.info("Mock detector loaded")
        return True

    def detect_people(self, image: np.ndarray,
                     classes: Optional[List[int]] = None) -> Tuple[List[DetectionResult], DetectionStats]:
        """Генерирует мок детекции"""
        import random
        import time

        # Имитируем время обработки
        time.sleep(0.1)

        # Случайно возвращаем детекции или пустой результат
        if random.random() > 0.3:  # 70% шанс детекции
            detections = [
                DetectionResult(**det) for det in self.mock_detections
            ]
            person_count = len(detections)
        else:
            detections = []
            person_count = 0

        stats = DetectionStats(
            total_detections=len(detections),
            person_count=person_count,
            avg_confidence=0.8 if detections else 0.0,
            processing_time=0.1,
            model_name="mock_detector"
        )

        return detections, stats