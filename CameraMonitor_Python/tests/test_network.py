"""
Тесты для сетевых компонентов
"""

import unittest
import json
import socket
import threading
import time
from unittest.mock import patch, MagicMock, mock_open

from src.core.network import (
    NetworkConfig, UDPServer, UDPClient, TCPClient, NetworkManager
)


class TestNetworkConfig(unittest.TestCase):
    """Тесты для NetworkConfig"""

    def test_default_config(self):
        """Тест конфигурации по умолчанию"""
        config = NetworkConfig()

        self.assertEqual(config.udp_listen_port, 5001)
        self.assertEqual(config.udp_send_port, 5000)
        self.assertEqual(config.tcp_host, "localhost")
        self.assertEqual(config.tcp_port, 8080)
        self.assertEqual(config.buffer_size, 4096)
        self.assertEqual(config.timeout, 5.0)
        self.assertEqual(config.reconnect_delay, 2.0)


class TestUDPServer(unittest.TestCase):
    """Тесты для UDPServer"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.config = NetworkConfig(udp_listen_port=5002)
        self.server = UDPServer(self.config)
        self.received_messages = []

    def tearDown(self):
        """Очистка после каждого теста"""
        self.server.stop()

    def test_server_start_stop(self):
        """Тест запуска и остановки сервера"""
        # Запуск
        result = self.server.start()
        self.assertTrue(result)
        self.assertTrue(self.server.running)

        # Остановка
        self.server.stop()
        self.assertFalse(self.server.running)

    def test_message_callback(self):
        """Тест callback обработки сообщений"""
        def callback(message):
            self.received_messages.append(message)

        self.server.set_message_callback(callback)

        # Запускаем сервер
        self.server.start()
        time.sleep(0.1)  # Даем время на запуск

        # Отправляем тестовое сообщение
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_message = {"type": "test", "data": "hello"}
        sock.sendto(json.dumps(test_message).encode(), ('localhost', 5002))
        sock.close()

        # Ждем обработки
        time.sleep(0.2)

        # Проверяем
        self.assertEqual(len(self.received_messages), 1)
        self.assertEqual(self.received_messages[0], test_message)

    def test_invalid_json(self):
        """Тест обработки невалидного JSON"""
        received_logs = []

        def mock_warning(msg):
            received_logs.append(msg)

        with patch('src.core.network.logger.warning', side_effect=mock_warning):
            self.server.start()
            time.sleep(0.1)

            # Отправляем невалидный JSON
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(b'invalid json', ('localhost', 5002))
            sock.close()

            time.sleep(0.2)

            # Проверяем что warning был залогирован
            self.assertTrue(any("Invalid JSON" in log for log in received_logs))


class TestUDPClient(unittest.TestCase):
    """Тесты для UDPClient"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.config = NetworkConfig()
        self.client = UDPClient(self.config)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.client.disconnect()

    def test_connect_disconnect(self):
        """Тест подключения и отключения"""
        # Подключение
        result = self.client.connect()
        self.assertTrue(result)
        self.assertTrue(self.client.connected)

        # Отключение
        self.client.disconnect()
        self.assertFalse(self.client.connected)

    def test_send_detection_data(self):
        """Тест отправки данных детекции"""
        self.client.connect()

        # Мокаем сокет для проверки отправки
        with patch.object(self.client, 'sock') as mock_sock:
            result = self.client.send_detection_data("cam1", 3)

            self.assertTrue(result)
            # Проверяем что sendto был вызван
            mock_sock.sendto.assert_called_once()

            # Проверяем содержимое сообщения
            call_args = mock_sock.sendto.call_args
            sent_data = json.loads(call_args[0][0].decode())
            self.assertEqual(sent_data["type"], "detection")
            self.assertEqual(sent_data["camera_id"], "cam1")
            self.assertEqual(sent_data["people_count"], 3)
            self.assertEqual(sent_data["status"], "occupied")

    def test_send_heartbeat(self):
        """Тест отправки heartbeat"""
        self.client.connect()

        with patch.object(self.client, 'sock') as mock_sock:
            result = self.client.send_heartbeat("cam1")

            self.assertTrue(result)
            mock_sock.sendto.assert_called_once()

            # Проверяем содержимое
            call_args = mock_sock.sendto.call_args
            sent_data = json.loads(call_args[0][0].decode())
            self.assertEqual(sent_data["type"], "heartbeat")
            self.assertEqual(sent_data["camera_id"], "cam1")

    def test_send_without_connection(self):
        """Тест отправки без подключения"""
        result = self.client.send_detection_data("cam1", 0)
        self.assertFalse(result)


class TestTCPClient(unittest.TestCase):
    """Тесты для TCPClient"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.config = NetworkConfig(tcp_host="127.0.0.1", tcp_port=9999)  # Не существующий порт
        self.client = TCPClient(self.config)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.client.disconnect()

    def test_connect_failure(self):
        """Тест неудачного подключения"""
        result = self.client.connect()
        self.assertFalse(result)
        self.assertFalse(self.client.connected)

    def test_send_without_connection(self):
        """Тест отправки без подключения"""
        result = self.client.send_room_request("101", "09:00-10:00")
        self.assertIsNone(result)

    @patch('socket.socket')
    def test_mock_connection(self, mock_socket_class):
        """Тест с мок подключением"""
        # Мокаем сокет
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock

        # Мокаем успешное подключение
        self.client.connect()
        self.assertTrue(self.client.connected)

        # Мокаем ответ сервера
        mock_response = {"status": "success", "room": "101", "available": True}
        mock_sock.recv.return_value = json.dumps(mock_response).encode()

        # Тест отправки запроса
        result = self.client.send_room_request("101", "09:00-10:00")

        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["available"], True)

        # Проверяем что данные были отправлены
        mock_sock.sendall.assert_called_once()


class TestNetworkManager(unittest.TestCase):
    """Тесты для NetworkManager"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.config = NetworkConfig()
        self.manager = NetworkManager(self.config)

    def tearDown(self):
        """Очистка после каждого теста"""
        self.manager.stop()

    def test_message_handler_registration(self):
        """Тест регистрации обработчиков сообщений"""
        def test_handler(message):
            pass

        self.manager.register_message_handler("test_type", test_handler)

        self.assertIn("test_type", self.manager.message_handlers)
        self.assertEqual(self.manager.message_handlers["test_type"], test_handler)

    @patch('src.core.network.UDPClient')
    def test_send_detection_update(self, mock_udp_client_class):
        """Тест отправки обновления детекции"""
        mock_client = MagicMock()
        mock_udp_client_class.return_value = mock_client
        self.manager.udp_client = mock_client

        result = self.manager.send_detection_update("cam1", 5)

        mock_client.send_detection_data.assert_called_once_with("cam1", 5)
        self.assertEqual(result, mock_client.send_detection_data.return_value)

    @patch('src.core.network.TCPClient')
    def test_request_room_info(self, mock_tcp_client_class):
        """Тест запроса информации о кабинете"""
        mock_client = MagicMock()
        mock_tcp_client_class.return_value = mock_client
        self.manager.tcp_client = mock_client

        result = self.manager.request_room_info("101", "09:00-10:00")

        mock_client.send_room_request.assert_called_once_with("101", "09:00-10:00")
        self.assertEqual(result, mock_client.send_room_request.return_value)


if __name__ == "__main__":
    unittest.main()