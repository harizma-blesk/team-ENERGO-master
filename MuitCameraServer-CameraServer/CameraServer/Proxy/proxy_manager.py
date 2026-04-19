from PyQt5.QtCore import QObject
from .php_server_proxy import PHPServerProxy
from .esp_server_proxy import EspServerProxy

class ProxyManager(QObject):
    def __init__(self, settings_file, parent=None):
        super().__init__(parent)
        self.php_proxy = PHPServerProxy(settings_file, self)
        self.esp_proxy = EspServerProxy(settings_file, self)

    def php_proxy_instance(self):
        return self.php_proxy

    def slot_cabinet_answer(self, note):
        """Send cabinet answer to PHP server"""
        self.php_proxy.slot_cabinet_answer(note)