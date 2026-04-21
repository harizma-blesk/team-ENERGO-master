"""
Тесты для системы базы данных
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.core.database import DatabaseManager, Camera, CabinetBooking, Notification


class TestDatabaseManager(unittest.TestCase):
    """Тесты для DatabaseManager"""

    def setUp(self):
        """Создание временной БД для тестов"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        """Очистка после тестов"""
        self.db.close()
        Path(self.db_path).unlink(missing_ok=True)

    def test_database_initialization(self):
        """Тест инициализации БД"""
        # Проверяем что таблицы созданы
        from sqlalchemy import inspect
        inspector = inspect(self.db.engine)

        # Проверяем существование таблиц
        table_names = inspector.get_table_names()
        self.assertIn("cameras", table_names)
        self.assertIn("cabinet_bookings", table_names)
        self.assertIn("notifications", table_names)
        self.assertIn("detection_logs", table_names)

    def test_camera_operations(self):
        """Тест операций с камерами"""
        # Добавление камеры
        camera = self.db.add_camera("Test Camera", "rtsp://test.com", "Room 101")
        self.assertEqual(camera.name, "Test Camera")
        self.assertEqual(camera.rtsp_url, "rtsp://test.com")
        self.assertEqual(camera.location, "Room 101")
        self.assertEqual(camera.status, "offline")

        # Получение камер
        cameras = self.db.get_cameras()
        self.assertEqual(len(cameras), 1)
        self.assertEqual(cameras[0].name, "Test Camera")

        # Обновление статуса
        self.db.update_camera_status(camera.id, "online")
        updated_cameras = self.db.get_cameras()
        self.assertEqual(updated_cameras[0].status, "online")

    def test_booking_operations(self):
        """Тест операций с бронированиями"""
        now = datetime.now(timezone.utc)
        later = now + timedelta(hours=2)

        # Добавление бронирования
        booking = self.db.add_booking("101", "A", now, later, 5)
        self.assertEqual(booking.cabinet_id, "101")
        self.assertEqual(booking.corpus, "A")
        self.assertEqual(booking.people_count, 5)

        # Поиск свободных кабинетов (пока все свободны)
        available = self.db.find_available_cabinets("A", now, later)
        self.assertEqual(len(available), 0)  # Нет кабинетов в корпусе A кроме занятого

        # Очистка временных бронирований
        deleted_count = self.db.clear_temporary_bookings()
        self.assertEqual(deleted_count, 1)

    def test_notification_operations(self):
        """Тест операций с уведомлениями"""
        # Добавление уведомления
        notification = self.db.add_notification("Test message", "warning", "101")
        self.assertEqual(notification.message, "Test message")
        self.assertEqual(notification.notification_type, "warning")
        self.assertEqual(notification.cabinet_id, "101")
        self.assertFalse(notification.is_read)

        # Получение непрочитанных уведомлений
        unread = self.db.get_unread_notifications()
        self.assertEqual(len(unread), 1)
        self.assertEqual(unread[0].message, "Test message")

    def test_detection_logging(self):
        """Тест логирования детекции"""
        # Добавление камеры для теста
        camera = self.db.add_camera("Detection Camera")

        # Логирование детекции
        self.db.log_detection(camera.id, 3, 0.85, "101")

        # Получение статистики
        stats = self.db.get_detection_stats(hours=1)
        self.assertEqual(stats["total_detections"], 1)
        self.assertEqual(stats["avg_people"], 3.0)
        self.assertEqual(stats["max_people"], 3)


if __name__ == "__main__":
    unittest.main()