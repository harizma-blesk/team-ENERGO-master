"""
Модуль захвата видео для Camera Monitor
Использует OpenCV для захвата RTSP потоков и локальных камер
"""

import cv2
import threading
import time
import queue
from typing import Optional, Tuple, Callable
from dataclasses import dataclass
import logging

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CameraConfig:
    """Конфигурация камеры"""
    rtsp_url: Optional[str] = None
    camera_index: int = 0
    fps_target: int = 30
    frame_width: int = 640
    frame_height: int = 480
    reconnect_delay: float = 2.0  # секунды
    max_reconnect_attempts: int = 5


class CameraManager:
    """
    Менеджер захвата видео

    Поддерживает RTSP потоки и локальные камеры
    Работает в отдельном потоке для неблокирующего захвата
    """

    def __init__(self, config: CameraConfig):
        """
        Инициализация менеджера камеры

        Args:
            config: Конфигурация камеры
        """
        self.config = config
        self.capture: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_connected = False
        self.current_fps = 0.0

        # Очередь для хранения кадров
        self.frame_queue = queue.Queue(maxsize=10)  # Буфер на 10 кадров

        # Поток захвата
        self.capture_thread: Optional[threading.Thread] = None

        # Статистика
        self.frames_captured = 0
        self.frames_dropped = 0
        self.last_frame_time = time.time()

        # Callbacks
        self.on_frame_callback: Optional[Callable[[cv2.Mat], None]] = None
        self.on_status_change_callback: Optional[Callable[[bool], None]] = None

        logger.info(f"CameraManager initialized: RTSP={config.rtsp_url}, index={config.camera_index}")

    def start(self) -> bool:
        """
        Запустить захват видео

        Returns:
            True если успешно запущен
        """
        if self.is_running:
            logger.warning("Camera already running")
            return True

        logger.info("Starting camera capture...")
        self.is_running = True

        # Создаем и запускаем поток захвата
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()

        # Ждем подключения
        timeout = 10.0
        start_time = time.time()
        while not self.is_connected and (time.time() - start_time) < timeout:
            time.sleep(0.1)

        if self.is_connected:
            logger.info("Camera started successfully")
            return True
        else:
            logger.error("Failed to start camera within timeout")
            self.stop()
            return False

    def stop(self):
        """Остановить захват видео"""
        if not self.is_running:
            return

        logger.info("Stopping camera capture...")
        self.is_running = False

        # Ждем завершения потока
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2.0)

        # Закрываем захват
        self._close_capture()

        # Очищаем очередь
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                break

        logger.info("Camera stopped")

    def get_frame(self, timeout: float = 1.0) -> Optional[cv2.Mat]:
        """
        Получить следующий кадр из очереди

        Args:
            timeout: Максимальное время ожидания в секундах

        Returns:
            Кадр или None если очередь пуста
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def set_frame_callback(self, callback: Callable[[cv2.Mat], None]):
        """
        Установить callback для обработки кадров

        Args:
            callback: Функция, принимающая cv2.Mat кадр
        """
        self.on_frame_callback = callback

    def set_status_callback(self, callback: Callable[[bool], None]):
        """
        Установить callback для изменения статуса подключения

        Args:
            callback: Функция, принимающая bool статус подключения
        """
        self.on_status_change_callback = callback

    def get_stats(self) -> dict:
        """
        Получить статистику захвата

        Returns:
            Словарь со статистикой
        """
        return {
            "is_connected": self.is_connected,
            "current_fps": self.current_fps,
            "fps": self.current_fps,
            "frames_captured": self.frames_captured,
            "frames_dropped": self.frames_dropped,
            "queue_size": self.frame_queue.qsize()
        }

    def start_camera(self) -> bool:
        """Запустить работу камеры (алиас для start)"""
        return self.start()

    def stop_camera(self):
        """Остановить работу камеры (алиас для stop)"""
        self.stop()

    def stop_all_cameras(self):
        """Остановить все камеры"""
        self.stop()

    def is_camera_active(self) -> bool:
        """Проверить, активна ли камера"""
        return self.is_connected

    def _capture_loop(self):
        """Основной цикл захвата в отдельном потоке"""
        reconnect_attempts = 0

        while self.is_running:
            try:
                # Пытаемся подключиться если не подключены
                if not self.is_connected:
                    if not self._connect():
                        reconnect_attempts += 1
                        if reconnect_attempts >= self.config.max_reconnect_attempts:
                            logger.error(f"Max reconnect attempts ({self.config.max_reconnect_attempts}) reached")
                            break
                        time.sleep(self.config.reconnect_delay)
                        continue
                    else:
                        reconnect_attempts = 0
                        self._notify_status_change(True)

                # Захватываем кадр
                ret, frame = self.capture.read()
                if not ret or frame is None:
                    logger.warning("Failed to read frame")
                    self._handle_disconnect()
                    continue

                # Обрабатываем кадр
                self.frames_captured += 1
                self._update_fps()

                # Добавляем в очередь (с отбрасыванием старых кадров если очередь полна)
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    # Удаляем старый кадр и добавляем новый
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                        self.frames_dropped += 1
                    except queue.Empty:
                        pass

                # Вызываем callback если установлен
                if self.on_frame_callback:
                    try:
                        self.on_frame_callback(frame)
                    except Exception as e:
                        logger.error(f"Frame callback error: {e}")

                # Контролируем FPS
                target_delay = 1.0 / self.config.fps_target
                elapsed = time.time() - self.last_frame_time
                if elapsed < target_delay:
                    time.sleep(target_delay - elapsed)

            except Exception as e:
                logger.error(f"Capture loop error: {e}")
                self._handle_disconnect()
                time.sleep(1.0)

    def _connect(self) -> bool:
        """
        Подключиться к камере

        Returns:
            True если подключение успешно
        """
        try:
            self._close_capture()

            # Создаем новый захват
            if self.config.rtsp_url:
                logger.info(f"Connecting to RTSP: {self.config.rtsp_url}")
                self.capture = cv2.VideoCapture(self.config.rtsp_url, cv2.CAP_FFMPEG)
            else:
                logger.info(f"Connecting to local camera: {self.config.camera_index}")
                self.capture = cv2.VideoCapture(self.config.camera_index)

            if not self.capture.isOpened():
                logger.error("Failed to open camera")
                return False

            # Настраиваем параметры захвата
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.frame_width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.frame_height)
            self.capture.set(cv2.CAP_PROP_FPS, self.config.fps_target)

            # Проверяем что захват работает
            ret, test_frame = self.capture.read()
            if not ret or test_frame is None:
                logger.error("Failed to read test frame")
                self._close_capture()
                return False

            self.is_connected = True
            logger.info("Camera connected successfully")
            return True

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self._close_capture()
            return False

    def _close_capture(self):
        """Закрыть захват"""
        if self.capture:
            try:
                self.capture.release()
            except Exception as e:
                logger.error(f"Error closing capture: {e}")
            self.capture = None

    def _handle_disconnect(self):
        """Обработать отключение"""
        if self.is_connected:
            self.is_connected = False
            self._notify_status_change(False)
            logger.warning("Camera disconnected")

    def _notify_status_change(self, connected: bool):
        """Уведомить об изменении статуса"""
        if self.on_status_change_callback:
            try:
                self.on_status_change_callback(connected)
            except Exception as e:
                logger.error(f"Status callback error: {e}")

    def _update_fps(self):
        """Обновить расчет FPS"""
        current_time = time.time()
        time_diff = current_time - self.last_frame_time

        if time_diff > 0:
            instant_fps = 1.0 / time_diff
            # Экспоненциальное сглаживание
            alpha = 0.1
            self.current_fps = alpha * instant_fps + (1 - alpha) * self.current_fps

        self.last_frame_time = current_time


class MockCameraManager(CameraManager):
    """
    Mock менеджер камеры для тестирования

    Генерирует тестовые кадры без реальной камеры
    """

    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self.mock_frame_count = 0
        # Для mock камеры сразу устанавливаем подключение
        self.is_connected = True

    def _connect(self) -> bool:
        """Мок подключение - всегда успешно"""
        self.is_connected = True
        logger.info("Mock camera connected")
        return True

    def _capture_loop(self):
        """Генерирует тестовые кадры"""
        import numpy as np

        while self.is_running and self.is_connected:
            try:
                # Создаем тестовый кадр (640x480 RGB)
                frame = np.zeros((480, 640, 3), dtype=np.uint8)

                # Добавляем простой паттерн
                self.mock_frame_count += 1
                color = (self.mock_frame_count % 255, 100, 200)
                cv2.rectangle(frame, (50, 50), (200, 150), color, -1)

                # Добавляем текст с счетчиком
                cv2.putText(frame, f"Mock Frame {self.mock_frame_count}",
                           (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

                # Добавляем в очередь
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass

                self.frames_captured += 1
                self._update_fps()

                # Имитируем FPS
                time.sleep(1.0 / self.config.fps_target)

            except Exception as e:
                logger.error(f"Mock capture error: {e}")
                time.sleep(1.0)