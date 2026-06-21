from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.database import engine, Base
from app.routers import courses, gps_tracking,auth_unified,auth,ride,firebase_route,driver_location,Notification
from app.routers.Websocket.driver_ws import router as driver_ws_router
from app.routers.Websocket.client_ws import router as client_ws_router
from app.routers.Websocket.rides_ws import router as rides_ws_router

from app.social_auth_service import social_auth_service
# from app.services.firebase_service import firebase_service
from app.services.notification_service import notification_service
from pathlib import Path
from typing import List
import logging
import firebase_admin
from fastapi.staticfiles import StaticFiles
import os
logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Gestion du cycle de vie de l'application"""
#     # Startup: Créer les tables si elles n'existent pas
#     # Note: En production, utiliser Alembic pour les migrations
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
    
#     yield
    
#     # Shutdown: Nettoyer les ressources
#     await engine.dispose()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # ✅ NOUVEAU (sync)
#     Base.metadata.create_all(bind=engine)
#     yield
#     # Cleanup si nécessaire




@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup et shutdown de l'application"""
    print("🚀 Démarrage de l'application...")
 
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tables MySQL créées/vérifiées avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        raise
    
    # Firebase (optionnel)
    firebase_path = settings.firebase_credentials_path or "/app/backend/firebase-credentials.json"
    if os.path.exists(firebase_path):
        print("✅ Firebase credentials trouvé")
    else:
        print(f"⚠️ Fichier Firebase credentials non trouvé: {firebase_path}")
        print("Les fonctions Firebase seront simulées")
    
    yield
    
    # Shutdown
    print("👋 Arrêt de l'application...")
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="""
    API pour application VTC et Covoiturage
    
    ## Fonctionnalités principales
    
    * **Courses VTC** - Trajets à la demande type Uber
    * **Covoiturage** - Trajets partagés planifiés
    * **Paiements** - MonCash, NatCash, Carte
    * **Avis** - Système de notation des chauffeurs
    * **Géolocalisation** - Suivi GPS en temps réel via WebSocket
    
    ## Authentification
    
    L'authentification se fait via Firebase (firebase_uid)
    
    ## WebSocket GPS Tracking
    
    - `/ws/driver/{id}/gps` - Chauffeur envoie sa position
    - `/ws/track/{driver_id}` - Client suit un chauffeur
    - `/ws/admin/tracking` - Admin voit tous les chauffeurs
    """,
    version="1.0.0",
    lifespan=lifespan
)

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("🚀 Démarrage de l'application...")
    
    # Vérifier Firebase
    if firebase_admin._apps:
        app = firebase_admin.get_app()
        logger.info(f"✅ Firebase prêt - Projet: {app.project_id}")
    else:
        logger.warning("⚠️ Firebase non initialisé")
        # Réessayer l'initialisation
        notification_service._initialize_firebase()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = Path(__file__).resolve().parent

static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")
# Configuration CORS

def format_validation_error(exc: RequestValidationError) -> dict:
    """Format Pydantic validation errors into user-friendly messages"""
    errors = {}
    for error in exc.errors():
        field_name = error['loc'][-1] if error['loc'] else 'unknown'
        error_type = error['type']
        
        # Create user-friendly messages
        if error_type == 'missing':
            message = f"Le champ '{field_name}' est requis"
        elif error_type == 'value_error.email':
            message = f"L'adresse email '{field_name}' n'est pas valide"
        elif error_type == 'type_error.integer':
            message = f"Le champ '{field_name}' doit être un nombre entier"
        elif error_type == 'type_error.float':
            message = f"Le champ '{field_name}' doit être un nombre"
        elif error_type == 'type_error.boolean':
            message = f"Le champ '{field_name}' doit être vrai ou faux"
        elif 'string_too_short' in error_type:
            message = f"Le champ '{field_name}' est trop court"
        elif 'string_too_long' in error_type:
            message = f"Le champ '{field_name}' est trop long"
        elif error_type == 'value_error':
            message = error.get('msg', f"Valeur invalide pour '{field_name}'")
        else:
            message = error.get('msg', f"Erreur de validation pour '{field_name}'")
        
        errors[field_name] = message
    
    return errors

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clean responses"""
    errors = format_validation_error(exc)
    print(errors)
    # Create a simple, clean error response
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": errors,#"Erreur de validation www",
            "message": "Veuillez vérifier les champs suivants",
            "fields": errors
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with clean responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors""" 
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Une erreur inattendue s'est produite",
            "message": "Veuillez réessayer plus tard"
        }
    )

def format_validation_error(exc: RequestValidationError) -> dict:
    """Format Pydantic validation errors into user-friendly messages"""
    errors = {}
    for error in exc.errors():
        field_name = error['loc'][-1] if error['loc'] else 'unknown'
        error_type = error['type']
        error_msg = error.get('msg', '')
        
        # Create user-friendly messages
        if error_type == 'missing':
            message = f"Le champ '{field_name}' est requis"
        elif error_type == 'value_error.email' or 'email' in error_msg.lower():
            message = f"L'adresse email n'est pas valide"
        elif error_type == 'type_error.integer':
            message = f"Le champ '{field_name}' doit être un nombre entier"
        elif error_type == 'type_error.float':
            message = f"Le champ '{field_name}' doit être un nombre"
        elif error_type == 'type_error.boolean':
            message = f"Le champ '{field_name}' doit être vrai ou faux"
        elif 'string_too_short' in error_type:
            message = f"Le champ '{field_name}' est trop court"
        elif 'string_too_long' in error_type:
            message = f"Le champ '{field_name}' est trop long"
        elif 'literal_error' in error_type or 'Input should be' in error_msg:
            # Extract valid values from error message
            if 'passenger' in error_msg and 'driver' in error_msg:
                message = f"Le rôle doit être 'passenger' ou 'driver'"
            else:
                message = error_msg
        elif error_type == 'value_error':
            message = error.get('msg', f"Valeur invalide pour '{field_name}'")
        else:
            message = error.get('msg', f"Erreur de validation pour '{field_name}'")
        errors[field_name] = message
    
    return errors
        

app.include_router(courses.router, prefix="/api")
app.include_router(gps_tracking.router, prefix="/api")
app.include_router(auth_unified.router, prefix="/api")
app.include_router(firebase_route.router, prefix="/api") 
app.include_router(ride.router, prefix="/api")
app.include_router(Notification.router, prefix="/api")
app.include_router(driver_location.router, prefix="/api")
app.include_router(driver_ws_router)
app.include_router(client_ws_router)
app.include_router(rides_ws_router)

# scp -r /chemin/local/api2 root@srv817831:~/lekol360/api2
# rsync -avz /chemin/local/api2/ root@srv817831:~/lekol360/api2/
 

# Routes de base
@app.get("/")
async def root():
    """Endpoint racine - Informations sur l'API"""
    return {
        "message": "Bienvenue sur l'API Kikip",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "services": {
            "courses": "Courses VTC à la demande",
            "rides": "Covoiturage planifié",
            "payments": "Gestion des paiements",
            "reviews": "Système d'avis",
            "gps_tracking": "Tracking GPS temps réel (WebSocket)"
        },
        "websockets": {
            "driver_gps": "/ws/driver/{id}/gps",
            "track_driver": "/ws/track/{driver_id}",
            "admin_tracking": "/ws/admin/tracking"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    # Importer ici pour éviter l'erreur de circular import
    from app.routers.gps_tracking import manager
    
    return {
        "status": "healthy",
        "database": "connected",
        "gps_tracking": {
            "drivers_online": len(manager.driver_connections),
            "active_trackings": sum(len(v) for v in manager.tracking_connections.values()),
            "admin_sessions": len(manager.admin_connections)
        }
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.debug
#     )