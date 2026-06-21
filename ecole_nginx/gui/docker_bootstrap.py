"""
Installation automatique de Docker pour app_gui.py, équivalent côté Mac/Linux
du téléchargement+installation silencieuse de MySQL/Nginx fait par
Controllers/Main_run.py sur Windows.

Limite incontournable sur Mac : après l'installation du cask Homebrew, Docker
Desktop doit être lancé une première fois et l'utilisateur doit accorder
manuellement certaines permissions système (mot de passe pour le composant
privilégié, autorisation du framework de virtualisation dans Réglages
Système > Confidentialité). macOS impose ces validations humaines, il n'existe
pas de mécanisme silencieux équivalent à un service Windows pour les
contourner.

Sur Linux, l'installation est entièrement automatisable via le script officiel
get.docker.com (apt/dnf en interne), donc aucune étape manuelle requise hors
mot de passe sudo.
"""
import platform
import shutil
import subprocess
import time


def is_docker_installed() -> bool:
    if shutil.which("docker"):
        return True
    if platform.system() == "Darwin":
        from pathlib import Path
        return Path("/Applications/Docker.app").exists()
    return False


def docker_daemon_running() -> bool:
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=10)
        return True
    except Exception:
        return False


def _install_docker_macos() -> bool:
    if not shutil.which("brew"):
        print("❌ Homebrew n'est pas installé, impossible d'installer Docker automatiquement.")
        print("   Installe Homebrew (https://brew.sh) puis relance, ou installe Docker")
        print("   Desktop manuellement : https://www.docker.com/products/docker-desktop/")
        return False
    print("==> Installation de Docker Desktop via Homebrew (brew install --cask docker)...")
    print("⚠️  macOS va probablement afficher une fenêtre de mot de passe administrateur")
    print("   (parfois derrière les autres fenêtres) pour installer le composant privilégié")
    print("   de Docker — surveille tes fenêtres et saisis ton mot de passe quand demandé.")
    try:
        subprocess.run(["brew", "install", "--cask", "docker"], check=True, timeout=1800)
    except subprocess.CalledProcessError as e:
        print(f"❌ L'installation via Homebrew a échoué : {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ L'installation via Homebrew a dépassé le délai imparti (30 min). Si une fenêtre de")
        print("   mot de passe attendait une saisie, relance simplement : le téléchargement est déjà")
        print("   en cache, seule l'installation sera refaite.")
        return False
    return True


def _install_docker_linux() -> bool:
    print("==> Installation de Docker via le script officiel get.docker.com (sudo requis)...")
    try:
        subprocess.run(
            "curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sh /tmp/get-docker.sh",
            shell=True, check=True, timeout=900,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ L'installation de Docker a échoué : {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ L'installation de Docker a dépassé le délai imparti.")
        return False

    try:
        whoami = subprocess.run(["whoami"], capture_output=True, text=True, check=True).stdout.strip()
        subprocess.run(["sudo", "usermod", "-aG", "docker", whoami], check=True, timeout=30)
        print("✅ Utilisateur ajouté au groupe 'docker' (déconnexion/reconnexion nécessaire pour que")
        print("   ça prenne effet sans sudo la prochaine fois).")
    except Exception as e:
        print(f"⚠️  Impossible d'ajouter l'utilisateur au groupe docker automatiquement : {e}")

    try:
        subprocess.run(["sudo", "systemctl", "enable", "--now", "docker"], check=True, timeout=30)
    except Exception as e:
        print(f"⚠️  Impossible de démarrer le service docker automatiquement : {e}")

    return True


def _start_engine() -> None:
    try:
        # `docker desktop start` ne démarre que le moteur + l'icône de la barre des
        # menus, sans ouvrir la fenêtre Dashboard — contrairement à `open -a Docker`.
        # On évite ainsi une fenêtre Docker visible en plus de ServiceControlWindow.
        subprocess.run(["docker", "desktop", "start", "--detach"], capture_output=True, timeout=15)
    except Exception:
        subprocess.run(["open", "-a", "Docker"])


def _poll_daemon(max_retries: int, delay: float) -> bool:
    for i in range(max_retries):
        if docker_daemon_running():
            print("\n✅ Docker est opérationnel.")
            return True
        time.sleep(delay)
        if i % 6 == 5:  # toutes les ~30s : un point d'état plus parlant que des étoiles
            try:
                status = subprocess.run(
                    ["docker", "desktop", "status"], capture_output=True, text=True, timeout=10,
                ).stdout.strip().splitlines()
                state = next((l.split()[-1] for l in status if l.startswith("Status")), "?")
                print(f"\n   ... toujours en cours ({state})", end="", flush=True)
            except Exception:
                print(end="*", flush=True)
        else:
            print(end="*", flush=True)
    print()
    return False


def _wait_for_macos_daemon() -> bool:
    print("==> Démarrage du moteur Docker en arrière-plan...")
    _start_engine()
    print("⏳ En attente du démarrage du moteur Docker (peut nécessiter une validation manuelle")
    print("   la première fois : mot de passe administrateur, autorisation de virtualisation dans")
    print("   Réglages Système > Confidentialité et sécurité)...")

    # Démarrage normal : ~2 minutes de marge.
    if _poll_daemon(max_retries=24, delay=5.0):
        return True

    # Au premier démarrage après une installation fraîche, le lien réseau interne de
    # la VM peut se figer dans une boucle de reconnexion ("starting" qui ne se termine
    # jamais) — un cycle stop/start le débloque de façon fiable. On le tente une fois
    # avant d'abandonner, avec une marge plus large (~7 min) pour la création du disque
    # virtuel qu'un premier démarrage peut nécessiter.
    print("⚠️  Toujours pas démarré, nouvelle tentative (arrêt puis redémarrage du moteur)...")
    try:
        subprocess.run(["docker", "desktop", "stop"], capture_output=True, timeout=60)
    except Exception:
        pass
    time.sleep(5)
    _start_engine()
    return _poll_daemon(max_retries=84, delay=5.0)


def ensure_docker_ready() -> bool:
    """
    Installe Docker si absent puis s'assure que le démon répond. Retourne True
    seulement si docker (et le plugin compose v2) sont prêts à l'emploi.
    """
    system = platform.system()

    if not is_docker_installed():
        print("⚠️  Docker n'est pas installé sur cette machine.")
        if system == "Darwin":
            ok = _install_docker_macos()
        elif system == "Linux":
            ok = _install_docker_linux()
        else:
            print(f"❌ Installation automatique non supportée sur {system}.")
            ok = False
        if not ok or not is_docker_installed():
            return False

    if docker_daemon_running():
        return True

    if system == "Darwin":
        return _wait_for_macos_daemon()
    elif system == "Linux":
        try:
            subprocess.run(["sudo", "systemctl", "start", "docker"], check=True, timeout=30)
        except Exception as e:
            print(f"❌ Impossible de démarrer le service docker : {e}")
            return False
        return docker_daemon_running()

    return False
