"""
Конфигурационная система для Camera Monitor
Парсит settings.ini файл и предоставляет доступ к настройкам
"""

import configparser
import os
from pathlib import Path
from typing import Optional


class Config:
    """
    Класс для работы с конфигурацией приложения

    Читает settings.ini файл и предоставляет доступ к настройкам
    через свойства с типизацией и валидацией
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Инициализация конфигурации

        Args:
            config_path: Путь к файлу конфигурации. Если None, используется config/settings.ini
        """
        if config_path is None:
            # По умолчанию ищем в config/settings.ini относительно корня проекта
            current_dir = Path(__file__).parent.parent.parent  # src/core/config.py -> CameraMonitor_Python/
            config_path = current_dir / "config" / "settings.ini"

        self.config_path = Path(config_path)
        # Отключаем интерполяцию чтобы избежать проблем с % в форматах логов
        self.parser = configparser.ConfigParser(interpolation=None)

        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            self.parser.read(self.config_path, encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Error reading config file: {e}")

    # Database section
    @property
    def db_path(self) -> str:
        """Путь к SQLite БД файлу"""
        return self.parser.get("Database", "path", fallback="camera_monitor.db")

    # Camera section
    @property
    def camera_rtsp_url(self) -> str:
        """Полный RTSP URL для камеры"""
        start = self.parser.get("Camera", "startRtcp", fallback="")
        end = self.parser.get("Camera", "endRtcp", fallback="")
        return f"{start}{end}" if start and end else start

    @property
    def camera_index(self) -> int:
        """Индекс локальной камеры"""
        return self.parser.getint("Camera", "cameraIndex", fallback=0)

    # UDP section
    @property
    def udp_server_ip(self) -> str:
        """IP адрес Python backend сервера"""
        return self.parser.get("UDP", "IP_PythonServer", fallback="127.0.0.1")

    @property
    def udp_listen_port(self) -> int:
        """Порт для прослушивания входящих UDP сообщений"""
        return self.parser.getint("UDP", "IP_Port_Listen", fallback=5000)

    @property
    def udp_send_port(self) -> int:
        """Порт для отправки UDP сообщений"""
        return self.parser.getint("UDP", "IP_Port_Send", fallback=5001)

    @property
    def udp_remote_port(self) -> int:
        """Удалённый порт (резервный)"""
        return self.parser.getint("UDP", "IP_Port_Remote", fallback=5002)

    # NEUROMODEL section
    @property
    def yolo_weights_path(self) -> str:
        """Путь к YOLO модели"""
        return self.parser.get("NEUROMODEL", "WeightsPath", fallback="models/yolov8n.pt")

    @property
    def yolo_conf_threshold(self) -> float:
        """Порог уверенности для YOLO детекции"""
        return self.parser.getfloat("NEUROMODEL", "ConfThreshold", fallback=0.5)

    @property
    def coco_names_path(self) -> str:
        """Путь к файлу с названиями классов COCO"""
        return self.parser.get("NEUROMODEL", "CocoNamesPath", fallback="data/coco.names")

    # TCP_Servers section
    @property
    def java_server_ip(self) -> str:
        """IP адрес Java сервера"""
        return self.parser.get("TCP_Servers", "IP_Java", fallback="192.168.1.50")

    @property
    def java_server_port(self) -> int:
        """Порт Java сервера"""
        return self.parser.getint("TCP_Servers", "PORT_Java", fallback=2222)

    @property
    def esp_device_ip(self) -> str:
        """IP адрес ESP устройства"""
        return self.parser.get("TCP_Servers", "IP_ESP", fallback="192.168.1.60")

    @property
    def esp_device_port(self) -> int:
        """Порт ESP устройства"""
        return self.parser.getint("TCP_Servers", "PORT_ESP", fallback=44444)

    @property
    def tcp_timeout(self) -> float:
        """Таймаут TCP подключения"""
        return self.parser.getfloat("TCP_Servers", "timeout", fallback=5.0)

    @property
    def tcp_reconnect_delay(self) -> float:
        """Задержка переподключения TCP при неудаче"""
        return self.parser.getfloat("TCP_Servers", "reconnect_delay", fallback=2.0)

    @property
    def udp_send_host(self) -> str:
        """Хост для отправки UDP сообщений"""
        return self.parser.get("UDP", "IP_PythonServer", fallback="127.0.0.1")

    @property
    def tcp_timeout(self) -> float:
        """Таймаут TCP подключения"""
        return self.parser.getfloat("TCP_Servers", "timeout", fallback=5.0)

    @property
    def tcp_reconnect_delay(self) -> float:
        """Задержка переподключения TCP при неудаче"""
        return self.parser.getfloat("TCP_Servers", "reconnect_delay", fallback=2.0)

    @property
    def udp_send_host(self) -> str:
        """Хост для отправки UDP сообщений"""
        return self.parser.get("UDP", "IP_PythonServer", fallback="127.0.0.1")

    # Logging section
    @property
    def log_level(self) -> str:
        """Уровень логирования"""
        return self.parser.get("Logging", "level", fallback="INFO").upper()

    @property
    def log_format(self) -> str:
        """Формат логов"""
        return self.parser.get("Logging", "format",
                              fallback="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @property
    def log_dir(self) -> str:
        """Директория для логов"""
        return self.parser.get("Logging", "log_dir", fallback="logs")

    # GUI section
    @property
    def window_width(self) -> int:
        """Ширина главного окна"""
        return self.parser.getint("GUI", "window_width", fallback=1200)

    @property
    def window_height(self) -> int:
        """Высота главного окна"""
        return self.parser.getint("GUI", "window_height", fallback=800)

    @property
    def fps_target(self) -> int:
        """Целевой FPS для обновления видео"""
        return self.parser.getint("GUI", "fps_target", fallback=30)

    # Laravel section
    @property
    def laravel_sync_enabled(self) -> bool:
        return self.parser.getboolean('Laravel', 'enabled', fallback=False)

    @property
    def laravel_base_url(self) -> str:
        return self.parser.get('Laravel', 'baseUrl', fallback='')

    @property
    def laravel_auditory_name(self) -> str:
        return self.parser.get('Laravel', 'auditoryName', fallback='')

    @property
    def laravel_camera_name(self) -> str:
        return self.parser.get('Laravel', 'cameraName', fallback='')

    @property
    def laravel_camera_address(self) -> str:
        return self.parser.get('Laravel', 'cameraAddress', fallback='')

    @property
    def laravel_camera_port(self) -> int:
        return self.parser.getint('Laravel', 'cameraPort', fallback=0)

    @property
    def laravel_sync_interval_seconds(self) -> float:
        return self.parser.getfloat('Laravel', 'syncIntervalSeconds', fallback=30.0)

    @property
    def laravel_timeout_seconds(self) -> float:
        return self.parser.getfloat('Laravel', 'timeoutSeconds', fallback=5.0)

    def reload(self):
        """Перезагрузить конфигурацию из файла"""
        try:
            self.parser.read(self.config_path, encoding='utf-8')
        except Exception as e:
            raise ValueError(f"Error reloading config file: {e}")

    def get_section(self, section_name: str) -> dict:
        """
        Получить все настройки из секции

        Args:
            section_name: Название секции

        Returns:
            Словарь с настройками секции
        """
        if not self.parser.has_section(section_name):
            return {}

        return dict(self.parser.items(section_name))

    def __str__(self) -> str:
        """Строковое представление конфигурации"""
        return f"Config(file='{self.config_path}')"

    def __repr__(self) -> str:
        """Детальное строковое представление"""
        return f"Config(config_path='{self.config_path}')"