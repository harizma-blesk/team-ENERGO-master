import cv2
import threading
from ultralytics import YOLO
from PyQt5.QtCore import QObject, pyqtSignal

class CameraWorker(QObject):
    signalProcessPacketReady = pyqtSignal(object)
    signalPeopleCount = pyqtSignal()
    finish = pyqtSignal()

    def __init__(self, url, model_path, parent=None):
        super().__init__(parent)
        self.url = url
        self.model = YOLO(model_path)
        self.running = False
        self.thread = None

    def set_url(self, url):
        self.url = url

    def set_running(self, running):
        self.running = running

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        cap = cv2.VideoCapture(self.url)
        while self.running:
            ret, frame = cap.read()
            if ret:
                results = self.model(frame)
                people_count = sum(1 for r in results for c in r.boxes.cls if c == 0)  # class 0 is person
                packet = {'image': frame, 'people': people_count}
                self.signalProcessPacketReady.emit(packet)
                self.signalPeopleCount.emit()
        cap.release()
        self.finish.emit()