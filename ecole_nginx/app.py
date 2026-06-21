import ctypes
import sys
import os
import io
import uvicorn
import socket
from pathlib import Path
import time  
from Controllers.Main_run import Main_run
from Helper.Ip_manager import Ip_manager
from Helper.manage_activate import Manage_active
import threading 
import requests
import subprocess

# from Helper.server_key_generate import delete_key, is_license_valid 


# Appuie sur Win + R, tape services.msc et valide.


# Cherche le service : Publication des ressources de découverte de fonctions (Function Discovery Resource Publication)
 
# netsh advfirewall firewall add rule name="Serveur Ecole (Nginx)" dir=in action=allow protocol=TCP localport=80,443
# netsh advfirewall firewall add rule name="Discovery mDNS" dir=in action=allow protocol=UDP localport=5353
# netsh advfirewall firewall show rule name="Serveur Ecole (Nginx)"
# netsh advfirewall firewall delete rule name="Serveur Ecole (Nginx)"
def check_nginx(service):
    """ Vérifie si un service MySQL existe """
    # print(service)
    try:
        result = subprocess.run(
            ["sc", "query", service], capture_output=True, text=True
        )
        # print(result.stdout)
        return service in result.stdout #"NginxAplekol"
    except Exception as e:
        # print(f" Erreur lors de la vérification du service {service}: {e}")
        return False

def is_app_installed():
    """Vérifie si l'application est déjà installée"""
    config_path = Path("C:\\Program Files\\ecole-serve\\app.exe")  
    return config_path.exists() and check_nginx("NginxAplekol") and check_nginx("MySQLEcole") 


def run_as_admin_if_needed():
    """Demande les droits admin seulement si nécessaire"""
    print("Ce script nécessite les droits administrateur. Redémarrage...")
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

def run_as_admin():
    """ Relance le script en mode administrateur si ce n'est pas déjà le cas. """
    if ctypes.windll.shell32.IsUserAnAdmin():
        return  # Déjà en mode admin, on continue

    print("Votre adresse ip a ete change Redémarrage en mode administrateur...")
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

def get_server_ip_():
    try: 
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        if not get_local_ip().startswith('127.'):
            if get_local_ip().startswith('192.'):
                return get_local_ip()
            elif get_local_ip().startswith('10.1'):
                return get_local_ip()
            elif ip_address.startswith('10.'):
                return ip_address
            else:
                return ip_address
    except Exception as e:
        print(f"Erreur lors de la récupération de l'adresse in app IP: {e}")
        return None
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # pas besoin que ça marche vraiment
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"
    
ip_address = get_server_ip_() 

# Exiger le mode admin
if not is_app_installed():
    run_as_admin()

def check_mysql_prerequisites():
    dlls_needed = [
        "msvcp140.dll", 
        "vcruntime140.dll", 
        "vcruntime140_1.dll"
    ]
    
    missing = []
    system32 = os.path.join(os.environ['SystemRoot'], 'System32')
    
    for dll in dlls_needed:
        path = os.path.join(system32, dll)
        if not os.path.exists(path):
            missing.append(dll)
             
    if not missing:
        # icacls "C:\Users\server\AppData\Local\System\cache\static" /grant Everyone:F
        print("✅ Système prêt : Toutes les DLL critiques sont présentes.")
        return True
    else:
        print(" ERREUR : Il manque des composants système.")
        print(f"Fichiers manquants : {', '.join(missing)}")
        print("\nACTION REQUISE :")
        print("L'administrateur doit installer 'Microsoft Visual C++ Redistributable 2015-2022'")
        print("Lien : https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False
     
def disable_quick_edit():
    """Désactive le mode QuickEdit du terminal Windows pour éviter les gels au clic."""
    if os.name == 'nt':  # Uniquement si on est sur Windows
        try:
            kernel32 = ctypes.windll.kernel32
            # ENABLE_EXTENDED_FLAGS (0x0080) désactive le QuickEdit
            # On récupère le handle de l'entrée standard (STD_INPUT_HANDLE = -10)
            handle = kernel32.GetStdHandle(-10)
            kernel32.SetConsoleMode(handle, 0x0080)
            print("INFO: QuickEdit Mode désactivé automatiquement.")
        except Exception as e:
            print(f"WARNING: Impossible de désactiver QuickEdit : {e}")
 

def start_api(): 
    from app.main import app
    uvicorn.run(
    app,           
    host="127.0.0.1",
    port=9001,
    # reload=True,           
    # workers=4,             
    timeout_keep_alive=75,
    log_level="warning"
    ) 

def kill_port_owner(port):
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

def launch_and_wait_for_api(): 
    # kill_port_owner(9001)
    
    # 1. Lancement du thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()


    # 2. Boucle d'attente intelligente
    api_url = "http://127.0.0.1:9001/api/v1/health" # Ou une route simple comme /health
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
            time.sleep(10) # Attendre 1 seconde avant de réessayer
            print(f"   (Tentative {retry_count}/{max_retries}...)")

    if not api_ready:
        print("❌ Erreur : L'API n'a pas démarré à temps.")


if __name__ == "__main__":
    # disable_quick_edit()
    # kill_port_owner('9001')
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    try: 
        start_time = time.time()    
        
        # check_mysql_prerequisites() 
        if not check_mysql_prerequisites():             
            input("\nVeuillez installer le redistribuable Visual C++")
            input("\nAppuyez sur Entrée pour quitter...")
            exit(1)
        if not is_app_installed():   
            print("Installation et configuration du serveur !")
        else:
            if ip_address !=  Ip_manager().get_server_ip():
                # run_as_admin()
                pass
            # launch_and_wait_for_api() 


        runner = Main_run()
        runner.install_and_config()


            # print("Démarrage du serveur...")
        # if is_app_installed(): 
        #     api_thread.join()
        
        print(f"⏳ Temps total d'exécution : {time.time() - start_time:.2f} secondes")
    except KeyboardInterrupt:
        print("\n\n⚠️ Installation annulée par l'utilisateur (Ctrl+C).")
    except Exception as e: 
        print(f"------ : {e}")
        import traceback
        traceback.print_exc()
# alembic stamp head

# alembic upgrade head
# alembic stamp dc9c98be1a37
# alembic stamp 861e3478f0cb
# alembic history
# alembic current
# alembic revision -m "ajouter_nom_dutilisateur_a_users"
# alembic revision  -autogenerate -m "ajouter_table"
# alembic revision --autogenerate -m "ajouter_table"


# mysqldump -u root -p ta_base > dump.sql
# Ou si tu es sur Windows avec XAMPP/WampServer :
# bashC:\xampp\mysql\bin\mysqldump.exe -u root -p ta_base > dump.sql
# 2. Ensuite lance le script :
# bashpython atom.py dump.sql > dump_anonymise.sql
# Le fichier dump.sql doit être dans le même dossier C:\ecole_nginx\ que ton script.

# scp "C:\ecole_nginx\frontend\dist\dist.zip" root@82.29.153.24:/var/www/institutionlemignon.com/public_html/

# # Voir les logs en temps réel
# sudo journalctl -u lemignon-api.service -f

# # Voir les dernières lignes
# sudo journalctl -u lemignon-api.service -n 100

# # Voir les logs depuis le dernier démarrage
# sudo journalctl -u lemignon-api.service -b

# # Voir les erreurs uniquement
# sudo journalctl -u lemignon-api.service -p err



# UPDATE paiements
# SET
#   updated_at = '2026-03-12 13:26:19',
#   last_paiement_key = '3bd039a0-c1cc-4185-b6e3-f46c6dae5ef5',
#   mois = JSON_OBJECT(
#     'mois', JSON_OBJECT(
#       'Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76', 31000,
#       'Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76', 12500
#     )
#   ),
#   paiement_details = JSON_SET(
#     JSON_REMOVE(
#       paiement_details,
#       '$.paiement_details.mois."Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76"',
#     ), 
#     '$.paiement_details.info_paiement."12-03-2026 09:20"',
#     CAST('{
#       "depot": 12500.0,
#       "status": 0,
#       "total_verse": 55000,
#       "total_annuel": 68500,
#       "employer": "Claudia",
#       "devise": "GDES",
#       "aide_financiere": "Aucune",
#       "status_paiement": ["Acqt: 2ème Versement", "Avns: 3ème Versement"],
#       "edit_by_id": "",
#       "return_by_id": "",
#       "edit_by": "",
#       "return_by": "",
#       "avance": "12500 + 11500",
#       "depot_et_avance": 11500,
#       "balance": 1000,
#       "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500
#     }' AS JSON),
#     -- Mettre à jour le mois interne
#     '$.paiement_details.mois',
#     CAST('{
#       "Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000,
#       "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500
#     }' AS JSON)
#   )

# WHERE id = 'd6c1c734-88a2-45d6-af58-00f8132e2f68';

# UPDATE paiements
# SET 
#   last_paiement_key = '2a8b3904-ff8d-45c2-9820-a69d83260a48',
#   mois = '{"mois": {"Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000, "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}}',
#   paiement_details = JSON_SET(
#     JSON_REMOVE(
#       paiement_details,
#       '$.paiement_details.info_paiement."12-03-2026 09:20"',
#       '$.paiement_details.mois."Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76"'
#     ),
#     '$.paiement_details.info_paiement."12-03-2026 09:20"',
#     CAST('{"depot": 12500.0, "status": 0, "total_verse": 55000, "total_annuel": 68500, "employer": "Claudia", "devise": "GDES", "aide_financiere": "Aucune", "status_paiement": ["Acqt: 2eme Versement", "Avns: 3eme Versement"], "edit_by_id": "", "return_by_id": "", "edit_by": "", "return_by": "", "avance": "12500 + 11500", "depot_et_avance": 11500, "balance": 1000, "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}' AS JSON),
#     '$.paiement_details.mois',
#     CAST('{"Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000, "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}' AS JSON)
#   )
# WHERE id = 'd6c1c734-88a2-45d6-af58-00f8132e2f68';

# ------------------------------------------------------------------------------------------------------------------+--------------------------------------+
# | d6c1c734-88a2-45d6-af58-00f8132e2f68 | 2025/2026        | c0f9525a-8bd1-4aa5-bafb-22fc2cc6420e | NULL       | NULL  | e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d | {"mois": {"Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000, "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500, "Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}} | 2025-11-10 09:48:00 | 2026-03-12 13:20:27 | d69d5d89-6cbd-4fd7-871a-eb03ec3f8280 | {"paiement_details": {"info_paiement": {"10-11-2025 09:48": {"depot": "20000", "depot_et_avance": 20000, "montant": null, "status": 0, "total_verse": 20000, "total_annuel": 68500, "employer": "Claudia", "balance": 11000, "avance": null, "status_paiement": ["Avns: 1er Versement"], "devise": "GDES", "aide_financiere": "Aucune"}, "15-12-2025 09:26": {"depot": "10000", "depot_et_avance": 30000, "montant": null, "status": 0, "total_verse": 30000, "total_annuel": 68500, "employer": "Claudia", "balance": 1000, "avance": "10000 + 20000", "status_paiement": ["Avns: 1er Versement"], "devise": "GDES", "aide_financiere": "Aucune"}, "26-01-2026 11:01": {"depot": "12500", "depot_et_avance": 11500, "montant": null, "status": 0, "total_verse": 42500, "total_annuel": 68500, "employer": "Claudia", "balance": 1000, "avance": "12500 + 30000", "status_paiement": ["Acqt: 1er Versement", "Avns: 2\u00e8me Versement"], "devise": "GDES", "aide_financiere": "Aucune", "Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000}, "12-03-2026 09:20": {"depot": 12500.0, "status": 0, "total_verse": 67500, "total_annuel": 68500, "employer": "Claudia", "devise": "GDES", "aide_financiere": "Aucune", "status_paiement": ["Acqt: 3\u00e8me Versement", "Avns: 4\u00e8me Versement"], "edit_by_id": "", "return_by_id": "", "edit_by": "", "return_by": "", "avance": "12500 + 11500", "depot_et_avance": 11500, "balance": 1000, "Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}}, "mois": {"Versement_1_8ef65c55-8166-4557-bc2f-5482d605cd76": 31000, "Versement_2_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500, "Versement_3_8ef65c55-8166-4557-bc2f-5482d605cd76": 12500}, "check_echeance": {"1er Versement": 31000, "2\u00e8me Versement": 12500, "3\u00e8me Versement": 12500, "4\u00e8me Versement": 12500}, "aide_financiere": "Aucune", "accessoires": [], "details_etudiant": {"identifiant": "1-29499", "nom": "GEROME", "prenom": "Tracy", "aide_financiere": "Aucune", "classe": "CMII A", "niveau": "Primaire", "faculte": null, "annee_academique": "2025/2026"}}} | 2a8b3904-ff8d-45c2-9820-a69d83260a48 |
