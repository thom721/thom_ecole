# pyinstaller --onefile --noconsole \
#     --add-data "Models:Models" \
#     --add-data "Views:Views" \
#     --add-data "Controllers:Controllers" \
#     --add-data "assets:assets" \
#     --add-data "Config.py:." \
#     --add-data "Helper:Helper" \
#     app.py

# pyinstaller --onefile `
# --hidden-import=PySide6.QtCore `
# --hidden-import=PySide6.QtGui `
# --hidden-import=PySide6.QtWidgets `
# --hidden-import=PySide6.QtQml `
# --hidden-import=PySide6.QtQuick `
# --hidden-import=PySide6.QtNetwork `
# --hidden-import=PySide6.QtSql `
# --add-data "Models;Models" `
# --add-data "Views;Views" `
# --add-data "Controllers;Controllers" `
# --add-data "assets;assets" `
# --add-data "Config.py;." `
# --add-data "Helper;Helper" `
# app.py


# pyinstaller --onefile `
# --add-data "Models;Models" `
# --add-data "Views;Views" `
# --add-data "Controllers;Controllers" `
# --add-data "assets;assets" `
# --add-data "Config.py;." `
# --add-data "Helper;Helper" `
# --add-data "Helper;Helper" `
# app.py


import sys
import logging
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QWidget

# Configuration du logging pour la console
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Définit le niveau de log à DEBUG pour tout afficher

# Création d'un handler pour la console (affichage dans la console)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Niveau de log pour la console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Ajout du handler à notre logger
logger.addHandler(console_handler)

# Exemple de fenêtre PySide6
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test PySide6 avec logs")
        self.setGeometry(100, 100, 400, 300)

        # Simuler une tâche lente
        self.simulate_slow_dependency()

    def simulate_slow_dependency(self):
        # Log lorsqu'on commence à charger une dépendance
        logging.info("Démarrage de la dépendance lente...")
        
        # Simuler une tâche lente (par exemple, une attente de 3 secondes)
        QTimer.singleShot(3000, self.dependency_done)

    def dependency_done(self):
        logging.info("Dépendance terminée.")

