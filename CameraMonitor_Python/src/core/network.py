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
from typing import Callable, Optional, Dict, Any, Union
from dataclasses import dataclass



from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NetworkConfig:
    """Конфигурация сетевых подключений"""
    udp_listen_port: int = 5001
    udp_send_port: int = 5000
    udp_send_host: str = "127.0.0.1"
    tcp_host: str = "localhost"
    tcp_port: int = 8080
    buffer_size: int = 4096
    timeout: float = 5.0
    reconnect_delay: float = 2.0

    @classmethod
    def from_config(cls, config: "Config") -> "NetworkConfig":
        """Создать NetworkConfig из общего Config"""
        return cls(
            udp_listen_port=config.udp_listen_port,
            udp_send_port=config.udp_send_port,
            udp_send_host=getattr(config, 'udp_send_host', '127.0.0.1'),
            tcp_host=config.PHP_server_ip,
            tcp_port=config.PHP_server_port,
            timeout=getattr(config, 'tcp_timeout', 5.0),
            reconnect_delay=getattr(config, 'tcp_reconnect_delay', 2.0)
        )


class UDPServer:
    """UDP сервер для приема сообщений от backend"""

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
        """Запустить UDP сервер"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('0.0.0.0', self.config.udp_listen_port))
            self.sock.settimeout(1.0)

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

                try:
                    message = json.loads(data.decode('utf-8'))
                    logger.info(f"Received message from {addr}: {message}")

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
                continue
            except Exception as e:
                if self.running:
                    logger.error(f"UDP listen error: {e}")
                time.sleep(0.1)


class UDPClient:
    """UDP клиент для отправки сообщений к backend"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.connected = False

    def connect(self) -> bool:
        """Подключиться к UDP серверу"""
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
        """Отправить данные о детекции"""
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
        """Отправить heartbeat сигнал"""
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
        """Отправить JSON сообщение"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.sock.sendto(data, (self.config.udp_send_host, self.config.udp_send_port))
            logger.debug(f"Sent message: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send UDP message: {e}")
            return False


class TCPClient:
    """TCP клиент для подключения к PHP/ESP серверам"""

    def __init__(self, config: NetworkConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.reconnect_thread: Optional[threading.Thread] = None
        self.running = False

    def connect(self) -> bool:
        """Подключиться к TCP серверу"""
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
        """Отправить запрос на поиск кабинета"""
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
        """Отправить команду серверу"""
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
        """Отправить запрос и получить ответ"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.sock.sendall(data)
            logger.debug(f"Sent request: {message}")

            response_data = self.sock.recv(self.config.buffer_size)
            if response_data:
                response = json.loads(response_data.decode('utf-8'))
                logger.info(f"Received response: {response}")
                return response
            return None

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
                else:
                    logger.warning(f"TCP reconnect failed, retrying in {self.config.reconnect_delay}s")
                    time.sleep(self.config.reconnect_delay)
            else:
                time.sleep(1.0)


class NetworkManager:
    """Менеджер сетевых подключений — UDP/TCP отключены (single machine mode)"""

    def __init__(self, config: Union[NetworkConfig, object]):
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
        self.message_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self.udp_server = None
        self.udp_client = None
        self.tcp_client = None

    def start(self) -> bool:
        logger.info("Network manager started (UDP/TCP disabled - single machine mode)")
        return True

    def stop(self):
        logger.info("Network manager stopped")

    def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]):
        self.message_handlers[message_type] = handler

    def send_detection_update(self, camera_id: str, people_count: int) -> bool:
        return True

    def send_heartbeat(self, camera_id: str) -> bool:
        return True

    def request_room_info(self, room_number: str, time_slot: str) -> Optional[Dict[str, Any]]:
        return None

    def _handle_udp_message(self, message: Dict[str, Any]):
        message_type = message.get("type")
        if not message_type:
            return
        handler = self.message_handlers.get(message_type)
        if handler:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Error executing handler for {message_type}: {e}")