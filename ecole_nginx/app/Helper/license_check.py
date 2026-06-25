"""
Vérification de licence pour les installations Mac/Linux (Docker).

Reprend le mécanisme MAC + HMAC + chiffrement Fernet de
Helper/server_key_generate.py (installateur Windows natif) :
- l'adresse MAC de la machine sert d'identifiant
- une clé d'activation est un HMAC-SHA256(SECRET_KEY, mac-date_expiration-
  days_valid-SECRET_KEY) encodé en base32, donc vérifiable localement sans
  serveur externe — format identique à infini-software/backend/genere_key.py
  (même SECRET_KEY, même construction du message), pour qu'une clé émise par
  l'un soit vérifiable par l'autre.
- la clé + sa date d'expiration + days_valid sont stockés chiffrés (Fernet,
  clé dérivée de la MAC) dans un fichier au lieu du registre Windows
  (QSettings)

Volontairement NON repris : Helper/save_onReg.py (LicenseManager), qui calcule
un identifiant matériel via des commandes Windows uniquement (wmic) et stocke
dans le registre — aucun équivalent Linux/Mac, et redondant avec le contrôle
MAC déjà utilisé comme verrou réel par is_license_valid() côté Windows.

Comme sur Windows (Controllers/Main_run.py install_and_config()), une licence
invalide/expirée n'empêche PAS le démarrage de l'API : seul un avertissement
est affiché au démarrage.
"""
import os
import re
import json
import uuid
import base64
import hashlib
import hmac
import platform
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken

# Secret PARTAGÉ avec infini-software (même variable d'env KEY_SECRET côté
# infini-software/backend/genere_key.py) : c'est ce secret qui rend une clé
# infalsifiable, pas le chiffrement Fernet du fichier local (qui ne protège
# que la confidentialité du contenu sur disque, pas son authenticité — voir
# is_license_valid() qui revérifie le HMAC). Le faire dériver d'une variable
# d'env permet de le faire évoluer sans toucher au code, mais TOUTE
# modification doit être déployée à l'identique sur infini-software ET sur
# chaque installation ecole_nginx existante, sous peine d'invalider toutes
# les clés déjà émises. "CLE_SECRETE_PERSO" reste la valeur par défaut pour
# rester compatible avec les installations déjà déployées sans cette
# variable d'env.
SECRET_KEY = os.environ.get("KEY_SECRET", "CLE_SECRETE_PERSO")

# Par défaut : dossier caché dans le profil utilisateur (équivalent Mac/Linux du
# AppData/Local/.ecole_360 utilisé sur Windows), pour app_gui.py qui tourne en
# natif sur la machine. Le service "app" du docker-compose.yml (mode headless,
# sans GUI) surcharge explicitement LICENSE_FILE vers le volume Docker monté.
LICENSE_FILE = os.getenv("LICENSE_FILE", str(Path.home() / ".ecole_360" / "license.json"))
TRIAL_DAYS = 30

# Cache local de l'adresse MAC détectée — voir get_host_mac(). Même dossier
# que LICENSE_FILE pour que le mode headless (volume Docker monté) persiste
# correctement aussi.
MAC_CACHE_FILE = os.getenv("MAC_CACHE_FILE", str(Path(LICENSE_FILE).parent / "machine_mac.txt"))


def get_host_mac() -> str:
    """
    Adresse MAC utilisée comme identifiant machine.

    Priorité à la variable d'environnement HOST_MAC_ADDRESS, calculée sur la
    machine hôte par scripts/start.sh : uuid.getnode() exécuté DANS le
    conteneur lirait l'interface réseau virtuelle du conteneur, pas celle de
    la machine hôte, ce qui rendrait la licence instable entre deux recréations
    du conteneur.

    Sinon, uuid.getnode() seul n'est PAS fiable sur Mac : il renvoie l'adresse
    d'une interface réseau quelconque parmi celles actives au moment de
    l'appel (Wi-Fi, pont virtuel, hotspot...), qui peut changer d'un appel à
    l'autre (constaté : Wi-Fi déconnecté/reconnecté → interface différente
    énumérée en premier ; en plus, macOS randomise l'adresse Wi-Fi visible par
    réseau — "Private Wi-Fi Address"). On détecte donc une seule fois puis on
    réutilise la même valeur via un fichier local, pour que la licence/le mac
    envoyé à infini-software ne changent jamais après la première détection.

    Sur Windows, on utilise "getmac" plutôt que uuid.getnode() : il liste
    toutes les interfaces (Ethernet, Wi-Fi, Bluetooth, adaptateurs virtuels
    VPN/Hyper-V/VirtualBox...) avec leur statut, ce qui permet d'ignorer
    celles marquées "Media disconnected" au lieu de prendre une interface
    virtuelle/déconnectée au hasard (même correctif que
    school_client/Controllers/Main.py get_mac_address()).
    """
    env_mac = os.getenv("HOST_MAC_ADDRESS")
    if env_mac:
        return env_mac.strip().upper()

    try:
        if os.path.exists(MAC_CACHE_FILE):
            cached = Path(MAC_CACHE_FILE).read_text().strip()
            if cached:
                return cached
    except OSError:
        pass

    mac = None
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output("getmac /fo csv /nh", shell=True).decode()
            for line in result.strip().splitlines():
                parts = [p.strip().strip('"') for p in line.split(',')]
                if len(parts) >= 2 and "disconnected" not in parts[1].lower():
                    mac = parts[0].replace('-', ':').upper()
                    break
        except Exception:
            mac = None

    if mac is None:
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode())).upper()

    try:
        os.makedirs(os.path.dirname(MAC_CACHE_FILE), exist_ok=True)
        Path(MAC_CACHE_FILE).write_text(mac)
    except OSError:
        pass
    return mac


def _generate_fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def _key_for_expiration(mac_address: str, expiration_date: str, days_valid: int) -> str:
    """HMAC déterministe de (mac, date d'expiration, days_valid) — c'est la
    seule chose qui rend une clé infalsifiable sans SECRET_KEY ; ne dépend
    jamais de la date du jour. Construction identique à
    infini-software/backend/genere_key.py::generate_activation_key (même
    ordre des champs, SECRET_KEY répété dans le message ET comme clé HMAC)."""
    raw_data = f"{mac_address}-{expiration_date}-{days_valid}-{SECRET_KEY}".encode()
    hashed = hmac.new(SECRET_KEY.encode(), raw_data, hashlib.sha256).digest()
    encoded_key = base64.b32encode(hashed).decode().upper()
    clean_key = ''.join(filter(str.isalnum, encoded_key))[:16]
    return '-'.join(clean_key[i:i + 4] for i in range(0, len(clean_key), 4))


def generate_activation_key(mac_address: str, days_valid: int = TRIAL_DAYS):
    """Calcule la clé d'activation attendue pour (mac, aujourd'hui + days_valid)."""
    expiration_date = (datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    return _key_for_expiration(mac_address, expiration_date, days_valid), expiration_date


def _save_license(mac: str, activation_key: str, expiration_date: str, days_valid: int | None = None) -> None:
    fkey = _generate_fernet_key(mac)
    f = Fernet(fkey)
    payload = {
        "activation_key": f.encrypt(activation_key.encode()).decode(),
        "expiration_date": f.encrypt(expiration_date.encode()).decode(),
    }
    if days_valid is not None:
        payload["days_valid"] = f.encrypt(str(days_valid).encode()).decode()
    os.makedirs(os.path.dirname(LICENSE_FILE), exist_ok=True)
    with open(LICENSE_FILE, "w") as fh:
        json.dump(payload, fh)


def _load_license(mac: str):
    """Renvoie (activation_key, expiration_date, days_valid). days_valid est
    None pour un fichier enregistré avant l'ajout de la revérification HMAC
    (voir is_license_valid()) — traité comme legacy, pas comme falsifié."""
    if not os.path.exists(LICENSE_FILE):
        return None, None, None
    try:
        with open(LICENSE_FILE) as fh:
            payload = json.load(fh)
        fkey = _generate_fernet_key(mac)
        f = Fernet(fkey)
        activation_key = f.decrypt(payload["activation_key"].encode()).decode()
        expiration_date = f.decrypt(payload["expiration_date"].encode()).decode()
        days_valid = None
        if "days_valid" in payload:
            try:
                days_valid = int(f.decrypt(payload["days_valid"].encode()).decode())
            except (InvalidToken, ValueError):
                days_valid = None
        return activation_key, expiration_date, days_valid
    except (InvalidToken, KeyError, json.JSONDecodeError, OSError):
        return None, None, None


KEY_ENTRY_GRACE_DAYS = 3


def verify_and_save_activation_key(provided_key: str, days_valid: int = TRIAL_DAYS) -> bool:
    """
    Valide une clé saisie par un administrateur pour cette machine et
    l'enregistre si elle correspond.

    La clé chiffre (mac, date d'expiration) — sans connaître SECRET_KEY,
    impossible de la forger pour une autre date. On essaie donc plusieurs
    dates de génération possibles (aujourd'hui, hier, ... jusqu'à
    KEY_ENTRY_GRACE_DAYS jours en arrière) plutôt qu'uniquement aujourd'hui :
    ça absorbe le décalage normal entre la génération d'une clé par le
    support et sa saisie par le client (1 jour de retard ne doit pas suffire
    à invalider une clé par ailleurs correcte), sans pour autant la rendre
    valide indéfiniment si elle fuite — toujours bornée à la fenêtre de
    grâce. La date d'expiration réellement enregistrée est celle qui
    correspond à la clé fournie, pas une date recalculée à partir
    d'aujourd'hui.
    """
    mac = get_host_mac()
    cleaned = provided_key.replace("-", "").upper()
    aujourdhui = datetime.utcnow().date()
    for jours_ecoules in range(KEY_ENTRY_GRACE_DAYS + 1):
        date_generation = aujourdhui - timedelta(days=jours_ecoules)
        expiration_date = (date_generation + timedelta(days=days_valid)).strftime("%Y-%m-%d")
        expected_key = _key_for_expiration(mac, expiration_date, days_valid)
        if cleaned == expected_key.replace("-", "").upper():
            _save_license(mac, provided_key, expiration_date, days_valid)
            return True
    return False


def apply_remote_licence(key: str, expiration_date: str, days_valid: int | None = None) -> None:
    """
    Enregistre localement une clé/date émise par infini-software après un
    paiement de renouvellement réussi (voir Routes/RClientInfos.py,
    /api/v1/licence/appliquer). days_valid est transmis par infini-software
    (voir GET /api/licence/derniere-cle) pour permettre à is_license_valid()
    de revérifier le HMAC à chaque lecture, comme pour une clé saisie à la
    main — infini-software et ecole_nginx utilisent désormais le même
    SECRET_KEY et le même format de hash (voir _key_for_expiration), donc une
    clé authentique passe toujours cette vérification, peu importe qui l'a
    appliquée. Si days_valid est absent (ancien client school_client pas
    encore mis à jour), la clé est enregistrée sans vérification possible
    (legacy, voir _load_license).
    """
    _save_license(get_host_mac(), key, expiration_date, days_valid)


def is_license_valid() -> bool:
    """
    True uniquement si une licence enregistrée existe, n'est pas expirée, ET
    (si days_valid est connu) si son HMAC est cohérent avec (mac, expiration,
    days_valid) — ça empêche de forger le fichier local directement, puisque
    sans SECRET_KEY on ne peut pas produire un HMAC valide. Pour un fichier
    enregistré avant l'ajout de days_valid (legacy), on ne peut pas revérifier
    : on se contente de la date, comme avant — pour ne pas invalider des
    licences déjà actives au moment de ce changement.
    """
    mac = get_host_mac()
    activation_key, expiration_date_str, days_valid = _load_license(mac)
    if not activation_key or not expiration_date_str:
        return False
    try:
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
    except ValueError:
        return False
    if days_valid is not None:
        expected_key = _key_for_expiration(mac, expiration_date_str, days_valid)
        if activation_key.replace("-", "").upper() != expected_key.replace("-", "").upper():
            return False
    return datetime.utcnow() <= expiration_date


def ensure_trial_license() -> tuple[str, str]:
    """
    Si aucune licence n'est enregistrée pour cette machine, auto-active un
    essai de TRIAL_DAYS jours (équivalent de show_activation_key() côté
    Windows, qui auto-enregistre une clé au premier lancement). Retourne
    (clé, date d'expiration) de la licence active après l'appel.
    """
    mac = get_host_mac()
    activation_key, expiration_date, _ = _load_license(mac)
    if activation_key and expiration_date:
        return activation_key, expiration_date

    key, expiration_date = generate_activation_key(mac, TRIAL_DAYS)
    _save_license(mac, key, expiration_date, TRIAL_DAYS)
    return key, expiration_date
