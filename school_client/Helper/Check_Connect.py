# import requests
# from PySide6.QtWidgets import QApplication, QLabel, QMessageBox
# import sys
# import threading
# import time

# def check_internet():
#     try:
#         requests.get("https://www.google.com", timeout=5)
#         return True
#     except requests.ConnectionError:
#         return False

# def monitor_connection():
#     while True:
#         if not check_internet():
#             msg = QMessageBox()
#             msg.setIcon(QMessageBox.Warning)
#             msg.setText("Pas de connexion Internet !")
#             msg.setWindowTitle("Alerte")
#             msg.exec()
#         time.sleep(10)  # Vérification toutes les 10 secondes

# app = QApplication(sys.argv)
# label = QLabel("Vérification de la connexion Internet...")
# label.show()

# # Lancer la vérification dans un thread pour ne pas bloquer l'UI
# thread = threading.Thread(target=monitor_connection, daemon=True)
# thread.start()

# sys.exit(app.exec())
