import ctypes
import sys

def run_as_admin():
    """ Relance le script en mode administrateur si ce n'est pas déjà le cas. """
    if ctypes.windll.shell32.IsUserAnAdmin():
        return  # Déjà en mode admin, on continue

    print("🔴 Ce script nécessite les droits administrateur. Redémarrage en mode administrateur...")
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit()

# Exiger le mode admin
run_as_admin()

# --- Ton code actuel commence ici ---
import time
import os
import subprocess
from Helper.manage_activate import Manage_active
from Helper.verify_key import delete_key
from Helper.Ip_manager import Ip_manager

try:
    from Controllers.Main_run import Main_run
except ImportError as e:
    print(f"❌ Erreur : Impossible d'importer 'Main_run'. Détail : {e}")
    input("Appuyez sur Entrée pour quitter...")
    sys.exit(1)

# def find_mysql_installation():
#     """ Recherche l'installation de MySQL via le registre Windows. """
#     try:
#         key_path = r"SOFTWARE\MySQL AB"
#         with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
#             for i in range(winreg.QueryInfoKey(key)[0]):
#                 subkey_name = winreg.EnumKey(key, i)
#                 subkey_path = f"{key_path}\\{subkey_name}"
#                 try:
#                     with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
#                         path, _ = winreg.QueryValueEx(subkey, "Location")
#                         if os.path.exists(path):
#                             return path
#                 except FileNotFoundError:
#                     continue
#     except FileNotFoundError:
#         pass
#     return None

# def find_mysql_from_path():
#     """ Vérifie si MySQL est accessible depuis le PATH """
#     try:
#         output = subprocess.check_output(["where", "mysqld"], shell=True, text=True)
#         return output.strip().split("\n")[0]  # Prend le premier résultat
#     except subprocess.CalledProcessError:
#         return None
    
# def find_mysql_from_path1():
#     """ Vérifie si MySQL est accessible depuis le PATH et retourne uniquement son dossier d'installation """
#     try:
#         output = subprocess.check_output(["where", "mysqld"], shell=True, text=True).strip()
#         mysql_bin = output.split("\n")[0]  # Prend le premier résultat
#         return os.path.dirname(mysql_bin)  # Retourne uniquement le dossier
#     except subprocess.CalledProcessError:
#         return None
    
# def find_mysql_root():
#     """ Trouve l'installation de MySQL en cherchant 'mysqld' dans le PATH et retourne le dossier racine """
#     try:
#         output = subprocess.check_output(["where", "mysqld"], shell=True, text=True).strip()
#         mysql_bin = output.split("\n")[0]  # Prend le premier résultat
#         mysql_root = os.path.dirname(os.path.dirname(mysql_bin))  # Remonte d'un niveau pour enlever /bin
#         return mysql_root
#     except subprocess.CalledProcessError:
#         return None

if __name__ == "__main__":
    start_time = time.time()
    # print(find_mysql_from_path(), find_mysql_from_path1(), find_mysql_root())
    # print("📦 Compilation détectée : vidage des paramètres QSettings...")
    # Manage_active().delete_manage_active()
    # Ip_manager().delete_server_ip()
    # delete_key()
    input("Appuyez sur Entrée pour quitter...")
    try:
        print("🚀 Démarrage du programme...")
        
        runner = Main_run()
        runner.install_and_config()
        print("✅ Installation et configuration terminées avec succès !")

        print(f"⏳ Temps total d'exécution : {time.time() - start_time:.2f} secondes")
        
        input("Appuyez sur Entrée pour quitter...")
    except Exception as e:
        print(e)
        input('An exception occurred')


















# import time
# import os
# import sys
# from Helper.manage_activate import Manage_active
# from Helper.verify_key import delete_key
# from Helper.Ip_manager import Ip_manager

# try:
#     from Controllers.Main_run import Main_run
# except ImportError as e:
#     print(f"❌ Erreur : Impossible d'importer 'Main_run'. Détail : {e}")
#     input("Appuyez sur Entrée pour quitter...")
#     sys.exit(1)

# if __name__ == "__main__":
#     start_time = time.time()

#     # if "PYINSTALLER_RUNNING" in os.environ:
    # print("📦 Compilation détectée : vidage des paramètres QSettings...")
    # Manage_active().delete_manage_active()
    # Ip_manager().delete_server_ip()
    # delete_key()

#     print("🚀 Démarrage du programme...")
    
#     # Exécuter l'installation et la configuration
#     # try:
#     runner = Main_run()
#     runner.install_and_config()
#     print("✅ Installation et configuration terminées avec succès !")
#     # except Exception as e:
#     #     print(f"❌ Une erreur est survenue : {e}")

#     print(f"⏳ Temps total d'exécution : {time.time() - start_time:.2f} secondes")
    
#     input("Appuyez sur Entrée pour quitter...")

