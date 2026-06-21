import os
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
from Helper import Ip_manager as reloadIp
import importlib
 
importlib.reload(reloadIp)


ENV = os.getenv("APP_ENV", "development") 

token_manager = TokenManager()
# ip_manager = Ip_manager()

SERVER_IP = Ip_manager().get_server_ip()

CONFIG = {
    "development": f"https://{Ip_manager().get_server_ip()}/api/v1/",
}

BASE_URL = CONFIG.get(ENV, CONFIG["development"])

HEADERS  = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        "Authorization": f"Bearer {token_manager.get_token()}"
    }



 


