from PySide6.QtCore import QObject, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
import json

class AsyncRequestHandler(QObject):
    def __init__(self):
        super().__init__()
        self.ip_manager = Ip_manager()
        self.token_manager = TokenManager()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.handle_response)
        self.current_callbacks = {}

    def ip(self):
        return f"https://{self.ip_manager.get_server_ip()}/api/"

    def headers_token(self):
        token = self.token_manager.get_token()
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {token}" if token else ""
        }

    def _prepare_request(self, endpoint, method="POST", data=None):
        url = QUrl(f"{self.ip()}{endpoint}")
        request = QNetworkRequest(url)
        
        headers = self.headers_token()
        for key, value in headers.items():
            request.setRawHeader(key.encode('utf-8'), value.encode('utf-8'))
        
        if data:
            payload = QByteArray(json.dumps(data).encode('utf-8'))
            return request, payload
        return request, None

    def _send_request(self, request, payload=None, callback=None, error_callback=None):
        if payload:
            reply = self.network_manager.post(request, payload)
        else:
            reply = self.network_manager.get(request)
        
        if callback or error_callback:
            self.current_callbacks[reply] = {
                'success': callback,
                'error': error_callback
            }
        return reply

    def handle_response(self, reply):
        callback_data = self.current_callbacks.pop(reply, None)
        
        try:
            raw_data = bytes(reply.readAll()).decode('utf-8')
            response_data = json.loads(raw_data) if raw_data else {}
            
            if reply.error():
                error_msg = reply.errorString()
                print(f"Request failed: {error_msg}")
                if callback_data and callback_data['error']:
                    callback_data['error'](error_msg, response_data)
            else:
                if callback_data and callback_data['success']:
                    callback_data['success'](response_data)
        
        except json.JSONDecodeError:
            error_msg = "Invalid JSON response"
            print(error_msg)
            if callback_data and callback_data['error']:
                callback_data['error'](error_msg, None)
        finally:
            reply.deleteLater()

    # Méthodes adaptées pour être asynchrones
    def authorization_connect(self, mac, username, callback=None, error_callback=None):
        endpoint = "client-authorisation-connect"
        data = {
            "client_mac": mac,
            "client_name": username
        }
        
        request, payload = self._prepare_request(endpoint, data=data)
        self._send_request(request, payload, callback, error_callback)

    def connect(self, email, password, callback=None, error_callback=None):
        endpoint = "login"
        data = {
            "email": email,
            "password": password
        }
        
        request, payload = self._prepare_request(endpoint, data=data)
        self._send_request(request, payload, callback, error_callback)

    def reset_password_and_connect(self, password, password_confirm, user_id, callback=None, error_callback=None):
        endpoint = "password-change-user"
        data = {
            "password": password,
            "password_confirm": password_confirm,
            "user_id": user_id
        }
        
        request, payload = self._prepare_request(endpoint, data=data)
        self._send_request(request, payload, callback, error_callback)

    # ... (autres méthodes transformées de la même manière)

    def enregistrer_etudiant(self, student_data, callback=None, error_callback=None):
        endpoint = "etudiant"
        request, payload = self._prepare_request(endpoint, data=student_data)
        self._send_request(request, payload, callback, error_callback)

    # ... (toutes les autres méthodes peuvent être adaptées de la même façon)