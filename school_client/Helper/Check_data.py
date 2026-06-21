import requests
# from Config import BASE_URL
import importlib
import Config
from Helper.Ip_manager import Ip_manager
 
importlib.reload(Config)
        

class Check_data:
    def __init__(self):
        self.ip_manager = Ip_manager()

    # 
    def ip(self):
        return f"https://{self.ip_manager.get_server_ip()}/api/"

    def verifier_donnees(self):
        """ Vérifie si la table contient des données via une API. """
        self.API_URL= self.ip() +'get-profile'
        try:
            response = requests.get(self.API_URL,timeout=50,verify="C:\Program Files\ecole-serve\Apache24\conf\ca.pem")
            response.raise_for_status()  

            data = response.json()  
            if not data: 
                return False
            return True


        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la vérification des données : {e}")
            return False  
        
    def config_donnees(self):
        """ Vérifie si la table contient des données via une API. """
        self.API_URL= self.ip() +'get-profile'
        try:
            response = requests.get(self.API_URL, timeout=60,verify="C:\Program Files\ecole-serve\Apache24\conf\ca.pem")
            response.raise_for_status()  

            data = response.json()  
            if not data: 
                return False
            return data


        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la vérification des données : {e}")
            return False  



    def check_server_connexion(self):
        try:
            response = requests.get(self.ip(), timeout=50)  
            if response.status_code == 200:
                print(" Serveur opérationnel")
                return True
            else:
                print(f" Le serveur répond avec un code {response.status_code}")
                return False
        except requests.ConnectionError:
            print(" Impossible de se connecter au serveur.")
            return False
        except requests.Timeout:
            print(" La requête a dépassé le temps limite.")
            return False

    def verify_sanctum_token(self, token):
        url = f"{self.ip()}verify-token"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {token}"
            }
        try:
            response = requests.get(url, headers=headers, timeout=60, verify="C:\Program Files\ecole-serve\Apache24\conf\ca.pem")
            if response.status_code == 200:
                print(f"verify_sanctum_token {response.json()}")
                return response.json()
            return {}

        except requests.RequestException as e:
            print(f"erreur verify_sanctum_token {e}")
            return {}
            return False
        
    def verify_authorization_token(self, mac):
        params = {"mac_address": mac}
        url = f"{self.ip()}client-authorisation-connect/{mac}"

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            }

        try:
            response = requests.get(url, headers=headers, timeout=60, verify="C:\Program Files\ecole-serve\Apache24\conf\ca.pem")
            if response.status_code == 200:
                data = response.json()
                if data and 'data' in data:
                    if data['status'] == 1:
                        return data['data']
                    return False
            print(f"response.json( false)   {response.json()}")
            return False

        except requests.RequestException as e:
            print(f"erreur verify_sanctum_token {e}")
            return False
