import subprocess
import ipaddress
import sys
from PySide6.QtWidgets import QDialog,QApplication
from Views.Login_page import Ui_Dialog
from PySide6.QtCore import Qt, QDate,Signal
from Models.enregistrement import Save_data
from Helper.Token_manager import TokenManager

from Helper.Ip_manager import Ip_manager

class Login_Dialog(QDialog, Ui_Dialog):
    login_signal = Signal()
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 600, 400)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)


        self.ip_manager = Ip_manager()
        self.ui.btn_connexion.clicked.connect(self.se_connecter)
        self.save_data = Save_data(f"http://{self.ip_manager.get_server_ip()}:8080/api/")

        self.ui.show_frame_ip.clicked.connect(self.show_modif_ip)
        self.ui.change_ip.clicked.connect(self.verify_and_save_server_ip_in_connect)
        self.ui.frame_240.setHidden(True)   
        self.ui.input_change_ip.setText(str(self.ip_manager.get_server_ip()))

    def verify_and_save_server_ip_in_connect(self):
        ip_text = self.ui.input_change_ip.text().strip()
        try:
            ip = ipaddress.ip_address(ip_text)

            self.ui.label_76.setText(f"  {ip_text} est une adresse IP valide !")
            self.ui.label_76.setStyleSheet("color: green;")

            # Vérifier si l'IP est accessible sur le réseau
            if self.is_ip_reachable(ip_text):
                self.ui.label_76.setText(f"  {ip_text} est en ligne sur le réseau !")
                self.ui.label_76.setStyleSheet("color: green;")
                self.ip_manager.delete_ip()
                print()
                self.ip_manager.save_server_ip(ip_text)
            else:
                self.ui.label_76.setText(f"  {ip_text} est hors ligne !")
                self.ui.label_76.setStyleSheet("color: orange;")
        except ValueError:
            print('n\'est pas une adresse IP valide')
            self.ui.label_76.setText(f"  {ip_text} n'est pas une adresse IP valide !")
            self.ui.label_76.setStyleSheet("color: red;")
        


    def show_modif_ip(self):
        is_checked = self.ui.show_frame_ip.isChecked()  # Ajout des parenthèses ()
        self.ui.frame_240.setHidden(not is_checked)  # Inverse l'état


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

    def se_connecter(self):
        email = self.ui.email_2.text()
        password = self.ui.password_2.text()

        if not email or not password:
            self.ui.error_message.setText("Veuillez remplir tous les champs.")            
            return

        # print(f"Tentative de connexion à : {self.save_data.api_url}/login")

        response = self.save_data.connect(email, password)
        print(response)  # <-- Voir la réponse exacte

        if response is None:
            self.ui.error_message.setText("Erreur : Impossible de contacter le serveur.")
            return

        if 'errors' in response or 'error' in response:
            self.ui.password_2.setText('')
            self.ui.error_message.setText(response.get("errors", {}).get('email', ["Erreur inconnue"])[0])
            return

        TokenManager().save_token(response.get("token", ""))
        self.login_signal.emit()
        self.close()



    # def se_connecter(self):
    #     email = self.ui.email_2.text()
    #     password = self.ui.password_2.text()

    #     if not email or not password:
    #         self.ui.error_message.setText("Veuillez remplir tous les champs.")            
    #         return
         
    #     response = self.save_data.connect(email, password)
    #     print(response)
    #     if response and 'errors' in response or  'error' in response:
    #         self.ui.password_2.setText('')
    #         self.ui.error_message.setText(response["errors"]['email'][0] if "errors" in response else response["error"]) 
    #         return

    #     if response:
    #         self.ui.error_message.setText("")
    #         # if self.check_data.config_donnees()['data']:
    #         #     image_url = self.check_data.config_donnees()['data'][0]['logo_image_url']
    #         #     self.load_image_from_url_for_dash(image_url, self.ui.logo_2)
    #         TokenManager().save_token(response.get("token",""))
    #         self.login_signal.emit()
    #         self.close()

            
