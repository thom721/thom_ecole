import os
import sys
import subprocess
import shutil
import re
import uvicorn
import socket
import zipfile
import platform
from shutil import copyfile
import time
import requests
import psutil # type: ignore
from PySide6.QtWidgets import QApplication,QMessageBox
from Helper.verify_key import ask_for_activation_key
from Helper.server_key_generate import show_activation_key,delete_key,is_license_valid,get_mac_address,apply_remote_licence,generate_fernet_key,decrypt_value
from Helper.Ip_manager import Ip_manager
from Helper.manage_activate import Manage_active
import threading
    # import time
    # import requests # Assure-toi d'avoir installé 'requests'
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

        # print(f"program_path   {program_path}")

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

    def genere_ssl_key(self, ip_address, update_client=False):
        """Générer/renouveler le certificat serveur (et la CA, si absente) pour
        aplekol360.local.

        Écrit dans %USERPROFILE%/AppData/Local/.ecole_360/.ssl_nginx, le
        dossier que configure_nginx() lit déjà pour peupler nginx/certs — donc
        avec les noms attendus par configure_nginx (ca.pem, server.key,
        server.crt), pas besoin d'étape de copie séparée.

        Volontairement PAS appelée automatiquement à l'installation ni au
        lancement (install_and_config() ne l'appelle pas) : la CA doit être
        générée une seule fois puis réutilisée à l'identique sur toutes les
        installations Windows/Mac/Linux, jamais régénérée au hasard à chaque
        install — donc déclenchement manuel uniquement, quand on a
        explicitement besoin de (re)créer la CA et/ou renouveler le
        certificat serveur."""
        try:
            user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
            _conf_path = os.path.join(user_profile, "AppData", "Local", ".ecole_360", ".ssl_nginx")

            # 1. S'ASSURER QUE LE RÉPERTOIRE EXISTE
            os.makedirs(_conf_path, exist_ok=True)
            self.set_full_permissions(_conf_path) # Assurez-vous que cette méthode existe

            # 2. Chemins des fichiers (noms attendus par configure_nginx())
            key_path = os.path.join(_conf_path, 'server.key')
            cert_path = os.path.join(_conf_path, 'server.crt')
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
            
            # 4. Générer la CA — une seule fois : si ca.key/ca.pem existent déjà
            # (CA partagée déjà en place), on les réutilise pour signer le
            # nouveau certificat serveur, sans jamais régénérer la CA elle-même.
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
            
            # 8. Signature — 825 jours max (limite Apple/macOS pour les
            # certificats serveur ; ne s'applique PAS à la CA elle-même,
            # signée pour 10 ans ci-dessus, qui n'est jamais présentée
            # directement lors d'un handshake TLS).
            subprocess.run([
                'openssl', 'x509', '-req', '-in', csr_path, '-CA', ca_cert, '-CAkey', ca_key,
                '-CAcreateserial', '-out', cert_path, '-days', '825',
                '-sha256', '-extfile', san_file, '-extensions', 'v3_req'
            ], check=True)


            # 10. Magasin Windows
            if update_client:
                subprocess.run(['certutil', '-addstore', '-f', 'Root', ca_cert], check=True)

            # 11. VÉRIFICATION FINALE (Le test qui échouait avant)
            result = subprocess.run(['openssl', 'verify', '-CAfile', ca_cert, cert_path],
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
        os.makedirs(os.path.join(nginx_directory, 'certs'), exist_ok=True)

        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".ssl_nginx")

        try:
            cert_files = ['server.key', 'server.crt', 'ca.pem']
            
            for cert_file in cert_files:
                source_file = os.path.join(source_path, cert_file)
                dest_file = os.path.join(nginx_directory, 'certs', cert_file)
                
                if os.path.exists(source_file):
                    shutil.copy2(source_file, dest_file)
                    # print(Fore.GREEN + f" [ok]   Copié: {cert_file}")
                else:
                    print(Fore.YELLOW + f" [warn] Fichier non trouvé: {source_file}")
                    
        except Exception as e:
            print(f" [x]   Erreur copie certificats: {e}")
            return False
        
        # Utiliser vos chemins SSL existants
        
        ssl_key = os.path.join(nginx_directory,"certs", 'server.key')
        ssl_cert = os.path.join(nginx_directory,"certs", 'server.crt')
        ca_cert = os.path.join(nginx_directory,"certs", 'ca.pem')
        
        
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
            send_timeout 5;
            
            # Gzip compression
            gzip on;
            gzip_vary on;
            gzip_min_length 1000;
            gzip_disable "msie6";
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

                

     
            # Param�tres SSL s�curis�s
            ssl_protocols TLSv1.2 TLSv1.3;
            ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
            ssl_prefer_server_ciphers on;
            ssl_session_cache shared:SSL:10m;
            ssl_session_timeout 10m;
            ssl_session_tickets off;
            
  
            # Headers de s�curit�
            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
            add_header Referrer-Policy "strict-origin-when-cross-origin" always;
            

            # Cache FastCGI
            fastcgi_cache_path "{Path(os.path.join(nginx_directory, 'cache', 'fastcgi')).as_posix()}" levels=1:2 keys_zone=FCGICACHE:100m inactive=60m;
            fastcgi_cache_key "$scheme$request_method$host$request_uri";
            fastcgi_cache_use_stale error timeout invalid_header http_500;
            fastcgi_ignore_headers Cache-Control Expires Set-Cookie;

            # Serveur principal HTTPS
            server {{
                listen       443 ssl;
                listen       [::]:443 ssl;
                #http2 on;
                server_name aplekol360.local _;
                
                ssl_certificate      "{Path(ssl_cert).as_posix()}";
                ssl_certificate_key  "{Path(ssl_key).as_posix()}";
                #ssl_trusted_certificate "{Path(ca_cert).as_posix()}";

                ssl_protocols        TLSv1.2 TLSv1.3;
                ssl_ciphers          HIGH:!aNULL:!MD5;
                ssl_session_cache    shared:SSL:10m;
                ssl_session_timeout  10m;
                
                # Logs
                access_log  "{Path(os.path.join(nginx_directory, 'logs', 'access.log')).as_posix()}";
                error_log   "{Path(os.path.join(nginx_directory, 'logs', 'error.log')).as_posix()}" warn;
                
                # Optimisations fichiers statiques
                location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {{
                    expires 1y;
                    add_header Cache-Control "public, immutable";
                    access_log off;
                }}
                
                location / {{
                    proxy_pass http://127.0.0.1:9001;
                    proxy_http_version 1.1;
                
                    proxy_buffering off; 
        
                    # Augmenter les timeouts (la génération Jinja2 peut prendre du temps)
                    proxy_read_timeout 300;
                    proxy_connect_timeout 300;
                    proxy_send_timeout 300;

                    proxy_max_temp_file_size 0;
                    # --- Configuration du Buffer ---
                    # proxy_buffering on;
                    proxy_buffer_size 128k;
                    proxy_buffers 16 256k;
                    proxy_busy_buffers_size 256k;


                    # --- Headers essentiels pour FastAPI ---
                    proxy_set_header Host $host;
                    proxy_set_header X-Real-IP $remote_addr;
                    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header X-Forwarded-Proto $scheme;
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
                listen       8082;
                listen       [::]:8082;
                server_name aplekol360.local localhost;
                
                # Redirection permanente vers HTTPS
                return 301 https://$server_name:443$request_uri;
            }}
        }}
        '''

        try:
            # Créer les répertoires nécessaires
            os.makedirs(os.path.join(nginx_directory, 'logs'), exist_ok=True)
            os.makedirs(os.path.join(nginx_directory, 'cache', 'fastcgi'), exist_ok=True)
            
            # Écrire la configuration Nginx
            with open(nginx_conf_path, 'w', encoding='utf-8') as file:
                file.write(nginx_config)
            
            print(Fore.GREEN + f"\n [ok]   Configuration Nginx écrite avec votre SSL personnalisé")
            
      
            # Mettre à jour le magasin de certificats Windows
            self.update_windows_certificate_store(ca_cert)
            
            return True
            
        except Exception as e:
            print(f"Erreur lors de la configuration de Nginx: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


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
        cmd_add = 'netsh advfirewall firewall add rule name="Serveur Ecole (Nginx)" dir=in action=allow protocol=TCP localport=80,443'

        ressources = 'netsh advfirewall firewall add rule name="Discovery mDNS" dir=in action=allow protocol=UDP localport=5353'

        cmd_show = 'netsh advfirewall firewall show rule name="Serveur Ecole (Nginx)"'

        # cmd_add1 = 'netsh advfirewall firewall add rule name="Nginx in" dir=in action=allow protocol=TCP localport=443'

        # cmd_show1 = 'netsh advfirewall firewall show rule name="Nginx in"'

        try: 
            check_process = subprocess.run(cmd_show, shell=True, capture_output=True, text=True)

            if check_process.returncode == 0:
                print(f" ")
            else: 
                add_process = subprocess.run(cmd_add, shell=True, check=True, capture_output=True, text=True) 
            # subprocess.run(cmd_add, shell=True, check=True, capture_output=True, text=True)
        
            subprocess.run(ressources, shell=True, check=True, capture_output=True, text=True)
            # result = subprocess.run(cmd_show, shell=True, capture_output=True, text=True)
            # print("--- État de la règle ---")
            # print(result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de la configuration du firewall : {e.stderr}")

        try:
            nginx_dir = os.path.join(self.current_project, 'nginx')
            nginx_exe = os.path.join(nginx_dir, 'nginx.exe')
            
            # Vérifier les fichiers SSL
            ssl_files = [
                os.path.join(nginx_dir, 'certs', 'server.key'),
                os.path.join(nginx_dir, 'certs', 'server.crt'),
                os.path.join(nginx_dir, 'certs', 'ca.pem')
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
            
                
            return service_installed
            
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
            nginx_exe = os.path.join(nginx_dir, 'nginx.exe').replace("/", "\\")
            nginx_logs = os.path.join(nginx_dir, 'logs').replace("/", "\\")
            nginx_root = nginx_dir.replace("/", "\\")
            
            # Créer le fichier de configuration WinSW
            winsw_config = textwrap.dedent(f'''\
                <service>
                    <id>NginxAplekol</id>
                    <name>Nginx Aplekol</name>
                    <description>Service Nginx pour Aplekol</description>
                    <executable>{nginx_exe}</executable>
                    <logpath>{nginx_logs}</logpath>
                    <log mode="roll"></log>
                    <startargument>-p</startargument>
                    <startargument>{nginx_root}</startargument>
                    <stopargument>-p</stopargument>
                    <stopargument>{nginx_root}</stopargument>
                    <stopargument>-s</stopargument>
                    <stopargument>stop</stopargument>
                </service>
            ''')

            # Écriture du fichier
            winsw_config_path = os.path.join(self.current_project,"data", "nginx-service.xml")
            with open(winsw_config_path, 'w', encoding='utf-8') as f:
                f.write(winsw_config.strip())
                        
     
            # Installer le service
            print("\n [+]   Installation du service Nginx...")
            ngin =os.path.join(self.current_project,"data")
            if not self.check_nginx():
                subprocess.run([winsw_exe, "install"], check=True, cwd=ngin)
            
            # Démarrer le service
            subprocess.run([winsw_exe, "start"], check=True, cwd=ngin)
            
            print(Fore.GREEN + " [ok]   Service Nginx installé et démarré!")
            
        except Exception as e:
            print(f" [x]   Erreur lors de l'installation avec WinSW: {e}")
            # Fallback: démarrer Nginx directement
            # import traceback
            # traceback.print_exc() 
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


    def check_nginx(self):
        """ Vérifie si un service MySQL existe """
        try:
            result = subprocess.run(
                ["sc", "query", "NginxAplekol"], capture_output=True, text=True
            )
            # print(result.stdout)
            return "NginxAplekol" in result.stdout
        except Exception as e:
            print(f"❌ Erreur lors de la vérification du service NginxAplekol: {e}")
            return False

    def add_or_update_host(self, ip: str,domain="aplekol360.local"):
        """
        Ajoute ou met à jour une entrée dans le fichier hosts pour un domaine donné.
        Nécessite les privilèges administrateur/root.
        """
        
        # Déterminer le chemin du fichier hosts selon le système
        system = platform.system()
        if system == "Windows":
            hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        elif system in ["Linux", "Darwin"]:
            hosts_path = "/etc/hosts"
        else:
            raise Exception("Système non supporté")

        # Lire le contenu existant
        try:
            with open(hosts_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise Exception(f"Fichier hosts non trouvé : {hosts_path}")
        
        # Nettoyer les lignes et préparer une liste pour les nouvelles
        new_lines = []
        domain_found = False

        for line in lines:
            if domain in line and not line.strip().startswith("#"):
                # Si le domaine existe déjà, on le remplace par la nouvelle IP
                new_lines.append(f"{ip}\t{domain}\n")
                domain_found = True
                # print(f"🔁 Domaine {domain} mis à jour -> {ip}")
            else:
                new_lines.append(line)

        if not domain_found:
            # Ajouter une nouvelle entrée si le domaine n’existe pas
            new_lines.append(f"{ip}\t{domain}\n")
            # print(f"✅ Domaine {domain} ajouté -> {ip}")

        # Sauvegarder les changements (privilèges requis)
        try:
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            # print(f"💾 Modifications enregistrées dans {hosts_path}")
        except PermissionError:
            print("❌ Permission refusée. Exécutez ce script en administrateur/root.")

    def configure_env(self): 
        try:
            if not self.is_installed("mysql",os.path.join(self.current_project,"mysql-8.0.41-winx64","bin")):
                         
                installer = MySQLInstaller()
                installer.install_and_config() 

                self.password = installer.return_data()[0]
                self.db_name = installer.return_data()[1] 
                path_certs = os.path.join(self.extract_dir, 'certs')

                # if not self.set_permissions(env_path):
                #     return 

                cmd_mysql_add = 'netsh advfirewall firewall add rule name="MySQL 3307" dir=in action=allow protocol=TCP localport=3307'
 
                cmd_mysql_show = 'netsh advfirewall firewall show rule name="MySQL 3307"'


                try:
                    # On exécute la vérification
                    # capture_output=True empêche d'afficher le texte dans la console si la règle existe
                    check_process = subprocess.run(cmd_mysql_show, shell=True, capture_output=True, text=True)

                    if check_process.returncode == 0:
                        print(f"")
                    else:
                        add_process = subprocess.run(cmd_mysql_add, shell=True, check=True, capture_output=True, text=True)

                except subprocess.CalledProcessError as e:
                    print(f"❌ Erreur lors de l'exécution de la commande : {e}")
                except PermissionError:
                    print("❌ Erreur : Vous devez exécuter ce script en tant qu'Administrateur !")

                # try:
                #     # On tente d'abord de supprimer l'ancienne règle pour éviter les doublons
                #     subprocess.run('netsh advfirewall firewall delete rule name="MySQL Server School"', shell=True, capture_output=True)
                    
                #     # Ajout de la règle
                #     subprocess.run(cmd_mysql_add, shell=True, check=True)
                #     print("✅ Port 3307 ouvert pour MySQL.")
                # except Exception as e:
                #     print(f"⚠️ Erreur Firewall MySQL : {e}")

                ip_address = self.get_server_ip_()
                self.add_or_update_host(ip_address)
                self.ip_manager.save_server_ip(ip_address)


        except PermissionError:
            print("\n [x]  Échec des droits d'accès après configuration")
        except Exception as e:
            print(f"\n [x]  Erreur inattendue 1: {str(e)}") 
            import traceback
            traceback.print_exc()   

     
        if not self.is_installed("nginx",os.path.join(self.install_dir,"nginx")) or not self.check_nginx():
            # Télécharger Nginx
            self.kill_port_owner(9001)
            if os.path.exists(os.path.join(self.current_project,"data", "nginx-1.26.3")):
                nginx_path = os.path.join(self.current_project,"data", "nginx-1.26.3")
            else:
            #  not os.path.exists(os.path.join(self.current_project, "nginx")):
                nginx_url = "https://nginx.org/download/nginx-1.24.0.zip"
                nginx_extract_path = self.install_program(nginx_url, "nginx.zip", "")
                
                nginx_path = os.path.join(nginx_extract_path, "nginx-1.24.0")
                
            nginx_final_path = os.path.join(self.current_project, "nginx")
            subprocess.run(["taskkill", "/F", "/IM", "nginx.exe", "/T"], capture_output=True)
            # self.set_full_permissions(nginx_final_path)
            
            # Déplacer Nginx à l'emplacement final
            if os.path.exists(nginx_final_path):
                shutil.rmtree(nginx_final_path)
            shutil.move(nginx_path, nginx_final_path)
            
            # self.add_to_path(os.path.join(nginx_final_path))
            
            print("\n [+] Installation et configuration de Nginx...")
            self.server_ip = self.get_server_ip_()
           
            # while not self.validate_ip(self.server_ip):
            while not self.validate_ip(self.server_ip):
                print("\n [x] L'adresse IP est invalide ou ne correspond pas à cette machine.")
                self.server_ip = input("\n\t [ + ] Entrez une adresse IP valide :  ")

            self.ip_manager.save_server_ip(self.server_ip)
            self.add_or_update_host(self.server_ip)
            if self.configure_nginx(ip_ser=self.server_ip):
                try:
                    self.configure_nginx_service()
                    print("\n Installation Nginx terminée !\n")
                    print("\n Installation terminée !")
                except:
                    pass
            
    

    def configure_mysql_user(self, ip_ser, password):
        # Extraire la plage d'IP
        ip_parts = ip_ser.split(".")
        ip_range = '127.0.0.1' #".".join(ip_parts[:3]) + ".%"
        _password = '@#Lekol3&0'
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

    def ensure_services_running(self, services, force=False):
        for service in services:
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
        # print(hostname,ip_address,self.get_local_ip())
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
        
        self.app = QApplication(sys.argv)

        if active == 'true':  
            self.verify_esystem_and_install_service() 
            ip_address = self.get_server_ip_()
            if ip_address != self.ip_manager.get_server_ip():
                self.add_or_update_host(self.get_server_ip_()) 

            self.ensure_services_running(services_a_verifier)
            print("\n [+]   Demarrage du server ...!!!--")
            self.launch_and_wait_for_api()
            
            try: 

                self.ip_manager.save_server_ip(ip_address)

                if ip_address:
                    base_url = f"https://aplekol360.local/api/v1/"

                elif self.get_server_ip_():
                    ip_address = self.get_server_ip_()
                    base_url = f"https://aplekol360.local/api/v1/"

                else:
                    ip_address = input("Nous ne pouvons pas détecter l'adresse IP automatiquement. Veuillez entrer l'IP du serveur: ")
                 
 
                if not self.is_ip_reachable(ip_address):
                    QMessageBox.critical(None, "Network Error", "We can't find your network, please reconnect or restart the router!.")
                    return 
                
                try:
                    url = f"{base_url}first-check"                    
                    response = requests.get(url, verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem")#
                    status_code = response.status_code
                except:
                    self.launch_and_wait_for_api()
                    url = f"{base_url}first-check"                    
                    response = requests.get(url, verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem")#
                    status_code = response.status_code
                # print(response.json(), status_code)   
                if status_code == 200: 
                    urls = f"{base_url}client-authorisation-connect"
                    # print(f"urls  {urls}")
                    headers = {
                        'Content-Type': 'application/json',
                         'Accept': 'application/json'
                    }
                    try: 
                        data = requests.get(urls, headers=headers,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem")
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
                        else:
                            pass
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
            input("\nCtrl + C pour quitter...")
            return
        

        # activation_key = ask_for_activation_key
        license = LicenseManager()
        val_bool, message, date = license.check_license() 
        if not date or date == None:
            show_activation_key()
        
        
        services_a_verifier = ["MySQLEcole", "NginxAplekol"]
        self.ensure_services_running(services_a_verifier)
        self.launch_and_wait_for_api()

        if val_bool== False and message == "Licence expirée":
            QMessageBox.critical(None, "Licence expirée", "Votre licence a expiré ou est invalide.\nOk pour continuer.")            
            print("\n [+]   Creer un compte administrateur! 1")
            self.insert_user()

        if val_bool== True and message == "Licence valide":
            print("\n [+]   Creer un compte administrateur! 2")
            self.insert_user()

        elif ask_for_activation_key():
            print("\n [+]   Creer un compte administrateur! 3")
            self.insert_user()   
            self.verify_esystem_and_install_service()         
            # self.ajouter_au_demarrage("école-server")

 
    def launch_and_wait_for_api(self):  
        api_thread = threading.Thread(target=self.start_api, daemon=True)
        api_thread.start()
        print("⏳ Démarrage de l'API en cours...")

        # 2. Boucle d'attente intelligente
        api_url = "http://127.0.0.1:9001/api/v1/health"
        max_retries = 220
        retry_count = 0
        api_ready = False

        while retry_count < max_retries:
            try:
                # On tente d'appeler l'API
                response = requests.get(api_url, timeout=1)
                if response.status_code == 200:
                    print("✅ API opérationnelle ! Poursuite du programme...")
                    api_ready = True
                    break
            except requests.exceptions.ConnectionError:
                # L'API n'est pas encore prête
                retry_count += 1
                time.sleep(5) 
                print(end=f"*", flush=True)

        if not api_ready:
            print("❌ Erreur : L'API n'a pas démarré à temps.")
            # Ici, tu peux décider de stopper le programme ou de lever une erreur

    def start_api(self):
        from app.main import app
        import uvicorn
        uvicorn.run(
            app,           
            host="0.0.0.0",
            port=9001,
            reload=False,   
            workers=1, 
            timeout_keep_alive=75,
            # log_level="critical"
            # log_level="warning"
        )

 


    def kill_port_owner(self,port):
        try:
            # Trouve le PID qui utilise le port
            result = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            for line in result.splitlines():
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    # print(f"🧹 Nettoyage du port {port} (PID: {pid})...")
                    os.system(f"taskkill /F /PID {pid}")
        except:
            pass # Le port est libre, rien à faire

    def verify_esystem_and_install_service(self):
        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".nssm")

        nssm_path = os.path.join(source_path, 'win64', 'nssm.exe')
        app_exe = r"C:\Program Files\ecole-serve\app.exe"
        service_name = "Esystem"
        app_dir = os.path.dirname(app_exe)

        log_dir = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_stdout = os.path.join(log_dir, "esystem_output.log")
        log_stderr = os.path.join(log_dir, "esystem_error.log")

        def service_exists():
            result = subprocess.run(
                [nssm_path, "status", service_name],
                capture_output=True, text=True
            )
            return result.returncode == 0 or "SERVICE_" in result.stdout

        def get_nssm_value(key):
            result = subprocess.run(
                [nssm_path, "get", service_name, key],
                capture_output=True, text=True
            )
            return result.stdout.strip()

        def configure_service_account():
            """Configure le service pour tourner sans session utilisateur"""
            changes = []

            current_account = get_nssm_value("ObjectName")
            if current_account != "LocalSystem":
                # Tourner sous LocalSystem = démarre même sans login
                subprocess.run([nssm_path, "set", service_name, "ObjectName", "LocalSystem"], check=True)
                changes.append("  + Compte : LocalSystem (démarre sans session)")

            current_start = get_nssm_value("Start")
            if current_start != "SERVICE_AUTO_START":
                # Démarrage automatique au boot
                subprocess.run([nssm_path, "set", service_name, "Start", "SERVICE_AUTO_START"], check=True)
                changes.append("  + Démarrage : Automatique au boot")

            current_type = get_nssm_value("Type")
            if current_type != "SERVICE_WIN32_OWN_PROCESS":
                subprocess.run([nssm_path, "set", service_name, "Type", "SERVICE_WIN32_OWN_PROCESS"], check=True)
                changes.append("  + Type : Service Windows natif")

            return changes

        def configure_logs():
            changes = []

            current_stdout = get_nssm_value("AppStdout")
            if not current_stdout or current_stdout != log_stdout:
                subprocess.run([nssm_path, "set", service_name, "AppStdout", log_stdout], check=True)
                changes.append(f"  + AppStdout → {log_stdout}")

            current_stderr = get_nssm_value("AppStderr")
            if not current_stderr or current_stderr != log_stderr:
                subprocess.run([nssm_path, "set", service_name, "AppStderr", log_stderr], check=True)
                changes.append(f"  + AppStderr → {log_stderr}")

            current_rotate = get_nssm_value("AppRotateFiles")
            if current_rotate != "1":
                subprocess.run([nssm_path, "set", service_name, "AppRotateFiles", "1"], check=True)
                subprocess.run([nssm_path, "set", service_name, "AppRotateSeconds", "86400"], check=True)
                subprocess.run([nssm_path, "set", service_name, "AppRotateBytes", "10485760"], check=True)
                changes.append("  + Rotation des logs activée (quotidienne / 10MB)")

            return changes

        try:
            if service_exists():
                print(f"✅ Le service '{service_name}' est déjà installé.")

                all_changes = []

                # Vérifier le compte de service
                account_changes = configure_service_account()
                all_changes.extend(account_changes)

                # Vérifier les logs
                log_changes = configure_logs()
                all_changes.extend(log_changes)

                if all_changes:
                    print("⚙ Modifications détectées :")
                    for c in all_changes:
                        print(c)

                    print("🔄 Redémarrage du service...")
                    subprocess.run([nssm_path, "stop", service_name], check=True)
                    subprocess.run([nssm_path, "start", service_name], check=True)
                    print("✅ Service redémarré avec succès.")
                else:
                    print("✅ Service correctement configuré. Aucun changement nécessaire.")

            else:
                print(f"📦 Installation du service '{service_name}'...")

                # 1. Création du service
                subprocess.run([nssm_path, "install", service_name, app_exe], check=True)

                # 2. Dossier de démarrage
                subprocess.run([nssm_path, "set", service_name, "AppDirectory", app_dir], check=True)

                # 3. ✅ Compte LocalSystem (fonctionne sans session utilisateur)
                subprocess.run([nssm_path, "set", service_name, "ObjectName", "LocalSystem"], check=True)

                # 4. Démarrage automatique au boot
                subprocess.run([nssm_path, "set", service_name, "Start", "SERVICE_AUTO_START"], check=True)

                # 5. Redémarrage automatique en cas de crash
                subprocess.run([nssm_path, "set", service_name, "AppRestartDelay", "1000"], check=True)

                # 6. Logs
                configure_logs()

                # 7. Lancement
                subprocess.run([nssm_path, "start", service_name], check=True)
                print(f"✅ Service '{service_name}' installé et démarré.")

        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur verify_esystem_and_install_service: {e}")
            import traceback
            traceback.print_exc()

    def verify_esystem_and_install_service1(self):
        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".nssm")

        nssm_path = os.path.join(source_path, 'win64', 'nssm.exe')
        app_exe = r"C:\Program Files\ecole-serve\app.exe"
        service_name = "Esystem"
        app_dir = os.path.dirname(app_exe)

        log_dir = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_stdout = os.path.join(log_dir, "esystem_output.log")
        log_stderr = os.path.join(log_dir, "esystem_error.log")

        def service_exists():
            """Vérifie si le service est déjà installé"""
            result = subprocess.run(
                [nssm_path, "status", service_name],
                capture_output=True, text=True
            )
            # Si le service n'existe pas, nssm retourne une erreur
            return result.returncode == 0 or "SERVICE_" in result.stdout

        def get_nssm_value(key):
            """Récupère la valeur actuelle d'un paramètre NSSM"""
            result = subprocess.run(
                [nssm_path, "get", service_name, key],
                capture_output=True, text=True
            )
            return result.stdout.strip()

        def configure_logs():
            """Configure les logs s'ils ne sont pas déjà définis"""
            changes = []

            current_stdout = get_nssm_value("AppStdout")
            if not current_stdout or current_stdout != log_stdout:
                subprocess.run([nssm_path, "set", service_name, "AppStdout", log_stdout], check=True)
                changes.append(f"  + AppStdout → {log_stdout}")

            current_stderr = get_nssm_value("AppStderr")
            if not current_stderr or current_stderr != log_stderr:
                subprocess.run([nssm_path, "set", service_name, "AppStderr", log_stderr], check=True)
                changes.append(f"  + AppStderr → {log_stderr}")

            current_rotate = get_nssm_value("AppRotateFiles")
            if current_rotate != "1":
                subprocess.run([nssm_path, "set", service_name, "AppRotateFiles", "1"], check=True)
                subprocess.run([nssm_path, "set", service_name, "AppRotateSeconds", "86400"], check=True)
                subprocess.run([nssm_path, "set", service_name, "AppRotateBytes", "10485760"], check=True)
                changes.append("  + Rotation des logs activée (quotidienne / 10MB)")

            return changes

        try:
            if service_exists():
                print(f" Le service '{service_name}' est déjà installé.")

                # Vérifier et compléter les logs manquants
                changes = configure_logs()

                if changes:
                    print("⚙ Logs manquants détectés, configuration ajoutée :")
                    for c in changes:
                        print(c)

                    # Redémarrer le service pour appliquer les changements
                    print(" Redémarrage du service pour appliquer les changements...")
                    subprocess.run([nssm_path, "restart", service_name], check=True)
                    print(" Service redémarré avec succès.")
                else:
                    print(" Les logs sont déjà correctement configurés. Aucun changement nécessaire.")

            else:
                print(f" Installation du service '{service_name}'...")

                # 1. Création du service
                subprocess.run([nssm_path, "install", service_name, app_exe], check=True)

                # 2. Dossier de démarrage
                subprocess.run([nssm_path, "set", service_name, "AppDirectory", app_dir], check=True)

                # 3. Redémarrage automatique
                subprocess.run([nssm_path, "set", service_name, "AppRestartDelay", "1000"], check=True)

                # 4. Configuration des logs
                configure_logs()

                # 5. Lancement
                subprocess.run([nssm_path, "start", service_name], check=True)

        except subprocess.CalledProcessError as e:
            print(f" Erreur verify_esystem_and_install_service: {e}")
            import traceback
            traceback.print_exc()
    def esystem_install_service(self):
        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".nssm")

        nssm_path = os.path.join(source_path, 'win64', 'nssm.exe')
        app_exe = r"C:\Program Files\ecole-serve\app.exe"
        service_name = "Esystem"
        app_dir = os.path.dirname(app_exe)

        # Dossier des logs
        log_dir = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_stdout = os.path.join(log_dir, "esystem_output.log")
        log_stderr = os.path.join(log_dir, "esystem_error.log")

        try:
            # 1. Création du service
            subprocess.run([nssm_path, "install", service_name, app_exe], check=True)

            # 2. Dossier de démarrage
            subprocess.run([nssm_path, "set", service_name, "AppDirectory", app_dir], check=True)

            # 3. Fichier log stdout
            subprocess.run([nssm_path, "set", service_name, "AppStdout", log_stdout], check=True)

            # 4. Fichier log stderr
            subprocess.run([nssm_path, "set", service_name, "AppStderr", log_stderr], check=True)

            # 5. Rotation des logs (optionnel) — évite que les fichiers grossissent indéfiniment
            subprocess.run([nssm_path, "set", service_name, "AppRotateFiles", "1"], check=True)
            subprocess.run([nssm_path, "set", service_name, "AppRotateSeconds", "86400"], check=True)  # Rotation quotidienne
            subprocess.run([nssm_path, "set", service_name, "AppRotateBytes", "10485760"], check=True)  # Max 10 MB

            # 6. Redémarrage automatique en cas de crash
            subprocess.run([nssm_path, "set", service_name, "AppRestartDelay", "1000"], check=True)

            # 7. Lancement du service
            subprocess.run([nssm_path, "start", service_name], check=True)

            print(f"Service '{service_name}' installé et démarré avec succès !")
            print(f"Logs output : {log_stdout}")
            print(f"Logs erreur : {log_stderr}")

        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation : {e}")

    # def esystem_install_service(self):
    #     # Chemins absolus (à adapter selon ton installation)
    #     self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
    #     source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".nssm")
    
    #     nssm_path = os.path.join(source_path,'win64','nssm.exe') #r"C:\OutilsServeur\nssm-2.24\win64\nssm.exe"
    #     app_exe = r"C:\Program Files\ecole-serve\app.exe"
    #     service_name = "Esystem"
    #     app_dir = os.path.dirname(app_exe)

    #     try:
    #         # 1. Création du service
    #         subprocess.run([nssm_path, "install", service_name, app_exe], check=True)
            
    #         # 2. Définition du dossier de démarrage (crucial pour les bases de données)
    #         subprocess.run([nssm_path, "set", service_name, "AppDirectory", app_dir], check=True)
            
    #         # 3. Optionnel : Redémarrage automatique en cas de crash après 1 seconde
    #         subprocess.run([nssm_path, "set", service_name, "AppRestartDelay", "1000"], check=True)
            
    #         # 4. Lancement immédiat du service
    #         subprocess.run([nssm_path, "start", service_name], check=True)
            
    #         print(f"Service '{service_name}' installé et démarré avec succès !")
            
    #     except subprocess.CalledProcessError as e:
    #         print(f"Erreur lors de l'installation : {e}")
    
    

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
        ca_path = r"C:\Program Files\ecole-serve\nginx\certs\ca.pem"
        while True:
            name, first_name, email, password = self.ask_for_user_data()

            url = f"https://aplekol360.local/api/v1/first-account"#first-account
            
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
                
                _conf_path = os.path.join(self.current_project, "nginx", "conf")
                url_fill = f"https://aplekol360.local/api/v1/first-account-fill"
                fill_data = requests.get(url_fill,verify=ca_path)
                if fill_data.status_code !=200: 
                    print(f"\n [x]   Erreur {fill_data.json()} : {fill_data.status_code}")
                    return
                response = requests.post(url, json=data, headers=headers,verify=ca_path)
                response_status_code=response.status_code
                # client_data_ = None

                if response_status_code == 200:
                    connect_code_status =None
                    base_url=f"https://aplekol360.local/api/v1/"

                
                    urls = f"https://aplekol360.local/api/v1/client-authorisation-connect"
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
        
 
        self.extract_dir = os.path.join(self.current_dir, f"mysql-{self.mysql_version}-winx64")
        self.bin_dir = os.path.join(self.extract_dir, "bin")
        self.data_dir = os.path.join(self.extract_dir, "data")
        self.my_ini_path = os.path.join(self.extract_dir, "my.ini") 
        self.service_name = "MySQLEcole"
        self.file_path = os.path.join(self.extract_dir, "init.sql")
        self.ssl_dir = os.path.join(self.extract_dir, "certs")

        if not os.path.exists(self.ssl_dir):
            os.makedirs(self.ssl_dir, exist_ok=True)

            os.makedirs(os.path.join(self.extract_dir, 'logs'), exist_ok=True)
        

   
    def mysql_ssl_path(self):
        server_name ="localhost" 
        server_ip = "127.0.0.1" 

        # san_file = os.path.join(self.ssl_dir, 'san.cnf')

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
        

    def create_my_ini(self):
        """Crée le fichier my.ini et génère les certificats SSL de manière sécurisée"""
        print("\n[ + ] Création du fichier .ini et génération des certificats SSL...")

        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        source_path = os.path.join(self.user_profile, "AppData", "Local", ".ecole_360", ".ssl_server")

        try:
            cert_files = ['server-key.pem', 'server-cert.pem', 'client-key.pem', 'client-cert.pem','ca.pem']
            
            for cert_file in cert_files:
                source_file = os.path.join(source_path, cert_file)
                dest_file = os.path.join(self.ssl_dir, cert_file)
                
                if os.path.exists(source_file):
                    shutil.copy2(source_file, dest_file)
                    # print(Fore.GREEN + f" [ok]   Copié: {cert_file}")
                else:
                    print(Fore.YELLOW + f" [warn] Fichier non trouvé: {source_file}")
                    
        except Exception as e:
            print(f" [x]   Erreur copie certificats: {e}")
            return False
        
        try:
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
            # ALTER USER 'root'@'localhost' IDENTIFIED BY '@#Lekol3&0';
            # CREATE USER 'replicator'@'%' IDENTIFIED WITH caching_sha2_password BY 'Repl!c@t0rP@ss';
            # GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
            # FLUSH PRIVILEGES; REQUIRE SSL
            # """
            scripts = f"""
                CREATE USER IF NOT EXISTS 'root'@'127.0.0.1' IDENTIFIED WITH caching_sha2_password BY '3&0@#Lekol';
                GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' WITH GRANT OPTION;
                ALTER USER 'root'@'localhost' IDENTIFIED BY '3&0@#Lekol';
                FLUSH PRIVILEGES;
                """
            self.file_path = os.path.join(self.extract_dir, "init.sql")
            
            with open(self.file_path, "w", encoding='utf-8') as f:
                f.write(textwrap.dedent(scripts)) 

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


# DELETE FROM sym_trigger WHERE trigger_id = 'trg_migrations';
# DELETE FROM sym_trigger_router WHERE trigger_id = 'trg_migrations';

# mysql -u user_pyside -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lekol360 < "C:\Users\fritz\OneDrive\Desktop\gestion ecole client\04_03_2026.sql"

# mysqldump -u user_pyside -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lekol360 > "C:\Users\fritz\OneDrive\Desktop\gestion ecole client\04_03_2026_dump.sql"


# mysqldump -u root -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY lemignon > "C:\bckup_mignon_before_all_student_16_02_2026.sql"

# mysql -u user_pyside -p --host=127.0.0.1 --ssl-ca="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" --ssl-cert="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" --ssl-key="C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem" --ssl-mode=VERIFY_IDENTITY test< "C:\Users\fritz\OneDrive\Desktop\mysql_table_11_02_2026.sql"


# lekol360
# @#Lekol3&0
# 3&0@#Lekol

# Exemple pour automatiser dans ton code Python
# from alembic.config import Config
# from alembic import command

# def run_migrations():
#     alembic_cfg = Config("alembic.ini")
#     command.upgrade(alembic_cfg, "head")
   
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
                subprocess.run([os.path.join(self.bin_dir, "mysqld"), "--initialize",f"--init-file={self.file_path}", "--console"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                    check=True)
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

    
    def install_mysql_as_service1(self):
        """Installe MySQL en tant que service Windows"""
        # if not self.is_installed_service("MySQLEcole"):
        try:
            print("\n [ + ]   Installation de MySQL en tant que service...")

            cmd = [
                os.path.join(self.bin_dir, "mysqld.exe"),
                "--install", self.service_name,
                f"--defaults-file={self.my_ini_path}"
            ]
            subprocess.run(cmd, check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print(Fore.GREEN + "\n [ ok ]   Service MySQL installé avec succès!")
        except Exception as e:
            print(f"\n [x]   Erreur lors de l'installation du service MySQL : {e}")

    def install_mysql_as_service(self):
        """Installe MySQL proprement avec gestion des espaces"""
        try:
            print("\n [ + ]   Installation du service MySQL...")
            # On prépare le chemin complet avec des guillemets pour Windows
            exe_path = os.path.join(self.bin_dir, "mysqld.exe")
            
            # Commande SC plus fiable pour les chemins complexes
            cmd = f'sc create "{self.service_name}" binPath= "\\"{exe_path}\\" --defaults-file=\\"{self.my_ini_path}\\" {self.service_name}" start= auto'
            
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            print(Fore.GREEN + " [ ok ]   Service MySQL installé avec succès!")
        except Exception as e:
            print(f" [x]   Erreur lors de l'installation : {e}")
    

    def start_mysql_service(self):
        """Démarre le service proprement avec indicateur de progression"""
        import time
        import sys

        try:
            # ÉTAPE A : On nettoie d'abord au cas où un mysqld.exe fantôme tourne
            subprocess.run("taskkill /F /IM mysqld.exe /T", shell=True, capture_output=True)
            
            print(f"\n [ + ]   Démarrage de {self.service_name} ", end="", flush=True)

            # ÉTAPE B : On lance le service Windows
            subprocess.Popen(["net", "start", self.service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # ÉTAPE C : Boucle de vérification (les fameux points)
            for i in range(25):
                # On vérifie si le service tourne vraiment avec 'sc query'
                check = subprocess.run(["sc", "query", self.service_name], capture_output=True, text=True)
                if "RUNNING" in check.stdout:
                    print(Fore.GREEN + " [ ok ]")
                    return True
                
                print("*", end="", flush=True)
                time.sleep(3)

            print(Fore.RED + "\n [ x ]   Le service n'a pas démarré à temps.")
            return False

        except Exception as e:
            print(Fore.RED + f"\n [ x ]   Erreur : {e}")

    def start_mysql_service1(self):
        """Démarre le service MySQL"""
        try:
            print("\n [ + ]   Démarrage du service MySQL...") 
            subprocess.Popen([os.path.join(self.bin_dir, 'mysqld.exe'), f"--defaults-file={self.my_ini_path}"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            subprocess.Popen(["net", "start", self.service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        filepath = os.path.join("data", self.download_path)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                os.remove(self.file_path)
                self.file_path = os.path.join(self.extract_dir, "init.sql")
                scripts = f"""
                     sql content
                            """
                with open(self.file_path, "w", encoding='utf-8') as f:
                    f.write(textwrap.dedent(scripts))
                # On ne print rien ou on utilise un logger discret 
                subprocess.run(["taskkill", "/F", "/IM", "mysqld.exe", "/T"], capture_output=True)
            except OSError as e:
                print(f"Erreur lors de la suppression : {e}")

    def prompt_for_password_and_db(self):
        """Demander à l'utilisateur un mot de passe et un nom de base de données"""
        self.db_name = 'lekol360' #input("\n [+]  Entrez le nom de la base de données à créer : ")

        self.new_password = '@#Lekol3&0' # self.masked_input("\n [+]  Entrez le nouveau mot de passe de la base: ")
        # Vérification de la longueur du mot de passe
        while len(self.new_password) < 6:
            print("\n [+]  Le mot de passe doit contenir au moins 6 caractères.")
            self.new_password =  self.masked_input("\n [+]  Entrez le nouveau mot de passe de la base: ")
        
        # if self.db_name != "lekol360":
        mysql_admin = MySQLAdmin(
            service_name=self.service_name,
            bin_dir=self.bin_dir,
            my_ini_path=self.my_ini_path,
            extract=self.ssl_dir
        )

        mysql_admin.set_root_password(self.new_password, self.db_name)


    def return_data(self):
        return [self.new_password, self.db_name]
    


    def get_resource_path(self, relative_path: str)-> str:
        
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
        if not os.path.exists(os.path.join(self.current_dir,self.zip_file)):
            self.download_mysql()

        self.fix_permissions()

        self.extract_mysql()

        self.create_my_ini()

        # self.setup_mysql_ssl()

        self.fix_permissions()

        self.initialize_database()
        
        self.install_mysql_as_service()
    

        self.start_mysql_service()
         
        
        self.prompt_for_password_and_db()
 
        self.clean_up()

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
            # subprocess.run(["net", "start", self.service_name], timeout=30, check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["net", "stop", self.service_name], timeout=30, check=False)
            subprocess.run(["net", "start", self.service_name], timeout=30, check=True)


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
        
    def ensure_services_running(self, services, force=False):
        for service in services:
            if force:
                subprocess.run(["net", "stop", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["net", "start", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                
            result = subprocess.run(["sc", "query", service], capture_output=True, text=True)
            
            
            if "STOPPED" in result.stdout:
                print(f"\n [+] Démarrage du service {service}...")
                subprocess.run(["net", "start", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif "RUNNING" in result.stdout:
                print(f"\n [ok]  Le service {service} est déjà en cours d'exécution.")
            else:
                subprocess.run(["taskkill", "/F", "/IM", "mysqld.exe", "/T"], 
                           capture_output=True, text=True, shell=True)  
                services_a_verifier = ["MySQLEcole"]
                self.ensure_services_running(services=services_a_verifier)

    def get_service_status(self,service_name):
        try:
            # On lance 'sc query nom_du_service'
            result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True, check=True)
            
            if "RUNNING" in result.stdout:
                return "RUNNING"
            elif "STOPPED" in result.stdout:
                return "STOPPED"
            else:
                return "INSTALLED" # Existe mais état intermédiaire
                
        except subprocess.CalledProcessError:
            return "NOT_INSTALLED" # 'sc query' renvoie une erreur si le service n'existe pas

    
    def set_root_password(self, new_password, db_name):
        # ... tes vérifications de service ...
        pass_word = '3&0@#Lekol'
        # Prépare les arguments SSL une seule fois pour la lisibilité
        ssl_args = [
            f'--ssl-ca={Path(self.extract_dir,"ca.pem").as_posix()}',
            f'--ssl-cert={Path(self.extract_dir,"client-cert.pem").as_posix()}',
            f'--ssl-key={Path(self.extract_dir,"client-key.pem").as_posix()}'
        ]          

        # self.check_network_configuration()

        print(f"\n [ + ]   Connexion et configuration de la base de donnees ...")            

        mysql_path = os.path.join(self.bin_dir, "mysql.exe")           
        

        if not os.path.exists(mysql_path):
            print(f" [x] ERREUR: mysql.exe introuvable à l'emplacement {mysql_path}")
            return
        
        # print(f"\n[*] Tentative de connexion via : {mysql_path}")

        # 2. Boucle d'attente : On attend que le service démarre vraiment
        service_name = "MySQLEcole"
        status = self.get_service_status(service_name)

        if status == "NOT_INSTALLED":
            print(f"❌ Erreur : Le service {service_name} n'est pas installé sur ce système.")
            # Ici, tu pourrais appeler ta fonction d'installation
        elif status == "STOPPED":
            print(f"⚠️ Le service {service_name} est arrêté. Tentative de démarrage...")
            # print(f"🔄 Tentative de redémarrage du service...")
            try:
                services_a_verifier = ["MySQLEcole"]
                self.ensure_services_running(services=services_a_verifier)
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(e)
                    
            # Petit délai pour laisser Windows libérer le port 3307
            max_retries = 20
            for i in range(max_retries):
                try:
                    subprocess.run([
                        mysql_path, '-u', 'root', '-P', '3307', '-h', 'localhost', '-e', 'status'
                    ], check=True, capture_output=True, timeout=5)
                    print("✅ MySQL est prêt !")
                    break
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    print("*", end="", flush=True)
                    time.sleep(20)
        else:
            pass
    

        # Maintenant on tente la connexion seulement si le service tourne
        if self.get_service_status(service_name) == "RUNNING":
            
            # Base de la commande mysql
            base_cmd = [mysql_path, '-u', 'root', f'-p{pass_word}', '-P', '3307', '-h', 'localhost'] + ssl_args

            try:
                # 1. Création Root & Privilèges (Utilise pass_word actuel)
                sql_init = f"CREATE USER IF NOT EXISTS 'root'@'localhost' IDENTIFIED BY '{pass_word}'; GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION; FLUSH PRIVILEGES;"
                subprocess.run(base_cmd + ['-e', sql_init], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

                # 2. Création de l'utilisateur applicatif user_pyside (Avant de changer le pass root !)
                sql_app_user = """
                CREATE USER IF NOT EXISTS 'user_pyside'@'%' IDENTIFIED BY '@#Janvier21';
                ALTER USER 'user_pyside'@'%' REQUIRE X509;
                GRANT ALL PRIVILEGES ON *.* TO 'user_pyside'@'%';
                CREATE DATABASE IF NOT EXISTS {db_name};
                FLUSH PRIVILEGES;
                """.replace('{db_name}', db_name)
                
                subprocess.run(base_cmd + ['-e', sql_app_user], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

                # 3. EN DERNIER : Changer le mot de passe Root
                # Une fois cela fait, base_cmd ne marchera plus !
                sql_final = f"ALTER USER 'root'@'localhost' IDENTIFIED BY '{new_password}'; FLUSH PRIVILEGES;"
                subprocess.run(base_cmd + ['-e', sql_final], check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

                print(Fore.GREEN + "\n [ ok ] Configuration terminée avec succès.")

            except subprocess.CalledProcessError as e:
                import traceback
                traceback.print_exc()
                print(f"Erreur lors de l'exécution SQL : {e}")
                return
        else:
            service = self.get_service_status(service_name)
            print(f"l'etat du service {service_name} est {service}")
            return



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
import httpx

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
        # print(f"base__url  {self.base__url}")
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
            service_label = QLabel("Service MySQL" if service == "MySQLEcole" else "Service Nginx")
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

        self.fram_activate_btn =  QFrame()
        self.layout_btn_active = QVBoxLayout(self.fram_activate_btn)
        self.label1  = QLabel()
        self.btn_verify = QPushButton("Vérifier la clé")
        self.btn_verify.setCursor(Qt.PointingHandCursor)


        self.fram_activate_info =  QFrame()
        self.layout_info = QHBoxLayout(self.fram_activate_info)
        self.key_input_payment = QLineEdit()
        self.key_input_payment.setPlaceholderText("Identifiant du paiement")        
        self.layout_info.addWidget(self.key_input_payment)
        

        self.btn_verify_online = QPushButton("Active online")
        self.btn_verify_online.setCursor(Qt.PointingHandCursor)

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

        self.btn_verify_online.setStyleSheet("""
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
        
        url_copy = base_url
        # Même lien pour le bouton "Active online" et le texte d'alerte
        # ci-dessous — avec la MAC de CETTE machine (le serveur), pas celle
        # d'un client, puisque c'est le serveur qui doit être réactivé.
        renew_url = f"https://infini-software.cloud/renouveler?mac={get_mac_address()}"
        self.btn_verify.clicked.connect(lambda: self.verifier_cle(url_copy))
        self.btn_verify_online.clicked.connect(lambda: self.verify_online(renew_url, url_copy))
         
        self.fram_activate_h =  QFrame()
        self.layout_h_active = QHBoxLayout(self.fram_activate_h)

        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.key_input)
        self.layout_btn_active.addWidget(self.label1)
        self.layout_btn_active.addWidget(self.btn_verify)

        self.layout_h_active.addWidget(self.fram_activate)
        self.layout_h_active.addWidget(self.fram_activate_btn) 
 
 
        self.alert_frame = QFrame() 

        layout_label = QHBoxLayout(self.alert_frame)

        info_icon = QLabel("ℹ️")

        # Texte avec lien HTML intégré
        info_text = QLabel(
            'Pour continuer à utiliser toutes les fonctionnalités,<br>' # <br> force le retour à la ligne
            f'veuillez <a href="{renew_url}" style="color: #D32F2F;">'
            'cliquer ici pour payer et récupérer votre clé d\'activation</a>.'
        )

        info_text.setStyleSheet("""
            QLabel {
                border: none; 
                color: #01579B; 
                line-height: 1.5; /* Ajoute de l'espace entre les lignes */
            }
        """)

        # Configuration cruciale pour le lien
        info_text.setWordWrap(True)
        info_text.setOpenExternalLinks(True)
        info_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        info_text.setStyleSheet("border: none; color: #01579B; font-weight: bold;")
        info_text.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout_label.addWidget(info_icon)
        layout_label.addWidget(info_text, 1)
                

        self.layout_info.addWidget(self.btn_verify_online)

        main_layout.addLayout(v_layout_service)
        layout.addLayout(body_layout)
        if not is_license_valid():
            layout.addWidget(self.fram_activate_h)
            layout.addWidget(self.alert_frame)
            layout.addWidget(self.fram_activate_info)
        # layout.addWidget(self.fram_activate_online)
        self.setLayout(layout)

    def verifier_cle(self, url):
        user_input_key = self.key_input.text().strip()
        mac = get_mac_address()
        result = verify_activation_key_graphic(provided_key=user_input_key, mac_address=mac, url=url)
        if result is True:
            from PySide6.QtCore import QSettings
            settings = QSettings("MonAppServer", "Licence")
            enc_key = generate_fernet_key(mac)
            expiration_date_ = decrypt_value(settings.value("expiration_date", ""), enc_key)
            self.fram_activate.setHidden(True)
            QMessageBox.information(self, "Succès", f"Clé valide. Expire le {expiration_date_}")
            print("✅ Clé valide.")
        elif result is None:
            print("❌ Erreur serveur lors de l'activation.")
            QMessageBox.critical(self, "Erreur", "Impossible de contacter le serveur local. Assurez-vous que le serveur est démarré, puis réessayez.")
        else:
            print("❌ Clé invalide.")
            QMessageBox.critical(self, "Erreur", "Clé invalide ou expirée.")

    def verify_online(self, renew_url, local_url):
        payment_id = self.key_input_payment.text().strip()
        if not payment_id:
            import webbrowser
            webbrowser.open(renew_url)
            return
        try:
            r = requests.get(
                "https://infini-software.cloud/api/licence/payer/confirmer",
                params={"payment_id": payment_id},
                timeout=15,
            )
            if r.status_code != 200:
                QMessageBox.warning(self, "Erreur", f"Paiement introuvable ({r.status_code}).")
                return
            data = r.json()
            if data.get("status") != "success":
                QMessageBox.warning(self, "Erreur", "Paiement non confirmé par infini-software.")
                return
            key = data.get("key", "")
            expiration_date = data.get("expiration_date", "")
            days_valid = data.get("days_valid")
            from PySide6.QtCore import QSettings
            settings = QSettings("MonAppServer", "Licence")
            enc_key = generate_fernet_key(get_mac_address())
            old_key = decrypt_value(settings.value("activation_key", ""), enc_key)
            try:
                requests.post(
                    f"{local_url}log-activate",
                    json={"last_key": old_key, "new_key": key, "exprired_at": expiration_date},
                    timeout=10,
                    verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem",
                ).raise_for_status()
            except Exception as e:
                print(f"Log-activate POST failed: {e}")
                QMessageBox.critical(self, "Erreur", "Impossible de contacter le serveur local. Assurez-vous que le serveur est démarré, puis réessayez.")
                return
            apply_remote_licence(key, expiration_date, days_valid)
            self.fram_activate.setHidden(True)
            QMessageBox.information(self, "Succès", f"Licence activée. Expire le {expiration_date}.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de contacter infini-software : {e}")

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
            
            data = requests.get(url, timeout=35,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem")
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



    def toggle_authorization(self, client_id, url, button):
        print(url)
        if client_id is None:
            print("Erreur : client_id est None, abandon de la requête.")
            return
        cert_path = r"C:/Program Files/ecole-serve/nginx/certs/ca.pem" 
        pem, b64 = self.get_server_cert_content(cert_path)
        payload = {"id": client_id, "certi_key": b64}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.token_access:
            headers['X-Admin-Token'] = self.token_access
        print(url,client_id)

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=45,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem")
            response_data = response.json()
            print(response_data)
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
                if response_data and "detail" in response_data and '422' in response_data.get("detail"):
                    self.request_access_for_delete(client_id, button)
                else: 
                    # button.setChecked(not new_state)
                    self.show_error_message("Update failed")
                    print("Erreur:", response_data)
                    return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")


    def request_access_for_delete(self,client_id, button):
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

            self.client_id=client_id
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
        log_url = f"{self.base__url}client-authorisation-connect"#autorisation-access 
        refresh_url = f"{self.base__url}client-authorisation-connect"#autorisation-access 
        self.delete.setDisabled(True)
        self.delete.setText("Traitement en cours ...")
        try:
            response = requests.post(
            log_url,
            json={
                'email':email,
                'password':password, 
                "login_as": "as_desktop",
                "id":self.client_id,
                'permission':"Modifier personnel" 
                },
            timeout=50,verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem"
        )
            # with httpx.Client(verify="C:/Program Files/ecole-serve/nginx/certs/ca.pem") as client:
            #     response = client.post(
            #         log_url,
            #         json={
            #             'email': email,
            #             'password': password,
            #             'id': self.client_id,
            #             'permission': "Modifier personnel"
            #         },
            #         timeout=50.0
            #     )
            #     response.raise_for_status()
            response_data = response.json()
            if response.status_code == 200:
                self.delete.setDisabled(False)
                self.delete.setText("Confirmer")
                # self.token_access=response_data['token']
                self.refresh_client_data(refresh_url)
                self.dialog_delete.close() 
                new_status = response_data.get('authorisation', 0)
                if new_status == 1:                    
                    QMessageBox.information(
                    None,
                    "Succès",
                    "Autorisation accordée!"
                )
                else:
                    QMessageBox.information(
                    None,
                    "Succès",
                    "Autorisation enlevée!"
                )
                    
                # print(response_data)
                return response_data
            else:
                self.delete.setDisabled(False)
                self.delete.setText("Confirmer")
                print(response_data)
                if response_data and 'detail' in response_data:
                    errors = response_data.get('detail')
                    QMessageBox.critical(None, "Error", errors)
                    # print('users not update')
        except Exception as e:
            self.delete.setDisabled(False)
            self.delete.setText("Confirmer")
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


        self.continuer = QPushButton("Continuer")
        if public_key:
            self.input_public_local_key.setText(public_key)
            self.continuer.setHidden(True)
        self.layout_input_public_local_key.addWidget(self.input_public_local_key)

        self.input_public_local_key = CopyOnFocusLineEdit(self.input_public_local_key)


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
from PySide6.QtWidgets import QMessageBox
import os, subprocess, ctypes
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
            f.write(f"[{datetime.now()}] {message}\n")

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
                Address = 10.50.0.2/24
               # DNS = {dns}
                ListenPort = {self.port}

                [Peer]
                PublicKey = {public_key}
                AllowedIPs = 10.50.0.0/0
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



