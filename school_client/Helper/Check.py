import requests
from Config import BASE_URL

def check_internet():
    try:
        response = requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def check_server_connexion():
    try:
        response = requests.get(BASE_URL, timeout=20)
        return True
    except requests.ConnectionError:
        return False
