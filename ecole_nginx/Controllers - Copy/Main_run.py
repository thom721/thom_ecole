import os
import sys
import subprocess
import shutil
import re
import socket
import zipfile
from shutil import copyfile
import time
import requests
import psutil # type: ignore
from PySide6.QtWidgets import QApplication,QMessageBox
from Helper.verify_key import ask_for_activation_key
from Helper.server_key_generate import show_activation_key,delete_key,is_license_valid,get_mac_address
from Helper.Ip_manager import Ip_manager
from Helper.manage_activate import Manage_active

import winreg
import ctypes
from pathlib import Path
from Helper.save_onReg import LicenseManager
import re
import sys
from typing import Optional
import msvcrt  # Gestion des entrées clavier sous Windows
from colorama import Fore

class Main_run:
    def __init__(self):
        # colorama.init(autoreset=True)
        # Configuration
        # rd /s /q "C:\Users\fritz\OneDrive\Desktop\ecole_1\mysql-8.0.41-winx64"
        # rd /s /q "C:\Users\fritz\OneDrive\Desktop\ecole_1\mysql-8.0.41-winx64\data"
        self.install_dir = os.path.join(os.getenv('PROGRAMFILES'),'ecole-serve')
        current_dir = os.path.dirname(__file__)
        self.current_project = self.install_dir # os.getcwd() #= os.path.dirname(current_dir)
      
        self.APACHE_PORT = 8080
        
        self.NGINX_SSL_PORT = "443"  # Port standard HTTPS
        self.NGINX_HTTP_PORT = "80"  # Port standard HTTP
        # self.NGINX_PORT
        self.API_FOLDER = os.path.join(self.current_project, 'api')
 
        self.mysql_version = "8.0.41"
        self.extract_dir = os.path.join(self.current_project, f"mysql-{self.mysql_version}-winx64")
        self.bin_dir = os.path.join(self.extract_dir, "bin")
        # self.my_ini_path = os.path.join(self.extract_dir, "my.ini")
        self.password = None
        self.ip_manager = Ip_manager()
        self.manage_active = Manage_active()
        # self.running_direct_migration = False

    def keyPressEvent(self,event): 
        print(f"Enter pressé dans le modal ! ✅ {event}")
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            print(f"Enter pressé dans le modal ! ✅ {event}")
            QApplication.quit
            # self.analyse_row_and_fetch_data()
            # tu peux appeler ici ta fonction
            # ex: self.on_enter_pressed()


    def add_to_startup(name="école-server", file_path=None):
        if file_path is None:
            file_path = sys.executable 
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(reg_key)
    
    def get_resource_path(self, relative_path: str) -> str:
        """Retourne le chemin absolu d'une ressource (compatible PyInstaller et Nuitka)."""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            base_path = sys._MEIPASS
        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
        else:
            # Exécution normale
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


    def is_installed_a(self, program):
        try:
            if program == 'nginx':
              subprocess.run([program, "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            else:
                subprocess.run([program, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
           
            return True
        except FileNotFoundError:         
            return False
        except subprocess.CalledProcessError as e:
           
            return False
 

    def is_installed(self, program: str,directory) -> bool:
        exe_name = program
        if os.name == "nt":  # Windows
            exe_name += ".exe"

        program_path = os.path.join(directory, exe_name)

        print(f"program_path   {program_path}")

        if not os.path.isfile(program_path):
            return False

        try:
            if program == "nginx":
                subprocess.run(
                    [program_path, "-v"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
            else:
                subprocess.run(
                    [program_path, "--version"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True
                )
            return True

        except subprocess.CalledProcessError:
            return False



    def install_program(self, url, installer_name, args):
        installer_path = os.path.join(os.getcwd(), installer_name)

        try:
            print(f"\n [+]   Téléchargement de {installer_name}...")
            # if not os.path.exists(installer_path):
            if not os.path.exists(self.get_resource_path(installer_path)):
                subprocess.run(["curl", "-L", url, "-o", installer_path], check=True)
         
            if installer_name.endswith(".zip"):
                extract_path = os.path.join(
                    os.getcwd(), 
                    installer_name.replace(".zip", "") if installer_name.startswith('php') else ""
                )
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                print(f"\n [+]   Extracted {installer_name}")
                # os.remove(installer_path)

                return extract_path 

            # For other installer types (e.g., .exe), just run the installer
            subprocess.run(["powershell", "-Command", f"Start-Process {installer_path} -ArgumentList '{args}' -Wait -NoNewWindow"], check=True)
            # os.remove(installer_path)
        except subprocess.CalledProcessError as e:
            print(f"\n [x]   Erreur lors du téléchargement du fichier depuis {url}")
            print(e.stderr)  # Afficher l'erreur retournée par PowerShell
            return None  # Ou gérer l'erreur de manière appropriée
        except Exception as e:
            print(f"Erreur lors de l'ajout du chemin : {e}")
            import traceback
            traceback.print_exc()


    def add_to_path(self, path):
        try:
            # Vérifier si PowerShell est accessible
            paths = os.environ.get("PATH", "")
            if path not in paths:
                try:
                    # Vérifier si PowerShell est disponible
                    subprocess.run(["powershell", "-Command", "exit"], check=True)
                    # print("Utilisation de PowerShell pour modifier Path.")

                    shell_command = [
                        "powershell",
                        "-Command",
                        f"$env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';{path}';"
                        "[System.Environment]::SetEnvironmentVariable('Path', $env:Path, 'Machine')"
                    ]
                except FileNotFoundError:
                    # Si PowerShell n'est pas trouvé, utiliser cmd.exe à la place
                    # print("PowerShell n'est pas disponible. Utilisation de cmd.exe à la place.")

                    # Récupérer la valeur actuelle de Path
                    current_path = os.environ["Path"]

                    # Ajouter le nouveau chemin
                    new_full_path = f"{current_path};{path}"

                    shell_command = ["cmd", "/c", f"setx Path \"{new_full_path}\" /M"]

                # Exécuter la commande
                try:
                    subprocess.run(shell_command, check=True)
                    print(f"Chemin ajouté avec succès : {path}")
                except subprocess.CalledProcessError as e:
                    print(f"Erreur lors de la mise à jour de Path : {e}")
  
        
        except Exception as e:
            print(f"Erreur lors de l'ajout du chemin : {e}")

    def validate_ip(self, ip):
        pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
        if not pattern.match(ip):
            return False
        return ip in socket.gethostbyname_ex(socket.gethostname())[2]
    
  

        # return key_path, cert_path
    

    def genere_ssl_key111(self, ip_address, update_client = False): 
        firstPath = "C:\Program Files\ecole-serve"
        _conf_path = os.path.join(firstPath,"certspath")

        key_path = Path(_conf_path, f'aplekol360.local-key.pem').as_posix()
        cert_path = Path(_conf_path, f'aplekol360.local.pem').as_posix()
        server_key = Path(_conf_path, f'server.key').as_posix()
        server_crt = Path(_conf_path, f'server.crt').as_posix()

        ca_key = Path(_conf_path, 'ca.key').as_posix()
        ca_cert = Path(_conf_path, 'ca.pem').as_posix()
        csr_path = Path(_conf_path, f'aplekol360.local.csr').as_posix()
        # san_file = r"C:\Apache24\conf\openssl.cnf"
        san_file = Path(_conf_path, f'aplekol360.local_san.cnf').as_posix()

        try:
            ca_conf = Path(_conf_path, 'ca.cnf').as_posix()
            with open(ca_conf, 'w') as f:
                f.write("""[req]
            distinguished_name=req_distinguished_name
            x509_extensions = v3_ca
            [req_distinguished_name]
            [ v3_ca ]
            subjectKeyIdentifier=hash
            authorityKeyIdentifier=keyid:always,issuer
            basicConstraints = critical, CA:true
            keyUsage = critical, digitalSignature, cRLSign, keyCertSign
            """)
            # openssl verify -CAfile "C:\Program Files\ecole-serve\Apache24\conf\ca.pem" "C:\Program Files\ecole-serve\Apache24\conf\server.crt"

            # 1. Générer CA (si pas déjà là)
            # if not os.path.exists(ca_key) or not os.path.exists(ca_cert):
                # print("🔐 Génération de l'autorité de certification (CA)...")
            subprocess.run(['openssl', 'genrsa', '-out', ca_key, '2048'], check=True)
            # subprocess.run([
            #     'openssl', 'req', '-x509', '-new', '-nodes', '-key', ca_key, '-sha256',
            #     '-days', '3650', '-out', ca_cert, '-subj', '/CN=Ecole CA'
            # ], check=True)

            subprocess.run([
                'openssl', 'req', '-x509', '-new', '-nodes', '-key', ca_key, '-sha256',
                '-days', '3650', '-out', ca_cert, '-subj', '/CN=aplekol360.local',
                '-config', ca_conf, '-extensions', 'v3_ca'
            ], check=True)

            # 2. Générer SAN config
            with open(san_file, 'w') as f:
                f.write(f"""[req]
            distinguished_name=req_distinguished_name
            req_extensions=v3_req
            [req_distinguished_name]
            [v3_req]
            subjectAltName=IP:{ip_address},DNS:aplekol360.local
            """)

            # 3. Générer CSR + Clé privée serveur
            print("🔐 Génération de la clé privée du serveur...")
            subprocess.run(['openssl', 'genrsa', '-out', key_path, '2048'], check=True)

            print("📜 Création de la CSR...")
            subprocess.run([
                'openssl', 'req', '-new', '-key', key_path, '-out', csr_path,
                '-subj', f'/CN=aplekol360.local', '-config', san_file
            ], check=True)

            # 4. Signer le certificat avec la CA
            print("✅ Signature du certificat serveur avec la CA...")
            subprocess.run([
                'openssl', 'x509', '-req', '-in', csr_path, '-CA', ca_cert, '-CAkey', ca_key,
                '-CAcreateserial', '-out', cert_path, '-days', '3650',
                '-sha256', '-extfile', san_file, '-extensions', 'v3_req'
            ], check=True)
        except Exception as e:
            print(f"[x] Erreur lors de l'échhhhhhhhhhhhhhhhhhhhhhhhhhriture dans httpd-ssl.conf : {e} \n\n\n\n\n")
            import traceback
            traceback.print_exc()

        if Path(key_path).exists() and Path(cert_path).exists():
            copyfile(key_path, server_key)
            copyfile(cert_path, server_crt) 
        else:
            print("❌ Les fichiers source de certificat n'existent pas.")

        # try:
        #     path=r"C:\Program Files\ecole-serve\certspath\ca.pem"
        #     subprocess.run([
        #         'certutil', '-addstore', '-f', 'Root', path
        #     ], check=True)
        #     print(f"addstore certutil mise à jour avec succès. {ip_address}")
        # except Exception as e:
        #     print(f"owioeriheori    {e}")

        if update_client:
            self.toggle_authorization_update(server_ip=ip_address)

    def genere_ssl_key11(self, ip_address, update_client=False):
        """Générer les certificats SSL - Version corrigée"""
        try:
            firstPath = r"C:\Program Files\ecole-serve"
            _conf_path = os.path.join(firstPath, "certspath")
            
            # 1. S'ASSURER QUE LE RÉPERTOIRE EXISTE
            print(f"📁 Création du répertoire certspath: {_conf_path}")
            os.makedirs(_conf_path, exist_ok=True)
            
            # Donner les permissions
            self.set_full_permissions(_conf_path)
            
            # 2. Chemins des fichiers
            key_path = os.path.join(_conf_path, 'aplekol360.local-key.pem')
            cert_path = os.path.join(_conf_path, 'aplekol360.local.pem')
            server_key = os.path.join(_conf_path, 'server.key')
            server_crt = os.path.join(_conf_path, 'server.crt')
            ca_key = os.path.join(_conf_path, 'ca.key')
            ca_cert = os.path.join(_conf_path, 'ca.pem')
            csr_path = os.path.join(_conf_path, 'aplekol360.local.csr')
            san_file = os.path.join(_conf_path, 'aplekol360.local_san.cnf')
            ca_conf = os.path.join(_conf_path, 'ca.cnf')
            
            print(f"🔐 Génération des certificats SSL pour IP: {ip_address}")
            
            # 3. Créer le fichier ca.cnf (celui qui manquait)
            print("📝 Création du fichier ca.cnf...")
            ca_config_content = """[req]
                distinguished_name = req_distinguished_name
                x509_extensions = v3_ca
                prompt = no

                [req_distinguished_name]
                CN = aplekol360.local CA

                [v3_ca]
                subjectKeyIdentifier = hash
                authorityKeyIdentifier = keyid:always,issuer
                basicConstraints = critical, CA:true
                keyUsage = critical, digitalSignature, cRLSign, keyCertSign
                """
            
            with open(ca_conf, 'w') as f:
                f.write(ca_config_content)
            
            # 4. Générer la CA
            print("🔑 Génération de l'autorité de certification (CA)...")
            if not os.path.exists(ca_key) or not os.path.exists(ca_cert):
                subprocess.run(['openssl', 'genrsa', '-out', ca_key, '2048'], 
                            check=True, capture_output=True)
                
                subprocess.run([
                    'openssl', 'req', '-x509', '-new', '-nodes', '-key', ca_key, '-sha256',
                    '-days', '3650', '-out', ca_cert, '-subj', '/CN=aplekol360.local',
                    '-config', ca_conf, '-extensions', 'v3_ca'
                ], check=True, capture_output=True)
            
            # 5. Créer le fichier SAN
            print("📝 Création du fichier SAN...")
            san_content = f"""[req]
                distinguished_name = req_distinguished_name
                req_extensions = v3_req
                prompt = no

                [req_distinguished_name]
                CN = aplekol360.local

                [v3_req]
                subjectAltName = @alt_names

                [alt_names]
                DNS.1 = aplekol360.local
                IP.1 = {ip_address}
                """
            
            with open(san_file, 'w') as f:
                f.write(san_content)
            
            # 6. Générer la clé privée du serveur
            print("🔑 Génération de la clé privée du serveur...")
            subprocess.run(['openssl', 'genrsa', '-out', key_path, '2048'], 
                        check=True, capture_output=True)
            
            # 7. Générer la CSR
            print("📄 Génération de la CSR...")
            subprocess.run([
                'openssl', 'req', '-new', '-key', key_path, '-out', csr_path,
                '-subj', '/CN=aplekol360.local', '-config', san_file
            ], check=True, capture_output=True)
            
            # 8. Signer le certificat avec la CA
            print("✍️  Signature du certificat serveur...")
            subprocess.run([
                'openssl', 'x509', '-req', '-in', csr_path, '-CA', ca_cert, '-CAkey', ca_key,
                '-CAcreateserial', '-out', cert_path, '-days', '3650',
                '-sha256', '-extfile', san_file, '-extensions', 'v3_req'
            ], check=True, capture_output=True)
            
            print(Fore.GREEN + "✅ Certificats SSL générés avec succès")
            
            # 9. Copier les fichiers serveur
            if os.path.exists(key_path) and os.path.exists(cert_path):
                shutil.copy2(key_path, server_key)
                shutil.copy2(cert_path, server_crt)
                print(Fore.GREEN + "✅ Fichiers serveur copiés")
            else:
                print(Fore.RED + "❌ Fichiers source non trouvés")
                return False
            
            # 10. Ajouter la CA au magasin Windows
            if update_client:
                print("🪟 Ajout de la CA au magasin Windows...")
                try:
                    subprocess.run(['certutil', '-addstore', '-f', 'Root', ca_cert], 
                                check=True, capture_output=True)
                    print(Fore.GREEN + "✅ CA ajoutée au magasin Windows")
                except Exception as e:
                    print(Fore.YELLOW + f"⚠️  Impossible d'ajouter la CA: {e}")
            
            # 11. Vérifier les fichiers créés
            print("\n📋 Vérification des fichiers générés:")
            for cert_file in ['server.key', 'server.crt', 'ca.pem']:
                file_path = os.path.join(_conf_path, cert_file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(Fore.GREEN + f"   ✓ {cert_file}: {size} octets")
                else:
                    print(Fore.RED + f"   ✗ {cert_file}: NON TROUVÉ")
            
            # return True
            
        except Exception as e:
            print(f"\n❌ Erreur génération SSL: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


    def genere_ssl_key(self, ip_address, update_client=False):
        """Générer les certificats SSL - Version Corrigée et Validée"""
        try:
            firstPath = r"C:\Program Files\ecole-serve"
            _conf_path = os.path.join(firstPath, "certspath")
            
            # 1. S'ASSURER QUE LE RÉPERTOIRE EXISTE
            os.makedirs(_conf_path, exist_ok=True)
            self.set_full_permissions(_conf_path) # Assurez-vous que cette méthode existe
            
            # 2. Chemins des fichiers
            key_path = os.path.join(_conf_path, 'aplekol360.local-key.pem')
            cert_path = os.path.join(_conf_path, 'aplekol360.local.pem')
            server_key = os.path.join(_conf_path, 'server.key')
            server_crt = os.path.join(_conf_path, 'server.crt')
            ca_key = os.path.join(_conf_path, 'ca.key')
            ca_cert = os.path.join(_conf_path, 'ca.pem')
            csr_path = os.path.join(_conf_path, 'aplekol360.local.csr')
            san_file = os.path.join(_conf_path, 'aplekol360.local_san.cnf')
            ca_conf = os.path.join(_conf_path, 'ca.cnf')
            
            print(f"🔐 Génération SSL pour: {ip_address}")

            # 3. Créer le fichier ca.cnf (CORRECTION : CN différent du serveur)
            ca_config_content = """[req]
                distinguished_name = req_distinguished_name
                x509_extensions = v3_ca
                prompt = no

                [req_distinguished_name]
                CN = aplekol360.local Root CA

                [v3_ca]
                subjectKeyIdentifier = hash
                authorityKeyIdentifier = keyid:always,issuer
                basicConstraints = critical, CA:true
                keyUsage = critical, digitalSignature, cRLSign, keyCertSign
                """
            with open(ca_conf, 'w') as f:
                f.write(ca_config_content)
            
            # 4. Générer la CA
            if not os.path.exists(ca_key) or not os.path.exists(ca_cert):
                subprocess.run(['openssl', 'genrsa', '-out', ca_key, '2048'], check=True)
                subprocess.run([
                    'openssl', 'req', '-x509', '-new', '-nodes', '-key', ca_key, '-sha256',
                    '-days', '3650', '-out', ca_cert, '-config', ca_conf, '-extensions', 'v3_ca'
                ], check=True)
            
            # 5. Créer le fichier SAN (CORRECTION : Ajout serverAuth et CA:FALSE)
            san_content = f"""[req]
                distinguished_name = req_distinguished_name
                req_extensions = v3_req
                prompt = no

                [req_distinguished_name]
                CN = aplekol360.local

                [v3_req]
                basicConstraints = CA:FALSE
                keyUsage = digitalSignature, keyEncipherment
                extendedKeyUsage = serverAuth
                subjectAltName = @alt_names

                [alt_names]
                DNS.1 = aplekol360.local
                DNS.2 = localhost
                IP.1 = {ip_address}
                IP.2 = 127.0.0.1
                """
            with open(san_file, 'w') as f:
                f.write(san_content)
            
            # 6 & 7. Clé serveur et CSR
            subprocess.run(['openssl', 'genrsa', '-out', key_path, '2048'], check=True)
            subprocess.run([
                'openssl', 'req', '-new', '-key', key_path, '-out', csr_path,
                '-config', san_file
            ], check=True)
            
            # 8. Signature (CORRECTION : Utilisation de v3_req pour inclure les SAN)
            subprocess.run([
                'openssl', 'x509', '-req', '-in', csr_path, '-CA', ca_cert, '-CAkey', ca_key,
                '-CAcreateserial', '-out', cert_path, '-days', '3650',
                '-sha256', '-extfile', san_file, '-extensions', 'v3_req'
            ], check=True)
            
            # 9. Copie vers les noms standards
            shutil.copy2(key_path, server_key)
            shutil.copy2(cert_path, server_crt)
            
            # 10. Magasin Windows
            if update_client:
                subprocess.run(['certutil', '-addstore', '-f', 'Root', ca_cert], check=True)

            # 11. VÉRIFICATION FINALE (Le test qui échouait avant)
            result = subprocess.run(['openssl', 'verify', '-CAfile', ca_cert, server_crt], 
                                    capture_output=True, text=True)
            
            if "OK" in result.stdout:
                print(Fore.GREEN + "✅ SSL validé avec succès : aplekol360.local: OK")
                return True
            else:
                print(Fore.RED + f"❌ Échec de validation interne : {result.stderr}")
                return False

        except Exception as e:
            print(Fore.RED + f"❌ Erreur: {str(e)}")
            return False

    def toggle_authorization_update(self, server_ip):
        # openssl verify -CAfile ca.pem server.crt

        cert_path = r"C:\Program Files\ecole-serve\certspath\ca.pem" 
        pem, b64 = self.get_server_cert_content(cert_path)
        payload = {"certi_key": b64}
        base_url = f"https://aplekol360.local/api/update-user"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        } 
        try:
            response = requests.post(base_url, json=payload, headers=headers, timeout=30,verify="C:\Program Files\ecole-serve\certspath\ca.pem")
            response_data = response.json()
            print(response_data)
            if response.status_code == 200:
                # Nouvelle autorisation renvoyée par l'API
                new_status = response_data.get('authorisation', 0)
                if new_status == 1: 
                    return response_data
                else: 
                    return response_data 

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")

    def get_server_cert_content(self, cert_path):
        """Lit le fichier cert et le renvoie en base64 ou texte brut"""
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

             
    def configure_nginx(self, ip_ser):
        """Configure Nginx avec votre système SSL existant"""
        nginx_conf_dir = os.path.join(self.current_project, "nginx", "conf")
        nginx_conf_path = os.path.join(nginx_conf_dir, "nginx.conf")
        
        # Chemins importants
        nginx_directory = os.path.join(self.current_project, 'nginx')
        php_dir = os.path.join(self.current_project, "php")
        htdocs_dir = os.path.join(nginx_directory, 'html', 'api', 'public')
        
        # Utiliser vos chemins SSL existants
        certs_path = r"C:\Program Files\ecole-serve\certspath"
        ssl_key = os.path.join(certs_path, 'server.key')
        ssl_cert = os.path.join(certs_path, 'server.crt')
        ca_cert = os.path.join(certs_path, 'ca.pem')
        
        # Créer le répertoire htdocs s'il n'existe pas
        os.makedirs(htdocs_dir, exist_ok=True)
        
        # Configuration Nginx optimisée pour votre SSL
        nginx_config = f'''
            worker_processes  auto;

            events {{
                worker_connections  1024;
                multi_accept on;
            }}

        http {{
            include       mime.types;
            default_type  application/octet-stream;
            
            # Optimisations de performance
            sendfile        on;
            tcp_nopush      on;
            tcp_nodelay     on;
            keepalive_timeout  65;
            keepalive_requests 100;
            
            # Buffer optimisations
            client_body_buffer_size 10K;
            client_header_buffer_size 1k;
            client_max_body_size 100m;
            large_client_header_buffers 4 8k;
            
            # Timeouts
            client_body_timeout 12;
            client_header_timeout 12;
            send_timeout 10;
            
            # Gzip compression
            gzip on;
            gzip_vary on;
            gzip_min_length 256;
            gzip_proxied any;
            gzip_comp_level 6;
            gzip_types
                application/atom+xml
                application/javascript
                application/json
                application/rss+xml
                application/vnd.ms-fontobject
                application/x-font-ttf
                application/x-web-app-manifest+json
                application/xhtml+xml
                application/xml
                font/opentype
                image/svg+xml
                image/x-icon
                text/css
                text/plain
                text/x-component
                text/xml;

            # Configuration SSL améliorée
            ssl_certificate      "{ssl_cert}";
            ssl_certificate_key  "{ssl_key}";
            ssl_trusted_certificate "{ca_cert}";
            
            # Paramètres SSL sécurisés
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
            ssl_prefer_server_ciphers on;
            ssl_session_cache shared:SSL:10m;
            ssl_session_timeout 10m;
            ssl_session_tickets off;
            
            # HSTS (Strict Transport Security)
            add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
            
            # Headers de sécurité
            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
            add_header Referrer-Policy "strict-origin-when-cross-origin" always;
            
            # Configuration PHP via FastCGI
            upstream php_fastcgi {{
                server 127.0.0.1:9000;
                keepalive 32;
            }}

            # Cache FastCGI
            fastcgi_cache_path "{os.path.join(nginx_directory, 'cache', 'fastcgi')}" levels=1:2 keys_zone=FCGICACHE:100m inactive=60m;
            fastcgi_cache_key "$scheme$request_method$host$request_uri";
            fastcgi_cache_use_stale error timeout invalid_header http_500;
            fastcgi_ignore_headers Cache-Control Expires Set-Cookie;

            # Serveur principal HTTPS
            server {{
                listen       {self.NGINX_SSL_PORT} ssl;
                listen       [::]:{self.NGINX_SSL_PORT} ssl;
                #http2 on;
                server_name  {ip_ser} aplekol360.local localhost;
                
                ssl_certificate      "{ssl_cert}";
                ssl_certificate_key  "{ssl_key}";
                ssl_trusted_certificate "{ca_cert}";
                
                root   "{htdocs_dir}";
                index  index.php index.html index.htm;
                
                # Logs
                access_log  "{os.path.join(nginx_directory, 'logs', 'access.log')}";
                error_log   "{os.path.join(nginx_directory, 'logs', 'error.log')}" warn;
                
                # Optimisations fichiers statiques
                location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {{
                    expires 1y;
                    add_header Cache-Control "public, immutable";
                    access_log off;
                }}
                
                location / {{
                    try_files $uri $uri/ /index.php?$query_string;
                }}

                # Passer les fichiers PHP à PHP-FPM avec cache
                location ~ \.php$ {{
                    fastcgi_pass   php_fastcgi;
                    fastcgi_index  index.php;
                    fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
                    fastcgi_param  HTTPS ${{ssl_protocol}};
                    include        fastcgi_params;
                    
                    # Cache FastCGI
                    fastcgi_cache FCGICACHE;
                    fastcgi_cache_valid 200 301 302 5m;
                    fastcgi_cache_valid 404 1m;
                    fastcgi_cache_methods GET HEAD;
                    fastcgi_cache_bypass $http_cache_control;
                    add_header X-Cache $upstream_cache_status;
                    
                    # Timeouts
                    fastcgi_connect_timeout 60s;
                    fastcgi_send_timeout 60s;
                    fastcgi_read_timeout 60s;
                    fastcgi_buffers 16 16k;
                    fastcgi_buffer_size 32k;
                }}

                # Bloquer l'accès aux fichiers sensibles
                location ~ /\.(?!well-known).* {{
                    deny all;
                }}
                
                location ~ /(\.env|composer\.json|composer\.lock|package\.json|\.git) {{
                    deny all;
                }}
                
                location ~* \.(log|sql|bak|old)$ {{
                    deny all;
                }}
                
                # Health check
                location /nginx-health {{
                    access_log off;
                    return 200 "healthy";
                    add_header Content-Type text/plain;
                }}
            }}

            # Redirection HTTP vers HTTPS
            server {{
                listen       {self.NGINX_HTTP_PORT};
                listen       [::]:{self.NGINX_HTTP_PORT};
                server_name  {ip_ser} aplekol360.local localhost;
                
                # Redirection permanente vers HTTPS
                return 301 https://$server_name:{self.NGINX_SSL_PORT}$request_uri;
            }}
        }}
        '''

        try:
            # Créer les répertoires nécessaires
            os.makedirs(os.path.join(nginx_directory, 'logs'), exist_ok=True)
            os.makedirs(os.path.join(nginx_directory, 'cache', 'fastcgi'), exist_ok=True)
            
            # Écrire la configuration Nginx
            with open(nginx_conf_path, 'w') as file:
                file.write(nginx_config)
            
            print(Fore.GREEN + f"\n [ok]   Configuration Nginx écrite avec votre SSL personnalisé")
            
            # Copier vos certificats SSL existants vers le répertoire Nginx
            self.copy_ssl_certificates_to_nginx(certs_path, nginx_conf_dir)
            
            # Configurer PHP pour FastCGI (adapté pour Nginx)
            self.configure_php_for_fastcgi_nginx(php_dir)
            
            # Mettre à jour le magasin de certificats Windows
            self.update_windows_certificate_store(ca_cert)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la configuration de Nginx: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def copy_ssl_certificates_to_nginx(self, source_path, nginx_conf_dir):
        """Copier les certificats SSL existants vers Nginx"""
        try:
            cert_files = ['server.key', 'server.crt', 'ca.pem']
            
            for cert_file in cert_files:
                source_file = os.path.join(source_path, cert_file)
                dest_file = os.path.join(nginx_conf_dir, cert_file)
                
                if os.path.exists(source_file):
                    shutil.copy2(source_file, dest_file)
                    print(Fore.GREEN + f" [ok]   Copié: {cert_file}")
                else:
                    print(Fore.YELLOW + f" [warn] Fichier non trouvé: {source_file}")
                    
        except Exception as e:
            print(f" [x]   Erreur copie certificats: {e}")

    def configure_php_for_fastcgi_nginx(self, php_dir):
        """Configurer PHP pour FastCGI avec Nginx (optimisé)"""
        try:
            php_ini_path = os.path.join(php_dir, "php.ini")
            
            if os.path.exists(php_ini_path):
                with open(php_ini_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Modifications spécifiques pour Nginx + FastCGI
                modifications = {
                    'cgi.fix_pathinfo=1': 'cgi.fix_pathinfo=0',
                    ';cgi.fix_pathinfo=1': 'cgi.fix_pathinfo=0',
                    
                    # Activer les extensions nécessaires
                    ';extension=curl': 'extension=curl',
                    ';extension=gd': 'extension=gd',
                    ';extension=mbstring': 'extension=mbstring',
                    ';extension=mysqli': 'extension=mysqli',
                    ';extension=openssl': 'extension=openssl',
                    ';extension=pdo_mysql': 'extension=pdo_mysql',
                    ';extension=fileinfo': 'extension=fileinfo',
                    ';extension=exif': 'extension=exif',
                    
                    # Optimisations pour FastCGI
                    'max_execution_time = 30': 'max_execution_time = 300',
                    'max_input_time = 60': 'max_input_time = 300',
                    'memory_limit = 128M': 'memory_limit = 256M',
                    
                    # Timezone
                    ';date.timezone =': 'date.timezone = Europe/Paris',
                    'date.timezone =': 'date.timezone = Europe/Paris',
                    
                    # Upload
                    'upload_max_filesize = 2M': 'upload_max_filesize = 100M',
                    'post_max_size = 8M': 'post_max_size = 105M',
                    
                    # Output buffering pour Nginx
                    'output_buffering = 4096': 'output_buffering = Off',
                    
                    # Sessions
                    'session.gc_maxlifetime = 1440': 'session.gc_maxlifetime = 86400',
                    'session.cookie_lifetime = 0': 'session.cookie_lifetime = 86400',
                    
                    # OPCache (amélioration performance)
                    ';opcache.enable=1': 'opcache.enable=1',
                    ';opcache.memory_consumption=128': 'opcache.memory_consumption=256',
                    ';opcache.interned_strings_buffer=8': 'opcache.interned_strings_buffer=16',
                    ';opcache.max_accelerated_files=10000': 'opcache.max_accelerated_files=20000',
                    ';opcache.revalidate_freq=2': 'opcache.revalidate_freq=60',
                    ';opcache.fast_shutdown=1': 'opcache.fast_shutdown=1',
                    ';opcache.enable_cli=1': 'opcache.enable_cli=1',
                }
                
                for old, new in modifications.items():
                    if old in content:
                        content = content.replace(old, new)
                
                # Ajouter des configurations si manquantes
                additional_configs = [
                    '\n; Configuration optimisée pour Nginx + FastCGI',
                    'realpath_cache_size = 4096K',
                    'realpath_cache_ttl = 600',
                    'expose_php = Off',
                    'opcache.enable_file_override = 1',
                    'opcache.validate_timestamps = 0',
                    'opcache.save_comments = 1',
                    'opcache.load_comments = 1',
                ]
                
                content += '\n' + '\n'.join(additional_configs)
                
                with open(php_ini_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(Fore.GREEN + " [ok]   Configuration PHP optimisée pour Nginx")
                
        except Exception as e:
            print(f" [x]   Erreur configuration PHP: {e}")

    def update_windows_certificate_store(self, ca_cert_path):
        """Ajouter la CA au magasin de certificats Windows (comme vous le faites déjà)"""
        try:
            if os.path.exists(ca_cert_path):
                # Vérifier si le certificat est déjà installé
                check_cmd = ['certutil', '-verifystore', 'Root', ca_cert_path]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if "ERROR" in result.stderr or "Certificate NOT found" in result.stdout:
                    # Installer le certificat
                    install_cmd = ['certutil', '-addstore', '-f', 'Root', ca_cert_path]
                    subprocess.run(install_cmd, check=True)
                    print(Fore.GREEN + " [ok]   CA ajoutée au magasin de certificats Windows")
                else:
                    print(Fore.GREEN + " [info] CA déjà présente dans le magasin Windows")
            else:
                print(Fore.YELLOW + f" [warn] Fichier CA non trouvé: {ca_cert_path}")
                
        except Exception as e:
            print(f" [x]   Erreur mise à jour magasin certificats: {e}")

    def configure_nginx_service(self):
        """Configurer et installer le service Nginx"""
        try:
            nginx_dir = os.path.join(self.current_project, 'nginx')
            nginx_exe = os.path.join(nginx_dir, 'nginx.exe')
            
            # Vérifier les fichiers SSL
            ssl_files = [
                os.path.join(nginx_dir, 'conf', 'server.key'),
                os.path.join(nginx_dir, 'conf', 'server.crt'),
                os.path.join(nginx_dir, 'conf', 'ca.pem')
            ]
            
            for ssl_file in ssl_files:
                if not os.path.exists(ssl_file):
                    print(Fore.YELLOW + f" [warn] Fichier SSL manquant: {ssl_file}")
            
            # Tester la configuration
            print("\n [+]   Test de configuration Nginx...")
            test_result = subprocess.run(
                [nginx_exe, "-t"], 
                capture_output=True, 
                text=True,
                cwd=nginx_dir
            )
            
            if test_result.returncode != 0:
                print(Fore.RED + f" [x]   Erreur configuration: {test_result.stderr}")
                return False
            
            print(Fore.GREEN + " [ok]   Test configuration réussi")
            
            # Arrêter Nginx s'il est en cours d'exécution
            subprocess.run([nginx_exe, "-s", "stop"], 
                        capture_output=True, 
                        cwd=nginx_dir)
            
            # Installer comme service avec votre méthode existante ou nouvelle
            service_installed = self.install_nginx_with_winsw(nginx_dir)
            
            if service_installed:
                print(Fore.GREEN + "\n✅ Nginx configuré avec succès!")
                print(Fore.CYAN + f"\n📋 Informations d'accès:")
                print(Fore.CYAN + f"   HTTPS: https://aplekol360.local:{self.NGINX_SSL_PORT}")
                print(Fore.CYAN + f"   HTTP:  http://aplekol360.local:{self.NGINX_HTTP_PORT} (redirige vers HTTPS)")
                print(Fore.CYAN + f"   IP:    https://{self.server_ip}:{self.NGINX_SSL_PORT}")
                
                # Tester la connexion SSL
                self.test_ssl_configuration()
                
            # return service_installed
            
        except Exception as e:
            print(f"❌ Erreur configuration Nginx: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


    def install_nginx_with_winsw(self, nginx_dir):
        """Installer Nginx comme service Windows avec WinSW"""
        try:
            # Télécharger WinSW si nécessaire
            winsw_url = "https://github.com/winsw/winsw/releases/download/v2.12.0/WinSW-x64.exe"
            winsw_exe = os.path.join(self.current_project,"data", "nginx-service.exe")
            
            if not os.path.exists(winsw_exe):
                print("\n [+]   Téléchargement de WinSW...")
                # Télécharger WinSW
                # (implémenter la logique de téléchargement selon votre méthode existante)
            
            # Créer le fichier de configuration WinSW
            winsw_config = f'''
                    <service>
                    <id>NginxAplekol</id>
                    <name>Nginx Aplekol</name>
                    <description>Service Nginx pour Aplekol</description>
                    <executable>{os.path.join(nginx_dir, 'nginx.exe')}</executable>
                    <logpath>{os.path.join(nginx_dir, 'logs')}</logpath>
                    <logmode>roll</logmode>
                    <depend></depend>
                    <startargument>-p</startargument>
                    <startargument>{nginx_dir}</startargument>
                    <stopargument>-p</startargument>
                    <stopargument>{nginx_dir}</stopargument>
                    <stopargument>-s</stopargument>
                    <stopargument>stop</stopargument>
                    </service>
                '''
            
            winsw_config_path = os.path.join(nginx_dir, "nginx-service.xml")
            with open(winsw_config_path, 'w') as file:
                file.write(winsw_config)
            
            # Installer le service
            print("\n [+]   Installation du service Nginx...")
            subprocess.run([winsw_exe, "install"], check=True, cwd=nginx_dir)
            
            # Démarrer le service
            subprocess.run([winsw_exe, "start"], check=True, cwd=nginx_dir)
            
            print(Fore.GREEN + " [ok]   Service Nginx installé et démarré!")
            
        except Exception as e:
            print(f" [x]   Erreur lors de l'installation avec WinSW: {e}")
            # Fallback: démarrer Nginx directement
            print("\n [+]   Démarrage direct de Nginx...")
            nginx_exe = os.path.join(nginx_dir, 'nginx.exe')
            subprocess.Popen([nginx_exe], cwd=nginx_dir)

    def create_startup_script(self):
        """Créer un script pour démarrer Nginx au démarrage"""
        startup_script = f'''
        @echo off
        cd /d "{os.path.join(self.current_project, 'nginx')}"
        start /B nginx.exe
        echo Nginx démarré le %date% %time% >> nginx_startup.log
        '''
        
        script_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup',
            'start_nginx.bat'
        )
        
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        print(f"✅ Script de démarrage créé: {script_path}")

    def set_full_permissions(self, path):
        """Définir les permissions complètes sur un répertoire/fichier"""
        try:
            import win32security
            import ntsecuritycon as con
            
            # Donner à Everyone le contrôle total
            cmd = f'icacls "{path}" /grant Everyone:(OI)(CI)F /t'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            print(Fore.GREEN + f" [ok] Permissions définies pour: {path}")
            return True
            
        except Exception as e:
            print(Fore.YELLOW + f" [warn] Impossible de définir les permissions: {e}")
            
            # Fallback: utiliser takeown
            try:
                subprocess.run(f'takeown /f "{path}" /r /d y', shell=True, check=True)
                subprocess.run(f'icacls "{path}" /grant Everyone:F /t', shell=True, check=True)
                print(Fore.GREEN + f" [ok] Permissions définies avec takeown")
                return True
            except Exception as e2:
                print(Fore.RED + f" [x] Échec des permissions: {e2}")
                return False


    def configure_env(self):
        env_path = os.path.join(self.current_project,'data',".env")
        try:            
            self.set_full_permissions(env_path)
        except subprocess.CalledProcessError as e:
            # pass
            print(f"\n [x]   Erreur lors de la mise à jour des permissions : {e}")
# ========================================================================================
        try:
            # path_certs = os.path.join(self.extract_dir, 'certs')
            # installer = MySQLInstaller()
            # installer.create_my_ini()
            # installer.install_mysql_as_service()
            # installer.start_mysql_service()
            if not self.is_installed_a("mysql") or not self.is_installed("mysql",os.path.join(self.current_project,"mysql-8.0.41-winx64","bin")):               
                installer = MySQLInstaller()
                installer.install_and_config() 
                self.manage_active.delete_direct_migration()

                self.password = installer.return_data()[0]
                self.db_name = installer.return_data()[1] 
                path_certs = os.path.join(self.extract_dir, 'certs')

                if not self.set_permissions(env_path):
                    return
                # direct_ = input("Voulez vous installer Php et Apache ?")
                # response = input(f"❓ Voulez-vous installer PHP et APACHE? (oui/non): ")

                # if response.lower() not in ['oui', 'o', 'yes', 'y','n','non']:
                #     response = input(f"❓ Voulez-vous installer PHP et APACHE? (oui/non): ")

                # if response.lower() not in ['oui', 'o', 'yes', 'y']:
                #     Manage_active().delete_manage_active()
                #     Ip_manager().delete_server_ip()
                #     delete_key()
                #     self.manage_active.save_direct_migration(True) 

                ip_address = self.get_server_ip_()
                self.ip_manager.save_server_ip(ip_address)

                if not bool(self.manage_active.get_direct_migration()):
                    with open(env_path, "r") as file:
                        content = file.read()  # Lire tout le contenu

                    content = content.replace("DB_DATABASE=", f"DB_DATABASE={self.db_name} #")
                    content = content.replace("DB_PASSWORD=", f"DB_PASSWORD='{self.password}' #")
                    content = content.replace("DB_USERNAME=", f"DB_USERNAME='root' #")

                    content = content.replace("DB_SSL_CA=", f"DB_SSL_CA='{Path(os.path.join(path_certs, 'ca.pem')).as_posix()}' #")
                    content = content.replace("DB_SSL_CERT=", f"DB_SSL_CERT='{Path(os.path.join(path_certs, 'client-cert.pem')).as_posix()}'  #")
                    content = content.replace("DB_SSL_KEY=", f"DB_SSL_KEY='{Path(os.path.join(path_certs, 'client-key.pem')).as_posix()}' #")

                    # Réécriture correcte
                    with open(env_path, "w") as file:
                        file.write(content)

                # self.configure_mysql_user('127.0.0.1',self.password)
                # self.add_to_path(self.bin_dir)
                print("\n [ ok ]  Configuration .env mise à jour avec succès")

        except PermissionError:
            print("\n [x]  Échec des droits d'accès après configuration")
        except Exception as e:
            print(f"\n [x]  Erreur inattendue 1: {str(e)}") 
            import traceback
            traceback.print_exc()   

       
        if not self.is_installed_a("php") or not self.is_installed("php",os.path.join(self.install_dir,"php")) and not bool(self.manage_active.get_direct_migration()):
            php_versions = [
                # "https://windows.php.net/downloads/releases/php-8.3.25-Win32-vs16-x64.zip",
                # "https://windows.php.net/downloads/releases/archives/php-8.3.24-Win32-vs16-x64.zip",
                # "https://windows.php.net/downloads/releases/php-8.3.23-Win32-vs16-x64.zip",
                # "https://windows.php.net/downloads/releases/php-8.3.22-Win32-vs16-x64.zip",
            "https://github.com/php/php-src/releases/download/php-8.3.24/php-8.3.24-Win32-vs16-x64.zip",
            "https://github.com/php/php-src/releases/download/php-8.3.23/php-8.3.23-Win32-vs16-x64.zip",
            "https://github.com/php/php-src/releases/download/php-8.3.22/php-8.3.22-Win32-vs16-x64.zip",
            "https://github.com/php/php-src/releases/download/php-8.3.21/php-8.3.21-Win32-vs16-x64.zip",
            "https://github.com/php/php-src/releases/download/php-8.3.20/php-8.3.20-Win32-vs16-x64.zip",
            ]

            php_downloaded = False
            php_zip_path = ""
            extract_path = os.path.join(self.current_project,"php")
            self.set_full_permissions(extract_path)
            if not os.path.exists(os.path.join(self.current_project,"data","php.zip")):
                for php_url in php_versions:
                    try:
                        print(f"\n [+] Tentative de téléchargement: {php_url.split('/')[-1]}")
                        # php_zip_path = self.download_file(php_url, "php.zip")
                        php_extract_path = self.install_program(php_url, "php.zip", "")
                        if os.path.exists(php_extract_path):
                            php_downloaded = True
                            print(Fore.GREEN + f" [ok] PHP téléchargé avec succès")
                            break
                    except Exception as e:
                        print(f" [x] Échec: {e}")
                        continue
            else:
                # if installer_name.endswith(".zip"):
                
                installer_path = os.path.join(self.current_project,"data","php.zip")
                with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            # php_extract_path = self.install_program("https://windows.php.net/downloads/releases/php-8.3.24-Win32-vs16-x64.zip", "php.zip", "")            

            # self.add_to_path(os.path.join(self.current_project, "php"))

            php_ini_src = os.path.join(self.current_project, "php", "php.ini-production")
            php_ini_dest = os.path.join(self.current_project, "php", "php.ini")

            if os.path.exists(php_ini_src) and not os.path.exists(php_ini_dest):
                shutil.copy(php_ini_src, php_ini_dest)
                print("php.ini-production copié en php.ini")
            else:
                print("php.ini-production introuvable !")

            php_ini_path = os.path.join(self.current_project, "php", "php.ini")
            ext_php_path = os.path.join(self.current_project, "php","ext")

            with open(php_ini_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            with open(php_ini_path, "w", encoding="utf-8") as file:
                for line in lines:
                    # Décommenter les extensions nécessaires
                    if line.strip() == ";extension=pdo_mysql":
                        file.write("extension=pdo_mysql\n")
                    elif line.strip() == ";extension=pdo_sqlite":
                        file.write("extension=pdo_sqlite\n")
                    elif line.strip() == ";extension=openssl":
                        file.write("extension=openssl\n")
                    elif line.strip() == ";extension=fileinfo":
                        file.write("extension=fileinfo\n")
                    elif line.strip() == ";extension=gd":
                        file.write("extension=gd\n")
                    elif line.strip() == "mysqli.default_port = 3306":
                        file.write("mysqli.default_port = 3307\n")
                    elif line.startswith("; On windows:\n"):
                        file.write(f'extension_dir ="{ext_php_path}" \n') 
                    elif line.startswith("; https://php.net/cgi.fix-pathinfo"):
                        file.write("; https://php.net/cgi.fix-pathinfo \ncgi.fix_pathinfo=1\n")
                    else:
                        file.write(line)


        if not self.is_installed("nginx",os.path.join(self.install_dir,"nginx")) or not os.path.exists(os.path.join(self.install_dir,"nginx","html","api")) and not bool(self.manage_active.get_direct_migration()):
            Manage_active().delete_manage_active()
            Ip_manager().delete_server_ip()
            delete_key()
            
            # Télécharger Nginx
            if os.path.exists(os.path.join(self.current_project,"data", "nginx-1.26.3")):
                nginx_path = os.path.join(self.current_project,"data", "nginx-1.26.3")
            else:
            #  not os.path.exists(os.path.join(self.current_project, "nginx")):
                nginx_url = "https://nginx.org/download/nginx-1.24.0.zip"
                nginx_extract_path = self.install_program(nginx_url, "nginx.zip", "")
                
                nginx_path = os.path.join(nginx_extract_path, "nginx-1.24.0")
                
            

            nginx_final_path = os.path.join(self.current_project, "nginx")
            
            # Déplacer Nginx à l'emplacement final
            if os.path.exists(nginx_final_path):
                shutil.rmtree(nginx_final_path)
            shutil.move(nginx_path, nginx_final_path)
            
            # self.add_to_path(os.path.join(nginx_final_path))
            
            print("\n [+] Installation et configuration de Nginx...")
            self.server_ip = self.get_server_ip_()
            print(self.server_ip) 
            # while not self.validate_ip(self.server_ip):
            while not self.validate_ip(self.server_ip):
                print("\n [x] L'adresse IP est invalide ou ne correspond pas à cette machine.")
                self.server_ip = input("\n\t [ + ] Entrez une adresse IP valide :  ")

            self.ip_manager.save_server_ip(self.server_ip)
            self.genere_ssl_key(self.server_ip)
            # Configurer Nginx
            self.configure_nginx(ip_ser=self.server_ip)
            
            # Mettre à jour le fichier .env
            self.update_env_file(ip=self.server_ip, port=self.NGINX_SSL_PORT, env_path=env_path)
            
            print("\n [ + ]   Copie des dossiers dans le répertoire...")
            nginx_html_dir = os.path.join(nginx_final_path, 'html')
            
            # Déployer l'application
            self.process_zip_project(
                os.path.join(self.current_project,'data','api.zip'), 
                nginx_html_dir
            )
            
            # Fusionner les fichiers .env
            self.merge_env_files(
                env_path, 
                os.path.join(nginx_html_dir, 'api', '.env')
            )
            
            # Configurer le répertoire public
            # public_dir = os.path.join(nginx_html_dir, 'api', 'public')
            # if not os.path.exists(public_dir):
            #     os.makedirs(public_dir)
            
            # Déplacer les fichiers publics si nécessaire
            # api_dir = os.path.join(nginx_html_dir, 'api')
            # for item in os.listdir(api_dir):
            #     item_path = os.path.join(api_dir, item)
            #     if item != 'public' and os.path.isfile(item_path):
            #         shutil.move(item_path, os.path.join(public_dir, item))
            
            # Installer le service Nginx
            self.configure_nginx_service()
            
            print("\n Installation Nginx terminée !")

 
        # if not self.is_installed("httpd") and not bool(self.manage_active.get_direct_migration()):
        #     Manage_active().delete_manage_active()
        #     Ip_manager().delete_server_ip()
        #     delete_key()
        #     apache_extract_path = self.install_program("https://www.apachelounge.com/download/VS17/binaries/httpd-2.4.63-250207-win64-VS17.zip", "apache.zip", "")

        #     apache_bin_path = os.path.join(apache_extract_path, "Apache24")
        #     self.add_to_path(os.path.join(apache_bin_path, "bin"))
            
        #     print("\n [+] Installation et configuration d'Apache en tant que service...")
        #     self.server_ip = self.get_server_ip_()# input("\n\t [ + ] Entrez l'adresse IP du serveur : ")
            
        #     while not self.validate_ip(self.server_ip):
        #         print("\n [x] L'adresse IP est invalide ou ne correspond pas à cette machine.")
        #         self.server_ip = input("\n\t [ + ] Entrez une adresse IP valide :  ")

        #     self.ip_manager.save_server_ip(self.server_ip)
            
        #     # if self.password:
        #     #     self.configure_mysql_user('127.0.0.1', password=self.password)

            # _conf_path = os.path.join(self.current_project, "certspath")
            # subprocess.run([
            #     'openssl', 'req', '-x509', '-nodes', '-days', '3650',
            #     '-newkey', 'rsa:2048',
            #     '-keyout', Path(_conf_path, 'server.key').as_posix(),
            #     '-out', Path(_conf_path, 'server.crt').as_posix(),
            #     '-subj', f'/CN=aplekol360.local',
            #     '-addext', f'subjectAltName=DNS:aplekol360.local,IP:{self.server_ip}'
            # ], check=True)

        #     self.configure_apache(ip_ser=self.server_ip)

        #     self.update_env_file(ip=self.server_ip, port=port, env_path=env_path)
            
        #     print("\n [ + ]   Copie des dossiers dans le repertoire ...")
        #     current_directory = os.getcwd()
        #     apache_directory = os.path.join(current_directory, 'Apache24')
        #     php_directory_public = os.path.join(current_directory, 'Apache24','htdocs','api','public')
        #     # os.path.join(current_directory, 'api.zip')
        #     self.process_zip_project(self.get_resource_path(os.path.join('data','api.zip')), os.path.join(apache_directory,'htdocs'))

        #     # shutil.copy2(env_path, os.path.join(apache_directory, 'htdocs', 'api', '.env'))
        #     self.merge_env_files(env_path, os.path.join(apache_directory, 'htdocs', 'api', '.env'))
        #     # self.merge_or_add_project(os.path.join(current_directory, 'api'), os.path.join(apache_directory,'htdocs'))
        #     apache_directory_extra = os.path.join(self.current_project, 'Apache24','conf','extra','httpd-vhosts.conf')


        #     os.path.join(apache_directory, 'htdocs', 'api', '.env')
        #     with open(apache_directory_extra, 'r') as file:
        #         lines = file.readlines()

        #     # Rechercher et modifier la ligne Define SRVROOT dans le fichier
        #     with open(apache_directory_extra, 'w') as file:
        #         for line in lines:
        #             if line.startswith('# VirtualHost example:'):
        #                 file.write(f'<VirtualHost *:{self.APACHE_PORT}>\nDocumentRoot "{php_directory_public}"\nServerName aplekol360.local\n<Directory "{php_directory_public}">\nAllowOverride All\nRequire all granted\n</Directory>\n</VirtualHost>\n')  
                   
        #             else:
        #                 pass
        #                 # file.write(line)




            print("\n Installation terminée !")

    def merge_env_files(self,source_env, dest_env):
        """
        Fusionne le fichier source .env avec le fichier destination.
        - Remplace les anciennes valeurs par celles du source
        - Ajoute les nouvelles variables sans supprimer les anciennes
        """
        source_data = {}
        dest_data = {}

        # Charger le fichier source
        if os.path.exists(source_env):
            with open(source_env, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        source_data[key.strip()] = value.strip()

        # Charger le fichier destination s'il existe
        if os.path.exists(dest_env):
            with open(dest_env, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        dest_data[key.strip()] = value.strip()

        # Mettre à jour les valeurs du fichier destination avec celles du source
        dest_data.update(source_data)

        # Réécrire le fichier destination avec les valeurs fusionnées
        with open(dest_env, "w", encoding="utf-8") as f:
            for key, value in dest_data.items():
                f.write(f"{key}={value}\n\n")

        print(f"✅ Fusion du fichier .env terminée : {dest_env}")


    def configure_mysql_user(self, ip_ser, password):
        # Extraire la plage d'IP
        ip_parts = ip_ser.split(".")
        ip_range = '127.0.0.1' #".".join(ip_parts[:3]) + ".%"
        _password = '@@@@@@'
        # Chemin vers mysql.exe
        mysql_path = os.path.join(self.bin_dir, "mysql.exe")
        
        path_certs = os.path.join(self.extract_dir, 'certs')
        
        try:

            subprocess.run([
                mysql_path, '-u', 'root', f'-p{_password}', '-P', '3307', '-h', 'localhost',
                f"--ssl-ca={Path(path_certs,'ca.pem').as_posix()}",
                    f"--ssl-cert={Path(path_certs,'client-cert.pem').as_posix()}",
                    f"--ssl-key={Path(path_certs,'client-key.pem').as_posix()}",
                '-e', (
                    f"CREATE USER IF NOT EXISTS 'root'@'{ip_range}' IDENTIFIED WITH caching_sha2_password BY '{password}'; "
                    f"ALTER USER 'root'@'{ip_range}' IDENTIFIED BY '{password}'; "
                    f"GRANT ALL PRIVILEGES ON *.* TO 'root'@'{ip_range}' WITH GRANT OPTION;"
                    "FLUSH PRIVILEGES;"
                
                )
                # f"CREATE USER IF NOT EXISTS 'root'@'{ip_range}' IDENTIFIED WITH caching_sha2_password BY '{password}';"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
# stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
# "FLUSH PRIVILEGES;"
            # Accorder tous les privilèges à l'utilisateur sur toutes les bases de données
            # subprocess.run([
            #     mysql_path, '-u', 'root', f'-p{_password}', '-P', '3307', '-h', 'localhost',    
            #    f"--ssl-ca={Path(path_certs,'ca.pem').as_posix()}",
            #         f"--ssl-cert={Path(path_certs,'client-cert.pem').as_posix()}",
            #         f"--ssl-key={Path(path_certs,'client-key.pem').as_posix()}",
            #     '-e', f"GRANT ALL PRIVILEGES ON *.* TO 'root'@'{ip_range}' WITH GRANT OPTION;"
            # ], check=True)
            
            # # Appliquer les changements
            # subprocess.run([
            #     mysql_path, '-u', 'root', f'-p{_password}', '-P', '3307', '-h', 'localhost',    
            #  f"--ssl-ca={Path(path_certs,'ca.pem').as_posix()}",
            #         f"--ssl-cert={Path(path_certs,'client-cert.pem').as_posix()}",
            #         f"--ssl-key={Path(path_certs,'client-key.pem').as_posix()}",
            #     '-e', "FLUSH PRIVILEGES;"
            # ], check=True)
            
            # print("Utilisateur MySQL configuré avec succès.")
            
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande MySQL : {e}")
        except Exception as e:
            print(f"Erreur inattendue in l'exécution de la commande MySQL: {str(e)}")
            import traceback
            traceback.print_exc()


    def extract_zip(self, zip_path, extract_to):
        """Décompresse un fichier ZIP vers un dossier donné."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"ZIP extrait vers: {extract_to}")
        except Exception as e:
            print(f"Erreur lors de la décompression du ZIP: {e}")

    def merge_directories_(self,source, destination):
        """Fusionne les fichiers du dossier source vers le dossier destination."""
        try:
            for item in os.listdir(source):
                source_item = os.path.join(source, item)
                dest_item = os.path.join(destination, item)

                if os.path.isdir(source_item):
                    if not os.path.exists(dest_item):
                        os.makedirs(dest_item)
                        print(f"Création du dossier: {dest_item}")
                    self.merge_directories_(source_item, dest_item)
                else:
                    if not os.path.exists(dest_item):
                        shutil.copy2(source_item, dest_item)
                        print(f"Fichier copié: {dest_item}")
                    else:
                        print(f"Le fichier existe déjà: {dest_item}")
        except Exception as e:
            print(f"Erreur lors de la fusion: {e}")

    def process_zip_project(self,zip_file, dest_dir):
        """
        Gère l'ajout ou la fusion d'un projet ZIP dans la destination.
        - Copie le ZIP dans la destination.
        - Décompresse le fichier ZIP.
        - Fusionne ou ajoute le projet.
        - Supprime le ZIP et le dossier temporaire.

        :param zip_file: Chemin du fichier ZIP
        :param dest_dir: Répertoire où fusionner ou ajouter le projet
        """
        try:
            # Vérifier si le fichier ZIP existe
            if not os.path.exists(zip_file):
                print(f"Fichier ZIP non trouvé: {zip_file}")
                return

            # Copier le ZIP dans le dossier de destination
            zip_basename = os.path.basename(zip_file)
            #dest_zip_path = dest_dir #os.path.join(dest_dir, zip_basename)
            dest_zip_path = os.path.join(dest_dir, zip_basename)
            shutil.copy2(zip_file, dest_zip_path)
            print(f"ZIP copié vers: {dest_zip_path}")

            # Définir le dossier temporaire pour l'extraction
            temp_extract_dir = os.path.join(dest_dir, "temp_extracted")

            # Supprimer tout ancien dossier temporaire avant d'extraire
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)

            # Extraire le ZIP
            self.extract_zip(dest_zip_path, temp_extract_dir)

            # Récupérer le nom du projet (nom du dossier extrait)
            extracted_dirs = os.listdir(temp_extract_dir)
            if not extracted_dirs:
                print("Le fichier ZIP est vide !")
                return

            project_name = extracted_dirs[0]  # Supposons qu'un seul projet soit extrait
            
            extracted_project_path = os.path.join(temp_extract_dir, project_name)
            destination_project_path = os.path.join(dest_dir, project_name)
            print(f"project_name    {project_name}")
            print(f"extracted_project_path    {extracted_project_path}")
            print(f"destination_project_path    {destination_project_path}")

            # Vérifier si le projet existe déjà
            if os.path.exists(destination_project_path):
                print(f"Fusion du projet existant: {destination_project_path}")
                self.merge_directories(extracted_project_path, destination_project_path)
            else:
                shutil.move(extracted_project_path, destination_project_path)
                print(f"Projet ajouté dans: {destination_project_path}")

            # Nettoyer : supprimer le fichier ZIP et le dossier temporaire
            os.remove(dest_zip_path)
            shutil.rmtree(temp_extract_dir)

            print("Opération terminée avec succès ✅")

        except Exception as e:
            print(f"Erreur: {e}")


    def compress_directory(self,source_dir, zip_path):
        """
        Compresse un répertoire en un fichier zip.
        :param source_dir: Le répertoire source à compresser
        :param zip_path: Le chemin du fichier zip à créer
        """
        try:
            shutil.make_archive(zip_path, 'zip', source_dir)
            print(f"Compression réussie: {zip_path}.zip")
        except Exception as e:
            print(f"Erreur lors de la compression: {e}")

    def decompress_zip(self,zip_path, extract_to):
        """
        Décompresse un fichier zip dans un répertoire donné.
        :param zip_path: Le chemin du fichier zip
        :param extract_to: Le répertoire où extraire les fichiers
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"Décompression réussie: {extract_to}")
        except Exception as e:
            print(f"Erreur lors de la décompression: {e}")

    def merge_or_add_project(self, source_dir, dest_dir):
        """
        Fusionne ou ajoute un projet compressé dans le répertoire de destination.
        :param source_dir: Le répertoire source du projet
        :param dest_dir: Le répertoire de destination (htdocs d'Apache)
        """
        try:
            if not os.path.exists(source_dir):
                print(f"Le répertoire source n'existe pas: {source_dir}")
                return

            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                print(f"Création du répertoire destination: {dest_dir}")

            project_name = os.path.basename(source_dir)
            zip_file_path = os.path.join(dest_dir, project_name)

            # Compression avant la copie
            self.compress_directory(source_dir, zip_file_path)

            # Vérification et fusion si nécessaire
            if os.path.exists(os.path.join(dest_dir, project_name)):
                print(f"Le projet existe déjà dans le dossier de destination: {dest_dir}")
                decompressed_path = os.path.join(dest_dir, f"{project_name}_temp")
                self.decompress_zip(f"{zip_file_path}.zip", decompressed_path)
                self.merge_directories(decompressed_path, os.path.join(dest_dir, project_name))
                shutil.rmtree(decompressed_path)  # Nettoyage du dossier temporaire
            else:
                self.decompress_zip(f"{zip_file_path}.zip", dest_dir)
                print(f"Le projet a été ajouté à {dest_dir}")

        except Exception as e:
            print(f"Une erreur est survenue: {e}")

    def merge_directories(self, source, destination):
        """
        Fusionne deux répertoires en ajoutant les fichiers manquants.
        :param source: Le répertoire source
        :param destination: Le répertoire de destination
        """
        try:
            for item in os.listdir(source):
                source_item = os.path.join(source, item)
                dest_item = os.path.join(destination, item)

                if os.path.isdir(source_item):
                    if not os.path.exists(dest_item):
                        os.makedirs(dest_item)
                    self.merge_directories(source_item, dest_item)
                else:
                    if not os.path.exists(dest_item):
                        shutil.copy2(source_item, dest_item)
                    else:
                        print(f"Fichier existant non écrasé: {dest_item}")

        except Exception as e:
            print(f"Erreur lors de la fusion: {e}")


    def ensure_services_running(self, services, force=False):
        for service in services:
            # Vérifier le statut du service
            # Si le service est arrêté, on le démarre
            if force and service.startswith("NginxApl"):
                subprocess.run(["net", "stop", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["net", "start", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            if service.startswith("NginxApl"):
                subprocess.run(["net", "stop", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                

            result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
            
            
            if "STOPPED" in result.stdout:
                print(f"\n [+] Démarrage du service {service}...")
                subprocess.run(["net", "start", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif "RUNNING" in result.stdout:
                print(f"\n [ok]  Le service {service} est déjà en cours d'exécution.")
            else:
                print(f"[x] Impossible de déterminer l'état de {service}. Vérifie son nom.")
                print(result.stdout)

 

    def get_server_ip_(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname) 
        print(hostname,ip_address,self.get_local_ip())
        try:
            if not self.get_local_ip().startswith('127.'):
                if self.get_local_ip().startswith('192.'):
                    return self.get_local_ip()
                elif self.get_local_ip().startswith('10.1'):
                    return self.get_local_ip()
                elif ip_address.startswith('10.'):
                    return ip_address
                else:
                    return ip_address
            else:
                return ip_address
        except Exception as e:
            print(f"Erreur lors de la récupération de l'adresse IP in main: {e}")
            import traceback
            traceback.print_exc()
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # pas besoin que ça marche vraiment
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
        
    def is_ip_reachable(self, ip):
        """Teste si une adresse IP répond au ping."""
        try:
            # Commande ping pour Windows (-n 1) ou Linux/Mac (-c 1)
            param = "-n" if sys.platform == "win32" else "-c"
            result = subprocess.run(["ping", param, "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return result.returncode == 0  # 0 = succès, sinon échec
        except Exception:
            return False

    def install_and_config(self):        
        services_a_verifier = ["MySQLEcole", "NginxAplekol"]
        self.configure_env()
        active = Manage_active().get_manage_active()
        # self.genere_ssl_key(self.get_server_ip_(), True)
        self.app = QApplication(sys.argv)
        if active == 'true':     
            # self.ajouter_au_demarrage("école-server")       
            print("\n [+]   Demarrage du server ...!!!--")

            services_a_verifier = ["MySQLEcole", "NginxAplekol"]
            self.ensure_services_running(services_a_verifier)
            
            try:
                time.sleep(5) 
                ip_address = self.get_server_ip_()
                
                mysql_path = os.path.join('data', "mysql_path.sql")
                if os.path.exists(mysql_path):
                    self.main_migration_sql()
                

                # if ip_address != self.ip_manager.get_server_ip():

                self.ip_manager.save_server_ip(ip_address)
                # from .direct_request import load_data

                # direct_request = load_data().get('value',0) if load_data() else None

                # if not direct_request:
                #     try: 
                #         env_path_ = r"C:\Program Files\ecole-serve\Apache24\htdocs\api\.env"

                #         with open(env_path_, "r") as file:
                #             content = file.read()

                #         # Appliquer les modifications sur la base du contenu d'origine
                #         new_content = content
                #         new_content = new_content.replace("APP_URL=https://", f"APP_URL=https://aplekol360.local #")
                #         new_content = new_content.replace("SANCTUM_STATEFUL_DOMAINS=", f"SANCTUM_STATEFUL_DOMAINS=aplekol360.local #")
                #         new_content = new_content.replace("SESSION_DOMAIN=", f"SESSION_DOMAIN=aplekol360.local #")                       

                #         # Écriture des modifications dans le fichier
                #         with open(env_path_, "w") as file:
                #             file.write(new_content)


                #         self.genere_ssl_key(ip_address, update_client=True)
                #     except Exception as e:
                #         print('An exceptiuuuuuuuuuuuuuuuuuuuuon occurred') 
                #         print(f"------ : {e}")
                #         import traceback
                #         traceback.print_exc()
                        
                        # self.genere_ssl_key(ip_address, update_client=False)
                # self.ip_manager.save_server_ip(ip_address)
                print(f"--------ip_address--------{ip_address}")
                if ip_address:
                    base_url = f"https://aplekol360.local/api/"

                elif self.get_server_ip_():
                    ip_address = self.get_server_ip_()
                    base_url = f"https://aplekol360.local/api/"

                else:
                    ip_address = input("Nous ne pouvons pas détecter l'adresse IP automatiquement. Veuillez entrer l'IP du serveur: ")
                 
 
                if not self.is_ip_reachable(ip_address):
                    QMessageBox.critical(None, "Network Error", "We can't find your network, please reconnect or restart the router!.")
                    return 
                
                from .direct_request import first_check, load_data,get_authorisation
                direct_request = load_data().get('value',0) if load_data() else None
                client_data_ = None
                status_code = None

                if direct_request:
                    response, status = first_check()
                    status_code = status
                    
                else:
                    url = f"{base_url}first-check"
                    print(f"url  {url}")
                    
                    response = requests.get(url, verify="C:/Program Files/ecole-serve/certspath/ca.pem")
                    status_code = response.status_code
                print(response.json(), status_code)   
                if status_code == 200: 
                    urls = f"{base_url}client-authorisation-connect"
                    print(f"urls  {urls}")
                    headers = {'Content-Type': 'application/json',
                                'Accept': 'application/json'
                                }
                    try:
                        response_status_code =  None
                        if direct_request:
                            response_data, status = get_authorisation()
                            response_status_code=status
                        else:
                            data = requests.get(urls, headers=headers,verify="C:/Program Files/ecole-serve/certspath/ca.pem")
                            response_data = data.json()
                            response_status_code=data.status_code
                   
                        if response_status_code == 200:                           
                            client_data_ = response_data['data_client']
                    except Exception as e:
                        print(f'An exception occurred 1 {e}')


                    try:
                        # app = QApplication(sys.argv)
                        if not is_license_valid(url=base_url):
                            QMessageBox.critical(None, "Licence expirée", "Votre licence a expiré ou est invalide.\nContactez l'administrateur.")
                        # exit(1)  # Stoppe l'application si la clé n'est pas valide 
                        window = ServiceControlWindow(base__url=base_url)
                        self.app.setQuitOnLastWindowClosed(False) 
                        window.init_ui(services=services_a_verifier,url=urls, client_data=client_data_,base_url=base_url)
                        # window.show()
                        window.hide()
                        sys.exit(self.app.exec())
                    except Exception as e: 
                        print(f"------ : {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    self.start_and_save_user()
                    print("\n [+]   Creer un compte administrateur!")
                    self.insert_user()
            except subprocess.CalledProcessError as e:
                print(f"error in starting   {e}")
                import traceback
                traceback.print_exc()
            except Exception as e:
                print('An exceptiuuuuuuuuuhhhhhhhhhhhhhhhuuuuuuuuuuuon occurred') 
                print(f"------ : {e}")
                import traceback
                traceback.print_exc()
            return
        

        # activation_key = ask_for_activation_key
        license = LicenseManager()
        val_bool, message, date = license.check_license() 
        if not date:
            show_activation_key()
        

        if val_bool== False and message == "Licence expirée":
            QMessageBox.critical(None, "Licence expirée", "Votre licence a expiré ou est invalide.\nOk pour continuer.")
            print("\n [+]   Connexion et demarage du server!  Licence ---")
            self.start_and_save_user()
            print("\n [+]   Creer un compte administrateur! 1")
            self.insert_user()

        if val_bool== True and message == "Licence valide":
            print("\n [+]   Connexion et demarage du server! Licence +++")
            self.start_and_save_user()
            print("\n [+]   Creer un compte administrateur! 2")
            self.insert_user()

        elif ask_for_activation_key():
            print("\n [+]   Connexion et demarage du server! in ask_for_activation_key")
            self.start_and_save_user()
            print("\n [+]   Creer un compte administrateur! 3")
            self.insert_user()

            self.ajouter_au_demarrage("école-server")

    def ajouter_au_demarrage(self, nom_app: str = "école-server"):
        """Ajoute l'application au démarrage de Windows avec des vérifications de sécurité."""
        
        try:
            # 1. Vérifier les droits admin
            if not ctypes.windll.shell32.IsUserAnAdmin():
                raise PermissionError("Les droits administrateur sont requis pour cette opération.")
            
            # 2. Déterminer le chemin du dossier Startup
            startup_dir = Path(os.path.join(
                os.environ["APPDATA"], 
                "Microsoft\\Windows\\Start Menu\\Programs\\Startup"
            ))
            
            # 3. Vérifier si le raccourci existe déjà
            raccourci_path = startup_dir / f"{nom_app}.bat"
            if raccourci_path.exists():
                print(f"⚠️ Un raccourci existe déjà dans le démarrage: {raccourci_path}")
                return False
            
            # 4. Déterminer le chemin de l'exécutable
            if getattr(sys, 'frozen', False):
                chemin_executable = Path(sys.executable)
            else:
                chemin_executable = Path(sys.argv[0]).absolute()
            
            # 5. Vérifier que l'exécutable existe
            if not chemin_executable.exists():
                raise FileNotFoundError(f"Fichier exécutable introuvable: {chemin_executable}")
            
            # 6. Créer le fichier batch
            contenu_batch = f'@echo off\nstart "" "{chemin_executable}"'
            
            with open(raccourci_path, "w", encoding='utf-8') as f:
                f.write(contenu_batch)
            
            # 7. Vérifier que le fichier a bien été créé
            if not raccourci_path.exists():
                raise RuntimeError("Échec de la création du fichier de démarrage.")
            
            print(f"✅ Ajouté au démarrage: {raccourci_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'ajout au démarrage: {str(e)}")
            return False

    def set_permissions(self,env_path):
        try:            
            take_own_cmd = f'takeown /F "{env_path}"'
            subprocess.run(take_own_cmd, shell=True, check=True, capture_output=True, text=True)

            # Définir les permissions complètes
            username = os.getenv('USERNAME')
            print(username)
            icacls_cmd = (
                f'icacls "{env_path}" /grant:r "{username}":(F) '
                f'/inheritance:r /T /C /Q'
            )
            subprocess.run(icacls_cmd, shell=True, check=True, capture_output=True, text=True)
            
            # Attendre que les permissions soient appliquées
            time.sleep(4)
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erreur de permission : {e.stderr}")
            return False

    def update_env_file(self,ip, port, env_path):
        # env_path = r"C:\Users\Saddam\Desktop\school_server\api\.env"
        
        if not os.path.exists(env_path):
            print("\n [x]   Fichier .env introuvable")
            return

        # Vérifier les privilèges administrateur
        # try:
        #     subprocess.run(['net', 'session'], check=True, shell=True)
        # except subprocess.CalledProcessError:
        #     print("\n [+]   Veuillez exécuter en tant qu'administrateur")
        #     return

        # Tentative de modification
        try:

            if not self.set_permissions(env_path):
                return
            
            with open(env_path, "r") as file:
                content = file.read()  # Lire tout le contenu

            # Appliquer les modifications
            content = content.replace("APP_URL=https://", f"APP_URL=https://aplekol360.local #")
            content = content.replace("DB_HOST=", f"DB_HOST=127.0.0.1 #")

            content = content.replace("SANCTUM_STATEFUL_DOMAINS=", f"SANCTUM_STATEFUL_DOMAINS=aplekol360.local #")
            content = content.replace("SESSION_DOMAIN=", f"SESSION_DOMAIN=aplekol360.local #")

            # Réécriture correcte
            with open(env_path, "w") as file:
                file.write(content)

            print(Fore.GREEN + "\n [ ok ]   Configuration .env mise à jour avec succès")

            is_install = MySQLSetup()
            is_install.run(ip_ser=ip)

        except PermissionError:
            print("\n [x]   Échec des droits d'accès après configuration")
        except Exception as e:
            print(f"\n [x]   Erreur inattendue : {str(e)}")
    
    
    def main_migration_sql(self):
        import argparse
        from Helper.db import Database 
        db = Database()
        connection = db.get_connection()
        
        mysql_path = os.path.join('data', "mysql_path.sql")
        # export_laravel_clean = self.get_resource_path(os.path.join('data', "export_laravel_clean.sql"))
        if not os.path.exists(mysql_path): 
        # if not os.path.exists(args.sql_file): 
            print(f"❌ Fichier SQL non trouvé: {mysql_path}")
            return
        
        # Initialiser le migrateur
        migrator = SQLFileMigrator(
            connection=connection
        )
        
        if not migrator.connect():
            return
        
        try:
            # migrator.clean_sql_file(mysql_path, export_laravel_clean)
            migrator.execute_sql_data(mysql_path)
        
      
            if os.path.exists(mysql_path):
                print(f"path removed {mysql_path}")
                # os.remove(mysql_path)
                # os.remove(export_laravel_clean)
        except Exception as e:
            migrator.log("ERROR", f"Erreur générale: {e}")
        # finally:
        #     connection.close()

    def start_and_save_user(self):
        print("\n [+]   Migration de la base de donnees ---")
        # services_a_verifier = ["MySQLEcole", "NginxAplekol"]
        # self.ensure_services_running(services_a_verifier, force=True)
        # subprocess.Popen([os.path.join(self.bin_dir, 'mysqld.exe'), f"--defaults-file={self.my_ini_path}"])
        if bool(self.manage_active.get_direct_migration()):
            self.main_migration_sql()
            try:
                mysql_path = os.path.join(self.bin_dir, "mysql.exe")
                pass_word = '@#Lekol3&0'
                
                path_certs = os.path.join(self.extract_dir, 'certs')

                ssl_ca = os.path.join(self.extract_dir, 'certs','ca.pem')
                ssl_cert = os.path.join(self.extract_dir, 'certs','client-cert.pem')
                ssl_key = os.path.join(self.extract_dir, 'certs','client-key.pem')
                print(ssl_ca)
                create_user_ssl = [
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                    f'--ssl-ca={ssl_ca}',
                    f'--ssl-cert={ssl_cert}',
                    f'--ssl-key={ssl_key}',
                    '-e',
                    f"""
                    CREATE USER 'ssl_reader'@'%' IDENTIFIED BY '@#ssl_reader21'; 
                    GRANT SELECT ON lekol360.client_infos TO 'ssl_reader'@'%';
                    GRANT SELECT ON lekol360.direct_configs TO 'ssl_reader'@'%'; 
                    GRANT INSERT ON lekol360.client_infos TO 'ssl_reader'@'%'; 
                    GRANT UPDATE ON lekol360.client_infos TO 'ssl_reader'@'%'; 
                    FLUSH PRIVILEGES;
                    """
                ]
                subprocess.run(create_user_ssl)

                #   CREATE USER 'ssl_reader'@'%' IDENTIFIED BY '@#ssl_reader21'; 
                #     GRANT SELECT ON lemignon.client_infos TO 'ssl_reader'@'%';
                #     GRANT SELECT ON lemignon.direct_configs TO 'ssl_reader'@'%'; 
                #     GRANT INSERT ON lemignon.client_infos TO 'ssl_reader'@'%'; 
                #     GRANT UPDATE ON lemignon.client_infos TO 'ssl_reader'@'%'; 
                #     FLUSH PRIVILEGES;

            except Exception as e:
               import traceback
               traceback.print_exc()
               print(f'An exception occurred 2 {e}')
        
            
            from .direct_request import insert_load_data,fill_roles_and_permission
            insert_load_data()
            fill_roles_and_permission()
        else:
            try:
                services_a_verifier = ["MySQLEcole", "NginxAplekol"]
                self.ensure_services_running(services_a_verifier)
            except Exception as e:
                print(e)
            try: 

                php_path = os.path.join(self.install_dir, "php", "php.exe")  # adapte ce chemin si besoin
                # cwd = self.get_resource_path(os.path.join('Apache24', 'htdocs', 'api'))

                # subprocess.run([php_path, "artisan", "migrate", "--force"], check=True, cwd=cwd)
                cwd=os.path.join(self.install_dir, 'nginx','html','api')
                command_migrate = (
                        'cd "C:\\Program Files\\ecole-serve\\nginx\\html\\api" && '
                        '"C:\\Program Files\\ecole-serve\\php\\php.exe" artisan migrate --force'
                    )
                command_key = (
                        'cd "C:\\Program Files\\ecole-serve\\nginx\\html\\api" && '
                        '"C:\\Program Files\\ecole-serve\\php\\php.exe" artisan key:generate --force'
                    )
                
                command_clear = (
                        'cd "C:\\Program Files\\ecole-serve\\nginx\\html\\api" && '
                        '"C:\\Program Files\\ecole-serve\\php\\php.exe" artisan config:clear'
                    )
                # time.sleep(10)
                subprocess.run(
                    command_migrate,
                # f'cd "{cwd}" && "{php_path}" php artisan migrate --force',
                shell=True,
                check=True
                ) 
                subprocess.run(
                    command_clear,
                shell=True,
                check=True
                 ) 
                
                subprocess.run(
                    command_key,
                # f'cd "{cwd}" && "{php_path}" php artisan key:generate --force',
                shell=True,
                check=True
            ) 
                # time.sleep(10)
                # subprocess.run(["php", "artisan", "key:generate", "--force"], check=True, cwd=cwd)
            except subprocess.CalledProcessError as e:
                print(f" Erreur CalledProcessError lors ... : {e}")
            except Exception as e:
                print(f" Erreur Exception lors ... : {e}")
                return

    def format_key_input(self):
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


    def validate_email(self, email):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def validate_name(self, name):
        return re.match(r'^[A-Za-zÀ-ÿ -]+$', name) is not None and 2 <= len(name) <= 50

    def ask_for_user_data(self):
        
        while True:
            name = input("\n [+] Entrez le nom : ").strip()
            if self.validate_name(name):
                break
            else:
                print("\n [x] Le nom est invalide. Il ne doit contenir que des lettres et des espaces, et être entre 2 et 50 caractères.")


        while True:
            first_name = input("\n [+] Entrez le prénom : ").strip()
            if self.validate_name(first_name):
                break
            else:
                print("\n [x] Le prénom est invalide. Il ne doit contenir que des lettres et des espaces, et être entre 2 et 50 caractères.")
        
        
        while True:
            email = input("\n [+] Entrez l'email : ").strip()
            if self.validate_email(email):
                break
            else:
                print("\n [x] L'email est invalide. Veuillez entrer un email valide.")


        password = self.masked_input("\n [+] Entrez le mot de passe : ").strip()

        return name, first_name, email, password
    
    def masked_input(self, prompt="Mot de passe : "):
        print(prompt, end="", flush=True)
        password = ""

        while True:
            char = msvcrt.getch()  # Lire un caractère sans affichage
            if char in {b'\r', b'\n'}:  # Touche Entrée
                break
            elif char == b'\b':  # Gérer le backspace
                if len(password) > 0:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)  # Efface visuellement
            else:
                password += char.decode("utf-8")
                print("*", end="", flush=True)  # Afficher `*`
        
        print()  # Nouvelle ligne après validation
        return password

    # Fonction principale
    def insert_user(self):
        if not self.is_ip_reachable(self.get_server_ip_()):
            print("We can't find your network, please reconnect or restart the router...")
            QMessageBox.critical(None, "Network Error", "We can't find your network, please reconnect or restart the router.")
            return
        ca_path = r"C:\Program Files\ecole-serve\certspath\ca.pem"
        while True:
            name, first_name, email, password = self.ask_for_user_data()

            url = f"https://aplekol360.local/api/first-account"
            
            headers = {
                "Content-Type": "application/json"
            }

            data = {
                'nom': first_name,
                'prenom': name,
                'email': email,
                'first': True,
                'password': password
            }
            client_data_ = None
            response_status_code =None
            try:
                from .direct_request import first_check, load_data,get_authorisation,store_personnel_first
                direct_request = load_data().get('value',0) if load_data() else None

                if direct_request:
                    
                    response_data, status = store_personnel_first(data)
                    response_status_code=status
                else:
                    _conf_path = os.path.join(self.current_project, "nginx", "conf")
                    response = requests.post(url, json=data, headers=headers,verify=ca_path)
                    response_status_code=response.status_code
                # client_data_ = None
                if response_status_code == 200:
                    connect_code_status =None
                    base_url=f"https://aplekol360.local/api/"

                    if direct_request:
                        # fill_roles_and_permission()
                        response_data, status = get_authorisation()
                        connect_code_status=status
                    else:
                        url = f"https://aplekol360.local/api/first-account-fill"
                        requests.get(url,verify=ca_path)
                    
                        urls = f"https://aplekol360.local/api/client-authorisation-connect"
                        headers = {'Content-Type': 'application/json',
                            'Accept': 'application/json'
                            }
                        data = requests.get(urls, headers=headers,verify=ca_path)
                        response_data = data.json()
                        connect_code_status =data.status_code
                    try:
                        if connect_code_status == 200:
                            client_data_ = response_data['data_client']
                            try:
                                _data = {
                                    'nom': first_name,
                                    'prenom': name,
                                    'email': email, 
                                    'mac': get_mac_address(), 
                                }
                                _url = 'https://www.infini-software.cloud/api/save-data'
                                response = requests.post(_url, json=_data, headers=headers,verify=Path(_conf_path, 'ca.pem').as_posix())
                            except:
                              print('An exception occurred tttt')
                              pass
                    except Exception as e:
                        print(f'An exception occurred 3 {e}')
                    try:
                        # app = QApplication(sys.argv)
                        self.app.setQuitOnLastWindowClosed(False)
                        if not is_license_valid(url=base_url):
                            QMessageBox.critical(None, "Licence expirée", "Votre licence a expiré ou est invalide.\nContactez l'administrateur.")
                        # exit(1)  # Stoppe l'application si la clé n'est pas valide
                        services_a_verifier = ["MySQLEcole", "NginxAplekol"]
                        window = ServiceControlWindow(base__url=base_url)
                        window.init_ui(services=services_a_verifier,url=urls, client_data=client_data_,base_url=base_url)#init_ui(services_a_verifier)
                        window.show()
                        sys.exit(self.app.exec())
                        continue  # Sortie de la boucle en cas de succès
                    except Exception as e: 
                        print(f"------ : {e}")
                        import traceback
                        traceback.print_exc()

                else:
                    print(f"\n [x]   Erreur {response_status_code} : {response_status_code}")

            except requests.exceptions.RequestException as e:
                print(f"\n [x]   Erreur de connexion : {e}")

            except Exception as e:
                print('An exceptiuuuuuuuuuuuuuuuuuuuuon occurred')
                print(f"------ : {e}")
                import traceback
                traceback.print_exc()

            # Demander à l'utilisateur de réessayer en cas d'échec
            print("\n [ - ]   Veuillez entrer les informations à nouveau.")

import textwrap
import urllib.request
import tempfile
class MySQLInstaller:
    def __init__(self):
        self.install_dir = os.path.join(os.getenv('PROGRAMFILES'),'ecole-serve')
        self.current_dir = self.install_dir 
        self.mysql_version = "8.0.41"
        self.mysql_url = f"https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-{self.mysql_version}-winx64.zip"
        # mysql-8.4.4-winx64.zip
        self.zip_file = f"mysql-{self.mysql_version}-winx64.zip"
        self.download_path = os.path.join(self.current_dir, self.zip_file)
        # self.openSSl_path = os.path.join(self.current_dir, self.zip_file)
 
        #self.extract_dir = os.path.join(self.current_dir, "mysql")
        self.extract_dir = os.path.join(self.current_dir, f"mysql-{self.mysql_version}-winx64")
        self.bin_dir = os.path.join(self.extract_dir, "bin")
        self.data_dir = os.path.join(self.extract_dir, "data")
        self.my_ini_path = os.path.join(self.extract_dir, "my.ini") 
        self.service_name = "MySQLEcole"
        self.file_path = os.path.join(self.extract_dir, "init.sql")
        self.ssl_dir = os.path.join(self.extract_dir, "certs")
        # self.openssl_path = self._get_openssl_path()

    def _get_openssl_path(self) -> Path:
        """Trouve le chemin d'OpenSSL avec vérification"""
        # 1. Essayer dans le PATH
        openssl = shutil.which('openssl')
        if openssl:
            return Path(openssl)
            
        # 2. Chercher dans les emplacements Windows typiques
        common_paths = [
            Path(os.environ.get('ProgramFiles', '')) / 'OpenSSL-Win64' / 'bin' / 'openssl.exe',
            Path(os.environ.get('ProgramFiles(x86)', '')) / 'OpenSSL-Win32' / 'bin' / 'openssl.exe',
            Path('C:') / 'OpenSSL-Win64' / 'bin' / 'openssl.exe'
        ]
        
        for path in common_paths:
            if path.exists():
                return path
                
        # 3. Erreur si non trouvé
        raise FileNotFoundError(
            "OpenSSL requis. Installez la version Win64 depuis:\n"
            "https://slproweb.com/products/Win32OpenSSL.html\n"
            "Et ajoutez-le au PATH système."
        )
    
    def install_openssl(self):
        """Installe OpenSSL automatiquement avec plusieurs fallbacks"""
        try:
            # 1. Vérifier si déjà installé
            if shutil.which('openssl'):
                print("✓ OpenSSL déjà installé")
                return True

            print("\n[+] Installation d'OpenSSL...")

            # 2. Essayer avec le fichier local d'abord
            installer_path = os.path.join("data", "Win64OpenSSL_Light-3_5_1.msi")
            if os.path.exists(installer_path):
                print(f"Utilisation du fichier local...{installer_path}")
                # installer_path = local_path
            else:
                # 3. Téléchargement depuis le web
                print("Téléchargement depuis le web...")
                url = "https://slproweb.com/download/Win64OpenSSL_Light-3_4_3.msi"
                temp_dir = Path(tempfile.gettempdir())
                installer_path = temp_dir / "openssl_installer.msi"

                try:
                    with requests.get(url, stream=True) as r:
                        r.raise_for_status()
                        total_size = int(r.headers.get('content-length', 0))
                        with open(installer_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                except requests.RequestException as e:
                    print(f"Échec de l'installation local: {e}")
                    return self._install_openssl_alternative()

            # 4. Installation
            print(f"Installation depuis les dossiers local...")
            result = subprocess.run(
                ["msiexec", "/i", str(installer_path), "/quiet", "/norestart"],
                check=True,
                capture_output=True,
                text=True,
                timeout=300
            )

            # 5. Vérification
            openssl_bin = Path(os.environ["ProgramFiles"]) / "OpenSSL-Win64" / "bin"
            os.environ["PATH"] = f"{openssl_bin};{os.environ['PATH']}"

            if not shutil.which('openssl'):
                raise Exception("OpenSSL toujours introuvable après installation")

            print("✓ OpenSSL installé avec succès")
            return True

        except subprocess.TimeoutExpired:
            print("Timeout lors de l'installation")
        except subprocess.CalledProcessError as e:
            print(f"Erreur d'installation: {e.stderr}")
        except Exception as e:
            print(f"Erreur inattendue: {str(e)}")
        
        return self._install_openssl_alternative()


    # Vérification initiale
    def _install_openssl_alternative(self):
        """Installe OpenSSL automatiquement avec une URL valide"""
        try:
            # Vérifier si déjà installé
            if shutil.which('openssl'):
                return True

            print("Téléchargement d'OpenSSL...")
            
            # URL valide (version légère 3.1.4)
            
            url = "https://slproweb.com/download/Win64OpenSSL_Light-3_5_2.msi"
            
            temp_dir = Path(tempfile.gettempdir())
            installer_path = temp_dir / "openssl_installer.msi"
            # path = self.get_resource_path__(os.path.join("data","Win64OpenSSL_Light-3_5_1.msi"))
            # Téléchargement avec barre de progression
            def report(count, block_size, total_size):
                percent = int(count * block_size * 100 / total_size)
                print(f"\rProgression: {percent}%", end='')

            urllib.request.urlretrieve(url, installer_path, reporthook=report)

            print("\nInstallation d'OpenSSL en cours...")
            print(f"Path open ssl {installer_path}")
            # Installation silencieuse
            result = subprocess.run(
                ["msiexec", "/i", str(installer_path), "/quiet", "/norestart"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise Exception(f"Échec installation: {result.stderr}")

            # Ajout au PATH
            openssl_path = Path(os.environ["ProgramFiles"]) / "OpenSSL-Win64" / "bin"
            os.environ["PATH"] = f"{openssl_path};{os.environ['PATH']}"
            
            # Vérification finale
            if not shutil.which('openssl'):
                raise Exception("OpenSSL toujours introuvable après installation")
                
            print("✓ OpenSSL installé avec succès")
            return True

        except Exception as e:
            print(f"\nErreur: {str(e)}")
            print("Veuillez installer manuellement depuis:")
            print("https://slproweb.com/products/Win32OpenSSL.html")
            return False
        
    
    def mysql_ssl_path(self):
        
        server_name ="localhost" # "127.0.0.1"  # À remplacer par votre FQDN ou IP
        server_ip = "127.0.0.1"          # À remplacer par votre IP serveur
        san_file = os.path.join(self.ssl_dir, 'san.cnf')
        with open(san_file, 'w') as f:
            f.write(f"""[req]
                    distinguished_name = req_distinguished_name
                    req_extensions = v3_req

                    [req_distinguished_name]

                    [v3_req]
                    subjectAltName = @alt_names

                    [alt_names]
                    DNS.1 = localhost
                    IP.1 = 127.0.0.1          
        
                """)
        ssl_commands = [
            # Autorité de certification
            ['openssl', 'genrsa', '-out', Path(self.ssl_dir, 'ca-key.pem').as_posix(), '2048'],
            
            ['openssl', 'req', '-new', '-x509', '-nodes', '-days', '3650',
            '-key', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
            '-out', Path(self.ssl_dir, 'ca.pem').as_posix(),
            '-subj', f'/CN=CA MySQL - {server_name}'],
            # 2. COMMANDE OPENSSL - SUPPRIMER -addext
            ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes',
            '-keyout', Path(self.ssl_dir, 'server-key.pem').as_posix(),
            '-out', Path(self.ssl_dir, 'server-req.pem').as_posix(),
            '-subj', f'/CN={server_name}',
            # '-addext', f'subjectAltName=DNS:{server_name},IP:{server_ip}',  # <-- SUPPRIMER CETTE LIGNE
            '-config', san_file],  # <-- AJOUTER -config pour utiliser le fichier

            # 3. GARDER LA COMMANDE x509 TEL QUEL
            ['openssl', 'x509', '-req', '-in', Path(self.ssl_dir, 'server-req.pem').as_posix(),
            '-days', '3650', '-CA', Path(self.ssl_dir, 'ca.pem').as_posix(),
            '-CAkey', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
            '-set_serial', '01', '-out', Path(self.ssl_dir, 'server-cert.pem').as_posix(),
            '-extensions', 'v3_req',
            '-extfile', san_file],
            # Certificat client
            ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes',
            '-keyout', Path(self.ssl_dir, 'client-key.pem').as_posix(),
            '-out', Path(self.ssl_dir, 'client-req.pem').as_posix(),
            '-subj', f'/CN=Client MySQL - {server_name}'],
            
            ['openssl', 'x509', '-req', '-in', Path(self.ssl_dir, 'client-req.pem').as_posix(),
            '-days', '3650', '-CA', Path(self.ssl_dir, 'ca.pem').as_posix(),
            '-CAkey', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
            '-set_serial', '01', '-out', Path(self.ssl_dir, 'client-cert.pem').as_posix()]
        ]

        try:
            for cmd in ssl_commands:
                subprocess.run(cmd,  
            check=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\n [x] {e}")



    def create_my_ini(self):
        """Crée le fichier my.ini et génère les certificats SSL de manière sécurisée"""
        print("\n[ + ] Création du fichier .ini et génération des certificats SSL...")

        if not shutil.which('openssl') and not self.install_openssl():
            print("""
            OpenSSL est requis. Options :
            1. Installez manuellement depuis :
            https://slproweb.com/products/Win32OpenSSL.html
            2. Ou relancez ce script en administrateur
            """)
            sys.exit(1)
        
        try:
            if not os.path.exists(self.ssl_dir):
                os.makedirs(self.ssl_dir, exist_ok=True)
    
                os.makedirs(os.path.join(self.extract_dir, 'logs'), exist_ok=True)

                # 1. Configuration du nom d'hôte (à adapter selon votre environnement)
                server_name ="localhost" # "127.0.0.1"  # À remplacer par votre FQDN ou IP
                server_ip = "127.0.0.1"          # À remplacer par votre IP serveur

                san_file = os.path.join(self.ssl_dir, 'san.cnf')

                san_file = os.path.join(self.ssl_dir, 'san.cnf')
                with open(san_file, 'w') as f:
                    f.write(f"""[ req ]
                        default_bits = 2048
                        default_md = sha256
                        prompt = no
                        encrypt_key = no
                        distinguished_name = dn
                        x509_extensions = v3_req

                        [ dn ]
                        CN = localhost

                        [ v3_req ]
                        subjectAltName = @alt_names
                        keyUsage = digitalSignature, keyEncipherment
                        extendedKeyUsage = serverAuth, clientAuth

                        [ alt_names ]
                        DNS.1 = localhost
                        DNS.2 = aplekol360.local
                        IP.1 = 127.0.0.1
                        IP.2 = ::1
                        """)
                    
                
                # 2. Génération sécurisée des certificats AVEC SAN
                ssl_commands = [
                    # Autorité de certification
                    ['openssl', 'genrsa', '-out', Path(self.ssl_dir, 'ca-key.pem').as_posix(), '2048'],

                    [
                        'openssl', 'req', '-new', '-x509', '-nodes', '-days', '3650',
                        '-key', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
                        '-out', Path(self.ssl_dir, 'ca.pem').as_posix(),
                        '-subj', f'/CN=CA MySQL - {server_name}',
                        '-addext', 'basicConstraints=critical,CA:TRUE'  # <--- AJOUTEZ CETTE LIGNE
                    ],
                    

                    # 2. COMMANDE OPENSSL - SUPPRIMER -addext
                    ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes',
                    '-keyout', Path(self.ssl_dir, 'server-key.pem').as_posix(),
                    '-out', Path(self.ssl_dir, 'server-req.pem').as_posix(),
                    '-subj', f'/CN={server_name}',
                    '-config', san_file],  # <-- AJOUTER -config pour utiliser le fichier

                    # 3. GARDER LA COMMANDE x509 TEL QUEL
                    ['openssl', 'x509', '-req', '-in', Path(self.ssl_dir, 'server-req.pem').as_posix(),
                    '-days', '3650', '-CA', Path(self.ssl_dir, 'ca.pem').as_posix(),
                    '-CAkey', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
                    '-set_serial', '01', '-out', Path(self.ssl_dir, 'server-cert.pem').as_posix(),
                    '-extensions', 'v3_req',
                    '-extfile', san_file],
                    
                    # Certificat client
                    ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes',
                    '-keyout', Path(self.ssl_dir, 'client-key.pem').as_posix(),
                    '-out', Path(self.ssl_dir, 'client-req.pem').as_posix(),
                    '-subj', f'/CN=Client MySQL - {server_name}'],
                    
                    ['openssl', 'x509', '-req', '-in', Path(self.ssl_dir, 'client-req.pem').as_posix(),
                    '-days', '3650', '-CA', Path(self.ssl_dir, 'ca.pem').as_posix(),
                    '-CAkey', Path(self.ssl_dir, 'ca-key.pem').as_posix(),
                    '-set_serial', '02', '-out', Path(self.ssl_dir, 'client-cert.pem').as_posix()]
                ]

                try:
                    for cmd in ssl_commands:
                        subprocess.run(cmd,  
                    check=True)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(f"\n [x] {e}")

            # ... (exécution des commandes) ...


            # 3. Configuration MySQL optimisée
            config = f"""
            [mysqld]
            # SSL/TLS Configuration
            require_secure_transport=ON
            ssl-ca={Path(self.ssl_dir, "ca.pem").as_posix()}
            ssl-cert={Path(self.ssl_dir, "server-cert.pem").as_posix()}
            ssl-key={Path(self.ssl_dir, "server-key.pem").as_posix()}
            # ssl-cipher=DHE-RSA-AES256-SHA
            tls_version=TLSv1.2,TLSv1.3
            #tls_version=TLSv1.2,TLSv1.3
            #default-time-zone = 'America/Port-au-Prince'

            # ... (le reste de la configuration reste inchangé) ...
            basedir={self.extract_dir}
            datadir={self.data_dir}
            # Réseau
            bind-address=0.0.0.0
            port=3307
            socket=mysql3307.sock
            skip_shared_memory=ON
            #skip-networking=0
            # shared-memory=on
            skip_shared_memory=ON  # Désactive les connexions via mémoire partagée
            shared_memory=OFF
            skip_name_resolve=ON
             
            # require-secure-transport=ON
            # require-secure-transport=ON
            # require-secure-transport=OFF


            
            log_bin_trust_function_creators=1
            
            # InnoDB
            innodb_force_recovery=0
            innodb_flush_method=normal
            innodb_buffer_pool_size=1024M
            innodb_redo_log_capacity=268435456
            innodb_file_per_table=ON
            innodb_flush_log_at_trx_commit=2
            innodb_buffer_pool_instances=2

            init-file="{os.path.join(self.extract_dir, 'init.sql')}"

            authentication_policy=caching_sha2_password

            # Logging
            log_error={os.path.join(self.extract_dir, 'logs', 'mysql_error.log')}
            general_log_file={os.path.join(self.extract_dir, 'logs', 'mysql_query.log')}
            general_log=1

            # Optimisation mémoire
            key_buffer_size=232M
            max_allowed_packet=464M
            thread_cache_size=10
            table_open_cache=2000

            [client]
            # protocol=TCP 
            port=3307
            socket=mysql3307.sock
            ssl-mode=VERIFY_IDENTITY #VERIFY_CA   
            # ssl-ca={Path(self.ssl_dir, "ca.pem").as_posix()} 
            # ssl-cert={Path(self.ssl_dir, "client-cert.pem").as_posix()}
            # ssl-key={Path(self.ssl_dir, "client-key.pem").as_posix()}

            [mysql]
            default-character-set=utf8
            """

            # ... (écriture du fichier de configuration) ...
            with open(self.my_ini_path, 'w',encoding='utf-8') as f:
                f.write(textwrap.dedent(config))

            # 6. Initialisation du mot de passe root
            # init_script = f"""
            # ALTER USER 'root'@'localhost' IDENTIFIED BY '@@@@@@';
            # CREATE USER 'replicator'@'%' IDENTIFIED WITH caching_sha2_password BY 'Repl!c@t0rP@ss';
            # GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
            # FLUSH PRIVILEGES; REQUIRE SSL
            # """
            scripts = f"""
                CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED WITH caching_sha2_password BY '@@@@@@';
                GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
                ALTER USER 'root'@'localhost' IDENTIFIED BY '@@@@@@';
                FLUSH PRIVILEGES;
                """
            self.file_path = os.path.join(self.extract_dir, "init.sql")
            
            with open(self.file_path, "w", encoding='utf-8') as f:
                        # with open(self.file_path, "w") as file:
                # f.write("ALTER USER 'root'@'localhost' IDENTIFIED BY '@@@@@@';\nFLUSH PRIVILEGES;")
                f.write(textwrap.dedent(scripts))

            print("✅ Configuration MySQL créée avec succès")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"\n [x] Erreur : {e}")
            return

# mysql -u root -p --host=127.0.0.1 --port=3307 ^
# --ssl-ca=C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem ^
# --ssl-cert=C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem ^
# --ssl-key=C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem ^
# --ssl-mode=VERIFY_IDENTITY



# mysql -u root -p --host=192.168.0.106 --ssl-ca=C:/ecole_1/mysql-8.0.41-winx64/certs/ca.pem --ssl-mode=VERIFY_IDENTITY

# openssl x509 -in C:/ecole_1/mysql-8.0.41-winx64/certs/server-cert.pem -text -noout


# mysqldump -u root -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lemignon > "C:\local_mignon_10_12_2025.sql"

# mysqldump -u root -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lemignon --no-data > "C:\local_mignon_no_data_9_12_2025.sql"


# mysql -u root -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lekol360 < "C:\Users\fritz\OneDrive\Desktop\04_02_2025.sql"

# mysql -u root -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY < "C:\Users\fritz\OneDrive\Desktop\local_5_12_2025_v2.sql"


# lekol360
# @#Lekol3&0
   
    def download_mysql(self):
        """Télécharge MySQL depuis le site officiel"""
        print("\n [ + ]   Téléchargement de MySQL... \n")

        if not self.download_path:
            print("\n [x]   Le chemin de téléchargement n'est pas spécifié.")
            return

        try:
            subprocess.run(["curl", "-L", self.mysql_url, "-o", self.download_path], check=True, timeout=1800)  # timeout de 10 minutes
            print(Fore.GREEN + "\n [ ok ]   Téléchargement terminé.")
        except subprocess.CalledProcessError as e:
            print(f"\n [x]   Erreur lors du téléchargement de MySQL : {e}")
            return
        except subprocess.TimeoutExpired:
            print("\n [ x ]   Le téléchargement a expiré. Réessayez plus tard.")
            return
        except Exception as e:
            print(f"\n [x]   Erreur inconnue : {e}")
            return
 
    def extract_mysql(self):
        """Extrait le fichier ZIP téléchargé"""
        print("\n [ + ]   Extraction de MySQL...")

        if not os.path.exists(self.download_path):
            print(f"Le fichier téléchargé '{self.download_path}' n'existe pas.")
            input("Quitter...")
            return

        os.makedirs(self.current_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(self.current_dir)
            print(Fore.GREEN + "\n [ ok ]   Extraction terminée.")
        except zipfile.BadZipFile:
            print(f"\n [x]   Erreur lors de l'extraction du fichier ZIP : Le fichier semble corrompu.")
        except Exception as e:
            print(f"\n [x]   Erreur lors de l'extraction : {e}")


    def masked_input(self, prompt="Mot de passe : "):
        print(prompt, end="", flush=True)
        password = ""

        while True:
            char = msvcrt.getch()  # Lire un caractère sans affichage
            if char in {b'\r', b'\n'}:  # Touche Entrée
                break
            elif char == b'\b':  # Gérer le backspace
                if len(password) > 0:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)  # Efface visuellement
            else:
                password += char.decode("utf-8")
                print("*", end="", flush=True)  # Afficher `*`
        
        print()  # Nouvelle ligne après validation
        return password
   
    def initialize_database(self):
        """Initialise la base de données MySQL"""
        # Initialisation de la base de données MySQL
        if not self.is_installed_service("MySQLEcole"):
            try:
                print("\n [ + ]   Initialisation de la base de données MySQL...")
                subprocess.run([os.path.join(self.bin_dir, "mysqld"), "--initialize",f"--init-file={self.file_path}", "--console"], 
                    check=True)

                # stdout=subprocess.DEVNULL, # Ignore la sortie standard
                # stderr=subprocess.DEVNULL,  # Ignore les erreurs
                #   stdout=subprocess.DEVNULL,
                print(Fore.GREEN + "\n [ ok ]   Base de données initialisée.")
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"\n [x]   error in initilize {e}")
                return
            
    def is_installed_service(self, service_name):
        """ Vérifie si un service MySQL existe """
        try:
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            return "FAILED" not in result.stdout
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du service {service_name}: {e}")
            return False

    
    def install_mysql_as_service(self):
        """Installe MySQL en tant que service Windows"""
        if not self.is_installed_service("MySQLEcole"):
            try:
                print("\n [ x ]   Suppression de l'ancien service MySQL s'il existe...")
                subprocess.run(["sc", "delete", self.service_name], shell=True, check=False)

                print("\n [ + ]   Installation de MySQL en tant que service...")

                cmd = [
                    os.path.join(self.bin_dir, "mysqld.exe"),
                    "--install", self.service_name,
                    f"--defaults-file={self.my_ini_path}"
                ]
                subprocess.run(cmd, check=True)
                
                print(Fore.GREEN + "\n [ ok ]   Service MySQL installé avec succès!")
            except Exception as e:
                print(f"\n [x]   Erreur lors de l'installation du service MySQL : {e}")

    def start_mysql_service(self):
        """Démarre le service MySQL"""
        try:
            print("\n [ + ]   Démarrage du service MySQL...")
            # mysql_path = r"C:\Users\fritz\OneDrive\Desktop\ecole_1\mysql-8.0.41-winx64\bin\mysqld.exe"
            subprocess.Popen([os.path.join(self.bin_dir, 'mysqld.exe'), f"--defaults-file={self.my_ini_path}"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            #  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            # subprocess.Popen(["net", "start", self.service_name])
            # subprocess.Popen(["net", "start", self.service_name], shell=True, check=True)
            print(Fore.GREEN + "\n [ ok ]   Service MySQL démarré avec succès!")
        except subprocess.CalledProcessError as er:
            print(f" [x]   Erreur lors du démarrage du service MySQL ---: {er}")
        except Exception as e:
            print(f" [x]   Erreur lors du démarrage du service MySQL ---: {e}")


    def fix_permissions(self):
        try:
            subprocess.run(["icacls", self.data_dir, "/grant", "Everyone:(OI)(CI)F", "/t"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True)
            subprocess.run(["icacls", self.ssl_dir, "/grant", "Everyone:(OI)(CI)F", "/t"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True,)
            subprocess.run(["icacls", self.bin_dir, "/grant", "Everyone:(OI)(CI)F", "/t"],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,check=True,)
            #print("Permissions corrigées")Erreur lors de l'extraction 
        except Exception as e:
            print(f"--------not perms------------- {e}")

    def set_full_permissions(self, path):
        """Définir les permissions complètes sur un répertoire/fichier"""
        try:
            import win32security
            import ntsecuritycon as con
            
            # Donner à Everyone le contrôle total
            cmd = f'icacls "{path}" /grant Everyone:(OI)(CI)F /t'
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            print(Fore.GREEN + f" [ok] Permissions définies pour: {path}")
            return True
            
        except Exception as e:
            print(Fore.YELLOW + f" [warn] Impossible de définir les permissions: {e}")
            
            # Fallback: utiliser takeown
            try:
                subprocess.run(f'takeown /f "{path}" /r /d y', shell=True, check=True)
                subprocess.run(f'icacls "{path}" /grant Everyone:F /t', shell=True, check=True)
                print(Fore.GREEN + f" [ok] Permissions définies avec takeown")
                return True
            except Exception as e2:
                print(Fore.RED + f" [x] Échec des permissions: {e2}")
                return False

    def clean_up(self):
        """Supprime les fichiers temporaires"""
        print("\n [-]   Nettoyage des fichiers temporaires...")
        if self.download_path:
            # os.remove(self.download_path)
            print("\n [-]   Fichier ZIP supprimé.")

    def prompt_for_password_and_db(self):
        """Demander à l'utilisateur un mot de passe et un nom de base de données"""
        self.db_name = 'lekol360' #input("\n [+]  Entrez le nom de la base de données à créer : ")

        self.new_password = '@#Lekol3&0' # self.masked_input("\n [+]  Entrez le nouveau mot de passe de la base: ")
        # Vérification de la longueur du mot de passe
        while len(self.new_password) < 6:
            print("\n [+]  Le mot de passe doit contenir au moins 6 caractères.")
            self.new_password =  self.masked_input("\n [+]  Entrez le nouveau mot de passe de la base: ")
        
        if self.db_name != "lekol360":
            mysql_admin = MySQLAdmin(
                service_name=self.service_name,
                bin_dir=self.bin_dir,
                my_ini_path=self.my_ini_path,
                extract=self.ssl_dir
            )

            mysql_admin.set_root_password(self.new_password, self.db_name)

        # manager = WireGuardWindowsManager()
        
        # manager.setup_wireguard()


    def return_data(self):
        return [self.new_password, self.db_name]
    


    def get_resource_path(self, relative_path: str)-> str:
        """
        Retourne le chemin absolu d'une ressource, compatible avec :
        - Exécution normale (script Python)
        - Applications compilées avec PyInstaller
        - Applications compilées avec Nuitka
        - Mode développement et production

        Args:
            relative_path: Chemin relatif de la ressource
            verify_exists: Si True, vérifie que le fichier existe avant de retourner

        Returns:
            Chemin absolu ou None si vérification activée et fichier introuvable
        """
        
        # return base_path.resolve()
        """Retourne le chemin absolu d'une ressource (compatible PyInstaller et Nuitka)."""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            base_path = sys._MEIPASS
        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
        else:
            # Exécution normale
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


    def install_and_config(self):
        """Procédure complète d'installation et de configuration de MySQL"""
        # if not os.path.exists(self.download_path):
        if not os.path.exists(os.path.join(self.current_dir,"data",self.zip_file)):
            self.download_mysql()

        self.fix_permissions()

        self.extract_mysql()

        self.create_my_ini()

        # self.setup_mysql_ssl()

        self.fix_permissions()

        self.initialize_database()
        
        self.install_mysql_as_service()
    

        self.start_mysql_service()
         
        self.clean_up()
        
        self.prompt_for_password_and_db()

        print("Installation de MySQL terminée.")


class MySQLSetup:
    def __init__(self):
        self.db_name = "ecole_db"
        self.user = "ecole_user"
        self.nom_actuel = None

    def is_installed_service(self, service_name):
        """ Vérifie si un service MySQL existe """
        try:
            result = subprocess.run(
                ["sc", "query", service_name], capture_output=True, text=True
            )
            return "FAILED" not in result.stdout
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du service {service_name}: {e}")
            return False
        
    def find_mysql_root(self):
        """ Trouve l'installation de MySQL en cherchant 'mysqld' dans le PATH et retourne le dossier racine """
        try:
            output = subprocess.check_output(["where", "mysqld"], shell=True, text=True).strip()
            mysql_bin = output.split("\n")[0]  # Prend le premier résultat
            mysql_root = os.path.dirname(os.path.dirname(mysql_bin))  # Remonte d'un niveau pour enlever /bin
            return mysql_root
        except subprocess.CalledProcessError:
            return None
        
    def create_mysql_service(self, service_name="MySQLEcole"):
        """ Crée un service MySQL avec un nouveau fichier my.ini et un port dynamique. """
        mysql_path = self.find_mysql_root()
        if not mysql_path:
            print("❌ MySQL n'est pas installé.")
            return
        
        bin_path = os.path.join(mysql_path, "bin", "mysqld.exe")
        data_path = os.path.join(mysql_path, "data")
        
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        try:
            subprocess.run(["icacls", data_path, "/grant", "Everyone:(OI)(CI)F", "/t"], check=True)
            print("Permissions corrigées")
        except Exception as e:
            print(f"---------{e}")
        my_ini_path = os.path.join(mysql_path, "my.ini")

        print("\n [+]   Création du fichier my.ini avec les chemins corrects !!!")

        config_content = f"""
        [mysqld]
        # Chemins critiques
        basedir={mysql_path}
        datadir={data_path}
        #os.path.join(mysql_path, 'data')
   

        # Réseau et connexion
        bind-address=0.0.0.0
        port=3306 
        skip-networking=0
        socket=mysql3306.sock
        shared-memory=on
        skip-name-resolve

        # Paramètres InnoDB essentiels
        innodb_force_recovery=1
        innodb_flush_method=normal
        innodb_buffer_pool_size=256M
        innodb_redo_log_capacity=268435456
        innodb_file_per_table=ON
        innodb_flush_log_at_trx_commit=2
        innodb_buffer_pool_instances=2

        # Sécurité et authentification
        authentication_policy=caching_sha2_password 
        require_secure_transport=OFF


        # Journalisation
        log_error={os.path.join(mysql_path, 'logs', 'mysql_error.log')}
        general_log=1
        general_log_file={os.path.join(mysql_path, 'logs', 'mysql_query.log')}

        # Optimisation mémoire
        key_buffer_size=232M
        max_allowed_packet=464M
        thread_cache_size=10
        table_open_cache=2000

        
        [client]
        port=3306
        socket=mysql3306.sock

        [mysql]
        default-character-set=utf8
        """

        os.makedirs(os.path.join(mysql_path, 'logs'), exist_ok=True)

        with open(my_ini_path, 'w') as f:
            f.write(config_content)
        
        # Créer le service Windows pour MySQL
        service_cmd = [bin_path,
                "--install", "MySQLEcole",
                f"--defaults-file={my_ini_path}"
            ]

        
        try:
            subprocess.run(service_cmd, shell=True, check=True)

            subprocess.Popen([bin_path, f"--defaults-file={my_ini_path}"])
            
            # Démarrer le service
            subprocess.run(f'sc start {service_name}', shell=True, check=True)
            print(f"🚀 Service {service_name} démarré.")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la création du service : {e}")

    def get_resource_path(self, relative_path: str) -> str:
        """Retourne le chemin absolu d'une ressource (compatible PyInstaller et Nuitka)."""
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            base_path = sys._MEIPASS
        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
        else:
            # Exécution normale
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path) 
    
    def masked_input(self, prompt="Mot de passe : "):
        print(prompt, end="", flush=True)
        password = ""

        while True:
            char = msvcrt.getch()  # Lire un caractère sans affichage
            if char in {b'\r', b'\n'}:  # Touche Entrée
                break
            elif char == b'\b':  # Gérer le backspace
                if len(password) > 0:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)  # Efface visuellement
            else:
                password += char.decode("utf-8")
                print("*", end="", flush=True)  # Afficher `*`
        
        print()  # Nouvelle ligne après validation
        return password

    def create_database_and_user(self, ip_ser):
        """ Demande le mot de passe root et crée la base + utilisateur """

        self.nom_actuel = input("\n [+]  Entrez le nom d'utilisateur de la base: ")
        port_use = input("\n [+]  Entrez le port utilisé:  ")

        root_password = self.masked_input(f"\n [+]  Entrez le mot de passe MySQL pour {self.nom_actuel} : ")

        db_name ='lekol360' #input("\n [+]  Entrez le nom de la base de données à créer:  ")
        username ='root' #input("\n [+]  Entrez le nom d'utilisateur de la base:  ")

        new_password ='@#Lekol3&0' #self.masked_input(f"\n [+]  Entrez le nouveau mot de passe pour l'utilisateur {db_name} : ")
        
        # if not self.nom_actuel or
        
        ip_parts = ip_ser.split(".")
        ip_range = '127.0.0.1' #".".join(ip_parts[:3]) + ".%"
        try:
            print("📌 Création de la base de données et de l'utilisateur...")
            commands = [
                f"CREATE DATABASE IF NOT EXISTS {db_name};",
                f"CREATE USER IF NOT EXISTS '{username}'@'{ip_range}' IDENTIFIED BY '{new_password}';",
                # f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{user}'@'localhost';",

                f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{username}'@'{ip_range}' WITH GRANT OPTION;"
                "FLUSH PRIVILEGES;"
            ]
            for cmd in commands:
                subprocess.run(
                    ["mysql", "-u", f"{self.nom_actuel}", f"-p{root_password}", "-P", f"{port_use}", "-e", cmd],
                    check=True, stderr=subprocess.DEVNULL
                )

            # subprocess.Popen([bin_path, f"--defaults-file={my_ini_path}"])
            print("✅ Base de données et utilisateur créés avec succès !")

            env_path = os.path.join(self.current_project,'data', ".env")
            with open(env_path, "r") as file:
                content = file.read()  # Lire tout le contenu

            content = content.replace("DB_DATABASE=", f"DB_DATABASE={db_name} #")
            content = content.replace("DB_PASSWORD=", f"DB_PASSWORD='{new_password}'#")
            content = content.replace("DB_USERNAME=", f"DB_USERNAME='{username}'#")
            content = content.replace("DB_PORT=", f"DB_PORT={port_use}#")

            # content = content.replace("DB_SSL_CA=C:/", f"DB_SSL_CA={Path(self.ssl_dir, 'ca.pem').as_posix()}#")
            # content = content.replace("DB_SSL_CERT=C:/", f"DB_SSL_CERT={Path(self.ssl_dir, 'ca.pem').as_posix()}#")
            # content = content.replace("DB_SSL_KEY=C:/", f"DB_SSL_KEY={Path(self.ssl_dir, 'ca.pem').as_posix()}#")

            



            # Réécriture correcte
            with open(env_path, "w") as file:
                file.write(content)
        except Exception as e:
            print(f"❌ Erreur lors de la création de la base/utilisateur, ")
            return

    def run(self, ip_ser):
        """ Exécute la vérification et la configuration """
        # if not self.is_installed("MySQL"):
        #     print("❌ MySQL n'est pas installé.")
        #     return

        if not self.is_installed_service("MySQLEcole"):
            if self.nom_actuel == 'sqlite':
                env_path = os.path.join(self.current_project,'data',".env")
                # env_path = os.path.join(self.current_project,"data", ".env"))
                with open(env_path, "r") as file:
                    content = file.read()
                content = content.replace("DB_CONNECTION=", f"DB_CONNECTION=sqlite #")
                content = content.replace("DB_HOST=", "#DB_HOST")
                content = content.replace("DB_PORT=", "#DB_PORT")
                content = content.replace("DB_DATABASE=", f"DB_DATABASE={os.path.join(self.current_project,'nginx','html', 'api', 'database.db')}#")
                content = content.replace("DB_USERNAME=", "#DB_USERNAME")
                content = content.replace("DB_PASSWORD=", "#DB_PASSWORD")

                with open(env_path, "w") as file:
                    file.write(content)
            else:
                self.create_database_and_user(ip_ser)
            # self.create_mysql_service()


class MySQLAdmin:
    def __init__(self, bin_dir, my_ini_path, service_name, port="3307", extract=None):
        self.bin_dir = bin_dir
        self.my_ini_path = my_ini_path
        self.service_name = service_name
        self.port = port
        self.extract_dir = extract


    def check_mysql_service(self):
        """Vérifie et corrige l'état du service MySQL"""
        try:
            # Vérifier si le service est installé
            subprocess.run(
                ["sc", "query", self.service_name],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
          
            # Forcer un redémarrage propre
            subprocess.run(["net", "stop", self.service_name], timeout=30, check=False)
            subprocess.run(["net", "start", self.service_name], timeout=30, check=True)
            # "default_authentication_plugin": "mysql_native_password"


    def get_connection_protocol(self):
        """Détermine le meilleur protocole de connexion"""
        try:
            # Essai de connexion TCP
            with socket.create_connection(("127.0.0.1", 3307), timeout=20):
                return "TCP"
        except:
            return "SOCKET"

    def check_network_configuration(self):
        """Diagnostic réseau complet"""
        print("\n [ + ]   === DIAGNOSTIC RÉSEAU ===")        
        # 1. Vérification du port
        subprocess.run(["netstat", "-ano|findstr", ":3307"], shell=True)
        
    def set_root_password(self, new_password, db_name):
        if db_name != "lekol360":
            try:
                self.check_mysql_service()           

                self.get_connection_protocol()            

                self.check_network_configuration()

                print(f"\n [ + ]   Connexion et configuration de la base de donnees ...")
                time.sleep(5)

                mysql_path = os.path.join(self.bin_dir, "mysql.exe")
                pass_word = '@@@@@@'
                
                # --ssl-mode=REQUIRED

                if not os.path.exists(mysql_path):
                    print(f" [x] ERREUR: mysql.exe introuvable à l'emplacement {mysql_path}")
                    return
    
                print(f"\n [ok]  Connexion reussie")
                
                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}",
                    '-e', "CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '@@@@@@';"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(Fore.GREEN + "\n [ ok ]  Utilisateur créé avec succès.")

                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}",
                    '-e', "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                print(Fore.GREEN + "\n [ ok ]   PRIVILEGES créé avec succès.")

                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}",
                    '-e', "FLUSH PRIVILEGES;"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)          


                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}",
                        '-e', f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{new_password}';"
                ], ) 

                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                    f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}",
                        '-e', "FLUSH PRIVILEGES;"
                ], )

                print(Fore.GREEN + "\n [ok]   Mot de passe changé avec succès !")
    
                        # CREATE USER 'ssl_reader'@'%' IDENTIFIED BY '@#ssl_reader21'; 
                        # GRANT SELECT ON lemignon.client_infos TO 'ssl_reader'@'%';
                        # GRANT SELECT ON lemignon.direct_configs TO 'ssl_reader'@'%'; 
                        # FLUSH PRIVILEGES;

                # try:
                #     ssl_ca = Path(self.extract_dir,'ca.pem').as_posix()
                #     ssl_cert = Path(self.extract_dir,'client-cert.pem').as_posix()
                #     ssl_key = Path(self.extract_dir,'client-key.pem').as_posix()
                #     create_user_ssl = [
                #         mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                #         f'--ssl-ca={ssl_ca}',
                #         f'--ssl-cert={ssl_cert}',
                #         f'--ssl-key={ssl_key}',
                #         '-e',
                #         f"""
                #         CREATE USER 'ssl_reader'@'%' IDENTIFIED BY '@#ssl_reader21'; 
                #         GRANT SELECT ON {db_name}.client_infos TO 'ssl_reader'@'%';
                #         GRANT SELECT ON {db_name}.direct_configs TO 'ssl_reader'@'%'; 
                #         FLUSH PRIVILEGES;
                #         """
                #     ]
                #     subprocess.run(create_user_ssl)

                # except Exception as e:
                #   print(f'An exception occurred {e}')

                try:
                    ssl_ca = Path(self.extract_dir,'ca.pem').as_posix()
                    ssl_cert = Path(self.extract_dir,'client-cert.pem').as_posix()
                    ssl_key = Path(self.extract_dir,'client-key.pem').as_posix()

                    # Requête pour tester si l'utilisateur existe
                    check_user_cmd = [
                        mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f'--ssl-ca={ssl_ca}',
                        f'--ssl-cert={ssl_cert}',
                        f'--ssl-key={ssl_key}',
                        '-N', '-B',  # Pour un output brut
                        '-e', "SELECT COUNT(*) FROM mysql.user WHERE user='user_pyside' AND host='%';"
                    ]

                    result = subprocess.run(check_user_cmd, capture_output=True, text=True)
                    user_exists = result.stdout.strip() == '1'

                    if not user_exists:
                        create_user_cmd = [
                            mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                            f'--ssl-ca={ssl_ca}',
                            f'--ssl-cert={ssl_cert}',
                            f'--ssl-key={ssl_key}',
                            '-e',
                            """
                            CREATE USER 'user_pyside'@'%' IDENTIFIED BY '@#Janvier21';
                            ALTER USER 'user_pyside'@'%' REQUIRE X509;
                            GRANT ALL PRIVILEGES ON *.* TO 'user_pyside'@'%';
                            FLUSH PRIVILEGES;
                            """
                        ]

                        subprocess.run(create_user_cmd)
                    else:
                        print("Utilisateur 'user_pyside' existe déjà.")

                except Exception as e:
                    print(f'An exception occurred 4 {e}')

                print("\n [ + ] Création de la base de données...")
                subprocess.run([
                    mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost',
                        f"--ssl-ca={Path(self.extract_dir,'ca.pem').as_posix()}",
                        f"--ssl-cert={Path(self.extract_dir,'client-cert.pem').as_posix()}",
                        f"--ssl-key={Path(self.extract_dir,'client-key.pem').as_posix()}", '-e', f"CREATE DATABASE IF NOT EXISTS {db_name};"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #             stderr=subprocess.DEVNULL
    # stderr=subprocess.DEVNULL
    # stderr=subprocess.DEVNULL
    # stderr=subprocess.DEVNULL
    # stderr=subprocess.DEVNULL
    # stderr=subprocess.DEVNULL

                print(Fore.GREEN +  f"\n [ ok ] Configuration terminée ! La base `{db_name}` est prête.")

            except FileNotFoundError as e:
                print(f"\n [x]    Erreur eeeee: {e}")
                self.check_network_configuration()
                raise
            except Exception as e:
                
                import traceback
                traceback.print_exc()



import sys
import os
import requests
import subprocess
from functools import partial
import platform
from PySide6.QtGui import QColor,QIcon,QCursor
# from PySide6.QtGui import 

from PySide6.QtCore import Qt,QTimer
from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,QGraphicsDropShadowEffect,QFrame,QGroupBox,QCheckBox,QScrollArea, QSystemTrayIcon, QMenu,QApplication,QLineEdit,QDialog,QTextEdit
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap
from Helper.Ip_manager import Ip_manager
from Helper.Ip_manager import Ip_manager
from Helper.server_key_generate import get_mac_address,verify_activation_key_graphic,is_license_valid
from PySide6.QtGui import QAction
import base64

class ServiceControlWindow(QWidget):
    def __init__(self, base__url = None):
        super().__init__()
        self.setWindowTitle("Gestion des Services")
        self.setGeometry(100, 100, 600, 640)
        self.WG_CONF_PATH = r"C:\ProgramData\WireGuard\Configurations\wg0.conf"

        self.setWindowFlags(Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground,False) 
        # self.setWindowOpacity(1)
        self.token_access = None
        # self.setStyleSheet("background-color: #2E2E2E; color: white; border-radius: 0px;") 
        self.base__url= base__url
        print(f"base__url  {self.base__url}")
        self.setStyleSheet("""

                          QWidget{background-color: #2E2E2E; color: white; border-radius: 10px;}
                                    QComboBox, QLineEdit, QDateEdit{ width: 400px; min-height: 33px; max-height: 33px;border: 1px solid #999; border-radius:5px;padding-left:7px}

                            QComboBox:hover,QComboBox:focus, QLineEdit:hover, QDateEdit:hover, QLineEdit:focus, QDateEdit:focus {
                    
                    border: 1px solid #007bff;
                }
                            QComboBox:disabled::drop-down{
                
                    color:#555
                }
                            QComboBox:disabled::drop-down, QDateEdit:disabled::drop-down{
                    background: transparent;
                }
                QLabel,QComboBox,QLineEdit{font-size:13pt}

    """)
     
 
        self.old_pos = None  
        self.services = ["MySQLEcole", "NginxAplekol"]  
        self.service_buttons = {}
        self.title_bar = QWidget()
        self.widget = QWidget()
        
 

        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(15, 15)  
        shadow.setBlurRadius(30)  
        shadow.setColor(QColor(2, 6, 0, 150))  
        self.widget.setGraphicsEffect(shadow)

        # self.ajouter_au_demarrage("école-server")


# ================================================MINIMIZE=========================================
        self.icon_path_logo = self.get_resource_path(os.path.join('Controllers', 'favicon.ico'))
 
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path_logo), parent=self)
        self.tray_icon.setToolTip("Server Gestion d'école")

        # Menu contextuel de l'icône (clic droit)
        self.tray_menu = QMenu(self)

        show_action = QAction("Afficher", self)
        quit_action = QAction("Quitter", self)

        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.shutDownAll)

        self.tray_menu.addAction(show_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        # menu.exec_(table_widget.mapToGlobal(pos))
        

        # Clic sur l'icône (clic gauche)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Affiche l'icône
        self.tray_icon.show()
    
    def shutDownAll(self):
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment fermer toutes les services en cours?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes: 
            for service in self.services:
                print(f"service   {service}")
                # self.get_service_status(service)
                subprocess.run(["net", "stop", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            QApplication.quit

    def show_window(self):
        # self.hide()
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """Lorsqu'on ferme la fenêtre, on la cache et on affiche un message."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application réduite",
            "L'application continue de s'exécuter en arrière-plan.",
            QSystemTrayIcon.Information,
            3000
        )


    def on_tray_icon_activated(self, reason):
        """Gère les interactions avec l'icône de la barre système"""
        if reason == QSystemTrayIcon.Trigger:  # Clic gauche
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
        elif reason == QSystemTrayIcon.DoubleClick:  # Double-clic
            self.show_window()
        elif reason == QSystemTrayIcon.Context:  # Clic droit
            # Le menu contextuel s'affichera automatiquement grâce à setContextMenu
            pass

 #=================================================================================================

     #    self.init_ui()
    def get_resource_path(self, relative_path: str) -> str:
        """Retourne le chemin absolu d'une ressource, adapté à PyInstaller."""
        # if getattr(sys, 'frozen', False):
        #     # Chemin dans le contexte temporaire de PyInstaller
        #     base_path = sys._MEIPASS
        # else:
        #     # Chemin normal (lors de l'exécution en script)
        #     base_path = os.path.abspath(".")
        # return os.path.join(base_path, relative_path)
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            base_path = sys._MEIPASS
        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
        else:
            # Exécution normale
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path) 
    

    def ajouter_au_demarrage(self, nom_app: str = "école-server"):
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")

        chemin_script = sys.argv[0]
        
        # Si tu utilises un .exe compilé (via PyInstaller), prends ce chemin-là
        if getattr(sys, 'frozen', False):
            chemin_executable = sys.executable
        else:
            # Sinon, on utilise le script Python directement
            chemin_executable = chemin_script

        raccourci_path = os.path.join(startup_dir, f"{nom_app}.bat")

        with open(raccourci_path, "w") as f:
            f.write(f'start "" "{chemin_executable}"')
 

    
    def init_ui(self, services,url,client_data = None, base_url =None):
        """Initialisation de l'interface."""
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 0, 10, 20)        

        
        
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #1C1C1C;")  
        self.title_bar.move(0, 0)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("Gestion des Services")
        title_label.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        title_layout.addWidget(title_label)

        #
        minimize_button = QPushButton()

        minimize_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 13pt;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: yellow;
            }
        """)
        minimize_button.setFixedSize(35, 35)
        min_icon = os.path.join(self.get_resource_path('Controllers'), 'min_w.png')
        icon = QIcon(min_icon)  
        minimize_button.setIcon(icon)
        minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_button)
 
       
        close_button = QPushButton()
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 12pt;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: red;
                                   
            }
        """)
        close_button.setFixedSize(35, 35)

        close_icon = os.path.join(self.get_resource_path('Controllers'), 'close_w.png')
        icon = QIcon(close_icon)  
        close_button.setIcon(icon)

        close_button.clicked.connect(self.confirm_close)
        title_layout.addWidget(close_button)

        self.title_bar.setLayout(title_layout)
        layout.addWidget(self.title_bar)

        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(6, 9, 6, 9)
        body_layout.setSpacing(10)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.authorization(body_layout,client_data,url)

        groupe_box = QGroupBox("Services")

        groupe_box.setStyleSheet("""
                                 QLabel{font-size:12pt}
            QGroupBox {
                font-size: 12pt;
                color: #333;
                border: 1px solid #777;
                border-radius: 5px;
                margin-top: 15px;
                padding: 5px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0px;
                color: #0078D7;
            }
        """)

        main_layout = QVBoxLayout(groupe_box)
        main_layout.setSpacing(0)
        # self.attach_php(main_layout)

        self.attach_services(main_layout)

        body_layout.addWidget(groupe_box)

        # Liste des services avec leurs boutons ON/OFF
        v_layout_service = QVBoxLayout()
        v_layout_service.setSpacing(0)
        v_layout_service.setContentsMargins(0, 0, 0, 0)

        for service in services:
            service_layout = QHBoxLayout()
            service_layout.setContentsMargins(2, 0, 2, 0)
            service_label = QLabel("Service MySQL" if service == "MySQLEcole" else "Service Apache")
            service_label.setStyleSheet("font-size: 14pt; padding: 7px;")  # 🔹 Texte blanc, sans fond
            service_layout.addWidget(service_label)

            # Vérifier l'état du service
            status = self.get_service_status(service)
            toggle_button = QPushButton("ON" if status else "OFF")
            toggle_button.setCheckable(True)
            toggle_button.setChecked(status)
            toggle_button.setStyleSheet(self.get_button_style(status))
            toggle_button.clicked.connect(lambda checked, s=service, b=toggle_button: self.toggle_service(s, b, checked))

            self.service_buttons[service] = toggle_button
            service_layout.addWidget(toggle_button)
            v_layout_service.addLayout(service_layout)

        # self.fram_activate_synchro =  QFrame()
        # self.layout__synchro = QVBoxLayout(self.fram_activate_synchro) 
        # self.layout__synchro.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.btn_verify_synchro = QPushButton("Activer la synchronisation")
        # self.btn_verify_synchro.setCursor(Qt.PointingHandCursor)
        # self.btn_verify_synchro.setStyleSheet("""
        #         QPushButton {
        #             text-align: center;
        #             padding: 5px;
        #             width: 200px;
        #             color: #007bff; 
        #             border: 1px solid #007bff; 
        #             border-radius: 5px; 
        #             font-size: 13pt;
        #         }
        #         QPushButton:hover { 
        #             color: #fff; 
        #             background-color: #007bff;
        #         }
        # """)
        # # self.btn_verify_synchro.clicked.connect(self.check_and_active_synchro)

        # v_layout_service.addWidget(self.fram_activate_synchro)


        self.fram_activate =  QFrame()
        self.layout_ = QVBoxLayout(self.fram_activate)
        self.label = QLabel("Entrez votre clé d'activation :")
        self.key_input = QLineEdit()
        self.btn_verify = QPushButton("Vérifier la clé")
        self.btn_verify.setCursor(Qt.PointingHandCursor)

        self.btn_verify.setStyleSheet("""
        QPushButton {
            text-align: center;
            padding: 5px;
            min-width: 120px;
            color: #007bff; 
            border: 1px solid #007bff; 
            border-radius: 5px; 
            font-size: 13pt;
        }
        QPushButton:hover { 
            color: #fff; 
            background-color: #007bff;
        }
""")
        
        url_copy = base_url  # pour geler la valeur
        self.btn_verify.clicked.connect(lambda: self.verifier_cle(url_copy))
         

        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.key_input)
        self.layout_.addWidget(self.btn_verify)

        main_layout.addLayout(v_layout_service)
        layout.addLayout(body_layout)
        if not is_license_valid():
            layout.addWidget(self.fram_activate)
        self.setLayout(layout)

    def verifier_cle(self, url):
        user_input_key = self.key_input.text().strip()
        mac = get_mac_address()  # Exemple: "4CCC6A3FA142"  '84:a6:c8:f3:d5:bc'#
        expiration_date = 30
        # user_input_key = "ABCD-EFGH-IJKL-MNOP"
        if verify_activation_key_graphic(provided_key=user_input_key, mac_address=mac, days=expiration_date, url=url):
            expiration_date_ =(datetime.utcnow() + timedelta(days=expiration_date)).strftime("%Y-%m-%d") #datetime.utcnow() + timedelta(days=expiration_date).strftime("%Y-%m-%d")
            self.fram_activate.setHidden(True)
            QMessageBox.information(self, "Succès", f"Clé valide. Expire le {expiration_date_}")
            print(f"✅ Clé valide. mac {mac}")
        else:
            QMessageBox.critical(self, "Erreur", "Clé invalide ou expirée.")
            print(f"❌ Clé invalide. mac {mac}") 

    def get_service_status(self, service_name):
        """Vérifie si un service est en cours d'exécution."""
        try:
            result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True)
          #   print(result)
            return "RUNNING" in result.stdout
        except Exception:
            return False  # Si erreur, considérer comme arrêté

    def toggle_service(self, service_name, button, checked):
        """Démarre ou arrête un service."""
        if checked:
            subprocess.run(["net", "start", service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            button.setText("ON")
        else:
            subprocess.run(["net", "stop", service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            button.setText("OFF")

        # Mettre à jour le style du bouton
        button.setStyleSheet(self.get_button_style(checked))

    def get_button_style(self, active):
        """Retourne le style du bouton ON/OFF sans transition."""
        return """
            QPushButton {
                border-radius: 8px;
                padding: 5px;
                font-size: 13pt;
                color: %s;
            }
            QPushButton:checked {
               color: %s;
               font-weight: bold;
            }
        """ % ("#ff4d4d" if not active else "#4CAF50", "#4CAF50" if active else "#ff4d4d")
          
    def confirm_close(self):
        """Affiche une boîte de dialogue pour confirmer la fermeture."""
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment fermer l'application ?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    # Permettre le déplacement de la fenêtre en cliquant sur la barre de titre
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 40:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def attach_php(self, layouts):
        """Initialisation de l'interface."""

        self.server_label = QLabel()

        layouts.addWidget(self.server_label)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.start_button = QPushButton("Démarrer")
        self.stop_button = QPushButton("Arrêter")
        if not self.is_php_running():
            self.buttons_layout.setContentsMargins(9,0,9,0)
            self.start_button.setStyleSheet("color: #4CAF50; font-size: 13pt; padding: 5px; border-radius: 5px;")
            self.stop_button.setHidden(True)
            self.start_button.clicked.connect(self.start_php)
            self.buttons_layout.addWidget(self.start_button)
        else:
            self.stop_button.setStyleSheet("color: #FF4D4D; font-size: 13pt; padding: 5px; border-radius: 5px;")
            self.start_button.setHidden(True)
            self.stop_button.clicked.connect(self.stop_php)
            self.buttons_layout.addWidget(self.stop_button)

        layouts.addLayout(self.buttons_layout)

        self.update_php_status()

    def is_php_running(self, port=8080):
        """Vérifie si PHP fonctionne sur le port donné."""
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            return f":{port}" in result.stdout
        except Exception:
            return False

    def update_php_status(self):
        """Mise à jour du texte et de la couleur du label selon l'état du serveur PHP."""
        if self.is_php_running():
            self.server_label.setText("Le server est en cours d'exécution")
            self.server_label.setStyleSheet("color: #4CAF50; font-size: 14pt; ")
            self.start_button.setEnabled(False)  # Désactive le bouton Démarrer
            self.stop_button.setEnabled(True)  # Active le bouton Arrêter
        else:
            self.server_label.setText("Le server est arrêté")
            self.server_label.setStyleSheet("color: #FF4D4D; font-size: 13pt;")
            self.start_button.setEnabled(True)  # Active le bouton Démarrer
            self.stop_button.setEnabled(False)  # Désactive le bouton Arrêter

    def start_php(self):
        """Démarre le serveur PHP."""
        try:
            cwds=os.path.join(os.getcwd(), 'nginx','html','api')
            process = subprocess.Popen(
                    ["php", "artisan", "serve", "--host", Ip_manager().get_server_ip(), "--port", "8080"],
                    cwd=cwds, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
                    # Écrit le PID dans un fichier
            with open("php_server.pid", "w") as pid_file:
                pid_file.write(str(process.pid))
                self.update_php_status()  # Met à jour l'état après le démarrage
        except Exception as e:
            print(f"Erreur lors du démarrage de PHP: {e}")

    def stop_php(self):
        """Arrête le serveur PHP."""
        try:
            if os.path.exists("php_server.pid"):
                with open("php_server.pid", "r") as pid_file:
                    pid = pid_file.read().strip()

                subprocess.run(["taskkill", "/PID", pid, "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove("php_server.pid")
                self.update_php_status()
            else:
                print("Aucun fichier PID trouvé. Le serveur n'a peut-être pas été lancé depuis cette app.")
        except Exception as e:
            print(f"Erreur lors de l'arrêt du serveur PHP artisan: {e}")



    def authorization(self, layout, client_data, url):
        groupe_box = QGroupBox("Client Authorization")
        groupe_box.setStyleSheet("""
                                  QLabel{font-size:12pt}
            QGroupBox {
                font-size: 12pt;
                color: #333;
                border: 1px solid #777;
                border-radius: 5px;
                margin-top: 15px;
                padding: 4px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0px;
                color: #0078D7;
            }
        """)

        main_layout = QVBoxLayout(groupe_box)
        main_layout.setContentsMargins(2, 0, 2, 0)
        self.status_label = QLabel("")
        # main_layout.addWidget(self.status_label)
        
        # Section de contrôle refresh
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        # Bouton refresh manuel
        self.btn_manual_refresh = QPushButton("Manual Refresh")
        self.btn_manual_refresh.setStyleSheet("font-size: 12pt; padding: 4px;")
        self.btn_manual_refresh.clicked.connect(lambda: self.refresh_client_data(url))
        
        # Contrôle auto-refresh
        self.auto_refresh_toggle = QCheckBox("Auto Refresh (30s)")
        self.auto_refresh_toggle.setStyleSheet("font-size: 12pt;")
        self.auto_refresh_toggle.stateChanged.connect(self.toggle_auto_refresh)

        self.auto_refresh_toggle.setStyleSheet("""
            QCheckBox {
                font-size: 12pt;
                color: #999;
            }
            QCheckBox::indicator:checked {
                background-color: #0078D7;
                border: 1px solid #fff;
            }
                                               
            QCheckBox::indicator:unchecked {
                background-color: #fff;
                border: 1px solid #777;
            }
        """)

        self.btn_manual_refresh.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 12pt;
                width:150px
            }
                                              
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)

        
        control_layout.addWidget(self.btn_manual_refresh)
        control_layout.addStretch()
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        control_layout.addWidget(self.auto_refresh_toggle)
        
        # Zone des clients
        self.client_scroll = QScrollArea()
        self.client_widget = QWidget()
        self.client_layout = QVBoxLayout(self.client_widget)
        self.client_layout.setContentsMargins(10,0,0,10)
        self.client_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.client_layout.setSpacing(2)
        # self.client_widget.setStyleSheet("""background:#444;border-bottom:1px solid #555""")
        
        self.client_scroll.setWidgetResizable(True)
        self.client_scroll.setWidget(self.client_widget)
        
        main_layout.addWidget(control_frame)
        main_layout.addWidget(self.client_scroll)
        
        # Timer pour auto-refresh
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.setInterval(30000)  # 30 secondes
        self.auto_refresh_timer.timeout.connect(lambda: self.refresh_client_data(url))
        
        self.populate_clients(client_data, url)
        
        layout.addWidget(groupe_box)


    def populate_clients(self, client_data, url):
        # Nettoyer l'ancien contenu
        # print(f"client_data, urlclient_data, urlclient_data, url  {client_data, url}")
        for i in reversed(range(self.client_layout.count())): 
            self.client_layout.itemAt(i).widget().setParent(None)
        
        if client_data:
            for client in client_data:
                client_frame = QFrame()
                frame_layout = QHBoxLayout(client_frame)
                frame_layout.setContentsMargins(0,0,0,3)
                frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

                # Info client
                info_layout = QVBoxLayout()
                info_layout.setContentsMargins(0,0,0,0)
                info_layout.setSpacing(0)
                label_name = QLabel(client.get("client_name", "Unknown Device"))
                label_mac = QLabel(client.get("client_mac", "00:00:00:00:00:00"))
                
                label_name.setStyleSheet("font-size: 13pt; font-weight: bold;")
                label_mac.setStyleSheet("font-size: 12pt; color: #999;height:20px")
                
                info_layout.addWidget(label_name)
                info_layout.addWidget(label_mac)
                
                # Bouton d'autorisation
                btn_auth = QPushButton()
                btn_auth.setCheckable(True)
                btn_auth.setChecked(client.get('authorisation', 0) == 1)
                self.update_auth_button_style(btn_auth)
                
                btn_auth.clicked.connect(partial(
                    self.toggle_authorization,
                    client.get("id"),
                    url,
                    btn_auth
                ))
                
                frame_layout.addLayout(info_layout)
                frame_layout.addWidget(btn_auth)
                
                self.client_layout.addWidget(client_frame)

  
    def update_auth_button_style(self, button):
        state = "Authorized" if button.isChecked() else "Blocked"
        color = "#4CAF50" if button.isChecked() else "#F44336"
        
        button.setText(state)
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 12pt;
                min-width: 80px;
                padding: 6px;
                color: white;
                background-color: {color};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {color}AA;
            }}
        """)


    def toggle_auto_refresh(self, state):
        if self.auto_refresh_toggle.isChecked():
            self.auto_refresh_timer.start()
            self.btn_manual_refresh.setEnabled(False)
            self.status_label.setText("🔄 Auto-refresh activé")
        else:
            self.auto_refresh_timer.stop()
            self.btn_manual_refresh.setEnabled(True)
            self.status_label.setText("⏸️ Auto-refresh désactivé")

        #QTimer.singleShot(113000, lambda: self.status_label.setText(""))  # Efface le message après 3s


    def refresh_client_data(self, url):
        try:
            status_code = 500
            from .direct_request import get_authorisation,load_data
            direct_request = load_data().get('value',0) if load_data() else None
            
            if direct_request:
                response_data, status = get_authorisation()
                status_code = status
            else:
                data = requests.get(url, timeout=35,verify="C:/Program Files/ecole-serve/certspath/ca.pem")
                response_data = data.json()
                status_code = data.status_code

            if status_code == 200: 
                client_data = response_data['data_client']
                self.populate_clients(client_data, url)
            else:
                self.show_error_message("Refresh failed")
                print(response_data)
        except Exception as e:
            print(f"Refresh error: {str(e)}")
            self.show_error_message("Connection error")

    def show_error_message(self, text):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(text)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()
 

    def get_server_cert_content(self, cert_path):
        """Lit le fichier cert et le renvoie en base64 ou texte brut"""
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


    # Exemple d’utilisation
    
    

    # Envoyer via API (dans un champ "server_cert")
    # payload = {
    #     "id": client_id,
    #     "server_cert": b64  # plus sûr que brut
    # }
    # response = requests.post(url, json=payload, headers=headers, timeout=15)



    def toggle_authorization(self, client_id, url, button):
        cert_path = r"C:/Program Files/ecole-serve/certspath/ca.pem" 
        pem, b64 = self.get_server_cert_content(cert_path)
        payload = {"id": client_id, "certi_key": b64}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.token_access:
            headers['X-Admin-Token'] = self.token_access
            

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=45,verify="C:/Program Files/ecole-serve/certspath/ca.pem")
            response_data = response.json()
            
            if response.status_code == 200:
                # Nouvelle autorisation renvoyée par l'API
                new_status = response_data.get('authorisation', 0)
                if new_status == 1:
                    self.update_auth_button_style(button)
                    button.setText("Authorized")
                else:
                    button.setText("Not Authorized")
                    button.setStyleSheet("""
                        QPushButton {
                            font-size: 12pt;
                            color: white;
                            background-color: red;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 5px;
                        }
                    """)
                # print(response_data)
                return response_data
            if response.status_code == 422:
                if response_data and "Authorization" in response_data and response_data["Authorization"] == False:
                    self.request_access_for_delete()
                else: 
                    # button.setChecked(not new_state)
                    self.show_error_message("Update failed")
                    print("Erreur:", response_data)
                    return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")


    def request_access_for_delete(self):
        self.dialog_delete = QDialog()
        self.dialog_delete.setModal(True) 
        self.dialog_delete.setWindowTitle("Confirmation requise")
        self.dialog_delete.setStyleSheet("""
            QDialog {
                        background: #fff;
                    }
            QComboBox, QLineEdit, QDateEdit{ width: 350px; min-height: 33px; max-height: 33px;border: 1px solid #999; border-radius:5px;padding-left:7px}
        QComboBox:hover,QComboBox:focus, QLineEdit:hover, QDateEdit:hover, QLineEdit:focus, QDateEdit:focus {
                    
                    border: 1px solid #007bff;
                            }
            QLabel,QComboBox,QLineEdit{font-size:13pt}
                QPushButton {
                        text-align: center;
                        padding: 5px;
                        min-width: 120px;
                        color: #007bff; 
                        border: 1px solid #007bff; 
                        border-radius: 5px; 
                        font-size: 13pt;
                    }
                    QPushButton:hover { 
                        color: #fff; 
                        background-color: #007bff;
                    }
            """)
        try:
            vh_layout_confirm = QVBoxLayout()

            self.frame_image = QFrame()
            self.layout_image = QVBoxLayout(self.frame_image)

            self.icon_path_lock = os.path.join(self.get_resource_path('Controllers'), 'lock.png') #self.get_path(os.path.join('assets', 'icons', 'lock.png'))
            pixmap = QPixmap(self.icon_path_lock)

            label = QLabel()
            # Fixer une taille spécifique si nécessaire, sinon le pixmap peut être vide
            label.setFixedSize(80, 80)  # exemple de taille
            pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.layout_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setPixmap(pixmap)
            self.layout_image.setContentsMargins(0,0,0,0)
            label.setStyleSheet("border-radius: 75px;")  # ça fonctionne uniquement si l'image est carrée
            self.layout_image.addWidget(label)


            self.frame_input_email = QFrame()
            self.layout_input_email = QVBoxLayout(self.frame_input_email)
            self.layout_input_email.setContentsMargins(0,0,0,0)
            self.frame_input_email.setContentsMargins(0,0,0,0)
            self.label_email = QLabel("Votre Email")
            self.layout_input_email.addWidget(self.label_email)

            self.input_email = QLineEdit() 
            self.layout_input_email.addWidget(self.input_email)

            # Frame for input
            self.frame_input = QFrame()
            self.layout_input = QVBoxLayout(self.frame_input)  
            self.layout_input.setContentsMargins(0,5,0,0)      
            self.frame_input.setContentsMargins(0,0,0,0)      
            self.label = QLabel("Mot de passe")
            self.layout_input.addWidget(self.label)
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.layout_input.addWidget(self.password_input)

            # Frame for button
            self.frame_buttons = QFrame()
            self.layout_buttons = QVBoxLayout(self.frame_buttons)
            self.layout_buttons.setContentsMargins(0,10,0,30)

            self.delete = QPushButton("Confirmer")
            self.delete.setCursor(Qt.PointingHandCursor)
            self.delete.clicked.connect(self.authorisation_status)
            self.layout_buttons.addWidget(self.delete)

            # Add frames to dialog layout
            vh_layout_confirm.addWidget(self.frame_image)
            vh_layout_confirm.addWidget(self.frame_input_email)
            vh_layout_confirm.addWidget(self.frame_input)
            vh_layout_confirm.addWidget(self.frame_buttons)
            vh_layout_confirm.setSpacing(4)
            self.dialog_delete.setLayout(vh_layout_confirm)
            self.dialog_delete.exec()
        except Exception as e:
            print('An exception occurred 5')
            print(f"------ : {e}")
            import traceback
            traceback.print_exc()


    def authorisation_status(self):
        email = self.input_email.text()
        password = self.password_input.text()
        log_url = f"{self.base__url}autorisation-access" 
        try:
            response = requests.post(
            log_url,
            json={
                'email':email,
                'password':password, 
                'permission':"Modifier personnel" 
                },
            timeout=50,verify="C:/Program Files/ecole-serve/certspath/ca.pem"
        )
            response_data = response.json()
            if response.status_code == 200:
                self.token_access=response_data['token']
                self.dialog_delete.close()
                QMessageBox.information(
                    None,
                    "Succès",
                    "Autorisation accordée, vous pouvez continuer."
                )
            else:
                print(response_data)
                if response_data and 'errors' in response_data:
                    errors = response_data['errors']
                    QMessageBox.critical(None, "Error", errors)
                # print('users not update')
        except Exception as e:
            print(f"------ : {e}")
            import traceback
            traceback.print_exc()

    def is_installed(self, program):
        try:
            if program == 'nginx':
              subprocess.run([program, "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            else:
                subprocess.run([program, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
           
            return True
        except FileNotFoundError:         
            return False
        except subprocess.CalledProcessError as e:
           
            return False


    def attach_services(self, layouts):
        self.layout__synchro = QVBoxLayout() 
        self.layout__synchro.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.btn_verify_synchro = QPushButton("Activer la synchronisation")
        self.btn_verify_synchro.setCursor(Qt.PointingHandCursor)
        self.layout__synchro.addWidget(self.btn_verify_synchro)
        self.btn_verify_synchro.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 5px;
                    width: 200px;
                    color: #007bff; 
                    border: 1px solid #007bff; 
                    border-radius: 5px; 
                    font-size: 13pt;
                }
                QPushButton:hover { 
                    color: #fff; 
                    background-color: #007bff;
                }
        """)
        self.btn_verify_synchro.clicked.connect(self.check_and_active_synchro)

        # v_layout_service.addWidget(self.fram_activate_synchro)
        layouts.addLayout(self.layout__synchro)

    def check_and_active_synchro(self):
        self.dialog_synchro = QDialog()
        self.dialog_synchro.setModal(True) 
        self.dialog_synchro.setWindowTitle("Synchronisation des données")

        if not self.is_installed('java'):
            QMessageBox.critical(None, "Warning", 'Impossible de continuer sans une installation de Java')
            return
        self.dialog_synchro.setStyleSheet("""
            QDialog {
                        background: #fff;
                    }
            QComboBox, QLineEdit, QDateEdit{ min-width: 400px; min-height: 33px; max-height: 35px;border: 1px solid #999; border-radius:5px;padding-left:7px}
            QComboBox:hover,QComboBox:focus, QLineEdit:hover, QDateEdit:hover, QLineEdit:focus, QDateEdit:focus {
                    
                    border: 1px solid #007bff;
                            }
            QLabel,QComboBox,QLineEdit{font-size:13pt}
                QPushButton {
                        text-align: center;
                        padding: 5px;
                        width: 150px;
                        color: #007bff; 
                        border: 1px solid #007bff; 
                        border-radius: 5px; 
                        font-size: 13pt;
                    }
                    QPushButton:hover { 
                        color: #fff; 
                        background-color: #007bff;
                    }
            """)
        
        vh_layout_confirm = QVBoxLayout()
        vh_layout_confirm.setAlignment(Qt.AlignmentFlag.AlignTop)

        
        public_key = self.load_public_key()

            # # Vérifier la config
            # sudo wg-quick down wg0
            # sudo wg-quick up wg0

            # # Voir l'état
            # sudo wg show

            # # Vérifier IP
            # ip a


        commands = f"""
            # 1. Mettre à jour la liste des paquets
            sudo apt update

            # 2. Installer WireGuard
            sudo apt install wireguard -y

            # 3. Vérifier l’installation
            wg --version

            # 4. Créer le répertoire de configuration
            sudo mkdir -p /etc/wireguard
            cd /etc/wireguard

            # 5. Générer les clés privée et publique
            umask 077
            wg genkey | tee privatekey | wg pubkey > publickey

            # 6. Créer le fichier de configuration (exemple wg0.conf)
            sudo nano /etc/wireguard/wg0.conf

            # Exemple wg0.conf :
            [Interface]
            Address = 10.10.0.1/24
            PrivateKey = <clé_privée>
            ListenPort = 51820

            [Peer]
            PublicKey = {public_key}
            AllowedIPs = 10.10.0.2/32

            # 7. Activer le forwarding IP
            sudo sysctl -w net.ipv4.ip_forward=1
            echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

            # 8. Démarrer et activer le service WireGuard
            sudo systemctl start wg-quick@wg0
            sudo systemctl enable wg-quick@wg0

            # 9. Vérifier l’état
            sudo systemctl status wg-quick@wg0

            =================================================
            ip link show wg0   ,    wg-quick down wg0     
            ,systemctl start wg-quick@wg0, 
             systemctl status wg-quick@wg0,  
             systemctl enable wg-quick@wg0
            =================================================
 

            # 10. Tester la configuration
            wg show
        """

        self.frame_input_commande_ = QFrame()
        self.layout_input_commande = QVBoxLayout(self.frame_input_commande_)
        self.text_edit_install_wireguard = QTextEdit()
        self.text_edit_install_wireguard.setPlainText(commands)
        self.text_edit_install_wireguard.setReadOnly(True)
        self.layout_input_commande.addWidget(self.text_edit_install_wireguard)


        self.frame_input_public_key = QFrame()
        self.layout_input_public_key = QVBoxLayout(self.frame_input_public_key)
        self.layout_input_public_key.setContentsMargins(0,0,0,0)
        self.frame_input_public_key.setContentsMargins(0,0,0,0)
        self.label_public_key = QLabel("Votre clé public distante")
        self.layout_input_public_key.addWidget(self.label_public_key)
        self.input_public_key = QLineEdit() 
        self.layout_input_public_key.addWidget(self.input_public_key)

        self.frame_input_endpoint = QFrame()
        self.layout_input_endpoint = QVBoxLayout(self.frame_input_endpoint)
        self.layout_input_endpoint.setContentsMargins(0,0,0,0)
        self.frame_input_endpoint.setContentsMargins(0,0,0,0)
        self.label_endpoint = QLabel("Votre endpoint")
        self.layout_input_endpoint.addWidget(self.label_endpoint)
        self.input_endpoint = QLineEdit() 
        self.layout_input_endpoint.addWidget(self.input_endpoint)

        self.frame_input_public_local_key = QFrame()
        self.layout_input_public_local_key = QVBoxLayout(self.frame_input_public_local_key)
        self.layout_input_public_local_key.setContentsMargins(0,0,0,0)
        self.frame_input_public_local_key.setContentsMargins(0,0,0,0)
        self.label_public_local_key = QLabel("Votre clé public local")
        self.layout_input_public_local_key.addWidget(self.label_public_local_key) 
        self.input_public_local_key = QLineEdit() 
        self.input_public_local_key.setReadOnly(True)

        # public_key = self.load_public_key()
        self.continuer = QPushButton("Continuer")
        if public_key:
            self.input_public_local_key.setText(public_key)
            self.continuer.setHidden(True)
        self.layout_input_public_local_key.addWidget(self.input_public_local_key)

        self.input_public_local_key = CopyOnFocusLineEdit(self.input_public_local_key)
        # self.layout_input_public_local_key.addWidget(self.input_public_local_key)


        self.frame_buttons = QFrame()
        self.layout_buttons = QVBoxLayout(self.frame_buttons)
        self.layout_buttons.setContentsMargins(0,10,0,20)
        # self.continuer = QPushButton("Continuer")
        self.continuer.setCursor(Qt.PointingHandCursor)
        self.layout_buttons.addWidget(self.continuer)
        self.layout_buttons.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.continuer.clicked.connect(self.next_step_to_wireGuard)

        self.frame_buttons_next = QFrame()
        self.layout_buttons_next = QVBoxLayout(self.frame_buttons_next)
        self.layout_buttons_next.setContentsMargins(0,10,0,20)
        self.continuer_next = QPushButton("Suivant")
        self.continuer_next.setCursor(Qt.PointingHandCursor)
        self.layout_buttons_next.addWidget(self.continuer_next)
        self.layout_buttons_next.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.continuer_next.clicked.connect(self.next_step_to_symmetrics)

        vh_layout_confirm.addWidget(self.frame_input_commande_)
        vh_layout_confirm.addWidget(self.frame_input_public_key)
        vh_layout_confirm.addWidget(self.frame_input_endpoint)
        vh_layout_confirm.addWidget(self.frame_input_public_local_key)
        vh_layout_confirm.addWidget(self.frame_buttons)

        if self.load_public_key():
            vh_layout_confirm.addWidget(self.frame_buttons_next)
        
        vh_layout_confirm.setSpacing(8)
        self.dialog_synchro.setLayout(vh_layout_confirm)

        if not self.is_installed('wg'):


            reply = QMessageBox.question(None, "WireGuard manquant", 
                                  "WireGuard n'est pas installé. Voulez-vous l'installer maintenant ?", 
                                  QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes: 
                pass
                # manager = WireGuardWindowsManager() peer_public_key="CLE_PUBLIQUE_SERVEUR",
                # manager.setup_wireguard( endpoint="example.com:51820")
            else:
                QMessageBox.critical(None, "Erreur", "Impossible de continuer sans WireGuard.")
                return
        


        # self.dialog_synchro.setLayout(vh_layout_confirm)
        self.dialog_synchro.exec()

    def next_step_to_symmetrics(self):
        ips = self.extract_ips_from_conf(self.WG_CONF_PATH)
        reachable = any(self.ping_ip(ip) for ip in ips)
        if reachable:
            self.install_symmetricds_if_needed()
            print(f"IPs trouvées: {ips}, Accessible? {reachable}")
        else:
            QMessageBox.critical(None, "Erreur", "Erreur de configuration.")
            return

    # Exemple d'utilisation
    def load_public_key(self):
        """Lire la clé publique si elle existe"""
        PUBLIC_KEY_FILE = r"C:\ProgramData\WireGuard\Configurations\publickey.txt"
        if os.path.exists(PUBLIC_KEY_FILE):
            with open(PUBLIC_KEY_FILE, "r") as f:
                return f.read().strip()
        return None
    
    def is_valid_public_key(self, key: str) -> bool:
        try:
            decoded = base64.b64decode(key)
            return len(decoded) == 32
        except Exception as e: 
            import traceback
            traceback.print_exc()
            return False

    def is_valid_endpoint(self, endpoint: str) -> bool:
        try:
            host, port = endpoint.split(":")
            port = int(port)
            if not (1 <= port <= 65535):
                return False
            socket.gethostbyname(host)  # Vérifie que le host est résolvable
            return True
        except Exception:
            return False


    def next_step_to_wireGuard(self):
        peer_public_key =self.input_public_key.text().strip()# "CLE_PUBLIQUE_SERVEUR"
        endpoint = self.input_endpoint.text().strip() # "example.com:51820"

        if not self.is_valid_public_key(peer_public_key):
            QMessageBox.critical(None, "Erreur", "Clé publique invalide.")
            return

        if not self.is_valid_endpoint(endpoint):
            QMessageBox.critical(None, "Erreur", "Endpoint invalide ou non joignable.")
            return
        
        # manager = WireGuardWindowsManager() 
        # manager.setup_wireguard(peer_public_key=peer_public_key, endpoint=endpoint)
        self.input_public_local_key.setText(peer_public_key)
        self.continuer.setHidden(True)

            # Exemple d'utilisation
        # ips = self.extract_ips_from_conf(self.WG_CONF_PATH)
        # reachable = any(self.ping_ip(ip) for ip in ips)
        # if reachable:
        #     self.install_symmetricds_if_needed()
        # print(f"IPs trouvées: {ips}, Accessible? {reachable}")


    def extract_ips_from_conf(self, conf_path):
        ips = []
        if os.path.exists(conf_path):
            with open(conf_path, "r") as f:
                for line in f:
                    if line.strip().startswith("Endpoint"):
                        # Récupère l'IP avant les ":"
                        ip = line.split("=",1)[1].strip().split(":")[0]
                        ips.append(ip)
                    elif line.strip().startswith("AllowedIPs"):
                        # Peut contenir des plages IP (on peut les ignorer ou ping 1 IP)
                        ip = line.split("=",1)[1].strip().split("/")[0]
                        ips.append(ip)

                    elif line.strip().startswith("Address"):
                        # Peut contenir des plages IP (on peut les ignorer ou ping 1 IP)
                        ip = line.split("=",1)[1].strip().split("/")[0]
                        ips.append(ip)
        return ips

    def ping_ip(self, ip):
        try:
            result = subprocess.run(["ping", "-n", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return "TTL=" in result.stdout  # Si TTL présent, la cible répond
        except:
            QMessageBox.critical(None, "Erreur", "Endpoint invalide ou non joignable.")
            return False
 

    def install_symmetricds_if_needed(self):
        sym_dir = r"C:\Program Files\ecole-serve\symmetricds"

        if not os.path.exists(sym_dir):
            print("Téléchargement de SymmetricDS...")
            url = "https://sourceforge.net/projects/symmetricds/files/latest/download"
            
            # Téléchargement dans un fichier temporaire
            zip_path = os.path.join(tempfile.gettempdir(), "symmetricds.zip")
            urllib.request.urlretrieve(url, zip_path)

            print("Extraction en cours...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Vérifier le premier dossier du zip
                root_folder = zip_ref.namelist()[0].split('/')[0]

                # Extraire d'abord dans un dossier temporaire
                temp_extract = os.path.join(tempfile.gettempdir(), "sym_extract")
                if not os.path.exists(temp_extract):
                    os.makedirs(temp_extract)
                zip_ref.extractall(temp_extract)

            # Copier le contenu du sous-dossier vers sym_dir
            source_folder = os.path.join(temp_extract, root_folder)
            os.makedirs(sym_dir, exist_ok=True)

            for item in os.listdir(source_folder):
                s = os.path.join(source_folder, item)
                d = os.path.join(sym_dir, item)
                if os.path.isdir(s):
                    import shutil
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            symmetricds_path = r"C:\Program Files\ecole-serve\symmetricds"

            # Ajout variable SYMMETRICDS_HOME
            subprocess.run([
                "setx", "SYMMETRICDS_HOME", symmetricds_path, "/M"
            ])

            # Mise à jour du PATH
            current_path = os.environ.get("PATH", "")
            # if symmetricds_path not in current_path:
            #     subprocess.run([
            #         "setx", "PATH", f"{current_path};{symmetricds_path}", "/M"
            #     ])

                # print("✅ SYMMETRICDS_HOME ajouté et PATH mis à jour.")
            # Exécuter la fonction
            self.certificat_keyston_for_symetricds()
            print(f"Installation terminée dans : {sym_dir}")
            self.configure_setenv_bat()
            self.add_ssl_lines_to_setenv()
        else:
            print("SymmetricDS déjà installé.") 



    def install_symmetricds_if_needed111():
        sym_dir = r"C:\Program Files\ecole-serve\symmetricds"
        if not os.path.exists(sym_dir):
            print("Téléchargement de SymmetricDS...")
            url = "https://sourceforge.net/projects/symmetricds/files/latest/download"
            zip_path = os.path.join(os.getenv("TEMP"), "symmetricds.zip")
            urllib.request.urlretrieve(url, zip_path)

            print("Extraction...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extraire dans un dossier temporaire
                temp_extract_dir = os.path.join(os.getenv("TEMP"), "symmetricds_temp")
                zip_ref.extractall(temp_extract_dir)

            # Trouver le dossier racine extrait (ex: symmetric-server-3.14.x)
            extracted_root = None
            for item in os.listdir(temp_extract_dir):
                full_path = os.path.join(temp_extract_dir, item)
                if os.path.isdir(full_path) and "symmetric" in item:
                    extracted_root = full_path
                    break

            if extracted_root is None:
                raise Exception("Impossible de trouver le dossier SymmetricDS extrait.")

            # Déplacer le contenu directement dans sym_dir
            os.makedirs(sym_dir, exist_ok=True)
            for item in os.listdir(extracted_root):
                s = os.path.join(extracted_root, item)
                d = os.path.join(sym_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

            print(f"SymmetricDS installé dans {sym_dir}")

            # Nettoyage
            os.remove(zip_path)
            shutil.rmtree(temp_extract_dir)

        else:
            print("SymmetricDS déjà installé.")



    def certificat_keyston_for_symetricds(self):
        # Répertoires
        symmetricds_path = r"C:\Program Files\ecole-serve\symmetricds"
        certs_path = os.path.join(symmetricds_path, "certs")
        mysql_certs_path = r"C:\Program Files\ecole-serve\mysql-8.0.41-winx64\certs"
        
        # Créer le dossier certs si inexistant
        os.makedirs(certs_path, exist_ok=True)
        
        # Fichiers et mots de passe
        ca_cert = os.path.join(mysql_certs_path, "ca.pem")
        ca_key = os.path.join(mysql_certs_path, "ca-key.pem")
        keystore_file = os.path.join(certs_path, "keystore.p12")
        truststore_file = os.path.join(certs_path, "truststore.p12")
        keystore_password = "@@@@@@@@"  # à remplacer par ton mot de passe
        alias_name = "symmetricds"
        
        # Commandes
        openssl_cmd = [
            "openssl", "pkcs12", "-export",
            "-in", ca_cert,
            "-inkey", ca_key,
            "-out", keystore_file,
            "-name", alias_name,
            "-passout", f"pass:{keystore_password}"
        ]
        
        keytool_cmd = [
            "keytool", "-importcert",
            "-file", ca_cert,
            "-keystore", truststore_file,
            "-storetype", "PKCS12",
            "-alias", f"{alias_name}-trust",
            "-storepass", keystore_password,
            "-noprompt"
        ]
        
        try:
            print("🔐 Génération du keystore avec OpenSSL...")
            subprocess.run(openssl_cmd, check=True)
            
            print("🔐 Génération du truststore avec keytool...")
            subprocess.run(keytool_cmd, check=True)
            
            print("✅ Keystore et Truststore générés avec succès dans :", certs_path)
        except subprocess.CalledProcessError as e:
            print("❌ Erreur lors de la génération :", e)



    
    def config_engine_win_node_properties(self):
        pass

    def config_win_node_properties(self):
        pass
 


    def configure_setenv_bat(self):
        """
        Configure automatiquement setenv.bat existant dans SYMMETRICDS_HOME\bin
        avec JAVA_HOME, PATH, SYM_HOME et certificats SSL.
        """
        # Définir les chemins globaux
        SYMMETRICDS_HOME = r"C:\Program Files\ecole-serve\symmetricds"
        JAVA_HOME = r"C:\Program Files\Java\jdk-17"
        KEYSTORE_PASS = "@@@@@@@@"
        TRUSTSTORE_PASS = "@@@@@@@@"
        bin_dir = os.path.join(SYMMETRICDS_HOME, "bin")
        setenv_path = os.path.join(bin_dir, "setenv.bat")

        if not os.path.exists(setenv_path):
            raise FileNotFoundError(f"{setenv_path} n'existe pas !")

        with open(setenv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        sym_home_set = False
        path_set = False
        java_set = False
        keystore_section_added = False

        for line in lines:
            stripped = line.strip()

            # Ajouter SYM_HOME juste après pushd "%~dp0.."
            if not sym_home_set and stripped.startswith("pushd"):
                new_lines.append(line.rstrip("\n"))
                new_lines.append(f"set SYM_HOME=%CD%\n")
                new_lines.append("popd\n")
                sym_home_set = True
                continue

            # Ajouter PATH avec bin
            if sym_home_set and not path_set and stripped.startswith("set PATH"):
                new_lines.append(f"set PATH=%PATH%;%SYM_HOME%\\bin")
                path_set = True

            # Configurer SYM_JAVA
            if not java_set and stripped.startswith("set SYM_JAVA"):
                new_lines.append(f'set SYM_JAVA=java\n')
                new_lines.append(f'if /i NOT "%JAVA_HOME%" == "" set SYM_JAVA=%JAVA_HOME%\\bin\\java\n')
                new_lines.append(f'set CLASSPATH=%SYM_HOME%\patches;%SYM_HOME%\patches\*;%SYM_HOME%\lib\*;%SYM_HOME%\web\WEB-INF\lib\*\n')
                new_lines.append(f'set PATH=%PATH%;%SYM_HOME%\lib\n')
                java_set = True
                continue

            # Ajouter la section keystore/SSL si on rencontre le commentaire
            # if not keystore_section_added and stripped.startswith(":: Chemins des keystores"):
            #     new_lines.append(f':: Chemins des keystores')
            #     new_lines.append(f'set "TRUST_STORE={SYMMETRICDS_HOME}\\certs\\truststore.p12"')
            #     new_lines.append(f'set "KEY_STORE={SYMMETRICDS_HOME}\\certs\\keystore.p12"')
            #     new_lines.append(f':: Options SSL Java')
            #     new_lines.append(f'set "JAVA_OPTS=-Djavax.net.ssl.trustStore=%TRUST_STORE%"')
            #     new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.trustStorePassword={TRUSTSTORE_PASS}"')
            #     new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.keyStore=%KEY_STORE%"')
            #     new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.keyStorePassword={KEYSTORE_PASS}"')
            #     keystore_section_added = True
            #     continue

            # Sinon on copie la ligne telle quelle
            new_lines.append(line.rstrip("\n"))

        # Réécrire le fichier
        with open(setenv_path, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

        print(f"setenv.bat configuré automatiquement dans {bin_dir}")
 


    def add_ssl_lines_to_setenv(self):
        SYMMETRICDS_HOME = r"C:\Program Files\ecole-serve\symmetricds"
        KEYSTORE_PASS = "@@@@@@@@"
        TRUSTSTORE_PASS = "@@@@@@@@"

        bin_dir = os.path.join(SYMMETRICDS_HOME, "bin")
        setenv_path = os.path.join(bin_dir, "setenv.bat")

        if not os.path.exists(setenv_path):
            raise FileNotFoundError(f"{setenv_path} n'existe pas !")

        with open(setenv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        added_ssl = False

        for line in lines:
            new_lines.append(line.rstrip("\n"))

            # Ajouter les 4 lignes SSL après la ligne contenant "-Djava.io.tmpdir"
            if not added_ssl and "Djava.net.preferIPv4Stack" in line:
                new_lines.append(f'-Djavax.net.ssl.trustStore="%{SYMMETRICDS_HOME}%\\certs\\keystore.p12" ^')
                new_lines.append(f'-Djavax.net.ssl.trustStorePassword={KEYSTORE_PASS} ^')
                new_lines.append(f'-Djavax.net.ssl.trustStore="%{SYMMETRICDS_HOME}%\\certs\\truststore.p12" ^')
                new_lines.append(f'-Djavax.net.ssl.trustStorePassword={TRUSTSTORE_PASS} ^')
                added_ssl = True

        # Réécrire le fichier
        with open(setenv_path, "w", encoding="utf-8") as f:
            for l in new_lines:
                f.write(l + "\n")

        print("Les lignes SSL ont été ajoutées avec succès à setenv.bat")
 





    def configure_setenv_batrrrr(sym_home, java_home, key_pass="@@@@@@@@", trust_pass="@@@@@@@@"):
        """
        Édite le setenv.bat existant pour ajouter JAVA_HOME et les certificats.
        Conserve tout le reste du fichier intact.
        """
        setenv_path = os.path.join(sym_home, "bin", "setenv.bat")

        if not os.path.exists(setenv_path):
            raise FileNotFoundError(f"{setenv_path} n'existe pas !")

        with open(setenv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        new_lines = []
        for line in lines:
            stripped = line.strip()
            # Mettre à jour JAVA_HOME
            if stripped.startswith("set SYM_JAVA"):
                new_lines.append(f'set SYM_JAVA=java\n')
                new_lines.append(f'if /i NOT "%JAVA_HOME%" == "" set SYM_JAVA={java_home}\\bin\\java\n')
            # Mettre à jour les chemins de keystore/truststore
            elif stripped.startswith(":: Chemins des keystores"):
                new_lines.append(f':: Chemins des keystores')
                new_lines.append(f'set "TRUST_STORE={sym_home}\\certs\\truststore.p12"')
                new_lines.append(f'set "KEY_STORE={sym_home}\\certs\\keystore.p12"')
            elif stripped.startswith(":: Options SSL Java"):
                new_lines.append(f':: Options SSL Java')
                new_lines.append(f'set "JAVA_OPTS=-Djavax.net.ssl.trustStore=%TRUST_STORE%"')
                new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.trustStorePassword={trust_pass}"')
                new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.keyStore=%KEY_STORE%"')
                new_lines.append(f'set "JAVA_OPTS=%JAVA_OPTS% -Djavax.net.ssl.keyStorePassword={key_pass}"')
            else:
                new_lines.append(line.rstrip("\n"))

        # Réécrire le fichier
        with open(setenv_path, "w", encoding="utf-8") as f:
            for line in new_lines:
                f.write(line + "\n")

        print(f"setenv.bat mis à jour avec JAVA_HOME et certificats dans {sym_home}\\bin")

    # Exemple d'utilisation
    # configure_setenv_bat(
    #     sym_home=r"C:\Program Files\ecole-serve\symmetricds",
    #     java_home=r"C:\Program Files\Java\jdk-17"
    # )



 
from PySide6.QtGui import QClipboard
# from PySide6.QtCore import Qt

class CopyOnFocusLineEdit:
    def __init__(self, lineEdit):
        # super().__init__(*args, **kwargs)
        self.lineEdit=lineEdit
        self.lineEdit.setReadOnly(True)  # Rend le champ en lecture seule

    def focusInEvent(self, event):
        self.lineEdit.focusInEvent(event)
        # Copie automatiquement le contenu dans le presse-papier
        clipboard = QApplication.clipboard()
        clipboard.setText(self.lineEdit.text(), QClipboard.Mode.Clipboard)
 
import ctypes
import datetime
from PySide6.QtWidgets import QMessageBox
import os, subprocess, ctypes, datetime
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QMessageBox, QProgressDialog


class WireGuardWindowsManager:
    def __init__(self):
        self.config_name = "wg0"
        self.config_dir = os.path.join(os.getenv("ProgramData"), "WireGuard", "Configurations")
        self.wg_exe = r"C:\Program Files\WireGuard\wg.exe"
        self.ui_exe = r"C:\Program Files\WireGuard\wireguard.exe"
        self.port = 51820

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def log(self, message):
        log_file = os.path.join(self.config_dir, "manager.log")
        os.makedirs(self.config_dir, exist_ok=True)
        with open(log_file, "a") as f:
            f.write(f"[{datetime.datetime.now()}] {message}\n")

    def is_installed(self):
        return os.path.exists(self.wg_exe) and os.path.exists(self.ui_exe)

    def install_wireguard_async(self):
        self.progress = QProgressDialog("Téléchargement et installation en cours...", None, 0, 0)
        self.progress.setWindowTitle("WireGuard")
        self.progress.setCancelButton(None)
        self.progress.setWindowModality(Qt.ApplicationModal)
        self.progress.show()

        self.installer_thread = WireGuardInstaller()
        self.installer_thread.finished.connect(self.on_install_finished)
        self.installer_thread.start()

    def save_public_key(self, public_key):
        PUBLIC_KEY_FILE = os.path.join(self.config_dir, "publickey.txt")
        os.makedirs(os.path.dirname(PUBLIC_KEY_FILE), exist_ok=True)
        with open(PUBLIC_KEY_FILE, "w") as f:
            f.write(public_key)

    def generate_keys(self):
        try:
            private_key = subprocess.check_output([self.wg_exe, "genkey"], text=True).strip()
            public_key = subprocess.check_output(
                [self.wg_exe, "pubkey"], input=private_key, text=True
            ).strip()
            return private_key, public_key
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Échec de la génération des clés : {e}")
            return None, None

    def create_config(self, private_key, public_key, endpoint, dns="1.1.1.1"):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            config_path = os.path.join(self.config_dir, f"{self.config_name}.conf")

            config_content = f"""
                [Interface]
                PrivateKey = {private_key}
                Address = 10.10.0.2/24
               # DNS = {dns}
                ListenPort = {self.port}

                [Peer]
                PublicKey = {public_key}
                AllowedIPs = 10.10.0.0/0
                #Endpoint = {endpoint}
                PersistentKeepalive = 25
            """

            with open(config_path, "w") as f:
                f.write(config_content.strip())

            self.log(f"Config créée à {config_path}")
            return config_path
        except Exception as e:
            QMessageBox.critical(None, "Erreur", f"Impossible de créer le fichier de configuration : {e}")
            return None

    def open_firewall_port(self):
        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=WireGuard", "dir=in", "action=allow",
                "protocol=UDP", f"localport={self.port}"
            ], check=True)
            self.log("Port UDP ouvert dans le pare-feu")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(None, "Firewall", f"Échec d'ouverture du port UDP : {e}")

    def install_service(self, config_path):
        try:
            subprocess.run([self.ui_exe, "/installtunnelservice", config_path], check=True)
            service_name = f"WireGuardTunnel${self.config_name}"
            subprocess.run(["sc", "config", service_name, "start=auto"], check=True)
            subprocess.run(["sc", "start", service_name], check=True)
            QMessageBox.information(None, "Succès", "WireGuard installé comme service et démarré.")
            self.log(f"Service {service_name} installé et démarré")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(None, "Erreur", f"Échec de l'installation du service : {e}")

    def on_install_finished(self, success, message):
        self.progress.close()
        if success:
            QMessageBox.information(None, "Succès", message)
            QMessageBox.information(None, "Information", "Veuillez relancer l'application pour finaliser la configuration.")
        else:
            QMessageBox.critical(None, "Erreur", message)

    def setup_wireguard(self, endpoint=None):
        if not self.is_admin():
            QMessageBox.critical(None, "Permission refusée", "Veuillez exécuter l'application en tant qu'administrateur.")
            return

        if not self.is_installed():
            reply = QMessageBox.question(None, "WireGuard manquant",
                                          "WireGuard n'est pas installé. Voulez-vous l'installer maintenant ?",
                                          QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.install_wireguard_async()
            else:
                QMessageBox.critical(None, "Erreur", "Impossible de continuer sans WireGuard.")
                return

        private_key, public_key = self.generate_keys()
        if not private_key or not public_key:
            return
        self.save_public_key(public_key)

        config_path = self.create_config(private_key, public_key, endpoint)
        if config_path:
            self.open_firewall_port()
            self.install_service(config_path)


class WireGuardInstaller(QThread):
    finished = Signal(bool, str)

    def run(self):
        try:
            url = "https://download.wireguard.com/windows-client/wireguard-installer.exe"
            installer = os.path.join(os.getenv("TEMP"), "wireguard-installer.exe")

            subprocess.run(["powershell", "-Command", f"Invoke-WebRequest -Uri {url} -OutFile {installer}"], check=True)
            subprocess.run([installer, "/S"], check=True)
            self.finished.emit(True, "WireGuard a été installé avec succès.")
        except subprocess.CalledProcessError as e:
            self.finished.emit(False, f"Erreur pendant l'installation : {e}")




import re
import os
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Tuple
from collections import defaultdict, deque

class SQLFileMigrator:
    def __init__(self, connection): 
        self.connection = connection
        self.changes_made = []
        self.backup_dir = "backups"
        self.migration_log = []
        conn = None
        cursor = None

# --- FONCTIONS CORRIGÉES ---

    def get_tables(self):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='lekol360'")
            results = cursor.fetchall() 
            # Vérification que les résultats existent et ont au moins une colonne
            if results:
                # Les résultats sont des dictionnaires, on utilise la clé 'TABLE_NAME'
                return {row['TABLE_NAME'] for row in results if 'TABLE_NAME' in row}
            else:
                return set()  # Retourne un ensemble vide si pas de résultats
        except Exception as e:
            print(f"-------------- Erreur get_tables: {e}")
            import traceback
            traceback.print_exc()
            return set()  # Toujours retourner un ensemble même en cas d'erreur
        
    def get_columns(self, table):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA='lekol360' AND TABLE_NAME='{table}'
            """)
            results = cursor.fetchall()
            if results:
                return {row['COLUMN_NAME']: {
                    'type': row['COLUMN_TYPE'], 
                    'nullable': row['IS_NULLABLE'], 
                    'key': row['COLUMN_KEY'], 
                    'default': row['COLUMN_DEFAULT'], 
                    'extra': row['EXTRA']
                } for row in results if 'COLUMN_NAME' in row}
            else:
                return {}
        except Exception as e:
            print(f"++++++++++++++++ Erreur get_columns: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def get_primary_key(self, table):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                WHERE TABLE_SCHEMA='lekol360' AND TABLE_NAME='{table}' AND CONSTRAINT_NAME='PRIMARY'
            """)
            results = cursor.fetchall()
            if results:
                return [row['COLUMN_NAME'] for row in results if 'COLUMN_NAME' in row and row['COLUMN_NAME'] is not None]
            else:
                return []
        except Exception as e:
            print(f"gtttttttttttttttttt Erreur get_primary_key: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_foreign_keys(self, table):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA='lekol360' AND TABLE_NAME='{table}' AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            results = cursor.fetchall()
            if results:
                return {(row['CONSTRAINT_NAME'], row['COLUMN_NAME']): (row['REFERENCED_TABLE_NAME'], row['REFERENCED_COLUMN_NAME']) 
                        for row in results if all(key in row for key in ['CONSTRAINT_NAME', 'COLUMN_NAME', 'REFERENCED_TABLE_NAME', 'REFERENCED_COLUMN_NAME'])}
            else:
                return {}
        except Exception as e:
            print(f"gfhuuuuuuuuuuuuuuuuuuuuu Erreur get_foreign_keys: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def get_indexes(self, table):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(f"SHOW INDEX FROM `{table}`;")
            results = cursor.fetchall()
            indexes = {}
            if results:
                for row in results:
                    if all(key in row for key in ['Key_name', 'Column_name', 'Non_unique']):
                        key_name = row['Key_name']
                        column_name = row['Column_name']
                        non_unique = row['Non_unique']
                        if key_name not in indexes:
                            indexes[key_name] = {'columns': [], 'unique': not bool(non_unique)}
                        indexes[key_name]['columns'].append(column_name)
            return indexes
        except Exception as e:
            print(f"Erreur get_indexes: {e}")
            return {}
    


    def order_tables_by_dependencies(self, tables_sql):
        """
        Trie les tables selon leurs dépendances FOREIGN KEY.
        tables_sql = [(table_name, table_def), ...]
        """
        # Étape 1 : construire les dépendances
        deps = defaultdict(set)  # table → tables dont elle dépend
        all_tables = {name for name, _ in tables_sql}

        for table_name, table_def in tables_sql:
            referenced = re.findall(r'REFERENCES\s+`([^`]+)`', table_def)
            for ref in referenced:
                if ref in all_tables:
                    deps[table_name].add(ref)

        # Étape 2 : tri topologique (Kahn)
        ordered = []
        indegree = {t: 0 for t in all_tables}
        for t in deps:
            for dep in deps[t]:
                indegree[t] += 1

        queue = deque([t for t in all_tables if indegree[t] == 0])

        while queue:
            t = queue.popleft()
            ordered.append(t)
            for child in all_tables:
                if t in deps[child]:
                    indegree[child] -= 1
                    if indegree[child] == 0:
                        queue.append(child)

        # Vérifier s’il reste des dépendances non résolues
        remaining = [t for t in all_tables if t not in ordered]
        ordered += remaining  # On les met à la fin si elles sont circulaires

        # Retourne la liste triée complète [(nom_table, def_table), ...]
        ordered_tables = [(t, next(def_ for name, def_ in tables_sql if name == t)) for t in ordered]
        return ordered_tables


    def execute_sql_data(self, sql_file):
        try:
            conn = self.connection
            cursor = conn.cursor()
            
            # Vérifier que la connexion est valide
            if conn is None:
                print("Erreur: Pas de connexion à la base de données")
                return
            
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Nettoyer les commentaires plus agressivement
            sql_content = re.sub(r'--[^\n]*\n?', '', sql_content)  # Commentaires --
            sql_content = re.sub(r'#[^\n]*\n?', '', sql_content)   # Commentaires #
            sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.S)  # Commentaires /* */

            tables_sql = []
            i = 0
            content_length = len(sql_content)

            while i < content_length:
                # Chercher "CREATE TABLE"
                create_pos = sql_content.find('CREATE TABLE', i)
                if create_pos == -1:
                    break
                    
                # Trouver le début de la définition de table
                table_start = sql_content.find('`', create_pos)
                if table_start == -1:
                    i = create_pos + 12
                    continue
                    
                # Trouver la fin du nom de table
                table_end = sql_content.find('`', table_start + 1)
                if table_end == -1:
                    i = table_start + 1
                    continue
                    
                table_name = sql_content[table_start + 1:table_end]
                
                # Trouver le début de la définition des colonnes
                paren_start = sql_content.find('(', table_end)
                if paren_start == -1:
                    i = table_end + 1
                    continue
                    
                # Trouver la fin de la définition des colonnes
                paren_depth = 1
                j = paren_start + 1
                while j < content_length and paren_depth > 0:
                    if sql_content[j] == '(':
                        paren_depth += 1
                    elif sql_content[j] == ')':
                        paren_depth -= 1
                    j += 1
                
                if paren_depth == 0:
                    table_def = sql_content[paren_start + 1:j - 1]  # -1 pour exclure la parenthèse fermante
                    tables_sql.append((table_name, table_def))
                    i = j
                else:
                    i = paren_start + 1

            # t = self.extract_tables(sql_file)
            tables_sql = self.order_tables_by_dependencies(tables_sql)
            print(f"Nombre de tables trouvées: {tables_sql}")
            for i, (table_name, table_def) in enumerate(tables_sql):
                print(f"Création dans l’ordre logique {i+1}: {table_name}")

            existing_tables = self.get_tables()
            print(f"existing_tables    {existing_tables}")
                

            
            # S'assurer que existing_tables n'est pas None
            if existing_tables is None:
                print("Avertissement: existing_tables est None, utilisation d'un ensemble vide")
                existing_tables = set()
            # print(f"table sql {existing_tables}")
            for table_name, table_def in tables_sql:
                print(f"\n=== Vérification table `{table_name}` ===")
                lignes = [l.strip() for l in table_def.split(',\n') if l.strip()]
                
                colonnes_sql = {}
                primary_key_sql = None
                foreign_keys_sql = []
                uniques_sql = []

                for ligne in lignes:
                    if ligne.startswith('PRIMARY KEY'):
                        primary_key_sql = ligne
                    elif ligne.startswith('UNIQUE KEY') or ligne.startswith('KEY'):
                        uniques_sql.append(ligne)
                    elif ligne.startswith('CONSTRAINT') and 'FOREIGN KEY' in ligne:
                        foreign_keys_sql.append(ligne)
                    else:
                        match = re.match(r'`(\w+)`\s+(.+)', ligne)
                        if match:
                            colonnes_sql[match.group(1)] = match.group(2)

                # Vérification supplémentaire avant de continuer
                # print(f"table_name table_name  {table_name}")
                if table_name not in existing_tables:
                    print(f"Création table `{table_name}`")
                    try:
                        cursor.execute(f"CREATE TABLE `{table_name}` ({table_def});")
                        # Mettre à jour la liste des tables existantes
                        existing_tables = self.get_tables()
                    # except Exception as e:
                    except Exception as e:
                        err_msg = e.args[1] if hasattr(e, 'args') and len(e.args) > 1 else str(e)
                        if "already exists" not in err_msg:
                            print(f"Erreur création table {table_name}: {err_msg}")

                else:
                    colonnes_existantes = self.get_columns(table_name)

                    # --- Colonnes : ajout / modification / renommage ---
                    for col, typ in colonnes_sql.items():
                        if col not in colonnes_existantes:
                            sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {typ};"
                            print("Ajout colonne :", sql)
                            cursor.execute(sql)
                        else:
                            col_db = colonnes_existantes[col]
                            typ_db = col_db['type'].upper()
                            typ_sql = typ.split()[0].upper()
                            if typ_db != typ_sql:
                                sql = f"ALTER TABLE `{table_name}` CHANGE COLUMN `{col}` `{col}` {typ};"
                                print("Modification/rename colonne :", sql)
                                cursor.execute(sql)

                    # Colonnes en trop (détection + suggestion)
                    for col in colonnes_existantes:
                        if col not in colonnes_sql:
                            print(f"⚠ Colonne en trop dans `{table_name}` : {col} (à renommer ou supprimer si nécessaire)")

                    # --- PRIMARY KEY ---
                    pk_exist = self.get_primary_key(table_name)
                    if primary_key_sql and set(pk_exist) != set(re.findall(r'`(\w+)`', primary_key_sql)):
                        if pk_exist:
                            cursor.execute(f"ALTER TABLE `{table_name}` DROP PRIMARY KEY;")
                        sql = f"ALTER TABLE `{table_name}` ADD {primary_key_sql};"
                        print("Mise à jour PRIMARY KEY :", sql)
                        cursor.execute(sql)

                    # --- Index uniques et clés ---
                    indexes_exist = self.get_indexes(table_name)
                    for uq in uniques_sql:
                        uq_cols = re.findall(r'`(\w+)`', uq)
                        uq_name_match = re.match(r'(UNIQUE KEY|KEY) `(\w+)`', uq)
                        uq_name = uq_name_match.group(2) if uq_name_match else "_".join(uq_cols)
                        if uq_name not in indexes_exist:
                            sql = f"ALTER TABLE `{table_name}` ADD {uq};"
                            print("Ajout index/unique :", sql)
                            cursor.execute(sql)

                    # --- FOREIGN KEYS ---
                    fk_exist = self.get_foreign_keys(table_name)
                    for fk in foreign_keys_sql:
                        fk_cols = re.findall(r'FOREIGN KEY \(`(\w+)`\)', fk)
                        fk_name_match = re.match(r'CONSTRAINT `(\w+)`', fk)
                        fk_name = fk_name_match.group(1) if fk_name_match else fk_cols[0]
                        if all((fk_name, c) not in fk_exist for c in fk_cols):
                            sql = f"ALTER TABLE `{table_name}` ADD {fk};"
                            print("Ajout FOREIGN KEY :", sql)
                            try:
                                cursor.execute(sql)
                            except Exception as e:
                                print("Erreur FOREIGN KEY:", e)


            conn.commit()
            print("\n=== Importation ultime et synchronisation complète du schéma terminées ✅ ===")
            
        except Exception as e:
            print(f"gfhdfdnlhdnhdh Erreur execute_sql_data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Fermeture sécurisée des ressources
            try:
                if 'cursor' in locals() and cursor:
                    cursor.close()
            except:
                pass
            try:
                if 'conn' in locals() and conn:
                    conn.close()
            except:
                pass
        
        # try:
        #     conn = self.connection
        #     cursor = conn.cursor()
        #     with open(sql_file, 'r', encoding='utf-8') as f:
        #         sql_content = f.read()

        #     # Extraire les CREATE TABLE
        #     tables_sql = re.findall(r'CREATE TABLE `(.*?)`\s*\((.*?)\);', sql_content, re.S)
        #     existing_tables = self.get_tables()

        #     for table_name, table_def in tables_sql:
        #         print(f"\n=== Vérification table `{table_name}` ===")
        #         lignes = [l.strip() for l in table_def.split(',\n') if l.strip()]
                
        #         colonnes_sql = {}
        #         primary_key_sql = None
        #         foreign_keys_sql = []
        #         uniques_sql = []

        #         for ligne in lignes:
        #             if ligne.startswith('PRIMARY KEY'):
        #                 primary_key_sql = ligne
        #             elif ligne.startswith('UNIQUE KEY') or ligne.startswith('KEY'):
        #                 uniques_sql.append(ligne)
        #             elif ligne.startswith('CONSTRAINT') and 'FOREIGN KEY' in ligne:
        #                 foreign_keys_sql.append(ligne)
        #             else:
        #                 match = re.match(r'`(\w+)`\s+(.+)', ligne)
        #                 if match:
        #                     colonnes_sql[match.group(1)] = match.group(2)

        #         if table_name not in existing_tables:
        #             print(f"Création table `{table_name}`")
        #             cursor.execute(f"CREATE TABLE `{table_name}` ({table_def});")
        #         else:
        #             colonnes_existantes = self.get_columns(table_name)

        #             # --- Colonnes : ajout / modification / renommage ---
        #             for col, typ in colonnes_sql.items():
        #                 if col not in colonnes_existantes:
        #                     sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {typ};"
        #                     print("Ajout colonne :", sql)
        #                     cursor.execute(sql)
        #                 else:
        #                     col_db = colonnes_existantes[col]
        #                     typ_db = col_db['type'].upper()
        #                     typ_sql = typ.split()[0].upper()
        #                     if typ_db != typ_sql:
        #                         sql = f"ALTER TABLE `{table_name}` CHANGE COLUMN `{col}` `{col}` {typ};"
        #                         print("Modification/rename colonne :", sql)
        #                         cursor.execute(sql)

        #             # Colonnes en trop (détection + suggestion)
        #             for col in colonnes_existantes:
        #                 if col not in colonnes_sql:
        #                     print(f"⚠ Colonne en trop dans `{table_name}` : {col} (à renommer ou supprimer si nécessaire)")

        #             # --- PRIMARY KEY ---
        #             pk_exist = self.get_primary_key(table_name)
        #             if primary_key_sql and set(pk_exist) != set(re.findall(r'`(\w+)`', primary_key_sql)):
        #                 if pk_exist:
        #                     cursor.execute(f"ALTER TABLE `{table_name}` DROP PRIMARY KEY;")
        #                 sql = f"ALTER TABLE `{table_name}` ADD {primary_key_sql};"
        #                 print("Mise à jour PRIMARY KEY :", sql)
        #                 cursor.execute(sql)

        #             # --- Index uniques et clés ---
        #             indexes_exist = self.get_indexes(table_name)
        #             for uq in uniques_sql:
        #                 uq_cols = re.findall(r'`(\w+)`', uq)
        #                 uq_name_match = re.match(r'(UNIQUE KEY|KEY) `(\w+)`', uq)
        #                 uq_name = uq_name_match.group(2) if uq_name_match else "_".join(uq_cols)
        #                 if uq_name not in indexes_exist:
        #                     sql = f"ALTER TABLE `{table_name}` ADD {uq};"
        #                     print("Ajout index/unique :", sql)
        #                     cursor.execute(sql)

        #             # --- FOREIGN KEYS ---
        #             fk_exist = self.get_foreign_keys(table_name)
        #             for fk in foreign_keys_sql:
        #                 fk_cols = re.findall(r'FOREIGN KEY \(`(\w+)`\)', fk)
        #                 fk_name_match = re.match(r'CONSTRAINT `(\w+)`', fk)
        #                 fk_name = fk_name_match.group(1) if fk_name_match else fk_cols[0]
        #                 if all((fk_name, c) not in fk_exist for c in fk_cols):
        #                     sql = f"ALTER TABLE `{table_name}` ADD {fk};"
        #                     print("Ajout FOREIGN KEY :", sql)
        #                     try:
        #                         cursor.execute(sql)
        #                     except Exception as e:
        #                         print("Erreur FOREIGN KEY:", e)


    def clean_sql_file(self,input_file, output_file):
        """
        Supprime uniquement les lignes DROP TABLE / DROP DATABASE
        et ajoute les protections FOREIGN_KEY_CHECKS.
        """
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Supprimer les DROP TABLE / DROP DATABASE
        cleaned = re.sub(r"(?im)^\s*DROP\s+(TABLE|DATABASE)\b[^;]*;", "", content)

        # Ajouter la désactivation/réactivation des clés étrangères
        cleaned = (
            "SET FOREIGN_KEY_CHECKS = 0;\n\n"
            + cleaned.strip()
            + "\n\nSET FOREIGN_KEY_CHECKS = 1;\n"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned)


    def import_sql_file(self,sql_file_path):
        try:
            cursor = self.connection.cursor()

            print(f"🚀 Importation du fichier .sql")

            # 🔧 Désactiver les contraintes étrangères
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

            # 📂 Lecture du fichier SQL
            with open(sql_file_path, "r", encoding="utf-8") as file:
                sql_commands = file.read()

            # 🧩 Découper le script par point-virgule
            commands = sql_commands.split(";")

            for command in commands:
                cmd = command.strip()
                # Ignorer les lignes vides et commentaires
                if cmd and not cmd.startswith("--") and not cmd.startswith("/*"):
                    try:
                        cursor.execute(cmd)
                    except Exception as e:
                        pass
                        # print(f"⚠️ Erreur sur : {cmd[:80]}...")
                        # print("   →", e)

            # 🔧 Réactiver les contraintes
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

            print("✅ Importation terminée avec succès !")

        except Exception as e:
            print("❌ Erreur lors de l’importation :", e)

        finally:
            if cursor:
                cursor.close()
            if self.connection:
                self.connection.close()

    # Exemple d’utilisation :


    def connect(self):
        return self.connection

# CREATE USER 'user_pyside'@'%' IDENTIFIED BY '@#Janvier21' REQUIRE SSL;
# GRANT ALL PRIVILEGES ON lemignon.* TO 'user_pyside'@'%';
# FLUSH PRIVILEGES;


# SET group_concat_max_len = 1000000;

# SELECT CONCAT('DROP TABLE ', GROUP_CONCAT(CONCAT('`', table_name, '`')), ';')
# FROM information_schema.tables
# WHERE table_schema = 'lekol360'
#   AND table_name LIKE 'sym_%';

# SELECT TRIGGER_SCHEMA, TRIGGER_NAME, EVENT_OBJECT_TABLE, ACTION_STATEMENT, DEFINER
# FROM information_schema.TRIGGERS
# WHERE ACTION_STATEMENT LIKE '%sym_data%';


# SELECT TRIGGER_SCHEMA AS db,
#        TRIGGER_NAME AS trigger_name,
#        EVENT_OBJECT_TABLE AS table_name,
#        DEFINER
# FROM information_schema.TRIGGERS
# WHERE DEFINER = 'repl@10.10.0.1';

# SELECT CONCAT('DROP TRIGGER `', TRIGGER_SCHEMA, '`.`', TRIGGER_NAME, '`;') AS drop_cmd
# FROM information_schema.TRIGGERS
# WHERE DEFINER = 'repl@10.10.0.1';

# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_LN_RPYMNTS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_LN_RPYMNTS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_LN_RPYMNTS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_LNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_LNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_LNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_THR_TRNSCTNS_MN`; 
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_THR_TRNSCTNS_MN`; 
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_THR_TRNSCTNS_MN`;




# SET FOREIGN_KEY_CHECKS = 0;
#   DROP TABLE `sym_channel`,`sym_conflict`,`sym_context`,`sym_data_event`,`sym_data_gap`,`sym_extension`,`sym_extract_request`,`sym_file_incoming`,`sym_file_snapshot`,`sym_file_trigger`,`sym_file_trigger_router`,`sym_grouplet`,`sym_grouplet_link`,`sym_incoming_batch`,`sym_incoming_error`,`sym_job`,`sym_load_filter`,`sym_lock`,`sym_node`,`sym_node_channel_ctl`,`sym_node_communication`,`sym_node_group`,`sym_node_group_channel_wnd`,`sym_node_group_link`,`sym_node_host`,`sym_node_host_channel_stats`,`sym_node_host_job_stats`,`sym_node_host_stats`,`sym_node_identity`,`sym_node_security`,`sym_outgoing_batch`,`sym_outgoing_error`,`sym_parameter`,`sym_registration_redirect`,`sym_registration_request`,`sym_router`,`sym_sequence`,`sym_table_reload_request`,`sym_table_reload_status`,`sym_transform_column`,`sym_transform_table`,`sym_trigger`,`sym_trigger_hist`,`sym_trigger_router`,`sym_trigger_router_grouplet`;
# SET FOREIGN_KEY_CHECKS = 1;


# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_RSPNSBLS_MN`;
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NN_CDMQS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NN_CDMQS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NN_CDMQS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NNS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NNS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NNS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CCH_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CCH_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CCH_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CCH_LCKS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CCH_LCKS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CCH_LCKS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CLSS_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CLSS_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CLSS_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CLSSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CLSSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CLSSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CLSSS_TDNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CLSSS_TDNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CLSSS_TDNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CLNT_NFS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CLNT_NFS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CLNT_NFS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CRS_TDNTS_MN`;       
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CRS_TDNTS_MN`;       
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CRS_TDNTS_MN`;       
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_DPNSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_DPNSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_DPNSS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_TDNT_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_TDNT_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_TDNT_FCLTS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_TDNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_TDNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_TDNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_FCLTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_FCLTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_FCLTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_FLD_JBS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_FLD_JBS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_FLD_JBS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_FRS_DNSCRPTNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_FRS_DNSCRPTNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_FRS_DNSCRPTNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_FRS_DVRS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_FRS_DVRS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_FRS_DVRS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_HRT_TS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_HRT_TS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_HRT_TS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_JB_BTCHS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_JB_BTCHS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_JB_BTCHS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_JBS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_JBS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_JBS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_LG_CTVS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_LG_CTVS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_LG_CTVS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_LGS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_LGS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_LGS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_MGRTNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_MGRTNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_MGRTNS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_MDL_HS_PRMSSNS_MN`;  
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_MDL_HS_PRMSSNS_MN`;  
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_MDL_HS_PRMSSNS_MN`;  
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_MDL_HS_RLS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_MDL_HS_RLS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_MDL_HS_RLS_MN`;      
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NV_DTDS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NV_DTDS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NV_DTDS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NVX_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NVX_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NVX_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NTS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NTS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NTS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_RDR_TMS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_RDR_TMS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_RDR_TMS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PMNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PMNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PMNTS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRMTR_PMNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRMTR_PMNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRMTR_PMNTS_MN`;     
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRMS_XMS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRMS_XMS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRMS_XMS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PSSWRD_RST_TKNS_MN`; 
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PSSWRD_RST_TKNS_MN`; 
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PSSWRD_RST_TKNS_MN`; 
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRMSSNS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRMSSNS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRMSSNS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRSNNLS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRSNNLS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRSNNLS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PCS_SMSS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PCS_SMSS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PCS_SMSS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRSNCS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRSNCS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRSNCS_MN`;          
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRFSSRS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRFSSRS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRFSSRS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRFLS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRFLS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRFLS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PRGRMMS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PRGRMMS_MN`;         
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PRGRMMS_MN`;         |
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_RSPNSBLS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_RSPNSBLS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_RSPNSBLS_MN`;        
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_RL_HS_PRMSSNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_RL_HS_PRMSSNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_RL_HS_PRMSSNS_MN`;   
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_RLS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_RLS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_RLS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_SSSNS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_SSSNS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_SSSNS_MN`;           
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_SRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_SRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_SRS_MN`;             
#  DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_VNTS_MN`;            
#  DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_VNTS_MN`;            
#  DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_VNTS_MN`;






 
# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_CTGRS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_CTGRS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_CTGRS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_VNTS_MN1`;
# DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_VNTS_MN1`;
# DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_VNTS_MN1`;
# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_NWS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_NWS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_NWS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_I_FOR_TRG_PMNT_STTTS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_U_FOR_TRG_PMNT_STTTS_MN`;
# DROP TRIGGER `lekol360`.`SYM_ON_D_FOR_TRG_PMNT_STTTS_MN`;

