import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtQml import QQmlApplicationEngine, QQmlContext
from PyQt5.QtCore import QUrl

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from settings import SettingsFile
from algorithms import AlgorithmManager
from proxy import ProxyManager
from view_models import ObjectManager
from database_manager import DatabaseManager


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Load settings
        self.file = SettingsFile()
        self.file.read_config_file()
        
        # Initialize database
        self.database = DatabaseManager(self.file, self)
        self.database.open_connection()
        
        # Initialize managers
        self.m_algoManager = AlgorithmManager(self.file, self)
        self.m_algoManager.initialize(self.database)
        self.m_proxy = ProxyManager(self.file, self)
        
        # Connect signals
        self.m_proxy.php_proxy_instance().signalFindRequest.connect(
            self.m_algoManager.slot_get_find_request
        )
        self.m_algoManager.get_finder_instance().signalAuditoryFound.connect(
            self.m_proxy.slot_cabinet_answer
        )
        
        # Initialize QML engine
        self.m_qmlEngine = QQmlApplicationEngine()
        self.m_objManager = ObjectManager(self.m_algoManager, self)
        
        # Set up QML context properties
        root_context = self.m_qmlEngine.rootContext()
        root_context.setContextProperty("cameraWindowObject", self.m_objManager.camera_window_obj())
        root_context.setContextProperty("requestObject", self.m_objManager.request_window_obj())
        
        # Load QML components
        qml_dir = os.path.dirname(__file__)
        qml_path = os.path.join(qml_dir, 'CameraCheckerWindow.qml')
        
        if os.path.exists(qml_path):
            self.m_qmlEngine.load(QUrl.fromLocalFile(qml_path))
        else:
            print(f"Warning: QML file not found at {qml_path}")
        
        # Show window if QML loaded successfully
        if not self.m_qmlEngine.rootObjects():
            print("Error loading QML or no root objects")
            return
        
        self.m_qmlWindow = self.m_qmlEngine.rootObjects()[0]
        self.m_qmlWindow.show()
    
    def __del__(self):
        pass


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
