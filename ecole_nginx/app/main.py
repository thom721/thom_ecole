from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from time import time
from app.Routes import Etudiants, RAcademic,RCours,RProgramme,dashboard,RCoursEtudiant,RParamExam,RAnneAcademique,RClasses,RInscription,RPaiement,RPaiementParam,RClientInfos,RProfile,RAuth,RRolePermission,RVente,RLog,RNotes,RSavePaiement,Initialisation,Returns,RTransaction,RPromus,REvents,RNews,RCategory,RPresences,RFormations,RPageSections

from app.Routes.pdf import BulletinPrint, paiement_recu,GlobalRepport,PaymentRepport,Register_report,VenteRecu,RegisterRepport,PedagogicRepport,MasBulletinPrint,PedaRepport,RPRepport,RExcelExport
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
from app.Helper.license_check import ensure_trial_license, is_license_valid

# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# from slowapi.middleware import SlowAPIMiddleware

#   --include-data-dir=venv/Lib/site-packages/limits/resources=limits/resources \
#   --include-package=limits \
#   --include-package=slowapi \

# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["100/minute"],
#     storage_uri="memory://" 
# )

_req_log: dict = {}
_req_count = 0

# Limites spécifiques par chemin (max_requêtes, fenêtre_en_secondes).
# Les endpoints sensibles (login, reset password) ont une limite bien plus stricte
# que le reste de l'API pour réduire le risque de brute-force.
_RATE_LIMITS = {
    "/api/v1/auth/login": (10, 60),
    "/api/v1/password-reset-request": (5, 60),
    "/api/v1/password-reset-verify": (10, 60),
}
_DEFAULT_RATE_LIMIT = (100, 60)
 
app = FastAPI(   root_path="/app",
    title="API Gestion Scolaire - Le Mignon",
    description="API REST pour la gestion d'établissement scolaire",
    version="1.0.0"
    # docs_url=None, redoc_url=None, openapi_url=None
    )

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
# app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def rate_limit_middleware(request: Request, call_next):
    global _req_count

    ip = request.client.host if request.client else "unknown"
    now = time()
    max_requests, window = _RATE_LIMITS.get(request.url.path, _DEFAULT_RATE_LIMIT)
    key = f"{request.url.path}:{ip}"

    recent = [t for t in _req_log.get(key, []) if now - t < window]
    if len(recent) >= max_requests:
        _req_log[key] = recent
        return JSONResponse(status_code=429, content={"detail": "Trop de requêtes, réessayez dans une minute."})

    recent.append(now)
    _req_log[key] = recent

    # Purge périodique des clés inactives pour éviter une fuite mémoire
    # (sans cette purge, chaque IP/chemin vu une seule fois restait en mémoire indéfiniment).
    _req_count += 1
    if _req_count % 1000 == 0:
        for stale_key, timestamps in list(_req_log.items()):
            if not timestamps or now - timestamps[-1] > 300:
                _req_log.pop(stale_key, None)

    return await call_next(request)

app.middleware("http")(rate_limit_middleware)
 
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


def is_compiled() -> bool:
    return (
        "NUITKA_ONEFILE_PARENT" in os.environ
        or '__compiled__' in globals()
        or getattr(sys, 'frozen', False)
    )


APP_ROOT = get_app_root()
@app.on_event("startup")
def startup_event():
    """
    Enregistrer tous les observers au démarrage de l'application
    """
    # Vérification de licence (Mac/Linux uniquement) : sur Windows, la licence
    # est déjà gérée avant ce point par Controllers/Main_run.py (app.py), donc
    # on ne change rien à ce comportement. Comme côté Windows, une licence
    # invalide/expirée n'empêche pas l'API de démarrer : avertissement seulement.
    if sys.platform != "win32":
        try:
            key, expiration_date = ensure_trial_license()
            if is_license_valid():
                print(f" Licence active jusqu'au {expiration_date} (clé: {key})")
            else:
                print(f" ATTENTION : licence expirée ou invalide (clé: {key}, expirée le {expiration_date}).")
                print(" Contactez le support pour obtenir une nouvelle clé d'activation.")
        except Exception as e:
            print(f"Erreur lors de la vérification de licence : {e}")

    # alembic -c app/alembic1.ini revision --autogenerate -m "create_paiement_statuts"
    ALEMBIC_INI = os.path.join(APP_ROOT, "app", "alembic1.ini")
    ALEMBIC_SCRIPTS = os.path.join(APP_ROOT, "app", "alembic")

    print(f"APP_ROOT  {APP_ROOT} ALEMBIC_INI  {ALEMBIC_INI} ALEMBIC_SCRIPTS  {ALEMBIC_SCRIPTS}")

    engine = get_engine_dynamically()

    try:
        inspector = inspect(engine)
        alembic_cfg = Config(ALEMBIC_INI)
        alembic_cfg.set_main_option("script_location", ALEMBIC_SCRIPTS)
        # sourceless=true (app/alembic1.ini) n'a d'utilité QUE pour le build
        # compilé (Nuitka), où seuls des .pyc propres sont expédiés, sans
        # __pycache__ — voir scripts/compile_alembic_versions.py. En dev, les
        # .py sources sont présents, donc inutile ; pire, l'activer ferait
        # aussi scanner __pycache__/ (gitignoré, jamais nettoyé), où peuvent
        # traîner d'anciens .pyc orphelins (révisions renommées au fil du
        # dev, parfois compilés sous une autre version de Python) →
        # "bad magic number" sur l'application des migrations.
        if not is_compiled():
            alembic_cfg.set_main_option("sourceless", "false")

        if not inspector.has_table("users"):
            # Base neuve (ex: Docker Mac/Linux) : on crée le schéma directement depuis
            # les modèles à jour, puis on marque la base comme étant à la dernière
            # révision Alembic (inutile de rejouer migration par migration un schéma
            # qu'on vient de créer dans son état le plus récent).
            print(" Base de données vide détectée : création du schéma...")
            Base.metadata.create_all(bind=engine)
            command.stamp(alembic_cfg, "head")
        else:
            # Base existante (ex: installation Windows en production) : applique
            # uniquement les migrations pas encore jouées. Si la base est déjà à
            # jour, c'est un no-op. Erreur capturée séparément pour ne jamais
            # empêcher le démarrage de l'API à cause d'un souci de migration.
            try:
                print(" Vérification des migrations Alembic en attente...")
                command.upgrade(alembic_cfg, "head")
            except Exception as mig_err:
                print(f"Erreur lors de l'application des migrations Alembic: {mig_err}")

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
        # Seed sections page d'accueil
        from app.services.home_seed import seed_home, seed_formations
        seed_home(db)
        seed_formations(db)
    finally:
        db.close()
 
from app.Helper.persistent_storage import ensure_persistent_static
app.mount("/static", StaticFiles(directory=str(ensure_persistent_static())), name="static")
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
app.include_router(RExcelExport.router)
app.include_router(RTransaction.router_transac)
app.include_router(RPromus.router)

app.include_router(REvents.router)
app.include_router(RFormations.router)
app.include_router(RPageSections.router)
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

 