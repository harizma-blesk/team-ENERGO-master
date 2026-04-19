import socket
from PyQt5.QtCore import QObject, pyqtSignal

class TCPManager(QObject):
    packetReceived = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = None

    def send_raw_data_to_ip(self, data, ip):
        # Send data to specific IP
        pass