"""
Утилиты для работы с изображениями
Конвертация между OpenCV, PyQt6 и другими форматами
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
from PIL import Image, ImageQt
import logging

try:
    from PyQt6.QtGui import QImage, QPixmap, QColor, QPainter, QPen, QBrush
    from PyQt6.QtCore import Qt
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    QImage = None
    QPixmap = None

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ImageConverter:
    """
    Конвертер изображений между различными форматами

    Поддерживает конвертацию:
    - OpenCV BGR ↔ RGB
    - OpenCV ndarray ↔ PyQt6 QImage/QPixmap
    - Масштабирование и обрезка
    """

    @staticmethod
    def cv2_to_qimage(cv_img: np.ndarray) -> Optional['QImage']:
        """
        Конвертировать OpenCV изображение в PyQt6 QImage

        Args:
            cv_img: OpenCV изображение (BGR формат)

        Returns:
            QImage или None если Qt недоступен
        """
        if not QT_AVAILABLE:
            logger.warning("PyQt6 not available, cannot convert to QImage")
            return None

        try:
            # Конвертируем BGR → RGB
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

            # Создаем QImage
            height, width, channel = rgb_image.shape
            bytes_per_line = 3 * width
            qimage = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)

            return qimage

        except Exception as e:
            logger.error(f"Error converting CV2 to QImage: {e}")
            return None

    @staticmethod
    def cv2_to_qpixmap(cv_img: np.ndarray, max_size: Optional[Tuple[int, int]] = None) -> Optional['QPixmap']:
        """
        Конвертировать OpenCV изображение в PyQt6 QPixmap

        Args:
            cv_img: OpenCV изображение (BGR формат)
            max_size: Максимальный размер (width, height) для масштабирования

        Returns:
            QPixmap или None если Qt недоступен
        """
        if not QT_AVAILABLE:
            logger.warning("PyQt6 not available, cannot convert to QPixmap")
            return None

        try:
            qimage = ImageConverter.cv2_to_qimage(cv_img)
            if qimage is None:
                return None

            # Масштабируем если нужно
            if max_size:
                qimage = qimage.scaled(max_size[0], max_size[1],
                                     Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)

            return QPixmap.fromImage(qimage)

        except Exception as e:
            logger.error(f"Error converting CV2 to QPixmap: {e}")
            return None

    @staticmethod
    def qimage_to_cv2(qimage: 'QImage') -> Optional[np.ndarray]:
        """
        Конвертировать PyQt6 QImage в OpenCV изображение

        Args:
            qimage: QImage изображение

        Returns:
            OpenCV изображение (BGR формат) или None
        """
        if not QT_AVAILABLE:
            logger.warning("PyQt6 not available")
            return None

        try:
            # Конвертируем QImage в numpy array
            qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
            width = qimage.width()
            height = qimage.height()

            ptr = qimage.constBits()
            arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 3))

            # RGB → BGR
            bgr_image = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

            return bgr_image

        except Exception as e:
            logger.error(f"Error converting QImage to CV2: {e}")
            return None

    @staticmethod
    def resize_cv2_image(cv_img: np.ndarray, target_size: Tuple[int, int],
                        keep_aspect: bool = True) -> np.ndarray:
        """
        Изменить размер OpenCV изображения

        Args:
            cv_img: Исходное изображение
            target_size: Целевой размер (width, height)
            keep_aspect: Сохранять соотношение сторон

        Returns:
            Измененное изображение
        """
        try:
            if keep_aspect:
                # Вычисляем соотношение сторон
                h, w = cv_img.shape[:2]
                target_w, target_h = target_size

                ratio = min(target_w / w, target_h / h)
                new_w = int(w * ratio)
                new_h = int(h * ratio)

                # Масштабируем
                resized = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                # Создаем канву целевого размера и центрируем
                canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
                x_offset = (target_w - new_w) // 2
                y_offset = (target_h - new_h) // 2

                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                return canvas
            else:
                return cv2.resize(cv_img, target_size, interpolation=cv2.INTER_LINEAR)

        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return cv_img

    @staticmethod
    def draw_detections(cv_img: np.ndarray, detections: List[dict],
                       color: Tuple[int, int, int] = (0, 255, 0),
                       thickness: int = 2) -> np.ndarray:
        """
        Нарисовать bounding boxes детекции на изображении

        Args:
            cv_img: Исходное изображение
            detections: Список детекций [{'bbox': (x1,y1,x2,y2), 'confidence': float, 'class': str}]
            color: Цвет рамки (BGR)
            thickness: Толщина линии

        Returns:
            Изображение с нарисованными рамками
        """
        try:
            result = cv_img.copy()

            for detection in detections:
                bbox = detection.get('bbox')
                confidence = detection.get('confidence', 0.0)
                class_name = detection.get('class', 'unknown')

                if bbox:
                    x1, y1, x2, y2 = map(int, bbox)

                    # Рисуем рамку
                    cv2.rectangle(result, (x1, y1), (x2, y2), color, thickness)

                    # Добавляем текст с классом и уверенностью
                    label = f"{class_name}: {confidence:.2f}"
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                    # Фон для текста
                    cv2.rectangle(result, (x1, y1 - text_height - baseline),
                                (x1 + text_width, y1), color, -1)

                    # Текст
                    cv2.putText(result, label, (x1, y1 - baseline),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            return result

        except Exception as e:
            logger.error(f"Error drawing detections: {e}")
            return cv_img

    @staticmethod
    def crop_image(cv_img: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Вырезать область изображения по bounding box

        Args:
            cv_img: Исходное изображение
            bbox: Координаты (x1, y1, x2, y2)

        Returns:
            Вырезанная область или None если ошибка
        """
        try:
            x1, y1, x2, y2 = bbox
            height, width = cv_img.shape[:2]

            # Проверяем границы
            x1 = max(0, min(x1, width))
            y1 = max(0, min(y1, height))
            x2 = max(0, min(x2, width))
            y2 = max(0, min(y2, height))

            if x2 <= x1 or y2 <= y1:
                return None

            return cv_img[y1:y2, x1:x2].copy()

        except Exception as e:
            logger.error(f"Error cropping image: {e}")
            return None

    @staticmethod
    def pil_to_cv2(pil_image: Image.Image) -> np.ndarray:
        """
        Конвертировать PIL Image в OpenCV изображение

        Args:
            pil_image: PIL Image

        Returns:
            OpenCV изображение (RGB формат)
        """
        try:
            # Конвертируем в numpy array
            cv_image = np.array(pil_image)

            # PIL использует RGB, OpenCV тоже RGB для этого случая
            return cv_image

        except Exception as e:
            logger.error(f"Error converting PIL to CV2: {e}")
            return np.array(pil_image)

    @staticmethod
    def cv2_to_pil(cv_img: np.ndarray) -> Image.Image:
        """
        Конвертировать OpenCV изображение в PIL Image

        Args:
            cv_img: OpenCV изображение (BGR формат)

        Returns:
            PIL Image (RGB формат)
        """
        try:
            # BGR → RGB
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            return Image.fromarray(rgb_image)

        except Exception as e:
            logger.error(f"Error converting CV2 to PIL: {e}")
            return Image.fromarray(cv_img)


class DetectionVisualizer:
    """
    Визуализатор результатов детекции

    Предоставляет высокоуровневые методы для отображения детекции
    """

    # Цвета для разных классов (BGR формат)
    COLORS = {
        'person': (0, 255, 0),      # Зеленый
        'car': (255, 0, 0),         # Синий
        'truck': (0, 0, 255),       # Красный
        'bus': (255, 255, 0),       # Голубой
        'bicycle': (255, 0, 255),   # Магента
        'motorcycle': (0, 255, 255), # Желтый
    }

    @classmethod
    def draw_yolo_results(cls, cv_img: np.ndarray, results,
                         conf_threshold: float = 0.5) -> np.ndarray:
        """
        Нарисовать результаты YOLO детекции

        Args:
            cv_img: Исходное изображение
            results: Результаты YOLO (ultralytics Results object)
            conf_threshold: Порог уверенности

        Returns:
            Изображение с нарисованными результатами
        """
        try:
            result_img = cv_img.copy()

            if results and len(results) > 0:
                # Получаем detections
                boxes = results[0].boxes
                if boxes is not None:
                    for box in boxes:
                        # Координаты
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        conf = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())

                        if conf < conf_threshold:
                            continue

                        # Получаем имя класса
                        class_names = results[0].names
                        class_name = class_names.get(class_id, f'class_{class_id}')

                        # Цвет для класса
                        color = cls.COLORS.get(class_name, (128, 128, 128))

                        # Рисуем
                        detection = {
                            'bbox': (x1, y1, x2, y2),
                            'confidence': conf,
                            'class': class_name
                        }

                        result_img = ImageConverter.draw_detections(
                            result_img, [detection], color=color)

            return result_img

        except Exception as e:
            logger.error(f"Error drawing YOLO results: {e}")
            return cv_img

    @classmethod
    def create_overlay_image(cls, detections: List[dict],
                           image_size: Tuple[int, int]) -> Optional[np.ndarray]:
        """
        Создать overlay изображение с детекциями

        Args:
            detections: Список детекций
            image_size: Размер изображения (width, height)

        Returns:
            Overlay изображение или None
        """
        try:
            width, height = image_size
            overlay = np.zeros((height, width, 3), dtype=np.uint8)

            for detection in detections:
                bbox = detection.get('bbox')
                class_name = detection.get('class', 'unknown')
                color = cls.COLORS.get(class_name, (128, 128, 128))

                if bbox:
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

            return overlay

        except Exception as e:
            logger.error(f"Error creating overlay: {e}")
            return None
