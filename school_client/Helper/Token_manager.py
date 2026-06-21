import json
from PySide6.QtCore import QSettings, QByteArray
from cryptography.fernet import Fernet

class TokenManager:
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


    # def save_token(self, token):
    #     """Chiffre et sauvegarde le token"""
    #     cipher = Fernet(self.key)
    #     encrypted_token = cipher.encrypt(token.encode()).decode()
    #     self.settings.setValue("auth-token", encrypted_token)

    def save_token(self, token):
        """Chiffre et sauvegarde le token"""
        cipher = Fernet(self.key)
        encrypted_token = cipher.encrypt(token.encode()).decode()  # Convertir en str
        self.settings.setValue("auth-token", encrypted_token)
        # print(f"Token chiffré : {encrypted_token}")


    def get_token(self):
        """Récupère et déchiffre le token"""
        encrypted_token = self.settings.value("auth-token", type=str)  # Récupérer en str
        # Bearer F7RKIO1wGfLyzNh2t74ZqTn2RFY4FqKEnfPuAbYM8e6fae7
        if encrypted_token:
            try:
                cipher = Fernet(self.key)
                decrypted_token = cipher.decrypt(encrypted_token.encode()).decode()
                # if "|" in decrypted_token:
                #     decrypted_token = decrypted_token.split("|")[1]
         
                # print(f"Token déchiffré : {decrypted_token}")
                return decrypted_token
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None


    def delete_token(self):
        """Supprime le token (déconnexion)"""
        self.settings.remove("auth-token")

    def save_user_email(self, user_email):
        self.settings.setValue("user-email", user_email)

    def get_user_email(self):
        """Récupère et déchiffre le token"""
        user__email = self.settings.value("user-email", type=str)
        if user__email:
            try:
                return user__email
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None



    def save_token_access(self, token):
        self.settings.setValue("access-token", token)

    def save_certificat_signed(self, certif):
        self.settings.setValue("certif", certif)

    def get_certificat_signed(self):
        """Récupère et déchiffre le token"""
        certif_signed = self.settings.value("certif", type=bool)
        if certif_signed:
            try:
                return certif_signed
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None

    def get_token_access(self):
        """Récupère et déchiffre le token"""
        token_access = self.settings.value("access-token", type=str)
        if token_access:
            try:
                return token_access
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None
    
    def delete_token_access(self):
        """Supprime le token (déconnexion)"""
        self.settings.remove("access-token")

    def save_direct_request(self, request:bool):
        self.settings.setValue("direct-request", request)

    def get_direct_request(self):
        request = False#self.settings.value("direct-request", type=bool)
        if request:
            try:
                return bool(request)
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None
    
    def save_adress_type(self, request:bool):
        self.settings.setValue("adress-type", request)

    def get_adress_type(self):
        adress_type = self.settings.value("adress-type", type=bool)
        if adress_type:
            try:
                return adress_type
            except Exception as e:
                print(f"Erreur de déchiffrement : {e}")
                return None
        return None