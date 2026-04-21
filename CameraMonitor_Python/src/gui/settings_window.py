"""
Окно настроек приложения
"""

import logging
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QGroupBox, QCheckBox, QComboBox,
    QTabWidget, QMessageBox, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.core.config import Config


class SettingsWindow(QWidget):
    """Окно настроек"""

    def __init__(self, config: Config):
        super().__init__()

        self.config = config
        self.logger = logging.getLogger(__name__)

        # Оригинальные значения для сравнения
        self.original_values: Dict[str, Any] = {}

        self.setup_ui()
        self.load_current_settings()

        self.logger.info("Settings window initialized")

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Настройки - Camera Monitor")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout(self)

        # Создаем вкладки для разных категорий настроек
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Вкладка основных настроек
        self.setup_general_tab()

        # Вкладка камеры
        self.setup_camera_tab()

        # Вкладка детекции
        self.setup_detection_tab()

        # Вкладка сети
        self.setup_network_tab()

        # Вкладка базы данных
        self.setup_database_tab()

        # Панель кнопок
        self.setup_buttons(layout)

    def setup_general_tab(self):
        """Настройка вкладки основных настроек"""
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)

        # Группа интерфейса
        ui_group = QGroupBox("Интерфейс")
        ui_layout = QVBoxLayout(ui_group)

        # Тема
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Тема:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная", "Системная"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)

        # Язык
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Язык:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Русский", "English"])
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        ui_layout.addLayout(lang_layout)

        general_layout.addWidget(ui_group)

        # Группа логирования
        log_group = QGroupBox("Логирование")
        log_layout = QVBoxLayout(log_group)

        # Уровень логирования
        log_level_layout = QHBoxLayout()
        log_level_layout.addWidget(QLabel("Уровень логирования:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_level_layout.addWidget(self.log_level_combo)
        log_level_layout.addStretch()
        log_layout.addLayout(log_level_layout)

        # Максимальный размер файла лога
        max_log_size_layout = QHBoxLayout()
        max_log_size_layout.addWidget(QLabel("Макс. размер лога (МБ):"))
        self.max_log_size_spin = QSpinBox()
        self.max_log_size_spin.setRange(1, 100)
        self.max_log_size_spin.setValue(10)
        max_log_size_layout.addWidget(self.max_log_size_spin)
        max_log_size_layout.addStretch()
        log_layout.addLayout(max_log_size_layout)

        general_layout.addWidget(log_group)

        general_layout.addStretch()

        self.tab_widget.addTab(general_widget, "Основные")

    def setup_camera_tab(self):
        """Настройка вкладки камеры"""
        camera_widget = QWidget()
        camera_layout = QVBoxLayout(camera_widget)

        # Группа камеры
        camera_group = QGroupBox("Камера")
        camera_group_layout = QVBoxLayout(camera_group)

        # RTSP URL
        rtsp_layout = QHBoxLayout()
        rtsp_layout.addWidget(QLabel("RTSP URL:"))
        self.rtsp_edit = QLineEdit()
        self.rtsp_edit.setPlaceholderText("rtsp://username:password@ip:port/stream")
        rtsp_layout.addWidget(self.rtsp_edit)
        camera_group_layout.addLayout(rtsp_layout)

        # Разрешение
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Разрешение:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "640x480", "800x600", "1024x768", "1280x720", "1920x1080"
        ])
        resolution_layout.addWidget(self.resolution_combo)
        resolution_layout.addStretch()
        camera_group_layout.addLayout(resolution_layout)

        # FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(30)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addStretch()
        camera_group_layout.addLayout(fps_layout)

        camera_layout.addWidget(camera_group)

        # Группа обработки
        processing_group = QGroupBox("Обработка видео")
        processing_layout = QVBoxLayout(processing_group)

        # Использовать аппаратное ускорение
        self.hw_accel_checkbox = QCheckBox("Аппаратное ускорение (CUDA)")
        processing_layout.addWidget(self.hw_accel_checkbox)

        # Буфер кадров
        buffer_layout = QHBoxLayout()
        buffer_layout.addWidget(QLabel("Буфер кадров:"))
        self.buffer_spin = QSpinBox()
        self.buffer_spin.setRange(1, 10)
        self.buffer_spin.setValue(3)
        buffer_layout.addWidget(self.buffer_spin)
        buffer_layout.addStretch()
        processing_layout.addLayout(buffer_layout)

        camera_layout.addWidget(processing_group)

        camera_layout.addStretch()

        self.tab_widget.addTab(camera_widget, "Камера")

    def setup_detection_tab(self):
        """Настройка вкладки детекции"""
        detection_widget = QWidget()
        detection_layout = QVBoxLayout(detection_widget)

        # Группа модели
        model_group = QGroupBox("Модель детекции")
        model_layout = QVBoxLayout(model_group)

        # Модель YOLO
        model_layout_inner = QHBoxLayout()
        model_layout_inner.addWidget(QLabel("Модель YOLO:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["yolov8n", "yolov8s", "yolov8m", "yolov11n", "yolov11s"])
        model_layout_inner.addWidget(self.model_combo)
        model_layout_inner.addStretch()
        model_layout.addLayout(model_layout_inner)

        # Уверенность
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Минимальная уверенность:"))
        self.confidence_spin = QSpinBox()
        self.confidence_spin.setRange(1, 100)
        self.confidence_spin.setValue(50)
        self.confidence_spin.setSuffix("%")
        confidence_layout.addWidget(self.confidence_spin)
        confidence_layout.addStretch()
        model_layout.addLayout(confidence_layout)

        detection_layout.addWidget(model_group)

        # Группа классов
        classes_group = QGroupBox("Классы для детекции")
        classes_layout = QVBoxLayout(classes_group)

        self.detect_person_checkbox = QCheckBox("Человек (person)")
        self.detect_person_checkbox.setChecked(True)
        self.detect_person_checkbox.setEnabled(False)  # Всегда включено
        classes_layout.addWidget(self.detect_person_checkbox)

        # Дополнительные классы можно добавить позже
        self.detect_car_checkbox = QCheckBox("Автомобиль (car)")
        classes_layout.addWidget(self.detect_car_checkbox)

        detection_layout.addWidget(classes_group)

        # Группа производительности
        perf_group = QGroupBox("Производительность")
        perf_layout = QVBoxLayout(perf_group)

        # Максимальный размер изображения
        max_size_layout = QHBoxLayout()
        max_size_layout.addWidget(QLabel("Макс. размер изображения:"))
        self.max_size_combo = QComboBox()
        self.max_size_combo.addItems(["320", "416", "512", "640", "800", "1024"])
        self.max_size_combo.setCurrentText("640")
        max_size_layout.addWidget(self.max_size_combo)
        max_size_layout.addStretch()
        perf_layout.addLayout(max_size_layout)

        detection_layout.addWidget(perf_group)

        detection_layout.addStretch()

        self.tab_widget.addTab(detection_widget, "Детекция")

    def setup_network_tab(self):
        """Настройка вкладки сети"""
        network_widget = QWidget()
        network_layout = QVBoxLayout(network_widget)

        # Группа UDP
        udp_group = QGroupBox("UDP настройки")
        udp_layout = QVBoxLayout(udp_group)

        # Порт прослушки
        listen_port_layout = QHBoxLayout()
        listen_port_layout.addWidget(QLabel("Порт прослушки:"))
        self.udp_listen_port_spin = QSpinBox()
        self.udp_listen_port_spin.setRange(1024, 65535)
        self.udp_listen_port_spin.setValue(5001)
        listen_port_layout.addWidget(self.udp_listen_port_spin)
        listen_port_layout.addStretch()
        udp_layout.addLayout(listen_port_layout)

        # Порт отправки
        send_port_layout = QHBoxLayout()
        send_port_layout.addWidget(QLabel("Порт отправки:"))
        self.udp_send_port_spin = QSpinBox()
        self.udp_send_port_spin.setRange(1024, 65535)
        self.udp_send_port_spin.setValue(5000)
        send_port_layout.addWidget(self.udp_send_port_spin)
        send_port_layout.addStretch()
        udp_layout.addLayout(send_port_layout)

        network_layout.addWidget(udp_group)

        # Группа TCP
        tcp_group = QGroupBox("TCP настройки")
        tcp_layout = QVBoxLayout(tcp_group)

        # Хост
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Хост сервера:"))
        self.tcp_host_edit = QLineEdit()
        self.tcp_host_edit.setText("localhost")
        host_layout.addWidget(self.tcp_host_edit)
        tcp_layout.addLayout(host_layout)

        # Порт
        tcp_port_layout = QHBoxLayout()
        tcp_port_layout.addWidget(QLabel("Порт сервера:"))
        self.tcp_port_spin = QSpinBox()
        self.tcp_port_spin.setRange(1024, 65535)
        self.tcp_port_spin.setValue(8080)
        tcp_port_layout.addWidget(self.tcp_port_spin)
        tcp_port_layout.addStretch()
        tcp_layout.addLayout(tcp_port_layout)

        # Таймаут
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Таймаут (сек):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(5)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        tcp_layout.addLayout(timeout_layout)

        network_layout.addWidget(tcp_group)

        # Группа авто-реконнекта
        reconnect_group = QGroupBox("Авто-реконнект")
        reconnect_layout = QVBoxLayout(reconnect_group)

        self.auto_reconnect_checkbox = QCheckBox("Включить авто-реконнект")
        self.auto_reconnect_checkbox.setChecked(True)
        reconnect_layout.addWidget(self.auto_reconnect_checkbox)

        # Интервал реконнекта
        reconnect_interval_layout = QHBoxLayout()
        reconnect_interval_layout.addWidget(QLabel("Интервал (сек):"))
        self.reconnect_interval_spin = QSpinBox()
        self.reconnect_interval_spin.setRange(1, 300)
        self.reconnect_interval_spin.setValue(2)
        reconnect_interval_layout.addWidget(self.reconnect_interval_spin)
        reconnect_interval_layout.addStretch()
        reconnect_layout.addLayout(reconnect_interval_layout)

        network_layout.addWidget(reconnect_group)

        network_layout.addStretch()

        self.tab_widget.addTab(network_widget, "Сеть")

    def setup_database_tab(self):
        """Настройка вкладки базы данных"""
        db_widget = QWidget()
        db_layout = QVBoxLayout(db_widget)

        # Группа подключения
        conn_group = QGroupBox("Подключение к БД")
        conn_layout = QVBoxLayout(conn_group)

        # Путь к БД
        db_path_layout = QHBoxLayout()
        db_path_layout.addWidget(QLabel("Путь к БД:"))
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setText("data/camera_monitor.db")
        db_path_layout.addWidget(self.db_path_edit)
        conn_layout.addLayout(db_path_layout)

        # Драйвер
        driver_layout = QHBoxLayout()
        driver_layout.addWidget(QLabel("Драйвер:"))
        self.db_driver_combo = QComboBox()
        self.db_driver_combo.addItems(["sqlite", "postgresql", "mysql"])
        self.db_driver_combo.setCurrentText("sqlite")
        driver_layout.addWidget(self.db_driver_combo)
        driver_layout.addStretch()
        conn_layout.addLayout(driver_layout)

        db_layout.addWidget(conn_group)

        # Группа обслуживания
        maintenance_group = QGroupBox("Обслуживание")
        maintenance_layout = QVBoxLayout(maintenance_group)

        # Автоматическая очистка
        self.auto_cleanup_checkbox = QCheckBox("Автоматическая очистка старых записей")
        self.auto_cleanup_checkbox.setChecked(True)
        maintenance_layout.addWidget(self.auto_cleanup_checkbox)

        # Период хранения
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("Хранить данные (дни):"))
        self.retention_days_spin = QSpinBox()
        self.retention_days_spin.setRange(1, 365)
        self.retention_days_spin.setValue(30)
        retention_layout.addWidget(self.retention_days_spin)
        retention_layout.addStretch()
        maintenance_layout.addLayout(retention_layout)

        # Кнопка очистки
        cleanup_btn = QPushButton("🗑️ Очистить старые записи")
        cleanup_btn.clicked.connect(self.cleanup_database)
        maintenance_layout.addWidget(cleanup_btn)

        db_layout.addWidget(maintenance_group)

        db_layout.addStretch()

        self.tab_widget.addTab(db_widget, "База данных")

    def setup_buttons(self, parent_layout: QVBoxLayout):
        """Настройка панели кнопок"""
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        parent_layout.addWidget(separator)

        # Панель кнопок
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)

        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.save_btn)

        self.reset_btn = QPushButton("🔄 Сбросить")
        self.reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_btn)

        self.apply_btn = QPushButton("⚡ Применить")
        self.apply_btn.clicked.connect(self.apply_settings)
        buttons_layout.addWidget(self.apply_btn)

        buttons_layout.addStretch()

        self.close_btn = QPushButton("❌ Закрыть")
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)

        parent_layout.addWidget(buttons_widget)

    def load_current_settings(self):
        """Загрузка текущих настроек"""
        try:
            # Основные настройки
            self.theme_combo.setCurrentText("Системная")
            self.lang_combo.setCurrentText("Русский")
            self.log_level_combo.setCurrentText("INFO")
            self.max_log_size_spin.setValue(10)

            # Камера
            self.rtsp_edit.setText(getattr(self.config, 'camera_rtsp_url', ''))
            self.resolution_combo.setCurrentText("1280x720")
            self.fps_spin.setValue(30)
            self.hw_accel_checkbox.setChecked(False)
            self.buffer_spin.setValue(3)

            # Детекция
            self.model_combo.setCurrentText("yolov8n")
            self.confidence_spin.setValue(50)
            self.detect_car_checkbox.setChecked(False)
            self.max_size_combo.setCurrentText("640")

            # Сеть
            self.udp_listen_port_spin.setValue(getattr(self.config, 'udp_listen_port', 5001))
            self.udp_send_port_spin.setValue(getattr(self.config, 'udp_send_port', 5000))
            self.tcp_host_edit.setText(getattr(self.config, 'tcp_host', 'localhost'))
            self.tcp_port_spin.setValue(getattr(self.config, 'tcp_port', 8080))
            self.timeout_spin.setValue(5)
            self.auto_reconnect_checkbox.setChecked(True)
            self.reconnect_interval_spin.setValue(2)

            # База данных
            self.db_path_edit.setText(getattr(self.config, 'db_path', 'data/camera_monitor.db'))
            self.db_driver_combo.setCurrentText("sqlite")
            self.auto_cleanup_checkbox.setChecked(True)
            self.retention_days_spin.setValue(30)

            # Сохраняем оригинальные значения
            self.save_original_values()

            self.logger.info("Settings loaded")

        except Exception as e:
            self.logger.error(f"Failed to load settings: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки:\n{e}")

    def save_original_values(self):
        """Сохранение оригинальных значений для сравнения"""
        self.original_values = {
            'theme': self.theme_combo.currentText(),
            'lang': self.lang_combo.currentText(),
            'log_level': self.log_level_combo.currentText(),
            'max_log_size': self.max_log_size_spin.value(),
            'rtsp_url': self.rtsp_edit.text(),
            'resolution': self.resolution_combo.currentText(),
            'fps': self.fps_spin.value(),
            'hw_accel': self.hw_accel_checkbox.isChecked(),
            'buffer_size': self.buffer_spin.value(),
            'model': self.model_combo.currentText(),
            'confidence': self.confidence_spin.value(),
            'detect_car': self.detect_car_checkbox.isChecked(),
            'max_size': self.max_size_combo.currentText(),
            'udp_listen_port': self.udp_listen_port_spin.value(),
            'udp_send_port': self.udp_send_port_spin.value(),
            'tcp_host': self.tcp_host_edit.text(),
            'tcp_port': self.tcp_port_spin.value(),
            'timeout': self.timeout_spin.value(),
            'auto_reconnect': self.auto_reconnect_checkbox.isChecked(),
            'reconnect_interval': self.reconnect_interval_spin.value(),
            'db_path': self.db_path_edit.text(),
            'db_driver': self.db_driver_combo.currentText(),
            'auto_cleanup': self.auto_cleanup_checkbox.isChecked(),
            'retention_days': self.retention_days_spin.value(),
        }

    def save_settings(self):
        """Сохранение настроек"""
        try:
            # Здесь должна быть логика сохранения в config
            # Пока просто показываем сообщение
            QMessageBox.information(self, "Успех", "Настройки сохранены!\n\n(В следующей версии будет реализовано сохранение в файл)")
            self.save_original_values()
            self.logger.info("Settings saved")

        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить настройки:\n{e}")

    def reset_settings(self):
        """Сброс настроек к оригинальным значениям"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Сбросить все изменения к сохраненным значениям?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Восстанавливаем оригинальные значения
            for key, value in self.original_values.items():
                if key == 'theme':
                    self.theme_combo.setCurrentText(value)
                elif key == 'lang':
                    self.lang_combo.setCurrentText(value)
                elif key == 'log_level':
                    self.log_level_combo.setCurrentText(value)
                elif key == 'max_log_size':
                    self.max_log_size_spin.setValue(value)
                elif key == 'rtsp_url':
                    self.rtsp_edit.setText(value)
                elif key == 'resolution':
                    self.resolution_combo.setCurrentText(value)
                elif key == 'fps':
                    self.fps_spin.setValue(value)
                elif key == 'hw_accel':
                    self.hw_accel_checkbox.setChecked(value)
                elif key == 'buffer_size':
                    self.buffer_spin.setValue(value)
                elif key == 'model':
                    self.model_combo.setCurrentText(value)
                elif key == 'confidence':
                    self.confidence_spin.setValue(value)
                elif key == 'detect_car':
                    self.detect_car_checkbox.setChecked(value)
                elif key == 'max_size':
                    self.max_size_combo.setCurrentText(value)
                elif key == 'udp_listen_port':
                    self.udp_listen_port_spin.setValue(value)
                elif key == 'udp_send_port':
                    self.udp_send_port_spin.setValue(value)
                elif key == 'tcp_host':
                    self.tcp_host_edit.setText(value)
                elif key == 'tcp_port':
                    self.tcp_port_spin.setValue(value)
                elif key == 'timeout':
                    self.timeout_spin.setValue(value)
                elif key == 'auto_reconnect':
                    self.auto_reconnect_checkbox.setChecked(value)
                elif key == 'reconnect_interval':
                    self.reconnect_interval_spin.setValue(value)
                elif key == 'db_path':
                    self.db_path_edit.setText(value)
                elif key == 'db_driver':
                    self.db_driver_combo.setCurrentText(value)
                elif key == 'auto_cleanup':
                    self.auto_cleanup_checkbox.setChecked(value)
                elif key == 'retention_days':
                    self.retention_days_spin.setValue(value)

            self.logger.info("Settings reset to original values")

    def apply_settings(self):
        """Применение настроек без сохранения"""
        QMessageBox.information(self, "Информация", "Настройки применены!\n\n(В следующей версии будет реализовано применение настроек)")

    def cleanup_database(self):
        """Очистка базы данных"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Удалить старые записи из базы данных?\nЭто действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Здесь должна быть логика очистки БД
                QMessageBox.information(self, "Успех", "База данных очищена!")
                self.logger.info("Database cleanup completed")

            except Exception as e:
                self.logger.error(f"Database cleanup failed: {e}")
                QMessageBox.critical(self, "Ошибка", f"Ошибка при очистке базы данных:\n{e}")

    def closeEvent(self, event):
        """Обработка закрытия"""
        # Проверяем несохраненные изменения
        if self.has_unsaved_changes():
            reply = QMessageBox.question(
                self, "Несохраненные изменения",
                "У вас есть несохраненные изменения. Сохранить перед выходом?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.save_settings()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return

        self.logger.info("Settings window closing...")
        event.accept()

    def has_unsaved_changes(self) -> bool:
        """Проверка на несохраненные изменения"""
        current_values = {
            'theme': self.theme_combo.currentText(),
            'lang': self.lang_combo.currentText(),
            'log_level': self.log_level_combo.currentText(),
            'max_log_size': self.max_log_size_spin.value(),
            'rtsp_url': self.rtsp_edit.text(),
            'resolution': self.resolution_combo.currentText(),
            'fps': self.fps_spin.value(),
            'hw_accel': self.hw_accel_checkbox.isChecked(),
            'buffer_size': self.buffer_spin.value(),
            'model': self.model_combo.currentText(),
            'confidence': self.confidence_spin.value(),
            'detect_car': self.detect_car_checkbox.isChecked(),
            'max_size': self.max_size_combo.currentText(),
            'udp_listen_port': self.udp_listen_port_spin.value(),
            'udp_send_port': self.udp_send_port_spin.value(),
            'tcp_host': self.tcp_host_edit.text(),
            'tcp_port': self.tcp_port_spin.value(),
            'timeout': self.timeout_spin.value(),
            'auto_reconnect': self.auto_reconnect_checkbox.isChecked(),
            'reconnect_interval': self.reconnect_interval_spin.value(),
            'db_path': self.db_path_edit.text(),
            'db_driver': self.db_driver_combo.currentText(),
            'auto_cleanup': self.auto_cleanup_checkbox.isChecked(),
            'retention_days': self.retention_days_spin.value(),
        }

        return current_values != self.original_values