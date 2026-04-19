from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, QTime, QDate
from .auditory_finder import AuditoryFinder
from .camera_checker import CameraChecker
from database_manager.models import AuditoryNote

class AlgorithmManager(QObject):
    signalAuditoryFound = pyqtSignal(object)
    
    def __init__(self, settings_file, parent=None):
        super().__init__(parent)
        self.settings = settings_file
        self.database = None  # Will be set later
        self.finder = None
        self.checker = None
        self.cleaner = None
        self.checker_thread = None
        self.is_checking = False

    def initialize(self, database_manager):
        self.database = database_manager
        self.finder = AuditoryFinder(self.database, self)
        self.checker = CameraChecker(self.settings, self.database, None)
        # self.cleaner = TemporaryAuditoryCleaner(self.database, self)

        self.checker_thread = QThread(self)
        self.checker.moveToThread(self.checker_thread)
        self.checker_thread.started.connect(self.checker.start_monitoring)
        self.checker_thread.start()

        self.finder.signalAuditoryFound.connect(self.on_auditory_found)

    def get_finder_instance(self):
        return self.finder

    def get_checker_instance(self):
        return self.checker

    @pyqtSlot(str, QTime, int)
    def slot_get_find_request(self, target_corpus, start_time, longness):
        if self.is_checking or not start_time.isValid():
            print("[ALGORITHMMANAGER] Rejecting request: Invalid time or busy.")
            return
        self.is_checking = True
        print(f"[ALGORITHMMANAGER] New request: Corpus {target_corpus} Time {start_time.toString()}")
        self.find_next_available_room(target_corpus, start_time, longness)

    def find_next_available_room(self, target_corpus, start_time, longness):
        day_of_week = QDate.currentDate().dayOfWeek()
        found_note = self.finder.find_auditory(target_corpus, start_time, day_of_week, longness)

        if found_note.id != 0:
            print(f"[ALGORITHMMANAGER] Auditory found: {found_note.number}")
            self.finder.complete_booking(found_note, start_time, day_of_week, longness)
            self.finder.signalAuditoryFound.emit(found_note)
        else:
            print("[ALGORITHMMANAGER] No free auditories found")
            self.finder.signalAuditoryFound.emit(AuditoryNote())
            self.finder.signalAuditoryNotFound.emit("Cabinet not found")

        self.is_checking = False

    def on_auditory_found(self, note):
        pass  # Handle as needed