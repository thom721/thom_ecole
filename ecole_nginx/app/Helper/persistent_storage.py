"""Répertoire persistant pour les fichiers uploadés à l'exécution (logo,
documents, photos de profil, images d'actualités/formations/événements).

Contrairement à app/static, qui vit À L'INTÉRIEUR du dossier d'installation
et est donc écrasé chaque fois qu'un nouveau build est dézippé par-dessus
l'ancien, ce dossier vit hors du dossier d'installation et survit aux mises
à jour — même principe que LICENSE_FILE dans app/Helper/license_check.py.

Sur Windows, le serveur tourne en service NSSM sous le compte LocalSystem
(voir Controllers/Main_run.py, service "Esystem", ObjectName=LocalSystem,
"démarre sans session"). Sous ce compte, Path.home() résoudrait vers le
profil système caché (C:\\Windows\\System32\\config\\systemprofile) — un
dossier protégé que certains antivirus/EDR surveillent sur les PC clients.
On utilise donc %ProgramData% à la place : même valeur que le service tourne
en LocalSystem ou que l'exe soit lancé manuellement par un admin, et c'est
l'emplacement standard Windows pour des données d'application partagées.
Sur Mac/Linux, app_gui.py tourne nativement sous la session de l'utilisateur
connecté (pas de notion de service système équivalent), donc Path.home()
reste correct et cohérent avec license_check.py.
"""
import os
import platform
import shutil
from pathlib import Path

from app.Helper.get_real_path import get_app_root


def _default_base_dir() -> Path:
    if platform.system() == "Windows":
        program_data = os.environ.get("ProgramData", r"C:\ProgramData")
        return Path(program_data) / ".ecole_360" / "static"
    return Path.home() / ".ecole_360" / "static"


# Surchargeable via variable d'env (utilisé par le service "app" headless du
# docker-compose.yml, qui pointe vers le volume Docker monté — voir LICENSE_FILE
# dans license_check.py pour le même principe).
BASE_DIR = Path(os.getenv("STATIC_DATA_DIR", str(_default_base_dir())))

DOCUMENTS_DIR = BASE_DIR / "documents"
LOGO_DIR = BASE_DIR / "logo"
PROFILE_DIR = BASE_DIR / "profile"
PROFILE_STUDENT_DIR = PROFILE_DIR / "student"
EVENTS_DIR = BASE_DIR / "uploads" / "events"
NEWS_DIR = BASE_DIR / "uploads" / "news"
FORMATIONS_DIR = BASE_DIR / "uploads" / "formations"

_ALL_DIRS = [DOCUMENTS_DIR, LOGO_DIR, PROFILE_STUDENT_DIR, EVENTS_DIR, NEWS_DIR, FORMATIONS_DIR]

# Ancien emplacement (à l'intérieur du dossier d'installation) — conservé
# uniquement pour migrer une fois les fichiers déjà uploadés par une
# installation existante datant d'avant ce changement. Résolu via
# get_app_root() (pas un chemin relatif au cwd) pour rester fiable peu
# importe comment l'exe est lancé (service NSSM, raccourci, double-clic).
_LEGACY_DIR = Path(get_app_root()) / "app" / "static"


def ensure_persistent_static() -> Path:
    first_run = not BASE_DIR.exists()

    for d in _ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)

    if first_run and _LEGACY_DIR.exists():
        _migrate_legacy_files()

    return BASE_DIR


def _migrate_legacy_files() -> None:
    for d in _ALL_DIRS:
        legacy_sub = _LEGACY_DIR / d.relative_to(BASE_DIR)
        if not legacy_sub.exists():
            continue
        for item in legacy_sub.iterdir():
            if item.is_file():
                shutil.copy2(item, d / item.name)
