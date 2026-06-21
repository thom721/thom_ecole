import sys
import subprocess
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGroupBox


class ServiceManager(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des Services")
        self.setGeometry(300, 200, 400, 300)

        # Initialisation de l'interface
        self.layout = QVBoxLayout()

        # Ajouter les services (exemple)
        self.services = {
            "Apache": "stopped",
            "MySQL": "running"
        }

        for service_name, status in self.services.items():
            self.create_service_widget(service_name, status)

        # Ajouter un bouton pour éteindre le serveur
        self.shutdown_button = QPushButton("Éteindre le serveur")
        self.shutdown_button.clicked.connect(self.shutdown_server)
        self.layout.addWidget(self.shutdown_button)

        self.setLayout(self.layout)

    def create_service_widget(self, service_name, status):
        """ Crée un widget pour chaque service """
        service_widget = QGroupBox(service_name)
        service_layout = QHBoxLayout()

        # Étiquette de statut
        status_label = QLabel(f"Status: {status}")
        service_layout.addWidget(status_label)

        # Bouton pour démarrer ou arrêter le service
        toggle_button = QPushButton("Démarrer" if status == "stopped" else "Arrêter")
        toggle_button.clicked.connect(lambda: self.toggle_service(service_name, status_label, toggle_button))
        service_layout.addWidget(toggle_button)

        service_widget.setLayout(service_layout)
        self.layout.addWidget(service_widget)

    def toggle_service(self, service_name, status_label, toggle_button):
        """ Démarre ou arrête un service selon son état actuel """
        current_status = status_label.text().split(": ")[1]

        if current_status == "running":
            # Arrêter le service
            self.stop_service(service_name)
            status_label.setText("Status: stopped")
            toggle_button.setText("Démarrer")
        else:
            # Démarrer le service
            self.start_service(service_name)
            status_label.setText("Status: running")
            toggle_button.setText("Arrêter")

    def start_service(self, service_name):
        """ Démarre un service (exemple) """
        print(f"Démarrage de {service_name}")
        # Remplacer par le code pour démarrer le service
        subprocess.run(["net", "start", service_name], shell=True)

    def stop_service(self, service_name):
        """ Arrête un service (exemple) """
        print(f"Arrêt de {service_name}")
        # Remplacer par le code pour arrêter le service
        subprocess.run(["net", "stop", service_name], shell=True)

    def shutdown_server(self):
        """ Éteindre le serveur """
        print("Éteindre le serveur...")
        subprocess.run(["shutdown", "/s", "/f", "/t", "0"], shell=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServiceManager()
    window.show()
    sys.exit(app.exec())
