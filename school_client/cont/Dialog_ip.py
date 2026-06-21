import subprocess
import ipaddress
import sys
from PySide6.QtWidgets import QDialog,QApplication
from Views.server_ip_dialog import Ui_Dialog
from PySide6.QtCore import Qt, QDate,Signal

from Helper.Ip_manager import Ip_manager

class Ip_Dialog(QDialog, Ui_Dialog):
    dialog_ip_signal = Signal()
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 600, 400)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.frame_229.setHidden(True)

        self.ip_manager = Ip_manager()
        self.ui.valider_id_server.clicked.connect(self.verify_and_save_server_ip)

#     def verify_and_save_server_ip_in_connect(self):
#         ip_text = self.ui.input_change_ip.text().strip()
#         try:
#             ip = ipaddress.ip_address(ip_text)

#             self.ui.label_76.setText(f"  {ip_text} est une adresse IP valide !")
#             self.ui.label_76.setStyleSheet("color: green;")

#             # Vérifier si l'IP est accessible sur le réseau
#             if self.is_ip_reachable(ip_text):
#                 self.ui.label_76.setText(f"  {ip_text} est en ligne sur le réseau !")
#                 self.ui.label_76.setStyleSheet("color: green;")
#                 self.ip_manager.delete_ip()
#                 print()
#                 self.ip_manager.save_server_ip(ip_text)
#             else:
#                 self.ui.label_76.setText(f"  {ip_text} est hors ligne !")
#                 self.ui.label_76.setStyleSheet("color: orange;")
#         except ValueError:
#             print('n\'est pas une adresse IP valide')
#             self.ui.label_76.setText(f"  {ip_text} n'est pas une adresse IP valide !")
#             self.ui.label_76.setStyleSheet("color: red;")
        

    def verify_and_save_server_ip(self):
        ip_text = self.ui.server_ip.text().strip()
        try:
            ip = ipaddress.ip_address(ip_text)
            self.ui.label.setText(f"  {ip_text} est une adresse IP valide !")
            self.ui.label.setStyleSheet("color: green;")
            

            # Vérifier si l'IP est accessible sur le réseau
            if self.is_ip_reachable(ip_text):
                self.ip_manager.delete_ip()
                self.ui.label.setText(f"  {ip_text} est en ligne sur le réseau !")
                self.ui.label.setStyleSheet("color: green;")

                self.ip_manager.save_server_ip(ip_text)

               
                print(f"self.ip_manager.get_server_ip    {self.ip_manager.get_server_ip()}")
               #  QApplication.processEvents()
                self.dialog_ip_signal.emit()
                self.close()
            else:
                self.ui.label.setText(f"  {ip_text} est hors ligne !")
                self.ui.label.setStyleSheet("color: orange;")
        except ValueError:
            print('n\'est pas une adresse IP valide')
            self.ui.label.setText(f"  {ip_text} n'est pas une adresse IP valide !")
            self.ui.label.setStyleSheet("color: red;")

    def is_ip_reachable(self, ip):
        """Teste si une adresse IP répond au ping."""
        try:
            # Commande ping pour Windows (-n 1) ou Linux/Mac (-c 1)
            param = "-n" if sys.platform == "win32" else "-c"
            result = subprocess.run(["ping", param, "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result)
            return result.returncode == 0  # 0 = succès, sinon échec
        except Exception:
            return False
