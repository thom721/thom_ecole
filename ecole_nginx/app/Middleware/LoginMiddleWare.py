from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware pour capturer l'IP et l'utilisateur courant
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        # Récupérer l'IP du client
        client_ip = request.client.host
        
        # Stocker dans le request state pour utilisation ultérieure
        request.state.client_ip = client_ip
        
        # Traiter la requête
        response = await call_next(request)
        
        return response