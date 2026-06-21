"""
Point d'entrée Mac/Linux avec interface graphique — équivalent de app.py
(Windows) + Controllers/Main_run.py + Controllers/ShowControl.py, sans les
dépendances Windows uniquement (winreg, win32security, msvcrt, ctypes.windll,
NSSM, netsh...).

Comme sur Windows, l'API FastAPI est EMBARQUÉE dans ce process (thread
uvicorn), pas un service séparé. En revanche MySQL et nginx restent gérés par
Docker Compose (services "mysql"/"certgen"/"nginx" — jamais "app", qui n'est
démarré que dans le mode headless sans GUI, voir docker-compose.yml et
scripts/start.sh). Faire tourner les deux modes en même temps provoquerait un
conflit sur le port 9001.

Prérequis sur la machine hôte : Python 3.10+, Docker, et
`pip install -r requirements.txt -r requirements-gui.txt`.
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

import requests
import uvicorn

PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)  # pour que les chemins relatifs (app/static, app/templates...) se résolvent correctement

# app/database.py lit le .env de la racine (identifiants Windows natifs : port 3306,
# mot de passe "@#1900"). Ici, l'API tourne en natif mais MySQL tourne dans Docker
# (voir docker-compose.yml, service "mysql") avec ses propres identifiants et un port
# hôte différent (3307, pour ne pas entrer en conflit avec un MySQL natif déjà présent
# sur la machine) — donc on impose ces valeurs avant l'import de app.main. load_dotenv()
# (appelé par database.py) ne écrase jamais une variable déjà présente dans os.environ.
os.environ["DB_HOST"] = "127.0.0.1"
os.environ["DB_PORT"] = "3307"
os.environ["DB_USER"] = "root"
os.environ["DB_PASSWORD"] = "ecole360_root"
os.environ["DB_NAME"] = "lekol360"

API_HOST = "0.0.0.0"
API_PORT = 9001
API_HEALTH_URL = f"http://127.0.0.1:{API_PORT}/api/v1/health"
API_BASE_URL = f"http://127.0.0.1:{API_PORT}/api/v1/"
DOCKER_SERVICES = ["mysql"]  # nginx/certgen restent disponibles via la fenêtre (voir gui/service_window.py)


def docker_compose_available() -> bool:
    try:
        subprocess.run(["docker", "compose", "version"], capture_output=True, check=True, timeout=10)
        return True
    except Exception:
        return False


def start_required_docker_services() -> bool:
    try:
        subprocess.run(
            ["docker", "compose", "up", "-d", *DOCKER_SERVICES],
            cwd=PROJECT_DIR, check=True, capture_output=True, timeout=180,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du démarrage des services Docker : {e.stderr.decode(errors='replace')}")
        return False
    except Exception as e:
        print(f"Erreur lors du démarrage des services Docker : {e}")
        return False


def start_api():
    from app.main import app
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        timeout_keep_alive=75,
        log_level="warning",
    )


def launch_and_wait_for_api(max_retries: int = 60, delay: float = 2.0) -> bool:
    threading.Thread(target=start_api, daemon=True).start()
    print("⏳ Démarrage de l'API en cours...")
    for attempt in range(max_retries):
        try:
            response = requests.get(API_HEALTH_URL, timeout=1)
            if response.status_code == 200:
                print("✅ API opérationnelle.")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(delay)
        print(end="*", flush=True)
    return False


def main():
    from gui.docker_bootstrap import ensure_docker_ready

    if not ensure_docker_ready():
        print("❌ Docker n'a pas pu être installé/démarré automatiquement.")
        print("   Mac    : https://www.docker.com/products/docker-desktop/")
        print("   Linux  : https://docs.docker.com/engine/install/")
        sys.exit(1)

    if not docker_compose_available():
        print("❌ Le plugin 'docker compose' (v2) n'est pas disponible malgré l'installation de Docker.")
        sys.exit(1)

    print("==> Démarrage de MySQL (Docker)...")
    if not start_required_docker_services():
        print("❌ Impossible de démarrer MySQL via Docker Compose.")
        sys.exit(1)

    if not launch_and_wait_for_api():
        print("❌ L'API n'a pas démarré à temps.")
        sys.exit(1)

    from PySide6.QtWidgets import QApplication
    from gui.service_window import ServiceControlWindow
    from gui.first_account import ensure_first_account

    qt_app = QApplication(sys.argv)
    qt_app.setQuitOnLastWindowClosed(False)

    # Équivalent de insert_user() dans Controllers/Main_run.py (Windows) : sur
    # une base fraîchement créée, aucun utilisateur n'existe encore et personne
    # ne pourrait se connecter depuis school_client sans cette étape.
    ensure_first_account(API_BASE_URL)

    window = ServiceControlWindow(api_base_url=API_BASE_URL)
    window.show()
    sys.exit(qt_app.exec())


if __name__ == "__main__":
    main()
