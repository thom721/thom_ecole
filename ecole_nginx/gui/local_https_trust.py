"""
Installe automatiquement la CA auto-signée générée par le service "certgen"
dans le magasin de confiance du système et ajoute l'entrée /etc/hosts
nécessaire — équivalent de scripts/setup-local-https.sh, mais déclenché
automatiquement au démarrage de "nginx" depuis la fenêtre de contrôle
(gui/service_window.py), pour ne plus avoir à lancer ce script à la main à
chaque nouvelle installation.

Idempotent : si l'entrée hosts et la CA sont déjà en place, ne fait rien (pas
de prompt sudo aux lancements suivants). Nécessite un mot de passe sudo, lu
directement depuis le terminal qui a lancé l'app (même principe que
gui/docker_bootstrap.py). Best-effort : un échec ici n'empêche jamais
nginx/l'API de fonctionner, seul l'accès HTTPS à https://aplekol360.local
depuis un navigateur ou un poste client en dépend.
"""
import platform
import subprocess
from pathlib import Path

DOMAIN = "aplekol360.local"
HOSTS_FILE = Path("/etc/hosts")
LINUX_CA_PATH = Path("/usr/local/share/ca-certificates/aplekol360-ca.crt")


def _hosts_entry_present() -> bool:
    try:
        return DOMAIN in HOSTS_FILE.read_text()
    except OSError:
        return False


def _ca_already_trusted() -> bool:
    system = platform.system()
    if system == "Linux":
        return LINUX_CA_PATH.exists()
    if system == "Darwin":
        result = subprocess.run(
            ["security", "find-certificate", "-c", f"{DOMAIN} Root CA",
             "/Library/Keychains/System.keychain"],
            capture_output=True, timeout=10,
        )
        return result.returncode == 0
    return True  # OS non supporté pour l'automatisation : ne bloque pas le démarrage


def is_local_https_trusted() -> bool:
    return _hosts_entry_present() and _ca_already_trusted()


def ensure_local_https_trusted(project_dir: Path) -> None:
    if is_local_https_trusted():
        return

    print(f"==> Configuration HTTPS locale ({DOMAIN}) — un mot de passe sudo peut être demandé dans ce terminal...")

    if not _hosts_entry_present():
        try:
            subprocess.run(
                f'echo "127.0.0.1 {DOMAIN}" | sudo tee -a {HOSTS_FILE}',
                shell=True, check=True, timeout=30,
            )
        except Exception as e:
            print(f"❌ Impossible d'ajouter {DOMAIN} à {HOSTS_FILE} : {e}")
            return

    if _ca_already_trusted():
        print(f"✅ {DOMAIN} configuré (hosts + CA déjà de confiance).")
        return

    export_dir = project_dir / "docker-certs-export"
    export_dir.mkdir(exist_ok=True)
    ca_path = export_dir / "ca.pem"
    try:
        subprocess.run(
            ["docker", "compose", "cp", "certgen:/certs/ca.pem", str(ca_path)],
            cwd=project_dir, check=True, timeout=30,
        )
    except Exception as e:
        print(f"❌ Impossible de récupérer le certificat CA depuis certgen : {e}")
        return

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(
                ["sudo", "security", "add-trusted-cert", "-d", "-r", "trustRoot",
                 "-k", "/Library/Keychains/System.keychain", str(ca_path)],
                check=True, timeout=30,
            )
        elif system == "Linux":
            subprocess.run(["sudo", "cp", str(ca_path), str(LINUX_CA_PATH)], check=True, timeout=30)
            subprocess.run(["sudo", "update-ca-certificates"], check=True, timeout=30)
        else:
            print(f"❌ OS non supporté pour l'installation automatique de la CA : {system}")
            return
    except Exception as e:
        print(f"❌ Installation de la CA dans le magasin système a échoué : {e}")
        return

    print(f"✅ {DOMAIN} configuré (hosts + CA de confiance). https://{DOMAIN} devrait être accessible sans avertissement SSL.")
