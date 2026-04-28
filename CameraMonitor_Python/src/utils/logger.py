"""
Система логирования для Camera Monitor
Использует стандартный logging модуль Python с ротацией файлов
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logger(name: str, log_dir: str = "logs", level: str = "INFO",
                 log_format: Optional[str] = None, max_bytes: int = 10485760,
                 backup_count: int = 5) -> logging.Logger:

    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Если LoggerManager уже есть — просто возвращаем логгер
    if get_logger_manager() is not None:
        return logger

    # Если уже есть handlers — не добавляем
    if logger.handlers:
        return logger

    # Fallback — только если нет LoggerManager
    formatter = logging.Formatter(log_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False  # ← важно: отключаем propagate в fallback

    return logger

class LoggerManager:
    """
    Менеджер логирования для всего приложения

    Управляет настройкой логгеров для разных компонентов
    """

    def __init__(self, config):
        """
        Инициализация менеджера логирования

        Args:
            config: Объект конфигурации (src.core.config.Config)
        """
        self.config = config
        self.loggers = {}

        # Настраиваем корневой логгер
        self._setup_root_logger()

    def _setup_root_logger(self):
        """Настройка корневого логгера"""
        root_logger = logging.getLogger()

        # Очищаем существующие handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Устанавливаем уровень
        level = getattr(logging, self.config.log_level.upper(), logging.INFO)
        root_logger.setLevel(level)

        formatter = logging.Formatter(self.config.log_format)

        # File handler
        log_dir = Path(self.config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "camera_monitor.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        # Console handler — ТОЛЬКО ОДИН
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

    # Отключаем propagate у всех существующих логгеров
    for name, logger in logging.Logger.manager.loggerDict.items():
        if isinstance(logger, logging.Logger):
            logger.propagate = True
            # Убираем все handlers у дочерних логгеров
            # чтобы они не дублировали вывод
            logger.handlers.clear()

    def get_logger(self, name: str) -> logging.Logger:
        """
        Получить логгер для компонента

        Args:
            name: Имя компонента (например, 'core.camera', 'gui.main_window')

        Returns:
            Настроенный логгер
        """
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger

        return self.loggers[name]

    def set_level(self, level: str):
        """
        Изменить уровень логирования для всех логгеров

        Args:
            level: Новый уровень (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)

        # Обновляем корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)

        # Обновляем все handlers корневого логгера
        for handler in root_logger.handlers:
            handler.setLevel(numeric_level)

        # Обновляем кэшированные логгеры
        for logger in self.loggers.values():
            logger.setLevel(numeric_level)

    def cleanup_old_logs(self, days: int = 30):
        """
        Очистить старые файлы логов

        Args:
            days: Количество дней для хранения логов
        """
        import time
        import os

        log_dir = Path(self.config.log_dir)
        if not log_dir.exists():
            return

        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)

        deleted_count = 0
        for log_file in log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    deleted_count += 1
                except OSError:
                    pass  # Игнорируем ошибки удаления

        if deleted_count > 0:
            logger = self.get_logger(__name__)
            logger.info(f"Cleaned up {deleted_count} old log files")


# Глобальный менеджер логирования
_logger_manager = None


def get_logger_manager(config=None):
    """
    Получить глобальный менеджер логирования

    Args:
        config: Объект конфигурации (если None, используется глобальный)

    Returns:
        LoggerManager instance
    """
    global _logger_manager
    if _logger_manager is None and config is not None:
        _logger_manager = LoggerManager(config)
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """
    Получить логгер для компонента

    Args:
        name: Имя компонента

    Returns:
        Логгер
    """
    manager = get_logger_manager()
    if manager:
        return manager.get_logger(name)
    else:
        # Fallback: создаем базовый логгер
        return setup_logger(name)


# Удобные функции для логирования
def log_info(message: str, component: str = "app"):
    """Логировать информационное сообщение"""
    get_logger(component).info(message)


def log_warning(message: str, component: str = "app"):
    """Логировать предупреждение"""
    get_logger(component).warning(message)


def log_error(message: str, component: str = "app"):
    """Логировать ошибку"""
    get_logger(component).error(message)


def log_debug(message: str, component: str = "app"):
    """Логировать отладочное сообщение"""
    get_logger(component).debug(message)


def log_exception(e: Exception, component: str = "app"):
    """Логировать исключение с traceback"""
    get_logger(component).exception(f"Exception occurred: {e}")


# Performance logging decorator
def log_performance(func):
    """
    Декоратор для логирования времени выполнения функции

    Usage:
        @log_performance
        def my_function():
            pass
    """
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()

        logger = get_logger(func.__module__)
        logger.debug(f"Starting {func.__name__}")

        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.debug(f"Completed {func.__name__} in {duration:.4f}s")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"Failed {func.__name__} in {duration:.4f}s: {e}")
            raise

    return wrapper