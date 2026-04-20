"""
Сетевые компоненты для коммуникации с backend серверами

Реализует UDP/TCP протоколы для обмена данными о детекции
и получении результатов поиска кабинетов.
"""

import socket
import threading
import json
import time
import logging
from typing import Callable, Optional, Dict, Any, Union, Union
from dataclasses import dataclass

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NetworkConfig:
    """Конфигурация сетевых подключений"""
    udp_listen_port: int = 5001  # Порт для прослушивания UDP
    udp_send_port: int = 5000    # Порт для отправки UDP
    udp_send_host: str = "127.0.0.1"  # Хост для UDP отправки
    tcp_host: str = "localhost"  # Хост TCP сервера
    tcp_port: int = 8080         # Порт TCP сервера
    buffer_size: int = 4096      # Размер буфера
    timeout: float = 5.0         # Таймаут подключения
    reconnect_delay: float = 2.0 # Задержка переподключения

    @classmethod
    def from_config(cls, config: "Config") -> "NetworkConfig":
        """Создать NetworkConfig из общего Config"""
        return cls(
            udp_listen_port=config.udp_listen_port,
            udp_send_port=config.udp_send_port,
            udp_send_host=getattr(config, 'udp_send_host', '127.0.0.1'),
            tcp_host=config.java_server_ip,
            tcp_port=config.java_server_port,
            timeout=getattr(config, 'tcp_timeout', 5.0),
            reconnect_delay=getattr(config, 'tcp_reconnect_delay', 2.0)
        )
    reconnect_delay: float = 2.0 # Задержка переподключения

    @classmethod
    def from_config(cls, config: "Config") -> "NetworkConfig":
        """Создать NetworkConfig из общего Config"""
        return cls(
            udp_listen_port=config.udp_listen_port,
            udp_send_port=config.udp_send_port,
            udp_send_host=getattr(config, 'udp_send_host', '127.0.0.1'),
            tcp_host=config.java_server_ip,
            tcp_port=config.java_server_port,
            timeout=getattr(config, 'tcp_timeout', 5.0),
            reconnect_delay=getattr(config, 'tcp_reconnect_delay', 2.0)
        )


class UDPServer:
    """
    UDP сервер для приема сообщений от backend

    Асинхронно слушает UDP порт и вызывает callback
    при получении сообщений.
    """

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.message_callback: Optional[Callable[[Dict[str, Any]], None]] = None

    def set_message_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Установить callback для обработки входящих сообщений"""
        self.message_callback = callback

    def start(self) -> bool:
        """
        Запустить UDP сервер

        Returns:
            True если сервер запущен успешно
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.config.udp_listen_port))
            self.sock.settimeout(1.0)  # Таймаут для graceful shutdown

            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()

            logger.info(f"UDP server started on port {self.config.udp_listen_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start UDP server: {e}")
            return False

    def stop(self):
        """Остановить UDP сервер"""
        if not self.running:
            return

        logger.info("Stopping UDP server...")
        self.running = False

        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        logger.info("UDP server stopped")

    def _listen_loop(self):
        """Основной цикл прослушивания"""
        while self.running:
            try:
                if not self.sock:
                    break

                data, addr = self.sock.recvfrom(self.config.buffer_size)
                logger.debug(f"Received {len(data)} bytes from {addr}")

                # Парсим JSON
                try:
                    message = json.loads(data.decode('utf-8'))
                    logger.info(f"Received message from {addr}: {message}")

                    # Вызываем callback
                    if self.message_callback:
                        try:
                            self.message_callback(message)
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON received from {addr}: {e}")
                except UnicodeDecodeError as e:
                    logger.warning(f"Invalid UTF-8 received from {addr}: {e}")

            except socket.timeout:
                # Нормально, просто продолжаем
                continue
            except Exception as e:
                if self.running:  # Не логируем ошибку при shutdown
                    logger.error(f"UDP listen error: {e}")
                time.sleep(0.1)


class UDPClient:
    """
    UDP клиент для отправки сообщений к backend

    Отправляет данные о детекции и получает подтверждения.
    """

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """
        Подключиться к UDP серверу

        Returns:
            True если подключение успешно
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(self.config.timeout)
            self.connected = True
            logger.info(f"UDP client connected to port {self.config.udp_send_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect UDP client: {e}")
            return False

    def disconnect(self):
        """Отключиться от UDP сервера"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.connected = False
        logger.info("UDP client disconnected")

    def send_detection_data(self, camera_id: str, people_count: int,
                          timestamp: Optional[float] = None) -> bool:
        """
        Отправить данные о детекции

        Args:
            camera_id: ID камеры
            people_count: Количество обнаруженных людей
            timestamp: Временная метка (текущее время если None)

        Returns:
            True если отправка успешна
        """
        if not self.connected or not self.sock:
            logger.warning("UDP client not connected")
            return False

        if timestamp is None:
            timestamp = time.time()

        message = {
            "type": "detection",
            "camera_id": camera_id,
            "people_count": people_count,
            "timestamp": timestamp,
            "status": "occupied" if people_count > 0 else "free"
        }

        return self._send_message(message)

    def send_heartbeat(self, camera_id: str) -> bool:
        """
        Отправить heartbeat сигнал

        Args:
            camera_id: ID камеры

        Returns:
            True если отправка успешна
        """
        if not self.connected or not self.sock:
            logger.warning("UDP client not connected")
            return False

        message = {
            "type": "heartbeat",
            "camera_id": camera_id,
            "timestamp": time.time()
        }

        return self._send_message(message)

    def _send_message(self, message: Dict[str, Any]) -> bool:
        """
        Отправить JSON сообщение

        Args:
            message: Сообщение для отправки

        Returns:
            True если отправка успешна
        """
        try:
            data = json.dumps(message).encode('utf-8')
            self.sock.sendto(data, (self.config.udp_send_host, self.config.udp_send_port))
            logger.debug(f"Sent message: {message}")
            return True

        except Exception as e:
            logger.error(f"Failed to send UDP message: {e}")
            return False


class TCPClient:
    """
    TCP клиент для подключения к Java/ESP серверам

    Используется для получения результатов поиска кабинетов
    и отправки команд.
    """

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.reconnect_thread: Optional[threading.Thread] = None
        self.running = False

    def connect(self) -> bool:
        """
        Подключиться к TCP серверу

        Returns:
            True если подключение успешно
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.config.timeout)
            self.sock.connect((self.config.tcp_host, self.config.tcp_port))
            self.connected = True
            logger.info(f"TCP client connected to {self.config.tcp_host}:{self.config.tcp_port}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect TCP client: {e}")
            return False

    def disconnect(self):
        """Отключиться от TCP сервера"""
        self.running = False

        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

        self.connected = False
        logger.info("TCP client disconnected")

    def start_auto_reconnect(self):
        """Запустить автоматическое переподключение"""
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            return

        self.running = True
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
        logger.info("Auto-reconnect started")

    def stop_auto_reconnect(self):
        """Остановить автоматическое переподключение"""
        self.running = False
        if self.reconnect_thread and self.reconnect_thread.is_alive():
            self.reconnect_thread.join(timeout=2.0)

    def send_room_request(self, room_number: str, time_slot: str) -> Optional[Dict[str, Any]]:
        """
        Отправить запрос на поиск кабинета

        Args:
            room_number: Номер кабинета
            time_slot: Временной слот

        Returns:
            Ответ сервера или None при ошибке
        """
        if not self.connected or not self.sock:
            logger.warning("TCP client not connected")
            return None

        message = {
            "type": "room_request",
            "room_number": room_number,
            "time_slot": time_slot,
            "timestamp": time.time()
        }

        return self._send_request(message)

    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Отправить команду серверу

        Args:
            command: Команда
            params: Параметры команды

        Returns:
            Ответ сервера или None при ошибке
        """
        if not self.connected or not self.sock:
            logger.warning("TCP client not connected")
            return None

        message = {
            "type": "command",
            "command": command,
            "params": params or {},
            "timestamp": time.time()
        }

        return self._send_request(message)

    def _send_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Отправить запрос и получить ответ

        Args:
            message: Сообщение для отправки

        Returns:
            Ответ сервера или None при ошибке
        """
        try:
            # Отправляем запрос
            data = json.dumps(message).encode('utf-8')
            self.sock.sendall(data)

            # Получаем ответ
            response_data = self.sock.recv(self.config.buffer_size)
            response = json.loads(response_data.decode('utf-8'))

            logger.debug(f"TCP request: {message}")
            logger.debug(f"TCP response: {response}")

            return response

        except Exception as e:
            logger.error(f"TCP request failed: {e}")
            self.connected = False
            return None

    def _reconnect_loop(self):
        """Цикл автоматического переподключения"""
        while self.running:
            if not self.connected:
                logger.info("Attempting to reconnect TCP client...")
                if self.connect():
                    logger.info("TCP client reconnected successfully")
                else:Union[NetworkConfig, object]):
        # Поддержка передачи как NetworkConfig, так и Config
        if not isinstance(config, NetworkConfig):
            try:
                from src.core.config import Config
            except ImportError:
                Config = None

            if Config is not None and isinstance(config, Config):
                config = NetworkConfig.from_config(config)
            else:
                raise TypeError("NetworkManager requires NetworkConfig or Config instance")

                    logger.warning(f"TCP reconnect failed, retrying in {self.config.reconnect_delay}s")
                    time.sleep(self.config.reconnect_delay)
            else:
                time.sleep(1.0)  # Проверяем соединение каждую секунду


class NetworkManager:
    """
    Менеджер сетевых подключений

    Управляет всеми сетевыми компонентами приложения.
    """

    def __init__(self, config: Union[NetworkConfig, object]):
        # Поддержка передачи как NetworkConfig, так и Config
        if not isinstance(config, NetworkConfig):
            try:
                from src.core.config import Config
            except ImportError:
                Config = None

            if Config is not None and isinstance(config, Config):
                config = NetworkConfig.from_config(config)
            else:
                raise TypeError("NetworkManager requires NetworkConfig or Config instance")

        self.config = config

        # Создаем компоненты
        self.udp_server = UDPServer(config)
        self.udp_client = UDPClient(config)
        self.tcp_client = TCPClient(config)

        self.message_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

    def start(self) -> bool:
        """
        Запустить все сетевые компоненты

        Returns:
            True если все компоненты запущены успешно
        """
        logger.info("Starting network manager...")

        success = True

        # Запускаем UDP сервер
        if not self.udp_server.start():
            success = False

        # Подключаем UDP клиент
        if not self.udp_client.connect():
            success = False

        # Подключаем TCP клиент и включаем авто-реконнект
        if self.tcp_client.connect():
            self.tcp_client.start_auto_reconnect()
        else:
            logger.warning("TCP client initial connection failed, auto-reconnect enabled")
            self.tcp_client.start_auto_reconnect()

        # Настраиваем обработчик сообщений UDP сервера
        self.udp_server.set_message_callback(self._handle_udp_message)

        if success:
            logger.info("Network manager started successfully")
        else:
            logger.warning("Network manager started with some failures")

        return success

    def stop(self):
        """Остановить все сетевые компоненты"""
        logger.info("Stopping network manager...")

        self.udp_server.stop()
        self.udp_client.disconnect()
        self.tcp_client.stop_auto_reconnect()
        self.tcp_client.disconnect()

        logger.info("Network manager stopped")

    def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]):
        """
        Зарегистрировать обработчик для типа сообщений

        Args:
            message_type: Тип сообщения
            handler: Функция обработчик
        """
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    def send_detection_update(self, camera_id: str, people_count: int) -> bool:
        """
        Отправить обновление данных детекции

        Args:
            camera_id: ID камеры
            people_count: Количество людей

        Returns:
            True если отправка успешна
        """
        return self.udp_client.send_detection_data(camera_id, people_count)

    def send_heartbeat(self, camera_id: str) -> bool:
        """
        Отправить heartbeat

        Args:
            camera_id: ID камеры
        message_type = message.get("type")

        if not message_type:
            logger.warning("UDP message missing type field")
            return

        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error executing handler for {message_type}: {e}")
        else:
            logger.warning(f"No handler registered for UDP message type: {message_type}")

        Returns:
            True если отправка успешна
        """
        return self.udp_client.send_heartbeat(camera_id)

    def request_room_info(self, room_number: str, time_slot: str) -> Optional[Dict[str, Any]]:
        """
        Запросить информацию о кабинете

        Args:
            room_number: Номер кабинета
            time_slot: Временной слот

        Returns:
            Информация о кабинете или None
        """
        return self.tcp_client.send_room_request(room_number, time_slot)

    def _handle_udp_message(self, message: Dict[str, Any]):
        """
        Обработать входящее UDP сообщение

        Args:
            message: Полученное сообщение
        """
        message_type = message.get("type")

        if not message_type:
            logger.warning("UDP message missing type field")
            return

        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error executing handler for {message_type}: {e}")
        else:
            logger.warning(f"No handler registered for UDP message type: {message_type}")

            logger.error(f"Error handling UDP message: {e}")