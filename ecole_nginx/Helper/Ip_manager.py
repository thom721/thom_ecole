import json
from PySide6.QtCore import QSettings
from cryptography.fernet import Fernet

class Ip_manager:
    def __init__(self):
        self.settings = QSettings("School", "Gestin_des_ip_decoles")


    def save_server_ip(self, server_ip):
        """Chiffre et sauvegarde le server_ip"""
        if self.get_server_ip():
            self.delete_server_ip()        
        self.settings.setValue("auth-server_ip", server_ip)


    def get_server_ip(self):
        """Récupère et déchiffre le server_ip"""
        server_ip = self.settings.value("auth-server_ip", type=str)  # Récupérer en str

        if server_ip:
            try:
                return server_ip
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_server_ip(self):
        """Supprime le server_ip (déconnexion)"""
        self.settings.remove("auth-server_ip")