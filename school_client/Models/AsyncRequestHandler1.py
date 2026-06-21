from PySide6.QtCore import QObject, Signal, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import json

class BaseAsyncRequestHandler(QObject):
    request_complete = Signal(str, dict)  # endpoint, response_data
    request_failed = Signal(str, str, dict)  # endpoint, error_msg, response_data

    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_response)

    def _prepare_request(self, endpoint, data=None):
        url = QUrl(f"{self.base_url()}{endpoint}")
        request = QNetworkRequest(url)
        
        headers = self._get_headers()
        for key, value in headers.items():
            request.setRawHeader(key.encode(), value.encode())
        
        if data:
            return request, QByteArray(json.dumps(data).encode())
        return request, None

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self._get_token()}"
        }

    def _get_token(self):
        """À implémenter dans la classe enfant ou via composition"""
        raise NotImplementedError

    def base_url(self):
        """À implémenter dans la classe enfant"""
        raise NotImplementedError

    def _send_request(self, endpoint, method="POST", data=None):
        request, payload = self._prepare_request(endpoint, data)
        
        if method == "POST":
            reply = self.network_manager.post(request, payload)
        elif method == "GET":
            reply = self.network_manager.get(request)
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")
        
        # Stocker l'endpoint avec la reply pour identification
        reply.setProperty("endpoint", endpoint)
        return reply

    def _handle_response(self, reply):
        endpoint = reply.property("endpoint")
        try:
            raw_data = bytes(reply.readAll()).decode()
            response_data = json.loads(raw_data) if raw_data else {}
            
            if reply.error():
                error_msg = reply.errorString()
                self.request_failed.emit(endpoint, error_msg, response_data)
            else:
                self.request_complete.emit(endpoint, response_data)
        
        except json.JSONDecodeError as e:
            self.request_failed.emit(endpoint, f"Invalid JSON: {str(e)}", None)
        except Exception as e:
            self.request_failed.emit(endpoint, f"Unexpected error: {str(e)}", None)
        finally:
            reply.deleteLater()