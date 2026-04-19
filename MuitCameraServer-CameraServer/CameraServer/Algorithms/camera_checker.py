import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from database_manager.models import CameraCabJournalNote

class CameraChecker(QObject):
    dataUpdated = pyqtSignal(object)  # CameraProcessPacket
    peopleCount = pyqtSignal()

    def __init__(self, settings_file, database_manager, parent=None):
        super().__init__(parent)
        self.database = database_manager
        self.settings = settings_file
        self.camera_list = []
        self.current_index = 0
        self.step_timer = QTimer(self)
        self.step_timer.timeout.connect(self.process_next_camera)
        self.step_timer.setSingleShot(True)
        self.camera_thread = None
        self.camera_worker = None

    def start_monitoring(self):
        self.camera_list = self.database.get_notes(CameraCabJournalNote)
        if not self.camera_list:
            print("[CAMERACHECKER] Camera list is empty, retrying in 5 seconds")
            QTimer.singleShot(5000, self.start_monitoring)
            return
        print(f"[CAMERACHECKER] Loaded {len(self.camera_list)} cameras for monitoring")
        self.current_index = 0
        self.process_next_camera()

    def process_next_camera(self):
        if not self.camera_list:
            return

        if self.current_index >= len(self.camera_list):
            self.current_index = 0
            self.camera_list = self.database.get_notes(CameraCabJournalNote)

        current_note = self.camera_list[self.current_index]
        print(f"[CAMERACHECKER] Checking camera: {current_note.camera_ip} for cab: {current_note.id_cab}")

        # Here we would start the camera worker in a thread
        # For simplicity, simulate
        self.step_timer.start(3000)

    def slot_frame_ready(self, packet):
        self.dataUpdated.emit(packet)

    def slot_people_count(self):
        if not self.camera_list:
            print("[CAMERACHECKER] Camera list empty, waiting 2 seconds")
            self.step_timer.start(2000)
            return

        if self.current_index < 0 or self.current_index >= len(self.camera_list):
            self.current_index = 0

        count = 0  # Simulate people count
        current_note = self.camera_list[self.current_index]
        current_note.is_busy = 1 if count > 0 else 0
        self.database.update_note(current_note)

        print(f"[CAMERACHECKER] Cabinet {current_note.id_cab} checked. People: {count}")
        self.peopleCount.emit()

        self.current_index = (self.current_index + 1) % len(self.camera_list)
        self.step_timer.start(3000)