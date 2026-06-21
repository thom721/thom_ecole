from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap
import requests
from PySide6.QtCore import Qt
from io import BytesIO

class ImageLoaderThread(QThread):
    finished = Signal(QPixmap)
    error = Signal(str)

    def __init__(self, url, label_size):
        super().__init__()
        self.url = url
        self.label_size = label_size

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            if pixmap.loadFromData(image_data.read()):
                scaled_pixmap = pixmap.scaled(
                    self.label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.finished.emit(scaled_pixmap)
            else:
                self.error.emit("Impossible de charger l'image depuis les données.")
        except Exception as e:
            self.error.emit(str(e))
