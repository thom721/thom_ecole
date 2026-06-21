from PySide6.QtCore import QAbstractAnimation
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, QVariantAnimation, QRectF, QEvent, QTimer
from PySide6.QtGui import QPainter, QPen, QColor

class LoaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(70, 70)
        self.angle = 0

        self.animation = QVariantAnimation()
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.update_angle)

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

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 90);")

        # Layout principal avec marges pour le bouton
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 10, 10, 5)  # Marge en haut et à droite pour le bouton
        
        # Layout horizontal pour le bouton croix en haut
        self.top_layout = QHBoxLayout()
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bouton croix - plus visible
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(40, 40)  # Plus grand
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 80);
                color: white;
                border: 2px solid white;
                border-radius: 20px;
                font-size: 24px; 
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 150);
                border: 2px solid red;
            }
        """)
        self.close_button.clicked.connect(self.finish_loading)
        
        # Ajouter le bouton à droite
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.close_button)

        # Ajouter le layout du bouton en haut
        self.main_layout.addLayout(self.top_layout)

        # Contenu central (loader et label)
        self.loader = LoaderWidget()
        self.label = QLabel("Chargement...")
        self.label.setStyleSheet("color: white; font-size: 14pt; padding: 7px;")
        self.label.setAlignment(Qt.AlignCenter)

        # Ajouter le loader et le label au centre
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.loader, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.close_button, Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.close_button)
        # self.close_button.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.main_layout.addStretch()

        self.hide()

    def start_loading(self, message="Chargement...!!!"):
        self.label.setText(message)
        self.close_button.setText('X')
        if self.parent():
            # S'assurer qu'on couvre tout le parent
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        
        # Rendre le bouton bien visible
        self.close_button.setVisible(True)
        self.close_button.raise_()  # S'assurer qu'il est au-dessus

        if not self.isVisible():
            self.loader.start()
            self.show()
            self.raise_()  # S'assurer que l'overlay est au-dessus de tout
        
        # Timeout de sécurité
        # QTimer.singleShot(10000, self.finish_loading)

    def finish_loading(self):
        if self.isVisible():
            self.loader.stop()
            self.hide()

    def resizeEvent(self, event):
        """Redimensionne l'overlay quand la fenêtre parent change de taille"""
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)