"""
Окно камеры с live видео и детекцией
"""

import logging
import time
import cv2
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QGroupBox, QCheckBox, QSplitter,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import QPoint

from src.core.config import Config
from src.core.camera import CameraManager
from src.core.detector import PersonDetector
from src.core.database import DatabaseManager
from src.utils.image_utils import ImageConverter, DetectionVisualizer


class VideoDisplayThread(QThread):
    """Поток для отображения видео"""

    frame_ready = pyqtSignal(QImage, dict)

    def __init__(self, camera_manager: CameraManager, detector: PersonDetector):
        super().__init__()
        self.camera_manager = camera_manager
        self.detector = detector
        self.running = True
        self.show_detections = True
        self.last_frame_time = 0

    def run(self):
        """Основной цикл обработки видео"""
        while self.running:
            try:
                frame = self.camera_manager.get_frame()
                if frame is None:
                    self.msleep(100)
                    continue

                detection_data = {}
                if self.show_detections and self.detector.is_loaded:
                    try:
                        detections, stats = self.detector.detect_people(frame)
                        frame = self._draw_detections(frame, detections)
                        detection_data = {
                            'detections': detections,
                            'count': stats.person_count,
                            'stats': stats,
                            'timestamp': time.time()
                        }
                    except Exception as e:
                        logging.error(f"Detection error: {e}")

                qimage = ImageConverter.cv2_to_qimage(frame)
                self.frame_ready.emit(qimage, detection_data)

                current_time = time.time()
                if current_time - self.last_frame_time < 1/30:
                    self.msleep(10)
                self.last_frame_time = current_time

            except Exception as e:
                logging.error(f"Video display thread error: {e}")
                self.msleep(100)

    def _draw_detections(self, frame, detections):
        """Нарисовать детекции прямо на кадре, чтобы они точно были видны в UI."""
        result = frame.copy()

        for detection in detections:
            x1, y1, x2, y2 = map(int, detection.bbox)
            label = f"{detection.class_name}: {detection.confidence:.2f}"

            cv2.rectangle(result, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                result,
                label,
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return result

    def stop(self):
        """Остановка потока"""
        self.running = False
        self.wait()

    def set_show_detections(self, show: bool):
        """Включить/выключить отображение детекций"""
        self.show_detections = show


class DetectionOverlay(QLabel):
    """Виджет для наложения детекций на видео"""

    def __init__(self):
        super().__init__()
        self.detection_data = {}
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_detection_data(self, data: dict):
        """Установить данные детекций"""
        self.detection_data = data
        self.update()

    def paintEvent(self, event):
        """Отрисовка детекций"""
        super().paintEvent(event)
        detections = self.detection_data.get('detections')
        if not detections:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for detection in detections:
            if hasattr(detection, 'bbox'):
                bbox = detection.bbox
            else:
                bbox = detection.get('bbox', [])

            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]

                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

                confidence = detection.confidence if hasattr(detection, 'confidence') else detection.get('confidence', 0)
                class_name = detection.class_name if hasattr(detection, 'class_name') else detection.get('class', 'person')

                label = f"{class_name}: {confidence:.2f}"
                font = QFont()
                font.setPointSize(8)
                painter.setFont(font)
                painter.drawText(int(x1), int(y1) - 5, label)


class CameraWindow(QWidget):
    """Главное окно камеры с видео"""

    def __init__(self, config: Config, camera_manager: CameraManager,
                 detector: PersonDetector, db_manager: DatabaseManager):
        super().__init__()
        self.config = config
        self.camera_manager = camera_manager
        self.detector = detector
        self.db_manager = db_manager

        self.init_ui()
        self.start_video_thread()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout()

        # Видео область
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setScaledContents(True)

        # Наложение детекций
        self.overlay = DetectionOverlay()
        self.overlay.setGeometry(self.video_label.geometry())

        # Контролы
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Запустить")
        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_camera)
        self.show_detections_cb = QCheckBox("Показать детекции")
        self.show_detections_cb.setChecked(True)
        self.show_detections_cb.stateChanged.connect(self.toggle_detections)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.show_detections_cb)
        control_layout.addStretch()

        layout.addWidget(self.video_label)
        layout.addLayout(control_layout)

        self.setLayout(layout)

    def start_video_thread(self):
        """Запустить поток видео"""
        self.video_thread = VideoDisplayThread(self.camera_manager, self.detector)
        self.video_thread.frame_ready.connect(self.on_frame_ready)
        self.video_thread.start()

    def on_frame_ready(self, qimage: QImage, detection_data: dict):
        """Обработка готового кадра"""
        pixmap = QPixmap.fromImage(qimage)
        self.video_label.setPixmap(pixmap)
        self.overlay.set_detection_data(detection_data)

    def start_camera(self):
        """Запуск камеры"""
        try:
            self.camera_manager.start()
        except Exception as e:
            logging.error(f"Error starting camera: {e}")

    def stop_camera(self):
        """Остановка камеры"""
        try:
            self.camera_manager.stop()
        except Exception as e:
            logging.error(f"Error stopping camera: {e}")

    def toggle_detections(self):
        """Включить/выключить детекции"""
        show = self.show_detections_cb.isChecked()
        self.video_thread.set_show_detections(show)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.video_thread.stop()
        self.camera_manager.stop()
        event.accept()
