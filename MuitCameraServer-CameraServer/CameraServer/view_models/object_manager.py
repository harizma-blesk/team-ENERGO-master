from PyQt5.QtCore import QObject

class ObjectManager(QObject):
    def __init__(self, algo_manager, parent=None):
        super().__init__(parent)
        self.algo_manager = algo_manager

    def img_provider_obj(self):
        return None  # Placeholder

    def camera_window_obj(self):
        return None

    def request_window_obj(self):
        return None