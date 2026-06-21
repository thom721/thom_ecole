import sys
import types

# Crée un faux module redis pour bloquer l'import automatique
def _make_fake_module(name):
    mod = types.ModuleType(name)
    mod.__spec__ = None
    sys.modules[name] = mod
    return mod

# Bloque les modules Redis que limits essaie d'importer
for _mod in [
    "limits.storage.redis",
    "limits.aio.storage.redis",
]:
    if _mod not in sys.modules:
        _make_fake_module(_mod)

# Patch get_package_data pour éviter le FileNotFoundError .lua
try:
    import limits.util as _limits_util
    _limits_util.get_package_data = lambda *a, **kw: ""
except Exception:
    pass


from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from app.Routes import Etudiants, RAcademic,RCours,RProgramme,dashboard,RCoursEtudiant,RParamExam,RAnneAcademique,RClasses,RInscription,RPaiement,RPaiementParam,RClientInfos,RProfile,RAuth,RRolePermission,RVente,RLog,RNotes,RSavePaiement,Initialisation,Returns,RTransaction,RPromus,REvents,RNews,RCategory,RPresences


from app.Routes.pdf import BulletinPrint, paiement_recu,GlobalRepport,PaymentRepport,Register_report,VenteRecu,RegisterRepport,PedagogicRepport,MasBulletinPrint,PedaRepport,RPRepport
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles 
from pydantic import ValidationError

from app.Models.MModels import User,Etudiant
from app.Models.MFinancials import Paiement,ParametrePaiement,ParamExam,OtherTransaction,Vente,Depense
from app.Models.MSystems import Log
from app.database import SessionLocal, engine, Base,get_engine_dynamically
import os
import sys
from pathlib import Path
from app.Helper.get_real_path import get_real_path
import logging.config  # Ajoute cette ligne explicitement
import logging
from alembic.config import Config
from alembic import command
from sqlalchemy import inspect 

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

#   --include-data-dir=venv/Lib/site-packages/limits/resources=limits/resources \
#   --include-package=limits \
#   --include-package=slowapi \

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://" 
)
 
app = FastAPI(   root_path="/app",
    title="API Gestion Scolaire - Le Mignon",
    description="API REST pour la gestion d'établissement scolaire",
    version="1.0.0"
    # docs_url=None, redoc_url=None, openapi_url=None
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
def setup_weasyprint_dlls(): 
    gtk_bin_path_str = get_real_path("gtk_runtime") 

    fonts_conf_path = Path(gtk_bin_path_str) / "etc" / "fonts" / "fonts.conf"
    bin_path = Path(gtk_bin_path_str) / "bin"
    user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
    # server_path = os.path.join(
    # user_profile, "AppData", "Local", ".ecole_360"
    #         )
    server_path = os.getcwd()
    if sys.platform == "win32": 
        if os.path.exists(bin_path): 
            gtk_path_obj = bin_path.resolve() 
            
            final_path = str(gtk_path_obj)
            
            os.add_dll_directory(final_path)
            os.environ['PATH'] = final_path + os.pathsep + os.environ['PATH']
            
            # print(f"✅ DLL GTK chargées depuis : {final_path}")

            if fonts_conf_path.exists():
                os.environ['FONTCONFIG_FILE'] = str(fonts_conf_path.resolve())
                # On définit aussi le dossier racine de fontconfig
                os.environ['FONTCONFIG_PATH'] = str(fonts_conf_path.parent.resolve())
                print(f"✅ Configuration Fontconfig liée.")
        else:
            dir = Path(os.path.join(server_path,"gtk_runtime","bin"))
            fonts_conf_path = Path(os.path.join(server_path,"gtk_runtime","etc" , "fonts" , "fonts.conf"))
            gtk_path_obj = dir.resolve()
            final_path = str(gtk_path_obj)
            
            os.add_dll_directory(final_path)
            
            
            os.environ['PATH'] = final_path + os.pathsep + os.environ['PATH']
            
            # print(f"✅ DLL GTK chargées depuis : {final_path}")
            if fonts_conf_path.exists():
                os.environ['FONTCONFIG_FILE'] = str(fonts_conf_path.resolve())
                # On définit aussi le dossier racine de fontconfig
                os.environ['FONTCONFIG_PATH'] = str(fonts_conf_path.parent.resolve())
                # print(f"✅ Configuration Fontconfig liée.")
            else:
                print(f"Not found.")
 
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
            message = f"Le champ '{field_name}' est requis ou trop court"
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

# Gestionnaire pour les erreurs de validation Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gestionnaire personnalisé pour les erreurs de validation"""
    errors = format_validation_error(exc)
    print(errors)
    # Create a simple, clean error response
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "errors": errors,#"Erreur de validation www",
            "message": "Veuillez vérifier les champs suivants",
            "fields": errors
        }
    )
    # errors = exc.errors()
    # print(f"Erreur de validation : {exc.errors()}")
    # # Formatage des erreurs
    # formatted_errors = []
    # for error in errors:
    #     error_dict = {
    #         "loc": error.get("loc", []),
    #         "msg": str(error.get("msg", "")),  # Convertir en string
    #         "type": error.get("type", ""),
    #         "input": str(error.get("input", "")) if error.get("input") is not None else None
    #     }
        
    #     # Nettoyer les données pour la sérialisation JSON
    #     if "ctx" in error and error["ctx"]:
    #         # Convertir le contexte en string ou le supprimer
    #         try:
    #             error_dict["ctx"] = str(error["ctx"])
    #         except:
    #             error_dict["ctx"] = "Context not serializable"
        
    #     formatted_errors.append(error_dict)
    
    # return JSONResponse(
    #     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    #     content={
    #         "success": False,
    #         "message": "Erreur de validation des données",
    #         "errors": formatted_errors
    #     }
    # )

# Gestionnaire pour les erreurs génériques
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Gestionnaire pour toutes les autres exceptions"""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Pour les ValueError, extraire le message
    if isinstance(exc, ValueError):
        error_message = str(exc)
    else:
        error_message = "Une erreur interne est survenue"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": error_message,
            "error_type": exc.__class__.__name__
        }
    )

def get_app_root():
    if "NUITKA_ONEFILE_PARENT" in os.environ or '__compiled__' in globals(): 
        return os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))

    return os.path.abspath(".")
APP_ROOT = get_app_root()
@app.on_event("startup")
def startup_event():
    """
    Enregistrer tous les observers au démarrage de l'application
    """   
    # alembic -c app/alembic.ini revision --autogenerate -m "create_paiement_statuts"
    # pass
    ALEMBIC_INI = os.path.join(APP_ROOT, "app", "alembic.ini")
    ALEMBIC_SCRIPTS = os.path.join(APP_ROOT, "app", "alembic")

    print(f"APP_ROOT  {APP_ROOT} ALEMBIC_INI  {ALEMBIC_INI} ALEMBIC_SCRIPTS  {ALEMBIC_SCRIPTS}")

    engine = get_engine_dynamically() 
    url_db = str(engine.url).replace('%', '%%') 

    try:  
        # pass
        alembic_cfg = Config(ALEMBIC_INI) 
        alembic_cfg.set_main_option("script_location", ALEMBIC_SCRIPTS) 
        alembic_cfg.set_main_option("sqlalchemy.url", url_db)
        
        inspector = inspect(engine) 
        
        if not inspector.has_table("users"): 
            print(" Création des tables dans la base de données...")
            Base.metadata.create_all(bind=engine) 
            command.stamp(alembic_cfg, "head") 
        else: 
            command.upgrade(alembic_cfg, "head")
            
    except Exception as e:
        print(f'An exception occurred  on running base  {e}')
    
    db = SessionLocal()       
    try: 
        User.register_observers(db) 
        Paiement.register_observers(db)
        Etudiant.register_observers(db)
        OtherTransaction.register_observers(db)
        Vente.register_observers(db)
        Depense.register_observers(db)
        ParametrePaiement.register_observers(db)
    finally:
        db.close()
 
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# print(os.path.abspath("app/static"))
setup_weasyprint_dlls()

try:
    from weasyprint import HTML
    print("🚀 WeasyPrint est prêt !")
except Exception as e:
    print(f"❌ Erreur WeasyPrint : {e}")
    
 
# Inclusion des routers
app.include_router(Initialisation.router)
app.include_router(RAuth.router)
app.include_router(dashboard.router)
app.include_router(dashboard.router_class)
app.include_router(Etudiants.router)
app.include_router(RCours.router)
app.include_router(RProgramme.router)
app.include_router(RAnneAcademique.router)
app.include_router(RClasses.router)
app.include_router(RInscription.router)
app.include_router(RPaiement.router)
app.include_router(RVente.router)
app.include_router(RPaiementParam.router)
app.include_router(RSavePaiement.router_paie)
app.include_router(RParamExam.router)
app.include_router(RCoursEtudiant.router)
app.include_router(RAcademic.router_annee)
app.include_router(RAcademic.router_niveau)
app.include_router(RAcademic.router_faculte)
app.include_router(RAcademic.router_classe)
app.include_router(RAcademic.router_professeur)
app.include_router(RAcademic.router_personnel)
app.include_router(RClientInfos.router)
app.include_router(RProfile.router)
app.include_router(RRolePermission.router)
app.include_router(RNotes.router_note)
app.include_router(RLog.router)
app.include_router(Returns.router_return)
app.include_router(RPRepport.router)
app.include_router(RTransaction.router_transac)
app.include_router(RPromus.router)

app.include_router(REvents.router)
app.include_router(RNews.router)
app.include_router(RCategory.router)
app.include_router(RPresences.router)
 

# {"classe": "All", "date_debut": "2026-01-20", "date_fin": "2026-01-20", "versement": "tous les versements"}
# ==============================PDF==========================================================
app.include_router(paiement_recu.router)
app.include_router(GlobalRepport.router)
app.include_router(PaymentRepport.router)
app.include_router(Register_report.router)
app.include_router(VenteRecu.router)
app.include_router(RegisterRepport.router)
app.include_router(PedagogicRepport.router)
app.include_router(BulletinPrint.router)
app.include_router(MasBulletinPrint.router)
app.include_router(PedaRepport.router)



@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API de Gestion Scolaire - Le Mignon",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

 