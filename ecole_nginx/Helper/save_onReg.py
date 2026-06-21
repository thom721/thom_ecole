
import winreg
import hashlib
import json
from datetime import datetime
import subprocess
import uuid
from pathlib import Path
import ctypes
import subprocess
import json
import os
from cryptography.fernet import Fernet
import re
import unicodedata

class LicenseManager:
    def __init__(self, app_name="ecole-server"):
        self.app_name ="ecole-server"
        self.reg_path = f"Software\\{app_name}\\Licenses"
        self.hw_id = self.get_hardware_id()
     #    self.lock_registry_key()


    def sanitize_app_name(self, name: str) -> str:
        # Supprimer les accents
        name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
        # Remplacer les caractères interdits (espace, tirets spéciaux, etc.) par "_"
        name = re.sub(r"[^A-Za-z0-9\-]", "_", name)
        return name

    def get_hardware_id(self):
        """Génère un ID unique basé sur le matériel"""
        components = [
            str(uuid.getnode()),  # Adresse MAC
            subprocess.getoutput('wmic diskdrive get serialnumber').strip(),  # Serial disk
            subprocess.getoutput('wmic csproduct get uuid').strip()  # UUID BIOS
        ]
        return hashlib.sha256(''.join(components).encode()).hexdigest()

    def write_license_to_registry11(self, license_data):
        """Stocke les infos de licence dans le registre"""
        try:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.reg_path) as key:
                winreg.SetValueEx(key, "LicenseKey", 0, winreg.REG_BINARY, license_data['key'].encode())
                winreg.SetValueEx(key, "ExpiryDate", 0, winreg.REG_SZ, license_data['expiry_date'])
                winreg.SetValueEx(key, "HWID", 0, winreg.REG_SZ, self.hw_id)
                winreg.SetValueEx(key, "IsTrial", 0, winreg.REG_DWORD, 1 if license_data.get('is_trial') else 0)
            return True
        except PermissionError:
            print(f"❌ Erreur lors de l'écriture PermissionError")
            import traceback
            traceback.print_exc() 
            return False
        except Exception as e:
            import traceback
            traceback.print_exc() 
            print(f"❌ Erreur lors de l'écriture dans le registre : {e} license_data {license_data}")
            return False
        
    def write_license_to_registry1(self, license_data):
        """Stocke les infos de licence dans le registre Windows de manière sécurisée"""
        if not license_data or not isinstance(license_data, dict):
            print("❌ Données de licence invalides")
            return False

        required_fields = {'key', 'expiry_date'}
        if not required_fields.issubset(license_data.keys()):
            print(f"❌ Champs manquants dans license_data. Requis: {required_fields}")
            return False

        try:
            # Convertit les données en types appropriés pour le registre
            reg_data = {
                'LicenseKey': license_data['key'].encode('utf-8'),
                'ExpiryDate': str(license_data['expiry_date']),
                'HWID': str(getattr(self, 'hw_id', '')),
                'IsTrial': 1 if license_data.get('is_trial', False) else 0
            }

            # Accès au registre avec vérification des permissions
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.reg_path) as key:
                for name, value in reg_data.items():
                    reg_type = (
                        winreg.REG_BINARY if name == 'LicenseKey' else
                        winreg.REG_DWORD if name == 'IsTrial' else
                        winreg.REG_SZ
                    )
                    winreg.SetValueEx(key, name, 0, reg_type, value)

            # Vérification que les données ont bien été écrites
            if not self.verify_registry_write(reg_data):
                raise RuntimeError("La vérification de l'écriture a échoué")

            return True

        except PermissionError:
            print("❌ Permission refusée - Essayez d'exécuter en administrateur")
            return False
        except Exception as e:
            print(f"❌ Erreur critique: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def verify_registry_write(self, expected_data):
        """Vérifie que les données ont bien été écrites dans le registre"""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path) as key:
                for name, expected_value in expected_data.items():
                    reg_type = (
                        winreg.REG_BINARY if name == 'LicenseKey' else
                        winreg.REG_DWORD if name == 'IsTrial' else
                        winreg.REG_SZ
                    )
                    actual_value = winreg.QueryValueEx(key, name)[0]
                    
                    if name == 'LicenseKey' and actual_value != expected_value:
                        return False
                    elif name != 'LicenseKey' and str(actual_value) != str(expected_value):
                        return False
            return True
        except:
            return False

    def check_license11111(self):
        """Vérifie la validité de la licence"""
        try:
            #HKEY_LOCAL_MACHINE
            # with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path) as key:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_READ) as key:

                expiry_date = datetime.fromisoformat(winreg.QueryValueEx(key, "ExpiryDate")[0])
                hwid = winreg.QueryValueEx(key, "HWID")[0]
                
                if hwid != self.hw_id:
                    return False, "Licence non valide pour ce matériel"
                
                if datetime.now() > expiry_date: #+ timedelta(days=30):
                    print(False, "Licence expirée", None)
                    return False, "Licence expirée", None
                
                print(True, "Licence valide", expiry_date)
                return True, "Licence valide", expiry_date
        except FileNotFoundError:
            return False, "Aucune licence trouvée",None
        except Exception as e:
            print( f"Erreur de vérification 555: {str(e)}")
            import traceback
            traceback.print_exc() 
            return False, f"Erreur de vérification: {str(e)}",None

    def write_license_to_registry00000(self, license_data):
        """Utilise reg.exe pour écrire dans le registre"""
        name = self.sanitize_app_name(self.app_name)
        key_path = fr"HKCU\Software\{name}\Licenses"
        # f"HKCU\Software\{self.app_name}\Licenses"
        try:
            # reg add "HKCU\Software\ecole-server\Licenses" /v ExpiryDate /t REG_SZ /d 2025-09-24 /f

            # reg add "HKCU\Software\ecole-server\Licenses" /v ExpiryDate /t REG_SZ /d WAAU-XUPM-XGC5-6IXM /f
            
            subprocess.run(
                ["reg", "add", key_path,
                "/v", "ExpiryDate", "/t", "REG_SZ",
                "/d", license_data['expiry_date'], "/f"],
                check=True
            )
            subprocess.run(
                ["reg", "add", key_path,
                "/v", "LicenseKey", "/t", "REG_SZ",
                "/d", license_data['key'], "/f"],
                check=True
            )


            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur CalledProcessError : {e}") 
            import traceback
            traceback.print_exc()  
            return False
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def write_license_to_registry00000222(self, license_data):
        try:
            safe_name = self.sanitize_app_name(self.app_name)
            key_path = fr"HKCU\Software\{safe_name}\Licenses"

            subprocess.run(
                ["reg", "add", key_path,
                "/v", "ExpiryDate", "/t", "REG_SZ",
                "/d", license_data['expiry_date'], "/f"],
                check=True
            )
            subprocess.run(
                ["reg", "add", key_path,
                "/v", "LicenseKey", "/t", "REG_SZ",
                "/d", license_data['key'], "/f"],
                check=True
            )

            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur CalledProcessError : {e}")
            return False


    def write_license_to_registry00000__(self, license_data):
        try:
            ps_script = f"""
            New-Item -Path HKCU:\\Software\\{self.app_name}\\Licenses -Force | Out-Null;
            New-ItemProperty -Path HKCU:\\Software\\{self.app_name}\\Licenses `
                -Name LicenseKey -Value '{license_data['key']}' -PropertyType String -Force | Out-Null;
            New-ItemProperty -Path HKCU:\\Software\\{self.app_name}\\Licenses `
                -Name ExpiryDate -Value '{license_data['expiry_date']}' -PropertyType String -Force | Out-Null;
            """

            subprocess.run(
                ["powershell", "-Command", ps_script],
                check=True,
                capture_output=True,
                text=True
            )

            return True

        except subprocess.CalledProcessError as e:
            print("❌ Erreur PowerShell:", e.stderr)
            return False
 
    def write_license_to_registry(self, license_data):
        """Écrit dans le registre Windows avec plusieurs fallbacks"""
        def try_reg_add(key_path, value_name, value_data, reg_type="REG_SZ"):
            try:
                # reg add "HKCU\Software\test-cle" /v test /t REG_SZ /d test /f
                subprocess.run(
                    ["reg", "add", key_path,
                    "/v", value_name,
                    "/t", reg_type,
                    "/d", str(value_data),
                    "/f"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=10
                )
                return True
            except subprocess.CalledProcessError:
                return False

        try:
            # 1. Essai standard avec reg.exe
            base_path = f"HKCU\Software\{self.app_name}\Licenses"
            success = (
                try_reg_add(base_path, "LicenseKey", license_data['key']) and
                try_reg_add(base_path, "ExpiryDate", license_data['expiry_date']) and
                try_reg_add(base_path, "HWID", self.hw_id) #and
                # try_reg_add(base_path, "IsTrial", 1 if license_data.get('is_trial') else 0, "REG_DWORD")
            )

            if success:
                return True

            # 2. Fallback PowerShell avec élévation
            ps_script = f"""
            $key = 'HKCU:\\Software\\{self.app_name}\\Licenses'
            New-Item -Path $key -Force
            Set-ItemProperty -Path $key -Name 'LicenseKey' -Value '{license_data['key']}'
            Set-ItemProperty -Path $key -Name 'ExpiryDate' -Value '{license_data['expiry_date']}'
            Set-ItemProperty -Path $key -Name 'HWID' -Value '{self.hw_id}'
            Set-ItemProperty -Path $key -Name 'IsTrial' -Value {1 if license_data.get('is_trial') else 0}
            """
            
            try:
                subprocess.run(
                    ["powershell", "-Command", ps_script],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=15
                )
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur PowerShell: {e}")

            # 3. Fallback fichier chiffré si tout échoue
            return self._save_to_secure_file(license_data)

        except Exception as e:
            print(f"❌ Erreur critique: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._save_to_secure_file(license_data)

    def _save_to_secure_file(self, license_data):
        """Sauvegarde de fallback avec chiffrement AES"""
        try:
            from cryptography.fernet import Fernet  # Import local pour éviter dépendance inutile
            
            # 1. Préparation du dossier
            config_dir = Path(os.getenv('APPDATA')) / self.app_name
            config_dir.mkdir(exist_ok=True, mode=0o700)
            
            # 2. Préparation des données
            payload = {
                **license_data,
                'hwid': self.hw_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # 3. Chiffrement
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(json.dumps(payload).encode('utf-8'))
            
            # 4. Écriture atomique
            temp_key = config_dir / "license.key.tmp"
            temp_data = config_dir / "license.dat.tmp"
            
            temp_key.write_bytes(key)
            temp_data.write_bytes(encrypted)
            
            # Renommage atomique
            temp_key.replace(config_dir / "license.key")
            temp_data.replace(config_dir / "license.dat")
            
            return True
            
        except Exception as e:
            print(f"❌ Échec du chiffrement: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
    def _read_secure_file(self):
        """Lit les données de licence chiffrées"""
        try:
            config_dir = Path(os.getenv('APPDATA')) / self.app_name
            key = (config_dir / "license.key").read_bytes()
            encrypted = (config_dir / "license.dat").read_bytes()
            
            cipher = Fernet(key)
            return json.loads(cipher.decrypt(encrypted).decode('utf-8'))
        except:
            return None
        
    def _save_to_secure_file1111(self, license_data):
        """Fallback: Sauvegarde dans un fichier chiffré"""
        try:
            config_dir = Path(os.getenv('APPDATA')) / self.app_name
            config_dir.mkdir(exist_ok=True, mode=0o700)
            
            # Ajoute HWID et autres métadonnées
            full_data = {
                **license_data,
                'hwid': self.hw_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Chiffrement AES
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(json.dumps(full_data).encode())
            
            # Écriture sécurisée
            (config_dir / "license.key").write_bytes(key)
            (config_dir / "license.dat").write_bytes(encrypted)
            
            print("⚠ Licence sauvegardée dans un fichier chiffré")
            return True
        except Exception as e:
            print(f"❌ Échec du fallback fichier: {str(e)}")
            return False
            

    def write_to_registry_admin(license_data):
        """Écrit dans le registre avec élévation de privilèges"""
        try:
            ps_script = f"""
            Start-Process powershell -ArgumentList @"
            \$key = 'HKCU:\\Software\\ecole-server\\License'
            New-Item -Path \$key -Force
            Set-ItemProperty -Path \$key -Name 'LicenseKey' -Value '{license_data['key']}'
            Set-ItemProperty -Path \$key -Name 'ExpiryDate' -Value '{license_data['expiry_date']}'
            "@ -Verb RunAs -Wait
            """
            
            subprocess.run(
                ["powershell", "-Command", ps_script],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur PowerShell: {e.stderr.decode()}")
            return False

   
   
   
    # def write_license_to_registry(self, license_data):
    #     """Utilise reg.exe pour écrire dans le registre"""
    #     try: 
    #         subprocess.run(
    #             ["reg", "add", f"HKCU\\Software\\{self.app_name}\\Licenses", 
    #             "/v", "LicenseKey", "/t", "REG_SZ", 
    #             "/d", license_data['key'], "/f"],
    #             check=True
    #         )
            
    #         subprocess.run(
    #             ["reg", "add", f"HKCU\\Software\\{self.app_name}\\Licenses", 
    #             "/v", "ExpiryDate", "/t", "REG_SZ", 
    #             "/d", license_data['expiry_date'], "/f"],
    #             check=True
    #         )
            
    #         return True
            
    #     except subprocess.CalledProcessError: 
    #         print(f"❌ Erreur CalledProcessError : {e} license_data {license_data}")           
    #         return False
    #     except Exception as e:
    #         import traceback
    #         traceback.print_exc() 
    #         print(f"❌ Erreur registre : {e} license_data {license_data}")
    #         return False


    def check_license(self):
        """Vérifie la licence via commandes reg"""
        name = self.sanitize_app_name(self.app_name)
        key_path = fr"HKCU\Software\{self.app_name}\Licenses"
        try:
            # 1. Vérifier si la clé existe
            check_key = subprocess.run(
                ['reg', 'query', key_path],
                capture_output=True,
                text=True
            )
            if "ERROR" in check_key.stderr:
                return False, "Aucune licence trouvée", None

            # 2. Lire les valeurs
            expiry_cmd = ['reg', 'query', key_path, '/v', 'ExpiryDate']
            expiry_result = subprocess.run(expiry_cmd, capture_output=True, text=True)
            expiry_date = expiry_result.stdout.split()[-1]  # Dernière valeur = date
            
            # hwid_cmd = ['reg', 'query', f"HKCU\Software\{self.app_name}\Licenses", '/v', 'HWID']
            # hwid_result = subprocess.run(hwid_cmd, capture_output=True, text=True)
            # hwid = hwid_result.stdout.split()[-1]

            # 3. Validation
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")
            # if hwid != self.hw_id:
            #     return False, "Licence non valide pour ce matériel", None
                
            if datetime.now() > expiry_date:
                return False, "Licence expirée", expiry_date

            return True, "Licence valide", expiry_date

        except Exception as e:
            return False, f"Erreur de vérification: {str(e)}", None

    def write_to_registry_ps(license_data):
        """Écrit dans le registre via PowerShell"""
        try:
            # Convertir les données en JSON pour le passage sécurisé
            license_json = json.dumps(license_data)
            
            # Commande PowerShell en une ligne
            ps_script = f"""
            $key = "HKCU:\\Software\\VotreApplication"
            New-Item -Path $key -Force
            $licenseData = '{license_json}' | ConvertFrom-Json
            Set-ItemProperty -Path $key -Name "LicenseKey" -Value $licenseData.key
            Set-ItemProperty -Path $key -Name "ExpiryDate" -Value $licenseData.expiry_date
            Set-ItemProperty -Path $key -Name "HWID" -Value $licenseData.hwid
            Set-ItemProperty -Path $key -Name "IsTrial" -Value $licenseData.is_trial
            """
            
            # Exécution avec PowerShell
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Erreur PowerShell: {e.stderr}")
            return False



     
    def block_uninstall(self):
        """Empêche la désinstallation si licence expirée"""
        valid, msg = self.check_license()
        if not valid and "expirée" in msg:
            ctypes.windll.user32.MessageBoxW(
                0,
                "La licence a expiré. Veuillez contacter le support.",
                "Erreur de licence",
                0x10
            )
            return False
        return True
     
    def unlock_registry_key(self):
        """Déverrouille la clé de registre (modification possible)."""
        try:
            ps_script = '''      
            $keyPath = "HKCU:\\Software\\ecole-server\\Licenses"
            
            # Vérifier si la clé existe, sinon la créer
            if (-not (Test-Path $keyPath)) {
                New-Item -Path $keyPath -Force
            }
            
            $acl = Get-Acl -Path $keyPath
            
            # Récupérer l'utilisateur actuel
            $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
            
            # Ajouter plusieurs règles d'accès pour plus de sécurité
            $rule1 = New-Object System.Security.AccessControl.RegistryAccessRule(
                $user, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
            )
            
            # Ajouter aussi l'administrateur
            $rule2 = New-Object System.Security.AccessControl.RegistryAccessRule(
                "BUILTIN\\Administrators", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
            )
            
            # Désactiver l'héritage et supprimer toutes les règles existantes
            $acl.SetAccessRuleProtection($true, $false)
            $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }
            
            # Ajouter les nouvelles règles
            $acl.AddAccessRule($rule1)
            $acl.AddAccessRule($rule2)
            
            Set-Acl -Path $keyPath -AclObject $acl
            Write-Output "Clé déverrouillée avec succès"
            '''
            
            # Exécuter PowerShell en tant qu'administrateur
            result = subprocess.run(["powershell", "-Command", ps_script], 
                                check=True, capture_output=True, text=True)
            print("🔓 Clé déverrouillée (modifications autorisées)")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur PowerShell: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def unlock_registry_keyaaa(self):
        ps_take_ownership = r'''
        $key = "HKCU:\Software\ecole-server\Licenses"
        $acl = Get-Acl $key
        $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $acl.SetOwner([System.Security.Principal.NTAccount]$user)
        Set-Acl $key $acl
        '''

        ps_grant_full = r'''
        $key = "HKCU:\Software\ecole-server\Licenses"
        $acl = Get-Acl $key
        $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        $rule = New-Object System.Security.AccessControl.RegistryAccessRule($user,"FullControl","Allow")
        $acl.SetAccessRuleProtection($true, $false)
        $acl.SetAccessRule($rule)
        Set-Acl $key $acl
        '''

        try:
            subprocess.run(["powershell", "-Command", ps_take_ownership], check=True)
            subprocess.run(["powershell", "-Command", ps_grant_full], check=True)
            print("🔓 Clé déverrouillée avec succès (droits FullControl donnés)")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Erreur:", e)
            return False



    # def unlock_registry_key(self):
    #     """Déverrouille la clé de registre (modification possible)."""
    #     self_app_name = "ecole-server"
    #     key_path = f"Software\\{self_app_name}\\Licenses"
    #     ps_reg_path = f"HKCU:\\{key_path}"

    #     try:
    #         # ps_script = f'''
    #         # $keyPath = "{ps_reg_path}"
    #         # $acl = Get-Acl -Path $keyPath
            
    #         # $rule = New-Object System.Security.AccessControl.RegistryAccessRule(
    #         #     "Everyone", "FullControl", "Allow"
    #         # )
    #         # $acl.SetAccessRuleProtection($true, $false)  # Désactive héritage
    #         # $acl.SetAccessRule($rule)
    #         # Set-Acl -Path $keyPath -AclObject $acl
    #         # '''

    #         ps_script = f'''      
    #         $keyPath = "HKCU:\Software\ecole-server\Licenses"
    #                 $acl = Get-Acl -Path $keyPath

    #                 # Récupérer l’utilisateur actuel
    #                 $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    #                 $rule = New-Object System.Security.AccessControl.RegistryAccessRule(
    #                     $user, "FullControl", "Allow"
    #                 )

    #                 $acl.SetAccessRuleProtection($true, $false) # Désactive héritage
    #                 $acl.SetAccessRule($rule)
    #                 Set-Acl -Path $keyPath -AclObject $acl
    #         '''
    #         subprocess.run(["powershell", "-Command", ps_script], check=True)
    #         print("🔓 Clé déverrouillée (modifications autorisées)")
    #     except ValueError:
    #         print(f"❌ Erreur ValrrrrrueError: {str(e)}")
    #         import traceback
    #         traceback.print_exc()
    #         return False
    #     except Exception as e:
    #         print(f"❌ Erreurrrrrrrrrr critique: {str(e)}")
    #         import traceback
    #         traceback.print_exc()
    #         return False

    
