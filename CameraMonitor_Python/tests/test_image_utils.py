"""
Тесты для утилит работы с изображениями
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock
import cv2

from src.utils.image_utils import ImageConverter, DetectionVisualizer


class TestImageConverter(unittest.TestCase):
    """Тесты для ImageConverter"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем тестовое изображение OpenCV (BGR)
        self.test_image_bgr = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        # Создаем тестовое изображение RGB
        self.test_image_rgb = cv2.cvtColor(self.test_image_bgr, cv2.COLOR_BGR2RGB)

    def test_resize_cv2_image_keep_aspect(self):
        """Тест изменения размера с сохранением соотношения"""
        resized = ImageConverter.resize_cv2_image(
            self.test_image_bgr, (320, 240), keep_aspect=True
        )

        # Проверяем что размеры корректны
        self.assertEqual(resized.shape[1], 320)  # width
        self.assertEqual(resized.shape[0], 240)  # height

    def test_resize_cv2_image_no_aspect(self):
        """Тест изменения размера без сохранения соотношения"""
        resized = ImageConverter.resize_cv2_image(
            self.test_image_bgr, (320, 240), keep_aspect=False
        )

        self.assertEqual(resized.shape[1], 320)
        self.assertEqual(resized.shape[0], 240)

    def test_draw_detections(self):
        """Тест рисования детекций"""
        detections = [
            {'bbox': (10, 10, 100, 100), 'confidence': 0.85, 'class': 'person'},
            {'bbox': (200, 200, 300, 300), 'confidence': 0.72, 'class': 'car'}
        ]

        result = ImageConverter.draw_detections(self.test_image_bgr, detections)

        # Проверяем что изображение изменилось (нарисованы рамки)
        self.assertFalse(np.array_equal(result, self.test_image_bgr))

        # Проверяем размеры
        self.assertEqual(result.shape, self.test_image_bgr.shape)

    def test_crop_image_valid(self):
        """Тест обрезки изображения с валидными координатами"""
        bbox = (100, 100, 300, 200)
        cropped = ImageConverter.crop_image(self.test_image_bgr, bbox)

        self.assertIsNotNone(cropped)
        self.assertEqual(cropped.shape, (100, 200, 3))  # height, width, channels

    def test_crop_image_invalid(self):
        """Тест обрезки изображения с невалидными координатами"""
        # bbox за пределами изображения
        bbox = (700, 700, 800, 800)
        cropped = ImageConverter.crop_image(self.test_image_bgr, bbox)

        self.assertIsNone(cropped)

    def test_crop_image_empty(self):
        """Тест обрезки с нулевой площадью"""
        bbox = (100, 100, 100, 200)  # width = 0
        cropped = ImageConverter.crop_image(self.test_image_bgr, bbox)

        self.assertIsNone(cropped)

    @patch('src.utils.image_utils.QT_AVAILABLE', False)
    def test_qimage_conversion_no_qt(self):
        """Тест конвертации без PyQt6"""
        qimage = ImageConverter.cv2_to_qimage(self.test_image_bgr)
        self.assertIsNone(qimage)

        qpixmap = ImageConverter.cv2_to_qpixmap(self.test_image_bgr)
        self.assertIsNone(qpixmap)

    @patch('src.utils.image_utils.QT_AVAILABLE', True)
    def test_qimage_conversion_mock_qt(self):
        """Тест конвертации с мок PyQt6"""
        # Мокаем Qt классы
        with patch('src.utils.image_utils.QImage') as mock_qimage, \
             patch('src.utils.image_utils.QPixmap') as mock_qpixmap:

            # Настраиваем моки
            mock_qimage_instance = MagicMock()
            mock_qimage.return_value = mock_qimage_instance

            mock_qpixmap.fromImage.return_value = MagicMock()

            # Тест cv2_to_qimage
            result = ImageConverter.cv2_to_qimage(self.test_image_bgr)
            self.assertEqual(result, mock_qimage_instance)

            # Тест cv2_to_qpixmap
            result = ImageConverter.cv2_to_qpixmap(self.test_image_bgr)
            mock_qpixmap.fromImage.assert_called_once()

    def test_pil_conversion(self):
        """Тест конвертации PIL"""
        # Создаем PIL изображение
        pil_image = ImageConverter.cv2_to_pil(self.test_image_bgr)
        self.assertEqual(pil_image.mode, 'RGB')
        self.assertEqual(pil_image.size, (640, 480))

        # Конвертируем обратно
        cv2_image = ImageConverter.pil_to_cv2(pil_image)
        self.assertEqual(cv2_image.shape, (480, 640, 3))


class TestDetectionVisualizer(unittest.TestCase):
    """Тесты для DetectionVisualizer"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def test_colors_defined(self):
        """Тест что цвета определены"""
        self.assertIn('person', DetectionVisualizer.COLORS)
        self.assertIn('car', DetectionVisualizer.COLORS)
        self.assertEqual(len(DetectionVisualizer.COLORS['person']), 3)  # BGR

    @patch('src.utils.image_utils.ImageConverter.draw_detections')
    def test_draw_yolo_results(self, mock_draw):
        """Тест рисования результатов YOLO"""
        # Мокаем YOLO результаты
        mock_results = [MagicMock()]
        mock_results[0].boxes = MagicMock()
        mock_results[0].names = {0: 'person'}

        # Мокаем boxes
        mock_box = MagicMock()
        mock_xyxy = MagicMock()
        mock_xyxy.cpu.return_value.numpy.return_value = np.array([10, 20, 100, 200])
        mock_box.xyxy = [mock_xyxy]
        
        mock_conf = MagicMock()
        mock_conf.cpu.return_value.numpy.return_value = 0.85
        mock_box.conf = [mock_conf]
        
        mock_cls = MagicMock()
        mock_cls.cpu.return_value.numpy.return_value = 0
        mock_box.cls = [mock_cls]
        
        mock_results[0].boxes = [mock_box]

        mock_draw.return_value = self.test_image

        result = DetectionVisualizer.draw_yolo_results(self.test_image, mock_results)

        # Проверяем что draw_detections был вызван
        mock_draw.assert_called_once()
        self.assertEqual(result.shape, self.test_image.shape)

    def test_draw_yolo_results_no_boxes(self):
        """Тест рисования без bounding boxes"""
        mock_results = [MagicMock()]
        mock_results[0].boxes = None

        result = DetectionVisualizer.draw_yolo_results(self.test_image, mock_results)

        # Изображение не должно измениться
        self.assertTrue(np.array_equal(result, self.test_image))

    def test_create_overlay_image(self):
        """Тест создания overlay изображения"""
        detections = [
            {'bbox': (10, 10, 100, 100), 'class': 'person'},
            {'bbox': (200, 200, 300, 300), 'class': 'car'}
        ]

        overlay = DetectionVisualizer.create_overlay_image(detections, (640, 480))

        self.assertIsNotNone(overlay)
        self.assertEqual(overlay.shape, (480, 640, 3))

        # Проверяем что overlay не пустой
        non_zero = np.count_nonzero(overlay)
        self.assertGreater(non_zero, 0)


if __name__ == "__main__":
    # Импортируем здесь чтобы избежать проблем с PyQt6
    import cv2
    from PIL import Image

    unittest.main()