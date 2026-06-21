import json
from PySide6.QtCore import QSettings, QByteArray
from cryptography.fernet import Fernet

class Ip_manager:
    def __init__(self):
        self.settings = QSettings("MaSociété", "MonApplication")
        self.key = self._get_encryption_key()

    def _get_encryption_key(self):
        """Génère ou récupère une clé de chiffrement sécurisée"""
        key = self.settings.value("encryption_key", type=str)  # Récupérer sous forme de str

        if not key:
            key = Fernet.generate_key().decode()  # Générer une nouvelle clé
            self.settings.setValue("encryption_key", key)  # Sauvegarder

        return key.encode()  # Convertir en bytes avant utilisation


    def save_server_ip(self, server_ip):
        """Chiffre et sauvegarde le ip"""
        self.settings.setValue("auth-ip", server_ip)
        self.settings.sync()


    def get_server_ip(self):
        """Récupère et déchiffre le ip"""
        self.settings.sync()
        server_ip = self.settings.value("auth-ip", "")  # Récupérer en str

        if server_ip:
            try:
                return server_ip
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_ip(self):
        """Supprime le ip (déconnexion)"""
        self.settings.remove("auth-ip")
        self.settings.sync()