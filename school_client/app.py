import sys
import os

if sys.platform != "win32":
    # Sur Mac/Linux, le certifi bundle utilisé par défaut par `requests` ignore le
    # magasin de confiance du système (Keychain sur Mac, ca-certificates sur
    # Linux) — donc la CA auto-signée installée par
    # ecole_nginx/scripts/setup-local-https.sh n'y serait jamais reconnue. Sur
    # Windows ce comportement existait déjà via le magasin de certificats
    # Windows (certutil), donc on ne touche pas à ce cas. truststore patche le
    # SSLContext par défaut pour consulter le magasin natif de l'OS à la place.
    import truststore
    truststore.inject_into_ssl()

import requests
from PySide6.QtWidgets import QApplication, QMessageBox
from Controllers.Main import Main
import importlib
import Config

import faulthandler
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
from Helper import Ip_manager as IpManagerReload
# from Controllers.Dialog_ip import Ip_Dialog
# from Controllers.Dialog_login import Login_Dialog
from Helper.Check_data import Check_data
from Models.enregistrement import Save_data
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QByteArray

UNIQUE_KEY = "MonAppUniqueServerKey"
 
import os
import sys

def get_base_path():
    permanent_dir = os.path.dirname(os.path.realpath(sys.executable))
    temp_dir = os.environ.get("NUITKA_ONEFILE_PARENT", None)
    print(f"temp_dir  {temp_dir}")
    if temp_dir is None:
        temp_dir = os.path.abspath(".")
        
    return permanent_dir, temp_dir

# Usage
permanent_root, temp_root = get_base_path()


ALEMBIC_INI = os.path.normpath(os.path.join(temp_root, "app", "alembic.ini"))
ALEMBIC_SCRIPTS = os.path.normpath(os.path.join(temp_root, "app", "alembic"))

# La base de données doit être dans le dossier PERMANENT (pour ne pas être effacée)
# DATABASE_PATH = os.path.join(permanent_root, "ecole.db")

import traceback
import sys

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    print("=== UNHANDLED EXCEPTION ===")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    print("===========================")

sys.excepthook = handle_exception
# print("VERSION JINJA :", jinja2.__version__) 
# GRANT CREATE, INSERT, UPDATE ON `lemignon`.`client_infos` TO 'ssl_reader'@'%';
# FLUSH PRIVILEGES;


# print("=== Démarrage de l'application ===")

server = None
window = None  # Pour qu’on puisse y accéder globalement

def handle_new_connection():
    global server, window
    socket = server.nextPendingConnection()
    if socket and window:
        window.activate_window()
    socket.disconnectFromServer()


def is_another_instance_running():
    socket= QLocalSocket()
    socket.connectToServer(UNIQUE_KEY)
    if socket.waitForConnected(100):
        return True
    return False
def create_local_server():
    server = QLocalServer()
    try:
        server.removeServer(UNIQUE_KEY)
    except:
        pass
    server.listen(UNIQUE_KEY)
    return server

def get_path(relative_path):
    """ Récupère le chemin des fichiers inclus avec PyInstaller """
    if getattr(sys, 'frozen', False):  # Si l'application est packagée
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))  # Mode développement

    return os.path.join(base_path, relative_path)

def open_app(): 
    try:
        global window
        window = Main()
        window.show()
        sys.exit(app.exec())  
    except Exception as e:
        import traceback
        traceback.print_exc()
        input("Erreur détectée, appuyez sur Entrée pour quitter...")
    

if __name__ == "__main__":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try: 
        os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        if is_another_instance_running():
            # Envoie une requête pour activer la fenêtre existante
            socket = QLocalSocket()
            socket.connectToServer(UNIQUE_KEY)
            if socket.waitForConnected(100):
                socket.write(b"ACTIVATE")
                socket.flush()
                socket.waitForBytesWritten(100)
            sys.exit(0)
        else:
            server = create_local_server()
            server.newConnection.connect(handle_new_connection)
            open_app() 
    except Exception as e:
        print(f"Erreur lors de l'ajout du chemin : {e}")
        import traceback
        traceback.print_exc()
        input("Erreur détectée, appuyez sur Entrée pour quitter...")


# UPDATE paiements
# SET paiement_details = REGEXP_REPLACE(
#         paiement_details,
#         'Versement_([0-9]+)_None',
#         CONCAT('Versement_\\1_', '8ef65c55-8166-4557-bc2f-5482d605cd76')
#     ),
#     mois = REGEXP_REPLACE(
#         mois,
#         'Versement_([0-9]+)_None',
#         CONCAT('Versement_\\1_', '8ef65c55-8166-4557-bc2f-5482d605cd76')
#     )
# WHERE paiement_details REGEXP 'Versement_[0-9]+_None';


# $this->removeVersement("075ad46c-ab5c-42e9-b562-5dffe086686c", 8000);

# public function removeVersement($paiementId, $montant = 8000)
# {
#     $p = Paiement::findOrFail($paiementId);

#     $data = json_decode($p->paiement_details, true);
#     $mois = json_decode($p->mois, true);

#     // 1) SUPPRESSION DANS info_paiement
#     foreach ($data['paiement_details']['info_paiement'] as $date => $details) {

#         if (isset($details['depot']) && intval($details['depot']) == $montant) {
#             unset($data['paiement_details']['info_paiement'][$date]);
#         }
#     }

#     // 2) SUPPRESSION DANS mois
#     foreach ($data['paiement_details']['mois'] as $key => $value) {
#         if (intval($value) == $montant) {
#             unset($data['paiement_details']['mois'][$key]);
#         }
#     }

#     // 3) SUPPRESSION DANS mois (colonne séparée)
#     foreach ($mois['mois'] as $key => $value) {
#         if (intval($value) == $montant) {
#             unset($mois['mois'][$key]);
#         }
#     }

#     // 4) SUPPRESSION dans check_echeance si nécessaire
#     # foreach ($data['paiement_details']['check_echeance'] as $key => $value) {
#     #     if (intval($value) == $montant) {
#     #         unset($data['paiement_details']['check_echeance'][$key]);
#     #     }
#     # }

#     // Mise à jour
#     $p->paiement_details = json_encode($data, JSON_UNESCAPED_UNICODE);
#     $p->mois = json_encode($mois, JSON_UNESCAPED_UNICODE);
#     $p->save();

#     return "Versement supprimé avec succès.";
# }



   