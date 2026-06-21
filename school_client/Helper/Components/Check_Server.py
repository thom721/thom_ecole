from PySide6.QtCore import QObject, QTimer, Signal
from Helper.Check_data import check_server_connexion

class ServerChecker(QObject):
    # Signal émis uniquement si la connexion réussit
    server_connected = Signal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(5000)  # Vérifie toutes les 5 secondes
        self.timer.timeout.connect(self._check_connexion)
     #    self.attemp_show = attemp_show

    def start(self):
        """Démarre le monitoring."""
        if not self.timer.isActive():
            self.timer.start()

    def stop(self):
        """Arrête le monitoring."""
        self.timer.stop()

    def _check_connexion(self):
        """Vérifie la connexion et émet le signal si réussie."""
        try:
            if check_server_connexion():
                self.server_connected.emit()
                return True
            else:
               return False

        except Exception as e:
            print(f"Erreur lors de la vérification : {e}")

