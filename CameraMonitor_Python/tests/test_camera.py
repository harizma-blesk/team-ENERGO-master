"""
Тесты для модуля захвата видео
"""

import unittest
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import cv2
import numpy as np

from src.core.camera import CameraManager, CameraConfig, MockCameraManager


class TestCameraConfig(unittest.TestCase):
    """Тесты для CameraConfig"""

    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = CameraConfig()
        self.assertIsNone(config.rtsp_url)
        self.assertEqual(config.camera_index, 0)
        self.assertEqual(config.fps_target, 30)
        self.assertEqual(config.frame_width, 640)
        self.assertEqual(config.frame_height, 480)


class TestCameraManager(unittest.TestCase):
    """Тесты для CameraManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.config = CameraConfig(
            rtsp_url="rtsp://test.com",
            camera_index=0,
            fps_target=10  # Быстрее для тестов
        )

    def tearDown(self):
        """Очистка после каждого теста"""
        # Здесь можно добавить очистку если нужно
        pass

    @patch('cv2.VideoCapture')
    def test_start_rtsp_camera(self, mock_cv2):
        """Тест запуска RTSP камеры"""
        # Мокаем VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2.return_value = mock_cap

        manager = CameraManager(self.config)

        # Запускаем
        result = manager.start()
        self.assertTrue(result)
        self.assertTrue(manager.is_connected)

        # Останавливаем
        manager.stop()
        self.assertFalse(manager.is_running)

    @patch('cv2.VideoCapture')
    def test_start_local_camera(self, mock_cv2):
        """Тест запуска локальной камеры"""
        config = CameraConfig(camera_index=1)

        # Мокаем VideoCapture
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2.return_value = mock_cap

        manager = CameraManager(config)

        result = manager.start()
        self.assertTrue(result)

        manager.stop()

    @patch('cv2.VideoCapture')
    def test_camera_connection_failure(self, mock_cv2):
        """Тест обработки ошибки подключения"""
        # Мокаем VideoCapture с ошибкой
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cv2.return_value = mock_cap

        manager = CameraManager(self.config)

        result = manager.start()
        self.assertFalse(result)
        self.assertFalse(manager.is_connected)

    def test_get_frame_empty_queue(self):
        """Тест получения кадра из пустой очереди"""
        manager = CameraManager(self.config)

        frame = manager.get_frame(timeout=0.1)
        self.assertIsNone(frame)

    def test_get_stats(self):
        """Тест получения статистики"""
        manager = CameraManager(self.config)

        stats = manager.get_stats()
        self.assertIn('is_connected', stats)
        self.assertIn('current_fps', stats)
        self.assertIn('frames_captured', stats)
        self.assertFalse(stats['is_connected'])
        self.assertEqual(stats['frames_captured'], 0)

    def test_callbacks(self):
        """Тест callback функций"""
        manager = CameraManager(self.config)

        frame_callback_called = False
        status_callback_called = False

        def frame_callback(frame):
            nonlocal frame_callback_called
            frame_callback_called = True

        def status_callback(connected):
            nonlocal status_callback_called
            status_callback_called = True

        manager.set_frame_callback(frame_callback)
        manager.set_status_callback(status_callback)

        # Вызываем callbacks напрямую для теста
        manager.on_frame_callback and manager.on_frame_callback(np.zeros((480, 640, 3), dtype=np.uint8))
        manager.on_status_change_callback and manager.on_status_change_callback(True)

        self.assertTrue(frame_callback_called)
        self.assertTrue(status_callback_called)


class TestMockCameraManager(unittest.TestCase):
    """Тесты для MockCameraManager"""

    def test_mock_camera_start(self):
        """Тест запуска mock камеры"""
        config = CameraConfig()
        manager = MockCameraManager(config)

        result = manager.start()
        self.assertTrue(result)
        self.assertTrue(manager.is_connected)

        # Получаем несколько кадров
        for i in range(3):
            frame = manager.get_frame(timeout=1.0)
            self.assertIsNotNone(frame)
            self.assertEqual(frame.shape, (480, 640, 3))

        manager.stop()

    def test_mock_frame_content(self):
        """Тест содержимого mock кадров"""
        config = CameraConfig()
        manager = MockCameraManager(config)

        manager.start()

        frame = manager.get_frame(timeout=1.0)
        self.assertIsNotNone(frame)

        # Проверяем что кадр не пустой (содержит паттерн)
        # Mock рисует прямоугольники, так что не все пиксели нулевые
        non_zero_pixels = np.count_nonzero(frame)
        self.assertGreater(non_zero_pixels, 0)

        manager.stop()


if __name__ == "__main__":
    unittest.main()