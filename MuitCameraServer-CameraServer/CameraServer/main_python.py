import sys
from PyQt5.QtWidgets import QApplication
from settings import SettingsFile
from database_manager import DatabaseManager
from algorithms import AlgorithmManager
from proxy import ProxyManager
from view_models import ObjectManager

def main():
    app = QApplication(sys.argv)

    settings = SettingsFile()
    settings.read_config_file()

    database = DatabaseManager(settings)
    database.open_connection()

    algo_manager = AlgorithmManager(settings)
    algo_manager.initialize(database)

    proxy = ProxyManager(settings)

    # Connect signals
    proxy.php_proxy_instance().signalFindRequest.connect(algo_manager.slot_get_find_request)
    algo_manager.get_finder_instance().signalAuditoryFound.connect(proxy.slot_cabinet_answer)

    obj_manager = ObjectManager(algo_manager)

    # For QML, but since not touching Server, perhaps skip GUI for now
    # m_qmlEngine = QQmlApplicationEngine()
    # etc.

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()