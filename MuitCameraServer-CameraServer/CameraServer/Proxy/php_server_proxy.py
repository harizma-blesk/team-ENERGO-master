import requests
import json
from PyQt5.QtCore import QObject, pyqtSignal
from database_manager.models import AuditoryNote

class PHPServerProxy(QObject):
    """Proxy for PHP backend server communication via HTTP"""
    signalFindRequest = pyqtSignal(str, object, int)  # targetCorpus, startTime, longness
    signalError = pyqtSignal(str)

    def __init__(self, settings_file, parent=None):
        super().__init__(parent)
        self.ip = settings_file.tcp_settings.tcp_ip_php
        self.port = settings_file.tcp_settings.tcp_port_php
        self.base_url = f"http://{self.ip}:{self.port}"
        print(f"[PHPServerProxy] Initialized with {self.base_url}")

    def send_find_request(self, corpus, start_time, duration):
        """Send find auditory request to PHP server"""
        try:
            data = {
                'action': 'find_auditory',
                'corpus': corpus,
                'start_time': start_time.isoformat() if hasattr(start_time, 'isoformat') else str(start_time),
                'duration': duration
            }
            response = requests.post(f"{self.base_url}/api/find_auditory.php", json=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                self.signalError.emit(f"PHP Server error: {response.status_code}")
                return None
        except Exception as e:
            self.signalError.emit(f"Connection error: {e}")
            return None

    def slot_cabinet_answer(self, note):
        """Send cabinet answer to PHP server"""
        try:
            data = {
                'action': 'cabinet_answer',
                'id': note.id,
                'cabinet': note.number,
                'corpus': note.corpus,
                'status': 'available'
            }
            response = requests.post(f"{self.base_url}/api/cabinet_answer.php", json=data, timeout=5)
            if response.status_code == 200:
                print(f"[PHPServerProxy] Cabinet {note.number} sent to PHP server")
            else:
                self.signalError.emit(f"Failed to send answer: {response.status_code}")
        except Exception as e:
            self.signalError.emit(f"Send error: {e}")