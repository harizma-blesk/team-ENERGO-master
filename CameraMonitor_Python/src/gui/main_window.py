"""
Главное окно приложения Camera Monitor
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QStatusBar, QMenuBar, QSplitter, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QFont, QPalette, QColor

from src.core.config import Config
from src.core.database import DatabaseManager
from src.core.camera import CameraManager
from src.core.detector import PersonDetector
from src.core.network import NetworkManager

from src.gui.camera_window import CameraWindow
from src.gui.request_window import RequestWindow
from src.gui.settings_window import SettingsWindow


class StatusUpdateThread(QThread):
    """Поток для обновления статуса в фоне"""

    status_updated = pyqtSignal(str, str)  # (component, status)

    def __init__(self, camera_manager: CameraManager, network_manager: NetworkManager):
        super().__init__()
        self.camera_manager = camera_manager
        self.network_manager = network_manager
        self.running = True

    def run(self):
        """Основной цикл обновления статуса"""
        while self.running:
            try:
                # Обновляем статус камеры
                if self.camera_manager.is_camera_active():
                    camera_status = f"Камера активна ({self.camera_manager.get_stats()['current_current_fps']:.1f} FPS)"
                else:
                    camera_status = "Камера не активна"

                self.status_updated.emit("camera", camera_status)

                # Обновляем статус сети
                if hasattr(self.network_manager, 'tcp_client') and self.network_manager.tcp_client.connected:
                    network_status = "Сеть: подключено"
                else:
                    network_status = "Сеть: ожидание подключения"

                self.status_updated.emit("network", network_status)

            except Exception as e:
                logging.error(f"Error updating status: {e}")

            self.sleep(2)  # Обновление каждые 2 секунды

    def stop(self):
        """Остановка потока"""
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self,
                 config: Config,
                 db_manager: DatabaseManager,
                 camera_manager: CameraManager,
                 detector: PersonDetector,
                 network_manager: NetworkManager):
        super().__init__()

        self.config = config
        self.db_manager = db_manager
        self.camera_manager = camera_manager
        self.detector = detector
        self.network_manager = network_manager

        self.logger = logging.getLogger(__name__)

        # Инициализация компонентов
        self.status_thread: Optional[StatusUpdateThread] = None

        # Настройка UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_connections()

        # Запуск обновления статуса
        self.start_status_updates()

        self.logger.info("Main window initialized")

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Camera Monitor - Python")
        self.setMinimumSize(1200, 800)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        layout = QVBoxLayout(central_widget)

        # Создаем вкладки
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Вкладка камеры
        self.camera_window = CameraWindow(
            self.config, self.camera_manager, self.detector, self.db_manager
        )
        self.tab_widget.addTab(self.camera_window, "📹 Камера")

        # Вкладка запросов
        self.request_window = RequestWindow(
            self.config, self.network_manager, self.db_manager
        )
        self.tab_widget.addTab(self.request_window, "🔍 Поиск кабинетов")

        # Вкладка настроек
        self.settings_window = SettingsWindow(self.config)
        self.tab_widget.addTab(self.settings_window, "⚙️ Настройки")

        # Панель быстрого доступа
        self.setup_quick_actions(layout)

    def setup_quick_actions(self, parent_layout: QVBoxLayout):
        """Настройка панели быстрых действий"""
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        parent_layout.addWidget(separator)

        # Панель быстрых действий
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)

        # Кнопка запуска камеры
        self.start_camera_btn = QPushButton("▶️ Запустить камеру")
        self.start_camera_btn.clicked.connect(self.start_camera)
        actions_layout.addWidget(self.start_camera_btn)

        # Кнопка остановки камеры
        self.stop_camera_btn = QPushButton("⏹️ Остановить камеру")
        self.stop_camera_btn.clicked.connect(self.stop_camera)
        self.stop_camera_btn.setEnabled(False)
        actions_layout.addWidget(self.stop_camera_btn)

        # Кнопка поиска кабинетов
        self.search_btn = QPushButton("🔍 Найти кабинет")
        self.search_btn.clicked.connect(self.show_request_window)
        actions_layout.addWidget(self.search_btn)

        # Добавляем растяжку
        actions_layout.addStretch()

        # Метка статуса
        self.status_label = QLabel("Готов к работе")
        self.status_label.setStyleSheet("font-weight: bold; color: green;")
        actions_layout.addWidget(self.status_label)

        parent_layout.addWidget(actions_widget)

    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Вид
        view_menu = menubar.addMenu("Вид")

        toggle_fullscreen = QAction("Полноэкранный режим", self)
        toggle_fullscreen.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(toggle_fullscreen)

        # Меню Инструменты
        tools_menu = menubar.addMenu("Инструменты")

        refresh_action = QAction("Обновить", self)
        refresh_action.triggered.connect(self.refresh_all)
        tools_menu.addAction(refresh_action)

        # Меню Справка
        help_menu = menubar.addMenu("Справка")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Настройка строки состояния"""
        self.status_bar = self.statusBar()

        # Статус камеры
        self.camera_status_label = QLabel("Камера: не активна")
        self.status_bar.addWidget(self.camera_status_label)

        # Статус сети
        self.network_status_label = QLabel("Сеть: ожидание")
        self.status_bar.addWidget(self.network_status_label)

        # Статус БД
        self.db_status_label = QLabel("БД: подключено")
        self.status_bar.addWidget(self.db_status_label)

        # Добавляем постоянное сообщение
        self.status_bar.showMessage("Camera Monitor готов к работе", 3000)

    def setup_connections(self):
        """Настройка сигналов и слотов"""
        # Подключаем обновление статуса
        if self.status_thread:
            self.status_thread.status_updated.connect(self.update_status)

    def start_status_updates(self):
        """Запуск обновления статуса"""
        self.status_thread = StatusUpdateThread(self.camera_manager, self.network_manager)
        self.status_thread.status_updated.connect(self.update_status)
        self.status_thread.start()

    def update_status(self, component: str, status: str):
        """Обновление статуса компонента"""
        if component == "camera":
            self.camera_status_label.setText(f"Камера: {status}")
            # Обновляем кнопки
            is_active = "активна" in status
            self.start_camera_btn.setEnabled(not is_active)
            self.stop_camera_btn.setEnabled(is_active)

        elif component == "network":
            self.network_status_label.setText(status)

    def start_camera(self):
        """Запуск камеры"""
        try:
            self.camera_manager.start
            self.status_label.setText("Камера запущена")
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
            self.logger.info("Camera started from GUI")
        except Exception as e:
            self.status_label.setText(f"Ошибка запуска камеры: {e}")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            self.logger.error(f"Failed to start camera: {e}")

    def stop_camera(self):
        """Остановка камеры"""
        try:
            self.camera_manager.stop
            self.status_label.setText("Камера остановлена")
            self.status_label.setStyleSheet("font-weight: bold; color: orange;")
            self.logger.info("Camera stopped from GUI")
        except Exception as e:
            self.status_label.setText(f"Ошибка остановки камеры: {e}")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            self.logger.error(f"Failed to stop camera: {e}")

    def show_request_window(self):
        """Показать окно запроса кабинетов"""
        self.tab_widget.setCurrentWidget(self.request_window)

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def refresh_all(self):
        """Обновить все компоненты"""
        try:
            # Обновляем конфигурацию
            self.config.reload()

            # Обновляем статус
            self.status_label.setText("Обновлено")
            self.status_label.setStyleSheet("font-weight: bold; color: blue;")

            # Сбрасываем через 2 секунды
            QTimer.singleShot(2000, lambda: self.status_label.setText("Готов к работе"))

            self.logger.info("All components refreshed")

        except Exception as e:
            self.status_label.setText(f"Ошибка обновления: {e}")
            self.status_label.setStyleSheet("font-weight: bold; color: red;")
            self.logger.error(f"Failed to refresh: {e}")

    def show_about(self):
        """Показать информацию о программе"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            "О программе",
            "Camera Monitor Python v1.0.0\n\n"
            "Система мониторинга кабинетов с компьютерным зрением.\n"
            "Переведено с C++/Qt на Python.\n\n"
            "© 2024 Camera Monitor Team"
        )

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.logger.info("Main window closing...")

        # Останавливаем поток статуса
        if self.status_thread:
            self.status_thread.stop()

        # Останавливаем камеру
        try:
            self.camera_manager.stop_all_cameras()
        except Exception as e:
            self.logger.error(f"Error stopping cameras: {e}")

        # Останавливаем сеть
        try:
            self.network_manager.stop()
        except Exception as e:
            self.logger.error(f"Error stopping network: {e}")

        event.accept()
        self.logger.info("Main window closed")