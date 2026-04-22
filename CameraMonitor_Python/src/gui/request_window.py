"""
Окно поиска свободных кабинетов
"""

import logging
from datetime import datetime, time
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QTimeEdit, QGroupBox, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from src.core.config import Config
from src.core.network import NetworkManager
from src.core.database import DatabaseManager


class RequestWindow(QWidget):
    """Окно поиска кабинетов"""

    def __init__(self, config: Config, network_manager: NetworkManager, db_manager: DatabaseManager):
        super().__init__()

        self.config = config
        self.network_manager = network_manager
        self.db_manager = db_manager

        self.logger = logging.getLogger(__name__)

        # Данные
        self.current_results: Optional[Dict[str, Any]] = None
        self.search_history = []

        self.setup_ui()
        self.setup_connections()
        self.load_room_list()

        self.logger.info("Request window initialized")

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Создаем разделитель
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Верхняя панель - форма поиска
        self.setup_search_panel(splitter)

        # Нижняя панель - результаты
        self.setup_results_panel(splitter)

        # Устанавливаем пропорции
        splitter.setSizes([300, 400])

    def setup_search_panel(self, parent: QSplitter):
        """Настройка панели поиска"""
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)

        # Группа параметров поиска
        search_group = QGroupBox("Параметры поиска")
        search_form_layout = QVBoxLayout(search_group)

        # Выбор кабинета
        room_layout = QHBoxLayout()
        room_layout.addWidget(QLabel("Кабинет:"))

        self.room_combo = QComboBox()
        self.room_combo.addItem("Выберите кабинет...", "")
        room_layout.addWidget(self.room_combo)
        search_form_layout.addLayout(room_layout)

        # Дата и время
        datetime_layout = QHBoxLayout()

        # Дата
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Дата:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        datetime_layout.addLayout(date_layout)

        # Время начала
        time_start_layout = QVBoxLayout()
        time_start_layout.addWidget(QLabel("Время начала:"))
        self.time_start_edit = QTimeEdit()
        self.time_start_edit.setTime(QTime(9, 0))  # 9:00
        time_start_layout.addWidget(self.time_start_edit)
        datetime_layout.addLayout(time_start_layout)

        # Время окончания
        time_end_layout = QVBoxLayout()
        time_end_layout.addWidget(QLabel("Время окончания:"))
        self.time_end_edit = QTimeEdit()
        self.time_end_edit.setTime(QTime(10, 0))  # 10:00
        time_end_layout.addWidget(self.time_end_edit)
        datetime_layout.addLayout(time_end_layout)

        search_form_layout.addLayout(datetime_layout)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.search_btn = QPushButton("🔍 Найти")
        self.search_btn.clicked.connect(self.perform_search)
        self.search_btn.setStyleSheet("""
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
        buttons_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("🗑️ Очистить")
        self.clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_btn)

        buttons_layout.addStretch()
        search_form_layout.addLayout(buttons_layout)

        search_layout.addWidget(search_group)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        search_layout.addWidget(self.progress_bar)

        parent.addWidget(search_widget)

    def setup_results_panel(self, parent: QSplitter):
        """Настройка панели результатов"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        # Группа результатов
        results_group = QGroupBox("Результаты поиска")
        results_content_layout = QVBoxLayout(results_group)

        # Таблица результатов
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "Кабинет", "Статус", "Время", "Информация"
        ])

        # Настройка таблицы
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        results_content_layout.addWidget(self.results_table)

        # Детальная информация
        details_layout = QHBoxLayout()

        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setPlaceholderText("Детальная информация о выбранном кабинете...")
        details_layout.addWidget(self.details_text)

        # Кнопки действий
        actions_layout = QVBoxLayout()

        self.book_btn = QPushButton("📅 Забронировать")
        self.book_btn.clicked.connect(self.book_room)
        self.book_btn.setEnabled(False)
        actions_layout.addWidget(self.book_btn)

        self.refresh_btn = QPushButton("🔄 Обновить")
        self.refresh_btn.clicked.connect(self.refresh_results)
        actions_layout.addWidget(self.refresh_btn)

        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)

        results_content_layout.addLayout(details_layout)

        results_layout.addWidget(results_group)

        parent.addWidget(results_widget)

    def setup_connections(self):
        """Настройка соединений"""
        # Подключаем выбор строки в таблице
        self.results_table.itemSelectionChanged.connect(self.on_result_selected)

        # Таймер для автоматического обновления
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_refresh)
        self.update_timer.start(30000)  # Каждые 30 секунд

    def load_room_list(self):
        try:
            import requests
            base_url = self.config.parser.get('Laravel', 'baseUrl', fallback='http://127.0.0.1:3333/api')
            response = requests.get(f"{base_url}/schedule/auditories", timeout=5)
            response.raise_for_status()
            rooms = response.json()

            self.room_combo.clear()
            self.room_combo.addItem("Выберите кабинет...", "")

            for room in rooms:
                room_id = room.get('id', '')
                room_name = room.get('name', f'Кабинет {room_id}')
                self.room_combo.addItem(room_name, room_id)

            self.logger.info(f"Loaded {len(rooms)} rooms")

        except Exception as e:
            self.logger.error(f"Failed to load rooms: {e}")

    def perform_search(self):
        """Выполнение поиска"""
        try:
            # Получаем параметры
            room_id = self.room_combo.currentData()
            if not room_id:
                QMessageBox.warning(self, "Ошибка", "Выберите кабинет для поиска")
                return

            date = self.date_edit.date().toPyDate()
            time_start = self.time_start_edit.time().toPyTime()
            time_end = self.time_end_edit.time().toPyTime()

            # Проверяем корректность времени
            if time_start >= time_end:
                QMessageBox.warning(self, "Ошибка", "Время окончания должно быть позже времени начала")
                return

            # Формируем строку времени
            time_range = f"{time_start.strftime('%H:%M')}-{time_end.strftime('%H:%M')}"

            self.logger.info(f"Searching room {room_id} for {date} {time_range}")

            # Показываем прогресс
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Неопределенный прогресс
            self.search_btn.setEnabled(False)

            # Отправляем запрос
            result = self.network_manager.request_room_info(room_id, time_range)

            # Скрываем прогресс
            self.progress_bar.setVisible(False)
            self.search_btn.setEnabled(True)

            if result:
                self.display_results(result, room_id, time_range)
                self.add_to_history(room_id, time_range, result)
            else:
                QMessageBox.information(self, "Результат", "Не удалось получить информацию о кабинете")

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.search_btn.setEnabled(True)
            self.logger.error(f"Search failed: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при выполнении поиска:\n{e}")

    def display_results(self, result: Dict[str, Any], room_id: str, time_range: str):
        """Отображение результатов поиска"""
        try:
            self.results_table.setRowCount(0)  # Очищаем таблицу

            # Добавляем результат
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            # Кабинет
            room_name = self.room_combo.currentText()
            self.results_table.setItem(row, 0, QTableWidgetItem(room_name))

            # Статус
            status = result.get('status', 'unknown')
            available = result.get('available', False)

            if available:
                status_text = "Свободен"
                status_color = QColor(0, 128, 0)  # Зеленый
            else:
                status_text = "Занят"
                status_color = QColor(128, 0, 0)  # Красный

            status_item = QTableWidgetItem(status_text)
            status_item.setBackground(status_color)
            status_item.setForeground(QColor(255, 255, 255))
            self.results_table.setItem(row, 1, status_item)

            # Время
            self.results_table.setItem(row, 2, QTableWidgetItem(time_range))

            # Информация
            info_parts = []
            if result.get('occupant'):
                info_parts.append(f"Занят: {result['occupant']}")
            if result.get('purpose'):
                info_parts.append(f"Цель: {result['purpose']}")

            info_text = " | ".join(info_parts) if info_parts else "Нет информации"
            self.results_table.setItem(row, 3, QTableWidgetItem(info_text))

            # Сохраняем результат
            self.current_results = result

            # Выделяем первую строку
            self.results_table.selectRow(0)

            self.logger.info(f"Displayed search results for room {room_id}")

        except Exception as e:
            self.logger.error(f"Failed to display results: {e}")

    def on_result_selected(self):
        """Обработка выбора результата"""
        try:
            current_row = self.results_table.currentRow()
            if current_row >= 0 and self.current_results:
                # Формируем детальную информацию
                details = []

                room_name = self.results_table.item(current_row, 0).text()
                status = self.results_table.item(current_row, 1).text()
                time_range = self.results_table.item(current_row, 2).text()

                details.append(f"Кабинет: {room_name}")
                details.append(f"Статус: {status}")
                details.append(f"Время: {time_range}")

                if self.current_results.get('occupant'):
                    details.append(f"Занят: {self.current_results['occupant']}")

                if self.current_results.get('purpose'):
                    details.append(f"Цель использования: {self.current_results['purpose']}")

                if self.current_results.get('contact'):
                    details.append(f"Контакт: {self.current_results['contact']}")

                # Обновляем доступность кнопки бронирования
                available = self.current_results.get('available', False)
                self.book_btn.setEnabled(available)

                self.details_text.setPlainText("\n".join(details))

        except Exception as e:
            self.logger.error(f"Error handling result selection: {e}")

    def book_room(self):
        """Бронирование кабинета"""
        try:
            if not self.current_results:
                return

            room_name = self.room_combo.currentText()
            time_range = f"{self.time_start_edit.time().toPyTime().strftime('%H:%M')}-{self.time_end_edit.time().toPyTime().strftime('%H:%M')}"

            reply = QMessageBox.question(
                self, "Подтверждение бронирования",
                f"Забронировать кабинет '{room_name}' на время {time_range}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Здесь должна быть логика бронирования
                QMessageBox.information(self, "Успех", "Кабинет успешно забронирован!")
                self.logger.info(f"Room {room_name} booked for {time_range}")

        except Exception as e:
            self.logger.error(f"Booking failed: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при бронировании:\n{e}")

    def refresh_results(self):
        """Обновление результатов"""
        if self.room_combo.currentData():
            self.perform_search()

    def auto_refresh(self):
        """Автоматическое обновление"""
        # Обновляем только если есть активный поиск
        if self.current_results and self.room_combo.currentData():
            self.refresh_results()

    def clear_form(self):
        """Очистка формы"""
        self.room_combo.setCurrentIndex(0)
        self.date_edit.setDate(QDate.currentDate())
        self.time_start_edit.setTime(QTime(9, 0))
        self.time_end_edit.setTime(QTime(10, 0))
        self.results_table.setRowCount(0)
        self.details_text.clear()
        self.current_results = None
        self.book_btn.setEnabled(False)

    def add_to_history(self, room_id: str, time_range: str, result: Dict[str, Any]):
        """Добавление в историю поиска"""
        self.search_history.append({
            'room_id': room_id,
            'time_range': time_range,
            'result': result,
            'timestamp': datetime.now()
        })

        # Ограничиваем историю 10 записями
        if len(self.search_history) > 10:
            self.search_history.pop(0)

    def closeEvent(self, event):
        """Обработка закрытия"""
        self.logger.info("Request window closing...")
        self.update_timer.stop()
        event.accept()