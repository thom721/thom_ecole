import hashlib
import base64
import hmac
import uuid
import re
import os
import subprocess
from pathlib import Path
import requests
from datetime import datetime, timedelta
from PySide6.QtCore import QSettings
from .manage_activate import Manage_active
from .save_onReg import LicenseManager  
from cryptography.fernet import Fernet, InvalidToken
# Secret PARTAGÉ avec infini-software (même variable d'env KEY_SECRET côté
# infini-software/backend/genere_key.py) — voir app/Helper/license_check.py
# pour le détail de pourquoi ça doit être identique partout.
SECRET_KEY = os.environ.get("KEY_SECRET", "CLE_SECRETE_PERSO")
license = LicenseManager()
from Controllers.direct_request import load_data,store_log_activate, store

def get_mac_reliable():
    """Récupère l'adresse MAC de la machine."""
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode())) 
    return mac

# Même fichier que app.Helper.license_check.MAC_CACHE_FILE (API ecole_nginx) :
# les deux tournent sur la même machine (le serveur), donc partager ce cache
# garantit qu'ils rapportent toujours la même MAC.
_MAC_CACHE_FILE = Path.home() / ".ecole_360" / "machine_mac.txt"


def get_mac_address() -> str:
    """Adresse MAC de CETTE machine (le serveur) — utilisée pour la clé
    d'activation et le lien de renouvellement infini-software.

    "getmac" liste TOUTES les interfaces (Ethernet, Wi-Fi, Bluetooth,
    adaptateurs virtuels...), y compris déconnectées ("Transport Name" =
    "Media disconnected"). Prendre systématiquement la 1ère ligne pouvait
    donc renvoyer une interface déconnectée/virtuelle plutôt que la carte
    physique active — et la relancer à chaque appel pouvait faire changer la
    MAC rapportée d'une fois à l'autre. On filtre les lignes déconnectées et
    on mémorise le résultat (même correctif que school_client/Controllers/
    Main.py get_mac_address() et app.Helper.license_check.get_host_mac())."""
    print(f"[get_mac_address] cache file = {_MAC_CACHE_FILE}")
    try:
        if _MAC_CACHE_FILE.exists():
            cached = _MAC_CACHE_FILE.read_text().strip()
            print(f"[get_mac_address] cache trouvé, contenu = {cached!r}")
            if cached:
                return cached
        else:
            print("[get_mac_address] pas de cache, détection via getmac")
    except OSError as e:
        print(f"[get_mac_address] erreur lecture cache: {e}")

    mac = None
    try:
        result = subprocess.check_output("getmac /fo csv /nh", shell=True).decode()
        print(f"[get_mac_address] sortie brute getmac:\n{result}")
        for line in result.strip().splitlines():
            parts = [p.strip().strip('"') for p in line.split(',')]
            print(f"[get_mac_address] ligne parsée: {parts}")
            if len(parts) >= 2 and "disconnected" not in parts[1].lower():
                mac = parts[0].replace('-', ':')
                print(f"[get_mac_address] ligne retenue -> mac = {mac}")
                break
    except Exception as e:
        print(f"[get_mac_address] getmac a échoué: {e}")
        mac = None

    if mac is None:
        mac = get_mac_reliable()
        print(f"[get_mac_address] repli sur get_mac_reliable() -> {mac}")

    try:
        _MAC_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _MAC_CACHE_FILE.write_text(mac)
    except OSError as e:
        print(f"[get_mac_address] erreur écriture cache: {e}")

    print(f"[get_mac_address] valeur finale retournée = {mac}")
    return mac
        # return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def generate_activation_key(mac_address, days_valid=30):
    """Génère une clé d'activation alphanumérique avec tirets (XXXX-XXXX-XXXX-XXXX).
    Délègue à _key_for_expiration_graphic (même format que infini-software et
    que app.Helper.license_check, days_valid inclus dans le HMAC) — voir cette
    fonction plus bas dans ce fichier."""
    expiration_date = (datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    formatted_key = _key_for_expiration_graphic(mac_address, expiration_date, days_valid)
    return formatted_key, expiration_date



def save_key_to_settings():
    """Stocke la clé d'activation et la date d'expiration dans QSettings."""
    mac = get_mac_address()
    days_valid = 30
    activation_key, expiration_date = generate_activation_key(mac, days_valid)
    print(f"in save_key_to_settings    {activation_key}  --expiration_date-- {expiration_date}")
    settings = QSettings("MonAppServer", "Licence")

    encryption_key = generate_fernet_key(mac)

    encrypted_date1 = encrypt_value(expiration_date, encryption_key)
    activation_key1 = encrypt_value(activation_key, encryption_key)


    settings.setValue("activation_key", activation_key1)
    settings.setValue("expiration_date", encrypted_date1)
    # days_valid doit être enregistré pour que is_license_valid() puisse
    # revérifier le HMAC de cette clé ensuite (voir _key_for_expiration_graphic).
    settings.setValue("days_valid", encrypt_value(str(days_valid), encryption_key))

    return activation_key, expiration_date

# activation_key, expiration_date = save_key_to_settings()


def apply_remote_licence(key: str, expiration_date: str, days_valid: int = None) -> None:
    """
    Enregistre dans le registre (QSettings) une clé/date émise par
    infini-software après un paiement de renouvellement réussi (appelé par
    Routes/RClientInfos.py /api/v1/licence/appliquer). Équivalent Windows de
    app.Helper.license_check.apply_remote_licence() — n'effectue aucune
    validation HMAC à l'enregistrement (infini-software est l'autorité qui a
    généré cette clé), mais days_valid est conservé pour permettre à
    is_license_valid() de revérifier le HMAC à la lecture (voir plus bas).
    """
    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)
    settings = QSettings("MonAppServer", "Licence")
    settings.setValue("activation_key", encrypt_value(key, encryption_key))
    settings.setValue("expiration_date", encrypt_value(expiration_date, encryption_key))
    if days_valid is not None:
        settings.setValue("days_valid", encrypt_value(str(days_valid), encryption_key))
    else:
        settings.remove("days_valid")


def show_activation_key():
    activation_key, expiration_date = save_key_to_settings()
    print('--------------------------------------------------------------------------------------------')
    print(f"\t\t\t\t\t Clé d'activation     : {activation_key}")
    print(f"\t\t\t\t\t Date d'Expiration    : {expiration_date}")
    print('--------------------------------------------------------------------------------------------')
# print(f"📧 Envoyer la clé suivante à l'utilisateur : {activation_key}")


def delete_key():
    """Supprime la licence enregistrée localement (déconnexion / reset)."""
    settings = QSettings("MonAppServer", "Licence")
    settings.remove("activation_key")
    settings.remove("expiration_date")
    settings.remove("days_valid")



def is_license_valid(url = None):
    """Vérifie si la licence est encore valide et n'a pas expiré depuis plus de 30 jours."""
    settings = QSettings("MonAppServer", "Licence")
    # activation_key = settings.value("activation_key", "")
    # expiration_date_str = settings.value("expiration_date", "")

    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)

    mac1 = "B4:B5:2F:7F:F6:AF" #
    mac2="18:03:73:1B:40:E2"
    encryption_key_ = generate_fernet_key(mac1)
    # encryption_key_mac = generate_fernet_key(mac2)

    # encrypted_value = "gAAAAABprcxXIQcYIRitAAh2xlv4WdvuIEJoRdPMp7LubrLSs1YE6FR_laal06DaIaoBavNUM6GhwLsHO4T7wdFGBaoIjQA4Jw=="
    

    # result = decrypt_value(encrypted_value, encryption_key_)
    encrypted_date_mac = encrypt_value('2026-06-03', encryption_key_)
    encrypted_key_mac = encrypt_value('OJ7G-PZM3-MONN-AW3A', encryption_key_)

    # print('result')
    # print(result)
    # print('result')

    print('result encrypted_date_mac encription')
    print(encrypted_date_mac)
    print('result encrypted_date_mac encription')

    print('result encrypted_key_mac encription')
    print(encrypted_key_mac)
    print('result encrypted_key_mac encription')

    encrypted_key = settings.value("activation_key", "")
    encrypted_date = settings.value("expiration_date", "")

    try: 
        activation_key = decrypt_value(encrypted_key, encryption_key)
        expiration_date_str = decrypt_value(encrypted_date, encryption_key)
    except Exception as e:
        print(e) 
        print("Erreur is_license_valid :", e)
        import traceback
        traceback.print_exc()
        # Si le déchiffrement échoue, suppose que la valeur est en clair 
        
        # encrypted_date1 = encrypt_value(encrypted_date, encryption_key)
        # provided_key1 = encrypt_value(encrypted_key, encryption_key)


        # settings.setValue("activation_key", provided_key1)
        # settings.setValue("expiration_date", encrypted_date1)
    
        # activation_key = decrypt_value(encrypted_key, encryption_key)
        # expiration_date_str = decrypt_value(encrypted_date, encryption_key)

    # Revérifie le HMAC de la clé (mac, expiration_date, days_valid) si
    # days_valid a été enregistré (clés appliquées avant cet ajout n'ont pas
    # cette valeur : legacy, on ne peut pas les revérifier, comportement
    # inchangé pour elles). Empêche de forger directement le registre sans
    # connaître SECRET_KEY — voir app.Helper.license_check.is_license_valid()
    # côté Mac/Linux pour l'équivalent.
    encrypted_days_valid = settings.value("days_valid", "")
    if encrypted_days_valid and activation_key and expiration_date_str:
        try:
            days_valid_stocke = int(decrypt_value(encrypted_days_valid, encryption_key))
            expected_key = _key_for_expiration_graphic(mac, expiration_date_str, days_valid_stocke)
            if activation_key.replace("-", "").upper() != expected_key.replace("-", "").upper():
                print("❌ Licence locale invalide : HMAC ne correspond pas (registre modifié manuellement ?)")
                if url:
                    status_authorization(url, status=23)
                return False
        except (ValueError, TypeError):
            pass

    val_bool, message, date = license.check_license()

    print(f" show and verify date registre {date}  \n  date setting  {expiration_date_str}")
    print(f" val_bool, message and verify dateshow and verify date registre {date}  \n  date val_bool, message  {val_bool, message}")

    Manage_active().save_manage_active(True)

    if not activation_key or not expiration_date_str:
        if url:
          status_authorization(url,status=23)
        return False

    try:
        if not date:
            status_authorization(url,status=23)
            return
            # expiration_date =  date if isinstance(date, datetime) else datetime.strptime(date, "%Y-%m-%d")
        # else:
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        now = datetime.utcnow()

        # Licence encore valide
        if now <= expiration_date:
            if url:
                status_authorization(url,status=22)
            return True
        print(f" expiration_date {expiration_date}  \n  date expiration_date setting  {expiration_date}")
        # Licence expirée, mais vérifie si elle l'est depuis moins de 30 jours
        grace_period_end = expiration_date + timedelta(days=30)
        if now <= grace_period_end:
            if url:
                status_authorization(url,status=20)
            print(f"⚠️ Licence expirée mais encore dans la période de grâce.  {expiration_date}")
            return False
        
        print("❌ Licence expirée depuis plus de 30 jours.")
        if url:
          status_authorization(url,status=23)
        return False

    except ValueError:
        print(f"❌ Erreur ValueError: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
def get_server_cert_content(cert_path):
    """Lit le fichier cert et le renvoie en base64 ou texte brut"""
    try:
        path = Path(cert_path)
        if not path.exists():
            raise FileNotFoundError(f"Certificat introuvable : {path}")

        with open(path, "rb") as f:
            content = f.read()

        # Option 1 : texte brut (PEM inchangé)
        pem_content = content.decode("utf-8")

        # Option 2 : Base64 encodé (plus sûr pour l’envoyer via JSON)
        b64_content = base64.b64encode(content).decode("utf-8")

        return pem_content, b64_content 
    except Exception as e:
        print(e)
    
def status_authorization(url,status): 

    try:   
        request_data={
                'status':status,
                'ssl_ca':'ssl_cab64', 
                'ssl_cert':'ssl_certb64', 
                'ssl_key':'ssl_keyb64', 
                }

        log_url = f"{url}activate-state"
        response = requests.post(
            log_url,
            json=request_data,
            timeout=50,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem"
        )
        
        if response.status_code == 200:
            print(f'users update')
        else:
            print(f'users not update')
    except Exception as e:
        print(f"API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    

KEY_ENTRY_GRACE_DAYS = 3


def _key_for_expiration_graphic(mac_address, expiration_date, days_valid):
    """HMAC déterministe de (mac, date d'expiration, days_valid) — infalsifiable
    sans SECRET_KEY ; ne dépend jamais de la date du jour."""
    raw_data = f"{mac_address}-{expiration_date}-{days_valid}-{SECRET_KEY}".encode()
    hashed = hmac.new(SECRET_KEY.encode(), raw_data, hashlib.sha256).digest()
    encoded_key = base64.b32encode(hashed).decode().upper()
    clean_key = ''.join(filter(str.isalnum, encoded_key))[:16]
    return '-'.join(clean_key[i:i+4] for i in range(0, len(clean_key), 4))


def generate_activation_key_graphic(mac_address, days_valid=30):
    """Génère une clé d'activation alphanumérique avec tirets (XXXX-XXXX-XXXX-XXXX)."""
    expiration_date = (datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    formatted_key = _key_for_expiration_graphic(mac_address, expiration_date, days_valid)
    print(formatted_key, expiration_date, days_valid)
    return formatted_key, expiration_date, days_valid


_CANDIDATE_DAYS = [30, 60, 90, 120, 180, 365]


def verify_activation_key_graphic(provided_key, mac_address, url, days=None):
    """
    Vérifie le HMAC de provided_key en essayant toutes les durées connues
    (_CANDIDATE_DAYS) sur une fenêtre de KEY_ENTRY_GRACE_DAYS jours en arrière
    (tolérance de saisie tardive).
    Retourne True si tout réussit, False si le HMAC ne correspond pas,
    None si le POST /log-activate échoue (la clé n'est PAS sauvegardée dans ce cas).
    """
    cleaned_key = provided_key.replace("-", "").upper()
    aujourdhui = datetime.utcnow().date()

    days_to_try = _CANDIDATE_DAYS if days is None else sorted({days} | set(_CANDIDATE_DAYS))

    expected_key_cleaned = None
    expiration_date = None
    matched_days = None

    for candidate_days in days_to_try:
        for jours_ecoules in range(KEY_ENTRY_GRACE_DAYS + 1):
            date_generation = aujourdhui - timedelta(days=jours_ecoules)
            candidate_expiration = (date_generation + timedelta(days=candidate_days)).strftime("%Y-%m-%d")
            candidate_key = _key_for_expiration_graphic(mac_address, candidate_expiration, candidate_days).replace("-", "").upper()
            if cleaned_key == candidate_key:
                expected_key_cleaned = candidate_key
                expiration_date = candidate_expiration
                matched_days = candidate_days
                break
        if expected_key_cleaned is not None:
            break

    if expected_key_cleaned is None:
        return False

    # HMAC matched — POST to log-activate first; only persist key if it succeeds.
    # Returns None on server error so the caller can show a distinct message.
    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)
    settings = QSettings("MonAppServer", "Licence")
    old_key = decrypt_value(settings.value("activation_key", ""), encryption_key)

    try:
        resp = requests.post(
            f"{url}log-activate",
            json={"last_key": old_key, "new_key": provided_key, "exprired_at": expiration_date},
            timeout=15,
            verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem",
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"Log-activate POST failed: {e}")
        return None

    delete_key()
    settings.setValue("activation_key", encrypt_value(provided_key, encryption_key))
    settings.setValue("expiration_date", encrypt_value(expiration_date, encryption_key))
    settings.setValue("days_valid", encrypt_value(str(matched_days), encryption_key))

    return True


def lock_registry_key():
    """Verrouille la clé de registre via reg et PowerShell"""
    self_app_name = "ecole-server"
    key_path = f"Software\{self_app_name}\Licenses"
    full_reg_path = f"HKCU\{key_path}"
    ps_reg_path = f"HKCU:\{key_path}"

    try:
        # 1. Créer la clé si elle n'existe pas
        subprocess.run(
            ['reg', 'add', full_reg_path, '/f'],
            check=True,
            capture_output=True
        )

        # 2. PowerShell pour modifier les droits
        ps_script = f'''
        $keyPath = "{ps_reg_path}"
        $acl = Get-Acl -Path $keyPath
        $rule = New-Object System.Security.AccessControl.RegistryAccessRule(
            "Everyone", "ReadKey", "Allow"
        )
        $acl.SetAccessRuleProtection($true, $false)  # Désactive héritage
        $acl.SetAccessRule($rule)
        Set-Acl -Path $keyPath -AclObject $acl
        '''

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            check=True,
            capture_output=True,
            text=True
        )

        # 3. Vérification
        verify_cmd = ['reg', 'query', full_reg_path, '/s']
        result = subprocess.run(verify_cmd, capture_output=True, text=True)

        if "ERROR" in result.stderr.upper():
            raise PermissionError("Impossible de verrouiller la clé")

        print("✅ Clé verrouillée avec succès")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur subprocess : {e.stderr}")
    except Exception as e:
        print(f"❌ Erreur générale : {str(e)}")
    
    return False


# Exemple : Générer une clé à partir d'une phrase secrète ou de l'adresse MAC
def generate_fernet_key(secret: str) -> bytes:
    """Génère une clé Fernet à partir d'un secret (ex: MAC address).

    Ne capture plus l'exception ici : un appelant (apply_remote_licence...)
    qui recevait silencieusement None en cas d'échec écrivait quand même
    cette valeur dans le registre via settings.setValue(), masquant l'échec
    réel au lieu de le faire remonter."""
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)

# Fonction de chiffrement
def encrypt_value(value: str, key: bytes) -> str:
    """Ne capture plus l'exception ici, pour la même raison que
    generate_fernet_key()."""
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str, key: bytes) -> str:
    try:
        if not encrypted_value or not key:
            return None
        if isinstance(key, str):
            key = key.strip().encode()
        elif isinstance(key, bytes):
            key = key.strip()

        encrypted_value = encrypted_value.strip()

        f = Fernet(key)
        decrypted_bytes = f.decrypt(encrypted_value.encode())
        return decrypted_bytes.decode()

    except InvalidToken as e:
        print("[ERREUR] Jeton invalide - cle incorrecte ou donnee modifiee")
        print("Erreur  :", e)
        import traceback
        traceback.print_exc()
        return None
    except Exception as e:
        print(f"[ERREUR] decrypt_value : {e}")
        return None


# Fonction pour récupérer et déchiffrer
def load_key_from_settings():
    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)

    settings = QSettings("MonAppServer", "Licence")
    encrypted_key = settings.value("activation_key")
    encrypted_date = settings.value("expiration_date")

    if encrypted_key and encrypted_date:
        try:
            activation_key = decrypt_value(encrypted_key, encryption_key)
            expiration_date = decrypt_value(encrypted_date, encryption_key)
            print("Clé déchiffrée :", activation_key)
            print("Date d'expiration déchiffrée :", expiration_date)
            return activation_key, expiration_date
        except Exception as e:
            print("Erreur lors du déchiffrement :", e)
            import traceback
            traceback.print_exc()
            return None, None
    else:
        print("Aucune valeur trouvée dans les paramètres.")
        return None, None






