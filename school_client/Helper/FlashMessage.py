from PySide6.QtCore import QAbstractAnimation
# from utils.imports import *
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QVariantAnimation, QRectF, QEvent
from PySide6.QtGui import QPainter, QPen, QColor
class LoaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(70, 70)
        self.angle = 0

        # self.animation = QVariantAnimation()
        # self.animation.setStartValue(0)
        # self.animation.setEndValue(360)
        # self.animation.setDuration(1000)
        # self.animation.setLoopCount(-1)
        # self.animation.valueChanged.connect(self.update_angle)

        # Configuration visuelle
        self.color = QColor("#3498db")
        self.pen_width = 5
        self.size = 60

    def update_angle(self, value):
        self.angle = value
        self.update()

    def start(self):
        if self.animation.state() != QAbstractAnimation.Running:
            self.animation.start()

    def stop(self):
        if self.animation.state() == QAbstractAnimation.Running:
            self.animation.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        x = (self.width() - self.size) / 2
        y = (self.height() - self.size) / 2
        pen = QPen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.color)
        painter.setPen(pen)
        rectangle = QRectF(x, y, self.size, self.size)
        painter.drawArc(rectangle, self.angle * 16, 270 * 16)

class FlashMessage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setModal
        self.setStyleSheet("background-color: rgba(0, 0, 0, 90);padding:5px")

        self.loader = LoaderWidget()
        self.label = QLabel("Chargement...", self)
        self.label.setStyleSheet("color: white; font-size: 15px;")
        self.label.setAlignment(Qt.AlignCenter)

        self.layouts = QVBoxLayout(self)
        self.layouts.addStretch()
        self.layouts.addWidget(self.loader, alignment=Qt.AlignCenter)
        self.layouts.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layouts.addStretch()
        self.setLayout(self.layouts)

        self.hide()

    def start_loading(self, message="Chargement...!!!"):
        self.label.setText(message)
        self.resize(self.parent().size())

        if not self.isVisible():
            self.loader.start()
            self.show()

    def finish_loading(self):
        if self.isVisible():
            self.loader.stop()
            self.hide()