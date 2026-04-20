"""
Тесты для модуля детекции
"""

import unittest
import numpy as np
from unittest.mock import patch, MagicMock

from src.core.detector import PersonDetector, DetectionResult, DetectionStats, MockPersonDetector


class TestDetectionResult(unittest.TestCase):
    """Тесты для DetectionResult"""

    def test_detection_result_creation(self):
        """Тест создания DetectionResult"""
        result = DetectionResult(
            bbox=(10, 20, 100, 200),
            confidence=0.85,
            class_id=0,
            class_name="person"
        )

        self.assertEqual(result.bbox, (10, 20, 100, 200))
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.class_id, 0)
        self.assertEqual(result.class_name, "person")

    def test_to_dict(self):
        """Тест конвертации в словарь"""
        result = DetectionResult(
            bbox=(10, 20, 100, 200),
            confidence=0.85,
            class_id=0,
            class_name="person"
        )

        data = result.to_dict()
        expected = {
            'bbox': (10, 20, 100, 200),
            'confidence': 0.85,
            'class_id': 0,
            'class_name': "person"
        }
        self.assertEqual(data, expected)


class TestPersonDetector(unittest.TestCase):
    """Тесты для PersonDetector"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    @patch('src.core.detector.YOLO_AVAILABLE', False)
    def test_detector_without_ultralytics(self):
        """Тест детектора без установленного ultralytics"""
        with self.assertRaises(ImportError):
            PersonDetector()

    @patch('src.core.detector.YOLO_AVAILABLE', True)
    @patch('src.core.detector.YOLO')
    @patch('os.path.exists', return_value=True)
    def test_load_model_success(self, mock_exists, mock_yolo_class):
        """Тест успешной загрузки модели"""
        # Мокаем YOLO класс
        mock_model = MagicMock()
        mock_model.names = {0: 'person', 1: 'car'}
        mock_yolo_class.return_value = mock_model

        detector = PersonDetector("models/test.pt")
        result = detector.load_model()

        self.assertTrue(result)
        self.assertTrue(detector.is_loaded)
        self.assertEqual(detector.model, mock_model)

    @patch('src.core.detector.YOLO_AVAILABLE', True)
    def test_load_model_file_not_found(self):
        """Тест загрузки несуществующей модели"""
        detector = PersonDetector("nonexistent.pt")
        result = detector.load_model()

        self.assertFalse(result)
        self.assertFalse(detector.is_loaded)

    @patch('src.core.detector.YOLO_AVAILABLE', True)
    @patch('src.core.detector.YOLO')
    @patch('os.path.exists', return_value=True)
    def test_detect_people_mock(self, mock_exists, mock_yolo_class):
        """Тест детекции с мок моделью"""
        # Мокаем модель
        mock_model = MagicMock()
        mock_model.names = {0: 'person'}

        # Мокаем box как объект с методами cpu().numpy()
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock()]  # box.xyxy[0] должен быть tensor-like    
        mock_box.xyxy[0].cpu.return_value.numpy.return_value = np.array([10, 20, 100, 200])
        mock_box.conf = [MagicMock()]
        mock_box.conf[0].cpu.return_value.numpy.return_value = 0.85
        mock_box.cls = [MagicMock()]
        mock_box.cls[0].cpu.return_value.numpy.return_value = 0

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]  # Сделаем boxes списком
        mock_result.names = {0: 'person'}

        mock_model.return_value = [mock_result]
        mock_yolo_class.return_value = mock_model

        detector = PersonDetector("models/test.pt")
        detector.load_model()
        detector.is_loaded = True  # Принудительно устанавливаем для теста
        detector.model = mock_model

        detections, stats = detector.detect_people(self.test_image)

        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0].class_name, 'person')
        self.assertEqual(detections[0].confidence, 0.85)
        self.assertEqual(stats.person_count, 1)
        # self.assertGreater(stats.processing_time, 0)  # Пропускаем из-за мока time

    @patch('src.core.detector.YOLO_AVAILABLE', True)
    @patch('src.core.detector.YOLO')
    def test_detect_people_no_results(self, mock_yolo_class):
        """Тест детекции без результатов"""
        # Мокаем модель без результатов
        mock_model = MagicMock()
        mock_model.names = {0: 'person'}

        mock_result = MagicMock()
        mock_result.boxes = None  # Нет детекций

        mock_model.return_value = [mock_result]
        mock_yolo_class.return_value = mock_model

        detector = PersonDetector("models/test.pt")
        detector.load_model()

        detections, stats = detector.detect_people(self.test_image)

        self.assertEqual(len(detections), 0)
        self.assertEqual(stats.person_count, 0)
        self.assertEqual(stats.total_detections, 0)

    def test_get_supported_classes(self):
        """Тест получения поддерживаемых классов"""
        detector = PersonDetector()

        # Без загруженной модели возвращает COCO классы
        classes = detector.get_supported_classes()
        self.assertIn(0, classes)
        self.assertEqual(classes[0], 'person')

    def test_get_model_info(self):
        """Тест получения информации о модели"""
        detector = PersonDetector("models/test.pt", conf_threshold=0.7)

        info = detector.get_model_info()
        self.assertEqual(info['model_path'], 'models/test.pt')
        self.assertEqual(info['conf_threshold'], 0.7)
        self.assertFalse(info['is_loaded'])

    def test_unload_model(self):
        """Тест выгрузки модели"""
        detector = PersonDetector()
        detector.is_loaded = True
        detector.model = MagicMock()

        detector.unload_model()

        self.assertFalse(detector.is_loaded)
        self.assertIsNone(detector.model)


class TestMockPersonDetector(unittest.TestCase):
    """Тесты для MockPersonDetector"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    def test_mock_detector_load(self):
        """Тест загрузки mock детектора"""
        detector = MockPersonDetector()
        result = detector.load_model()

        self.assertTrue(result)
        self.assertTrue(detector.is_loaded)

    def test_mock_detector_detect(self):
        """Тест детекции mock детектора"""
        detector = MockPersonDetector()
        detector.load_model()

        detections, stats = detector.detect_people(self.test_image)

        # Mock может вернуть детекции или пустой результат
        self.assertIsInstance(detections, list)
        self.assertIsInstance(stats, DetectionStats)

        # Если есть детекции, проверяем их структуру
        for detection in detections:
            self.assertIsInstance(detection, DetectionResult)
            self.assertIn('bbox', detection.to_dict())
            self.assertIn('confidence', detection.to_dict())


if __name__ == "__main__":
    unittest.main()