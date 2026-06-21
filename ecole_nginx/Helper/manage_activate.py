import json
from PySide6.QtCore import QSettings
from cryptography.fernet import Fernet

class Manage_active:
    def __init__(self):
        self.settings = QSettings("School", "Gestin_des_active_decoles")


    def save_manage_active(self, value):
        """Chiffre et sauvegarde le value"""
        if self.get_manage_active():
            self.delete_manage_active()        
        self.settings.setValue("auth-server-active", value)


    def get_manage_active(self):
        """Récupère et déchiffre le manage_active"""
        manage_active = self.settings.value("auth-server-active", type=str)  # Récupérer en str

        if manage_active:
            try:
                return manage_active
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_manage_active(self):
        """Supprime le manage_active (déconnexion)"""
        self.settings.remove("auth-server-active")



    def save_manage_b_p(self, value):
        """Chiffre et sauvegarde le value"""
        if self.get_manage_b_p():
            self.delete_manage_b_p()        
        self.settings.setValue("auth-server-b-p", value)


    def get_manage_b_p(self):
        """Récupère et déchiffre le manage_active"""
        manage_active = self.settings.value("auth-server-b-p", type=str)  # Récupérer en str

        if manage_active:
            try:
                return manage_active
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_manage_b_p(self):
        """Supprime le manage_active (déconnexion)"""
        self.settings.remove("auth-server-b-p")


    def save_manage_b_name(self, value):
        """Chiffre et sauvegarde le value"""
        if self.get_manage_b_name():
            self.delete_manage_b_name()        
        self.settings.setValue("auth-server-b-name", value)


    def get_manage_b_name(self):
        """Récupère et déchiffre le manage_active"""
        manage_active = self.settings.value("auth-server-b-name", type=str)  # Récupérer en str

        if manage_active:
            try:
                return manage_active
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_manage_b_name(self):
        """Supprime le manage_active (déconnexion)"""
        self.settings.remove("auth-server-b-name")


    def save_direct_migration(self, value:bool):
        """Chiffre et sauvegarde le value"""
        if self.get_direct_migration():
            self.delete_direct_migration()        
        self.settings.setValue("direct-migration",False) #value)


    def get_direct_migration(self):
        """Récupère et déchiffre le direct_migration"""
        direct_migration = False# self.settings.value("direct-migration", type=bool)  # Récupérer en str

        if direct_migration:
            try:
                return direct_migration
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_direct_migration(self):
        """Supprime le direct_migration (déconnexion)"""
        self.settings.remove("direct-migration")