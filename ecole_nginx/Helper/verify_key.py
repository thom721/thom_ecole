import sys
import re
import hmac
import uuid
from datetime import datetime
from PySide6.QtCore import QSettings
import colorama
import re
import sys
import msvcrt 
from .server_key_generate import generate_activation_key
from .manage_activate import Manage_active
from colorama import Fore, Style
from .save_onReg import LicenseManager
import win32api
import win32con
import win32security 
import ntsecuritycon as con  # Pour WRITE_DAC

import subprocess
import winreg
import os
import json
colorama.init(autoreset=True)
from .server_key_generate import generate_fernet_key, decrypt_value

SECRET_KEY = "CLE_SECRETE_PERSO"
license = LicenseManager()
def get_mac_address():
    """Récupère l'adresse MAC de la machine cliente."""
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac

def verify_activation_key(input_key):
    """Vérifie si la clé entrée est correcte et non expirée."""
    settings = QSettings("MonAppServer", "Licence")
    # saved_key = settings.value("activation_key", "")
    # exp_date_str = settings.value("expiration_date", "")
    val_bool, message, date = license.check_license() 
    mac = get_mac_address()
    encryption_key = generate_fernet_key(mac)

    encrypted_key = settings.value("activation_key")
    encrypted_date = settings.value("expiration_date")

    saved_key = decrypt_value(encrypted_key, encryption_key)
    exp_date_str = decrypt_value(encrypted_date, encryption_key)

    if not saved_key or not exp_date_str:
        print(Fore.RED + " [x]   Erreur : Aucune clé enregistrée côté serveur.")
        sys.exit(1)

    # Générer la clé attendue
    
    expected_key, _ = generate_activation_key(mac)

    if input_key != expected_key:
        print(Fore.RED + "\n [x]   Clé invalide !")
        return False

    # Vérifier l’expiration
    exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")
    if exp_date < datetime.utcnow():
        print(Fore.RED + "\n [x]   Clé expirée ! Contactez le support.")
        return False

#     print(Fore.GREEN + "✅ Clé valide ! Installation autorisée.")
    license_data = {'key':saved_key,
                'expiry_date':exp_date_str
                }
    if not date:
        license.write_license_to_registry00000(license_data)
    return True

def format_key_input():
     """Gère la saisie clavier pour formater automatiquement la clé en XXXX-XXXX-XXXX-XXXX"""
     key = ""
     while True:
          char = msvcrt.getwch().upper() 
          
          if char == "\r" and len(key) == 19:
               print()
               return key
          
          elif char == "\b":
               if key:
                    key = key[:-1]
                    print("\b \b", end="", flush=True)
          
          elif len(key) < 19 and re.match(r"[A-Z0-9]", char):
               if len(key.replace("-", "")) % 4 == 0 and len(key) != 0:
                    key += "-" 
                    print("-", end="", flush=True)
               
               key += char
               print(char, end="", flush=True)

def ask_for_activation_key():
    """Demande la clé d’activation et vérifie sa validité."""
    max_attempts = 5
    attempts = 0
    pattern = re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$")

    while attempts < max_attempts:
        print(Fore.CYAN+"\n [-]   Entrez votre clé d'activation : \t ", end=" ")
        key = format_key_input()
     #    key = input(Fore.CYA N + "🔑 Entrez votre clé d'activation : ").strip().upper()

        if not pattern.match(key):
            attempts += 1
            print(Fore.RED + f"\n [x]   Format incorrect ! {max_attempts - attempts} tentative(s) restante(s).")
            continue

        if verify_activation_key(key):
            Manage_active().save_manage_active(True)
            lock_registry_key()
            print(Fore.GREEN + "\n [ok]   Clé enregistrée avec succès.")
            return True
        
        attempts += 1

    print(Fore.RED + "\n [x]   Trop de tentatives. Installation annulée.")
    sys.exit(1)

def lock_registry_key1():
    """Verrouille la clé de registre avec des permissions NTFS"""
    self_app_name = "ecole-server"
    key_path = f"Software\\{self_app_name}\\Licenses"

    try:
        # Récupérer les SID
        system_sid = win32security.CreateWellKnownSid(win32security.WinLocalSystemSid, None)
        admin_sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)

        # Créer le descripteur de sécurité
        sd = win32security.SECURITY_DESCRIPTOR()
        sd.SetSecurityDescriptorOwner(system_sid, False)
        sd.SetSecurityDescriptorGroup(admin_sid, False)

        # Créer la DACL (access control list)
        acl = win32security.ACL()
        acl.AddAccessAllowedAce(
            win32security.ACL_REVISION,
            win32con.KEY_QUERY_VALUE,
            system_sid
        )

        sd.SetSecurityDescriptorDacl(1, acl, 0)
        key = win32api.RegOpenKeyEx(
            win32con.HKEY_CURRENT_USER,
            key_path,
            0,
            win32con.KEY_READ | win32con.WRITE_DAC
        )

        win32api.RegSetKeySecurity(key, win32security.DACL_SECURITY_INFORMATION, sd)
        win32api.RegCloseKey(key)

        print("[✓] Clé de registre sécurisée.")

    except Exception as e:
        print(f"[x] Erreur de protection : {str(e)}")



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


def lock_registry_key______():
    """Verrouille la clé de registre via icacls et reg"""
    self_app_name = "ecole-server"
    key_path = f"Software\\{self_app_name}\\Licenses"
    full_reg_path = f"HKCU\\{key_path}"

    try:
        # 1. Créer la clé si elle n'existe pas (en admin)
        subprocess.run(
            ['reg', 'add', full_reg_path, '/f'],
            check=True,
            capture_output=True
        )

        # 2. Verrouillage avec icacls (nécessite admin)
        ps_script = f"""
        $keyPath = "HKCU:\{key_path}"
        $acl = Get-Acl $keyPath
        $rule = New-Object System.Security.AccessControl.RegistryAccessRule(
            "SYSTEM", 
            "ReadKey", 
            "Allow"
        )
        $acl.SetAccessRule($rule)
        $acl | Set-Acl $keyPath
        """
        
        subprocess.run(
            ["powershell", "-Command", ps_script],
            check=True,
            capture_output=True
        )

        # 3. Vérification
        verify_cmd = ['reg', 'query', full_reg_path, '/s']
        result = subprocess.run(verify_cmd, capture_output=True, text=True)
        
        if "ERROR" in result.stderr:
            raise PermissionError("Échec de la sécurisation de la clé")

        return True

    except subprocess.CalledProcessError as e:
        print(f"Erreur subprocess: {e.stderr.decode()}")
        return _fallback_lock_method(key_path)
    except Exception as e:
        print(f"Erreur générale: {str(e)}")
        return False

def _fallback_lock_method(key_path):
    """Méthode alternative si la sécurisation échoue"""
    try:
        # Solution 1: Fichier de verrouillage
        lock_file = os.path.join(os.environ['ProgramData'], 'app_lockfile')
        with open(lock_file, 'w') as f:
            f.write(json.dumps({"status": "locked"}))
        
        # Solution 2: Registry modifiée
        subprocess.run(
            ['reg', 'add', f"HKCU\{key_path}", '/v', 'Locked', '/t', 'REG_DWORD', '/d', '1', '/f'],
            check=True
        )
        return True
    except:
        print("Méthode alternative échouee")
        return False

def lock_registry_key1():
    """Verrouille la clé de registre avec des permissions NTFS"""
    self_app_name = "ecole-server"
    key_path = f"Software\\{self_app_name}\\Licenses"

    try:
        # S'assure que la clé existe
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)

        # Récupérer les SID
        system_sid = win32security.CreateWellKnownSid(win32security.WinLocalSystemSid, None)
        admin_sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)

        # Créer le descripteur de sécurité
        sd = win32security.SECURITY_DESCRIPTOR()
        sd.SetSecurityDescriptorOwner(system_sid, False)
        sd.SetSecurityDescriptorGroup(admin_sid, False)

        # Créer la DACL
        acl = win32security.ACL()
        acl.AddAccessAllowedAce(win32security.ACL_REVISION, win32con.KEY_READ, system_sid)

        # Appliquer la DACL
        sd.SetSecurityDescriptorDacl(1, acl, 0)

        # Ouvrir la clé avec le droit WRITE_DAC pour modifier la sécurité
        key = win32api.RegOpenKeyEx(
            win32con.HKEY_CURRENT_USER,
            key_path,
            0,
            win32con.KEY_READ | con.WRITE_DAC
        )

        win32api.RegSetKeySecurity(key, win32security.DACL_SECURITY_INFORMATION, sd)
        win32api.RegCloseKey(key)

        print("[✓] Clé de registre sécurisée.")

    except Exception as e:
        print(f"[x] Erreur de protection : {str(e)}")


def lock_registry_key111():
    """Verrouille la clé de registre avec des permissions NTFS"""
    self_app_name ="ecole-server"
    key_path =f"Software\\{self_app_name}\\Licenses"# r"SOFTWARE\ecole-server\Licenses"
    try:
        # 1. Définir des permissions restrictives
        sd = win32security.SECURITY_DESCRIPTOR()
        sd.SetSecurityDescriptorOwner(win32security.LookupAccountName(None, "SYSTEM")[0], False)
        sd.SetSecurityDescriptorGroup(win32security.LookupAccountName(None, "Administrateurs")[0], False)
        
        # 2. Bloquer tout accès sauf SYSTEM
        acl = win32security.ACL()
        acl.AddAccessAllowedAce(
            win32security.ACL_REVISION,
            win32con.KEY_QUERY_VALUE,
            win32security.LookupAccountName(None, "SYSTEM")[0]
        )
        sd.SetSecurityDescriptorDacl(1, acl, 0)
        
        # 3. Appliquer au registre
        key = win32api.RegOpenKeyEx(
            win32con.HKEY_CURRENT_USER,
            key_path,
            0,
            win32con.KEY_WRITE_DAC | win32con.KEY_READ
        )
        win32api.RegSetKeySecurity(key, win32security.DACL_SECURITY_INFORMATION, sd)
        win32api.RegCloseKey(key)
        
    except Exception as e:
        print(f"Erreur de protection : {str(e)}")



