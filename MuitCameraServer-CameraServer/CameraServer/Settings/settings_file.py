from dataclasses import dataclass
import configparser
import os
from PyQt5.QtCore import QObject, pyqtSignal

@dataclass
class DatabaseSettings:
    db_path: str = "camera_server.db"

@dataclass
class CameraSettings:
    start_rtcp: str = ""
    end_rtcp: str = ""
    camera_index: str = ""

@dataclass
class UdpSettings:
    ip_python_server: str = ""
    ip_port_listen: int = 0
    ip_port_send: int = 0
    ip_port_remote: int = 0

@dataclass
class NeuroModelSettings:
    config_file_path: str = ""
    weights_file_path: str = ""
    coco_names_file_path: str = ""

@dataclass
class TCPSettings:
    tcp_ip_java: str = ""
    tcp_port_java: int = 0
    tcp_ip_esp: str = ""
    tcp_port_esp: int = 0

class SettingsFile(QObject):
    signalSettingsReady = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.database_settings = DatabaseSettings()
        self.camera_settings = CameraSettings()
        self.udp_settings = UdpSettings()
        self.neuromodel_settings = NeuroModelSettings()
        self.tcp_settings = TCPSettings()

    def read_config_file(self):
        settings_path = os.path.join(os.getcwd(), "settings.ini")
        config = configparser.ConfigParser()
        config.read(settings_path)

        # Database
        if 'Database' in config:
            db = config['Database']
            self.database_settings.db_path = db.get('dbPath', 'camera_server.db')
        
        self.db_path = self.database_settings.db_path

        # Camera
        if 'Camera' in config:
            cam = config['Camera']
            self.camera_settings.start_rtcp = cam.get('startRtcp', 'rtsp://192.168.1.10')
            self.camera_settings.end_rtcp = cam.get('endRtcp', 'rtsp://192.168.1.11')
            self.camera_settings.camera_index = cam.get('cameraIndex', '0')

        # UDP
        if 'UDP' in config:
            udp = config['UDP']
            self.udp_settings.ip_python_server = udp.get('IP_PythonServer', '127.0.0.1')
            self.udp_settings.ip_port_listen = int(udp.get('IP_Port_Listen', '5000'))
            self.udp_settings.ip_port_send = int(udp.get('IP_Port_Send', '5001'))
            self.udp_settings.ip_port_remote = int(udp.get('IP_Port_Remote', '5002'))

        # NeuroModel
        if 'NEUROMODEL' in config:
            nm = config['NEUROMODEL']
            self.neuromodel_settings.config_file_path = nm.get('ConfigPath', '...')
            self.neuromodel_settings.weights_file_path = nm.get('WeightsPath', 'YOLOv11/yolov8n.onnx')
            self.neuromodel_settings.coco_names_file_path = nm.get('CocoNamesPath', '...')

        # TCP_Servers
        if 'TCP_Servers' in config:
            tcp = config['TCP_Servers']
            self.tcp_settings.tcp_ip_php = tcp.get('IP_PHP', '192.168.7.14')
            self.tcp_settings.tcp_port_php = int(tcp.get('PORT_PHP', '8080'))
            self.tcp_settings.tcp_ip_esp = tcp.get('IP_ESP', '192.168.7.17')
            self.tcp_settings.tcp_port_esp = int(tcp.get('PORT_ESP', '4444'))

        print(f"Settings loaded from: {settings_path}")
        self.signalSettingsReady.emit()