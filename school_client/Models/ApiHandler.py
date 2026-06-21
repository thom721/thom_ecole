from PySide6.QtCore import QObject, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtNetwork import QNetworkReply  # Assure-toi que c'est importé
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
import json


class ApiHandler(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.on_response)
        self.callbacks = {}
        self.timeout = 30000 

        self.ip_manager = Ip_manager()
        self.token_manager = TokenManager()

    def ip(self):
        """Retourne l'URL de base de l'API"""
        return f"https://{self.ip_manager.get_server_ip()}/api/v1/"

    def post(self, endpoint, data, success_callback, error_callback):
        """Envoie une requête POST"""
        url = QUrl(f"{self.ip()}{endpoint}")
        request = QNetworkRequest(url)
        
        # Configuration des headers (version compatible PySide6)
        request.setRawHeader("Content-Type".encode('utf-8'), "application/json".encode('utf-8'))
        request.setRawHeader("Accept".encode('utf-8'), "application/json".encode('utf-8'))
        request.setTransferTimeout(self.timeout)
        
        # Ajout du token si disponible
        token = self.token_manager.get_token()
        if token:
            auth_header = f"Bearer {token}"
            request.setRawHeader("Authorization".encode('utf-8'), auth_header.encode('utf-8'))

        # Préparation des données
        json_data = json.dumps(data)
        payload = QByteArray(json_data.encode('utf-8'))
        if token:
            print(f"  Authorization: Bearer [token_masqué]")

        # Envoi de la requête
        reply = self.manager.post(request, payload)
        self._register_callbacks(reply, endpoint, success_callback, error_callback)

    def _register_callbacks(self, reply, endpoint, success_cb, error_cb):
        """Enregistrement des callbacks"""
        self.callbacks[reply] = {
            "endpoint": endpoint,
            "success": success_cb,
            "error": error_cb
        }

    def on_response(self, reply):
        """Gestion des réponses"""
        callbacks = self.callbacks.pop(reply, None)
        if not callbacks:
            return

        endpoint = callbacks.get("endpoint", "unknown")
        success_cb = callbacks.get("success")
        error_cb = callbacks.get("error")

        try:
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            raw_data = bytes(reply.readAll()).decode('utf-8')
            
            if reply.error() and status_code != 200:
                data = json.loads(raw_data)
                error_message =data.get("errors")  
                print(f"error_message   {error_message}")
                if error_cb:
                    error_cb(endpoint, error_message)
                return

            response_data = json.loads(raw_data) if raw_data else {}

            if status_code == 401:
                self._handle_unauthorized(endpoint, error_cb)
            elif "error" in response_data:
                if error_cb:
                    error_cb(endpoint, response_data["error"])
            elif "errors" in response_data:
                first_error = next(iter(response_data["errors"].values()))[0]
                if error_cb:
                    error_cb(endpoint, first_error)
            elif success_cb:
                success_cb(endpoint, response_data)

        except json.JSONDecodeError:
            error_msg = "Réponse serveur invalide"
            print(f"⚠️ {error_msg} endpoint={endpoint} status_code={status_code} raw_data={raw_data!r}")
            if error_cb:
                error_cb(endpoint, error_msg)
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            print(f"⚠️ {error_msg}")
            if error_cb:
                error_cb(endpoint, error_msg)
        finally:
            reply.deleteLater()

    def _handle_unauthorized(self, endpoint, error_callback):
        """Gestion des erreurs 401"""
        error_msg = "Session expirée - Veuillez vous reconnecter"
        print(f"🔒 {error_msg}")
        if error_callback:
            error_callback(endpoint, error_msg)

    def login(self, email, password, success_callback, error_callback):
        """Méthode spécialisée pour le login"""
        data = {
            "email": email,
            "password": password,
            "device_name": "qt-desktop-app"
        }
        self.post("login", data, success_callback, error_callback)

    

    def get(self, endpoint, success_callback, error_callback, params=None):
        """Envoie une requête GET avec paramètres optionnels"""
        # Construction de l’URL
        url_str = f"{self.ip()}{endpoint}"
        
        # Ajout de paramètres GET si fournis
        if params:
            query_items = [f"{key}={value}" for key, value in params.items()]
            query_string = "&".join(query_items)
            url_str += f"?{query_string}"
        
        url = QUrl(url_str)
        request = QNetworkRequest(url)

        # Headers
        # request.setRawHeader("Accept".encode('utf-8'), "application/json".encode('utf-8'))
        request.setRawHeader("Content-Type".encode('utf-8'), "application/json".encode('utf-8'))
        request.setRawHeader("Accept".encode('utf-8'), "application/json".encode('utf-8'))
        request.setTransferTimeout(self.timeout)

        token = self.token_manager.get_token()
        if token:
            auth_header = f"Bearer {token}"
            request.setRawHeader("Authorization".encode('utf-8'), auth_header.encode('utf-8'))
            print(f"  Authorization: Bearer [token_masqué]")

        # Envoi de la requête GET
        reply = self.manager.get(request)
        self._register_callbacks(reply, endpoint, success_callback, error_callback)
