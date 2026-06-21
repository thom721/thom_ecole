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
SECRET_KEY = "CLE_SECRETE_PERSO"
license = LicenseManager()
from Controllers.direct_request import load_data,store_log_activate, store

def get_mac_reliable():
    """Récupère l'adresse MAC de la machine."""
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode())) 
    return mac

def get_mac_address() -> str:
    import subprocess
    try:
        result = subprocess.check_output("getmac /fo csv /nh", shell=True).decode()
        mac = result.split(',')[0].strip().strip('"').replace('-', ':')
        print(f"mac 1 {mac}")
        return mac
    except:
        print(f"mac 2 get_mac_reliable(")
        print(get_mac_reliable())
        return get_mac_reliable()
        # return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def generate_activation_key(mac_address, days_valid=30):
    """Génère une clé d'activation alphanumérique avec tirets (XXXX-XXXX-XXXX-XXXX)."""

    expiration_date =(datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    raw_data = f"{mac_address}-{expiration_date}-{SECRET_KEY}".encode()

    hashed = hmac.new(SECRET_KEY.encode(), raw_data, hashlib.sha256).digest()
    encoded_key = base64.b32encode(hashed).decode().upper()

    clean_key = ''.join(filter(str.isalnum, encoded_key))[:16]

    formatted_key = '-'.join(clean_key[i:i+4] for i in range(0, len(clean_key), 4))

    return formatted_key, expiration_date



def save_key_to_settings():
    """Stocke la clé d'activation et la date d'expiration dans QSettings."""
    mac = get_mac_address()
    activation_key, expiration_date = generate_activation_key(mac)
    print(f"in save_key_to_settings    {activation_key}  --expiration_date-- {expiration_date}")
    settings = QSettings("MonAppServer", "Licence")
    
    encryption_key = generate_fernet_key(mac)

    encrypted_date1 = encrypt_value(expiration_date, encryption_key)
    activation_key1 = encrypt_value(activation_key, encryption_key)
    

    settings.setValue("activation_key", activation_key1)
    settings.setValue("expiration_date", encrypted_date1)

    return activation_key, expiration_date

# activation_key, expiration_date = save_key_to_settings()


def show_activation_key():
    activation_key, expiration_date = save_key_to_settings()
    print('--------------------------------------------------------------------------------------------')
    print(f"\t\t\t\t\t Clé d'activation     : {activation_key}")
    print(f"\t\t\t\t\t Date d'Expiration    : {expiration_date}")
    print('--------------------------------------------------------------------------------------------')
# print(f"📧 Envoyer la clé suivante à l'utilisateur : {activation_key}")


def delete_key():
    """Supprime le server_ip (déconnexion)"""
    settings = QSettings("MonAppServer", "Licence")
    settings.remove("activation_key")
    settings.remove("expiration_date")



def is_license_valid(url = None):
    """Vérifie si la licence est encore valide et n'a pas expiré depuis plus de 30 jours."""
    settings = QSettings("MonAppServer", "Licence")
    # activation_key = settings.value("activation_key", "")
    # expiration_date_str = settings.value("expiration_date", "")

    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)

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
    

def generate_activation_key_graphic(mac_address, days_valid=30):
    """Génère une clé d'activation alphanumérique avec tirets (XXXX-XXXX-XXXX-XXXX)."""

    expiration_date =(datetime.utcnow() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
    raw_data = f"{mac_address}-{expiration_date}-{days_valid}-{SECRET_KEY}".encode()

    hashed = hmac.new(SECRET_KEY.encode(), raw_data, hashlib.sha256).digest()
    encoded_key = base64.b32encode(hashed).decode().upper()

    clean_key = ''.join(filter(str.isalnum, encoded_key))[:16]

    formatted_key = '-'.join(clean_key[i:i+4] for i in range(0, len(clean_key), 4))
    print(formatted_key, expiration_date,days_valid)
    return formatted_key, expiration_date,days_valid


def verify_activation_key_graphic(provided_key, mac_address, url, days=30): 
    cleaned_key = provided_key.replace("-", "").upper()
 
    expected_key, expiration_date, days_valid  = generate_activation_key_graphic(mac_address=mac_address, days_valid=days)
    print(f"value attemp {expected_key}  {expiration_date}  {days_valid}")
    expected_key_cleaned = expected_key.replace("-", "").upper()

    # print(cleaned_key, expected_key_cleaned, expiration_date, days_valid)
    if cleaned_key == expected_key_cleaned:
        settings = QSettings("MonAppServer", "Licence")
        activation_key = settings.value("activation_key", "")
        expiration_date_str = settings.value("expiration_date", "")

        mac = get_mac_address()
        encryption_key = generate_fernet_key(mac)

        # encrypted_key = settings.value("activation_key", "")
        
        activation_key_ = decrypt_value(activation_key, encryption_key)

        expiration_date_str = decrypt_value(encrypted_date, encryption_key)
        print(f"activation_key last {activation_key}   expiration_date {expiration_date_str}\n")
        print(f"activation_key new {provided_key}   expiration_date {expiration_date}\n")
        try:
            status_code = 500
            request_data={
                'last_key':activation_key_,
                'new_key':provided_key,
                'exprired_at':expiration_date
                    }

            log_url = f"{url}log-activate"
            response = requests.post(
                log_url,
                json=request_data,
                timeout=50,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem"
            ) 
            status_code = response.status_code

            if status_code == 200:
                delete_key()
                # settings = QSettings("MonAppServer", "Licence")

                encryption_key = generate_fernet_key(get_mac_address())

                encrypted_date1 = encrypt_value(expiration_date, encryption_key)
                provided_key1 = encrypt_value(provided_key, encryption_key)
    

                settings.setValue("activation_key", provided_key1)
                settings.setValue("expiration_date", encrypted_date1)

                # settings.setValue("activation_key", provided_key)
                # settings.setValue("expiration_date", expiration_date)

                license_data = {'key':provided_key,
                'expiry_date':expiration_date,
                # 'is_trial': False
                }
                # license.unlock_registry_key()
                # license.write_license_to_registry00000(license_data)
                # lock_registry_key()
                return cleaned_key == expected_key_cleaned
            else:
                return False

                
        except Exception as e:
            print(f"API Error: {str(e)}")


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
    """Génère une clé Fernet à partir d'un secret (ex: MAC address)."""
    try:
        digest = hashlib.sha256(secret.encode()).digest()
        return base64.urlsafe_b64encode(digest)
    except Exception as e:
        print("Erreur  :", e)
        import traceback
        traceback.print_exc()

# Fonction de chiffrement
def encrypt_value(value: str, key: bytes) -> str:
    try:
        f = Fernet(key)
        return f.encrypt(value.encode()).decode()
    except Exception as e:
        print("Erreur encrypt_value :", e)
        import traceback
        traceback.print_exc() 


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






