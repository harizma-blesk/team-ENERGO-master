from PyQt5.QtCore import QObject, QTimer

class TemporaryAuditoryCleaner(QObject):
    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database = database_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clean)
        self.timer.start(300000)  # 5 minutes

    def clean(self):
        # Clean temporary bookings
        self.database.execute_query("DELETE FROM auditory_journal WHERE timeStatus = 1")