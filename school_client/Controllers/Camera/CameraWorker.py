from PySide6.QtCore import QObject, Signal
import cv2
import time
import numpy as np
import requests

class CameraWorker(QObject):
    frame_ready = Signal(object)
    finished = Signal()

    def __init__(self, source, is_ip=False):
        super().__init__()
        self.source = source  # index pour USB, URL pour IP
        self.is_ip = is_ip
        self.running = True
        self.cap = None

    def run(self):
        if not self.is_ip:
            # Caméra USB
            self.cap = cv2.VideoCapture(self.source)
        else:
            # Flux IP Webcam MJPEG
            self.cap = cv2.VideoCapture(self.source)
        try:
            if not self.cap or not self.cap.isOpened():
                print("Impossible d'ouvrir la caméra")
                return
                self.finished.emit()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"errors": str(e), "status": 500}

        while self.running:
            if self.is_ip:
                # flux IP parfois lent → pause légère
                time.sleep(0.03)
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame)
                
        if not self.cap or not self.cap.isOpened():
            print("Impossible d'ouvrir la caméra")
            return

        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.finished.emit()
    
    def run11(self):
        try:
            self.cap = cv2.VideoCapture(self.source)

            if not self.cap.isOpened():
                print("Impossible d'ouvrir la caméra")
                self.finished.emit()
                return
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit()
            return

        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame_ready.emit(frame)
            time.sleep(0.03 if self.is_ip else 0.01)

        # Fermeture propre
        if self.cap.isOpened():
            self.cap.release()

        self.finished.emit()

    def stop(self):
        self.running = False

    @staticmethod
    def capture_ip_photo(url):
        """Capture instantanée depuis IP Webcam (/photo.jpg)"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(data, cv2.IMREAD_COLOR)
                return img
        except Exception as e:
            print("Erreur capture IP:", e)
        return None
