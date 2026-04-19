import socket
import struct
from PyQt5.QtCore import QObject

class EspServerProxy(QObject):
    def __init__(self, settings_file, parent=None):
        super().__init__(parent)
        self.ip = settings_file.tcp_settings.tcp_ip_esp
        self.port = settings_file.tcp_settings.tcp_port_esp
        # Similar to Java proxy but for ESP