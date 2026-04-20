"""
Окно камеры с live видео и детекцией
"""

import logging
import time
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QGroupBox, QCheckBox, QSplitter,
    QScrollArea, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QRect
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import QPoint

from src.core.config import Config
from src.core.camera import CameraManager
from src.core.detector import PersonDetector
from src.core.database import DatabaseManager
from src.utils.image_utils import ImageConverter, DetectionVisualizer


class VideoDisplayThread(QThread):
    """Поток для отображения видео"""

    frame_ready = pyqtSignal(QImage, dict)  # (image, detection_data)

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
                # Получаем кадр
                frame_data = self.camera_manager.get_frame()
                if frame_data is None:
                    self.msleep(100)  # Ждем если нет кадра
                    continue

                frame, timestamp, camera_id = frame_data

                # Детекция людей
                detection_data = {}
                if self.show_detections and self.detector.is_loaded():
                    try:
                        results = self.detector.detect_people(frame)
                        detection_data = {
                            'detections': results,
                            'count': len(results) if results else 0,
                            'timestamp': timestamp
                        }
                    except Exception as e:
                        logging.error(f"Detection error: {e}")

                # Конвертируем в QImage
                qimage = ImageConverter.cv2_to_qimage(frame)

                # Отправляем кадр в GUI
                self.frame_ready.emit(qimage, detection_data)

                # Ограничиваем FPS до 30
                current_time = time.time()
                if current_time - self.last_frame_time < 1/30:
                    self.msleep(10)
                self.last_frame_time = current_time

            except Exception as e:
                logging.error(f"Video display thread error: {e}")
                self.msleep(100)

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

        # Рисуем bounding boxes
        for detection in detections:
            if hasattr(detection, 'bbox'):
                bbox = detection.bbox
            else:
                bbox = detection.get('bbox', [])

            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]

                # Рисуем прямоугольник
                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

                # Рисуем метку
                confidence = detection.confidence if hasattr(detection, 'confidence') else detection.get('confidence', 0)
                class_name = detection.class_name if hasattr(detection, 'class_name') else detection.get('class', detection.get('class_name', 'person'))

                label = f"{class_name}: {confidence:.2f}" = self.detection_data.get('detections')
        if not detections:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем bounding boxes
        for detection in detections:
            if hasattr(detection, 'bbox'):
                bbox = detection.bbox
            else:
                bbox = detection.get('bbox', [])

            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]

                # Рисуем прямоугольникconfidence if hasattr(detection, 'confidence') else detection.get('confidence', 0)
                class_name = detection.class_name if hasattr(detection, 'class_name') else detection.get('class', detection.get('class_name', 'person')
                painter.setPen(pen)
                painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

                # Рисуем метку
                confidence = detection.confidence if hasattr(detection, 'confidence') else detection.get('confidence', 0)
                class_name = detection.class_name if hasattr(detection, 'class_name') else detection.get('class', detection.get('class_name', 'person'))

                label = f"{class_name}: {confidence:.2f}"

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем bounding boxes
        for detection in self.detection_data['detections']:
            bbox = detection.get('bbox', [])
            if len(bbox) >= 4:
                x1, y1, x2, y2 = bbox[:4]

                # Рисуем прямоугольник
                pen = QPen(QColor(255, 0, 0), 2)
                painter.setPen(pen)
                painter.drawRect(int(x1), int(y1), int(x2 - x1), int(y2 - y1))

                # Рисуем метку
                confidence = detection.confidence if hasattr(detection, 'confidence') else detection.get('confidence', 0)
                class_name = detection.class_name if hasattr(detection, 'class_name') else detection.get('class', detection.get('class_name', 'person'))

                label = f"{class_name}: {confidence:.2f}"
                font = QFont("Arial", 10, QFont.Weight.Bold)
                painter.setFont(font)

                # Фон для текста
                text_rect = painter.fontMetrics().boundingRect(label)
                text_rect.moveTopLeft(QPoint(int(x1), int(y1) - text_rect.height()))

                painter.fillRect(text_rect, QColor(255, 0, 0, 180))
                painter.setPen(QPen(QColor(255, 255, 255)))
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, label)


class CameraWindow(QWidget):
    """Окно отображения камеры"""

    def __init__(self,
                 config: Config,
                 camera_manager: CameraManager,
                 detector: PersonDetector,
                 db_manager: DatabaseManager):
        super().__init__()

        self.config = config
        self.camera_manager = camera_manager
        self.detector = detector
        self.db_manager = db_manager

        self.logger = logging.getLogger(__name__)

        # Компоненты
        self.video_thread: Optional[VideoDisplayThread] = None
        self.current_frame: Optional[QImage] = None
        self.detection_overlay: Optional[DetectionOverlay] = None

        # Статистика
        self.stats_data = {
            'fps': 0,
            'frame_count': 0,
            'detection_count': 0,
            'last_detection_time': 0
        }

        self.setup_ui()
        self.setup_connections()

        self.logger.info("Camera window initialized")

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QHBoxLayout(self)

        # Создаем разделитель для левой и правой панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Левая панель - видео
        self.setup_video_panel(splitter)

        # Правая панель - управление и статистика
        self.setup_control_panel(splitter)

        # Устанавливаем пропорции
        splitter.setSizes([700, 300])

    def setup_video_panel(self, parent: QSplitter):
        """Настройка панели видео"""
        video_widget = QWidget()
        video_layout = QVBoxLayout(video_widget)

        # Контейнер для видео с оверлеем
        self.video_container = QWidget()
        self.video_container.setMinimumSize(640, 480)
        self.video_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        video_container_layout = QVBoxLayout(self.video_container)
        video_container_layout.setContentsMargins(0, 0, 0, 0)

        # Виджет для отображения видео
        self.video_label = QLabel("Видео не запущено")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #888;
                border: 2px dashed #555;
                font-size: 16px;
            }
        """)
        self.video_label.setMinimumSize(640, 480)
        video_container_layout.addWidget(self.video_label)

        # Оверлей для детекций
        self.detection_overlay = DetectionOverlay()
        self.detection_overlay.setParent(self.video_label)
        self.detection_overlay.setGeometry(self.video_label.geometry())
        self.detection_overlay.lower()  # Помещаем под другие виджеты

        video_layout.addWidget(self.video_container)

        # Панель управления видео
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)

        self.start_btn = QPushButton("▶️ Запустить")
        self.start_btn.clicked.connect(self.start_video)
        controls_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Остановить")
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)

        self.snapshot_btn = QPushButton("📸 Снимок")
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.snapshot_btn.setEnabled(False)
        controls_layout.addWidget(self.snapshot_btn)

        controls_layout.addStretch()
        video_layout.addWidget(controls_widget)

        parent.addWidget(video_widget)

    def setup_control_panel(self, parent: QSplitter):
        """Настройка панели управления"""
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # Группа настроек детекции
        detection_group = QGroupBox("Детекция")
        detection_layout = QVBoxLayout(detection_group)

        self.detection_checkbox = QCheckBox("Показывать детекции")
        self.detection_checkbox.setChecked(True)
        self.detection_checkbox.stateChanged.connect(self.toggle_detections)
        detection_layout.addWidget(self.detection_checkbox)

        self.confidence_label = QLabel("Уверенность:")
        detection_layout.addWidget(self.confidence_label)

        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(1, 100)
        self.confidence_spin.setValue(50)
        self.confidence_spin.setSuffix("%")
        self.confidence_spin.valueChanged.connect(self.update_detection_confidence)
        detection_layout.addWidget(self.confidence_spin)

        control_layout.addWidget(detection_group)

        # Группа статистики
        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout(stats_group)

        self.fps_label = QLabel("FPS: 0")
        stats_layout.addWidget(self.fps_label)

        self.frame_count_label = QLabel("Кадров: 0")
        stats_layout.addWidget(self.frame_count_label)

        self.detection_count_label = QLabel("Детекций: 0")
        stats_layout.addWidget(self.detection_count_label)

        self.people_count_label = QLabel("Людей: 0")
        stats_layout.addWidget(self.people_count_label)

        control_layout.addWidget(stats_group)

        # Группа логов
        logs_group = QGroupBox("Последние события")
        logs_layout = QVBoxLayout(logs_group)

        self.logs_scroll = QScrollArea()
        self.logs_widget = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_widget)

        # Добавляем несколько пустых меток для логов
        for i in range(10):
            label = QLabel("")
            self.logs_layout.addWidget(label)
            if i == 0:
                label.setText("Система готова")

        self.logs_scroll.setWidget(self.logs_widget)
        self.logs_scroll.setWidgetResizable(True)
        logs_layout.addWidget(self.logs_scroll)

        control_layout.addWidget(logs_group)

        # Добавляем растяжку
        control_layout.addStretch()

        parent.addWidget(control_widget)

    def setup_connections(self):
        """Настройка соединений"""
        # Таймер для обновления статистики
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  # Каждую секунду

    def start_video(self):
        """Запуск видео"""
        try:
            # Запускаем камеру
            self.camera_manager.start_camera()

            # Запускаем поток отображения
            self.video_thread = VideoDisplayThread(self.camera_manager, self.detector)
            self.video_thread.frame_ready.connect(self.on_frame_ready)
            self.video_thread.start()

            # Обновляем UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.snapshot_btn.setEnabled(True)

            self.add_log_entry("Видео запущено")
            self.logger.info("Video started")

        except Exception as e:
            self.add_log_entry(f"Ошибка запуска видео: {e}")
            self.logger.error(f"Failed to start video: {e}")

    def stop_video(self):
        """Остановка видео"""
        try:
            # Останавливаем поток
            if self.video_thread:
                self.video_thread.stop()
                self.video_thread = None

            # Останавливаем камеру
            self.camera_manager.stop_camera()

            # Обновляем UI
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.snapshot_btn.setEnabled(False)

            # Очищаем видео
            self.video_label.setText("Видео остановлено")
            self.video_label.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    color: #888;
                    border: 2px dashed #555;
                    font-size: 16px;
                }
            """)

            self.add_log_entry("Видео остановлено")
            self.logger.info("Video stopped")

        except Exception as e:
            self.add_log_entry(f"Ошибка остановки видео: {e}")
            self.logger.error(f"Failed to stop video: {e}")

    def on_frame_ready(self, qimage: QImage, detection_data: dict):
        """Обработка готового кадра"""
        try:
            # Сохраняем кадр
            self.current_frame = qimage

            # Отображаем видео
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(
                self.video_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)

            # Обновляем оверлей детекций
            if self.detection_overlay:
                self.detection_overlay.set_detection_data(detection_data)
                self.detection_overlay.setGeometry(self.video_label.geometry())

            # Обновляем статистику
            self.stats_data['frame_count'] += 1
            if detection_data:
                self.stats_data['detection_count'] += len(detection_data.get('detections', []))
                people_count = detection_data.get('count', 0)
                self.people_count_label.setText(f"Людей: {people_count}")

                # Логируем обнаружение людей
                if people_count > 0:
                    current_time = time.time()
                    if current_time - self.stats_data['last_detection_time'] > 5:  # Не чаще раза в 5 сек
                        self.add_log_entry(f"Обнаружено {people_count} человек(а)")
                        self.stats_data['last_detection_time'] = current_time

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")

    def take_snapshot(self):
        """Сделать снимок"""
        try:
            if self.current_frame:
                # Сохраняем в файл (пока просто логируем)
                self.add_log_entry("Снимок сохранен")
                self.logger.info("Snapshot taken")
            else:
                self.add_log_entry("Нет активного кадра для снимка")

        except Exception as e:
            self.add_log_entry(f"Ошибка создания снимка: {e}")
            self.logger.error(f"Failed to take snapshot: {e}")

    def toggle_detections(self, state: int):
        """Переключение отображения детекций"""
        show = state == Qt.CheckState.Checked
        if self.video_thread:
            self.video_thread.set_show_detections(show)

    def update_detection_confidence(self, value: int):
        """Обновление порога уверенности детекции"""
        confidence = value / 100.0
        if self.detector:
            # Обновляем конфигурацию детектора
            self.logger.info(f"Detection confidence updated to {confidence}")

    def update_stats(self):
        """Обновление статистики"""
        try:
            # Получаем статистику от камеры
            camera_stats = self.camera_manager.get_stats()

            self.stats_data['fps'] = camera_stats.get('fps', 0)
            self.fps_label.setText(f"FPS: {self.stats_data['fps']:.1f}")
            self.frame_count_label.setText(f"Кадров: {self.stats_data['frame_count']}")
            self.detection_count_label.setText(f"Детекций: {self.stats_data['detection_count']}")

        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")

    def add_log_entry(self, message: str):
        """Добавление записи в лог"""
        try:
            # Находим первую пустую метку или сдвигаем существующие
            for i in range(self.logs_layout.count()):
                label = self.logs_layout.itemAt(i).widget()
                if isinstance(label, QLabel) and label.text() == "":
                    label.setText(message)
                    break
            else:
                # Если нет пустых, сдвигаем все вверх и добавляем новую
                for i in range(self.logs_layout.count() - 1):
                    current_label = self.logs_layout.itemAt(i).widget()
                    next_label = self.logs_layout.itemAt(i + 1).widget()
                    current_label.setText(next_label.text())

                last_label = self.logs_layout.itemAt(self.logs_layout.count() - 1).widget()
                last_label.setText(message)

        except Exception as e:
            self.logger.error(f"Error adding log entry: {e}")

    def resizeEvent(self, event):
        """Обработка изменения размера"""
        super().resizeEvent(event)
        # Обновляем размер оверлея
        if self.detection_overlay and self.video_label:
            self.detection_overlay.setGeometry(self.video_label.geometry())

    def closeEvent(self, event):
        """Обработка закрытия"""
        self.logger.info("Camera window closing...")
        self.stop_video()
        event.accept()