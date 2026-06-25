from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool
from PySide6.QtWidgets import QApplication, QMainWindow, QFrame,QSystemTrayIcon
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt 
import platform
import os
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import Qt
import signal
from shiboken6 import isValid
from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsOpacityEffect 
# from win10toast import ToastNotifier
from notifypy import Notify
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

# class BadgeEditorDialog(QDialog):
#     from Helper.Badge.Badge import BadgeEditorWidget
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Éditeur de Badge")
#         self.resize(950, 650)

#         # ton widget existant
#         self.editor = BadgeEditorWidget()

#         # boutons OK / Annuler
#         self.buttons = QDialogButtonBox(
#             QDialogButtonBox.Ok | QDialogButtonBox.Cancel
#         )
#         self.buttons.accepted.connect(self.accept)
#         self.buttons.rejected.connect(self.reject)

#         # Layout
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.editor)
#         layout.addWidget(self.buttons)

    # def get_result(self):
    #     """
    #     Retourne une image PNG des deux faces quand l’utilisateur clique OK.
    #     Tu peux personnaliser cette partie selon ton besoin.
    #     """

    #     recto_img = self.editor.export_png_return(is_recto=True)
    #     verso_img = self.editor.export_png_return(is_recto=False)
    #     return recto_img, verso_img


# QObject pour émettre les signaux
class ConfigSignals(QObject):
    finished = Signal(dict)

# QRunnable pour faire le travail en arrière-plan
# class ConfigWorker(QRunnable):
#     def __init__(self):
#         super().__init__()
#         self.signals = ConfigSignals()  # <- utiliser QObject pour les signaux

#     def run(self):
#         try:
#             from .DashboardController import get_config
#             result = get_config()
#             self.signals.finished.emit(result)  # <- émettre le signal
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             self.signals.finished.emit({})  # renvoyer dict vide en erreur



from utils.imports import *
import pdfkit
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from PySide6.QtWidgets import QProgressDialog 

import logging
from .Camera.CameraWorker import CameraWorker
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
import cv2
# from jinja2 import Template,Environment, FileSystemLoader
import time
import ctypes
# from pyzbar.pyzbar import decode
import qrcode
# from PySide6.QtMultimedia import QCameraInfo
from PySide6.QtMultimedia import QMediaDevices, QMediaPlayer

from Helper.Components.annee_academique import Annee_Academique # ajouter_annee_academique
from Helper.Components.Exam_params import Param_Exam #enregistrer_parametres_examen
from Helper.Components.Add_classes import Add_classe_Dialog #enregistrer_classe 
from Helper.Components.Frais_dinscription import Frais_dinscritipn 
from Helper.Components.Frais_divers import Frais_divers
from Helper.Components.Faculte import Faculte
from Helper.Components.Payment_params import Main_payment 
from Helper.Components.ImageLoaderThread import ImageLoaderThread
from Helper.LoadingOverlay import LoadingOverlay 

# from Helper.Check import check_internet
from Helper.Check_data import Check_data  


from Models.enregistrement import Save_data 

from Models.fetch_data import Fech_data  

from Views.main_view import Ui_MainWindow

documentTypes = [
    'Attestation', 'Certificat', 'Certificat de naissance',
    'Carte d\'identité',
    'Diplôme',
    'Relevé de notes',
    'Photo d\'identité', 'Autre',
]

sexe = {"M", "F"}


logger = logging.getLogger()
logger.setLevel(logging.DEBUG) 

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)

import sys
import traceback

def excepthook(exc_type, exc_value, exc_tb):
    print("❌ Exception non gérée :", exc_value)
    traceback.print_exception(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

import faulthandler
faulthandler.enable()
logger.addHandler(console_handler)
from Models.ApiHandler import ApiHandler 
from Models.AsyncDataHandler import AsyncDataHandler
from Models.DB.async_db_manager import AsyncDBManager
import requests
import json

# Domaine de production d'infini-software (voir docs/infini-software.md).
INFINI_API_BASE_URL = "https://infini-software.cloud"


class LicenceSyncWorker(QObject):
    """Vérifie auprès d'infini-software si une clé plus récente que celle
    actuellement connue existe pour ce mac (modèle "pull" : infini-software
    ne peut pas appeler directement ce serveur, voir
    docs/infini-software-PRD.md). Tourne hors du thread principal (réseau
    externe) ; n'écrit rien localement elle-même — émet juste le résultat,
    l'appel à /api/v1/licence/appliquer se fait ensuite sur le thread
    principal via l'ApiHandler existant (qui gère déjà le token)."""
    # (new_key, expiration_date, days_valid) — days_valid (object, pas int :
    # peut être None pour une clé émise avant l'ajout de ce champ côté
    # infini-software) est la valeur réellement utilisée dans le HMAC de la
    # clé, nécessaire à ecole_nginx pour revérifier son authenticité
    # localement (voir app.Helper.license_check.is_license_valid()).
    nouvelle_cle_disponible = Signal(str, str, object)

    def __init__(self, mac, cle_actuelle):
        super().__init__()
        self.mac = mac
        self.cle_actuelle = cle_actuelle

    def run(self):
        try:
            r = requests.get(
                f"{INFINI_API_BASE_URL}/api/licence/derniere-cle",
                params={"mac": self.mac}, timeout=5,
            )
            if r.status_code == 200:
                data = r.json()
                new_key = data.get("key")
                expiration_date = data.get("expiration_date")
                days_valid = data.get("days_valid")
                if new_key and expiration_date and new_key != self.cle_actuelle:
                    self.nouvelle_cle_disponible.emit(new_key, expiration_date, days_valid)
        except Exception:
            pass  # pas de connexion à infini-software : on reste sur l'état local, silencieusement
        finally:
            self.thread().quit()


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # self.overlay.start_loading("Lancement de l'application, Veuillez patienter svp...")

        # self.make_request()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.overlay = LoadingOverlay(self)
        # self.overlay = LoadingOverlay_(self)
        # self.load_data()
        # print(f" TokenManager().delete_token()     {TokenManager().get_token()}")
        TokenManager().delete_token()
        # if not TokenManager().get_certificat_signed():
        #     manager = CertificateManager()
        #     print("=== Vérification du certificat ===")
        #     if manager.certificat_existe():
        #         print("ℹ️  Certificat déjà présent, aucune action nécessaire.")
        #         # path_exe=r"C:\Program Files\gestion ecole\app.exe"
        #         # manager.signer_exe(path_exe)
        #     else:
        #         print("⚠️  Certificat absent → Génération et installation...")
        #         manager.generer_certificat()
        #         manager.installer_certificat()
        #         TokenManager().save_certificat_signed(True)
        
        self.ui.header_connexion.setHidden(True)
        self.ui.header_connexion_error.setHidden(True)
        # importlib.reload(Config)
        self.token_manager = TokenManager() 
        self.dialogs = None
        # self.token_manager.delete_token()
        self.center_on_screen()
        self.simulate_slow_dependency()

        self.api_handler = ApiHandler()

        self._setup_abonnement_page()

        self.api_handler_ = AsyncDataHandler()
        # self.api_handler_.vente_data_ready.connect(self.on_vente_data_received)
        # self.api_handler_.vente_data_ready.connect(self.on_vente_ready)
        
        # Connectez les signaux
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)

        self.api_handler_.request_binary_complete.connect(self.handle_pdf)
        self.api_handler_.admin_auth_required.connect(self.required_admin)
        # try:
        #     self.server_checking()
        # except Exception as e:
        #     print(e)
                # Retirer les bordures
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(750, 500)
        self.loaders = {}
        self.must_refresh_paiement=False
 
        # self.db = AsyncDBManager(loader_widget=self.overlay)

        # Connexions globales   

                    # Données exemple
        self.mois__ = ["Jan", "Fév", "Mar", "Avr"]
        self.paiements = [1200, 1500, 1000, 1800]
        self.inscriptions = [30, 45, 25, 60]
        self.reussite = [80, 85, 70, 90]
        self.rendement = [75, 80, 65, 88]
  

        self.ip_manager = Ip_manager()

        # self.check_data = Check_data()
        # self.fetch_data_ = Fech_data()
        # self.save_data = Save_data()

        self.row = None
        

        self.cap = None
        self.access_key = 0
        self.access_key_info = 0 
 

        def apply_shadow(widget, blur=20, color=QColor(190, 190, 190,150), offset_x=0, offset_y=0):
            shadow = QGraphicsDropShadowEffect(widget)
            shadow.setBlurRadius(blur)
            shadow.setColor(color)
            shadow.setOffset(offset_x, offset_y)
            
            widget.setGraphicsEffect(shadow)

            # widget.setStyleSheet("background-color: white;")

        

        apply_shadow(self.ui.etudiant_dash)
        apply_shadow(self.ui.professeur_dash)
        apply_shadow(self.ui.personnel_dash)
        apply_shadow(self.ui.classe_dash)

        apply_shadow(widget=self.ui.widget_administratif)
        apply_shadow(widget=self.ui.widget_financier)
        apply_shadow(widget=self.ui.widget_global) 
        apply_shadow(widget=self.ui.widget_11) 

        apply_shadow(widget=self.ui.cours_dash)
        apply_shadow(widget=self.ui.notes_dash)
        apply_shadow(widget=self.ui.paiement_dash) 


        apply_shadow(widget=self.ui.widget_20) 
        apply_shadow(widget=self.ui.tab_loans_form)

        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        server_path = os.path.join(get_local_data_dir(), ".ecole_360", ".certs")

     
        if not os.path.exists(server_path) or not TokenManager().get_token():
            self.fancy_modal_show(self.ui.connexion_page)       
            self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
            # self.fade_in_page(self.ui.connexion_page)   
            self.overlay.finish_loading()

        try:
            self.request_certificate_ss()
        except Exception as e:
            print(e) 


                # print(self.load_data())
        # try:
        #     # if os.path.exists(server_path):
        #         # from .EssantielController import load_data,load_profile_config
        #         # self.db.run(load_data)
        #         # data = load_data() 
        #         # self.direct_request =bool(data.get('value',0)) if data else None
        #         # self.token_manager.save_direct_request(bool(self.direct_request))
 
        #     pass
        #         # if self.token_manager.get_direct_request():
        #         #     self.db.run(load_profile_config)
        #         # else: 
        #         #     self.api_handler_.config_donnees() 
        #         # else:
        #         #     self.api_handler_.config_donnees()
        # except Exception as e:
        #     print(f'e        bfnfgff         {e}')
        #     self.token_manager.save_direct_request(False)
        #     self.api_handler_.config_donnees()

  # ==========================DONNEE DEPUIS L'API==================================================
        # self.niveau_selected = '' 
        self.main_layout = QVBoxLayout() 
        self.documents=[]
        self.cours_dictionary = []
        self.info_user_response_data = []
        self.programme_dictionary = []
        self.student_live_search_table =QTableWidget()
        self.student_live_seach_input=''

        current_dir = os.path.dirname(__file__)
        self.project_dir = os.path.dirname(current_dir) 
        # self.setStyleSheet(""" 
        #     QScrollArea {
        #         border: 1px solid #777779;
        #     }
        #     QLabel, QLineEdit { font-size: 13pt; } 

        #     QScrollBar:vertical {
        #         border: none;
        #         background: transparent;
        #         width: 10px;  
        #         margin: 4px 0 5px 0;
        #     }

        #     QScrollBar::handle:vertical {
        #         background: #777779;  
        #         border-radius: 2px;
        #         min-height: 50px;
        #     }

        #     QScrollBar::handle:vertical:hover {
        #         background: #37475b;
        #     }

        #     QScrollBar::handle:vertical:pressed {
        #         background: #122a55;
        #     }

        #     QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
        #         border: 1px solid #37475b;
        #         height: 0px;  
        #     }

        #     QRadioButton {
        #         spacing: 5px;
        #     }

        #     QRadioButton::indicator {
        #         width: 13px;
        #         height: 13px;
        #         border: 1px solid #666666;
        #         border-radius: 6px;  
        #     }

        #     QRadioButton::indicator:unchecked {
        #         background-color: #666;
        #     }

        #     QRadioButton::indicator:checked {
        #         border: 1px solid #40C057;
        #         background-color: #40C057;
        #     }
        # """)
        
        self.setStyleSheet(""" 
            QScrollArea {
                border: 1px solid #777779;
                background-color: transparent;
            }
            
            QLabel, QLineEdit { font-size: 13pt; } 

            /* --- BARRE VERTICALE --- */
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 10px;  
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #777779;  
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #37475b; }

            /* --- BARRE HORIZONTALE (L'oubliée) --- */
            QScrollBar:horizontal {
                border: none;
                background: transparent;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #777779;
                border-radius: 5px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover { background: #37475b; }

            /* --- NETTOYAGE DES BOUTONS ET ARRIÈRE-PLAN --- */
            QScrollBar::add-line, QScrollBar::sub-line {
                border: none;
                background: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }

            /* --- RADIO BUTTONS --- */
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #666666;
                border-radius: 7px;
            }
            QRadioButton::indicator:unchecked { background-color: #333; }
            QRadioButton::indicator:checked {
                border: 1px solid #40C057;
                background-color: #40C057;
            }
        """)


        self.ui.widget_piece_inner.setLayout(self.main_layout) 
        self.ui.tabWidget.tabBar().setVisible(False)
        self.ui.tabWidget_2.tabBar().setVisible(False)
        self.ui.tabWidget_3.tabBar().setVisible(False)
        self.ui.tabWidget_4.tabBar().setVisible(False)

# =======================================RECHERCHER=================================================
        self.disconnect_timer = QTimer(self)
        self.disconnect_timer.timeout.connect(lambda: self.deconnexion())

        # self.ui.sesrch_student.textChanged.connect(lambda: all_student(self.ui.sesrch_student.text()))
        self.search_timer_student = QTimer(self)
        self.search_timer_student.setSingleShot(True)
        self.search_timer_student.timeout.connect(lambda: self.go_to_student_page(self.current_page_student))
        self.ui.sesrch_student.textChanged.connect(self.restart_timer)

        
        self.search_timer_sell = QTimer()
        self.search_timer_sell.setSingleShot(True) 
        self.search_timer_sell.timeout.connect(lambda: self.go_to_vente_page(self.current_page_vente))
        self.ui.search_vente.textChanged.connect(self.restart_timer_vente)


        self.search_timer_depense = QTimer()
        self.search_timer_depense.setSingleShot(True) 
        self.search_timer_depense.timeout.connect(lambda: self.go_to_depense_page(self.current_page_depense))
        self.ui.search_depense.textChanged.connect(self.restart_timer_depense)


        self.search_timer_admin = QTimer(self)
        self.search_timer_admin.setSingleShot(True)
        self.search_timer_admin.timeout.connect(lambda: self.go_to_page_admin(self.current_page_admin))
        self.ui.search_admin.textChanged.connect(self.restart_timer_admin)
        

        self.search_timer_prof = QTimer(self)
        self.search_timer_prof.setSingleShot(True)
        self.search_timer_prof.timeout.connect(lambda: self.go_to_page_teacher(self.current_page_prof))
        self.ui.search_prof.textChanged.connect(self.restart_timer_prof)

        self.search_timer_paiement = QTimer(self)
        self.search_timer_paiement.setSingleShot(True)
        self.search_timer_paiement.timeout.connect(lambda: self.go_to_paiement_page(self.current_page_paiement))

        self.ui.search_paiement.textChanged.connect(self.restart_timer_paiement)


        self.search_timer_note = QTimer(self)
        self.search_timer_note.setSingleShot(True)
        self.search_timer_note.timeout.connect(lambda: self.go_to_note_page(self.current_page_student))
        self.ui.search_notes.textChanged.connect(self.restart_timer_note)

        self.search_timer_programme = QTimer(self)
        self.search_timer_programme.setSingleShot(True)
        self.search_timer_programme.timeout.connect(lambda:self.go_to_programme_page(self.current_page_programme))
        self.ui.search_programme.textChanged.connect(self.restart_timer_programme)
        


        self.ui.search_student_for_sell.textChanged.connect(lambda: self.set_table_refresh_data_for_sell())
        self.ui.search_student_for_detail.textChanged.connect(lambda: self.set_table_refresh_data_for_live_search_student())
        self.ui.search_cours.textChanged.connect(lambda:self.go_to_cours_page(self.current_page_cours))
        
        self.ui.search_programme.textChanged.connect(lambda:self.set_table_refresh_data_programme())
        # self.ui.btn_plus_classe.toggled.connect(self.show_student_number_in_classes) 
        self.ui.btn_plus_classe.toggled.connect(self.toggle_show_students) 
        self.ui.camera_ip_2.toggled.connect(self.active_camera_ip) 
        self.ui.btn_plus_professeur.clicked.connect(self.show_teacher_and_other_action)

        self.ui.ajouter_vente.clicked.connect(self.add_commande)
        self.ui.passer_la_commande.clicked.connect(self.commander)
        self.ui.depense_btn.clicked.connect(self.depense_page)
        self.ui.enregistrer_depense.clicked.connect(self.enregistrer_depense)

        self.ui.loans.clicked.connect(self.tab_loans)
        self.ui.faire_un_remboursement3.clicked.connect(self.bact_to_loans)
        self.ui.faire_un_remboursement.clicked.connect(self.to_loans_repayments)
        self.ui.accorder_un_pret.clicked.connect(self.loans_form)

        
# =======================================RECHERCHER=================================================

# ====================================PAGINATION========================================================            
# 
# 
        self.student_id_for_payment_show=None
        self.commande = []
        self.get_facultes = []
        self.user_roles = []
        self.user_permissions = []
        self.data_and_payment_info =[]
        self.index_data_and_payment_info=None
        self.current_page_student = 1
        self.total_pages_student = 1

        self.current_page_prof = 1
        self.total_pages_prof = 1

        self.current_page_admin = 1
        self.total_pages_admin = 1

        self.current_page_vente = 1
        self.total_pages_vente = 1 

        self.current_page_log = 1
        self.total_pages_log = 1 

        self.current_page_depense = 1
        self.total_pages_depense = 1
        
        self.current_page_loans = 1
        self.total_pages_loans = 1 

        self.current_page_cours = 1
        self.total_pages_cours = 1

        self.current_page_programme = 1
        self.total_pages_programme = 1

        self.current_page_paiement = 1
        self.total_pages_paiement = 1

        self.current_page_notes = 1
        self.total_pages_notes = 1

        self.current_page_annee = 1
        self.total_pages_annee = 1

        self.current_page_class = 1
        self.total_pages_class = 1

        self.current_page_frais = 1
        self.total_pages_frais = 1

        self.current_page_faculte=1
        self.total_pages_faculte=1

        self.current_page_frais_divers=1
        self.total_pages_frais_divers=1

        self.current_page_paiement_params = 1
        self.total_pages_paiement_params = 1

        self.current_page_param_exam = 1
        self.total_pages_param_exam = 1
        self.data_admin_for_authorization=None

        self.all_other_transac_data ={}
        self.current_page_transac = 1
        self.total_pages_transac=1

        self.user_identity_show=''
        self.mois_ =["Septembre", "Octobre", "Novembre", "Décembre", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août"]
# ====================================PAGINATION========================================================
        self.actions = {
            "create": "Créer",
            "update": "Mise à jour",
            "delete": "Supprimer"
        } 

        self.template = {
            "template_badge_1": "Template 1",
            "template_badge_2": "Template 2",
                }

        self.salle = {
            "A": "Salle A",
            "B": "Salle B",
            "C": "Salle C",
            "D": "Salle D",
                }

        self.models = {
            "Année académique": "App\\Models\\AnneeAcademique",
            # "annees": "App\\Models\\Annee",
            # "classe_facultes": "App\\Models\\ClasseFaculte",
            "Classe": "App\\Models\\Classe",
            "Etudiants classe": "App\\Models\\ClassesEtudiant",
            # "client_infos": "App\\Models\\ClientInfo",
            "Cours": "App\\Models\\Cours",
            "Note": "App\\Models\\CoursEtudiant",
            "Dépenses": "App\\Models\\Depense",
            "Etudiant faculté ": "App\\Models\\EtudiantFaculte",
            "Etudiants": "App\\Models\\Etudiant",
            "faculté": "App\\Models\\Faculte",
            # "failed_jobs": "App\\Models\\FailedJob",
            "Frais d'inscription": "App\\Models\\FraisDInscription",
            "Frais divers": "App\\Models\\FraisDivers",
            # "heart_autos": "App\\Models\\HeartAuto",
            # "job_batches": "App\\Models\\JobBatch",
            # "jobs": "App\\Models\\Job",
            # "log_actives": "App\\Models\\LogActive",
            # "logs": "App\\Models\\Log",
            # "migrations": "App\\Models\\Migration",
            # "model_has_permissions": "App\\Models\\ModelHasPermission",
            # "model_has_roles": "App\\Models\\ModelHasRole",
            # "niveau_detudes": "App\\Models\\NiveauDetude",
            "niveaux": "App\\Models\\Niveau",
            # "notes": "App\\Models\\Note",
            "order_items": "App\\Models\\OrderItem",
            "Paiements": "App\\Models\\Paiement",
            "Paramètre de paiement": "App\\Models\\ParametrePaiement",
            "Paramètre des examens": "App\\Models\\ParamExam",
            # "password_reset_tokens": "App\\Models\\PasswordResetToken",
            "Permissions": "App\\Models\\Permission",
            "Personnels": "App\\Models\\Personnel",
            "Professeurs": "App\\Models\\Professeur",
            "Profiles": "App\\Models\\Profile",
            "Programmes": "App\\Models\\Programme",
            "Utilisateur": "App\\Models\\User",
            "Ventes": "App\\Models\\Vente",
        }
        # Charger le GIF animé
        # gif_path = os.path.join(self.project_dir, 'assets', 'icons', 'reseau.gif')  
        # self.movie = QMovie(gif_path)

        # Associer le GIF au QLabel et démarrer l'animation
        # self.ui.gif_animate.setMovie(self.movie)
        # self.ui.gif_animate.size()
        # self.movie.start()

        self.ui.close_error.clicked.connect(lambda: self.close())
        self.ui.close_4.clicked.connect(lambda: self.close())
        
        self.ui.valider_id_server.clicked.connect(self.verify_and_save_server_ip)
        
        self.SERVER_IP = self.ip_manager.get_server_ip()
        self.ui.min_error.clicked.connect(self.showMinimized)
        
        # self.server_checker = ServerChecker()
        
        # self.server_checker.server_connected.connect(lambda: self.ui.main_with_shadow.setCurrentIndex(2))
        # self.server_checker.start()

        self.ui.show_frame_ip.clicked.connect(self.show_modif_ip)
        # self.ui.bulletin_dialog.toggled.connect(self.show_frame_print_bulletin)
        self.ui.bulletin_dialog.setCheckable(True) 
        self.ui.desicion_finale.clicked.connect(self.print_desicion_de_fin_dannee)
        self.ui.desicion_finale_exel.clicked.connect(self.print_desicion_de_fin_dannee_excel)

        self.ui.bulletin_dialog.toggled.connect(self.show_frame_print_bulletin)
        self.ui.global_rapport_imprimer.clicked.connect(self.print_global_report)
        self.ui.administratif_imprimer.clicked.connect(self.administratif_imprimer)
        self.ui.pedagogique_imprimer.clicked.connect(self.pedagogique_imprimer)
        self.ui.format_excel_pedagogique.clicked.connect(self.pedagogique_imprimer_exel)
        self.ui.financier_imprimer.clicked.connect(self.financier_imprimer)
        self.ui.recu_inscrit.clicked.connect(self.imprimer_fiche_inscription)
        self.ui.supprimer_etudiant.clicked.connect(self.delete_student)

        self.ui.change_ip.clicked.connect(self.verify_and_save_server_ip_in_connect)
        self.ui.frame_240.setHidden(True)   
        self.ui.input_change_ip.setText(str(self.ip_manager.get_server_ip()))  

        self.ui.delete_admin.clicked.connect(self.delete_personnel)       
        self.ui.delete_prof.clicked.connect(self.delete_professeur) 

        self.ui.intra_button.toggled.connect(self.on_radio_controle_university_changed)
        self.ui.finale_button.toggled.connect(self.on_radio_controle_university_changed)

        self.ui.direct_request.toggled.connect(self.on_radio_direct_request_changed)  
        self.ui.domain_or_ip.toggled.connect(self.on_radio_domain_or_ip_changed)  
        self.control_university   = '' 

        self.ui.live_log.clicked.connect(self.logs_console)
        self.ui.log_grafic.clicked.connect(self.log_grafic)


        self.ui.sexe.addItems(sexe)
        self.ui.sexe.setCurrentIndex(0)

 
        # Afficher l'ID sélectionné lors d'un changement
        self.ui.niveau_id.currentIndexChanged.connect(self.selection_changed_niveau)

        self.ui.combo_administratif_niveau.currentIndexChanged.connect(self.selection_changed_niveau)
        self.ui.combo_pedagogique_niveau.currentIndexChanged.connect(self.selection_changed_niveau)

        # self.ui.annee_academique_id.currentIndexChanged.connect(self.selection_changed_annee_academique)
        self.ui.classe_actuelle_id.currentIndexChanged.connect(self.selection_changed_classe)

        self.ui.action_log.currentIndexChanged.connect(self.call_action_log)
        self.ui.model_log.currentIndexChanged.connect(self.call_model_log)

        self.ui.admin_role.currentIndexChanged.connect(self.selection_changed_role)
        self.ui.combo_anne_for_dash.activated.connect(self.get_dash_data_by_date)

        # self.ui.combo.currentIndexChanged.disconnect()
        # self.ui.combo.currentIndexChanged.connect(self.load_dashboard)
        # OU utiliser :

        # self.ui.combo.activated.connect(self.load_dashboard)

        self.ui.next_page_student.clicked.connect(self.next_page_student)
        self.ui.prev_page_student.clicked.connect(self.prev_page_student)

        self.ui.next_paiement.clicked.connect(self.next_paiement)
        self.ui.prev_paiement.clicked.connect(self.prev_paiement)

        self.ui.next_notes.clicked.connect(self.next_notes)
        self.ui.prev_notes.clicked.connect(self.prev_notes)

        self.ui.next_cours.clicked.connect(self.next_cours)
        self.ui.prev_cours.clicked.connect(self.prev_cours)

        self.ui.prof_prev.clicked.connect(self.prof_prev)
        self.ui.prof_next.clicked.connect(self.prof_next)

        self.ui.admin_prev.clicked.connect(self.admin_prev)
        self.ui.admin_next.clicked.connect(self.admin_next)

        self.ui.next_programme.clicked.connect(self.next_programme)
        self.ui.prev_programme.clicked.connect(self.prev_programme)

        self.ui.next_annee.clicked.connect(self.next_annee)
        self.ui.prev_annee.clicked.connect(self.prev_annee)

        self.ui.next_class.clicked.connect(self.next_class)
        self.ui.prev_class.clicked.connect(self.prev_class)

        self.ui.next_frais.clicked.connect(self.next_frais)
        self.ui.prev_frais.clicked.connect(self.prev_frais)

        self.ui.next_paiement_params.clicked.connect(self.next_paiement_params)
        self.ui.prev_paiement_params.clicked.connect(self.prev_paiement_params)

        self.ui.next_param_exam.clicked.connect(self.next_param_exam)
        self.ui.prev_param_exam.clicked.connect(self.prev_param_exam)

        self.ui.next_depense.clicked.connect(self.next_depense)
        self.ui.prev_depense.clicked.connect(self.prev_depense)

        self.ui.next_vente.clicked.connect(self.next_vente)
        self.ui.prev_vente.clicked.connect(self.prev_vente)

        # self.ui.btn_close.clicked.connect(lambda: self.close())
        # self.ui.btn_min.clicked.connect(self.toggle_maximize)
        # self.ui.minimize.clicked.connect(self.showMinimized)

        self.ui.choise_profile_image.clicked.connect(self.choisir_image_profile)

        self.ui.template_badge_1.clicked.connect(self.template_badge_1)
        self.ui.template_badge_2.clicked.connect(self.template_badge_2)
        self.ui.template_badge_2.clicked.connect(self.template_badge_2)

        self.ui.btn_importer_exel.clicked.connect(self.btn_importer_exel)

        self.ui.template_certificat.clicked.connect(self.template_certificat)
        self.ui.template_diplome.clicked.connect(self.template_diplome)

        

        self.ui.recherche_user_permission.clicked.connect(lambda: self.set_table_refresh_data_for_live_search_permission())
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)

        # self.ui.niveau_for_promus.currentIndexChanged.connect(self.change_class_for_promus)
        # self.ui.niveau_promus.currentIndexChanged.connect(self.change_class_promus)

        self.ui.btn_for_promus.clicked.connect(self.rechercher_for_promus)
        self.ui.btn_promus.clicked.connect(self.promus_to)
        self.ui.cancel_promus.clicked.connect(self.cancel_promus_to)

        self.ui.add_year.clicked.connect(self.add_year)
        self.ui.add_param_exam.clicked.connect(self.add_param_exam)
        self.ui.add_class.clicked.connect(self.add_classe)
        self.ui.add_frais.clicked.connect(self.add_frais)
        self.ui.add_frais_divers.clicked.connect(self.add_frais_divers)
        self.ui.add_faculte.clicked.connect(self.add_faculte)
        self.ui.add_paiement_params.clicked.connect(self.add_paiement_params)
        self.ui.imprimer_vente.clicked.connect(self.imprimer_vente)
        self.ui.notes_dialog.clicked.connect(self.show_dialog_for_notes)

        self.ui.add_personnel.clicked.connect(self.add_personnel)
        self.ui.enregistrer_admin.clicked.connect(self.sauvegarder_admin)

        self.ui.valider_loans.clicked.connect(self.sauvegarder_loans)

        self.ui.add_prof_button.clicked.connect(self.add_professeur)
        self.ui.enregistrer_prof.clicked.connect(self.sauvegarder_professeur)

        self.ui.cours_stack.clicked.connect(self.cours_page)
        self.ui.addCours.clicked.connect(self.add_cours_page)
        self.ui.add_course_line.clicked.connect(self.add_cours_line)
        self.ui.enregistrer_cours.clicked.connect(self.enregistrer_cours)
        self.ui.btn_left_profile.clicked.connect(self.profile)
        self.ui.paiement_dialog.clicked.connect(self.search_student)
        # self.ui.paiement_dialog.clicked.connect(self.search_student)
        self.ui.modal_identifiant.clicked.connect(self.search_student)
         

        self.ui.programme_stack.clicked.connect(self.programme_index)
        self.ui.addProgramme.clicked.connect(self.add_programme_page)
        self.ui.add_programme_line.clicked.connect(self.add_programme_line)
        self.ui.enregistrer_programme.clicked.connect(self.enregistrer_programme)

        self.ui.anneeId.currentIndexChanged.connect(self.get_programs_by_anneeId)
        self.ui.class_id.currentIndexChanged.connect(self.get_programs_by_class_id)
        self.ui.niveauId.currentIndexChanged.connect(self.get_programs_by_niveauId)
        
        
        self.ui.autre_transaction.clicked.connect(self.autre_transaction) 
        self.ui.btn_vente_page.clicked.connect(self.add_vente)
        self.ui.btn_vente_back.clicked.connect(self.vente_page) 

        self.ui.save_transac.clicked.connect(self.sauvegarder_other_transaction)
        self.ui.edit_transact.clicked.connect(self.edit_other_transaction)
        
        

        self.ui.add_student.clicked.connect(self.add_student_page)
        self.ui.btn_diplome.clicked.connect(self.diplome_page)
        self.ui.btn_certificat.clicked.connect(self.certificat_page)

        self.ui.modifier_etudiant.clicked.connect(self.modifier_etudiant_page)
        self.ui.suivant_1.clicked.connect(self.responsable_info)
        self.ui.suivant_2.clicked.connect(self.pieces_soumise)

        self.ui.back_1.clicked.connect(self.back_to_personnal_info)
        self.ui.back_2.clicked.connect(self.back_to_responsable)

        self.ui.ajouter_document.clicked.connect(self.ajouter_document)
        self.ui.enregistre.clicked.connect(self.sauvegarde_etudiant)
        self.ui.back_to_details.clicked.connect(self.back_to_details)
        # self.ui.search_student_for_detail.textChanged.connect(lambda: self.set_table_refresh_data_for_live_search_student())
        
        self.ui.imprimer_etudiant.clicked.connect(self.print_student_details)
        self.ui.recherche_user_role.clicked.connect(lambda: self.set_table_refresh_data_for_live_search_role())

        self.ui.btn_param_paiement.clicked.connect(self.paiement_params_page)
        self.ui.btn_param_exam.clicked.connect(self.exam_params_page)
        self.ui.btn_frais.clicked.connect(self.frais_params_page)
        self.ui.btn_frais_divers.clicked.connect(self.frais_divers_params_page)
        self.ui.btn_param_faculte.clicked.connect(self.faculte_params_page)
        self.ui.btn_annee.clicked.connect(self.annee_params_page)
        self.ui.btn_classe.clicked.connect(self.class_params_page)
        

        self.ui.valider_profile.clicked.connect(self.save_profile)

        self.ui.btn_permission_page.clicked.connect(self.permission_page)
        self.ui.btn_role_page.clicked.connect(self.role_page)

        self.search_camera_timer = QTimer()
        # self.search_camera_timer.setSingleShot(True) 
        self.search_camera_timer.timeout.connect(lambda: self.populate_camera_selector()) 
        self.ui.stop_search_cam.clicked.connect(self.stop_populate_camera)

        self.ui.btn_badge.clicked.connect(self.make_an_identity_card)
        self.ui.camera_selector.currentIndexChanged.connect(self.on_camera_changed)

        self.auto_save_image=False
        self.ui.generate_btn.clicked.connect(self.generate_badge)
        self.ui.save_badge.clicked.connect(self.generate_badge_and_save)

        self.ui.capture_btn.clicked.connect(self.toggle_camera)
        self.ui.load_btn.clicked.connect(self.load_photo)
        self.ui.camera_selector.currentIndexChanged.connect(self.change_camera)

        self.ui.search_for_card.textChanged.connect(lambda: self.set_table_refresh_search_for_card())
        self.ui.search_for_deplome.textChanged.connect(lambda: self.set_table_refresh_search_for_deplome_())
        self.ui.search_for_certificat.textChanged.connect(lambda: self.set_table_refresh_search_for_certificat_())
        self.ui.combo_template.currentIndexChanged.connect(lambda: self.set_replace_template())

        # current_dir = os.path.dirname(__file__)
        # self.project_dir = os.path.dirname(current_dir)

        # Construct the full path to the icon
        self.icon_path_logo = self.get_path(os.path.join('assets', 'icons', 'logo.png'))
        self.icon_path_logo_lock = self.get_path(os.path.join('assets', 'icons', 'lock.png'))
        # self.background_image = self.get_path(os.path.join('assets', 'icons', 'template_bage_1.jpg'))
        appdata = os.path.join(get_user_data_dir(), "gestion_ecole", "assets", "icons")
        self.background_image = self.get_path(os.path.join(appdata, 'template_badge_1.jpg'))
        # icon_path_reduire = os.path.join(self.project_dir, 'assets', 'icons', 'reduire.png')
        # minimize = os.path.join(self.project_dir, 'assets', 'icons', 'hide.png')

        if os.path.exists(self.icon_path_logo):
            self.setWindowIcon(QIcon(self.icon_path_logo))

        if os.path.exists(self.icon_path_logo):
            self.setWindowIcon(QIcon(self.icon_path_logo))
            self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo)
        else:
            self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo_lock)
   
        # self.ui.stop_search_cam.clicked.connect(self.stop_populate_camera)
        # self.ui.btn_close.setIcon(QIcon(icon_path_close))
        # self.ui.label_logo.setIcon(QIcon(self.icon_path_logo))
        # self.ui.btn_min.setIcon(QIcon(icon_path_reduire))
        # self.ui.minimize.setIcon(QIcon(minimize))

        self.setWindowTitle("Lekol360 Watch")
          
        self.data_combo_cours = []
        self.camera_active = False
        self.niveaux = []
        self.annee_acades = []
        self.teacherList = {}
        self.fetch_data_roles = []
        self.fetch_data_permissions = []
        self.classes_combo = []
        self.all_students_data = []
        self.data_for_other_transac=False

        self.all_personnels_data = []
        self.all_notes_data = []
        self.all_paiement_data = []


        self.all_ventes_data = None
        self.all_loans_data =[]
        
        self.all_logs_data ={}
        self.get_data_user_for_loans={}
        
        self.all_depense_data = []
        self.all_cours_data = []
        self.all_teacher_data = []
        self.all_personnel_data = []
        self.all_programme_data = []
        self.all_etudiant_data = []
        self.all_notes_data = []
        self.all_paiement_data = []
        self.all_dash_data = []

        self.all_classes_paginate = []
        self.all_fee_paginate = []
        self.all_params_exam = []
        self.all_frais_divers = []
        self.all_faculte = []
        self.all_paiement_params = []
        self.all_anneeAcademique =[]
        self.live_search_student =[]
        self.save_data_and_exit = False

        
        self.permissions_delete = []



        self.user_connect = QLineEdit()
        self.niveaux = {}

        self.data_combo_cours = {}

        self.annee_acades = {}

        self.teacherList = {}

        self.classes_combo = {}

        self.fetch_data_roles = {}

        self.fetch_data_permissions = {}
        self.show_student_for_payment = []
        self.user_info = []
        self.is_data_updating = False
        self.config_data = []
        self.get_list_cours =[]
        self.verifier_donnees = False

        if "--as-admin" in sys.argv: 
            try: 
                self.add_or_update_host(ip=self.ip_manager.get_server_ip())
                # server_path = r"C:\Program Files\gestion ecole\crt\server.crt"
                # subprocess.run([
                #     'certutil', '-addstore', '-f', 'Root', server_path
                # ], check=True)
                mac, username = self.get_mac_address()

                request = {
                'client_mac':mac,
                'client_name':username,
                }
                response = self.api_handler_.authorization_connect(mac=mac,username=username)
            except Exception as e:
                print(f"owioeriheori    {e}")
        
 

        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.setInterval(20000)  # 30 secondes
        self.auto_refresh_timer.timeout.connect(lambda: self.api_handler_.all_logs(page=self.current_page_log))

 
        self.ui.imprimer_bulletin.clicked.connect(self.action_print_bulletin)

        self.ui.btn_connexion.clicked.connect(self.se_connecter)
        self.ui.password_2.returnPressed.connect(self.ui.btn_connexion.click)
        self.ui.email_2.returnPressed.connect(lambda: self.ui.password_2.setFocus())

        self.ui.btn_reset_password.clicked.connect(self.reset_password)
        self.ui.reinitialiser_mot_de_passe.clicked.connect(self.reset_password_personnel)
        self.ui.btn_reset_password_prof.clicked.connect(self.reset_password_professeur)
        
        self.ui.status_prof_change.clicked.connect(self.active_teacher)
        self.ui.admin_change_status.clicked.connect(self.active_personnel) 
       
        
        self.ui.repport_type.clear()
        self.ui.repport_type.addItems(['Global','Livres', 'Tissus', 'Fournitures', 'Arriéré', 'Dépense'
        ]) 
        self.ui.repport_type.currentIndexChanged.connect(self.change_repport_type)
        
        
        self.ui.unit_prise.returnPressed.connect(self.ui.ajouter_vente.click)
        self.ui.total_prise.returnPressed.connect(self.ui.ajouter_vente.click)

        QShortcut(QKeySequence("Ctrl+p"), self, activated=self.commander)
        QShortcut(QKeySequence("Ctrl+m"), self, activated=lambda: self.ui.materiel_name.setFocus())
        # 
        # QShortcut(QKeySequence("Ctrl+d"), self, activated=self.commander)

        self.ui.prix_depense.returnPressed.connect(self.ui.enregistrer_depense.click)
        self.ui.description_depense.returnPressed.connect(lambda: self.ui.prix_depense.setFocus())

        # self.montant_verser = QLineEdit(self)
        # self.paiement_index = QLineEdit()
        # QShortcut(QKeySequence("Ctrl+t"), self, activated=lambda: self.montant_verser.setFocus())
        # self.id_professeur_for_update = QLineEdit()
        # self.id_admin_for_update = QLineEdit()

        domain = bool(self.token_manager.get_adress_type())
        
        if domain:
            self.ui.domain_or_ip.setChecked(True)

        request = self.token_manager.get_direct_request()
      
        if request:
            self.ui.direct_request.setChecked(True)

        # self.student_live_seach_input = QLineEdit()

        self.ui.loans_status.clear()
        self.ui.loans_status.addItems(['pending','approved','declined','disbursed','paid'])
    


    def close_splash1(slef):
        # On cherche le processus PowerShell qui fait tourner le splash
        # Note : Il est plus sûr de chercher par le titre de la fenêtre ou via un tag
        try:
            # Commande Windows pour fermer la fenêtre ayant le titre spécifique
            os.system('taskkill /FI "WINDOWTITLE eq Lekol360" /F')
        except Exception as e:
            print(f"Erreur lors de la fermeture du splash: {e}")

        # Appelle cette fonction juste après self.show()

    def close_splash(self):
        """Fermer le splash screen depuis l'application"""
        # Chemin du fichier signal (même dossier que l'app)
        signal_file = os.path.join(os.path.dirname(__file__), "splash_close.signal")
        
        try:
            with open(signal_file, 'w') as f:
                f.write('close')
            print("✅ Signal de fermeture envoyé au splash")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi du signal: {e}")

    def fade_in(self, widget, duration=500):
        """Anime l'opacité d'un widget de 0 à 1"""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # On garde une référence pour éviter que l'animation ne soit supprimée par le Garbage Collector
        widget._ani = animation 
        animation.start()


    def fade_in_page(self, widget, duration=500): 
        # 1. On s'assure que le widget est visible
        widget.show()
        
        # 2. Création de l'effet
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        # 3. Configuration de l'animation
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.InOutQuad) # Plus fluide
        
        # 4. LE NETTOYAGE : On retire l'effet quand l'animation est finie
        # C'est ce qui règle les erreurs QPainter
        anim.finished.connect(lambda: widget.setGraphicsEffect(None))
        
        # 5. Gestion de la mémoire (référence temporaire)
        if not hasattr(self, '_anims'): self._anims = {}
        self._anims[widget] = anim # On indexe par widget pour éviter les doublons
        
        anim.start()

    def fancy_modal_show11(self, widget):
        # Opacité
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
        
        # Animation Opacité
        anim_op = QPropertyAnimation(eff, b"opacity")
        anim_op.setDuration(500)
        anim_op.setStartValue(0)
        anim_op.setEndValue(1)
        
        # Animation Position (Slide up)
        anim_pos = QPropertyAnimation(widget, b"pos")
        anim_pos.setDuration(500)
        start_pos = widget.pos()
        anim_pos.setStartValue(start_pos + QPoint(0, 20)) # Commence 20px plus bas
        anim_pos.setEndValue(start_pos)
        anim_pos.setEasingCurve(QEasingCurve.OutCubic)

        # Lancer les deux
        anim_op.start()
        anim_pos.start()
        
        # Nettoyage
        anim_op.finished.connect(lambda: widget.setGraphicsEffect(None))
        
        # Garder en mémoire
        self._modal_anim = [anim_op, anim_pos]

    def fancy_modal_show(self, widget):
        # from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
        # from PySide6.QtWidgets import QGraphicsOpacityEffect, QApplication

        # 1. Préparation de l'état initial (invisible et décalé)
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
        eff.setOpacity(0)
        
        
        # Forcer le calcul du layout pour obtenir la position finale réelle
        # widget.adjustSize()
        widget.resize(widget.sizeHint())
        widget.show()
        widget.raise_()
        # widget.setMinimumSize(100, 100)
        QApplication.processEvents() 

        final_pos = widget.pos()
        start_pos = final_pos + QPoint(0, 30)
        widget.move(start_pos)

        # 2. Création des animations
        anim_op = QPropertyAnimation(eff, b"opacity")
        anim_op.setDuration(500)
        anim_op.setStartValue(0.0)
        anim_op.setEndValue(1.0)
        anim_op.setEasingCurve(QEasingCurve.OutQuad)

        anim_pos = QPropertyAnimation(widget, b"pos")
        anim_pos.setDuration(500)
        anim_pos.setStartValue(start_pos)
        anim_pos.setEndValue(final_pos)
        anim_pos.setEasingCurve(QEasingCurve.OutCubic)

        # 3. Groupement (plus propre pour gérer la fin)
        self._group = QParallelAnimationGroup()
        self._group.addAnimation(anim_op)
        self._group.addAnimation(anim_pos)

        # Nettoyage à la fin : on enlève l'effet pour libérer des ressources GPU
        self._group.finished.connect(lambda: widget.setGraphicsEffect(None))
        
        self._group.start()

    def server_checking(self):
        self.overlay.start_loading("Vérification en cours. Patientez SVP")
        self.api_handler_.verifier_health()

    def on_radio_domain_or_ip_changed(self):
        radio = self.sender()
        
        domain = bool(self.token_manager.get_adress_type())
        if radio.isChecked(): 
            # if domain:
            self.token_manager.save_adress_type(True)
            # self.token_manager.save_adress_type(True)
        else:
            self.token_manager.save_adress_type(True)
            print(f"Vous avez sélectionné on_radio_domain_or_ip_changed: {radio.text()}")

    def on_radio_direct_request_changed(self):
        request = self.token_manager.get_direct_request()
        radio = self.sender()  

        if radio.isChecked():   
            print(f" Checked")
            self.token_manager.save_direct_request(False) 
        else:
            print(f" not Checked")
            self.token_manager.save_direct_request(False)
    
   
    def on_async_finished(self, result):
        print("✔ Tâche terminée :", result)
        notify = Notify()
        notify.title = "Succès"
        notify.message = "PDF généré avec succès !"
        notify.send()


    def on_async_error(self, error):
        print("❌ Erreur :", error)
        notify = Notify()
        notify.title = "Erreur"
        notify.message = f"Erreur lors de la génération du PDF : {error}"
        notify.send()


    def on_async_start(self):
        print("🚀 Tâche en cours de démarrage...")
        notify = Notify()
        notify.title = "Information"
        notify.message = "Tâche en cours de démarrage... PDF lancé avec succès !"
        notify.send()


    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        x = int((screen.width() - window.width()) / 2)
        y = int((screen.height() - window.height()) / 2)
        self.move(x, y)

    def keyPressEvent(self, event):
        #         print(Qt.Key_Return)  # 16777265
        # print(Qt.Key_Enter)   # 16777267
        modifiers = event.modifiers()         
        if event.key() == 16777265 or event.key() == 16777267:
            self.search_student()
        if event.key() == 80:
            self.paiement_page()
        if event.key() == 68:
            self.dash_page()
        if event.key() == 65:
            self.admin_page()
        if event.key() == 69:
            self.etudiant_page()
        if event.key() == 67:
            self.cours_page()
        if event.key() == 78:
            self.notes_page()
        if event.key() == 86:
            self.vente_page()
        if event.key() == 82:
            self.rapport_page()
        if event.key() == 16777266:
            self.add_vente()
        if event.key() == 16777267:
            self.depense_page()
        if event.key() == 16777268:
            self.vente_page()
            

    def ajouter_dashboard(self, frame: QFrame):
        self.ui.frame_2.setHidden(True)
        layout = frame.layout()

        # --- Combo principal (type de graphique) ---
        combo = QComboBox()
        combo.addItems(["Paiements", "Inscriptions", "Réussite", "Rendement"])
        layout.addWidget(combo)

        # --- Combo période ---
        combo_periode = QComboBox()
        combo_periode.addItems(["Mensuel", "Trimestriel", "Annuel", "Personnalisée"])
        combo_periode.setVisible(False)
        layout.addWidget(combo_periode)

        # --- Widgets pour la période personnalisée ---
        date_layout = QHBoxLayout()
        lbl_debut = QLabel("Début :")
        date_debut = QDateEdit()
        date_debut.setCalendarPopup(True)
        date_debut.setDate(QDate.currentDate().addMonths(-1))

        lbl_fin = QLabel("Fin :")
        date_fin = QDateEdit()
        date_fin.setCalendarPopup(True)
        date_fin.setDate(QDate.currentDate())

        # Ajout au layout horizontal
        date_layout.addWidget(lbl_debut)
        date_layout.addWidget(date_debut)
        date_layout.addWidget(lbl_fin)
        date_layout.addWidget(date_fin)
        layout.addLayout(date_layout)

        # Masquer les sélecteurs de dates au départ
        lbl_debut.setVisible(False)
        date_debut.setVisible(False)
        lbl_fin.setVisible(False)
        date_fin.setVisible(False)

        # --- Création du graphique ---
        fig, ax = plt.subplots(figsize=(8, 4))
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)

        # --- Fonction de mise à jour ---
        def update_graph():
            ax.clear()
            choix = combo.currentText()
            periode = combo_periode.currentText()

            # Si Paiements → afficher combo période
            if choix == "Paiements":
                combo_periode.setVisible(True)

                # Si période personnalisée → afficher les dates
                is_custom = (periode == "Personnalisée")
                lbl_debut.setVisible(is_custom)
                date_debut.setVisible(is_custom)
                lbl_fin.setVisible(is_custom)
                date_fin.setVisible(is_custom)

                if periode == "Mensuel":
                    ax.bar(self.mois__, self.paiements, color="skyblue")
                    ax.set_title("Paiements mensuels")
                elif periode == "Trimestriel":
                    data = [sum(self.paiements[i:i+3]) for i in range(0, len(self.paiements), 3)]
                    labels = ["T1", "T2", "T3", "T4"]
                    ax.bar(labels[:len(data)], data, color="royalblue")
                    ax.set_title("Paiements trimestriels")
                elif periode == "Annuel":
                    total = sum(self.paiements)
                    ax.bar(["Année"], [total], color="navy")
                    ax.set_title("Paiements annuels")
                elif periode == "Personnalisée":
                    start = date_debut.date().toPython()
                    end = date_fin.date().toPython()
                    # ici tu peux filtrer selon les paiements entre start et end
                    filtered = self.paiements  # à remplacer par ton vrai filtrage
                    ax.bar(self.mois__, filtered, color="teal")
                    ax.set_title(f"Paiements du {start} au {end}")
            else:
                # Si autre type de graphique → cacher tout le reste
                combo_periode.setVisible(False)
                lbl_debut.setVisible(False)
                date_debut.setVisible(False)
                lbl_fin.setVisible(False)
                date_fin.setVisible(False)

                if choix == "Inscriptions":
                    ax.plot(self.mois__, self.inscriptions, marker="o", color="green")
                    ax.set_title("Inscriptions")
                elif choix == "Réussite":
                    ax.bar(self.mois__, self.reussite, color="orange")
                    ax.set_title("Réussite (%)")
                elif choix == "Rendement":
                    ax.plot(self.mois__, self.rendement, marker="x", color="red")
                    ax.set_title("Rendement (%)")

            fig.tight_layout()
            canvas.draw()

        # --- Connexions ---
        combo.currentIndexChanged.connect(update_graph)
        combo_periode.currentIndexChanged.connect(update_graph)
        date_debut.dateChanged.connect(update_graph)
        date_fin.dateChanged.connect(update_graph)

        # --- Premier affichage ---
        update_graph()



    def get_client_autorisation(self, uuid_modifie):
        parties = uuid_modifie.split("-")
        deuxieme = parties[2]
        nombre = deuxieme[:2]
        return nombre

        # Méthode 2 : regex
        match = re.search(r"-(\d{2})[a-zA-Z]{2}-", uuid_modifie)
        if match:
            print(match.group(1))  # "22"

    def get_client_autorisation1(self, uuid_modifie, liste_clients):
        
        parties = uuid_modifie.split("-")
        # On cherche le segment qui contient le code (ici le 3ème segment '22yp')
        segment_code = parties[2] 
        code_extrait = segment_code[:2] # Récupère '22'

        # 2. Boucle pour vérifier l'existence et le match
        client_trouve = None
        
        for client in liste_clients:
            # On compare le code extrait avec l'ID ou le code du client
            # (Adapte 'client['id']' selon la structure de tes données)
            if str(client.get('id')) == code_extrait:
                client_trouve = client
                print(f"Match trouvé ! Client: {client.get('nom')}")
                break # On arrête la boucle dès qu'on a trouvé
                
        if not client_trouve:
            print("Aucun client ne correspond au code extrait de l'UUID.")
            
        return client_trouve

    def load_interface(self): 
        self.resize(750, 500)
        
        if self.token_manager.get_token(): 
            self.overlay.start_loading("Chargement des données nécessaire. Patientez SVP")                
            self.api_handler_.verify_sanctum_token()
            self.api_handler_.verify_authorization_token(self.get_mac_address()[0])
                 
   
        else:
            try:
                self.resize(750, 500)
                if self.verifier_donnees:
                    if self.config_data and self.config_data['data'] is not None and 'data' in self.config_data and self.config_data['data']:
                        image_url = self.config_data['data'].get('logo_image_base64', '')

                        if image_url and not os.path.exists(self.icon_path_logo):
                            self.download_image(image_url, self.icon_path_logo)

                    if os.path.exists(self.icon_path_logo):
                        self.setWindowIcon(QIcon(self.icon_path_logo))
                        self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo)
                        # self.ui.logo.setPixmap(QPixmap(self.icon_path_logo))
                    else:
                        self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo_lock)

                    self.overlay.finish_loading() 
                    self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                    self.fade_in_page(self.ui.connexion_page)
                    
                else:
                    self.overlay.finish_loading() 
                    self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                    self.fade_in_page(self.ui.connexion_page)
                    
                self.overlay.finish_loading()
                return 
            except Exception as e:
                print(f"----------------------   {e}")
                import traceback
                traceback.print_exc()
                self.overlay.finish_loading()
    
    
    def handler_verify_token(self, response_data):
        if not response_data.get('success'):
            self.token_manager.delete_token()
            self.deconnexion()
            self.overlay.finish_loading()
            self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
            self.fade_in_page(self.ui.connexion_page)
            return

        self.user_roles = response_data.get("roles", "")
        self.user_permissions = response_data.get("permissions", "")
        self.user_info = response_data.get("user",[]) 

        user = self.user_info  
        self.user_connect.setText(user.get('id')) 
        if user.get('heart_auto'):
            heart_auto = user.get('heart_auto')['descript']
            last_key = heart_auto.split('--')[1]
            self.access_key = last_key
            self.access_key_info  = self.get_client_autorisation(user.get('client_infos'))
            print(f"\nin handler authorisation success {self.access_key}, \n  heart_auto {heart_auto} \n self.access_key_info  {self.access_key_info}")

        self.info_user_response_data = response_data
        self.overlay.finish_loading()   
        # self.dash_page()  
        # self.connect_buttons() 

    def handle_authorization_success(self, response): 
        # self.api_handler_.verify_sanctum_token(self.token_manager.get_token())
        is_authorized = response.get("data", {})  

        self.token_manager.save_direct_request(False) 
        
        if is_authorized.get('authorisation') != 1:
            self.show_authorization_error()
            self.overlay.finish_loading()
            return

        if self.config_data and self.config_data['data'] is not None and 'data' in self.config_data and self.config_data['data'] and len(self.config_data['data']) >0: 
            image_url = self.config_data['data'].get('logo_image_base64', '')

            if image_url and not os.path.exists(self.icon_path_logo):
                self.download_image(image_url, self.icon_path_logo)

        if os.path.exists(self.icon_path_logo):
            self.setWindowIcon(QIcon(self.icon_path_logo))
            self.show_image_logo_on_app(self.ui.logo_2,self.icon_path_logo)

        # verify_sanctum_token = self.check_data.verify_sanctum_token(self.token_manager.get_token())
        # if not verify_sanctum_token.get('success'):
        #     self.token_manager.delete_token()
        #     self.api_handler_.logout()
        #     self.overlay.finish_loading()
        #     self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)

        if is_authorized['authorisation'] != 1:
            self.deconnexion()
            self.token_manager.delete_token()
   
            self.overlay.finish_loading()
            self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
            self.fade_in_page(self.ui.connexion_page)
            QMessageBox.critical(self, "Avertissement", "Votre PC n'est pas autorisé à se connecter au serveur !") 
            # self.api_handler_.all_student_()

        try:
            self.request_certificate_ss()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(e)
            return
         

    def handle_authorization_error(self, endpoint, error):
        self.show_authorization_error()

    def show_authorization_error(self):
        self.deconnexion()
        self.token_manager.delete_token()

        self.overlay.finish_loading()
        self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
        self.fade_in_page(self.ui.connexion_page)
        QMessageBox.critical(self, "Avertissement", "Votre PC n'est pas autorisé à se connecter au serveur !..")


    def get_path(self, relative_path): 

        # PyInstaller (onefile)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS

        # Nuitka compiled exe
        elif getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)

        # Mode normal (Python)
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def get_real_path(self, relative_path): 

        # PyInstaller (onefile)
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS

        elif '__compiled__' in globals():
            # Nuitka
            base_path = os.path.dirname(sys.executable)
            print(f"base_path {base_path}    relative_path   {relative_path}")

        # Mode normal (Python)
        else:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)



    def handle_api_success(self, endpoint, method, response_data):
        """Gère toutes les réponses réussies"""
        handler = getattr(self, f"handle_{endpoint}_success", None)
        if handler:
            handler(response_data)
        else:
            self.generic_success_handler(endpoint, method, response_data)



    def handle_api_error(self, endpoint, method, error_msg, response_data):
        """Gère toutes les erreurs"""
        handler = getattr(self, f"handle_{endpoint}_error", None)
        if handler:
            handler(error_msg, response_data)
        else:
            self.generic_error_handler(endpoint, method, error_msg, response_data)

    def generic_success_handler(self, endpoint, method, response_data): 
        # print(endpoint, method)
        if endpoint !="live-student":
            self.search_camera_timer.stop()
             
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.search_camera_timer.stop()

            if self.camera_active:
                pass    

            if hasattr(self, "camera_thread") and self.camera_thread:
                self.stop_camera_thread111()             
                # self.stop_camera()
 

        if endpoint.startswith("v1/health"):
            print(endpoint, method)
            self.overlay.finish_loading()

        if self.user_info:
            self.restart_disconnect_timer()
        else:
            self.disconnect_timer.stop()

        if endpoint.startswith("v1/verify-token"):
            self.handler_verify_token(response_data)
        
        if endpoint.startswith("v1/student-specific-details"):
            if response_data: 
                self.update_details_view(response_data)

  
            

        if endpoint.startswith("v1/get-profile"):  
            if response_data:
                self.verifier_donnees = True
            else:
                self.verifier_donnees = False
            self.config_data = response_data

        if endpoint.startswith("v1/profile"):
            self.api_handler_.config_donnees()

        if endpoint.startswith("v1/assign-permission-to-role"):
            self.connect_buttons()

        if endpoint.startswith("v1/assign-role-to-user"):
            self.connect_buttons()

        if endpoint.startswith("v1/get-profile"):
            if response_data and 'errors' in response_data: #response.get('errors'): 
                erreurs =response_data.get('errors')
                self.appliquer_erreurs(erreurs, 
                    ('nom', self.ui.input_nom),
                    ('email', self.ui.input_email),
                    ('adresse', self.ui.input_adresse),
                    ('ligne1', self.ui.input_ligne1),
                    
                )
                self.overlay.finish_loading()
                QMessageBox.information(None, "Erreur", "Erreur")
            else:
                if response_data and 'data' in response_data:
                    image_url = response_data['data'].get('logo_image_base64', '')
                    if image_url:
                        self.download_image(image_url, self.icon_path_logo)
                        self.show_image_logo_on_app(self.ui.show_image,self.icon_path_logo)
                        self.setWindowIcon(QIcon(self.icon_path_logo))
                        self.show_image_logo_on_app(self.ui.logo_2,self.icon_path_logo)
                        self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo) 
                    else:
                        self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo_lock)
        

        if endpoint.startswith("v1/auth/login"):
            # print(endpoint, method, response_data,self.commande)
            self.handle_login_response(response=response_data)
        
        if endpoint.startswith("v1/vente-delete"):
            # print(endpoint, method, response_data,self.commande)
            if len(self.commande) < 1:
                self.vente_page()
                self.set_table_refresh_data_vente()

            self.set_table_refresh_data_for_commande()
            self.ui.frame_301.setHidden(True)
            self.overlay.finish_loading()
            
        if endpoint.startswith("v1/vente?page"):
            if response_data != self.all_ventes_data:
                self.all_ventes_data = response_data
                self.ui.label_commande_number.setText("0")
                self.set_table_refresh_data_vente() 
                self.overlay.finish_loading()
        if endpoint.startswith("v1/vente?search"):
            if response_data:
                self.all_ventes_data = response_data
                self.set_table_refresh_data_vente()

        if endpoint.startswith("v1/logs-graphic"): 
            if response_data != self.all_logs_data:
                self.all_logs_data = response_data  
                self.set_table_refresh_data_log() 
                self.overlay.finish_loading()

        if endpoint.startswith("v1/logs-graphic-show/"): 
            if response_data and 'data' in response_data:
                response = response_data.get('data', '') 
                action = response.get('action', '')
                model = response.get('model_type', '')
                # model = "App\\Models\\Etudiant"
                old_data = response.get('old_values',{})
                new_data = response.get('new_values',{})
                # old_data = '{"aide_financiere": "1/4 Bourse", "date_de_naissance": "2010-09-01 15:11:26"}'
                # new_data = '{"id": "03ca81ba-9c58-484f-a307-578d808dcd9f", "nom": "FLEURENVIL", "code": "1699", "prenom": "Beyonca"}'
                dialog = LogDetailsDialog(action, model, old_data, new_data)
                dialog.exec_()

        

        if endpoint.startswith("v1/programme?page") or endpoint.startswith("v1/programme?search"):
            if response_data != self.all_programme_data:            
                self.all_programme_data = response_data
                self.set_table_refresh_data_programme() 
                # self.programme_index()
                # self.add_programme_page()
                self.clear_layout_(self.ui.scrollAreaWidgetContents_10.layout())
                self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
                self.overlay.finish_loading()

        elif endpoint.startswith("v1/programme") and method =="POST":
            self.programme_index()
            self.clear_layout_(self.ui.scrollAreaWidgetContents_10.layout())
            self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
            self.overlay.finish_loading()

        elif endpoint.startswith("v1/programme/"):
            if response_data:
                self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_4.layout())
                self.add_programme_page() 
                self.add_programme_line(response_data['data'])

        if endpoint.startswith("v1/professeur?page") or endpoint.startswith("v1/professeur?search"):
            self.overlay.start_loading("Chargement des professeurs 1")
            if response_data != self.all_teacher_data:            
                self.all_teacher_data = response_data          
                self.api_handler_.teacher_combo()
                self.set_table_refresh_data_teacher() 
                self.clear_professeurs()
                self.overlay.finish_loading()
        if endpoint.startswith("v1/professeur") and method=="POST": 
            self.professeur_page()     

        elif endpoint.startswith("v1/professeur/"):            
            if response_data:
                self.add_professeur(response_data['data'])

        if endpoint.startswith("v1/delete-professeur"):
            self.professeur_page()
            self.api_handler_.get_data_user_for_loans()
            # self.api_handler_.teacher_combo()
            # self.set_table_refresh_data_teacher() 
            self.clear_professeurs()

        if endpoint.startswith("v1/personnel?page") or endpoint.startswith("v1/personnel?search"):
            if response_data != self.all_personnel_data:            
                self.all_personnel_data = response_data
                # self.admin_page()
                self.set_table_refresh_data_admin()
                self.clear_personnel()
                self.overlay.finish_loading()

        if endpoint.startswith("v1/personnel") and method=="POST": 
            self.admin_page() 

        elif endpoint.startswith("v1/personnel/"): 
            if response_data:
                self.add_personnel(personnel=response_data['data']) 

        if endpoint.startswith("v1/delete-personnel"):
            self.api_handler_.get_data_user_for_loans()
            self.admin_page()
            # self.set_table_refresh_data_admin()
            self.clear_personnel()
        


        if endpoint.startswith("load-etudiant"):          
            if response_data != self.all_students_data: 
                self.all_students_data = response_data

        if endpoint.startswith("v1/auth/autorisation-access"):
            self.token_manager.save_token_access(response_data['approval_token'])
 

        if endpoint.startswith("v1/etudiant?page") or endpoint.startswith("v1/etudiant?search"):  
            if response_data and response_data != self.all_etudiant_data:            
                self.all_etudiant_data = response_data
                self.set_table_refresh_data_student()  
                # self.etudiant_page()

        if endpoint.startswith("v1/etudiant") and method == 'POST': 
            self.clear_fields(self.ui.student_id, self.ui.nom, self.ui.prenom, self.ui.telephone, self.ui.email_3,self.ui.sexe, self.ui.adresse,self.ui.niveau_id,self.ui.classe_actuelle_id,self.ui.annee_academique_id,self.ui.religion, self.ui.date_de_naissance, self.ui.lieu_de_naissance ,self.ui.nom_responsable,
            self.ui.prenom_responsable,
            self.ui.email_responsable,
            self.ui.sexe_responsable,
            self.ui.telephone_responsable,
            self.ui.adresse_responsable,
            self.ui.aide_financiere,
            )     
            self.documents.clear() 

            if self.ui.frame_40:
                layout = self.ui.widget_piece_inner.layout()
        
                for i in range(layout.count()):
                    widget = layout.itemAt(i).widget()
                    if widget == self.ui.frame_40:
                        layout.removeWidget(widget)
                        widget.deleteLater()
                        break 
            self.etudiant_page()
            # self.api_handler_.all_student_()      
            self.overlay.finish_loading()


        elif endpoint.startswith("v1/etudiant/"):
            if response_data:
                self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)
                self.add_student_page(response_data['data'])
                # print(response_data['data'])
                            # self.add_student_page(show_student)
                self.ui.search_student_for_detail.setText('')
                self.fade_in_page(self.ui.add_student_page)
                self.ui.frame_171.setHidden(False)
                self.ui.frame_195.setHidden(False) 

        elif endpoint.startswith("etudiant-promus-to"):
            self.promus_page()
       
        

        if endpoint.startswith("v1/coursEtudiant") or endpoint.startswith("v1/coursEtudiant?search"): 
            if response_data != self.all_notes_data:            
                self.all_notes_data = response_data
                self.set_table_refresh_data_notes()
                self.overlay.finish_loading()

        if endpoint.startswith("v1/coursEtudiant") and method == 'POST':
            print(self.save_data_and_exit)
            if method == 'POST':
                if self.save_data_and_exit:
                    self.notes_page()
                    self.clear_layout(self.ui.widget_notes.layout())
                else:
                    # self.get_data_cours_list(self.data_cours_list)
                    self.ui.combo_evaluation.setPlaceholderText("Evaluation")
                    self.ui.combo_evaluation.clear()
                    for month in self.mois_:
                        self.ui.combo_evaluation.addItem(month)
                        
                    self.ui.change_cours.setPlaceholderText("Cours / Matière")
                    self.ui.affiche_cours.setText(self.data_cours_list.get('cours_nom'))

                    for row in range(self.model.rowCount()):
                        item_id = self.model.item(row, 0).text()  
                        item_identifiant = self.model.item(row, 1).text()  
                        item_note = self.model.item(row, 4).setText('') 
                self.overlay.finish_loading()
            else:
                self.notes_page()
                self.clear_layout(self.ui.widget_notes.layout())

            self.overlay.finish_loading()

        if endpoint == "v1/cours" and method == 'POST':
            self.api_handler_.cours_combo()
            self.cours_page()

        elif endpoint.startswith("v1/cours?page") or endpoint.startswith("v1/cours?search"):
            if response_data != self.all_cours_data:            
                self.all_cours_data = response_data
                self.set_table_refresh_data_cours() 

                self.clear_layout_(self.ui.scrollAreaWidgetContents_4.layout())
                self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_4.layout()) 
                self.ui.enregistrer_programme.setText('Enregistrer')
                self.overlay.finish_loading()

        elif endpoint.startswith("v1/cours/"):
            if response_data:
                self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
                self.add_cours_page()
                self.add_cours_line(response_data['data']) 

        elif endpoint.startswith("v1/for-combo-cours"):
            if response_data['cours'] != self.data_combo_cours:            
                self.data_combo_cours = response_data['cours']


        # if endpoint.startswith("coursEtudiant"):  
        #     if response_data != self.all_notes_data:            
        #         self.all_notes_data = response_data
        #         self.set_table_refresh_data_notes()
        #         self.notes_page()
        #         self.clear_layout(self.ui.widget_notes.layout())
        #         self.overlay.finish_loading()

        # if endpoint.startswith("cours"):
        #     if response_data != self.all_cours_data:            
        #         self.all_cours_data = response_data
        #         self.set_table_refresh_data_cours() 
        #         self.cours_page()

        #         self.clear_layout_(self.ui.scrollAreaWidgetContents_4.layout())
        #         self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_4.layout())
        #         self.ui.enregistrer_programme.setText('Enregistrer')
        #         self.overlay.finish_loading()
        if endpoint.startswith("v1/paiement?page"):  
            if response_data != self.all_paiement_data:  
                self.must_refresh_paiement=False          
                self.all_paiement_data = response_data
                self.set_table_refresh_data_paiement()
                self.overlay.finish_loading()
        if endpoint.startswith("v1/paiement?search"):
            self.all_paiement_data = response_data
            self.set_table_refresh_data_paiement()
        elif endpoint.startswith("v1/paiement/"):
            if response_data:
                # self.student_id_for_payment_show = id_item_et.text()
                self.show_payment(response_data, self.student_id_for_payment_show)
                self.ui.stackedPaiement.setCurrentWidget(self.ui.show_paiement)
                self.fade_in_page(self.ui.show_paiement)
                
        if endpoint.startswith("v1/next-payment-step"):                
            self.show_last_payment_and_details_if_exist(response_data['data']) 
            self.overlay.finish_loading()

        if endpoint.startswith("v1/post-payment-save"):  
            self.paiement_page() 
            self.mois={}
            self.accessoires={}
            id = response_data.get('id')
            keys = response_data.get('keys')
            self.overlay.start_loading("Générer le reçu")
            notify = Notify()
            notify.title = "Succès"
            notify.message = "Succès ! Attendez patiemment le temps qu'on génère le reçu."
            notify.send()
            result = self.api_handler_.recu_paiement(id=id, keys=keys)
           
            self.ui.stackedPaiement.setCurrentWidget(self.ui.index_paiement)
            self.clear_fields( self.montant_verser)
            self.fade_in_page(self.ui.index_paiement)
            

        if endpoint.startswith("v1/fetch-data-with-payment-params"):
            if response_data['data'] != self.show_student_for_payment:
                self.show_student_for_payment = response_data['data'][-1]

                first_info = self.show_student_for_payment
                
                self.ui.identifiant.setText(first_info['identifiant'])
                self.ui.identifiant.setStyleSheet("""color:#555;font-weight:bold""")
                self.ui.fname.setStyleSheet("""color:#555""")
                self.ui.lname.setStyleSheet("""color:#555""")
                self.ui.classe_actuelle.setStyleSheet("""color:#555""")
                self.ui.fname.setText(first_info['nom'])
                self.ui.lname.setText(first_info['prenom'])
                self.ui.classe_actuelle.setText(first_info['nom_classe'])
                profile = self.get_path(os.path.join('assets', 'icons', 'profile.png'))#label.setPixmap(pixmap)
                pixmap = QPixmap(profile)

                pixmap = pixmap.scaled(self.ui.imag_ilustrative.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.ui.imag_ilustrative.setPixmap(pixmap)

                self.add_scroll_bar(response_data['data'])
            #     show_student_for_payment_ = get_student_with_params_payment(id) 
            # self.data_comming_in_direct_params_payment(show_student_for_payment_)
                self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement) 
                self.fade_in_page(self.ui.add_paiement)
                self.overlay.finish_loading()
       
                
        if endpoint.startswith("v1/dashboard"):
            if response_data != self.all_dash_data:
                self.all_dash_data = response_data
                self.show_data_in_dash()
                # self.show_student_number_in_classes()
                self.overlay.finish_loading()

        if endpoint.startswith("v1/abonnement"):
            self.abonnement_data = response_data
            self.show_data_in_abonnement()
            self.overlay.finish_loading()

        if endpoint.startswith("v1/licence/appliquer"):
            # Clé de renouvellement appliquée localement : on recharge
            # l'onglet Abonnement pour refléter la nouvelle date d'expiration.
            self.abonnement_page()


        if endpoint.startswith("v1/niveau"): 
            if response_data and 'data' in response_data:             
                self.niveaux = response_data['data']
                self.ui.niveauId.setPlaceholderText('Section / Niveau / Cycle')
                self.ui.niveauId.clear() 
                for niveau in self.niveaux:
                    self.ui.niveauId.addItem(niveau['name'],niveau['id'])


        if endpoint.startswith("v1/annee-academique"):
            if response_data['data'] != self.annee_acades:            
                self.annee_acades = response_data['data']
                self.ui.combo_anne_for_dash.clear() 
                self.ui.anneeId.setPlaceholderText('Année')  
                self.ui.anneeId.clear()
            
                default_value = None
                for annee_acade in self.annee_acades:
                    self.ui.anneeId.addItem(annee_acade['annee_academique'], annee_acade['id'])
                    self.ui.combo_anne_for_dash.addItem(annee_acade['annee_academique'], annee_acade['id'])
                    default_value = annee_acade.get('status') if annee_acade.get('status') else None

                if default_value:
                    index = self.ui.combo_anne_for_dash.findData(default_value)
                    if index >= 0:
                        self.ui.combo_anne_for_dash.setCurrentIndex(index)

        if endpoint.startswith("v1/prof-for-combo"):
            if response_data['prof'] != self.teacherList:            
                self.teacherList = response_data['prof']
             

        if endpoint.startswith("v1/role"):
            if response_data['data'] != self.fetch_data_roles:            
                self.fetch_data_roles = response_data['data']
            

        if endpoint.startswith("v1/permission"):
            if response_data['data'] != self.fetch_data_permissions:            
                self.fetch_data_permissions = response_data['data'] 

        if endpoint.startswith("v1/active-teacher"):
            self.professeur_page() 
            self.overlay.finish_loading()

        if endpoint.startswith("v1/active-personnel"):
            self.admin_page()
            self.overlay.finish_loading()

        if endpoint.startswith("v1/change-password-personnel"):
            self.admin_page()  
            self.ui.reset_password_perso.setText('')
            self.ui.confirm_reset_password_perso.setText('')          
            
            self.ui.reinitialiser_mot_de_passe.setDisabled(False)
            self.overlay.finish_loading() 

        if endpoint.startswith("v1/change-password-teacher"):
            self.professeur_page() 
            self.ui.reset_password_prof.setText('')
            self.ui.confirm_reset_password_prof.setText('') 
            self.ui.btn_reset_password_prof.setDisabled(False)
            self.overlay.finish_loading()

        if endpoint.startswith("v1/client-authorisation-connect/") and method == "GET":
            # print(response_data)
            try:
                # time.sleep(15)
                self.handle_authorization_success(response_data) 
            except Exception as e:
                print(f"++++++++   {e}")
                self.deconnexion()
                self.token_manager.delete_token()
        
                self.ui.btn_connexion.setDisabled(False)
                self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                self.fade_in_page(self.ui.connexion_page)
                import traceback
                traceback.print_exc()
                self.overlay.finish_loading() 
                return
            self.overlay.finish_loading() 
        
        if endpoint.startswith("v1/client-authorisation-connect") and method == "POST":
            ip_text = self.ui.input_change_ip.text().strip() if self.ui.input_change_ip.text() else "" 
            self.ui.label_76.setText(f"  {ip_text} est en ligne sur le réseau!")
            self.ui.label_76.setStyleSheet("color: green;")
            self.ip_manager.delete_ip()
            self.ip_manager.save_server_ip(ip_text)
            self.add_or_update_host(ip=ip_text)
          
            self.overlay.finish_loading()   


        if endpoint.startswith("v1/password-change-user"):
            # self.admin_page()  
            if response_data is None:
                self.ui.error_message_2.setText("Impossible de contacter le serveur.")
                return

            if response_data and 'errors' in response_data or  'error' in response_data:
                self.ui.error_message_2.setText(response_data["errors"] if "errors" in response_data else response_data["error"]) 
                self.ui.btn_connexion.setDisabled(False)
                return
            
            self.handle_login_response(response_data)
            
            # if self.config_data and self.config_data['data'] is not None and 'data' in self.config_data and len(self.config_data['data']) >0:
            #     image_url = self.config_data['data']['logo_image_url']

            #     if image_url and not os.path.exists(self.icon_path_logo):
            #         self.download_image(image_url, self.icon_path_logo)

            # if os.path.exists(self.icon_path_logo):
            #     self.setWindowIcon(QIcon(self.icon_path_logo))
            #     self.show_image_logo_on_app(self.ui.logo_2,self.icon_path_logo)

            #     # pngcrush -ow -rem allb your_logo.png


            # user = response_data.get("user","") 
            # self.user_connect.setText(user.get('id'))
            # self.token_manager.save_user_email(user.get("email",""))
            # self.token_manager.save_token(response_data.get("token",""))
            # self.user_roles = response_data.get("roles", [])
            # self.user_permissions = response_data.get("permissions", [])
            # self.user_info = response_data.get("user",[]) 
            # self.info_user_response_data = response_data
            # self.dash_page()            
            # self.ui.btn_connexion.setDisabled(False)
            # self.connect_buttons() 


        if endpoint.startswith("v1/anneeAcademique?page"):
            if response_data != self.all_anneeAcademique:            
                self.all_anneeAcademique = response_data
                # self.annee_params_page()
                self.set_table_refresh_data_annee_academique()
                # self.api_handler_.annee_academique()
        elif endpoint.startswith("v1/anneeAcademique/"):
            if response_data:
                self.add_year(response_data)
                self.api_handler_.annee_academique()


        if endpoint.startswith("v1/fraisDinscription?page"): 
            if response_data != self.all_fee_paginate:            
                self.all_fee_paginate = response_data 
                self.set_table_refresh_data_frais()
        elif endpoint.startswith("v1/fraisDinscription"):
            if response_data:
                self.add_frais(response_data)


        if endpoint.startswith("v1/classes?page"):
            if response_data != self.all_classes_paginate:            
                self.all_classes_paginate = response_data
                # self.class_params_page()
                self.set_table_refresh_data_classe() 

        elif endpoint.startswith("v1/classes/"): # and not endpoint.startswith("classes?page"): 
            if response_data:           
                self.add_classe(response_data) 

        elif endpoint.startswith("v1/classes") and method =="POST":  
            self.api_handler_.classes_show_check()    


        if endpoint.startswith("v1/cl-load-asses_"): 
            if response_data['data'] != self.classes_combo:            
                self.classes_combo = response_data['data'] 

        if endpoint.startswith("v1/paramsExam?page"):
            if response_data != self.all_params_exam:            
                self.all_params_exam = response_data
                # print(response_data)
                # self.exam_params_page()
                self.set_table_refresh_data_param_exam()

        elif endpoint.startswith("v1/paramsExam/"):
            if response_data:
                self.add_param_exam(response_data)

        if endpoint.startswith("v1/parametrePaiement?page"):
            if response_data != self.all_paiement_params:            
                self.all_paiement_params = response_data
                # self.paiement_params_page()
                self.set_table_refresh_data_paiement_params()
        elif endpoint.startswith("v1/parametrePaiement"):
            if response_data: 
                self.add_paiement_params(response_data)
        
        if endpoint.startswith("v1/frais-divers-index"):
            if response_data != self.all_frais_divers:            
                self.all_frais_divers = response_data
                # self.frais_divers_params_page()
                self.set_table_refresh_data_frais_divers()

        if endpoint.startswith("v1/show-frais-divers"):
            if response_data and 'data' in response_data:
                self.add_frais_divers(response_data)
                # != self.all_frais_divers:            
                # self.all_frais_divers = response_data
                # self.frais_divers_params_page()
                # self.set_table_refresh_data_frais_divers()

        if endpoint.startswith("v1/show-faculte"):
            # print(f"response_data faculte {response_data}")
            if response_data and 'data' in response_data:
                self.add_faculte(response_data)
                

        if endpoint.startswith("v1/faculte?page"):
            if response_data['data'] != self.all_faculte:            
                self.all_faculte = response_data 
                self.set_table_refresh_data_faculte()

        if endpoint.startswith("v1/post-faculte"): 
            self.faculte_params_page()
 
        if endpoint.startswith("v1/vente") and method == "POST":
            self.vente_page()
            self.ui.table_show_order.setRowCount(0) 
            self.commande.clear()
            self.ui.label_commande_number.setText(str(0))
            self.set_table_refresh_data_for_commande()

            if response_data:
                # self.overlay.start_loading("Recu vente")
                self.overlay.start_loading('On génère le reçu')
                notify = Notify()
                notify.title = "Succès"
                notify.message = "Succès ! Attendez patiemment le temps qu'on génère le reçu."
                notify.send()
                response_ = self.api_handler_.get_Vente_receipt(response_data.get('id',''))
         

        if endpoint.startswith("v1/depense") and method == "POST":
            self.ui.id_depense.setText('')
            self.ui.description_depense.setText('')
            self.ui.prix_depense.setText('')
            self.api_handler_.all_depenses(self.current_page_depense)
            self.set_table_refresh_data_depense()

            self.overlay.finish_loading()

        if endpoint.startswith("v1/delete-depense"):  
            self.ui.id_depense.setText('')
            self.ui.description_depense.setText('')
            self.ui.prix_depense.setText('')
            self.ui.delete_depense.setHidden(True)
            self.api_handler_.all_depenses(self.current_page_depense)
            self.set_table_refresh_data_depense()
            self.overlay.finish_loading() 

 
        if endpoint.startswith("v1/post-loans") and method == "POST":
            # self.set_table_refresh_data_loans() 
            # self.api_handler_.all_loans(self.current_page_loans)
            self.tab_loans()
            self.overlay.finish_loading()

                
        if endpoint.startswith("v1/loans/repay") and method == "POST":
            self.ui.loans_id.clear()
            self.ui.amount_to_pay.clear()
            self.tab_loans()
            self.overlay.finish_loading()
        

        if endpoint.startswith("v1/get-loans?page") or endpoint.startswith("v1/get-loans?search"):  
            if response_data != self.all_loans_data:
                self.all_loans_data= response_data

            self.set_table_refresh_data_loans()
            self.overlay.finish_loading() 

        if endpoint.startswith("v1/delete-student"):
            # self.ui.id_depense.setText('')
            # self.ui.description_depense.setText('')
            # self.ui.prix_depense.setText('')
            # self.ui.delete_depense.setHidden(True)
            self.etudiant_page()
            self.overlay.finish_loading()
            
        if endpoint.startswith("v1/delete-paiement"): 
            self.paiement_page()
            self.overlay.finish_loading() 

        if  endpoint.startswith("v1/get-data-user-for-loans"):
            # print(f"get-data-user-for-loans  {response_data}")
            if response_data and 'data' in response_data:
                for _user in response_data['data']: 
                    nom = f"{_user['prenom']} {_user['nom']}"
                    self.ui.identifiant_user.addItem(nom, _user['id'])

        if endpoint.startswith("v1/depense?page"):
            if response_data != self.all_depense_data:
                self.all_depense_data = response_data
                self.set_table_refresh_data_depense()
                self.overlay.finish_loading()
        elif endpoint.startswith("v1/depense?sea"):
            if response_data:
                self.all_depense_data = response_data
                self.set_table_refresh_data_depense()

        if endpoint.startswith("v1/print-recu-inscrit"):
            if response_data:
                self.open_file_directly(response_data.content)
                self.overlay.finish_loading()
        


        if endpoint.startswith("v1/print-recu"):
            self.overlay.finish_loading()
            if response_data:
                self.print_paiement_recu__(response_data)

        if endpoint.startswith("v1/imprime-bulletin"):
            self.overlay.finish_loading()


        if endpoint.startswith("v1/imprime-mas-bulletin"):
            self.overlay.finish_loading()
       

        if endpoint.startswith("v1/get-all-faculte"):
            if response_data['data']:
                self.get_facultes = response_data['data']
                for faculte in response_data['data']:
                    self.ui.faculte_id.addItem(faculte['nom'], faculte['id'])

        if not endpoint.startswith("v1/auth/autorisation-access"):
            self.token_manager.delete_token_access()

        if endpoint.startswith("v1/other-transaction") and method =="POST":
            self.ui.transac_id.setText("")
            self.ui.transac_descript.setText("")
            self.ui.transac_amount.setText("")
            self.ui.combo_transact_identifiant.clear()
            self.ui.combo_transact_description.clear()
            self.autre_transaction()

        if endpoint.startswith("v1/edit-other-transaction") and method =="PATCH":
            self.ui.transac_id.setText("")
            self.ui.transac_descript.setText("")
            self.ui.transac_amount.setText("")
            self.ui.combo_transact_identifiant.clear()
            self.ui.combo_transact_description.clear()
            self.autre_transaction()
            


        elif  endpoint.startswith("v1/other-transaction?page"): 
            self.all_other_transac_data=response_data
            self.set_table_refresh_data_other_transac()

# ==============================================================================================================================================================================================================
        
                    
        if endpoint.startswith("v1/order-vente/"):
            if response_data['data']:
                [self.commande.append(data) for data in response_data['data']]

                if response_data['data'] and len(response_data['data']) > 0:
                    vente_id = response_data['data'][0].get("vente_id", "")
                    self.ui.vente_edit_id.setText(vente_id)
                self.ui.vente_status.setHidden(True) 
                self.ui.tabWidget_2.setCurrentWidget(self.ui.add_vente)
                self.fade_in_page(self.ui.add_vente)
                self.set_table_refresh_data_for_commande()

        if endpoint.startswith("v1/search/etudiant/"):
            if response_data['data']:
                self.all_students_data=response_data 
                self.set_table_refresh_search_for_card_show(response_data)

        if endpoint.startswith("v1/live-student"): 
            if response_data['data']: 
                if self.data_for_other_transac: 
                    self.live_search_student = response_data.get('data',{})
                # else:
                self.live_search_student = response_data
                if self.student_live_seach_input and self.student_live_seach_input.text() != '':
                    self.show_student_live(response_data)



                    # self.api_handler_.student_live(self.ui.search_for_card.text()) 

                    # if data and 'data' in data and len(data['data']) > 0:
                    #     self.ui.tableWidget.setRowCount(len(data['data'])) 
                    #     self.ui.widget_search_student.setHidden(False)
                    #     self.ui.frame_171.setHidden(True)
                    #     self.ui.frame_195.setHidden(True)
                    #     for row_idx, row_data in enumerate(data['data']):
                    #         for col_idx, value in enumerate(row_data):
                    #             self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
                    #     self.ui.tableWidget.cellClicked.connect(self.on_row_clicked_live_search_student)
                    # else:
                    #     self.ui.tableWidget.setRowCount(0)
                    #     self.ui.widget_search_student.setHidden(True)
                    #     self.ui.frame_171.setHidden(False)
                    #     self.ui.frame_195.setHidden(False)


        if endpoint.startswith("v1/niveau-with-class/"):
            if response_data and 'classe_actuelle' in response_data:    
                self.ui.classe_actuelle_id.clear()
                self.ui.classe_for_promus.clear()
                self.ui.classe_promus.clear() 
                self.ui.combo_financier_classe.clear()
                self.ui.combo_administratif_classe.clear()
                self.ui.combo_pedagogique_classe.clear()  
                
                self.ui.class_id.clear()

                self.ui.combo_financier_classe.addItem("All", "All")          
                for classe in response_data['classe_actuelle']:
 
                    self.ui.class_id.addItem(classe.get('nom_classe'), classe.get('id'))
 
                    self.ui.classe_actuelle_id.addItem(classe.get('nom_classe'), classe.get('id')) 
                    self.ui.classe_for_promus.addItem(classe.get('nom_classe'), classe.get('id'))
                    self.ui.classe_promus.addItem(classe.get('nom_classe'), classe.get('id')) 
                    self.ui.combo_financier_classe.addItem(classe.get('nom_classe'), classe.get('id')) 
                    self.ui.combo_administratif_classe.addItem(classe.get('nom_classe'), classe.get('id')) 
                    self.ui.combo_pedagogique_classe.addItem(classe.get('nom_classe'), classe.get('id'))

        if endpoint.startswith("v1/get-promus"):  
            if response_data and 'result' in response_data:
                # self.clear_layouts_promus()
                data = response_data['result']

                if not data:
                    self.ui.frame_322.setHidden(True)
                    QMessageBox.warning(None, "Avertissement", "Aucune donnée trouvée pour les paramètres fournis")
                    return

                if data:
                    layout = self.ui.frame_321.layout()
                    if layout is not None:
                        self.layouts_promus = layout
                    else:
                        self.layouts_promus = QVBoxLayout(self.ui.frame_321)

                    self.table_view_promus = QTableView()
                    # Création du modèle de table
                    self.model_promus = QStandardItemModel(len(response_data['result']), 7)

                    self.model_promus.setHorizontalHeaderLabels(["Id", "Nom", "Prénom","Total N.", "Total Coéff",  "Moy G.", "Status"])
                    self.table_view_promus.setModel(self.model_promus)
                    self.table_view_promus.setAlternatingRowColors(True)
                    self.table_view_promus.horizontalHeader().setStretchLastSection(True)
                    self.table_view_promus.verticalHeader().setVisible(False)
                    self.table_view_promus.setColumnHidden(0, True) 
                    self.table_view_promus.setColumnWidth(0, 22)
                    self.table_view_promus.setColumnWidth(1, 220)
                    self.table_view_promus.setColumnWidth(2, 220)
                    self.table_view_promus.setColumnWidth(3, 100)
                    self.table_view_promus.setColumnWidth(4, 100)  
                    self.table_view_promus.setColumnWidth(5, 100)
                    self.table_view_promus.setColumnWidth(6, 120)
                    
                    self.table_view_promus.horizontalHeader().setStyleSheet("""
                        QHeaderView::section {
                            background-color: #4b5564;  
                            font-size:13pt;
                            color: white;
                            font-weight: bold;
                            padding: 4px;  
                        }
                    """)

                    self.table_view_promus.setStyleSheet("""
                        alternate-background-color: #e2e8f0;
                                                    font-size:12pt;
                        background-color: #fff;
                    """)


                    for row, data in enumerate(response_data['result']):
                        item_id = QStandardItem(str(data.get('id', '')))
                        item_nom = QStandardItem(str(data.get('nom', '')))
                        item_prenom = QStandardItem(str(data.get('prenom', '')))
                        item_note = QStandardItem(str(data.get('note', '')))
                        item_max = QStandardItem(str(data.get('max', '')))
                        item_moyenne = QStandardItem(str(data.get('moyenne', '')))
                        item_status = QStandardItem(str(data.get('status', '')))  
                        
                        item_id.setEditable(False)
                        item_moyenne.setEditable(False)
                        item_nom.setEditable(False)
                        item_prenom.setEditable(False)

                        for item in [item_id, item_nom, item_prenom,item_note,item_max,item_moyenne,item_status]:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            font = QFont()
                            font.setPointSize(14)
                            item_moyenne.setFont(font)  


                            
                            # if float(item_moyenne.text()) >= 6:
                            if item_status.text() == 'Succès':
                                item_moyenne.setForeground(QBrush(QColor(0, 167, 238))) 
                                item_status.setForeground(QBrush(QColor(0, 255, 0)))
                            else:
                                item_moyenne.setForeground(QBrush(QColor(255, 0, 0)))
                                item_status.setForeground(QBrush(QColor(255, 0, 0)))


                            item_status.setFont(font)

                        self.model_promus.setItem(row, 0, item_id)
                        self.model_promus.setItem(row, 1, item_nom)
                        self.model_promus.setItem(row, 2, item_prenom)
                        self.model_promus.setItem(row, 3, item_note)
                        self.model_promus.setItem(row, 4, item_max)
                        self.model_promus.setItem(row, 5, item_moyenne)
                        self.model_promus.setItem(row, 6, item_status)

                    self.ui.frame_322.setHidden(False)
                    self.layouts_promus.addWidget(self.table_view_promus)
            


        if endpoint.startswith("v1/cours-etudiant-edit-note"):
            self.fill_notes_data_for_add_or_edit(response_data)


           
        if endpoint.startswith("v1/cours-etudiant-add-note"):
            if response_data:
                response = response_data['datas']

                if response_data and 'errors' in response_data:
                    erreur = response.get('errors')
                    QMessageBox.warning(None, "Avertissement", f"{erreur}") 
                    self.overlay.finish_loading()
                    return
                self.show_data_after_search_for_insert_notes(response_data)
        
        #         if response_data and response_data is not None:
        #             if response_data.get('errors'): 
        #                 erreurs =response.get('errors')
        #                 self.appliquer_erreurs(erreurs, 
        #                     ('cours', self.cours_for_note),
        #                     ('class', self.class_for_note),
        #                     ('niveau', self.niveau_for_note),
        #                     ('annee_academique', self.annee_academique_id_for_notes),
                            
        #                 )
                        
        #                 # if response.get('errors').startswith("Les paramètres des évaluation"):
        #                 #     QMessageBox.warning(None, "Avertissement", f"{erreurs}")
                        
        #                 # if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
        #                 #     QMessageBox.warning(None, "Avertissement", erreurs)
        #                 # else:
        #                 #     errors = erreurs or erreurs.get("warning","")
        #                 #     QMessageBox.warning(None, "Erreur", errors)
        #                 if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
        #                     QMessageBox.warning(None, "Avertissement", erreurs)
        #                 else:
        #                     # S'assurer que 'erreurs' est un dict et récupérer la clé "warning"
        #                     if isinstance(erreurs, dict):
        #                         errors = erreurs.get("warning", str(erreurs))  # par défaut: tout convertir en str
        #                     else:
        #                         errors = str(erreurs)

        #                     QMessageBox.warning(None, "Erreur", errors)
        #                 self.overlay.finish_loading()
        #             else:
        #                 self.data_cours_list = {}
        #                 self.ui.stackedNotes.setCurrentWidget(self.ui.add_notes)
        #                 # print(response)
        #                 if 'result' in response:
        #                     # try:
        #                     #     self.valid_button.clicked.disconnect()
        #                     # except:
        #                     #     pass
        #                     print(response)
        #                     if self.ui.widget_notes.layout():
        #                         self.clear_layout(self.ui.widget_notes.layout()) 
        #                     else:
        #                         self.layouts = QVBoxLayout(self.ui.widget_notes)  # Crée un nouveau layout
                            
        #                     self.ui.frame_355.setHidden(True)
        #                     self.ui.intra_button.setHidden(True)
        #                     self.ui.finale_button.setHidden(True)
        #                     self.ui.combo_evaluation.setHidden(True)

        #                     if response['examEcheance'] is not None:
        #                         if response['examEcheance']['evaluation_par']=='Mois' or 'mois':
        #                             self.controle = 'mois'

        #                             mois = response['month'] or  self.mois_
        #                             # for month in response['month']:
        #                             self.ui.combo_evaluation.setHidden(False)
        #                             self.ui.combo_evaluation.setPlaceholderText("Evaluation")
        #                             self.ui.combo_evaluation.clear()
        #                             for month in mois:
        #                                 self.ui.combo_evaluation.addItem(month)

                                
        #                     else:
        #                         self.ui.frame_355.setHidden(False)
        #                         self.ui.intra_button.setHidden(False)
        #                         self.ui.finale_button.setHidden(False)
        #                         self.controle = ''

        #                     self.ui.change_cours.setPlaceholderText("Cours / Matière")
        #                     list_cours = response.get("list_cours","")
        #                     self.ui.change_cours.clear()
        #                     for cours_ in list_cours:
        #                         self.ui.change_cours.addItem(cours_['cours_nom'], cours_['id'])   

        #                     try:
        #                         self.ui.change_cours.currentIndexChanged.disconnect()
        #                     except TypeError as e:
        #                         print(f"signal__ {e}")
        #                         pass  # Aucun signal n'était connecté

        #                     self.ui.change_cours.currentIndexChanged.connect(lambda index, cours_=response['list_cours']: self.get_data_cours_list(cours_))

        #                     # if response['examEcheance'] in None: # ['name'] != 'Universitaire':
        #                     #     self.ui.frame_355.setHidden(True)
        #                     #     self.ui.intra_button.setHidden(True)
        #                     #     self.ui.finale_button.setHidden(True)
        #                     # else:
        #                     #     self.ui.combo_evaluation.setHidden(True)

                        
        #                     self.ui.affiche_cours.setText('----')
        #                     # self.ui.affiche_cours.setText(response['cours']['cours_nom'])
        #                     classe_and_annee = response.get('annee','')
        #                     nom_classe = response['cours'].get("nom_classe", "")
        #                     session_0 = response['cours'].get("session", "")
        #                     self.sesson_in_cours = response['cours'].get("session", "")
        #                     self.ui.affiche_classe.setText(f"{nom_classe}  -  {classe_and_annee} ")
        #                     # Création du bouton
        #                     frame_button_note = QFrame()
        #                     layouts_button_note = QHBoxLayout(frame_button_note) 
        #                     layouts_button_note.setAlignment(Qt.AlignmentFlag.AlignRight)

        #                     self.button_q = QPushButton("Enregistrer et quitter")
        #                     self.button = QPushButton("Enregistrer les notes")
        #                     layouts_button_note.addWidget(self.button_q)
        #                     layouts_button_note.addWidget(self.button)
        #                     if isinstance(response['examEcheance'], str):
        #                         evaluation_par = json.loads(evaluation_par)

        #                     if isinstance(response['session'], str):
        #                         session = json.loads(response['session'])

        #                     try:
        #                         self.ui.combo_evaluation.currentIndexChanged.disconnect()
        #                     except TypeError as e:
        #                         print(f"signal {e}")
        #                         pass  # Aucun signal n'était connecté

        #                     if response['examEcheance'] is not None:
        #                         if response['examEcheance']['name']=='Technique':
        #                             session_0=None

        #                     self.ui.combo_evaluation.currentIndexChanged.connect(lambda index, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle: self.edit_data_note_all(session, annee_academique,evaluation_par))
        # # cours=response['cours']

        #                     self.button.clicked.connect(
        #                         lambda checked, session=session_0,
        #                             annee_academique=response['annee'],
        #                             evaluation_par=self.controle,
        #                             save_data_and_exit=False:
        #                             self.enregistrer_notes(session, annee_academique, evaluation_par, save_data_and_exit)
        #                     )

        #                     self.button_q.clicked.connect(lambda checked, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle, save_data_and_exit=True : self.enregistrer_notes(session, annee_academique,evaluation_par,save_data_and_exit))
                            
        #                     self.button.setCheckable(True)
        #                     self.table_view = QTableView()

        #                     # Création du modèle de table
        #                     self.model = QStandardItemModel(len(response['result']), 5)

        #                     delegate = EnterKeyDelegate(self.table_view)
        #                     self.table_view.setItemDelegateForColumn(4, delegate)

        #                     self.model.setHorizontalHeaderLabels(["Id", "Identifiant", "Nom", "Prenom", "Note"])
        #                     self.table_view.setModel(self.model)
        #                     self.table_view.setAlternatingRowColors(True)
        #                     self.table_view.horizontalHeader().setStretchLastSection(True)
        #                     self.table_view.verticalHeader().setVisible(False)
        #                     self.table_view.setColumnHidden(0, True) 
        #                     self.table_view.setColumnWidth(1, 200)
        #                     self.table_view.setColumnWidth(2, 220)
        #                     self.table_view.setColumnWidth(3, 300)
        #                     self.table_view.setColumnWidth(4, 100)  
                            
        #                     self.table_view.horizontalHeader().setStyleSheet("""
        #                         QHeaderView::section {
        #                             background-color: #4b5564;  
        #                             font-size:13pt;
        #                             color: white;
        #                             font-weight: bold;
        #                             padding: 4px;  
        #                         }
        #                     """)

        #                     self.table_view.setStyleSheet("""
        #                         alternate-background-color: #e2e8f0;
        #                                                 font-size:12pt;
        #                         background-color: #fff;
        #                     """)

        #                     self.button.setStyleSheet("""
        #                         QPushButton {
        #                             text-align: center;
        #                             padding: 5px;
        #                             min-width:120px;
        #                                         color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px;
        #                                         font-size:14pt;
        #                                 font-weight:bold;                }
        #                                         QPushButton:hover { color: #fff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; background-color:#007bff;font-size:16px}
        #                     """)

        #                     self.button_q.setStyleSheet("""
        #                         QPushButton {
        #                             text-align: center;
        #                             padding: 5px;
        #                             min-width:120px;
        #                                         color: #fcbc05; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px;
        #                                         font-size:14pt;
        #                                 font-weight:bold;                }
        #                                         QPushButton:hover { color: #fff; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px; background-color:#fcbc05;font-size:16px}
        #                     """)

        #                     # Ajout des données à la table
        #                     for row, data in enumerate(response['result']):
        #                         item_id = QStandardItem(str(data.get('id', '')))
        #                         item_identifiant = QStandardItem(str(data.get('identifiant', '')))
        #                         item_nom = QStandardItem(str(data.get('nom', '')))
        #                         item_prenom = QStandardItem(str(data.get('prenom', '')))
        #                         item_note = QStandardItem("")  
                                
        #                         item_id.setEditable(False)
        #                         item_identifiant.setEditable(False)
        #                         item_nom.setEditable(False)
        #                         item_prenom.setEditable(False)
        #                         # item_note.setEditable(True)

        #                         # Aligner le texte au centre pour toutes les cellules
        #                         for item in [item_id, item_identifiant, item_nom, item_prenom]:
        #                             item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        #                             item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                                    
        #                             item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        #                             font = QFont()
        #                             font.setBold(True)
        #                             font.setPointSize(15)
        #                             item_note.setFont(font)  

                                    
        #                             palette = QPalette()
        #                             palette.setColor(QPalette.Active, QPalette.Text, QColor(0, 0, 255))  # Bleu
        #                             palette.setColor(QPalette.Inactive, QPalette.Text, QColor(0, 0, 255))  # Bleu si inactif

        #                             item_note.setForeground(QBrush(QColor(0, 167, 238))) 


        #                             item_note.setFont(font)

        #                         self.model.setItem(row, 0, item_id)
        #                         self.model.setItem(row, 1, item_identifiant)
        #                         self.model.setItem(row, 2, item_nom)
        #                         self.model.setItem(row, 3, item_prenom)
        #                         self.model.setItem(row, 4, item_note)

        #                     self.layouts.setContentsMargins(20,0,20,5)
        #                     self.layouts.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        #                     self.layouts.addWidget(self.table_view)
        #                     # self.layouts.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight) 
        #                     self.layouts.addWidget(frame_button_note) 
        #                     self.overlay.finish_loading()

        #                 self.ui.notes_dialog.disconnect
        #                 self.dialog.close()
        #         # QTimer.singleShot(5, self.request_finished)

                    

        if endpoint.startswith("v1/delete-cours"):   
            if response_data:
                self.cours_page()

        if endpoint.startswith("v1/delete-programme"):   
            if response_data:
                self.programme_index()

        if endpoint.startswith("v1/delete-paramsExam"):   
            if response_data:
                self.set_table_refresh_data_param_exam()

        if endpoint.startswith("v1/student-with-classe"):
            if response_data: 
                self.dialog_ = QDialog()
                self.dialog_.setModal(True)
                self.dialog_.setFixedSize(900, 600)
                self.dialog_.setWindowTitle("Liste des élèves de la classe")

                # --- Initialisation des composants selon ta structure ---
                info_frame = QFrame()
                self.student_change = QComboBox(info_frame)
                self.level_change = QComboBox(info_frame) # Ajout du Level
                self.classe_change = QComboBox(info_frame)
                self.annee_academique_change = QComboBox(info_frame)
                self.change = QPushButton("Modifier", info_frame)

                # 1. Remplissage Étudiants (Ton code)
                self.student_change.setEditable(True)
                self.student_change.setInsertPolicy(QComboBox.NoInsert)
                self.student_change.clear()
                for student in response_data['data']:
                    fullName = f"{student.get('nom','')}  {student.get('prenom','')}"
                    self.student_change.addItem(fullName, student.get('id',''))

                all_items = response_data['data'].copy()
                self.student_change.lineEdit().textEdited.connect(lambda text: self.filter_items(text, self.student_change, all_items))

                # 2. Remplissage Niveaux (Level)
                self.level_change.clear()
                self.level_change.addItem("Niveau/Cycle", None)
                for level in self.niveaux: 
                    self.level_change.addItem(level.get("name",""), level.get("id",""))

                # 3. Remplissage Année (Ton code)
                self.annee_academique_change.clear()
                for annee in self.annee_acades:
                    self.annee_academique_change.addItem(annee.get("annee_academique",""), annee.get("id",""))

                # --- LOGIQUE DYNAMIQUE : Changement de Classe quand le Level change ---
                def update_classes():
                    level_id = self.level_change.currentData()
                    self.classe_change.clear()
                    # On filtre les classes qui appartiennent à ce level_id
                    filtered = [c for c in self.classes_combo if c.get('niveau_id') == level_id]
                    for c in filtered:
                        self.classe_change.addItem(c.get("nom_classe",""), c.get("id",""))

                self.level_change.currentIndexChanged.connect(update_classes)

                # --- MISE EN PAGE HORIZONTALE (Une seule ligne) ---
                info_layout = QHBoxLayout(info_frame)
                info_layout.setContentsMargins(5, 5, 5, 5)
                info_layout.setSpacing(10)

                # On ajoute tout sur le même layout horizontal
                info_layout.addWidget(self.student_change, 2) # Plus large
                info_layout.addWidget(self.level_change, 1)
                info_layout.addWidget(self.classe_change, 1)
                info_layout.addWidget(self.annee_academique_change, 1)
                info_layout.addWidget(self.change)

                # --- Layout Principal du Dialog ---
                layout = QVBoxLayout()



                self.table_show = QTableWidget()
                header = ("Id", "Identifiant", "Nom", "Prénom", "Sexe", "id_cls_etudiant", "status_cls_etudiant", "Actif", 'Supprimer')

                self.all_headers_table_labels(
                    self.table_show, header, "#e2e8f0", 32, 100, 210, 210, 100, 50, 50, 50, 100
                )
                self.table_show.setSelectionBehavior(QAbstractItemView.SelectRows)

                self.select_all_populate(response_data['data'], self.table_show, self.on_row_clicked_Show,['id', 'identifiant','nom','prenom','sexe','id_cls_etudiant','status_cls_etudiant'])
                self.table_show.setColumnHidden(5, True)  # id_cls_etudiant
                self.table_show.setColumnHidden(6, True)  # status_cls_etudiant
                row_count = self.table_show.rowCount()
                for row in range(row_count):
                    status_item = self.table_show.item(row, 6)  # Colonne status_cls_etudiant
                    checkbox = QCheckBox()
                    button__ = QPushButton("Supprimer")
                    button__.setStyleSheet("""
                                  QPushButton {
                        text-align: center;
                        padding: 5px;
                        min-width: 100px;
                        color: #e94335; 
                        border-radius: 5px; 
                        font-size: 13pt;
                    }
                    QPushButton:hover { 
                        color: #fff; 
                        background-color: #e94335;
                    }
                    """)
                    button__.setCursor(Qt.PointingHandCursor)
                    button__.setFlat(True)
                    valeur_statut = status_item.text()

                    # On vérifie si c'est "1", ou si c'est le mot "True" (insensible à la casse)
                    if status_item and (valeur_statut == "1" or valeur_statut.lower() == "true"):
                        checkbox.setChecked(True)
                    # if status_item and status_item.text() == "1" or int(status_item.text()) ==1:

                    status_cls_item_status = self.table_show.item(row, 5)  # id_cls_etudiant
                    if status_cls_item_status:
                        cls_status = status_cls_item_status.text()

                        def handle_checkbox_change(state, cb=checkbox, cls_status=cls_status):
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Question)
                            msg.setWindowTitle("Confirmation")
                            msg.setText("Voulez-vous vraiment changer le statut de l'élève ?")
                            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            msg.setDefaultButton(QMessageBox.No)
                            reponse = msg.exec_()

                            if reponse == QMessageBox.Yes:
                                self.update_student_status(cls_status, state, delete=False)
                            else:
                                cb.blockSignals(True)
                                cb.setChecked(not cb.isChecked())
                                cb.blockSignals(False)
                                    # else:
                                self.overlay.finish_loading()

                        def handle_delete_in_class(state, btn=button__, cls_status=cls_status):
                            msg = QMessageBox(self)
                            msg.setIcon(QMessageBox.Question)
                            msg.setWindowTitle("Confirmation")
                            msg.setText("Voulez-vous vraiment supprimer l'élève de la classe?")
                            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            msg.setDefaultButton(QMessageBox.No)
                            reponse = msg.exec_()

                            if reponse == QMessageBox.Yes:
                                self.update_student_status(cls_status, state, delete=True)
                            # else:
                            #     cb.blockSignals(True)
                            #     cb.setChecked(not cb.isChecked())
                            #     cb.blockSignals(False)
                            else:
                                self.overlay.finish_loading()

                        checkbox.stateChanged.connect(handle_checkbox_change)
                        button__.clicked.connect(handle_delete_in_class)

                    # checkbox.setStyleSheet("""
                    #     QCheckBox {
                    #         max-width: 13px;
                    #         border: 1px solid #666;
                    #         border-radius: 4px;
                    #         padding-left: 18px; 
                    #         padding-right: 0px;
                    #     }
                    #     QCheckBox::indicator {
                    #         /*width: 13px;
                    #         height: 13px;*/
                    #         border: 1px solid #40C057;
                    #         border-radius: 4px;
                    #         background-color: white;
                    #     }
                    #     QCheckBox::indicator:checked {
                                           
                    #         background-color: #40C057;
                    #         border: 1px solid #40C057;
                    #     }
                    # """)

                    cell_widget = QWidget()
                    layout_cb = QHBoxLayout(cell_widget)
                    layout_cb.addWidget(checkbox)
                    layout_cb.setAlignment(Qt.AlignCenter)
                    layout_cb.setContentsMargins(0, 0, 0, 0)
                    self.table_show.setCellWidget(row, 7, cell_widget)

                    cell_widget_button = QWidget()
                    layout_btn = QHBoxLayout(cell_widget_button)
                    layout_btn.addWidget(button__)
                    layout_btn.setAlignment(Qt.AlignCenter)
                    layout_btn.setContentsMargins(0, 0, 0, 0)
                    self.table_show.setCellWidget(row, 8, cell_widget_button)

                # layout.addWidget(frame_button)
                # layout.addWidget(self.table_show)
                # self.dialog_.setLayout(layout)
                # self.dialog_.exec()

                layout.addWidget(info_frame)    # Ta ligne d'outils
                layout.addWidget(self.table_show) # Ton tableau (déjà défini)

                self.dialog_.setLayout(layout)
                self.change.clicked.connect(self.change_student_class) 

                self.dialog_.exec()

                # layout.addWidget(frame_button)
                # layout.addWidget(frame_classe_change)
                # layout.addWidget(self.table_show)
                # self.dialog_.setLayout(layout)
                # self.dialog_.exec()

        
        if endpoint.startswith("v1/fetch-data-with-role"):
            if not response_data or 'data' not in response_data or not response_data['data']:
                QMessageBox.information(None, "Avertissement", "Aucune donnée à afficher")
                return
            header = ("Id", "Nom", "Prénom")
            self.all_headers_table_labels(
                self.ui.table_roles, header, "#e2e8f0", 30, 250, 200)
            self.ui.table_roles.setSelectionBehavior(QAbstractItemView.SelectRows)
            
            
            if response_data and 'data' in response_data:
                row_datas = response_data['data']
                self.ui.table_roles.setRowCount(1)
                self.ui.table_roles.setHidden(False)
                self.ui.frame_258.setHidden(True)
                self.ui.widget_14.setHidden(True)

                for row_idx, row_data in enumerate(row_datas):
                    self.ui.table_roles.insertRow(row_idx)
                    
                    self.ui.table_roles.setItem(row_idx, 0, QTableWidgetItem(row_data.get("id", "")))
                    self.ui.table_roles.setItem(row_idx, 1, QTableWidgetItem(row_data.get("nom", "")))
                    self.ui.table_roles.setItem(row_idx, 2, QTableWidgetItem(row_data.get("prenom", "")))
                    self.roles_ids = [role for role in row_data.get("roles", [])]

                self.ui.table_roles.cellClicked.connect(self.on_row_clicked_live_search_role)
            else:
                self.ui.table_roles.setRowCount(0)
                self.ui.frame_258.setHidden(False)
                self.ui.widget_14.setHidden(False)

            
        if endpoint.startswith("v1/get-permission-by-role/"):
            if response_data:
                self.permission_ids = [permission["id"] for permission in response_data.get("permis","")]
                self.show_permissions()

        if endpoint.startswith("v1/fetch-data-with-permission"):        
            if not response_data or 'data' not in response_data or not response_data['data']:
                QMessageBox.information(None, "Avertissement", "Aucune donnée à afficher")
                return
            
            header = ("Id", "Nom", "Prénom")
            self.all_headers_table_labels(
                self.ui.table_permission, header, "#e2e8f0",30, 250, 100)
            self.ui.table_permission.setSelectionBehavior(QAbstractItemView.SelectRows)
            
            
            if response_data and 'data' in response_data:
                row_datas = response_data['data']
                self.ui.table_permission.setRowCount(1)
                self.ui.table_permission.setHidden(False)
                self.ui.frame_254.setHidden(True)
                self.ui.widget_15.setHidden(True)
                self.ui.table_permission.setRowCount(0)
                # self.ui.table_permission.resizeColumnsToContents()


                for row_idx, row_data in enumerate(row_datas):
                    # print(f"row_data {row_data}")
                    self.ui.table_permission.insertRow(row_idx)
                    
                    self.ui.table_permission.setItem(row_idx, 0, QTableWidgetItem(row_data.get("id", "")))
                    self.ui.table_permission.setItem(row_idx, 1, QTableWidgetItem(row_data.get("nom", "")))
                    self.ui.table_permission.setItem(row_idx, 2, QTableWidgetItem(row_data.get("prenom", "")))
 

                    self.permission_ids = [permission for permission in row_data.get("permissions", [])]
                self.ui.table_permission.cellClicked.connect(self.on_row_clicked_live_search_permission)
            else:
                self.ui.table_permission.setRowCount(0)

                self.ui.table_permission.setHidden(True)

                self.ui.frame_254.setHidden(False)
                self.ui.widget_15.setHidden(False)
            

        self.overlay.finish_loading()
        if endpoint == 'logout':
            self.disconnect_timer.stop()

        if method != 'GET' and endpoint.startswith("v1/auth/autorisation-access"):
            self.dialog_delete.close()
            QMessageBox.information(
                self, 
                "Succès", 
                response_data.get('message',"")
            )  
        elif method != 'GET' and endpoint !='v1/auth/login' and endpoint !='v1/auth/logout' and endpoint !='v1/live-student' and endpoint != 'v1/cours-etudiant-edit-note' and endpoint != 'v1/cours-etudiant-add-note' and endpoint != "v1/search/etudiant/" and endpoint != "v1/post-payment-save" and (endpoint != "v1/vente" and method == "POST") and endpoint !="v1/student-specific-details":
            QMessageBox.information(
                self, 
                "Succès", 
                response_data['message'] if response_data and 'message' in response_data else f"Opération réussie!"
            )
        
        self.overlay.finish_loading()

    def generic_error_handler111(self, endpoint, method, error_msg, response_data):

        try:
            full_message = ""
            
            if response_data is None:
                full_message = error_msg or "Erreur inconnue"
            elif isinstance(response_data, dict):
                full_message = response_data.get('detail', 
                            response_data.get('message', 
                            response_data.get('error', str(response_data))))
            else:
                full_message = str(response_data)
                
            # Vérifications
            if full_message and full_message != "":
                full_message_lower = full_message.lower()
                if not any(pattern in full_message_lower for pattern in 
                        ['sqlstate', 'unauthenticated', 'invalid token', 'token expired']):
                    QMessageBox.critical(self, "Erreur", full_message)
                    
        except Exception as e:
            print(f"[ERROR] Erreur dans le handler d'erreur: {e}")
            import traceback
            traceback.print_exc()

    def parse_fastapi_error(self, response_data):
        """Parse les erreurs FastAPI de manière intelligente"""
        if not isinstance(response_data, dict):
            return None
        
        # 1. Chercher les erreurs de validation détaillées
        if 'errors' in response_data:
            errors = []
            for error in response_data['errors']:
                # Message de base
                msg = error.get('msg', '')
                
                # Essayer d'extraire le message d'erreur Python
                ctx = error.get('ctx', '')
                if isinstance(ctx, str):
                    # Chercher ValueError, TypeError, etc.
                    import re
                    patterns = [
                        r"ValueError\('([^']+)'\)",
                        r"TypeError\('([^']+)'\)", 
                        r"ValidationError\('([^']+)'\)",
                        r"'error':\s*(\w+)\(([^)]+)\)"
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, ctx)
                        if match:
                            if len(match.groups()) > 1:
                                msg = f"{match.group(1)}: {match.group(2)}"
                            else:
                                msg = match.group(1)
                            break
                
                # Ajouter le champ concerné
                loc = error.get('loc', [])
                field_name = loc[-1] if loc else "Données"
                
                errors.append({
                    'field': str(field_name),
                    'message': msg,
                    'type': error.get('type', ''),
                    'raw_error': error
                })
            
            return {
                'type': 'validation',
                'message': response_data.get('message', 'Erreur de validation'),
                'errors': errors
            }
        
        # 2. Message simple
        elif 'detail' in response_data:
            return {
                'type': 'simple',
                'message': str(response_data['detail'])
            }
        
        # 3. Message standard
        elif 'message' in response_data:
            return {
                'type': 'simple', 
                'message': response_data['message']
            }
        
        return None

    def generic_error_handler(self, endpoint, method, error_msg, response_data):
 
        self.overlay.finish_loading()
        if self.user_info:
            self.restart_disconnect_timer()
        else:
            self.disconnect_timer.stop()

        if endpoint.startswith("v1/licence/appliquer"):
            # Synchro silencieuse en arrière-plan : un échec (offline, droits
            # insuffisants...) ne doit pas interrompre l'utilisateur avec une
            # boîte de dialogue, l'onglet Abonnement réessaiera à sa prochaine
            # ouverture.
            print(f"⚠️ Échec application licence distante : {error_msg}")
            return

        if 'Invalid JSON: Expecting value: line 1 column' in error_msg:
            QMessageBox.critical(
                    self,
                    "Erreur",
                    "Une erreur inconnue est survenue."
                )

        print("Response error content  yy:", response_data, error_msg, method, endpoint,response_data)

        if endpoint.startswith("v1/abonnement"):
            detail = (response_data or {}).get("detail") if isinstance(response_data, dict) else None
            QMessageBox.warning(self, "Abonnement", detail or "Impossible de récupérer les informations d'abonnement.")
            return

        if endpoint.startswith("v1/professeur") and method == "POST":
            prof_data={
                # 'id':self.id_professeur_for_update.text(),
                'nom':self.ui.nom_prof,
                'prenom':self.ui.prenom_prof,
                'email':self.ui.email_prof,
                # 'notification':self.ui.notif_prof.isChecked(),
                'sexe':self.ui.sexe_prof,
                'adresse':self.ui.adresse_prof,
                'matiere_enseignee':self.ui.matiere_enseignee,
                'telephone':self.ui.telephone_prof,
                # 'user_id':self.user_connect.text()
            } 
            HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=prof_data, overlay=self.overlay)
            return

        if endpoint.startswith("v1/personnel") and method == "POST":
            admin_data={ 
                "nom": self.ui.admin_nom,
                "telephone": self.ui.admin_telephone,
                "prenom": self.ui.admin_prenom,
                "email": self.ui.admin_email,
                "sexe": self.ui.admin_sexe,
                "adresse": self.ui.admin_adresse,
                "role": self.ui.admin_role,
            } 
            HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=admin_data, overlay=self.overlay)
            return

        if endpoint.startswith("v1/cours-etudiant-add-note") and method == "POST":
            admin_data={ 
                "niveau": self.niveau_for_note,
                "class": self.class_for_note,
                "cours": self.cours_for_note, 
                "annee_academique":self.annee_academique_id_for_notes,
                'faculte':self.faculte__,
                'session':self.session__,
            } 
            HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=admin_data, overlay=self.overlay)
            return

        if endpoint.startswith('v1/auth/login') or endpoint.startswith('v1/health'):
            if error_msg.startswith('Connection refuse') or error_msg.startswith('Operation canceled'):
                QMessageBox.critical(
                self,
                f"Serveur inaccessible",
                "Le serveur ne répond pas. Contactez l'administrateur."
            )
            if isinstance(response_data, dict) and "detail" in response_data: 
                error=response_data.get('detail')
                self.ui.label_76.setText(f"{error}")
                self.ui.label_76.setStyleSheet("color: red;")
            self.ui.btn_connexion.setDisabled(False) 

        if endpoint.startswith("v1/health") and 'Connection timed out' in error_msg:
            QMessageBox.critical(
                self,
                "Serveur inaccessible",
                "Le serveur ne répond pas. Contactez l'administrateur."
            )
            self.overlay.finish_loading()
            return

        if endpoint.startswith("v1/client-authorisation-connect/") and method == "GET":
            # self.deconnexion()
            self.token_manager.delete_token()
        
            self.api_handler_.logout()
            self.overlay.finish_loading()
            self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
            self.fade_in_page(self.ui.connexion_page)
            return
 

        try:            
            self.show_erros(error_msg, response_data)                     
        except Exception as e:
            import traceback
            traceback.print_exc()
            if isinstance(response_data, dict):
                QMessageBox.critical(
                    self,
                    "Erreur",
                    str(response_data)
                )
    def show_erros(self,error_msg,response_data):
        """
        Extrait proprement les messages d'erreurs de validation (FastAPI / Laravel-like)
        Retourne une string prête à afficher.
        """
        messages = []
        
        if not response_data:
             return "Une erreur inconnue est survenue."
             
        if isinstance(response_data, dict) and "errors" in response_data:
             errors = response_data["errors"]
             error_fields = []
             
             if isinstance(errors, list):
                 for err in errors:
                      msg = err.get("msg", "Erreur inconnue")
                      
                      field_name = err.get('loc', ['champ'])[-1]
                      error_fields.append(field_name)
                    
                      if msg.startswith("Input "):
                         msg = msg.replace("Input ", "", 1)
                    
                      msg = msg.replace("Value error,", "").strip()
                    
                      clean_message = f"<b>{field_name}</b>: {msg}" 
                      messages.append(clean_message)
                    
             elif isinstance(errors, dict):
                 for field, errs in errors.items():
                      if isinstance(errs, list) and errs:
                         messages.append(f"{field.capitalize()} : {errs[0]}")
                      else:
                         messages.append(f"{field.capitalize()} : {errs}")

          # 🔹 Message global
        elif isinstance(response_data, dict) and "message" in response_data:
               
             messages.append(response_data["message"])

        elif isinstance(response_data, dict) and "detail" in response_data:
               
             detail = response_data.get("detail")
             
             if isinstance(detail, dict) and "errors" in detail:
                  d=detail.get("errors","") 
                  if isinstance(d, dict) and "warning" in detail.get("errors",""):
                       m=detail.get("errors",{}).get("warning","")  
                       messages.append(m)
                  else:   
                       if "errors" in detail: 
                           x=detail.get("errors","") 
                           print(x)                                   
                           messages.append(x)
             else:
                  messages.append(str(detail))
          # 🔹 Fallback
        else: 
            detail = response_data.get("detail", "")
            messages.append(str(detail))
        full_message = "\n".join(f"• {m}" for m in messages if m)
        if 'SQLSTATE' not in full_message:
            QMessageBox.critical(
               self,
               f"Échec",
               full_message
               )

    # def extract_validation_messages(self,response_data):
    #     """
    #     Extrait proprement les messages d'erreurs de validation (FastAPI / Laravel-like)
    #     Retourne une string prête à afficher.
    #     """
    #     messages = []

    #     if not response_data:
    #         return "Une erreur inconnue est survenue."

    #     if isinstance(response_data, dict) and "errors" in response_data:
    #         errors = response_data["errors"]

    #         if isinstance(errors, list): 
    #             for err in errors: 
    #                 msg = err.get("msg")
    #                 if msg: 
    #                     msg = msg.replace("Value error,", "").strip()
    #                     messages.append(msg)
                
    #         elif isinstance(errors, dict):
    #             print("Cas Laravel : {")
    #             # Cas Laravel : {"errors": {"field": ["msg"]}}
    #             for field, errs in errors.items():
    #                 if isinstance(errs, list) and errs:
    #                     messages.append(f"{field.capitalize()} : {errs[0]}")
    #                 else:
    #                     messages.append(f"{field.capitalize()} : {errs}")

    #     # 🔹 Message global
    #     elif isinstance(response_data, dict) and "message" in response_data:
            
    #         messages.append(response_data["message"])

    #     elif isinstance(response_data, dict) and "detail" in response_data:
             
    #         detail = response_data.get("detail")
            
    #         if isinstance(detail, dict) and "errors" in detail:
    #             d=detail.get("errors","") 
    #             if isinstance(d, dict) and "warning" in detail.get("errors",""):
    #                 m=detail.get("errors",{}).get("warning","")  
    #                 messages.append(m)
    #             else:   
    #                 if "errors" in detail: 
    #                     x=detail.get("errors","") 
    #                     print(x)                                   
    #                     messages.append(x)
    #         else:
    #             messages.append(str(detail))
    #     # 🔹 Fallback
    #     else:
    #         print(f"Fallback",type(response_data))
    #         messages.append(str(response_data))
    #     print(f"messages messages   {messages}")
    #     return "\n".join(f"• {m}" for m in messages if m)

    def change_student_class(self):
        # Récupération des IDs
        student_id = self.student_change.currentData()
        new_classe_id = self.classe_change.currentData()
        annee = self.annee_academique_change.currentText()
        level = self.level_change.currentText()

        if not student_id or not new_classe_id:
            print("Erreur: Sélectionnez un étudiant et une classe")
            return

        # Préparation de l'appel API (FastAPI)
        url = "https://aplekol360.local/api/v1/change-student-class"
        payload = {
            "student_id": student_id,
            "new_classe_id": new_classe_id,
            "academic_year": annee
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.token_access}"}
            # with httpx.Client(verify=self.cert_path) as client:
            #     response = client.post(url, json=payload, headers=headers)
                
            #     if response.status_code == 200:
            #         print("Changement de classe réussi !")
            #         # Optionnel : rafraîchir la liste ou afficher un message succès
            #     else:
            #         print(f"Erreur serveur : {response.text}")
        except Exception as e:
            print(f"Erreur de connexion : {e}")


    def generic_direct_error_message(self, response_data):
        if self.user_info:
            self.restart_disconnect_timer()
        else:
            self.disconnect_timer.stop()
        full_message = ""
        full_error = ""
        if isinstance(response_data, dict):
            if "errors" in response_data:
                if isinstance(response_data["errors"], dict):
                    # Cas habituel : {"errors": {"field": ["message"]}}
                    messages = []
                    for field, errors in response_data["errors"].items():
                        if isinstance(errors, list):
                            QTimer.singleShot(200, self.overlay.finish_loading)
                            messages.append(f"{field.capitalize()} : {errors[0]}")
                        else:
                            QTimer.singleShot(200, self.overlay.finish_loading)
                            messages.append(f"{field.capitalize()} : {str(errors)}")
                    full_message = "\n".join(messages)
                elif isinstance(response_data["errors"], str):
                    # Cas spécial : {"errors": "message simple"}
                    full_message = response_data["errors"]
                    full_error = response_data["errors"]
            else:
                if 'message' in response_data:
                    full_message = response_data['message']
                full_error = str(response_data)
                # print(f"full_message in error_msg or str(response_data) {full_message}")
        elif isinstance(response_data, str):
            full_message = response_data
            full_error = response_data
            
        else:
            full_message = "Une erreur inconnue est survenue."
            full_error = "L'adresse ip du server n'est pas correspond a celle que vous indiquez."
        QTimer.singleShot(200, self.overlay.finish_loading)
        self.ui.label_76.setText(f"{full_error}")
        self.ui.label_76.setStyleSheet("color: red;")
        if 'SQLSTATE' not in full_message and 'Unauthenticated' not in full_message and full_message != "":
            QMessageBox.critical(
                self,
                f"Échec",
                full_message
            )
            return

    def run_as_admin(self):
        """ Relance le script en mode administrateur si ce n'est pas déjà le cas. """
        if sys.platform != "win32":
            # Pas d'équivalent ShellExecuteW("runas") hors Windows : on ne peut pas
            # se ré-élever soi-même sans repasser par un prompt sudo/osascript
            # explicite. On informe l'utilisateur plutôt que de planter sur
            # ctypes.windll, absent sur Mac/Linux.
            print(" Droits administrateur requis. Relancez l'application avec 'sudo' (Linux/Mac).")
            return False

        if ctypes.windll.shell32.IsUserAnAdmin():
            return True  # Déjà en mode admin, on continue

        print(" Ce script nécessite les droits administrateur. Redémarrage en mode administrateur...")
        params = " ".join([f'"{arg}"' for arg in sys.argv] + ["--as-admin"])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

    def request_certificate(self):
        ip = self.ui.input_change_ip.text().strip() if self.ui.input_change_ip.text() else "10.13.13.2"
        domain = bool(self.token_manager.get_adress_type())
        if domain:
            url_certificate = f"https://aplekol360.local/api/asking"
        else:
            url_certificate = f"https://aplekol360.local/api/asking"
        
        mac, username = self.get_mac_address()
        params = {"mac_address": mac}
        
        if domain:
            url_autorize = f"https://aplekol360.local/api/client-authorisation-connect"
        else:
            url_autorize = f"https://aplekol360.local/api/client-authorisation-connect"

        payload = {"client_mac": mac, "client_name": username}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        try:
            response = requests.post(url_autorize, json=payload, headers=headers, timeout=15)
            response_data = response.json()
            if response.status_code == 200:
                response = requests.post(url_certificate, json=params, headers=headers, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    if data and 'data' in data and data['status'] == 1:
                        if domain:
                            self.add_or_update_host(ip=self.ip_manager.get_server_ip())
                        # server_path = r"C:\Program Files\gestion ecole\crt\server.crt"
                        # os.makedirs(os.path.dirname(server_path), exist_ok=True)
                       
                        # with open(server_path, "wb") as f:
                        #     f.write(base64.b64decode(data['data']))
                        
                        # print(base64.b64decode(data['data']))
                        # if "--as-admin" not in sys.argv:
                        #     self.run_as_admin()
                return True
            return response_data
        except requests.RequestException as e:
            print(f"Erreur: {e}")
            return False
        

    def request_certificate_ss(self):
        mac, username = self.get_mac_address()
        params = {"mac_address": mac}
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        # server_path = r"C:\ProgramData\certs"
        # server_path = r"C:\Users\Charlorie\AppData\Local\.ecole_360\.certs"

        server_path = os.path.join(get_local_data_dir(), ".ecole_360", ".certs")
        if not os.path.exists(server_path):
            # from .EssantielController import asking, load_data 
            try:
                status_code = None

                url_certificate = f"https://aplekol360.local/api/v1/asking"

                # Route serveur définie en GET avec mac_address en query param
                # (voir app/Routes/RClientInfos.py: @router.get("/asking", ...)),
                # confirmé par test direct contre le serveur réel : POST renvoie
                # 405 Method Not Allowed, GET+params renvoie la réponse attendue.
                response = requests.get(url_certificate, params=params, headers=headers, timeout=60)
                status_code = response.status_code
                data = response.json()

                if status_code == 200:
                    if data and 'certy_ss' in data and data.get('certy_ss', '') is not None:
                        certy_ss = json.loads(data['certy_ss'])
                        # certy_ss = data['certy_ss']  # dictionnaire avec 'ssl_ca', 'ssl_cert', 'ssl_key'
                        # server_path = r"C:\Users\Charlorie\AppData\Local\.ecole_360\.certs"
                        server_path = os.path.join(get_local_data_dir(), ".ecole_360", ".certs")
                        os.makedirs(server_path, exist_ok=True)  # Crée le dossier s'il n'existe pas

                        # Dictionnaire pour mapper clé → nom de fichier
                        filename_map = {
                            "ssl_ca": "ca-cert.pem",
                            "ssl_cert": "client-cert.pem",
                            "ssl_key": "client-key.pem"
                        }

                        for key, b64_value in certy_ss.items():
                            filename = filename_map.get(key)
                            if filename and b64_value:
                                try:
                                    decoded = base64.b64decode(b64_value)
                                    file_path = os.path.join(server_path, filename)
                                    with open(file_path, "wb") as f:
                                        f.write(decoded)
                                        # f.write(b64_value.encode('utf-8'))
                                    print(f"[OK] {filename} enregistré dans {file_path}")
                                except Exception as e:
                                    print(f"[ERREUR] Impossible d’écrire {key} : {e}")
                            else:
                                print(f"[INFO] Clé {key} inconnue ou vide")
                    else:
                        print("[ERREUR] 'certy_ss' manquant dans la réponse")
                else:
                    print(f"[ERREUR] Réponse du serveur : {status_code} - {data}")
            except requests.RequestException as e:
                print(f"[EXCEPTION] Erreur réseau : {e}")
                return False

        
    
    def handle_etudiant_success(self, response_data):
        QMessageBox.information(self, "Succès", "Étudiant enregistré avec succès!")
        self.etudiant_page()
        self.set_table_refresh_data_student()
        self.overlay.finish_loading()
        # self.refresh_student_list()

    def handle_professeur_success(self, response_data):
        QMessageBox.information(self, "Succès", "Professeur enregistré avec succès!")
        # self.refresh_teacher_list()
        self.professeur_page()
        self.overlay.finish_loading()

    def handle_pdf(self, endpoint, method, data_bytes,types):   
        self.overlay.finish_loading() 
        self.api_handler_.verify_sanctum_token()
       
        if self.access_key != '22' or self.access_key_info != self.access_key and not endpoint.startswith('v1/print-recu'):
            QMessageBox.critical(
                self,
                "Avertissement",
                "La clé d'activation est invalide.\n"
                "Vous ne pouvez pas imprimer.\n"
                "Veuillez contacter l'administrateur ou l'équipe de développement."
            )
            return  # Empêche la suite du code si la clé est invalide
        if types == 'excel':
            self.handle_file_output(data_bytes,"xlsx")
        else:
            self.on_async_start()
            self.open_file_directly(data_bytes) 

    def closeEvent_(self, event):
        for key, thread in self.loaders.items():
            if thread.isRunning():
                thread.quit()
                thread.wait()
        event.accept() 

    def handle_file_output(self, file_data, file_type="pdf"):
        if not file_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée reçue.")
            return

        if file_type == "xlsx":  
            path, _ = QFileDialog.getSaveFileName(
                self, 
                "Enregistrer le fichier Excel", 
                "Palmares.xlsx", 
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if path:
                try: 
                    with open(path, 'wb') as f:
                        f.write(file_data)
                    
                    QMessageBox.information(self, "Succès", f"Fichier enregistré avec succès :\n{path}")
                     
                    # os.startfile(path)
                except Exception as e:
                    QMessageBox.critical(self, "Erreur", f"Impossible d'enregistrer le fichier : {str(e)}")
        
        else: 
            self.open_pdf_directly(file_data)

    def required_admin(self,endpoint, method, auth_message, response_data):
        print(endpoint, method, auth_message, response_data) 
        if endpoint == 'v1/post-payment-save':
            self.permissions_delete = ['Ajouter paiement','Modifier paiement']
        
        elif endpoint == 'v1/vente-delete':
            self.permissions_delete = ['Modifier paiement','Supprimer paiement']

        elif endpoint == 'v1/etudiant' and method == "POST":
            self.permissions_delete = ['Modifier etudiant','Ajouter etudiant']

        elif endpoint == 'v1/update-etudiant-classe' and method == "POST":
            self.permissions_delete = ['Modifier etudiant']
        
        elif endpoint.startswith("v1/delete-depense?id_depense"):
            self.permissions_delete = ['Supprimer paiement']

        elif endpoint == 'v1/delete-paiement':
            self.permissions_delete = ['Supprimer paiement']

        elif endpoint == 'v1/depense' and method == "POST":
            self.permissions_delete = ['Modifier paiement']
        

        elif endpoint == 'v1/etudiant-promus-to':
            self.permissions_delete = ['Modifier etudiant']

        elif endpoint == 'v1/active-teacher':
            self.permissions_delete = ['Modifier professeur']

        elif endpoint == 'v1/active-personnel':
            self.permissions_delete = ['Modifier personnel']

        elif endpoint == 'v1/change-password-teacher':
            self.permissions_delete = ['Modifier professeur']

        elif endpoint == 'v1/change-password-personnel':
            self.permissions_delete = ['Modifier personnel']


        self.request_access_for_delete()
        self.overlay.finish_loading()
        return
    
    def load_image_from_url_for_dash(self, url, label):
        self.image_thread = ImageLoaderThread(url, label.size())
        self.image_thread.finished.connect(lambda pixmap: self.set_image_on_label(pixmap, label))
        self.image_thread.error.connect(self.show_image_error)
        self.image_thread.start()

    def set_image_on_label(self, pixmap, label):
        label.setPixmap(pixmap)
        label.setStyleSheet("border-radius: 75px;")
        print("Image chargée avec succès ✅")

    def show_image_error(self, msg):
        print(f"Erreur de chargement d'image : {msg}")


    def fill_commbo_with_data(self,name_combo, default_value):
        index = name_combo.findData(default_value)
        if index >= 0:
            name_combo.setCurrentIndex(index)

    def make_request(self):
        # Créer un dialogue de progression 
        self.loading_dialog = LoadingDialog("Traitement en cours...", self)
        self.loading_dialog.show()
        QTimer.singleShot(0, self.start_processing)

    def start_processing(self):
        QTimer.singleShot(5, self.request_finished)  


    def request_finished(self):
        print()
        # self.loading_dialog.close()
        # Traiter les résultats ici

   
    def download_image(self, data_input, filename):
        """
        Gère l'image : 
        1. Si c'est du Base64, on le décode et l'enregistre.
        2. Si c'est une URL, on la télécharge.
        """
        local_path = self.get_path(os.path.join('assets', 'icons', filename))
        
        try:
            # --- OPTION BASE64 ---
            if "base64," in data_input or len(data_input) > 500: # Détection Base64
                if "," in data_input:
                    data_input = data_input.split(",")[1]
                
                image_data = base64.b64decode(data_input)
                with open(local_path, "wb") as file:
                    file.write(image_data)
                return local_path

            # --- OPTION URL (Votre code original) ---
            else:
                response = requests.get(data_input, stream=True)            
                response.raise_for_status()
                with open(local_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                return local_path

        except Exception as e:
            print(f"Erreur lors du traitement de l'image ({filename}) : {e}")
            return None

    # def show_modif_ip(self):
    #     is_checked = self.ui.show_frame_ip.isChecked() 
    #     self.ui.show_frame_ip.setText("Hide") if not is_checked
    #     self.ui.frame_240.setHidden(not is_checked)

    def show_modif_ip(self):
        is_checked = self.ui.show_frame_ip.isChecked() 
        
        # Correction de la syntaxe ternaire :
        new_text = "Hide" if is_checked else "Show"
        self.ui.show_frame_ip.setText(new_text)
        
        # Basculer la visibilité du frame
        self.fancy_modal_show(self.ui.frame_240)
        self.ui.frame_240.setHidden(not is_checked)
 
    def simulate_slow_dependency(self):
        # Log lorsqu'on commence à charger une dépendance
        logging.info("Démarrage de la dépendance lente...")
        
        # Simuler une tâche lente (par exemple, une attente de 3 secondes)
        QTimer.singleShot(100, self.dependency_done)

    def dependency_done(self):
        self.close_splash()
        logging.info("Dépendance terminée.")

    def get_mac_address_user(self):
        # import hmac
        import uuid
        """Récupère l'adresse MAC de la machine.

        uuid.getnode() seul n'est pas stable sur Mac/Linux : il renvoie l'adresse
        d'une interface réseau quelconque parmi celles actives au moment de l'appel
        (Wi-Fi, pont virtuel, hotspot...), qui peut changer d'un appel à l'autre
        (même bug déjà corrigé côté ecole_nginx, voir Helper/license_check.py
        get_host_mac()). On détecte donc une seule fois puis on réutilise la même
        valeur via un fichier local, pour ne pas déclencher de nouvelles demandes
        d'autorisation à chaque changement d'interface réseau détectée."""
        mac_cache_file = os.path.join(get_local_data_dir(), ".ecole_360", "machine_mac.txt")
        try:
            if os.path.exists(mac_cache_file):
                cached = Path(mac_cache_file).read_text().strip()
                if cached:
                    return cached, getpass.getuser()
        except OSError:
            pass

        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        try:
            os.makedirs(os.path.dirname(mac_cache_file), exist_ok=True)
            Path(mac_cache_file).write_text(mac)
        except OSError:
            pass

        # Nom de l'utilisateur
        username = getpass.getuser()

        return mac, username

    def get_mac_address(self):
        if sys.platform != "win32":
            # "getmac" est un utilitaire Windows uniquement ; uuid.getnode() (via
            # get_mac_address_user()) est déjà la méthode cross-platform utilisée
            # en repli ci-dessous, donc on l'appelle directement sur Mac/Linux pour
            # éviter un "command not found" systématique dans les logs.
            return self.get_mac_address_user()
        try:
            result = subprocess.check_output("getmac /fo csv /nh", shell=True).decode()
            mac = result.split(',')[0].strip().strip('"').replace('-', ':')
            return mac,self.get_mac_address_user()[1]
        except:
            return self.get_mac_address_user()



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
                print(f"🔁 Domaine {domain} mis à jour -> {ip}")
            else:
                new_lines.append(line)

        if not domain_found:
            # Ajouter une nouvelle entrée si le domaine n’existe pas
            new_lines.append(f"{ip}\t{domain}\n")
            print(f"✅ Domaine {domain} ajouté -> {ip}")

        # Sauvegarder les changements (privilèges requis)
        try:
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"💾 Modifications enregistrées dans {hosts_path}")
        except PermissionError:
            print("❌ Permission refusée. Exécutez ce script en administrateur/root.")
            if "--as-admin" not in sys.argv:
                self.run_as_admin()

 

    def verify_and_save_server_ip_in_connect(self): 
        ip_text = self.ui.input_change_ip.text().strip() 
        self.overlay.start_loading("Verifivation de l'adresse ip")
        # if getattr(self, "_ip_lock", False):
        #     self.overlay.finish_loading()
        #     print("⏳ Action déjà en cours, clic ignoré")
        #     return

        # self._ip_lock = True

        if ip_text and ip_text.strip() == self.ip_manager.get_server_ip(): 
            QMessageBox.critical(
                self, 
                "IP déjà configurée", 
                "Cette adresse IP est déjà enregistrée comme étant celle du serveur.\n\n"
                "Si vous souhaitez la modifier, saisissez la nouvelle adresse dans le champ."
            )
            self.overlay.finish_loading()
            return
        try:

            ip = ipaddress.ip_address(ip_text) 

            # Vérifier si l'IP est accessible sur le réseau
            if self.is_ip_reachable(ip_text): 
                self.ui.label_76.setText(f"  {ip_text} Verifivation est cours ... !")
                self.ui.label_76.setStyleSheet("color: orange;")
                self.ip_manager.delete_ip()
                self.ip_manager.save_server_ip(ip_text)

                self.add_or_update_host(ip=ip_text)
                

                mac, username = self.get_mac_address()

                request = {
                'client_mac':mac,
                'client_name':username,
                }
                ip = self.ui.input_change_ip.text().strip() 
                try: 
                    response = self.api_handler_.authorization_connect(mac=mac,username=username)
                except Exception as e:
                    print(f"{e} in save ip")
                    self.add_or_update_host(ip=ip_text)
                    response = self.api_handler_.authorization_connect(mac=mac,username=username)
                # if response and 'errors' in response:
                #     print(f"error detecter {response}")
                # print(response)

                # print(self.ip_manager.get_server_ip(), self.get_mac_address())
                # QApplication.processEvents()
            else:
                self.ui.label_76.setText(f"  {ip_text} est hors ligne !")
                self.ui.label_76.setStyleSheet("color: orange;")
                self.overlay.finish_loading()
        except ValueError as e:
            print(f'n\'est pas une adresse IP valide {e}')
            self.ui.label_76.setText(f"  {ip_text} n'est pas une adresse IP valide !")
            self.ui.label_76.setStyleSheet("color: red;")
            self.overlay.finish_loading()
        finally:
            self._ip_lock = False
        

    def verify_and_save_server_ip(self):
        ip_text = self.ui.server_ip.text().strip()
        try:
            ip = ipaddress.ip_address(ip_text)
            self.ui.label.setText(f"  {ip_text} est une adresse IP valide !")
            self.ui.label.setStyleSheet("color: green;")
            

            # Vérifier si l'IP est accessible sur le réseau
            if self.is_ip_reachable(ip_text):
                self.ui.label.setText(f"  {ip_text} est en ligne sur le réseau!")
                self.ui.label.setStyleSheet("color: green;")

                self.ip_manager.save_server_ip(ip_text)
                
                self.ui.main_with_shadow.setCurrentIndex(2)
            else:
                self.ui.label.setText(f"  {ip_text} est hors ligne !")
                self.ui.label.setStyleSheet("color: orange;")
        except ValueError:
            print('n\'est pas une adresse IP valide')
            self.ui.label.setText(f"  {ip_text} n'est pas une adresse IP valide !")
            self.ui.label.setStyleSheet("color: red;")

    def is_ip_reachable(self, ip):
        """Teste si une adresse IP répond au ping."""
        try:
            # Commande ping pour Windows (-n 1) ou Linux/Mac (-c 1)
            param = "-n" if sys.platform == "win32" else "-c"
            result = subprocess.run(["ping", param, "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # print(result)
            return result.returncode == 0  # 0 = succès, sinon échec
        except Exception:
            return False

    
    def load_image_from_url1(self, url, label):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            
            if pixmap.loadFromData(image_data.read()): 
                # pixmap = pixmap.scaled(label.size())
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                 
                label.setStyleSheet("border-radius: 75px;") 
            else:
                print("Erreur lors du chargement de l'image")

        except requests.exceptions.RequestException as e:
            print("Erreur de chargement d'image :", e)

    def load_image_from_url_for_dash1(self, url, label):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Vérifie si la requête a réussi
  
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            
            if pixmap.loadFromData(image_data.read()): 
                # pixmap = pixmap.scaled(label.size())
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                 
                label.setStyleSheet("border-radius: 75px;")
                # self.ui.widget_logo.setAlignment(Qt.AlignCenter)
                # self.ui.verticalLayout_11.setAlignment(Qt.AlignCenter)
                print("Image chargée avec succès !")
            else:
                print("Erreur lors du chargement de l'image")

        except requests.exceptions.RequestException as e:
            print("Erreur de chargement d'image :", e)

    def _setup_abonnement_page(self):
        """Onglet Abonnement (licence) : page + bouton de navigation construits à
        l'exécution plutôt que dans Views/main_view.py (fichier généré par Qt
        Designer — modifié à la main, ces changements seraient perdus à la
        prochaine régénération depuis le .ui)."""
        self.abonnement_data = None

        self.ui.btn_left_abonnement = QPushButton("Abonnement", self.ui.frame_6)
        self.ui.btn_left_abonnement.setObjectName("btn_left_abonnement")
        self.ui.btn_left_abonnement.setMinimumSize(QSize(180, 34))
        self.ui.btn_left_abonnement.setFont(self.ui.btn_left_admin.font())
        self.ui.btn_left_abonnement.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ui.btn_left_abonnement.setCheckable(True)
        self.ui.btn_left_abonnement.setAutoExclusive(True)
        self.ui.btn_left_abonnement.setFlat(True)
        self.ui.btn_left_abonnement.setStyleSheet(
            "QPushButton{color:#9ca3af;text-align:left;padding:2px 5px;padding-left:5px;}"
            "QPushButton:hover{background-color:#1f2937;padding:5px;padding-left:8px;color:#fff;}"
            "QPushButton:checked{background-color:#1f2937;color:#fff;padding:5px;padding-left:8px;"
            "font-weight:bold;border-top-left-radius:5px;border-bottom-left-radius:5px;}"
        )
        self.ui.verticalLayout_9.addWidget(self.ui.btn_left_abonnement)

        page = QWidget()
        page.setObjectName("abonnement_page")
        layout = QVBoxLayout(page)

        title = QLabel("Abonnement")
        title.setStyleSheet("font-size:16pt; font-weight:bold;")
        layout.addWidget(title)

        statut_row = QHBoxLayout()
        self.label_abonnement_statut = QLabel("Statut : -")
        self.label_abonnement_statut.setStyleSheet("font-size:11pt;")
        statut_row.addWidget(self.label_abonnement_statut)
        statut_row.addStretch()
        self.btn_abonnement_renouveler = QPushButton("Renouveler")
        self.btn_abonnement_renouveler.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_abonnement_renouveler.setStyleSheet(
            "QPushButton{background-color:#f59e0b;color:#fff;font-weight:bold;"
            "padding:5px 14px;border-radius:5px;}"
            "QPushButton:hover{background-color:#d97706;}"
        )
        # TEMPORAIRE — pointé sur le site infini-software local (npm run dev,
        # port Vite par défaut) pour tester le flux de renouvellement de bout
        # en bout. Remettre "https://www.infini-software.cloud" avant toute
        # mise en production.
        self.btn_abonnement_renouveler.clicked.connect(self._ouvrir_renouvellement)
        self.btn_abonnement_renouveler.setVisible(False)
        statut_row.addWidget(self.btn_abonnement_renouveler)
        layout.addLayout(statut_row)

        self.label_abonnement_cle = QLabel("Clé actuelle : -")
        self.label_abonnement_expiration = QLabel("Expire le : -")
        self.label_abonnement_jours = QLabel("Jours restants : -")
        for lbl in (self.label_abonnement_cle, self.label_abonnement_expiration, self.label_abonnement_jours):
            lbl.setStyleSheet("font-size:11pt;")
            layout.addWidget(lbl)

        history_title = QLabel("Historique des activations")
        history_title.setStyleSheet("font-size:13pt; font-weight:bold; margin-top:12px;")
        layout.addWidget(history_title)

        history_scroll = QScrollArea()
        history_scroll.setWidgetResizable(True)
        history_scroll.setFrameShape(QFrame.Shape.NoFrame)

        history_container = QWidget()
        self.layout_abonnement_historique = QVBoxLayout(history_container)
        self.layout_abonnement_historique.setSpacing(10)
        self.layout_abonnement_historique.addStretch()
        history_scroll.setWidget(history_container)
        layout.addWidget(history_scroll)

        self.ui.abonnement_page = page
        self.ui.stackedWidget.addWidget(self.ui.abonnement_page)

    def _ouvrir_renouvellement(self):
        # Le mac du SERVEUR (renvoyé par GET v1/abonnement, voir
        # show_data_in_abonnement), pas celui de ce poste client — plusieurs
        # postes peuvent se connecter au même serveur, seul le mac du serveur
        # est enregistré chez infini-software.
        mac = (self.abonnement_data or {}).get('mac')
        if not mac:
            QMessageBox.warning(self, "Renouvellement", "Adresse MAC du serveur introuvable. Réessayez après actualisation de la page Abonnement.")
            return
        QDesktopServices.openUrl(QUrl(f"{INFINI_API_BASE_URL}/renouveler?mac={quote(mac)}"))

    def abonnement_page(self):
        self.overlay.start_loading("Chargement des données d'abonnement")
        self.api_handler_.get_abonnement()
        self.ui.stackedWidget.setCurrentWidget(self.ui.abonnement_page)
        self.fade_in_page(self.ui.abonnement_page)

    def show_data_in_abonnement(self):
        data = self.abonnement_data or {}
        actif = data.get("actif")
        self.label_abonnement_statut.setText(f"Statut : {'Actif' if actif else 'Expiré/Invalide'}")
        self.label_abonnement_statut.setStyleSheet(
            f"font-size:11pt; font-weight:bold; color: {'#16a34a' if actif else '#dc2626'};"
        )
        jours_restants = data.get('jours_restants')
        self.btn_abonnement_renouveler.setVisible(jours_restants is not None and jours_restants <= 15)

        self.label_abonnement_cle.setText(f"Clé actuelle : {data.get('cle_actuelle', '-')}")
        self.label_abonnement_expiration.setText(f"Expire le : {data.get('date_expiration', '-')}")
        self.label_abonnement_jours.setText(f"Jours restants : {jours_restants if jours_restants is not None else '-'}")

        layout = self.layout_abonnement_historique
        while layout.count() > 1:
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        historique = data.get('historique', [])
        for entry in historique:
            date_expiration = entry.get('date_expiration')
            entry_actif = False
            if date_expiration:
                try:
                    entry_actif = datetime.strptime(date_expiration, "%Y-%m-%d").date() >= datetime.now().date()
                except ValueError:
                    pass

            card = QFrame()
            card.setStyleSheet(
                "QFrame{background-color:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;}"
            )
            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(15, 12, 15, 12)

            date_activation = entry.get('date_activation')
            activation_label = QLabel(f"Activé le : {date_activation or '-'}")
            activation_label.setStyleSheet("font-size:10.5pt;")
            card_layout.addWidget(activation_label)

            expiration_label = QLabel(f"Expire le : {date_expiration or '-'}")
            expiration_label.setStyleSheet("font-size:10.5pt;")
            card_layout.addWidget(expiration_label)

            card_layout.addStretch()

            statut_label = QLabel('Actif' if entry_actif else 'Expiré')
            statut_label.setStyleSheet(
                f"font-size:10.5pt; font-weight:bold; color: {'#16a34a' if entry_actif else '#dc2626'};"
            )
            card_layout.addWidget(statut_label)

            layout.insertWidget(layout.count() - 1, card)

        mac = data.get('mac')
        # Vérifié à chaque ouverture de l'onglet (pas seulement en fin de
        # plan) : un renouvellement anticipé doit être appliqué localement
        # dès la prochaine visite, sans attendre que le plan approche de
        # l'expiration.
        if mac:
            self._verifier_nouvelle_cle(mac, data.get('cle_actuelle'))

    def _verifier_nouvelle_cle(self, mac, cle_actuelle):
        self._licence_sync_thread = QThread()
        self._licence_sync_worker = LicenceSyncWorker(mac, cle_actuelle)
        self._licence_sync_worker.moveToThread(self._licence_sync_thread)
        self._licence_sync_thread.started.connect(self._licence_sync_worker.run)
        self._licence_sync_worker.nouvelle_cle_disponible.connect(self._appliquer_nouvelle_cle)
        self._licence_sync_thread.finished.connect(self._licence_sync_thread.deleteLater)
        self._licence_sync_thread.start()

    def _appliquer_nouvelle_cle(self, new_key, expiration_date, days_valid=None):
        # self.api_handler (ApiHandler brut) n'est utilisé nulle part ailleurs
        # dans ce fichier et n'a pas la même configuration (IP/token) que
        # self.api_handler_ (AsyncDataHandler), utilisé par tous les autres
        # appels authentifiés (cf. get_abonnement(), authorization_connect()...).
        self.api_handler_._send_request(
            "v1/licence/appliquer",
            method="POST",
            data={"new_key": new_key, "expiration_date": expiration_date, "days_valid": days_valid},
        )

    def show_image_logo_on_app(self, label, path):
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        label.setPixmap(pixmap)            
        label.setStyleSheet("border-radius: 75px;")

    def restart_disconnect_timer(self):
        self.disconnect_timer.start(1000000)

    def connect_buttons(self):       
        self.ui.main_with_shadow.setCurrentIndex(4)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.btn_left_deconnexion.clicked.connect(self.deconnexion)
        try:
            self.auto_refresh_timer.stop()
        except:
            pass
        roles_boutons = {
            'admin': [
                'btn_left_home', 'btn_left_admin', 'btn_left_etudiant', 'btn_left_paiement',
                'btn_left_prof', 'btn_left_cours', 'btn_left_promus', 'btn_left_rapport',
                'btn_left_vente', 'btn_left_profile', 'btn_settings', 'btn_actualiser','btn_left_notes','btn_log',
                'btn_left_abonnement'
            ],

            'teacher': ['btn_left_notes','btn_actualiser'],

            'Caissier': ['btn_left_paiement', 'btn_left_vente','btn_left_rapport', 'btn_left_etudiant','btn_actualiser'],

            'Responsable financier': ['btn_left_paiement', 'btn_left_vente','btn_left_rapport', 'btn_left_etudiant','btn_actualiser'],

            'Responsable des admissions': ['btn_left_etudiant','btn_actualiser'],

            'Responsable pédagogique': ['btn_left_rapport','btn_left_home','btn_left_cours', 'btn_left_etudiant', 'btn_settings','btn_left_notes','btn_actualiser','btn_left_promus'],

            'Comptable': ['btn_left_vente','btn_left_rapport','btn_left_home', 'btn_left_etudiant', 'btn_settings', 'btn_left_paiement','btn_actualiser']
        }  

        btn_left = ['btn_left_home', 'btn_left_admin', 'btn_left_etudiant','btn_left_paiement','btn_left_prof','btn_left_cours','btn_left_promus','btn_left_vente','btn_left_rapport','btn_left_profile','btn_left_notes','btn_settings','btn_actualiser','btn_log','btn_left_abonnement']

        button_callbacks = {
            'btn_left_home': self.dash_page,
            'btn_left_admin': self.admin_page,
            'btn_left_etudiant': self.etudiant_page,
            'btn_left_paiement': self.paiement_page,
            'btn_left_prof': self.professeur_page,
            'btn_left_cours': self.cours_page,
            'btn_left_notes': self.notes_page,
            'btn_settings': self.settings_page,
            'btn_actualiser': self.actualiser_page,
            'btn_left_promus': self.promus_page,
            'btn_left_rapport': self.rapport_page,
            'btn_left_vente': self.vente_page,
            'btn_left_profile': self.profile,
            'btn_log': self.logs,
            'btn_left_abonnement': self.abonnement_page,
        }
        

        self.api_handler_.config_donnees()
        self.api_handler_.annee_academique()
        self.api_handler_.classes_show_check()
        self.api_handler_.teacher_combo()
        self.api_handler_.cours_combo()
        self.api_handler_.niveau_index()
        self.api_handler_.roles()
        self.api_handler_.get_all_faculte()
        self.api_handler_.permissions()



        for btn_name in btn_left:
            btn = getattr(self.ui, btn_name)
            if any(role in self.user_roles for role in roles_boutons if btn_name in roles_boutons[role]):
                btn.setEnabled(True)
                self.ui.frame_350.setHidden(False)
                # self.ui.frame_408.setHidden(False)
                btn.clicked.connect(button_callbacks[btn_name])
            else:
                # self.ui.frame_408.setHidden(True)
                self.ui.frame_350.setHidden(True)
                btn.setEnabled(False)


    def se_connecter(self):        
        self.ui.user_id_for_change_password.setHidden(True)
        self.ui.password_for_reset.setText("")
        self.ui.confirm_password.setText("")
        self.ui.user_id_for_change_password.setText("")
        self.ui.error_message.setText("")

        email = self.ui.email_2.text()
        password = self.ui.password_2.text()
        self.ui.btn_connexion.setDisabled(True)

        if not email or not password:
            self.ui.error_message.setText("Veuillez remplir tous les champs.")
            self.ui.btn_connexion.setDisabled(False)
            self.overlay.finish_loading()
            return

        # Préparation des données pour la requête
        login_data = {
            "email": email,
            "password": password,
            "device_name": "qt-desktop-app"  # Nécessaire pour Laravel Sanctum
        }


        self.overlay.start_loading("Connexion...")
        self.api_handler_.login(email=email, password=password)



    def handle_login_response(self, response):
        """Gère la réponse du serveur après tentative de connexion"""  
        try:
            if not response:
                QMessageBox.critical(self, "Erreur", "Réponse vide du serveur")
                self.ui.btn_connexion.setDisabled(False)
                self.overlay.finish_loading()
                return

            # Vérification de l'autorisation MAC

            self.api_handler_.verify_authorization_token(self.get_mac_address()[0])
  
            if not response.get("user"):
                self.overlay.finish_loading()
                QMessageBox.critical(self, "Avertissement", "Les informations de connexion sont incorrectes !")
                self.ui.btn_connexion.setDisabled(False)
                self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                self.fade_in_page(self.ui.connexion_page)
                return

            user = response["user"]
            if user.get("status", "") != '1':
                self.overlay.finish_loading()
                QMessageBox.critical(self, "Avertissement", "Votre compte n'est pas actif !")
                self.ui.btn_connexion.setDisabled(False)
                self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                self.fade_in_page(self.ui.connexion_page)
                return

            user_type = user.get("userable_type", "")

            if not user_type.endswith("\\Personnel") and not user_type.endswith("\\Professeur"):
                self.overlay.finish_loading()
                QMessageBox.critical(self, "Avertissement", "Vous compte n'êtes pas autorisé à vous connecter au serveur.")
                self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
                self.fade_in_page(self.ui.connexion_page)
                self.ui.btn_connexion.setDisabled(False)
                return

            # Vérification du mot de passe changé
            if not user.get("password_changed_at"):
                self.ui.user_id_for_change_password.setText(user.get("id", ""))
                self.overlay.finish_loading()
                self.ui.main_with_shadow.setCurrentWidget(self.ui.reset_password)
                self.fade_in_page(self.ui.reset_password)
                # self.fancy_modal_show(self.ui.connexion_4)
                # self.ui.label_info_reset.setText("C'est votre première connexion. Veuillez changer votre mot de passe.")
                self.ui.btn_connexion.setDisabled(False)
                return
            
            if user.get('heart_auto'):
                heart_auto = user.get('heart_auto')['descript']
                last_key = heart_auto.split('--')[1]
                self.access_key = last_key
                self.access_key_info  = self.get_client_autorisation(user.get('client_infos'))
                

            # Gestion du logo
            if self.config_data and self.config_data['data'] and 'data' in self.config_data:
                image_url = self.config_data['data'].get('logo_image_base64')
                if image_url and not os.path.exists(self.icon_path_logo):
                    self.download_image(image_url, self.icon_path_logo)
                if os.path.exists(self.icon_path_logo):
                    self.setWindowIcon(QIcon(self.icon_path_logo))
                    self.show_image_logo_on_app(self.ui.logo_2, self.icon_path_logo)

            # Sauvegarde des informations utilisateur
            self.token_manager.save_user_email(user.get("email", ""))
            self.token_manager.save_token(response.get("token", ""))
            self.user_connect.setText(user.get('id'))
            self.user_info = response.get("user",[]) 
            self.user_roles = response.get("roles", [])
            self.user_permissions = response.get("permissions", [])
            self.info_user_response_data = response

 
            # self.api_handler_.all_student_() 
            self.dash_page()
            
            self.connect_buttons()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Une erreur inattendue est survenue: {str(e)}")
        finally:
            self.ui.btn_connexion.setDisabled(False)
        self.overlay.finish_loading()

    def handle_login_error(self, endpoint, message):
        """Gère les erreurs de connexion"""
        self.ui.password_2.setText('')
        if 'email' in message:
            error_message = f"{message['email']}"
        else:
            error_message = f"{message}"
        
        # Journalisation de l'erreur
        print(f"Erreur API __ ({endpoint}): {message}")
        
        # Affichage à l'utilisateur
        if 'errors' in message:
            error_message = f"{message['errors']}"
        self.ui.error_message.setText(error_message) 
        self.ui.btn_connexion.setDisabled(False)
        
        # Message supplémentaire pour certaines erreurs
        if "credentials" in str(message).lower():
            QMessageBox.warning(self, "Erreur", "Email ou mot de passe incorrect")
        elif "timed out" in str(endpoint).lower():
            QMessageBox.warning(self, "Erreur", "Le serveur ne répond pas. Vérifiez votre connexion.")
        self.overlay.finish_loading()



    def reset_password_personnel(self):        
        password = self.ui.reset_password_perso.text()
        password_confirm = self.ui.confirm_reset_password_perso.text()
        personnel_id = self.id_admin_for_update.text()
        self.ui.reinitialiser_mot_de_passe.setDisabled(True)
        if not password or not password_confirm:
            self.ui.label_128.setText("Veuillez remplir tous les champs.")
            self.ui.reinitialiser_mot_de_passe.setDisabled(False)
            return
  
        response = self.api_handler_.reset_password_perso(password, password_confirm,personnel_id)

        
    def reset_password_professeur(self):
        password = self.ui.reset_password_prof.text()
        password_confirm = self.ui.confirm_reset_password_prof.text()
        professeur_id = self.id_professeur_for_update.text()

        self.ui.btn_reset_password_prof.setDisabled(True)
        if not password or not password_confirm:
            self.ui.label_128.setText("Veuillez remplir tous les champs.")
            self.ui.btn_reset_password_prof.setDisabled(False)
            return

          
        response = self.api_handler_.reset_password_prof(password, password_confirm,professeur_id)


    def reset_password(self):
        password = self.ui.password_for_reset.text()
        password_confirm = self.ui.confirm_password.text()
        user_id = self.ui.user_id_for_change_password.text()

        if not password or not password_confirm:
            self.ui.error_message_2.setText("Veuillez remplir tous les champs.")
            return
        

        response = self.api_handler_.reset_password_and_connect(password, password_confirm,user_id)
        



    def deconnexion(self):
        self.overlay.start_loading("Déconnexion")
        self.disconnect_timer.stop()
        self.ui.password_2.setText('')
        self.ui.email_2.setText('')

        self.api_handler_.logout()

        self.token_manager.delete_token()

        self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
        self.fancy_modal_show(self.ui.connexion_page)
        self.resize(750, 500)

        if os.path.exists(self.icon_path_logo):
            self.setWindowIcon(QIcon(self.icon_path_logo))
            self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo)
        else:
            self.show_image_logo_on_app(self.ui.logo,self.icon_path_logo_lock)

        self.data_combo_cours.clear()
        self.niveaux.clear()
        self.annee_acades.clear()
        self.teacherList.clear()
        self.fetch_data_roles.clear()
        self.fetch_data_permissions.clear()
        self.classes_combo.clear()
        self.all_students_data.clear()
        self.all_personnels_data.clear()
        self.all_paiement_data.clear()
        self.all_notes_data.clear()  
        self.all_faculte.clear()
        self.all_frais_divers.clear()  
        self.user_connect.setText('')
        self.user_info.clear()
        self.info_user_response_data.clear()
        self.user_roles.clear()
        self.user_permissions.clear()

        if os.path.exists(self.icon_path_logo):
            self.show_image_logo_on_app(self.ui.logo_2,self.icon_path_logo)

        # if response:                
        #     self.ui.email_2.setText('')
        #     self.ui.password_2.setText('')
        #     self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
        #     self.resize(730, 450)
        self.overlay.finish_loading()

    def vente_page(self):
        # print(self.user_connect.text())
        # self.restart_disconnect_timer()
        self.ui.loans_id.setHidden(True)
        
        self.order_id = QLineEdit()
        self.order_id.setText("")
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        self.ui.vente_status.setHidden(True)
        # self.commande = []
        self.overlay.start_loading()
        self.go_to_vente_page(self.current_page_vente)
        self.commande.clear()  
        self.ui.table_show_order.setRowCount(0)
        self.ui.label_commande_number.setText("0")
        # self.set_table_refresh_data_vente()

        self.ui.frame_295.setHidden(True)
        
        self.ui.stackedWidget.setCurrentWidget(self.ui.vente_page)
        self.ui.tabWidget_2.setCurrentWidget(self.ui.vente_index)
        self.fade_in_page(self.ui.vente_index) 
        self.ui.delete_vente.clicked.connect(self.delete_vente)
        self.ui.delete_depense.clicked.connect(self.delete_depense)
        self.api_handler_.get_data_user_for_loans()

    def logs(self): 
        # self.restart_disconnect_timer()   
        # self.overlay.start_loading("Log")
        self.go_to_log_page(self.current_page_log)
        self.ui.action_log.setPlaceholderText("Action")
        self.ui.action_log_console.setPlaceholderText("Action")
        self.ui.action_log.clear()
        self.ui.action_log_console.clear()
        for key, label in self.actions.items():
            self.ui.action_log.addItem(label, key)
            self.ui.action_log_console.addItem(label, key)

        self.ui.model_log.setPlaceholderText('Model / Table')
        self.ui.model_log_console.setPlaceholderText('Model / Table')
        self.ui.model_log.clear()
        self.ui.model_log_console.clear()
        for table, model in self.models.items():
            self.ui.model_log.addItem(table, model)
            self.ui.model_log_console.addItem(table, model)
        self.ui.stackedWidget.setCurrentWidget(self.ui.log_page)
        self.ui.tabWidget_3.setCurrentWidget(self.ui.grafic_log)
        self.fade_in_page(self.ui.grafic_log)

    def call_action_log(self):
        self.overlay.start_loading(f"Log {self.ui.action_log.currentText()}")
        action = self.ui.action_log.currentData()
        model = self.ui.model_log.currentData()

        self.api_handler_.all_logs(search_term=self.ui.search_log.text(),action=action,model=model,page=self.current_page_log)

    def call_model_log(self):
        self.overlay.start_loading(f"Log {self.ui.model_log.currentText()}")
        action = self.ui.action_log.currentData()
        model = self.ui.model_log.currentData()

        self.api_handler_.all_logs(search_term=self.ui.search_log.text(),action=action,model=model,page=self.current_page_log)

    def logs_console(self):
        self.auto_refresh_timer.start()
        self.set_table_refresh_data_log_console()
        self.ui.tabWidget_3.setCurrentWidget(self.ui.console_log)
        self.fade_in_page(self.ui.console_log)

    def set_table_refresh_data_log_console(self):
        header = ("", " ", ' '," ", " ",' ')#, 'status')
        if self.is_data_updating:
            return

        # Marque la mise à jour comme en cours
        self.is_data_updating = True

        try:
            self.all_headers_table_labels(
            self.ui.console_log_table, header,  "#111", 28, 200, 150, 150, 300, 120, colors='#000',colors_="#06fa6c")
            self.ui.console_log_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)           
            if self.all_logs_data:
                self.current_page_log = self.all_logs_data.get("meta", {}).get("current_page", 1)
                self.total_pages_log = self.all_logs_data.get("meta", {}).get("last_page", 1)

                # self.ui.prev_log.setEnabled(self.current_page_log > 1)
                # self.ui.next_log.setEnabled(self.current_page_log < self.total_pages_log)

                # self.ui.prev_log.setStyleSheet("""
                #     QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                # """)

                # self.ui.next_log.setStyleSheet("""
                #     QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                # """)
    
                self.select_all_populate(self.all_logs_data.get('data',''), self.ui.console_log_table, self.on_row_clicked_log_,['id','user','authorization_id','action','model','date'])
        except:
          print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def log_grafic(self):
        self.auto_refresh_timer.stop()
        self.logs()

    def set_table_refresh_data_log(self):
        header = ("Id", "Utilisateur", 'Autorisation',"Action", "Model",'Date')#, 'status')
        if self.is_data_updating:
            return

        # Marque la mise à jour comme en cours
        self.is_data_updating = True

        try:
            self.all_headers_table_labels(
            self.ui.log_table, header,  "#e2e8f0", 32, 200, 150, 200, 250, 160)
            self.ui.log_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)           
            if self.all_logs_data:
                self.current_page_log = self.all_logs_data.get("meta", {}).get("current_page", 1)
                self.total_pages_log = self.all_logs_data.get("meta", {}).get("last_page", 1)

                self.ui.prev_log.setEnabled(self.current_page_log > 1)
                self.ui.next_log.setEnabled(self.current_page_log < self.total_pages_log)

                self.ui.prev_log.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_log.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)
    
                self.select_all_populate(self.all_logs_data.get('data',''), self.ui.log_table, self.on_row_clicked_log_,['id','user','authorization_id','action','model','date'])
        except:
          print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def go_to_log_page(self, page):
        self.overlay.start_loading("Log")
        self.current_page_log = page
        action = self.ui.action_log.currentData()
        model = self.ui.model_log.currentData()

        self.api_handler_.all_logs(search_term=self.ui.search_log.text(),action=action,model=model,page=page)

    def on_row_clicked_log_(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.log_table.item(row, 0)  # Colonne 0 = ID
        if id_item:
            self.api_handler_.logs_row_show(id_item.text()) 

    def tab_loans(self): 
        self.go_to_loans_page(self.current_page_loans)
        self.ui.tabWidget_2.setCurrentWidget(self.ui.loans_widget) 
        self.ui.tabWidget_4.setCurrentWidget(self.ui.tab_loans) 
        self.fancy_modal_show(self.ui.tab_loans)

    def bact_to_loans(self):
        self.tab_loans()
        

    def go_to_loans_page(self, page): 
        self.overlay.start_loading(f"Note page {page}") 
        self.current_page_loans = page 

        self.api_handler_.all_loans(self.ui.loans_search.text(), page)

    def loans_form(self): 
        self.set_table_refresh_data_loans()
        self.ui.tabWidget_4.setCurrentWidget(self.ui.tab_loans_form)
        self.fade_in_page(self.ui.tab_loans_form)

    def set_table_refresh_data_loans(self, page=1):
        header = ("Id", "Utilisateur", "Montant", 'Balance',
                  "Status", 'Date')
        try:
            self.all_headers_table_labels(
                self.ui.loans_table, header,  "#e2e8f0", 32, 200, 150, 150, 165, 200,c_header="#2180fc")
            self.ui.loans_table.setSelectionBehavior(
                QAbstractItemView.SelectRows) 
                 
            if self.all_loans_data:
                self.current_page_vente = self.all_loans_data.get("meta", {}).get("current_page", 1)
                self.total_pages_vente = self.all_loans_data.get("meta", {}).get("last_page", 1)

                self.ui.prev_vente.setEnabled(self.current_page_vente > 1)
                self.ui.next_vente.setEnabled(self.current_page_vente < self.total_pages_vente)

                self.ui.prev_vente.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_vente.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)
    
                self.select_all_populate(self.all_loans_data.get('data',''), self.ui.loans_table, self.on_row_clicked_loans_,['id','user','amount','remaining_balance','status','date'])
             

                # term_months
                # interest_rate
                # monthly_payment
 
        except:
          print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def on_row_clicked_loans_(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.loans_table.item(row, 0) 
        print(id_item)  
        if id_item: 
            self.ui.loans_id.setText(id_item.text())
            loans_line = next((item for item in self.all_loans_data['data'] if item['id'] == id_item.text()), None)
           
            if loans_line:
                self.ui.month_ter.setText(str(loans_line.get('monthly_payment','')))
                self.ui.inter_rate.setText(str(loans_line.get('interest_rate','0.0')))
                self.ui.tabWidget_4.setCurrentWidget(self.ui.tab_rembousement)
                self.fade_in_page(self.ui.tab_rembousement)
            


    def sauvegarder_loans(self):
        self.overlay.start_loading("Pret")
        data = {
        'user_id':self.ui.identifiant_user.currentData() if self.ui.identifiant_user else None,
        'amount':self.ui.amount.text() if self.ui.amount else None,
        'term_months':self.ui.term_months.text() if self.ui.term_months else None,
        'loans_status':self.ui.loans_status.currentText() if self.ui.loans_status else None,
        'monthly_payment':self.ui.monthly_payment.text() if self.ui.monthly_payment else None,
        # 'interest_rate':float(self.ui.interest_rate.text()) if self.ui.interest_rate else 0,
        'interest_rate': float(self.ui.interest_rate.text() or 0) if self.ui.interest_rate.text().strip() else 0.0,
        'approved_by':self.ui.approved_by.text() if self.ui.approved_by else None,
        'approved_at':self.ui.approved_at.text() if self.ui.approved_at else None,
        'disbursed_at':self.ui.disbursed_at.text() if self.ui.disbursed_at else None,
        # 'remaining_balance':float(self.ui.remaining_balance.text()) if self.ui.remaining_balance else 0,
        'created_at':self.ui.created_at.text() if self.ui.created_at else None,
        'updated_at':self.ui.updated_at.text() if self.ui.updated_at else None,
        }

        self.api_handler_.store_loans(data)

    def to_loans_repayments(self):
        self.overlay.start_loading("Remboursement")
        data = {
            'loans_id': self.ui.loans_id.text(),
            'paid_amount':self.ui.amount_to_pay.text()
        }
        self.api_handler_.store_loans_repayment(data)

    def load_students_into_combo(self):
        self.data_for_other_transac = True
        text = self.ui.combo_transact_identifiant.currentText()
        
        if len(text) < 2:
            return

        self.ui.combo_transact_identifiant.blockSignals(True)
        
        # On appelle l'API qui remplit apparemment la liste self.live_search_student
        self.api_handler_.student_live(text) 
        
        current_input = self.ui.combo_transact_identifiant.currentText()
        self.ui.combo_transact_identifiant.clear() 
        self.ui.combo_transact_identifiant.setEditText(current_input)
  
        if self.live_search_student: 
            for student in self.live_search_student['data']:
                # Si les éléments de la liste sont des dictionnaires :
                nom = student.get('nom', '')
                prenom = student.get('prenom', '')
                s_id = student.get('id', '')
                
                display_text = f"{nom} {prenom}" 
                self.ui.combo_transact_identifiant.addItem(display_text, s_id)
        else:
            self.ui.combo_transact_identifiant.addItem("Aucun résultat", None)

        # --- Configuration du Completer avec les noms corrects ---
        completer = self.ui.combo_transact_identifiant.completer()
        if completer:
            # Utilisation des noms importés directement ou via le module
            completer.setCompletionMode(QCompleter.PopupCompletion)
            completer.setFilterMode(Qt.MatchContains)
        time.sleep(2)
        self.ui.combo_transact_identifiant.showPopup()
        self.ui.combo_transact_identifiant.blockSignals(False)


    def autre_transaction(self): 
        self.data_for_other_transac = True
        self.ui.transac_id.setHidden(True)
        self.ui.edit_transact.setHidden(True)
        self.ui.delete_transact.setHidden(True)
        self.ui.save_transac.setHidden(False)
        self.ui.combo_transact_identifiant.clear()
        self.ui.combo_transact_description.clear()
        self.student_live_seach_input = QLineEdit()
        options = ["Initiale", "Badge perdu", "Relevé de notes", "Diplôme", "Autre"]
        self.ui.combo_transact_description.addItems(options)
        self.set_table_refresh_data_other_transac()

        self.go_to_other_transaction_page(self.current_page_transac)

        self.ui.tabWidget_2.setCurrentWidget(self.ui.transaction_page) 
        self.fancy_modal_show(self.ui.transaction_page)


    def set_table_refresh_data_other_transac(self, page=1):
        header = ("Id", "Utilisateur", "Descrition", 'Montant', 'Date')
        try:
            self.all_headers_table_labels(
                self.ui.table_transac, header,  "#e2e8f0", 32, 200, 300, 150, 165,c_header="#2180fc")
            self.ui.table_transac.setSelectionBehavior(
                QAbstractItemView.SelectRows) 
                 
            if self.all_other_transac_data:
                self.current_page_transac = self.all_other_transac_data.get("current_page", 1)
                self.total_pages_transac = self.all_other_transac_data.get("last_page", 1)

                self.ui.prev_transac.setEnabled(self.current_page_transac > 1)
                self.ui.next_transac.setEnabled(self.current_page_transac < self.total_pages_transac)

                self.ui.prev_transac.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_transac.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)
    
                self.select_all_populate(self.all_other_transac_data.get('data',{}), self.ui.table_transac, self.on_row_clicked_transac_,['id','utilisateur','description','montant','date'])
              
 
        except:
          print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def on_row_clicked_transac_(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_transac.item(row, 0) 
        self.ui.edit_transact.setHidden(False)
        self.ui.delete_transact.setHidden(False) 
        self.ui.save_transac.setHidden(True) 
        self.ui.combo_transact_identifiant.clear()
        if id_item:  
            transac_line = next((item for item in self.all_other_transac_data['data'] if item['id'] == id_item.text()), None)

            etudiant = transac_line.get("etudiant",None)
            self.ui.transac_id.setText(str(transac_line.get("id","")))
            self.ui.transac_descript.setText(str(transac_line.get("description_supplementaire","")))
            self.ui.transac_amount.setText(str(transac_line.get("montant",0.0)))
            self.fill_combo_box(self.ui.combo_transact_description, str(transac_line.get("description","")))
            if etudiant:
                nom = etudiant.get("nom","")
                prenom = etudiant.get("prenom","")
                s_id = etudiant.get("id","")                
                display_text = f"{nom} {prenom}" 
                self.ui.combo_transact_identifiant.addItem(display_text, s_id)
            print(transac_line)
     


    def sauvegarder_other_transaction(self):
        self.overlay.start_loading("Autres transaction")
        data = {
        'id':self.ui.transac_id.text() if self.ui.transac_id else None,
        'description_supplementaire':self.ui.transac_descript.text() if self.ui.transac_descript else None,
        'montant':self.ui.transac_amount.text() if self.ui.transac_amount else None,
        'identifiant':self.ui.combo_transact_identifiant.currentData() if self.ui.combo_transact_identifiant else None,
        'description':self.ui.combo_transact_description.currentText() if self.ui.transac_amount else None,

        }
        self.api_handler_.store_other_transaction(data)

    def edit_other_transaction(self):
        # delete_transact
        self.overlay.start_loading("Autres transaction")
        data = {
        'id':self.ui.transac_id.text() if self.ui.transac_id else None,
        'description_supplementaire':self.ui.transac_descript.text() if self.ui.transac_descript else None,
        'montant':self.ui.transac_amount.text() if self.ui.transac_amount else None,
        'identifiant':self.ui.combo_transact_identifiant.currentData() if self.ui.combo_transact_identifiant else None,
        'description':self.ui.combo_transact_description.currentText() if self.ui.transac_amount else None,

        }
        self.api_handler_.edit_other_transaction(self.ui.transac_id.text(),data)

    def go_to_other_transaction_page(self, page):
        self.overlay.start_loading("Autre transaction")
        self.current_page_transac = page

        self.api_handler_.all_other_transaction(self.ui.search_transac.text(), page)


    def depense_page(self):        
        self.overlay.start_loading("Dépense")
        self.ui.id_depense.setHidden(True)
        self.ui.delete_depense.setHidden(True)
        self.ui.enregistrer_depense.setText("Enregistrer")
 
        self.go_to_depense_page(self.current_page_depense)
        self.ui.id_depense.setText('')
        self.ui.description_depense.setText('')
        self.ui.prix_depense.setText('') 
        self.ui.tabWidget_2.setCurrentWidget(self.ui.depense)
        self.fancy_modal_show(self.ui.depense)


    def restart_timer_vente(self):
        self.search_timer_sell.start(300)

    def set_table_refresh_data_vente(self, page=1):
        header = ("Id", "ID", "Nom de l'élève", "Quantité", 
                  "Prix Total", "Utilisateur",'Date')#, 'status')
        if self.is_data_updating:
            return

        # Marque la mise à jour comme en cours
        self.is_data_updating = True

        try:
            self.all_headers_table_labels(
            self.ui.table_vente, header,  "#e2e8f0", 32, 120, 200, 120, 105, 180, 180)
            self.ui.table_vente.setSelectionBehavior(
            QAbstractItemView.SelectRows)         
          
            if self.all_ventes_data:
                self.current_page_vente = self.all_ventes_data.get("meta", {}).get("current_page", 1)
                self.total_pages_vente = self.all_ventes_data.get("meta", {}).get("last_page", 1)

                self.ui.prev_vente.setEnabled(self.current_page_vente > 1)
                self.ui.next_vente.setEnabled(self.current_page_vente < self.total_pages_vente)

                self.ui.prev_vente.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_vente.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)
    
                self.select_all_populate(self.all_ventes_data.get('data',''), self.ui.table_vente, self.on_row_clicked_vente_,['id','order_itemId','nom','quantite','total','utilisateur','date'])
        except:
          print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def go_to_vente_page(self, page):
        self.overlay.start_loading("Vente")
        self.current_page_vente = page

        self.api_handler_.all_ventes(self.ui.search_vente.text(), page)

    def go_to_depense_page(self, page):
        self.overlay.start_loading("Dépense")
        self.current_page_depense = page

        self.api_handler_.all_depenses(self.ui.search_depense.text(), page)

    def next_vente(self):
        if self.current_page_vente < self.total_pages_vente:
            self.go_to_vente_page(self.current_page_vente + 1)

    def prev_vente(self):
        if self.current_page_vente > 1:
            self.go_to_vente_page(self.current_page_vente - 1)

    def next_depense(self):
        if self.current_page_depense < self.total_pages_depense:
            self.go_to_depense_page(self.current_page_depense + 1)

    def prev_depense(self):
        if self.current_page_depense > 1:
            self.go_to_depense_page(self.current_page_depense - 1)


    def restart_timer_depense(self):
        self.search_timer_depense.start(300)

    def set_table_refresh_data_depense(self, page=1):
        header = ("Id", "description", "Prix", 
                  "Utilisateur", 'Date')
 
        self.all_headers_table_labels(
            self.ui.table_depense, header,  "#e2e8f0", 32, 300, 200, 200, 165)
        self.ui.table_depense.setSelectionBehavior(
            QAbstractItemView.SelectRows)         
          
        if self.all_depense_data:        

            self.current_page_depense = self.all_depense_data.get("meta", {}).get("current_page", 1)
            self.total_pages_depense = self.all_depense_data.get("meta", {}).get("last_page", 1)

            self.ui.prev_depense.setEnabled(self.current_page_depense > 1)
            self.ui.next_depense.setEnabled(self.current_page_depense < self.total_pages_depense)

            self.ui.prev_depense.setStyleSheet("""
                QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_depense.setStyleSheet("""
                QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)


            self.select_all_populate(self.all_depense_data.get('data',''), self.ui.table_depense, self.on_row_clicked_deppense_,['id','description','prix', 'user_name','date'])


    def on_row_clicked_vente_(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_vente.item(row, 0)  # Colonne 0 = ID
        self.row=None
        if id_item: 
            self.commande.clear() 
            self.ui.category.clear()
            self.ui.category.addItems(['Livres','Tissus','Fournitures', 'Arriéré','Inscription'])
            self.ui.vente_status.clear()
            self.ui.vente_status.addItems(['0','1','2'])
            self.ui.vente_status.setCurrentIndex(1)

            show_vente = self.api_handler_.vente_show(id_item.text())



    def on_row_clicked_deppense_(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_depense.item(row, 0)
        description_item = self.ui.table_depense.item(row, 1)
        prix_item = self.ui.table_depense.item(row, 2)
        if id_item: 
            # self.commande.clear()
            # show_vente = self.fetch_data_.vente_show(id_item.text())
            self.ui.enregistrer_depense.setText("Modifier")
            self.ui.delete_depense.setHidden(False)
            self.ui.id_depense.setText(id_item.text())
            self.ui.description_depense.setText(description_item.text())
            self.ui.prix_depense.setText(prix_item.text())

    def enregistrer_depense(self):
        self.overlay.start_loading("Enregistrement de dépense") 
        if not self.ui.description_depense or not self.ui.prix_depense:
            QMessageBox.warning(None, "Depense vide", "Aucune depense à enregistrer.")
            return

        description_depense = self.ui.description_depense.text()
        prix_depense = self.ui.prix_depense.text()
        id_depense = self.ui.id_depense.text()

        response = self.api_handler_.enregistrer_depense(id=id_depense, description_depense=description_depense, prix_depense=prix_depense)


    def delete_depense(self):
        self.overlay.start_loading(f'Suppression de depense')
        try: 
            id_depense = self.ui.id_depense.text()

            response = self.api_handler_.delete_depense(id_depense)
            # print(response)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.overlay.finish_loading()
            QMessageBox.critical(None, "Erreur", f"Une erreur est survenue lors de la suppression : {e}")



    def add_vente(self):
        self.commande.clear() 
        
        # self.order_id = QLineEdit()
        # self.order_id = QLineEdit()
        # self.order_id.setText("")
        self.ui.label_total_commande.setText('0')
        # self.row = None
        self.ui.vente_status.setHidden(True)
        self.ui.ajouter_vente.setText("Ajouter")
        self.ui.table_show_order.setRowCount(0)
        self.ui.search_student_for_sell.setFocus()
        self.set_table_refresh_data_for_commande()
        self.clear_fields(self.ui.materiel_name,self.ui.category,self.ui.unit_prise,self.ui.quantity,self.ui.total_prise,self.ui.student_vente_id,self.ui.vente_edit_id, self.ui.search_student_for_sell)
        
       
        # self.order_id = QLineEdit()
        self.ui.frame_301.setHidden(True)
        
        vente_status = {'0':'En attente', '2':'Retourner', '1':'Livré'}
        # for status in vente_status:
        self.ui.vente_status.clear()
        self.ui.vente_status.addItems(['0','1','2'])
        self.ui.vente_status.setCurrentIndex(1)

        self.ui.category.clear()
        self.ui.category.addItems(['Livres','Tissus','Fournitures', 'Arriéré','Inscription'])
        
        # self.ui.search_student_for_sell.textChanged.connect(self.self.set_table_refresh_data_for_sell())
        # self.ui.ajouter_vente.clicked.connect(self.add_commande)
        # self.ui.passer_la_commande.clicked.connect(self.commander)

        self.ui.unit_prise.textChanged.connect(self.total_prise)
        self.ui.quantity.textChanged.connect(self.total_prise)
        QTimer.singleShot(5, self.overlay.finish_loading)
        self.ui.tabWidget_2.setCurrentWidget(self.ui.add_vente)
        self.fancy_modal_show(self.ui.add_vente)

 

    def total_prise(self):
        unit_text = self.ui.unit_prise.text().strip()
        qty_text = self.ui.quantity.text().strip()

        if not unit_text or not qty_text:
            return 

        try:
            unit_prise = float(unit_text)
            quantity = float(qty_text)

            if unit_prise > 0 and quantity > 0:
                total = unit_prise * quantity
                self.ui.total_prise.setText(str(total))
        except ValueError:
            QMessageBox.warning(None, "Erreur", "Veuillez entrer des valeurs numériques valides.")


    def add_commande(self):
        try:
            nom = self.ui.materiel_name.text().strip()
            category = self.ui.category.currentText().strip()
            status_v = self.ui.vente_status.currentText().strip()
            unit_price = float(self.ui.unit_prise.text())
            quantity = float(self.ui.quantity.text())

            if not nom or not category or unit_price <= 0 or quantity <= 0:
                raise ValueError

            total = unit_price * quantity

            ligne = {
                'id': self.order_id.text(),
                'nom': nom,
                'category': category,
                'prix': unit_price,
                'quantite': quantity,
                'total': float(total),
                'status': 1 #status_v,
            }
            print(self.row,len(self.commande))
            # if self.row is not None and self.row >= 0:
            if self.row is not None and self.row < len(self.commande):
                self.commande[self.row] = ligne
            else:
                self.commande.append(ligne)

            # if self.row < len(self.commande):
            #     self.commande[self.row] = ligne  # Update existing line
            # else:
            #     self.commande.append(ligne)      # Add new line

            self.ui.ajouter_vente.setText("Ajouter")

            self.row = None

            total_general = sum(float(l['total']) for l in self.commande)
            self.ui.label_total_commande.setText(f"{total_general} GDES")
            self.ui.label_commande_number.setText(str(len(self.commande)))
            self.set_table_refresh_data_for_commande()
            self.clear_fields(self.ui.materiel_name,self.ui.category,self.ui.unit_prise,self.ui.quantity,self.ui.total_prise)

        except ValueError:
            QMessageBox.critical(None, "Erreur", "Veuillez remplir tous les champs correctement.")


    def delete_vente(self):
        self.overlay.start_loading(f'Suppression de la ligne {self.row}')
        try:
            if self.row is not None and self.row >= 0:
                response = self.api_handler_.delete_order(self.order_id.text(),self.ui.vente_edit_id.text())
                if self.row is not None and self.row >= 0:
                    if self.row < len(self.commande):
                        del self.commande[self.row]                   
                    else:
                        print("Index hors limites pour la commande.")
                        
                    self.ui.table_vente.removeRow(self.row)

                    self.clear_fields(self.ui.materiel_name,self.ui.category,self.ui.unit_prise,self.ui.quantity,self.ui.total_prise)

                    

                # self.set_table_refresh_data_for_commande()
                # self.ui.frame_301.setHidden(True)
                # print(f"Ligne supprimée : {self.row}")
            else:
                self.overlay.finish_loading()
                QMessageBox.warning(None, "Suppression impossible", "Aucune ligne sélectionnée pour suppression.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.overlay.finish_loading()
            QMessageBox.critical(None, "Erreur", f"Une erreur est survenue lors de la suppression : {e}")

    def set_table_refresh_data_for_commande(self):
        header = ("id", "Nom", "Category", "Prix", "Qt", "Total")

        self.all_headers_table_labels(
            self.ui.table_show_order, header, "#e2e8f0", 26, 180, 100, 60, 50, 80)
        self.ui.table_show_order.cellClicked.disconnect()
        self.ui.table_show_order.setSelectionBehavior(QAbstractItemView.SelectRows)
        data = self.commande

        if data:    
            self.select_all_populate(data, self.ui.table_show_order, self.on_row_clicked_vente,['id', 'nom','category','prix', 'quantite', 'total'])


    def on_row_clicked_vente(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        # self.order_id = QLineEdit()
        # self.order_id.setText("")
        self.row = None
        id_item = self.ui.table_show_order.item(row, 0)
        nom_item = self.ui.table_show_order.item(row, 1)
        cat_item = self.ui.table_show_order.item(row, 2)
        prix_u_item = self.ui.table_show_order.item(row, 3)
        qt_item = self.ui.table_show_order.item(row, 4)
        status_item = self.ui.table_show_order.item(row, 6)

        if nom_item: 
            self.row = row
            # self.vente_order_id.text()
            self.order_id.setText(id_item.text())
            self.ui.materiel_name.setText(nom_item.text())
            
            self.ui.frame_301.setHidden(False)
            category_index = self.ui.category.findText(str(cat_item.text()))
            self.ui.category.setCurrentIndex(category_index)
            status_index = self.ui.vente_status.findText(str(status_item.text() if status_item else ""))
            self.ui.vente_status.setCurrentIndex(status_index)

            self.ui.unit_prise.setText(prix_u_item.text())
            self.ui.quantity.setText(qt_item.text())
            self.total_prise()
            self.ui.ajouter_vente.setText("Modifier")


    def commander(self):
        # print(self.user_info)
        self.overlay.start_loading("Enregistrement de vente") 
        if not self.commande:
            self.overlay.finish_loading() 
            QMessageBox.warning(None, "Commande vide", "Aucune commande à enregistrer.")
            return

        id_vente = self.ui.vente_edit_id.text() 
        etudiant_id = self.ui.student_vente_id.text()
        user_id = self.user_connect.text() 

        response = self.api_handler_.enregistrer_vente(id=id_vente, items=self.commande, etudiant_id=etudiant_id, user_id=user_id)

    
    def imprimer_vente(self):
        self.overlay.start_loading('On génère le reçu')
        self.api_handler_.get_Vente_receipt(self.ui.vente_edit_id.text())
          

    def imprimer_direct_recu_vente(self, data):

        data = {
            "info": self.config_data['data'],
            "vente": {
                "order_itemId": data['order_itemId'],
                "user": data['user'],
                "etudiant":data['etudiant'], 
                "orderItems": data['orderItems'] 
            },
            "date": data['date']
        }


        try:
            self.run_async_direct_pdf(self.generate_direct_pdf_with_per,'vente_recu.html',data) 
            # template = Template(html_template)
            # rendered_html = template.render(info=data['info'], vente=data['vente'], date=data['date'])
            # HTML(string=rendered_html).write_pdf("recu_test.pdf", stylesheets=[custom_css])
            # os.startfile("recu_test.pdf") 
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("❌ Erreur lors de la génération :", e)

    def set_table_refresh_data_for_sell(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        if(self.ui.search_student_for_sell.text() == ''):
            self.ui.frame_280.setHidden(True)
            # self.ui.frame_280.setFixedHeight(0)

        header = ("Id", "Identifiant", "Nom", "prénom")
        self.all_headers_table_labels(
            self.ui.table_search_student_vente, header,  "#e2e8f0", 25, 100, 200, 200)
        self.ui.table_search_student_vente.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        
        self.api_handler_.student_live(self.ui.search_student_for_sell.text())        
        data = self.live_search_student 

        if data and 'data' in data and len(data['data']) > 0:
            self.ui.table_search_student_vente.setRowCount(len(data['data'])) 
            self.ui.frame_280.setHidden(False)
            # self.ui.frame_280.setFixedHeight(80)
            self.ui.frame_278.setHidden(True)
            self.ui.frame_279.setHidden(True)
            for row_idx, row_data in enumerate(data['data']):
                for col_idx, value in enumerate(row_data):
                    self.ui.table_search_student_vente.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
            self.ui.table_search_student_vente.cellClicked.connect(self.on_row_clicked_live_sell)
        else:
            self.ui.table_search_student_vente.setRowCount(0)
            self.ui.frame_280.setHidden(True)
            # self.ui.frame_280.setFixedHeight(0)
            self.ui.frame_278.setHidden(False)
            self.ui.frame_279.setHidden(False)

    def on_row_clicked_live_sell(self, row,column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_search_student_vente.item(row, 0)
        nom_item = self.ui.table_search_student_vente.item(row, 1)
        prenom_item = self.ui.table_search_student_vente.item(row, 2)
        if id_item:
            self.ui.student_vente_id.setText(id_item.text())
            full_name = f"{nom_item.text()} {prenom_item.text()}"
            self.ui.search_student_for_sell.setText(full_name)
            # self.search_for_sell.stop()
            self.ui.frame_280.setHidden(True)
            # self.ui.frame_280.setFixedHeight(0)
            self.ui.frame_278.setHidden(False)
            self.ui.frame_279.setHidden(False)

 

    def set_replace_template(self):  
        # self.background_image = self.get_path(os.path.join(
        #     'assets', 'icons', f'{self.ui.combo_template.currentData()}.jpg'
        # ))
        appdata = os.path.join(get_user_data_dir(), "gestion_ecole", "assets", "icons")
        self.background_image = self.get_path(os.path.join(
            appdata, f'{self.ui.combo_template.currentData()}.jpg'
        ))


        # Si le label n’existe pas encore, on le crée une seule fois
        if not hasattr(self, "background_label"):
            self.background_label = QLabel(self.ui.frame_108)
            self.background_label.setScaledContents(True)
            self.background_label.resize(self.ui.frame_108.size())
            self.background_label.lower()  # le mettre en arrière-plan

        # Mettre à jour le pixmap
        pixmap = QPixmap(self.background_image)
        self.background_label.setPixmap(pixmap)
 

    def make_an_identity_card(self):
        # self.overlay.start_loading()
        self.is_ip_camera = False
        self.ui.camera_ip_2.setChecked(False)
        self.search_camera_timer.start(1000)
        self.ui.combo_salle.clear()
        self.ui.combo_template.clear() 
        
        self.ui.stop_search_cam.setText("Arrêté")
        self.ui.stop_search_cam.setStyleSheet("color: red;")
        for name, title in self.salle.items():
            self.ui.combo_salle.addItem(title, name)

        for name, title in self.template.items():
            self.ui.combo_template.addItem(title,name)

        config = self.config_data 
        self.ui.frame_115.setHidden(True)
        # self.ui.frame_113.setHidden(True)
        self.school_name = ''
        self.school_address =" "
        self.school_phone = ' '
        self.full_name=''
        self.etudiant_id=None
        self.identifiant=''
        if config and config['data'] is not None and 'data' in config and  len(config['data']) > 0:
            data = config['data']
            ligne1 = data['ligne1']
            # self.ui.label_45.setText(str(data['nom']))
            self.ui.shool_adress.setText(str(data['adresse']))

            # self.school_name = data['nom']
            # self.school_address = data['adresse']
            # self.school_phone = f"+509 {ligne1}"

        self.student_photo = None
        self.institution_logo = None

        
        self.timer = QTimer()
        self.available_cameras = []
        self.camera_index = 0

        label_background = QLabel(self.ui.frame_108)
        pixmap = QPixmap(self.background_image)
        label_background.setPixmap(pixmap)
        label_background.setScaledContents(True)
        label_background.resize(self.ui.frame_108.size())
        label_background.lower()  # place le QLabel derrière tous les autres widgets

        # self.setup_connections()
        self.populate_camera_selector()
        # ===================================================================================================
        # load_btn
        # dlg = BadgeEditorDialog()
        # if dlg.exec() == QDialog.Accepted:
        #     recto, verso = dlg.get_result()
        #     recto.save("recto_final.png")
        #     verso.save("verso_final.png")
        #     print("Badges sauvegardés !")
        # else:
        #     print("Annulé par l'utilisateur.")

        #===============================================================================================


        self.ui.stackedWidget.setCurrentWidget(self.ui.ABadge)
        self.fancy_modal_show(self.ui.ABadge)



    def stop_populate_camera(self):
        if self.search_camera_timer.isActive():
            # Si le timer tourne → on l'arrête
            self.ui.stop_search_cam.setText("Relancé")
            self.ui.stop_search_cam.setStyleSheet("color: blue;")
            self.search_camera_timer.stop()
            print("⏸️ Timer arrêté.")
        else:
            # Si le timer est déjà arrêté → on le relance
            self.ui.stop_search_cam.setText("Arrêté")
            self.ui.stop_search_cam.setStyleSheet("color: red;")
            self.search_camera_timer.start(2000)
            print("▶️ Timer relancé.")



    def populate_camera_selector(self):        
        self.ui.camera_selector.clear()
        self.available_cameras = []
        cameras = QMediaDevices.videoInputs()         
        self.search_camera_timer.stop()
        if not cameras: 
            return        
        if self.is_ip_camera:
            self.ui.camera_selector.addItem('Camera ip', 0)
            # self.camera_index = 0
        else:
            for index, camera in enumerate(cameras):
                name = camera.description()
                self.available_cameras.append(index)
                self.ui.camera_selector.addItem(name, index)  # label = nom, data = index

            self.camera_index = self.available_cameras[0]
            self.camera_index_ = index

    def on_camera_changed(self, index):
        if self.is_ip_camera:
            ip = self.ui.line_camera_ip_2.text()
            if not ip:
                return
            self.camera_index=f"http://{ip}:8080/video"
        else:
            self.camera_index = self.ui.camera_selector.itemData(index)   
            print("Caméra sélectionnée :", self.camera_index)
 
    def start_camera_thread(self):
        from PySide6.QtCore import QThread

        # Cas où une référence zombie existe
        if getattr(self, "camera_thread", None):
            # Si l'objet C++ n'existe plus → on nettoie
            try:
                _ = self.camera_thread.isRunning()
            except RuntimeError:
                print("Thread zombie détecté → nettoyage")
                self.camera_thread = None
                self.worker = None

        # Vérifier si un thread est déjà actif
        if getattr(self, "camera_thread", None) and self.camera_thread.isRunning():
            print("Camera thread déjà actif")
            return

        # Création propre du thread
        self.camera_thread = QThread()
        self.worker = CameraWorker(self.camera_index, self.is_ip_camera)
        self.worker.moveToThread(self.camera_thread)

        self.camera_thread.started.connect(self.worker.run)
        self.worker.frame_ready.connect(self.update_camera_preview_threaded)

        # Quand worker finit → on demandera juste quit()
        self.worker.finished.connect(self.camera_thread.quit)

        # Pas de deleteLater ici → on contrôle nous-mêmes

        self.camera_thread.start()
        self.camera_active = True

    def active_camera_ip(self):
        ip = self.ui.line_camera_ip_2.text()
        if not ip or not self.is_ip_reachable(ip):
            self.is_ip_camera = False
            self.ui.camera_ip_2.setChecked(False)
            notify = Notify()
            notify.title = "Error"
            notify.message = f"{ip} n'est pas une adresse IP valide ou hors ligne!"
            notify.send()
            self.populate_camera_selector()
            return
        self.is_ip_camera = self.ui.camera_ip_2.isChecked()

        if self.is_ip_camera:
            self.ui.camera_ip_2.setText("IP active")
            # self.ui.camera_selector.addItem('Camera ip', 0)
            self.populate_camera_selector()
            self.ui.camera_ip_2.setStyleSheet("color: #34a853;")
        else:
            self.ui.camera_ip_2.setText("IP inactive")
            self.ui.camera_ip_2.setStyleSheet("color: #fcbc05;")
            self.populate_camera_selector()

            self.camera_index=0

        if self.camera_active:
            self.stop_camera_thread111()
         
        self.camera_active= False
        # self.camera_active= True
        self.toggle_camera()

    def change_camera(self, index): 
        print("we call camere change")
        self.stop_camera_thread111()
        self.camera_active = False
        if index < len(self.available_cameras):
            self.camera_index = self.available_cameras[index]
            if self.camera_active:
                self.timer.stop()
                if self.cap and self.cap.isOpened():
                    self.cap.release()
                print(f"self.is_ip_camera   {self.is_ip_camera}")
                if self.is_ip_camera:
                    ip = self.ui.line_camera_ip_2.text()
                    if not ip:
                        return
                    self.cap = cv2.VideoCapture(f"http://{ip}:8080/video")
                else:
                    self.cap = cv2.VideoCapture(self.camera_index)
                    self.camera_active = False
                    self.start_camera_thread() 
                self.timer.start(5)
            else:
                self.toggle_camera()
     
    def toggle_cameraeee(self):
        if self.is_ip_camera:
            ip = self.ui.line_camera_ip_2.text()
            if not ip:
                notify = Notify()
                notify.title ="Error"
                notify.message =f"{ip} n'est pas une adresse IP valide ou n'est hors ligne!"
                notify.send()
                return
            self.camera_index = f"http://{ip}:8080/video"
        if not self.camera_active:
            self.start_camera_thread() 
            self.ui.capture_btn.setText("Capturer")
            self.ui.capture_btn.setStyleSheet("color: #34a853;")
        else: 
            self.capture_photo()

    def toggle_camera(self):
        # Configuration IP
        if self.is_ip_camera:
            ip = self.ui.line_camera_ip_2.text()
            if not ip:
                notify = Notify()
                notify.title = "Error"
                notify.message = f"{ip} n'est pas une adresse IP valide ou est hors ligne!"
                notify.send()
                return
            self.camera_index = f"http://{ip}:8080/video"

        # Démarrer caméra
        if not self.camera_active:
            self.start_camera_thread()
            self.camera_active = True
            print('La caméra était active → prendre photo  1')
            self.ui.capture_btn.setText("Capturer")
            self.ui.capture_btn.setStyleSheet("color: #34a853;")
            return

        # La caméra était active → prendre photo
        print('La caméra était active → prendre photo  2')
        self.capture_photo()

    def update_camera_preview(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.ui.view_image.setPixmap(QPixmap.fromImage(qt_image).scaled(300, 350, Qt.KeepAspectRatio))

    def update_camera_preview_threaded(self, frame):
        # self.overlay.finish_loading()
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h,
                        bytes_per_line, QImage.Format_RGB888)
        
        self.ui.view_image.setPixmap(
            QPixmap.fromImage(qt_image).scaled(
                300, 350, Qt.KeepAspectRatio
            )
        )
    
    def stop_camera(self):
        if hasattr(self, "worker"):
            self.camera_active = False
            self.worker.stop()

    def stop_camera_thread111(self):
        try: 
            if getattr(self, "worker", None):
                self.worker.stop()   # -> running = False dans CameraWorker

            # 2. Demander l'arrêt du thread
            if getattr(self, "camera_thread", None):
                self.camera_thread.quit()

                # 3. ATTENDRE que le thread termine réellement
                if not self.camera_thread.wait(3000):  # 3 secondes max
                    print("Thread n'a pas voulu s'arrêter → forcer terminate()")
                    self.camera_thread.terminate()
                    self.camera_thread.wait()

            # 4. Nettoyage des pointeurs Python
            self.worker = None
            self.camera_thread = None

            # 5. État caméra
            self.camera_active = False 

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"errors: {e}") 

    def capture_photo(self):
        if not self.camera_active:
            print("capture_photo appelé alors que caméra OFF")
            return
        if not getattr(self, "worker", None):
            print("Worker inexistant → capture impossible")
            return
        if not getattr(self.worker, "cap", None) or not self.worker.cap.isOpened():
            print("Camera fermée, aucune capture possible")
            return

        # capture USB ou IP
        if self.is_ip_camera:
            ip = self.ui.line_camera_ip_2.text()
            if not ip:
                return
            self.student_photo = CameraWorker.capture_ip_photo(f"http://{ip}:8080/photo.jpg")
        else:
            # essayer plusieurs fois au cas où le read échoue
            frame = None
            for _ in range(5):
                ret, frame = self.worker.cap.read()
                if ret:
                    break
                time.sleep(0.05)
            if frame is not None:
                self.student_photo = frame
        if self.student_photo is None:
            print("Aucune image capturée")
            return

        # 5. Affichage
        self.update_photo_display()
        
        # 6. Arrêter proprement la caméra
        self.stop_camera_thread111()  # <--- IMPORTANT
        
        self.camera_active = False
        self.ui.capture_btn.setText("Prendre Photo")
        self.ui.capture_btn.setStyleSheet("color: #fcbc05;")

    def update_photo_display(self):
        if self.student_photo is not None:
            rgb_image = cv2.cvtColor(self.student_photo, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.ui.view_image.setPixmap(QPixmap.fromImage(qt_image).scaled(200, 250, Qt.KeepAspectRatio))


            frame_rect = QRect(40, 10, 234, 223)
            self.ui.image_path.setGeometry(frame_rect)

            w = self.ui.image_path.width()
            h = self.ui.image_path.height()
            # ou
            size = self.ui.image_path.size()
            print(size, w, h)
            w, h = size.width(), size.height() 

            # Charger et redimensionner l’image
            pixmap = QPixmap.fromImage(qt_image)
            pixmap = pixmap.scaled(
                frame_rect.width(), frame_rect.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Centrer l’image dans le QLabel
            self.ui.image_path.setPixmap(pixmap)
            self.ui.image_path.setAlignment(Qt.AlignCenter)
       
    def load_photo(self):
        # dlg = BadgeEditorDialog()
        # if dlg.exec() == QDialog.Accepted:
        #     recto, verso = dlg.get_result()
        #     recto.save("recto_final.png")
        #     verso.save("verso_final.png")
        #     print("Badges sauvegardés !")
        # else:
        #     print("Annulé par l'utilisateur.")
        file_path, _ = QFileDialog.getOpenFileName(self, "Charger une photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.student_photo = cv2.imread(file_path)
            self.update_photo_display()

    def closeEvent(self, event):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if hasattr(self, "camera_thread") and self.camera_thread:
            self.stop_camera_thread111() 
        # self.stop_camera()
        event.accept() 

        if event.type() == QEvent.Close:
            if self.user_info:
                reply = QMessageBox.question(
                self,
                "Quitter",
                "Voulez-vous vraiment quitter et vous déconnecter ?",
                QMessageBox.Yes | QMessageBox.No
                )

                if reply == QMessageBox.Yes:
                    self.deconnexion()
                    event.accept()  # On laisse fermer
                else:
                    event.accept()
                    # event.ignore()  # On bloque la fermeture
            else:
                event.accept()

    def set_table_refresh_search_for_card(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        if(self.ui.search_for_card.text() == ''):
            return  
        self.load_pixmap_image = None
        self.api_handler_.search_student(self.ui.search_for_card.text())  


    def set_table_refresh_search_for_card_show(self, data):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        header = ("Id", "Identifiant", "Nom", "prénom")
        self.ui.tableWidget_2.setColumnHidden(1, True)
        self.all_headers_table_labels(
            self.ui.tableWidget_2, header,  "#e2e8f0", 0, 10, 200, 200)
        self.ui.tableWidget_2.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        colonnes_ordre = ["id","identifiant", "nom", "prenom"]            
        
        if data and 'data' in data:
            self.select_all_populate(data.get('data',''), self.ui.tableWidget_2, self.on_row_clicked_live_search_,_ordre=colonnes_ordre) 
            

    def on_row_clicked_live_search_(self, row,column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.tableWidget_2.item(row, 0)
        self.responsable = "responsable info"
        if id_item:  
            if self.all_students_data:
                show_student = next((item for item in self.all_students_data['data'] if item['id'] == id_item.text()), None)
 
                if show_student:
                    self.etudiant_id=show_student.get('id',"")
                    self.load_pixmap_image = self.load_pixmap_from_base64(show_student.get('photo_base64',""))
                    print(self.load_pixmap_image)
                    self.full_name = f"{show_student['nom']} {show_student['prenom']}"
                    self.identifiant = show_student['identifiant']

                    self.ui.student_identifiant.setText(str(show_student['identifiant']))
                    self.ui.full_name.setText(str(self.full_name))

                    classe_etudiant = show_student.get('classes_etudiant')

                    if classe_etudiant:
                        # Vérifier que c'est une liste non vide
                        if isinstance(classe_etudiant, list) and len(classe_etudiant) > 0:
                            last_classe = classe_etudiant[-1]

                            # Vérifier que 'classes' existe et n'est pas vide
                            classes_info = last_classe.get('classes')
                            if classes_info and "nom_classe" in classes_info:
                                nom_classe = classes_info["nom_classe"]
                                print(f"nom_classe   {nom_classe}")
                                self.ui.classe.setText(str(nom_classe))
                            else:
                                print("⚠️ La clé 'classes' est absente ou vide.")
                        else:
                            print("⚠️ 'classe_etudiant' n'est pas une liste ou est vide.")
                    else:
                        print("⚠️ 'classe_etudiant' n'existe pas dans all_students_data.")


                    if self.all_students_data.get('responsable'):
                        adresse_responsable = show_student['responsable'].get('adresse_responsable','')
                        telephone_responsable = show_student['responsable'].get('telephone_responsable','')
                        self.responsable = f"{adresse_responsable} \n {telephone_responsable}"
                    self.ui.search_for_card.setText('')


    def get_base64_from_pixmap(self,pixmap):
        from PySide6.QtCore import QBuffer, QIODevice
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "JPG")
        base64_data = bytes(buffer.data().toBase64()).decode()
        return f"data:image/jpeg;base64,{base64_data}"

    # def convertir_image_en_base64(self,chemin_image):
    #     """Convertit une image en Base64"""
    #     with open(chemin_image, "rb") as image_file:
    #         image_data = image_file.read()
        
    #         encoded_string = base64.b64encode(image_data).decode("utf-8", errors="ignore")  # Ignorer erreurs d'encodage
    #         extension = chemin_image.split('.')[-1].lower()
    #         # print(f"data:image/{extension};base64,{encoded_string}")

    #     return f"data:image/{extension};base64,{encoded_string}"
 
   
    def generate_qrcode(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en QPixmap
        img = img.convert("RGB")
        qimg = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)
    
    def generate_badge_and_save(self):
        self.generate_badge(auto_save_image=True)

            #  if "base64," in data_input or len(data_input) > 500: # Détection Base64
            #     if "," in data_input:
            #         data_input = data_input.split(",")[1]
                
            #     image_data = base64.b64decode(data_input)
            #     with open(local_path, "wb") as file:
            #         file.write(image_data)
            #     return local_path


    def load_pixmap_from_base64(self,base64_str):
        try:
            # Nettoyage si la chaîne contient le préfixe "data:image/..."
            if "base64," in base64_str or len(base64_str) > 500:
                if "," in base64_str:
                    base64_str = base64_str.split(",")[1]
                
                img_data = base64.b64decode(base64_str)
                pixmap = QPixmap()
                pixmap.loadFromData(img_data)
                self.ui.image_path.setPixmap(pixmap)
                self.ui.view_image.setPixmap(pixmap)
                return pixmap
        except Exception as e:
            print(f"Erreur de conversion image: {e}")
            return None

    def generate_badge(self, auto_save_image=False):
        if not self.full_name or not self.identifiant:
            QMessageBox.critical(self, "Erreur", "Erreur : nom ou identifiant manquant !")
            return

        if not self.ui.classe:
            QMessageBox.critical(self, "Erreur", "Erreur : nom ou identifiant manquant !")
            return

        if self.student_photo is None and self.load_pixmap_image is None:
            QMessageBox.critical(self, "Erreur", "Erreur : photo de l'étudiant manquante !..")
            return

        if auto_save_image and self.student_photo is None:
            QMessageBox.critical(self, "Erreur", "Erreur : photo de l'étudiant manquante !")
            return
            
        # Création du badge final
        badge = QPixmap(QSize(1013, 638))  # 8.5x5.1cm @300DPI
        badge.fill(Qt.white)

        painter = QPainter(badge)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # 1️⃣ Fond avec image si disponible
        if self.background_image:
            background = QPixmap(self.background_image).scaled(
                badge.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(0, 0, background)

        # 2️⃣ Bordure du badge
        painter.setPen(QPen(QColor(0, 51, 102), 4))
        painter.drawRoundedRect(0, 0, 1013, 638, 0, 0)

        # 3️⃣ En-tête de l'institution
        painter.setFont(QFont("Arial", 28, QFont.Bold))
        painter.setPen(QColor(0, 51, 102))
        painter.drawText(0, 40, 1013, 50, Qt.AlignCenter, self.school_name)

        # 4️⃣ Cadre photo
        frame_rect = QRect(97, 127, 234, 261)

        if self.student_photo is not None or self.load_pixmap_image is not None:
            # not photo_pixmap.isNull()
            photo_pixmap = self.ui.view_image.pixmap() if self.ui.view_image else self.load_pixmap_image
            print(photo_pixmap)
            # 1️⃣ Mise à l’échelle avec KeepAspectRatioByExpanding (ça dépasse)
            scaled = photo_pixmap.scaled(
                frame_rect.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )

            # 2️⃣ Calcul du rectangle source à découper (crop centré)
            x = (scaled.width() - frame_rect.width()) // 2
            y = (scaled.height() - frame_rect.height()) // 2
            source_rect = QRect(x, y, frame_rect.width(), frame_rect.height())

            # 3️⃣ Dessin du crop dans le cadre
            painter.drawPixmap(frame_rect, scaled, source_rect)
        else:
            return
        # frame_rect = QRect(97, 127, 234, 261)
        # # painter.setPen(QPen(Qt.black, 2))
        # painter.drawRect(frame_rect)

        # # 5️⃣ Photo de l'étudiant
        # if self.student_photo is not None:
        #     photo_pixmap = self.ui.view_image.pixmap()
        #     filled = photo_pixmap.scaled(
        #         frame_rect.size().expandedTo(photo_pixmap.size()),
        #         Qt.KeepAspectRatioByExpanding,
        #         Qt.SmoothTransformation
        #     )
        #     painter.drawPixmap(frame_rect, filled)

       
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        painter.drawText(100, 180, 1013, 200, Qt.AlignCenter, self.full_name)

        painter.setFont(QFont("Arial", 20))
        painter.drawText(100, 220, 1013, 200, Qt.AlignCenter, self.ui.classe.text())

       
        painter.setFont(QFont("Arial", 17))
        # painter.drawText(60, 435, "ID No")
        painter.setFont(QFont("Arial", 18, QFont.Bold))
        painter.drawText(62, 475, self.identifiant)

        painter.setFont(QFont("Arial", 17))
        # painter.drawText(400, 435, "Date d'Exp.")
        painter.drawText(300, 480, "Juin 2026")
        # painter.drawText(300, 480, (datetime.now() + timedelta(days=330)).strftime("%d/%m/%Y"))

    
        painter.drawText(560, 480, self.ui.combo_salle.currentData() if self.ui.combo_salle else "")
        painter.setPen(QPen(Qt.black, 1))
        # painter.drawText(800, 435, "Signature")

       
        # painter.setFont(QFont("Arial", 16))
        # painter.drawText(360, 570, self.school_address)
        # painter.drawText(360, 600, self.school_phone)

        qr_pixmap = self.generate_qrcode(self.responsable)
        painter.drawPixmap(880, 530, qr_pixmap)

        painter.end()



        output_dir = os.path.join(os.path.expanduser("~"), "Desktop", f"Badges {self.ui.classe.text()}")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{self.full_name }.png")

        # Exemple : sauvegarder une QPixmap
        # pixmap.save(file_path, "PNG")

        if file_path:
            badge.save(file_path)
   
            self.toggle_camera()
            notify = Notify()
            notify.title ="Succès"
            notify.message ="Badge généré avec succès !"
            notify.send()
            if auto_save_image:
                payload={
                    'etudiant_id':self.etudiant_id,
                    'image_base64':self.get_base64_from_pixmap(self.ui.view_image.pixmap())
                } 
                self.api_handler_.save_badge_image(payload)
            # QMessageBox.information(self, "Succès", "Badge généré avec succès !")

    

    
    def profile(self, data_profile=None):
        # self.restart_disconnect_timer()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        try:
            data_profile = self.config_data 
            # print(data_profile,self.config_data) 
            if data_profile and data_profile['data'] is not None and 'data' in data_profile and len(data_profile['data']) >0:
                data = data_profile['data']
                self.ui.input_nom.setText(str(data.get('nom', "")))
                self.ui.input_email.setText(str(data.get('email', "")))
                self.ui.input_adresse.setText(str(data.get('adresse', "")))
                self.ui.input_ligne1.setText(str(data.get('ligne1', "")))
                self.ui.input_ligne2.setText(str(data.get('ligne2', "")))
                image_url = data.get('logo_image_base64', '')

                if image_url and not os.path.exists(self.icon_path_logo):
                    self.download_image(image_url, self.icon_path_logo)

                if os.path.exists(self.icon_path_logo):
                    self.show_image_logo_on_app(self.ui.show_image,self.icon_path_logo)

                    # self.ui.show_image.setPixmap(QPixmap(self.icon_path_logo))
            
            self.ui.input_image.setHidden(True)

            self.ui.input_image_template_certificat.setHidden(True)
            self.ui.input_image_temlate_diplome.setHidden(True)
            self.ui.input_image_temlate_2.setHidden(True)
            self.ui.input_image_temlate_1.setHidden(True)
            self.ui.stackedWidget.setCurrentWidget(self.ui.profile)
            self.fade_in_page(self.ui.profile)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading profile: {e}")
            QMessageBox.warning(self, "Error", "Failed to load profile data")

        try:
            appdata = os.path.join(get_user_data_dir(), "gestion_ecole", "assets", "icons")
            file_path_1 = os.path.join(appdata, "template_badge_1.jpg")
            file_path_2 = os.path.join(appdata, "template_badge_2.jpg")
            if file_path_1:
                pixmap = QPixmap(file_path_1)
                pixmap_display = pixmap.scaled(
                    self.ui.label_153.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.ui.label_153.setPixmap(pixmap_display)
            if file_path_2:
                pixmap = QPixmap(file_path_2)
                pixmap_display2 = pixmap.scaled(
                    self.ui.label_154.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.ui.label_154.setPixmap(pixmap_display2)
            
        except Exception as e:
            print(e)

    def role_page(self):
        self.ui.table_roles.setHidden(True)
        self.ui.input_id_user_for_role.setHidden(True)

        self.ui.rechercher_pour_role.setText('')
        self.ui.input_id_user_for_permission.setText('')
        
        self.ui.recherche_un_user.setText('')
        self.ui.input_id_user_for_role.setText('')  
        
        self.ui.combo_roles.setCurrentIndex(-1)  

        self.roles_ids = {}
        self.roles_ids_checked = [] 
        
        # Connect signals
        self.ui.btn_modifier_roles.clicked.connect(self.send_selected_roles)
        self.show_roles()
        self.ui.stackedWidget.setCurrentWidget(self.ui.role_page)
        self.fade_in_page(self.ui.role_page)

    def permission_page(self):
        self.ui.table_permission.setHidden(True)
        self.ui.input_id_user_for_permission.setHidden(True) 

        self.ui.rechercher_pour_role.setText('')
        self.ui.input_id_user_for_permission.setText('')

        self.ui.recherche_un_user.setText('')
        self.ui.input_id_user_for_role.setText('')  
        
        self.ui.combo_roles.setCurrentIndex(-1) 

        self.permission_ids = {}
        self.permissions_ids_checked = []
        self.ui.btn_modifier_permission.clicked.connect(self.send_selected_permissions)

        self.ui.combo_roles.clear()
        roles_ = self.fetch_data_roles
        for role in roles_:
            self.ui.combo_roles.addItem(role['name'], role['id'])
        self.show_permissions()
        self.ui.combo_roles.currentIndexChanged.connect(self.fetch_role_with_permission)

        self.ui.stackedWidget.setCurrentWidget(self.ui.permission_page)
        self.fade_in_page(self.ui.permission_page)

    def show_roles(self):
        """Display roles as checkboxes in a grid layout"""
        # Clear existing widgets from widget_14
        if self.ui.widget_14.layout():
            # Delete all child widgets
            for i in reversed(range(self.ui.widget_14.layout().count())):
                item = self.ui.widget_14.layout().takeAt(i)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())
            # Remove the layout
            # self.ui.scrollAreaWidgetContents_13.setLayout(self.ui.widget_14.layout())
            QWidget().setLayout(self.ui.widget_14.layout())

        # Create new layouts
        self.roles_ids_checked=[]
        layout_role = QVBoxLayout()
        self.checkbox_grid = QGridLayout()
        self.checkbox_grid.setSpacing(15)
        self.checkbox_grid.setContentsMargins(0,0,0,0)
        self.checkboxes_role = {}
        
        try:
            roles = self.fetch_data_roles
            COLUMNS = 3  # Configurable
            
            for row, role in enumerate(roles):
                col = row % COLUMNS
                row_pos = row // COLUMNS
                
                checkbox = QCheckBox(role["name"])
                role_id = role["id"]
                checkbox.setProperty("role_id", role_id)
                
                # Check if role is selected
                is_checked = role_id in self.roles_ids
                if is_checked:
                    self.roles_ids_checked.append(role_id)
                checkbox.setChecked(is_checked)
                
                # Style the checkbox based on state
                self.update_checkbox_style(checkbox, is_checked)
                
                # Connect signal using lambda with explicit role_id capture
                checkbox.toggled.connect(
                    lambda checked, cb=checkbox, rid=role_id: self.on_role_toggled(cb, checked, rid)
                )
                self.checkbox_grid.addWidget(checkbox, row_pos, col)
                self.checkboxes_role[role_id] = checkbox
            
            layout_role.addLayout(self.checkbox_grid)
            self.ui.widget_14.setLayout(layout_role)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error showing roles: {e}")
            QMessageBox.warning(self, "Error", "Failed to load roles")

    def clear_layout(self, layout):
        """Recursively clear a layout and its children"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())


    def on_role_toggled(self, checkbox, checked, role_id):
        """Handle role checkbox toggle"""
        if checked:
            if role_id not in self.roles_ids_checked:
                self.roles_ids_checked.append(role_id)
        else:
            if role_id in self.roles_ids_checked:
                self.roles_ids_checked.remove(role_id)
        self.update_checkbox_style(checkbox, checked)

    def update_checkbox_style(self, checkbox, checked):
        """Update checkbox appearance based on state"""
        checkbox.setStyleSheet(
            "font-size: 13pt; border: none; color: #22a120;" if checked 
            else "font-size: 13pt; border: none; color: #777;"
        )

    def send_selected_roles(self):
        """Send selected roles to backend"""
        try:
            if not self.roles_ids_checked or not self.ui.input_id_user_for_role.text():
                QMessageBox.warning(self, "Warning", "Please select at least one role and a valid user")
                return
            
            response = self.api_handler_.assign_role_to_user(
                self.roles_ids_checked,
                self.ui.input_id_user_for_role.text()
            )
 
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error sending roles: {e}")
            QMessageBox.warning(self, "Error", "Failed to assign roles")

    def set_table_refresh_data_for_live_search_role(self):
        """Dynamic table update for role search"""
        search_text = self.ui.rechercher_pour_role.text()
        self.ui.table_roles.setHidden(not bool(search_text))

        if not search_text:
            self.ui.frame_258.setHidden(False)
            self.ui.widget_14.setHidden(False)
            return
        self.roles_ids=[]
        self.ui.table_roles.setRowCount(0)
        try:
            data = self.api_handler_.fetchDataWithRole(
                        data=search_text
                    )                
        except Exception as e:
            print(f"Error refreshing role table: {e}")
            self.ui.table_roles.setRowCount(0)

    def on_row_clicked_live_search_role(self, row, column):
        """Handle row click in role search table"""
        try:
            id_item = self.ui.table_roles.item(row, 0).text()
            id_nom = self.ui.table_roles.item(row, 1).text()
            id_prenom = self.ui.table_roles.item(row, 2).text()
            
            if id_item:
                self.ui.input_id_user_for_role.setText(id_item)
                full_name = f"{id_nom} {id_prenom}"
                self.ui.rechercher_pour_role.setText(full_name)
                self.ui.frame_258.setHidden(False)
                self.ui.widget_14.setHidden(False)
                self.ui.table_roles.setHidden(True)
                self.show_roles()
        except Exception as e:
            print(f"Error handling row click: {e}")

    def fetch_role_with_permission(self):
        self.permission_ids=[]
        self.ui.recherche_un_user.setText("")
        self.ui.input_id_user_for_permission.setText('')
        if self.ui.combo_roles.currentData():
            self.api_handler_.getPermissionByRole(self.ui.combo_roles.currentData())

 

# ================================  PERMISSIONS SECTION ============================================
    def clear_layout_permission(self, layout):
        """Recursively clear a layout and its children"""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout_permission(item.layout())
 

    def show_permissions(self):
        """Affiche les rôles sous forme de cases à cocher dans un layout avec défilement"""
        
        if self.ui.widget_15.layout():
            QWidget().setLayout(self.ui.widget_15.layout())

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) 
        scroll_area.setStyleSheet("border: none; background: transparent;") 
        
        container = QWidget()
        self.checkbox_grid = QGridLayout(container) 
        self.checkbox_grid.setSpacing(15)
        
        self.checkboxes_permissions = {}
        self.permissions_ids_checked = []

        try:
            permissions = self.fetch_data_permissions 
            COLUMNS = 4 
            
            for index, permission in enumerate(permissions):
                col = index % COLUMNS
                row_pos = index // COLUMNS
                
                checkbox = QCheckBox(permission["name"])
                permission_id = permission["id"]
                checkbox.setProperty("permission_id", permission_id)
                
                
                is_checked = permission_id in self.permission_ids
                if is_checked:
                    self.permissions_ids_checked.append(permission_id)
                checkbox.setChecked(is_checked)
                
                
                self.update_checkbox_style_permission(checkbox, is_checked)
                checkbox.toggled.connect(
                    lambda checked, cb=checkbox, rid=permission_id: self.on_permission_toggled(cb, checked, rid)
                )
                
                # Ajout au grid
                self.checkbox_grid.addWidget(checkbox, row_pos, col)
                self.checkboxes_permissions[permission_id] = checkbox
            
            
            scroll_area.setWidget(container) 
            
            main_layout = QVBoxLayout(self.ui.widget_15)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(scroll_area)
            self.ui.widget_15.setLayout(main_layout)
            
        except Exception as e:
            print(f"Error showing permissions: {e}")
    
    def show_permissions1(self):
        """Display roles as checkboxes in a grid layout"""
        print(f"self.permission_ids\n\n {self.permission_ids} \n\n")
        # Clear existing widgets from widget_14
        if self.ui.widget_15.layout():
            for i in reversed(range(self.ui.widget_15.layout().count())):
                item = self.ui.widget_15.layout().takeAt(i)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout_permission(item.layout()) 
            QWidget().setLayout(self.ui.widget_15.layout())

        # Create new layouts
        layout_permission = QVBoxLayout()
        self.checkbox_grid = QGridLayout()
        self.checkbox_grid.setSpacing(15) 
        self.checkboxes_permissions = {}
        self.permissions_ids_checked =[]
        try:
            
            permissions = self.fetch_data_permissions 
            
            COLUMNS = 4  # Configurable
            
            for row, permission in enumerate(permissions):
                col = row % COLUMNS
                row_pos = row // COLUMNS
                
                checkbox = QCheckBox(permission["name"])
                permission_id = permission["id"]
                checkbox.setProperty("permission_id", permission_id)
                
                # Check if permission is selected
                is_checked = permission_id in self.permission_ids
                if is_checked:
                    self.permissions_ids_checked.append(permission_id)
                checkbox.setChecked(is_checked)
                
                # Style the checkbox based on state
                self.update_checkbox_style_permission(checkbox, is_checked)
                 
                checkbox.toggled.connect(
                    lambda checked, cb=checkbox, rid=permission_id: self.on_permission_toggled(cb, checked, rid)
                )
                self.checkbox_grid.addWidget(checkbox, row_pos, col)
               
                self.checkboxes_permissions[permission_id] = checkbox
            
            
            layout_permission.addLayout(self.checkbox_grid)
            self.ui.widget_15.setStyleSheet("""
                                    QCheckBox {
                                        max-width: 13px;
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        padding-right: 18px; 
                                    }
                                                QLabel{
                                                    color:#777}
                                    QCheckBox:checked {
                                        border: 1px solid #40C057;
                                        border-radius: 4px;
                                        padding-left: 18px; 
                                        padding-right: 0px;
                                    }
                                    QCheckBox::indicator {
                                        /*width: 13px;
                                            height: 13px;*/
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        background-color: #666;
                                    }
                                
                                    """)
            self.ui.widget_15.setLayout(layout_permission)
            
        except Exception as e:
            print(f"Error showing permissions: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load permissions")


    def on_permission_toggled(self, checkbox, checked, permission_id):
        """Handle permission checkbox toggle"""
        if checked:
            if permission_id not in self.permissions_ids_checked:
                self.permissions_ids_checked.append(permission_id)
        else:
            if permission_id in self.permissions_ids_checked:
                self.permissions_ids_checked.remove(permission_id)
        self.update_checkbox_style_permission(checkbox, checked)

    def update_checkbox_style_permission(self, checkbox, checked):
        """Update checkbox appearance based on state"""
        checkbox.setStyleSheet(
            "font-size: 13pt; border: none; color: #22a120;height:25px" if checked 
            else "font-size: 13pt; border: none; color: #777;"
        )

    def send_selected_permissions(self):
        """Send selected permissions to backend"""
        try:

            if not self.permissions_ids_checked:# or not self.ui.input_id_user_for_permission.text():
                QMessageBox.warning(self, "Warning", "Please select at least one permission and a valid user")
                return


            response = self.api_handler_.assign_permission_to_role(
            role=self.ui.combo_roles.currentData(),user_id=self.ui.input_id_user_for_permission.text(),permission=self.permissions_ids_checked)
          
                
        except Exception as e:
            print(f"Error sending permissions: {e}")
            QMessageBox.warning(self, "Error", "Failed to assign permissions")

    def send_selected_permissions1(self):
        """Récupère les rôles cochés et les envoie au backend"""
        selected_permissions = [
            permission_id
            # {"id": permission_id, "name": permission_data.text()}
            # for permission_id in self.checkboxes_permissions.items()
            for permission_id, permission_data in self.checkboxes_permissions.items()
            if permission_data.isChecked()
        ]


        if not self.permissions_ids_checked:
            QMessageBox.warning(self, "Aucune permission sélectionnée", "Veuillez sélectionner au moins une permission.")
            return
        
        permission_to_role = self.api_handler_.assign_permission_to_role(
            # token=self.token_manager.get_token(), 
            role=self.ui.combo_roles.currentData(),user_id=self.ui.input_id_user_for_permission.text(),permission=self.permissions_ids_checked)        

        # Ici, on pourrait envoyer via une API avec `requests.post(url, json=selected_permissions)`
        # QMessageBox.information(self, "Succès", "Les permissions ont été envoyés !")
    

    def set_table_refresh_data_for_live_search_permission(self):
        """Dynamic table update for permission search"""
        self.permission_ids = []
        search_text = self.ui.recherche_un_user.text()
        self.ui.combo_roles.setCurrentIndex(-1)
        self.ui.table_permission.setHidden(not bool(search_text))


        if not search_text:
            self.ui.frame_254.setHidden(True)
            self.ui.widget_15.setHidden(True)
            return

        try:

            data = self.api_handler_.fetchDataWithPermission(
                    data=search_text
                )
 
        except Exception as e:
            print(f"Error refreshing role table: {e}")
            # self.ui.table_roles.setRowCount(0)


    def on_row_clicked_live_search_permission(self, row, column):
        """Handle row click in permission search table"""
        try:
            id_item = self.ui.table_permission.item(row, 0).text()
            id_nom = self.ui.table_permission.item(row, 1).text()
            id_prenom = self.ui.table_permission.item(row, 2).text()
            
            if id_item:
                self.ui.input_id_user_for_permission.setText(id_item)
                full_name = f"{id_nom} {id_prenom}"
                self.ui.recherche_un_user.setText(full_name)
                self.ui.frame_254.setHidden(False)
                self.ui.widget_15.setHidden(False)
                self.ui.table_permission.setHidden(True)
                self.show_permissions()
        except Exception as e:
            print(f"Error handling row click: {e}")

    def save_profile(self):
        self.overlay.start_loading()
        nom = self.ui.input_nom.text()
        adresse = self.ui.input_adresse.text()
        email = self.ui.input_email.text()
        ligne1 = self.ui.input_ligne1.text()
        ligne2 = self.ui.input_ligne2.text()
        logo_image_path = self.convertir_image_en_base64(self.ui.input_image.text()) if self.ui.input_image.text() else None

        response = self.api_handler_.enregistrer_profile(nom=nom,email=email,ligne1=ligne1,ligne2=ligne2,adresse=adresse,logo_image_path=logo_image_path)
         

    # def choisir_image_profile(self):
    #     """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """
    #     options = QFileDialog.Options()
    #     file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.xpm *.jpg *.jpeg *.gif *.bmp)", options=options)
        
    #     if file_path:  
    #         pixmap = QPixmap(file_path)
       
    #         self.ui.input_image.setText(file_path)

    #         self.ui.show_image.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))  # 
            
    #     else:
    #         print("Aucune image sélectionnée")

    def choisir_image_profile(self):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """
         
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Choisir une image", 
            "", 
            "Images (*.png *.xpm *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:  
            pixmap = QPixmap(file_path) 
            if not pixmap.isNull():
                self.ui.input_image.setText(file_path) 
                self.ui.show_image.setPixmap(
                    pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
            else:
                print("Erreur : Le fichier image est corrompu ou illisible.")
        else:
            print("Aucune image sélectionnée")

    def template_badge_1(self):
        """Choisir une image template, vérifier sa taille, l'afficher et la sauvegarder dans AppData"""

        # options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le template No 1 1014, 1014 X 639 px",
            "",
            "Images (*.png *.jpg *.jpeg)"
            # options=options
        )
        
        if not file_path:
            print("Aucune image sélectionnée")
            return

        # Charger l’image
        pixmap = QPixmap(file_path)

        # --- Vérification de la taille ---
        if pixmap.width() not in [1014,1013, 1015] or pixmap.height() != 639:
            QMessageBox.warning(
                self,
                "Taille incorrecte",
                "L’image doit obligatoirement mesurer 1015 × 639 pixels."
            )
            return

        # --- Affichage dans le QLabel ---
        pixmap_display = pixmap.scaled(
            self.ui.label_153.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label_153.setPixmap(pixmap_display)
        self.ui.input_image_temlate_1.setText(file_path)

        # --- Chemin de stockage dans AppData ---
        appdata = os.path.join(get_user_data_dir(), "gestion_ecole", "assets", "icons")
        os.makedirs(appdata, exist_ok=True)

        save_path = os.path.join(appdata, "template_badge_1.jpg")

        # --- Sauvegarde sans redimensionner ---
        success = pixmap.save(save_path, "JPG")

        if success:
            print("Image validée et sauvegardée dans :", save_path)
        else:
            print("Erreur : impossible de sauvegarder l'image.")


    def template_badge_2(self):
        """Choisir une image template, vérifier sa taille, l'afficher et la sauvegarder dans AppData"""
 
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le template No 2 1014, 1014 X 639 px",
            "",
            "Images (*.png *.jpg *.jpeg)"  
        )
        
        if not file_path:
            print("Aucune image sélectionnée")
            return

        # Charger l’image
        pixmap = QPixmap(file_path)

        # --- Vérification de la taille ---
        if pixmap.width() not in [1014,1013, 1015] or pixmap.height() != 639:
            QMessageBox.warning(
                self,
                "Taille incorrecte",
                "L’image doit obligatoirement mesurer 1015,1014,1013 × 639 pixels."
            )
            return

        # --- Affichage dans le QLabel ---
        pixmap_display = pixmap.scaled(
            self.ui.label_154.size(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label_154.setPixmap(pixmap_display)
        self.ui.input_image_temlate_2.setText(file_path)

        # --- Chemin de stockage dans AppData ---
        appdata = os.path.join(get_user_data_dir(), "gestion_ecole", "assets", "icons")
        os.makedirs(appdata, exist_ok=True)

        save_path = os.path.join(appdata, "template_badge_2.jpg")

        # --- Sauvegarde sans redimensionner ---
        success = pixmap.save(save_path, "JPG")

        if success:
            print("Image validée et sauvegardée dans :", save_path)
        else:
            print("Erreur : impossible de sauvegarder l'image.")


    def template_diplome(self):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """
         
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir le template No 2", "", "Images (*.png *.jpg *.jpeg)" )
        
        if file_path:  
            pixmap = QPixmap(file_path)
       
            self.ui.input_image_temlate_diplome.setText(file_path)
            pixmap = pixmap.scaled(
                self.ui.label_156.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # garde le ratio mais "crop"
                Qt.TransformationMode.SmoothTransformation
            )
            self.ui.label_156.setPixmap(pixmap)

            # self.ui.label_156.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))  # 
            
        else:
            print("Aucune image sélectionnée")

    def template_certificat(self):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """        
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir le template No 2", "", "Images (*.png *.jpg *.jpeg)")
        
        if file_path:  
            pixmap = QPixmap(file_path)
       
            self.ui.input_image_template_certificat.setText(file_path)
            pixmap = pixmap.scaled(
                self.ui.label_155.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # garde le ratio mais "crop"
                Qt.TransformationMode.SmoothTransformation
            )
            self.ui.label_155.setPixmap(pixmap)

            # self.ui.label_155.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))  # 
            
        else:
            print("Aucune image sélectionnée")
    
# ================================AJOUTER  DES DOCUMENT============================================
        


# ================================AJOUTER  DES DOCUMENTS============================================  

    def ajouter_document(self): 
        row_frame = QFrame() 
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)

        # Déclaration des widgets
        combo_box = QComboBox()
        line_edit1 = QLineEdit() 
        line_path = QLineEdit() 
        date_edit = QDateEdit()
        chose_file = QPushButton("Choisir une image")
        supprimer = QPushButton("Supprimer")
        label_file = QLabel()

        supprimer.setFlat(True)
        chose_file.setFlat(True)
        line_edit1.setPlaceholderText('Numero du Document') 

        # Nommage pour identification future
        combo_box.setObjectName("combo_box")
        line_edit1.setObjectName("line_edit1")
        line_path.setObjectName("line_path")
        date_edit.setObjectName("date_edit")
        chose_file.setObjectName("chose_file")
        supprimer.setObjectName("supprimer")
        label_file.setObjectName("label_file")

        combo_box.addItems(documentTypes)
        row_layout.setSpacing(15)

        # Placement des widgets
        row_layout.addWidget(combo_box, 0, 0)
        row_layout.addWidget(line_edit1, 0, 1) 
        row_layout.addWidget(line_path, 1, 0) 
        row_layout.addWidget(date_edit, 0, 2)
        row_layout.addWidget(chose_file, 0, 3)
        row_layout.addWidget(label_file, 0, 4)
        row_layout.addWidget(supprimer, 0, 5)

        self.ui.widget_piece_inner.setStyleSheet("""
            QComboBox, QLineEdit, QDateEdit { width: 200px; }
            #supprimer { color: red; }
            #chose_file { 
                border: 1px solid #b23cfd;
                color: #b23cfd;
                padding: 5px;
                border-radius: 5px;
            }
            #label_file{
                border: 1px solid #ccc;
                color: #ccc;
                padding: 5px;
                min-width:20px;
                border-radius: 5px;
            }
            #date_edit,#combo_box,#line_edit1{
                min-width:200px;
            }
        """)

        self.ui.widget_piece_inner.layout().addWidget(row_frame)

        if self.ui.frame_40:
            layout = self.ui.widget_piece_inner.layout()
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget == self.ui.frame_40:
                    layout.removeWidget(widget)
                    widget.deleteLater()
                    print("frame_40 supprimé")
                    break

        supprimer.clicked.connect(lambda: self.supprimer_ligne_p(row_frame))
        chose_file.clicked.connect(lambda: self.choisir_image(label_file, line_path))

        # Stocker uniquement le QFrame pour traitement futur
        if not hasattr(self, 'document_frames'):
            self.document_frames = []
        self.document_frames.append(row_frame)


    def supprimer_ligne_p111(self, frame):
        """ Supprime une ligne en retirant le QFrame du layout """
        print('Suppression d\'une ligne')
        self.ui.widget_piece_inner.layout().removeWidget(frame)
        frame.deleteLater()

    def supprimer_ligne_p(self, frame):
        """ Supprime une ligne en retirant le QFrame du layout """
        print("Suppression d'une ligne")
        self.ui.widget_piece_inner.layout().removeWidget(frame)
        frame.deleteLater()

        # Supprimer aussi de la liste
        if hasattr(self, 'document_frames') and frame in self.document_frames:
            self.document_frames.remove(frame)


    def choisir_image(self, label_file,line_path):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """ 
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.xpm *.jpg *.jpeg *.gif *.bmp)")
        
        if file_path:  
            pixmap = QPixmap(file_path)
       
            line_path.setText(file_path)
            label_file.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))  # Dimensionner l'image
            label_file.setText("")
            label_file.setText("")  
            # print(f"Image sélectionnée : {file_path}")Fto
        else:
            print("Aucune image sélectionnée")

# ================================AJOUTER  DES DOCUMENTS============================================


# ================================RE-POSITIONNEMENT============================================
    # def mousePressEvent(self, event):
    #     # Lorsque l'on clique pour déplacer la fenêtre
    #     if event.button() == Qt.LeftButton:
    #         self.is_dragging = True
    #         self.drag_position = event.globalPosition().toPoint()
    #         event.accept()

    # def mouseMoveEvent(self, event):
    #     # Déplacer la fenêtre si on fait glisser
    #     if self.is_dragging:
    #         delta = event.globalPosition().toPoint() - self.drag_position
    #         self.move(self.pos() + delta)
    #         self.drag_position = event.globalPosition().toPoint()
    #         event.accept()

    # def mouseReleaseEvent(self, event):  
    #     if event.button() == Qt.LeftButton:
    #         self.is_dragging = False

    # def toggle_maximize(self):  
    #     if self.isMaximized():
    #         self.showNormal()
    #     else:
    #         self.showMaximized()
# ================================RE-POSITIONNEMENT============================================

# ==============================enregistre les etudiant============================================
    
    def sauvegarde_etudiant(self): 
        # 
        self.overlay.start_loading("Enregistrement d'élève")
        nom = self.ui.nom.text()
        prenom = self.ui.prenom.text()
        telephone = self.ui.telephone.text()
        sexe = self.ui.sexe.currentText()
        date_de_naissance = self.ui.date_de_naissance.text()
        adresse = self.ui.adresse.text()
        lieu_de_naissance = self.ui.lieu_de_naissance.text()
        religion = self.ui.religion.text()
        niveau_id = self.ui.niveau_id.currentData()
        classe_actuelle_id = self.ui.classe_actuelle_id.currentData()
        annee_academique_id = self.ui.annee_academique_id.currentData()
        faculte_id = self.ui.faculte_id.currentData()
        email = self.ui.email_3.text() if self.ui.email_3 else None
        nom_responsable = self.ui.nom_responsable.text()
        prenom_responsable = self.ui.prenom_responsable.text()
        email_responsable = self.ui.email_responsable.text()
        sexe_responsable = self.ui.sexe_responsable.text()
        telephone_responsable = self.ui.telephone_responsable.text()
        adresse_responsable =self.ui.adresse_responsable.text()
        student_id =self.ui.student_id.text()
        aide_financiere = self.ui.aide_financiere.currentText()

        nisu = self.ui.dernier_etablissement.text()
        dernier_etablissement = self.ui.nisu.text()

        documentss = []
        # for ligne in self.documents:            
        #     ligne_donnees = {
        #         "document_numero": ligne["document_numero"].text(),
        #         "document_date_dexpiration": ligne["document_date_dexpiration"].date().toString("yyyy-MM-dd"),
        #         "type_de_document": ligne["type_de_document"].currentText(),
        #         # "document_image":ligne["document_image"].text()
        #         "document_image": self.convertir_image_en_base64(ligne["document_image"].text())
        #     }
        #     documentss.append(ligne_donnees)


                # donnees_etudiant = []

        for frame in getattr(self, 'document_frames', []):
            if frame is None or not frame.isVisible():
                continue

            try:
                # Trouver les widgets par leur objectName
                combo_box = frame.findChild(QComboBox, "combo_box")
                line_edit1 = frame.findChild(QLineEdit, "line_edit1")
                line_path = frame.findChild(QLineEdit, "line_path")
                date_edit = frame.findChild(QDateEdit, "date_edit")

                # Sécurité : s'assurer qu'ils existent encore
                if any(widget is None for widget in [combo_box, line_edit1, line_path, date_edit]):
                    continue

                documentss.append({
                    "type_de_document": combo_box.currentText(),
                    "document_numero": line_edit1.text(),
                    "document_date_dexpiration": date_edit.date().toString("yyyy-MM-dd"),
                    "document_image": self.convertir_image_en_base64(line_path.text()) if line_path.text() else None
                })

            except RuntimeError as e:
                print("Erreur de récupération de données (widget supprimé) :", e)

        # Exemple : affichage ou traitement
        # print("Données collectées :", donnees_etudiant)
        

        response = self.api_handler_.enregistrer_etudiant(student_id,nom,prenom,telephone,sexe,date_de_naissance, adresse,lieu_de_naissance,  religion,niveau_id,classe_actuelle_id,annee_academique_id,faculte_id,email,nom_responsable,prenom_responsable,email_responsable,sexe_responsable,telephone_responsable,adresse_responsable,aide_financiere,documentss,nisu,dernier_etablissement)


    # def show_result_after_save_student(self,response):
    #     from Controllers.Validator import ValidatorError
    #     if response and 'errors' in response: 
    #         self.overlay.finish_loading()        
    #         ve = ValidatorError()
    #         ve.generic_direct_error_message(response_data=response) 

    #     if response and 'success' in response:
    #         self.etudiant_page()
    #         self.set_table_refresh_data_student()  
    #         self.etudiant_page()
    #         self.clear_fields(self.ui.student_id, self.ui.nom, self.ui.prenom, self.ui.telephone, self.ui.email_3,self.ui.sexe, self.ui.adresse,self.ui.niveau_id,self.ui.classe_actuelle_id,self.ui.annee_academique_id,self.ui.religion, self.ui.date_de_naissance, self.ui.lieu_de_naissance ,self.ui.nom_responsable,
    #         self.ui.prenom_responsable,
    #         self.ui.email_responsable,
    #         self.ui.sexe_responsable,
    #         self.ui.telephone_responsable,
    #         self.ui.adresse_responsable,
    #         self.ui.aide_financiere,
    #         )     
    #         self.documents.clear() 

    #         if self.ui.frame_40:
    #             layout = self.ui.widget_piece_inner.layout()
        
    #             for i in range(layout.count()):
    #                 widget = layout.itemAt(i).widget()
    #                 if widget == self.ui.frame_40:
    #                     layout.removeWidget(widget)
    #                     widget.deleteLater()
    #                     break 
    #         QMessageBox.information(None, "Success", f"{response.get('success')}")
        
    #         # self.api_handler_.all_student_()      
    #         self.overlay.finish_loading()        

    def imprimer_fiche_inscription(self):
        self.overlay.start_loading("Fiche d'inscription")

        recu = self.api_handler_.student_print_recu_inscrit(self.ui.student_id.text())
 


    # def imprimer_direct_fiche_inscrit(self, data):
    #     try:             
    #         # env = Environment(
    #         #         loader=FileSystemLoader("templates"),
    #                 # auto_reload=True,
    #                 # cache_size=0,  # 👈 pas de cache
    #                 # enable_async=True,
    #                 # extensions=['jinja2.ext.loopcontrols']
    #         #     )
    #         # template = env.get_template("inscrit.html")
             
    #         # rendered_html = template.render(
    #         #     info=self.config_data['data'],
    #         #     data_student=data['data_student'],
                
    #         #     date=data['date'],
    #         #     recu=data['recu'], 

    #         # ) 
    #         datas ={
    #               'info':self.config_data['data'],
    #             'data_student':data['data_student'],
                
    #             'date':data['date'],
    #             'recu':data['recu'], 
    #         }
    #         self.run_async_direct_pdf(self.generate_direct_pdf,"inscrit.html", datas)

    #         # HTML(string=rendered_html, base_url=".").write_pdf(
    #         #     "students_list.pdf",
    #         #     stylesheets=[CSS(string='''
    #         #         @page { size: A4; margin: 15mm; }
    #         #         body { font-family: "Times New Roman", serif; }
    #         #     ''')]
    #         # )
            
    #         # os.startfile("students_list.pdf") 
    #         # self.overlay.finish_loading()
    #     except Exception as e:
    #         print(e)
    #         import traceback
    #         traceback.print_exc()
    #         self.overlay.finish_loading()



    def imprimer_fiche_inscription1(self):
        self.overlay.start_loading()
        recu = self.api_handler_.student_print_recu_inscrit(self.ui.student_id.text())
 
    def convertir_image_en_base64(self,chemin_image):
        """Convertit une image en Base64"""
        with open(chemin_image, "rb") as image_file:
            image_data = image_file.read()
        
            encoded_string = base64.b64encode(image_data).decode("utf-8", errors="ignore")  # Ignorer erreurs d'encodage
            extension = chemin_image.split('.')[-1].lower()
            # print(f"data:image/{extension};base64,{encoded_string}")

        return f"data:image/{extension};base64,{encoded_string}"
     
# ==============================enregistre les etudiant============================================
    def toggle_show_students(self, checked):
        if checked:
            self.ui.frame_2.setHidden(False)
            self.ui.frame_chart_408.setHidden(True)
            self.show_student_number_in_classes()
            # self.ui.btn_plus_classe.setText("Masquer les élèves")
        else:
            self.ui.frame_chart_408.setHidden(False)
            self.ui.frame_2.setHidden(True)
            # self.hide_student_number_in_classes()
            # self.ui.btn_plus_classe.setText("Afficher les élèves")

    def show_student_number_in_classes(self):    
        header = ("Id", "Niveau / Cycle", "Classe", "Nb Eleve", "Prof")
        self.all_headers_table_labels(
            self.ui.table_show_number_student, header, "#e2e8f0", 32, 250, 250, 250, 250)
        self.ui.table_show_number_student.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        classeDetails = self.all_dash_data
        
        if classeDetails:
            colonnes_ordre = ["classe_id", "niveau_name", "nom_classe", "etudiant_count", "professeur"]

            self.select_all_populate(classeDetails['classeDetails'],self.ui.table_show_number_student, self.on_row_clicked_class_show,colonnes_ordre)


    def on_row_clicked_class_show(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_show_number_student.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            data = self.api_handler_.student_with_classe(id_item.text(),annee_id=self.ui.combo_anne_for_dash.currentData()) 
        else:
            print("not item")

    def filter_items(self,text, combo, data):
        combo.clear()
        for item in data:
            fullName = f"{item.get('nom','')}  {item.get('prenom','')}" 
            if text.lower() in item.get('nom','').lower() or text.lower() in item.get('prenom','').lower():
                combo.addItem(fullName,item.get('id',''))
             

    # def on_row_clicked_class_show(self, row, column):
    #     """Récupère l'ID de la ligne cliquée"""
    #     id_item = self.ui.table_show_number_student.item(row, 0)  # Colonne 0 = ID
    #     if id_item: 
    #         data = self.fetch_data_.student_with_classe(id_item.text())
    #         print(data)
    #         if data:
    #             self.dialog_ = QDialog()
    #             self.dialog_.setModal(True)  
    #             self.dialog_.setFixedSize(850, 600)
    #             self.email_button = QPushButton("Envoyer un email")
    #             self.email_button.clicked.connect(self.write_on_group_student)
    #             self.dialog_.setWindowTitle("Liste des élèves de la classe")
    #             frame_button = QFrame()
    #             button_layout = QVBoxLayout(frame_button)
    #             button_layout.addWidget(self.email_button)
    #             layout = QVBoxLayout()
    #             layout.setContentsMargins(0,0,0,0)
    #             self.table_show = QTableWidget()                

    #             # self.ui.frame_3.setHidden(True)
    #             # header = ("Id", "Identifiant", "Nom","Prénom", "Sexe", 'Actif')
    #             header = ("Id", "Identifiant", "Nom", "Prénom", "Sexe", "id_cls_etudiant", "status_cls_etudiant", "Actif")

        
    #             self.all_headers_table_labels(
    #                 self.table_show, header, "#e2e8f0", 32, 210, 210, 210, 50, 50,50,50)
    #             self.table_show.setSelectionBehavior(QAbstractItemView.SelectRows)
                
    #             # colonnes_ordre = ["id", "identifiant", "nom", "prenom", "sexe", "id_cls_etudiant", "status_cls_etudiant"]
    #             # if data:
    #             # colonnes_ordre = ["id", "identifiant", "nom", "prenom", "sexe"]
    #             # self.table_show.setColumnHidden(6, True)  # id_cls_etudiant
    #             # self.table_show.setColumnHidden(7, True)  # status_cls_etudiant

    #             self.select_all_populate(data['data'],self.table_show, self.on_row_clicked_Show)

    #             row_count = self.table_show.rowCount()
    #             for row in range(row_count):
    #                 status_item = self.table_show.item(row, 6)  # index 7 = colonne status_cls_etudiant
    #                 checkbox = QCheckBox()

    #                 # Vérifie si status = 1 pour cocher
    #                 if status_item and status_item.text() == "1":
    #                     checkbox.setChecked(True)

    #                 # Connecter avec ID unique de classe_etudiant (colonne 6)
    #                 status_cls_item_status = self.table_show.item(row, 5)
    #                 if status_cls_item_status:
    #                     cls_status = status_cls_item_status.text()
    #                     checkbox.stateChanged.connect(
    #                         lambda state, r=row, cls_status=cls_status: self.update_student_status(cls_status, state)
    #                     )
    #                 # checkbox.setStyleSheet("""
    #                 # QCheckBox {
    #                 #     max-width: 13px;
    #                 #     border: 1px solid #40C057;
    #                 #     border-radius: 4px;
    #                 #     padding-left: 18px; 
    #                 #     padding-right: 0px
    #                 # }
    #                 # QCheckBox::indicator {
    #                 #     width: 13px;
    #                 #     height: 13px;
    #                 #     border: 1px solid #40C057;
    #                 #     border-radius: 4px;
    #                 #     background-color: white;
    #                 # }
    #                 # QCheckBox::indicator:checked {
    #                 #     background-color: #40C057;
    #                 #     border: 1px solid #40C057;
    #                 # }
    #                 # """)

    #                 # checkbox.repaint() 

    #                 # Ajouter le checkbox à la cellule
    #                 cell_widget = QWidget()
    #                 layout_cb = QHBoxLayout(cell_widget)
    #                 layout_cb.addWidget()
    #                 layout_cb.setAlignment(Qt.AlignCenter)
    #                 layout_cb.setContentsMargins(0, 0, 0, 0)
    #                 self.table_show.setCellWidget(row, 7, cell_widget)  


    #             layout.addWidget(frame_button)
    #             layout.addWidget(self.table_show)
    #             self.dialog_.setLayout(layout)
    #             self.dialog_.exec()

    # def update_student_status(self, classe_etudiant_id, state):
    #     print(state)checkbox
    #     msg = QMessageBox(None)
    #     msg.setIcon(QMessageBox.Question)
    #     msg.setWindowTitle("Confirmation")
    #     msg.setText("Voulez-vous vraiment changer le statut de l'élève ?")
    #     msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #     msg.setDefaultButton(QMessageBox.No)

    #     reponse = msg.exec_()

    #     if reponse == QMessageBox.Yes:
    #         new_status = 1 if state == Qt.Checked else 0
    #         print(f"ID classe_etudiant: {classe_etudiant_id}, nouveau statut: {new_status}")
    #         response = self.fetch_data_.update_student_status_classe(classe_etudiant_id, new_status)
    #         print(response)
    #         if response and 'success' in response:
    #             return True
    #     else:
    #         return False




    # def update_student_status(self, row, state):
    #     id_item = self.table_show.item(row, 0)  # ID supposé en colonne 0
    #     if id_item:
    #         student_id = id_item.text()
    #         new_status = 1 if state == Qt.Checked else 0
    #         # Ici, vous devriez appeler une fonction de votre couche base de données
    #         self.fetch_data_.update_student_status_classe(student_id, new_status)
    #         print(f"Statut de l'étudiant ID {student_id} mis à jour à {new_status}")

    def update_student_status(self, classe_etudiant_id, state, delete=False):
        # self.start_lo
        new_status = 1 if state == Qt.Checked else 0       

        response = self.api_handler_.update_student_status_classe(classe_etudiant_id, new_status, delete)





    def on_row_clicked_Show(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.table_show.item(row, 0)  # Colonne 0 = ID
        if id_item:
            try:
                self.overlay.start_loading()
# 
                self.ui.frame_3.setHidden(False)
                # print(id_item.text(), self.table_show.item(row, 1).text())
                if self.all_students_data:
                    show_student = next((item for item in self.all_students_data['data'] if item['id'] == id_item.text()), None)
                    self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)
                    self.fancy_modal_show(self.ui.add_student_page)
                    self.add_student_page(show_student)
                    self.overlay.finish_loading() 
                else:
                    show_student = self.api_handler_.student_show(id_item.text())
                # self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)
                # self.add_student_page(show_student) 
                # self.dialog_.close()
                # print(f"show_student in show \n\n {show_student}")
            except Exception as e:
              print(f'An exception occurred {e}')

    def request_access_for_delete(self, permission=None):
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

            self.icon_path_lock = self.get_path(os.path.join('assets', 'icons', 'lock.png'))
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
            self.permission_direct_name = permission

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
            self.layout_buttons.setContentsMargins(0,10,0,25)

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
            self.fancy_modal_show(self.dialog_delete)
            self.dialog_delete.exec()
        except:
          print('An exception occurred')


    def authorisation_status(self):
        email = self.input_email.text()
        password = self.password_input.text()
        response = self.api_handler_.authorisation_request(email=email, password=password, permission=self.permissions_delete)
        


    def write_on_group_student(self):
        self.dialog_email = QDialog()
        self.dialog_email.setModal(True)  
        self.dialog_email.setFixedSize(850, 600)
        self.email_button = QPushButton("Envoyer un email")
        self.email_button.clicked.connect(self.write_on_group_student)
        self.dialog_email.setWindowTitle("Liste des élèves de la classe")
        frame_button = QFrame()
        button_layout = QVBoxLayout(frame_button)
        button_layout.addWidget(self.email_button)
        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)                

        layout.addWidget(frame_button)
        layout.addWidget(self.table_show)
        self.dialog_.setLayout(layout)
        self.dialog_.exec()

    def dash_page(self): 
        # self.restart_disconnect_timer()
        self.overlay.start_loading(f"Chargement des données")
        self.ui.combo_anne_for_dash.setStyleSheet("""
            QComboBox{ width: 200px; min-height: 20px; max-height: 20px; height:20px; border:none}
            """)
        self.ui.frame_350.setHidden(False)
        self.ui.frame_408.setHidden(True)
        self.ui.user_email.setText(self.token_manager.get_user_email())
        # data_for_dashbord()
        self.all_dash_data.clear() 
 
        self.api_handler_.data_for_dashbord()
        self.overlay.finish_loading()
        # self.ajouter_dashboard(self.ui.frame_chart)
        self.ui.stackedWidget.setCurrentWidget(self.ui.dash_page)
        self.fade_in_page(self.ui.dash_page)
        QTimer.singleShot(5, self.request_finished)


    def get_dash_data_by_date(self):
        self.all_dash_data.clear() 
        annee_ = self.ui.combo_anne_for_dash.currentData()
        self.all_dash_data.clear() 
 
        self.api_handler_.data_for_dashbord(search_term=annee_)

    def show_data_in_dash(self):
        data = self.all_dash_data 
        if 'admin' not in self.user_roles and 'Comptable' not in self.user_roles:
            self.ui.label_number_classe_dash.setText("********")
            self.ui.label_number_etudiant.setText("********")
            self.ui.label_number_paiement.setText(f"****** {data.get('devise', '')}")
            self.ui.label_number_cours.setText("********")
            self.ui.label_number_professeur.setText("********")
            self.ui.label_number_personnel.setText("********")
            self.ui.btn_plus_classe.setDisabled(True)
        else:  
            if self.all_dash_data is not None:  
                self.ui.btn_plus_classe.setEnabled(True)
                self.ui.label_number_classe_dash.setText(str(self.all_dash_data.get('classes', '')))
                self.ui.label_number_etudiant.setText(str(self.all_dash_data.get('etudiant', '')))
                self.ui.label_number_paiement.setText(f"{self.all_dash_data.get('paiement', '')} {self.all_dash_data.get('devise', '')}")
                self.ui.label_number_cours.setText(str(self.all_dash_data.get('classes', '')))
                self.ui.label_number_professeur.setText(str(self.all_dash_data.get('professeur', '')))
                self.ui.label_number_personnel.setText(str(self.all_dash_data.get('personnel', '')))

                self.fill_commbo_with_data(self.ui.combo_anne_for_dash,self.all_dash_data.get("id_annee","")) 
        self.overlay.finish_loading()


# ==============================================__ADMINISTRATION__====================================

    def admin_page(self): 
        # self.restart_disconnect_timer()
        self.overlay.start_loading("Chargement des Personnels")  
        self.ui.frame_350.setHidden(True)  
        self.ui.frame_408.setHidden(True)    
        self.id_admin_for_update = QLineEdit()
        
                
        self.set_table_refresh_data_admin()
        self.go_to_page_admin(self.current_page_admin)
        self.ui.stackedWidget.setCurrentWidget(self.ui.admin_page)
        self.ui.admin_stacked.setCurrentWidget(self.ui.index_admin)
        self.fade_in_page(self.ui.index_admin)
        # QTimer.singleShot(5, self.request_finished)
        # self.ui.titre_toggle.setText("Admin")

    def active_personnel(self):
        self.overlay.start_loading("Activation de personnel")
        id = self.id_admin_for_update.text()

        result = self.api_handler_.active_personnel(id=id) 


    def go_to_page_admin(self, page):
        self.overlay.start_loading()
        self.current_page_admin = page 

        self.api_handler_.all_admin(self.ui.search_admin.text(), page)

    def restart_timer_admin(self):
        self.search_timer_admin.start(300)

    def sauvegarder_admin(self):
        self.overlay.start_loading("Enregistrement de personnel") 
        id = self.id_admin_for_update.text()
        nom = self.ui.admin_nom.text()
        telephone = self.ui.admin_telephone.text()
        prenom = self.ui.admin_prenom.text()
        email = self.ui.admin_email.text()
        sexe = self.ui.admin_sexe.text()
        adresse = self.ui.admin_adresse.text()
        role = self.ui.admin_role.currentData()
        # role = self.role_selected

        response = self.api_handler_.enregistrer_admin(id=id,nom=nom,prenom=prenom, telephone=telephone, email=email,sexe=sexe,adresse=adresse,role=role)
        # print(response)
    # def show_result_after_save_admin(self, response_data,status):
    #     from Controllers.Validator import ValidatorError
    #     if response_data and 'errors' in response_data:
    #         self.overlay.finish_loading()
    #         ve = ValidatorError()
    #         ve.generic_direct_error_message(response_data=response_data) 
    #     else: 
    #         self.admin_page()
    #         self.id_admin_for_update.setText("") 
    #         self.clear_personnel()
    #         QMessageBox.information(self, "Success", f"{response_data.get('success','')}")
    #     QTimer.singleShot(200, self.overlay.finish_loading)
  
    def clear_personnel(self):
        self.clear_fields(
                self.ui.admin_nom,
                self.ui.admin_telephone,
                self.ui.admin_prenom,
                self.ui.admin_email,
                self.ui.admin_sexe,
                self.ui.admin_adresse,
                self.ui.admin_role  
            )


    def add_personnel(self, personnel=None):
        # self.overlay.start_loading()
        self.clear_personnel()
        roles = self.fetch_data_roles # or  
        for role in roles:
            self.ui.admin_role.addItem(role.get('name',''), role.get('id',''))

        self.ui.enregistrer_admin.setText("Enregistrer")
        self.ui.delete_admin.setHidden(True)
        self.ui.frame_305.setHidden(True)
        if personnel:
            self.ui.frame_305.setHidden(False)
            self.ui.delete_admin.setHidden(False)
            self.ui.enregistrer_admin.setText("Modifier")
            self.id_admin_for_update.setText(str(personnel.get("id","")))
            self.ui.admin_nom.setText(str(personnel.get("nom","")))
            self.ui.admin_telephone.setText(str(personnel.get("telephone","")))
            self.ui.admin_prenom.setText(str(personnel.get("prenom","")))
            self.ui.admin_email.setText(str(personnel.get("email","")))
            self.ui.admin_sexe.setText(str(personnel.get("sexe","")))
            self.ui.admin_adresse.setText(str(personnel.get("adresse","")))


            if 'user' in personnel:
                user = personnel.get("user")
                print(user)
                if isinstance(user, dict):
                    is_active = user.get("status")
                    is_active_bool = str(is_active) == '1'
                    
                    status = "Active" if is_active_bool else "Inactive"
                    button_text = "Desactiver" if is_active_bool else "Activer"
                else:
                    is_active_bool = False
                    status = "Inactive"
                    button_text = "Activer"

                self.ui.admin_status.setText(status)
                self.ui.admin_change_status.setText(button_text)

                if is_active_bool:
                    self.ui.admin_status.setStyleSheet("""
                        QLabel {
                            color: green;
                            font-weight: bold;
                        }
                    """)
                    self.ui.admin_change_status.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;  /* Rouge clair */
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                else:
                    self.ui.admin_status.setStyleSheet("""
                        QLabel {
                            color: red;
                            font-weight: bold;
                        }
                    """)
                    self.ui.admin_change_status.setStyleSheet("""
                        QPushButton {
                            background-color: #4caf50;  /* Vert clair */
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #388e3c;
                        }
                    """)
            
        # self.overlay.start_loading()
        self.overlay.finish_loading()
        self.fancy_modal_show(self.ui.add_admin)
        self.ui.admin_stacked.setCurrentWidget(self.ui.add_admin) 

 
    def delete_personnel(self):
        self.overlay.start_loading()
        id = self.id_admin_for_update.text()
        reply_delete_admin = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer  ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply_delete_admin == QMessageBox.Yes:
            result = self.api_handler_.delete_perso(id)
            
        self.overlay.finish_loading()
    
    def delete_student(self):
        self.overlay.start_loading()
        id = self.ui.student_id.text()
        reply_delete_admin = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer  ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply_delete_admin == QMessageBox.Yes:
            result = self.api_handler_.delete_student(id)
            # if result and 'success' in result:
            #     # self.load_all_personnel()
                # self.admin_page()
                # self.clear_personnel()
            # else:
            #     QMessageBox.warning(None, "Avertissement", "erreur")
        # self.overlay.start_loading()
        self.overlay.finish_loading()


    def set_table_refresh_data_admin(self, page=1):
        header = ("Id", "Nom", "prénom", "Sexe", 
                  "Email", "Téléphone",'Adresse', 'Status')
        self.all_headers_table_labels(
            self.ui.admin_table, header,  "#e2e8f0", 32, 130, 150, 20, 250, 115, 180, 60)
        self.ui.admin_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)  

        colonnes_ordre = ["id", "nom", "prenom", "sexe", "email", "telephone",'adresse','status_']

        if self.all_personnels_data:
            query = self.ui.search_admin.text() #.strip()
            if query:
                filtered_data = [
                    item for item in self.all_personnels_data['data']
                    if query.lower() in item['nom'].lower()
                    or query.lower() in item['prenom'].lower()
                    or query.lower() in item['email'].lower()
                ]
                data_to_display = filtered_data 
            else:

                self.current_page_admin = page
                data_per_page = 16  
                all_data = self.all_personnels_data['data']
                self.total_pages_admin = max(1, (len(all_data) + data_per_page - 1) // data_per_page)

                start_index = (page - 1) * data_per_page
                end_index = start_index + data_per_page
                data_to_display = all_data[start_index:end_index]

            self.select_all_populate(data_to_display, self.ui.admin_table, self.on_row_clicked_admin, _ordre=colonnes_ordre)
        else:
            if self.is_data_updating:
                return 
            self.is_data_updating = True

            try:
                # table = self.api_handler_.all_admin(self.ui.search_admin.text(), page)

                if self.all_personnel_data:
                    meta = self.all_personnel_data.get("meta", "")

                    self.current_page_admin = meta.get("current_page",1)
                    self.total_pages_admin = meta.get("last_page",1)

                    self.ui.admin_prev.setEnabled(self.current_page_admin > 1)
                    self.ui.admin_next.setEnabled(self.current_page_admin < self.total_pages_admin)

                    self.ui.admin_next.setText('Suivant')
                    self.ui.admin_prev.setText('Précédent')

                    self.ui.admin_prev.setStyleSheet("""
                        QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                        QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc; padding: 5px 10px; }
                    """)

                    self.ui.admin_next.setStyleSheet("""
                        QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                        QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc; padding: 5px 10px; }
                    """)
        
                    self.select_all_populate(self.all_personnel_data.get('data',''), self.ui.admin_table, self.on_row_clicked_admin,_ordre=colonnes_ordre) 
            except:
                print('Something went wrong')
            finally: 
                self.is_data_updating = False

    

    def on_row_clicked_admin(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.admin_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            self.overlay.start_loading() 

            show_admin = self.api_handler_.admin_show(id_item.text())
            
            return 
        
    def admin_next(self):
        if self.current_page_admin < self.total_pages_admin:
            self.go_to_page_admin(page=self.current_page_admin + 1)

    def admin_prev(self):
        if self.current_page_admin > 1:
            self.go_to_page_admin(page=self.current_page_admin - 1)

# ============================================== __ADMINISTRATION__====================================



# ================================================== __ETUDIANT__ ======================================
    def etudiant_page(self): 
        # self.restart_disconnect_timer()
        self.overlay.start_loading() 
        self.ui.frame_350.setHidden(True)  
        self.ui.frame_408.setHidden(True)     
        self.set_table_refresh_data_student()
        self.ui.date_de_naissance.setMaximumDate(QDate.currentDate())
        self.go_to_student_page(self.current_page_student) 
        self.ui.stackedWidget.setCurrentWidget(self.ui.etudiant_page)
        self.ui.stackedStudent.setCurrentWidget(self.ui.index_student) 
        self.fade_in_page(self.ui.index_student)

        self.clear_fields( self.ui.nom, self.ui.prenom, self.ui.telephone, self.ui.email_3,self.ui.sexe, self.ui.adresse,self.ui.niveau_id,self.ui.classe_actuelle_id,self.ui.annee_academique_id,self.ui.religion, self.ui.date_de_naissance, self.ui.lieu_de_naissance,self.ui.student_id  # QComboBox
        )

    def restart_timer(self):
        self.search_timer_student.start(300)

    def modifier_etudiant_page(self):
        self.overlay.start_loading()
        self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)  
        self.ui.tabWidget.setCurrentWidget(self.ui.personnel_info)  
        self.fancy_modal_show(self.ui.personnel_info)
        self.ui.enregistre.setText('Modifier')
        self.overlay.finish_loading()
        # self.ui.titre_toggle.setText("Modifier Etudiant")
    
    def print_student_details(self):
        self.overlay.start_loading()
        self.api_handler_.student_print_details(self.ui.student_id.text())
     

    def set_table_refresh_data_for_live_search_student(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        if(self.ui.search_student_for_detail.text() == ''):
            self.ui.widget_search_student.setHidden(True)

        header = ("Id", "Identifiant", "Nom", "prénom")
        self.all_headers_table_labels(
            self.ui.tableWidget, header,  "#e2e8f0", 0, 150, 200, 200)
        self.ui.tableWidget.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        # self.api_handler_.student_live(self.ui.search_for_card.text()) 

        # if data and 'data' in data and len(data['data']) > 0:
        #     self.ui.tableWidget.setRowCount(len(data['data'])) 
        #     self.ui.widget_search_student.setHidden(False)
        #     self.ui.frame_171.setHidden(True)
        #     self.ui.frame_195.setHidden(True)
        #     for row_idx, row_data in enumerate(data['data']):
        #         for col_idx, value in enumerate(row_data):
        #             self.ui.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
        #     self.ui.tableWidget.cellClicked.connect(self.on_row_clicked_live_search_student)
        # else:
        #     self.ui.tableWidget.setRowCount(0)
        #     self.ui.widget_search_student.setHidden(True)
        #     self.ui.frame_171.setHidden(False)
        #     self.ui.frame_195.setHidden(False)

    def on_row_clicked_live_search_student(self, row,column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.tableWidget.item(row, 0)
        if id_item:
            if self.all_students_data:
                show_student = next((item for item in self.all_students_data['data'] if item['id'] == id_item.text()), None)
            else:
                show_student = self.api_handler_.student_show(id_item.text())
            # self.add_student_page(show_student)
            # self.ui.search_student_for_detail.setText('')
            # self.ui.frame_171.setHidden(False)
            # self.ui.frame_195.setHidden(False)
            


    def set_table_refresh_data_student(self):
        header = ("Id", "Identifiant", "Nom", "prénom", "Sexe", "Date de Naissance",
                "Email", "Téléphone")
        
        self.all_headers_table_labels(
            self.ui.student_table, header, "#e2e8f0", 32, 130, 110, 165, 40, 155, 190, 100, 100)
        self.ui.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)


        
        if self.all_etudiant_data:
            self.current_page_student =  self.all_etudiant_data.get("meta", {}).get("current_page", 1)
            self.total_pages_student =  self.all_etudiant_data.get("meta", {}).get("last_page", 1) 

            self.ui.prev_page_student.setEnabled(self.current_page_student > 1)
            self.ui.next_page_student.setEnabled(self.current_page_student < self.total_pages_student)

            self.ui.prev_page_student.setStyleSheet("""
                QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_page_student.setStyleSheet("""
                QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            colonnes_ordre = ["id", "identifiant", "nom", "prenom", "sexe", "_naissance", "email", "telephone"]
            self.select_all_populate(self.all_etudiant_data['data'],self.ui.student_table, self.on_row_clicked,colonnes_ordre) 
        # except:
        #     print('Something went wrong')
        # finally: 
        #     self.is_data_updating = False

        # self.overlay.finish_loading()
        # Styles des boutons

    def go_to_student_page(self, page):
        self.overlay.start_loading(f"Elève page {self.current_page_student}")
        self.current_page_student = page
        search_term = self.ui.sesrch_student.text()  
        
        self.api_handler_.all_student(self.ui.sesrch_student.text(), page)
        

    def btn_importer_exel(self):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """ 
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.word *.exel, *.json)")

    def diplome_page(self):
       self.set_table_refresh_search_for_deplome_()
       self.ui.stackedStudent.setCurrentWidget(self.ui.diplome_page) 
       self.fancy_modal_show(self.ui.diplome_page)

    def set_table_refresh_search_for_deplome_(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche.""" 

        header = ("Id", "Identifiant", "Nom", "prénom")
        self.all_headers_table_labels(
            self.ui.diplome_table, header,  "#e2e8f0", 0, 100, 200, 200)
        self.ui.diplome_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        self.api_handler_.student_live(self.ui.search_for_card.text())     
            # self.api_handler_.student_live(self.ui.search_for_deplome.text()) 
        data = self.live_search_student    
        if data and 'data' in data and len(data['data']) > 0:
            self.ui.diplome_table.setRowCount(len(data['data']))  
            for row_idx, row_data in enumerate(data['data']):
                for col_idx, value in enumerate(row_data):
                    self.ui.diplome_table.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
            self.ui.diplome_table.cellClicked.connect(self.on_row_clicked_live_search_)
        else:
            self.ui.diplome_table.setRowCount(0)

    def certificat_page(self):
       self.set_table_refresh_search_for_certificat_()
       self.ui.stackedStudent.setCurrentWidget(self.ui.certificat_page) 
       self.fancy_modal_show(self.ui.certificat_page)  

    def set_table_refresh_search_for_certificat_(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        # if(self.ui.search_for_card.text() == ''):
        #     self.ui.tableWidget_2.setHidden(True)

        header = ("Id", "Identifiant", "Nom", "prénom")
        self.all_headers_table_labels(
            self.ui.certificat_table, header,  "#e2e8f0", 0, 100, 200, 200)
        self.ui.certificat_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
      
        self.api_handler_.student_live(self.ui.search_for_card.text())        
            # self.api_handler_.student_live(self.ui.search_for_certificat.text()) 
        data = self.live_search_student    
        if data and 'data' in data and len(data['data']) > 0:
            self.ui.certificat_table.setRowCount(len(data['data']))  
            for row_idx, row_data in enumerate(data['data']):
                for col_idx, value in enumerate(row_data):
                    self.ui.certificat_table.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
            self.ui.certificat_table.cellClicked.connect(self.on_row_clicked_live_search_)
        else:
            self.ui.certificat_table.setRowCount(0)


    def add_student_page(self, show_student=None): 
        self.overlay.start_loading()
        self.api_handler_.get_all_faculte()
        self.ui.faculte_id.setHidden(True)
        self.ui.aide_financiere.clear()
        self.ui.aide_financiere.addItems(['Aucune','1/4 Bourse', 'Démie Bourse', 'Bourse'])
        self.ui.annee_academique_id.clear()
        self.ui.niveau_id.clear()
        

        self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)  
        self.ui.tabWidget.setCurrentWidget(self.ui.details) 
        self.fade_in_page(self.ui.details)
        
        for niveau in self.niveaux:
            self.ui.niveau_id.addItem(niveau.get('name',""), niveau.get('id',"")) 
 
        for annee_acade in self.annee_acades:
            self.ui.annee_academique_id.addItem(annee_acade['annee_academique'], annee_acade['id'])
        self.ui.enregistre.setText('Enregistrer')

        if self.ui.frame_40:
            layout = self.ui.widget_piece_inner.layout()
    
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if widget == self.ui.frame_40:
                    layout.removeWidget(widget)
                    widget.deleteLater()
                    break

        def update_classes():
            level_id = self.ui.niveau_id.currentData()
            self.ui.classe_actuelle_id.clear() 
            # self.ui.classe_actuelle_id.addItem(classe.get('nom_classe'), classe.get('id')) 
            filtered = [c for c in self.classes_combo if c.get('niveau_id') == level_id]
            for c in filtered:
                self.ui.classe_actuelle_id.addItem(c.get("nom_classe",""), c.get("id",""))

            self.ui.faculte_id.clear()
            for faculte in self.get_facultes:
                self.ui.faculte_id.addItem(faculte.get('nom'), faculte.get('id'))

        self.ui.niveau_id.currentIndexChanged.connect(update_classes)
        self.ui.student_id.setHidden(True)
        try:
            if show_student: 
                self.ui.widget_search_student.setHidden(True)
                parcours_layout = self.ui.widget_parcours.layout()
                if parcours_layout:
                    self.clear_layout(parcours_layout)
                else:
                    v_box_frame = QFrame()
                    self.v_box_parcours = QVBoxLayout(v_box_frame)
                    self.ui.widget_parcours.setLayout(self.v_box_parcours)

                icon_path_prev = os.path.join(self.project_dir, 'assets', 'icons', 'prev.png')          

                self.ui.back_to_details.setIcon(QIcon(icon_path_prev))

                self.ui.nom.setText(show_student['nom'])
                self.ui.prenom.setText(show_student['prenom'])
                self.fill_combo_box(self.ui.sexe, str(show_student['sexe']))
                self.ui.telephone.setText(show_student['telephone'])
                self.ui.adresse.setText(show_student['adresse'])   
                self.ui.lieu_de_naissance.setText(show_student['lieu_de_naissance'])
                self.ui.religion.setText(show_student['religion'])
                self.ui.email_3.setText(show_student['email'])
                self.ui.student_id.setText(show_student['id'])
                self.fill_combo_box(self.ui.aide_financiere, str(show_student['aide_financiere']))
                

                # date_str = show_student['date_de_naissance']  # Exemple : '2002-05-14'
                date_str = show_student.get('date_de_naissance')  # Exemple : '2019-09-01'
                date_obj = QDate.fromString(date_str, "yyyy-MM-dd")

                # # Appliquer la date
                self.ui.date_de_naissance.setDate(date_obj)
            
                self.ui.date_de_naissance.setDisplayFormat("dd/MM/yyyy")
                


                # information details
                self.ui.label_101.setText(str(show_student['identifiant']))
                self.ui.label_103.setText(str(show_student['nom']))
                self.ui.label_105.setText(str(show_student['prenom']))
                self.ui.label_115.setText(str(show_student['sexe']))
                self.ui.label_113.setText(str(show_student['_naissance']))
                self.ui.label_107.setText(str(show_student['adresse']))
                self.ui.label_109.setText(str(show_student['email']))
                self.ui.label_111.setText(str(show_student['telephone']))
                self.ui.label_117.setText(str(show_student['lieu_de_naissance']))
                
                # self.ui.label_73.setText(str(show_student['nom']))
                
                # show_student['responsable']=
                self.ui.email_responsable.setText('')
                self.ui.nom_responsable.setText('')
                self.ui.prenom_responsable.setText('')
                self.ui.adresse_responsable.setText('')
                self.ui.telephone_responsable.setText('')
                self.ui.sexe_responsable.setText('')
                self.ui.label_97.setText('--- ---')
                self.ui.label_99.setText('--- ---')
                self.ui.label_91.setText('--- ---')
                self.ui.label_93.setText('--- ---')
                self.ui.label_95.setText('--- ---')

                if show_student['responsable']:
                    self.ui.email_responsable.setText(show_student['responsable'].get('email_responsable',''))
                    self.ui.nom_responsable.setText(show_student['responsable'].get('nom_responsable',''))
                    self.ui.prenom_responsable.setText(show_student['responsable'].get('prenom_responsable',''))
                    self.ui.adresse_responsable.setText(show_student['responsable'].get('adresse_responsable',''))
                    self.ui.telephone_responsable.setText(show_student['responsable'].get('telephone_responsable',''))
                    self.ui.sexe_responsable.setText(show_student['responsable'].get('sexe_responsable',''))

                    self.ui.label_97.setText(str(show_student['responsable'].get('nom_responsable','')))
                    self.ui.label_99.setText(str(show_student['responsable'].get('prenom_responsable','')))
                    self.ui.label_91.setText(str(show_student['responsable'].get('adresse_responsable','')))
                    self.ui.label_93.setText(str(show_student['responsable'].get('email_responsable','')))
                    self.ui.label_95.setText(str(show_student['responsable'].get('telephone_responsable','')))
               
                if show_student.get('classes_etudiant'):                    
                    if show_student['classes_etudiant'][-1]['niveaux']:
                        niveau_name = show_student['classes_etudiant'][-1]['niveaux']['name']  
                        self.fill_combo_box(self.ui.niveau_id, str(niveau_name))

                    if show_student['classes_etudiant'][-1]['classes']:
                        nom_classe = show_student['classes_etudiant'][-1]['classes']['nom_classe'] 
                        
                        self.ui.label_158.setText(str(nom_classe))
                        self.fill_combo_box(self.ui.classe_actuelle_id, str(nom_classe))

                    if show_student['classes_etudiant'][-1]['annee_academiques']:
                        annee_academique = show_student['classes_etudiant'][-1]['annee_academiques']['annee_academique']                      
                        self.fill_combo_box(self.ui.annee_academique_id, str(annee_academique))

                    self.populate_student_history(show_student,'classes_etudiant')
                    for parcours in  show_student['classes_etudiant']:
                        frame_date = QFrame()
                        layout = QHBoxLayout(frame_date)
                        details_layout = QVBoxLayout()
                        student_id=show_student.get('id')
                        classe_id=parcours.get("classes").get("id")
                        annee_id=parcours.get("annee_academiques").get("id")
                        button_date = QPushButton(parcours['annee_academiques']['annee_academique'])
                        button_date.clicked.connect(lambda _, classe=classe_id,student_=student_id,annee_=annee_id:self.get_student_details(classe,student_,annee_))
                        button_date.setFlat(True)
                        button_date.setCheckable(True)
                        button_date.setAutoExclusive(True)
                        button_date.setStyleSheet("""
                                QPushButton {
                                    padding: 5px;
                                    text-align: center;
                                    max-width: 130px;
                                    border-radius: 5px;
                                    font-size: 14pt; font-weight:bold;
                                    border: 1px solid #bbb;
                                    background: white;
                                    color: #999;
                                }
                                QPushButton:hover {
                                    background: #40af5d;
                                                border:1px solid #40af5d;
                                    color: white;
                                }
                            
                                QPushButton:checked{ 
                                    background: #40af5d;
                                    border:1px solid #40af5d;
                                    color: white;
                                                }
                            """)
                        # layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        # layout.addWidget(button_date)  



                        # self.v_box_parcours.addWidget(frame_date)
                        # self.v_box_parcours.update()
    

                if show_student.get('etudiant_facultes'):
                    print(show_student)
                    if show_student['etudiant_facultes'][-1]['niveaux']:
                        niveau_name = show_student['etudiant_facultes'][-1]['niveaux']['name']  
                        self.fill_combo_box(self.ui.niveau_id, str(niveau_name))
                        
                        self.selection_changed_niveau(self.ui.niveau_id.currentIndex())

                    if show_student['etudiant_facultes'][-1]['classes']:
                        nom_classe = show_student['etudiant_facultes'][-1]['classes']['nom_classe'] 
                        self.selection_changed_niveau(self.ui.niveau_id.currentIndex())
                        self.fill_combo_box(self.ui.classe_actuelle_id, str(nom_classe))
                        self.ui.label_158.setText(str(nom_classe))

                    if show_student['etudiant_facultes'][-1]['annee_academiques']:
                        annee_academique = show_student['etudiant_facultes'][-1]['annee_academiques']['annee_academique']                      
                        self.fill_combo_box(self.ui.annee_academique_id, str(annee_academique))

                    self.populate_student_history(show_student,'etudiant_facultes')
                    for parcours in  show_student['etudiant_facultes']:
                        frame_date = QFrame()
                        layout = QHBoxLayout(frame_date)
                        # button_date = QPushButton('ufgehorgheog')
                        button_date = QPushButton(parcours['annee_academiques']['annee_academique'])
                        button_date.setFlat(True)
                        button_date.setCheckable(True)
                        button_date.setAutoExclusive(True)
                        button_date.setStyleSheet("""
                                QPushButton {
                                    padding: 5px;
                                    text-align: center;
                                    max-width: 130px;
                                    border-radius: 5px;
                                    font-size: 14pt; font-weight:bold;
                                    border: 1px solid #bbb;
                                    background: white;
                                    color: #999;
                                }
                                QPushButton:hover {
                                    background: #40af5d;
                                                border:1px solid #40af5d;
                                    color: white;
                                }
                            
                                QPushButton:checked{ 
                                    background: #40af5d;
                                    border:1px solid #40af5d;
                                    color: white;
                                                }
                            """)
                        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        layout.addWidget(button_date)  


                        self.v_box_parcours.addWidget(frame_date)
                        self.v_box_parcours.update()

                # if show_student.get('etudiant_facultes'):  
                #     dernier_faculte = show_student['etudiant_facultes'][-1]

     
                self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)  
                self.ui.tabWidget.setCurrentWidget(self.ui.details)  
                # self.ui.titre_toggle.setText("Information")

            else:
                self.ui.back_to_details.setHidden(True)         

                self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)  
                self.ui.tabWidget.setCurrentWidget(self.ui.personnel_info)   
            self.overlay.finish_loading()
        except Exception as e:
            print("Erre=== :", e)
            import traceback
            traceback.print_exc()


    def clear_layout_with(self, layout, exclude=None):
        """Vide un layout en ignorant les widgets présents dans la liste 'exclude'"""
        if layout is not None:
            if exclude is None:
                exclude = []
                
            for i in reversed(range(layout.count())):
                item = layout.itemAt(i)
                widget = item.widget()
                
                if widget:
                    if widget not in exclude:
                        widget.setParent(None)
                        widget.deleteLater()
                elif item.layout():
                    # Si c'est un sous-layout, on le vide aussi
                    self.clear_layout_with(item.layout(), exclude)

    def populate_student_history(self, show_student, key): 
        # self.acad_container = QGroupBox("📊 Performance Académique")
        # self.acad_container.setVisible(False) 
        # self.layout_info_academique = QVBoxLayout(self.acad_container)
        # self.v_box_parcours.addWidget(self.acad_container)

        # self.fin_container = QGroupBox("💳 Situation Financière")
        # self.fin_container.setVisible(False) 
        # self.layout_info_financier = QVBoxLayout(self.fin_container)
        # self.v_box_parcours.addWidget(self.fin_container)

        # self.v_box_parcours.setSpacing(30)
 
        # 1. Création et Style de la Zone Académique
        # self.acad_container = QGroupBox("📊 Performance Académique")
        # self.acad_container.setVisible(False)
        # # Style : Couleur bleu ciel (#3498db ou SkyBlue) et espacement du titre
        # self.acad_container.setStyleSheet("""
        # QGroupBox {
        #         font-weight: bold;
        #         font-size: 12pt;
        #         border: none;
        #         margin-top: 15px; /* Espace pour le titre */
        #         background-color: transparent;
        #     }
        #     QGroupBox::title {
        #         subcontrol-origin: margin;
        #         subcontrol-position: top left;
        #         padding-left: 5px;
        #         color: #3498db; /* Bleu ciel */
        #     }
        # """)
        # self.layout_info_academique = QVBoxLayout(self.acad_container)
        # self.layout_info_academique.setContentsMargins(10, 25, 10, 10) # Espace sous le titre
        # self.v_box_parcours.addWidget(self.acad_container)

        # # 2. Création et Style de la Zone Financière
        # self.fin_container = QGroupBox("💳 Situation Financière")
        # self.fin_container.setVisible(False)
        # self.fin_container.setStyleSheet(self.acad_container.styleSheet()) # On réutilise le même style
        
        # self.layout_info_financier = QVBoxLayout(self.fin_container)
        # self.layout_info_financier.setContentsMargins(10, 25, 10, 10)
        # self.v_box_parcours.addWidget(self.fin_container)

        # 3. Espacement entre les blocs (Boutons, Académique, Financier)
        self.v_box_parcours.setSpacing(10)
 
        classes_annee = show_student.get(f'{key}', [])
        if not classes_annee:
            self.v_box_parcours.insertWidget(0, QLabel("Aucun historique trouvé."))
            return

        self.group_annee = QButtonGroup(self)
        self.group_annee.setExclusive(True) 

        # On identifie l'année la plus récente (Actuelle)
        id_annee_active = classes_annee[-1].get('annee_academiques', {}).get('id')
        button_to_click = None

        for parcours in classes_annee:
            annee_data = parcours.get("annee_academiques", {})
            classe_id = parcours.get("classes", {}).get("id")
            annee_id = annee_data.get("id")
            student_id = show_student.get('id')

            btn = QPushButton(annee_data.get('annee_academique'))
            btn.setCheckable(True)
            self.group_annee.addButton(btn)

            btn.setStyleSheet("""
                QPushButton {
                      padding: 5px; text-align: center;
                    max-width: 230px; min-width: 200px;
                    border-radius: 5px; font-size: 13pt;  
                    border: 1px solid #bbb; background: white; color: #999;
                }
                 QPushButton:hover, QPushButton:checked {
                    background: #40af5d; border: 1px solid #40af5d; color: white;padding: 7px;
                }
            """)

            # Si c'est l'année actuelle, on prépare le clic auto
            if annee_id == id_annee_active:
                btn.setText(f"⭐ {btn.text()} (Actuel)")
                button_to_click = btn

            btn.clicked.connect(lambda _, c=classe_id, s=student_id, a=annee_id: self.get_student_detail(c, s, a))
            
            # On insère les boutons AU-DESSUS des containers de détails
            self.v_box_parcours.insertWidget(self.v_box_parcours.count() - 2, btn)

        # 3. DECLENCHEMENT : Affiche l'année actuelle par défaut
        if button_to_click:
            button_to_click.click()

    def update_details_view222(self, data):
        """Re-génère les informations académiques et financières à chaque sélection"""

        for i in reversed(range(self.v_box_parcours.count())):
            widget = self.v_box_parcours.itemAt(i).widget()
            # On ne supprime que si c'est un GroupBox (nos containers) ou un Frame
            # Les QPushButton (tes boutons d'années) restent intacts !
            if isinstance(widget, (QGroupBox, QFrame)):
                widget.setParent(None)
                widget.deleteLater()

        # 2. CRÉATION DES CONTENEURS (Neufs)
        self.acad_container = QGroupBox("📊 Performance Académique")
        self.acad_container.setStyleSheet("""
            QGroupBox {
                font-weight: bold; font-size: 12pt; border: none;
                margin-top: 15px; background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin; subcontrol-position: top left;
                padding-left: 5px; color: #3498db;
            }
        """)
        self.layout_info_academique = QVBoxLayout(self.acad_container)
        self.layout_info_academique.setContentsMargins(10, 20, 10, 10)
        self.v_box_parcours.addWidget(self.acad_container)

        self.fin_container = QGroupBox("💳 Situation Financière")
        self.fin_container.setStyleSheet(self.acad_container.styleSheet())
        self.layout_info_financier = QVBoxLayout(self.fin_container)
        self.layout_info_financier.setContentsMargins(10, 20, 10, 10)
        self.v_box_parcours.addWidget(self.fin_container)

        # 3. EXTRACTION DES DONNÉES
        info_paiement = data.get('paiement_details', {}).get('info_paiement', {})
        mois_info = data.get('paiement_details', {}).get('mois', {})
        parcours_list = data.get("parcours", [])

        # --- LOGIQUE ACADÉMIQUE ---
        if parcours_list:
            acad_frame = QFrame()
            acad_frame.setStyleSheet("background: #f8f9fa; border-radius: 8px; border: 1px solid #eee;")
            acad_layout = QVBoxLayout(acad_frame)
            
            p = parcours_list[0]
            acad_layout.addWidget(QLabel(f"<b>Moyenne :</b> {p.get('moyenne_gen', 0)}"))
            acad_layout.addWidget(QLabel(f"<b>Top :</b> {p.get('top', {}).get('nom', 'N/A')}"))
            self.layout_info_academique.addWidget(acad_frame)

        # --- LOGIQUE FINANCIÈRE ---
        if info_paiement:
            # Tri pour trouver la situation la plus récente
            cles_triees = sorted(info_paiement.keys(), key=lambda x: datetime.strptime(x, "%d-%m-%Y %H:%M"))
            dernier = info_paiement[cles_triees[-1]]
            
            # Calcul de la balance réelle
            total_annuel = dernier.get("total_annuel", 0)
            total_verse = dernier.get("total_verse", 0)
            bal = total_annuel - total_verse
            
            lbl_bal = QLabel(f"⭐ Balance Actuelle : <b>{bal} GDES</b>")
            lbl_bal.setStyleSheet(f"color: {'#e74c3c' if bal > 0 else '#27ae60'}; font-size: 14pt; font-weight: bold;")
            self.layout_info_financier.addWidget(lbl_bal)

        # Affichage des versements (2 colonnes) depuis la clé 'mois'
        if mois_info:
            grid_badges = QGridLayout()
            grid_badges.setSpacing(8)
            
            # Extraire les numéros de versement pour les trier
            v_nums = []
            for k in mois_info.keys():
                if k.lower().startswith("versement_"):
                    v_nums.append(int(k.split('_')[1]))

            for i, num in enumerate(sorted(v_nums)):
                suffix = "er" if num == 1 else "ème"
                badge = QLabel(f"✅ {num}{suffix} Versement")
                badge.setStyleSheet("""
                    background-color: #e1f5fe; color: #01579b; 
                    padding: 6px; border-radius: 4px; font-weight: bold;
                """)
                badge.setAlignment(Qt.AlignCenter)
                grid_badges.addWidget(badge, i // 2, i % 2)
            
            self.layout_info_financier.addLayout(grid_badges)

        # 4. AFFICHAGE FINAL
        self.acad_container.setVisible(True)
        self.fin_container.setVisible(True)
        self.fade_in(self.acad_container)
        self.fade_in(self.fin_container)

    def update_details_view(self, data):
        """Appelée quand l'API répond après le clic"""

        for i in reversed(range(self.v_box_parcours.count())):
            widget = self.v_box_parcours.itemAt(i).widget() 
            if isinstance(widget, (QGroupBox, QFrame)):
                widget.setParent(None)
                widget.deleteLater()

        self.acad_container = QGroupBox("📊 Performance Académique")
        self.acad_container.setVisible(False)
        # Style : Couleur bleu ciel (#3498db ou SkyBlue) et espacement du titre
        self.acad_container.setStyleSheet("""
        QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: none;
                margin-top: 15px; /* Espace pour le titre */
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding-left: 5px;
                color: #3498db; /* Bleu ciel */
            }
        """)
        self.layout_info_academique = QVBoxLayout(self.acad_container)
        self.layout_info_academique.setContentsMargins(10, 25, 10, 10) # Espace sous le titre
        self.v_box_parcours.addWidget(self.acad_container)

        # 2. Création et Style de la Zone Financière
        self.fin_container = QGroupBox("💳 Situation Financière")
        self.fin_container.setVisible(False)
        self.fin_container.setStyleSheet(self.acad_container.styleSheet()) # On réutilise le même style
        
        self.layout_info_financier = QVBoxLayout(self.fin_container)
        self.layout_info_financier.setContentsMargins(10, 25, 10, 10)
        self.v_box_parcours.addWidget(self.fin_container)

        # 1. Rendre les containers visibles
        self.acad_container.setVisible(True)
        self.fin_container.setVisible(True)

        info_paiement = data.get('paiement_details',{}).get('info_paiement',{})
        mois_info = data.get('paiement_details',{}).get('mois',{})
        cles_triees = sorted(
                info_paiement.keys(), 
                key=lambda x: datetime.strptime(x, "%d-%m-%Y %H:%M")
            )
        if info_paiement:
            derniere_date = cles_triees[-1]
            dernier_paiement = info_paiement[derniere_date]
            print(f"Dernier paiement effectué le : {derniere_date}")
            print(f"Total versé à cette date : {dernier_paiement['total_verse']} GDES")


        # 2. Nettoyer les layouts internes (pas les containers eux-mêmes)
        self.clear_layout(self.layout_info_academique)
        self.clear_layout(self.layout_info_financier)

        # --- SECTION ACADÉMIQUE ---
        acad_frame = QFrame()
        acad_frame.setStyleSheet("background: #f8f9fa; border-radius: 5px;")
        acad_layout = QVBoxLayout(acad_frame)
        
        # On suppose que ton API renvoie une liste dans 'parcours'
        parcours_list = data.get("parcours", [])
        if parcours_list:
            p = parcours_list[0]
            acad_layout.addWidget(QLabel(f"<b>Moyenne :</b> {p.get('moyenne_gen', 0)}"))
            acad_layout.addWidget(QLabel(f"<b>Top :</b> {p.get('top', {}).get('nom', 'N/A')}"))
        
        self.layout_info_academique.addWidget(acad_frame)

        # --- SECTION FINANCIÈRE ---
        fin_frame = QFrame()
        fin_layout = QVBoxLayout(fin_frame)
        
        # pay_info = data.get("paiement_details", {})
        if info_paiement:
            total_annuel = dernier_paiement.get("total_annuel", 0)
            total_verse = dernier_paiement.get("total_verse", 0)
            bal =  total_annuel - total_verse
            lbl_bal = QLabel(f"Balance : <b>{bal} GDES</b>")
            lbl_bal.setStyleSheet(f"color: {'red' if float(bal) > 0 else 'green'}; font-size: 13pt;")
            fin_layout.addWidget(lbl_bal)



        # self.layout_info_financier.addLayout(grid_badges)
        if mois_info:
            grid_badges = QGridLayout()
            grid_badges.setSpacing(10)
            
            # 1. Extraction et tri des versements
            versements_list = []
            for key in mois_info.keys():
                if key.lower().startswith("versement_"):
                    parts = key.split('_')
                    if len(parts) > 1:
                        num = parts[1]
                        suffix = "er" if num == "1" else "ème"
                        versements_list.append(int(num)) # On garde l'int pour trier

            # 2. Création des badges (2 par ligne)
            for index, num in enumerate(sorted(versements_list)):
                suffix = "er" if num == 1 else "ème"
                texte_versement = f"✅ {num}{suffix} Versement : Acquitté"
                
                badge = QLabel(texte_versement)
                badge.setStyleSheet("""
                    background-color: #e1f5fe; 
                    color: #01579b; 
                    padding: 8px; 
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 10pt;
                    border: none;
                """)
                badge.setAlignment(Qt.AlignCenter)

                # Calcul de la ligne et de la colonne pour le 2 par ligne
                row = index // 2
                col = index % 2
                grid_badges.addWidget(badge, row, col)

            self.layout_info_financier.addLayout(grid_badges)
        else:
            self.layout_info_financier.addWidget(QLabel("Aucun versement acquitté."))
 
        
        # fin_layout.addLayout(badge_layout)
        self.layout_info_financier.addWidget(fin_frame)
        self.fade_in(self.acad_container)
        self.fade_in(self.fin_container)
        self.v_box_parcours.update()
    
    
    def populate_student_historyb(self, show_student): # J'ai enlevé le paramètre inutile
        classes_annee = show_student.get('classes_etudiant', [])
        if not classes_annee:
            self.v_box_parcours.addWidget(QLabel("Aucun historique trouvé."))
            return

        self.group_annee = QButtonGroup(self)
        self.group_annee.setExclusive(True) 

        id_annee_active = classes_annee[-1].get('annee_academiques', {}).get('id')
        button_to_click = None

        for parcours in classes_annee:
            annee_data = parcours.get("annee_academiques", {})
            
            btn = QPushButton(annee_data.get('annee_academique'))
            btn.setCheckable(True)
            
            self.group_annee.addButton(btn)
            student_id = show_student.get('id')
            annee_data = parcours.get("annee_academiques", {})
            classe_id = parcours.get("classes", {}).get("id")
            annee_id = annee_data.get("id")

            frame = QFrame()
            layout = QHBoxLayout(frame)
            layout.setContentsMargins(5, 2, 5, 2)

            btn = QPushButton(annee_data.get('annee_academique'))
            btn.setCheckable(True)
            btn.setAutoExclusive(True) 
            
            base_style = """
                QPushButton {
                    padding: 5px; text-align: center;
                    max-width: 230px; min-width: 200px;
                    border-radius: 5px; font-size: 13pt;  
                    border: 1px solid #bbb; background: white; color: #999;
                }
                QPushButton:hover, QPushButton:checked {
                    background: #40af5d; border: 1px solid #40af5d; color: white;
                }
            """
            btn.setStyleSheet(base_style)

            if annee_data.get("id") == id_annee_active:
                btn.setText(f"⭐ {btn.text()} (Actuel)")
                button_to_click = btn

            # btn.clicked.connect(lambda _, p=parcours: self.on_history_click(p, show_student))
            btn.clicked.connect(lambda _, c=classe_id, s=student_id, a=annee_id: self.get_student_detail(c, s, a))

            # On ajoute le bouton au layout (avec ou sans Frame)
            self.v_box_parcours.addWidget(btn)

        if button_to_click:
            button_to_click.click()




    def get_student_detail(self, classe_id, student_id, annee_id):
        # self.update_details_view()
        payload = {
            "student_id": student_id,
            "classe_id": classe_id,
            "annee_id": annee_id
        }
        self.api_handler_.get_student_details(payload=payload) 



    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def back_to_details(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.details)
        self.fancy_modal_show(self.ui.details)
        # self.ui.titre_toggle.setText("Information")

    def pieces_soumise(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.pieces)
        self.fancy_modal_show(self.ui.pieces)

    def verifier_champs_obligatoires(self):
        # Liste des champs à vérifier : (widget, type de champ, méthode pour obtenir la valeur)
        champs = [
            (self.ui.nom, "lineedit", lambda w: w.text().strip()),
            (self.ui.prenom, "lineedit", lambda w: w.text().strip()),
            (self.ui.date_de_naissance, "lineedit", lambda w: w.text().strip()),
            (self.ui.adresse, "lineedit", lambda w: w.text().strip()),
            (self.ui.lieu_de_naissance, "lineedit", lambda w: w.text().strip()),
            (self.ui.niveau_id, "combobox", lambda w: w.currentText().strip()),
            (self.ui.classe_actuelle_id, "combobox", lambda w: w.currentData()),
            (self.ui.annee_academique_id, "combobox", lambda w: w.currentData()),
        ]

        tous_remplis = True

        for widget, _, get_value in champs:
            widget.setStyleSheet("")  # Reset style

            if not get_value(widget):
                widget.setStyleSheet("border: 1px solid red;")
                tous_remplis = False

        if not tous_remplis:
            QMessageBox.warning(self, "Avertissement", "Les champs obligatoires ne sont pas remplis.")
            return False

        return True


    def responsable_info(self):
        if not self.verifier_champs_obligatoires():
            return  # Bloquer la suite si les champs ne sont pas valides
        self.ui.tabWidget.setCurrentWidget(self.ui.responsable_info)
        self.fancy_modal_show(self.ui.responsable_info)


    def back_to_responsable(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.responsable_info)
        self.fancy_modal_show(self.ui.responsable_info)
    
    def back_to_personnal_info(self):
        self.ui.tabWidget.setCurrentWidget(self.ui.personnel_info)

    def on_row_clicked(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        # from .EtudiantController import student_show
        id_item = self.ui.student_table.item(row, 0)  # Colonne 0 = ID
        if id_item:
            try:
                show_student = self.api_handler_.student_show(id_item.text())
            except Exception as e:
                print("Erre=== :", e)
                import traceback
                traceback.print_exc()
            # show_student = self.fetch_data_.student_show(id_item.text())
            # self.add_student_page(show_student)
       
            return id_item.text()

    def next_page_student(self):
        if self.current_page_student < self.total_pages_student:
            self.go_to_student_page(self.current_page_student + 1)

    def prev_page_student(self):
        if self.current_page_student > 1:
            self.go_to_student_page(self.current_page_student - 1)


    def go_to_paiement_page(self, page):
        self.overlay.start_loading(f"Paiement page {self.current_page_paiement}")
        self.current_page_paiement = page  

        self.api_handler_.all_paiement(self.ui.search_paiement.text(), page)
        # self.overlay.finish_loading()

    def restart_timer_paiement(self):
        self.search_timer_paiement.start(300)

    def paiement_page(self):
        try:
            # self.restart_disconnect_timer()
            self.ui.frame_350.setHidden(True)
            self.ui.frame_408.setHidden(True)
            self.data_for_other_transac = False
            self.ui.combo_transact_identifiant.clear()
            if not hasattr(self, "montant_verser") or not isValid(self.montant_verser):
                self.montant_verser = QLineEdit(self) 


            # QShortcut(QKeySequence("Ctrl+t"), self, activated=lambda: self.montant_verser.setFocus())
            self.student_live_seach_input = QLineEdit() 
            self.paiement_index = QLineEdit() 
            # self.set_table_refresh_data_paiement()
            self.fade_in_page(self.ui.paiement_page)
            self.go_to_paiement_page(self.current_page_paiement) 
            self.mois={}
            self.accessoires={}
            
            self.ui.stackedWidget.setCurrentWidget(self.ui.paiement_page)
            self.ui.stackedPaiement.setCurrentWidget(self.ui.index_paiement)
            
            
        except Exception as e:
            print(f"Erreur dans paiement_page: {e}")
            traceback.print_exc() 

    def set_table_refresh_data_paiement(self):
        header = ("Id","id_et", "Identifiant","Nom", "prénom", "Année", 
                  "Niveau", "Classe")
        self.all_headers_table_labels(
            self.ui.paiement_table, header,  "#e2e8f0", 32,32, 200, 130, 250, 165, 165, 200)
        self.ui.paiement_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.paiement_index.setText("")
        self.ui.paiement_table.setColumnHidden(1, True)
        
            
        if self.all_paiement_data:
            if self.is_data_updating:
                return 
            self.is_data_updating = True

            try:
                self.current_page_paiement =  self.all_paiement_data.get("meta", {}).get("current_page", 1)
                self.total_pages_paiement =  self.all_paiement_data.get("meta", {}).get("last_page", 1) 

        
                self.ui.prev_paiement.setEnabled(self.current_page_paiement > 1)
                self.ui.next_paiement.setEnabled(self.current_page_paiement < self.total_pages_paiement)
        
                self.ui.prev_paiement.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_paiement.setStyleSheet("""
                    /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """) 
                self.ui.next_paiement.setText('Suivant')
                self.ui.prev_paiement.setText('Précédent')
        
                self.select_all_populate(self.all_paiement_data['data'], self.ui.paiement_table, self.on_row_clicked_paiement,['id','id_','identifiant', 'nom', 'prenom', 'annee', 'niveaux', 'classes']) 
            except Exception as e:
                print(f'Something went wrong {e}')
            finally: 
                self.is_data_updating = False
        # self.ui.aide_financiere   

    def on_row_clicked_paiement(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        # from .PaiementController import show_paiement
        id_item = self.ui.paiement_table.item(row, 0)  
        id_item_et = self.ui.paiement_table.item(row, 1)  
        if id_item: 
            self.overlay.start_loading() 
            self.student_id_for_payment_show = id_item_et.text()

            self.api_handler_.paiement_show(id_item.text())  

    def parse_date(self, d):
        return datetime.strptime(d, "%d-%m-%Y %H:%M")

    def show_payment(self, show_paiement, id_etudiant):
        self.overlay.start_loading() 
        avances = ''
        is_returned=False
        if show_paiement and 'show_paiement' in show_paiement: 
            if 'paiement_details' in show_paiement['show_paiement']:
                paiement_details = show_paiement['show_paiement']['paiement_details']
                font4 = QFont()
                font4.setPointSize(14)
                font4.setBold(True)
            
                # if self.ui.scrollArea_show_paiement.layout():
                #     self.clear_layout(self.ui.scrollArea_show_paiement.layout())
                   
                # else:
                #     # self.historique_frame = QFrame()
                existing_layout = self.ui.scrollAreaWidgetContents_6.layout()
                # print(existing_layout)
                if self.ui.scrollAreaWidgetContents_6.layout():
                    self.clear_layout(existing_layout)
                else:
                    self.historique_layout = QVBoxLayout()
                    self.historique_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    self.historique_layout.setSpacing(30) 
                    
                if isinstance(paiement_details['paiement_details']['info_paiement'], dict):
                  
                    info = paiement_details['paiement_details']['info_paiement']

                    for indexs, (date_str, data) in enumerate(
                        sorted(info.items(), key=lambda x: self.parse_date(x[0]))
                    ):
                        details = (date_str, data)
                        label_date = QLabel()
                        label_date.setObjectName('label_date')
                        label_date.setText(str(details[0]))
                        label_date.setFont(font4)
                        # if is_returned:
                        #     label_date.setStyleSheet("color: red; font-weight: bold;")
                        # else:
                        #     label_date.setStyleSheet("color: rgb(0, 167, 238);")

                        if details[1].get('status', "") != 'retourné':
                            label_date.setStyleSheet("color: rgb(0, 167, 238);")
                            avances = [s.replace("Avns: ", "") for s in details[1].get('status_paiement', []) if s.startswith("Avns:")] 
                        else:
                            is_returned = True
                            label_date.setStyleSheet("color: red; font-weight: bold;")
                        #      avances = [s for s in details[1].get('status_paiement', []).get('last_status') ] 
                    
                        historique_frame = QFrame()
                        layout_employer = QVBoxLayout(historique_frame)

                        layout_employer.setContentsMargins(17,0,0,0)
                        layout_employer.setSpacing(4)
                        # employer_text = details[1].get('employer', '') if is_returned else details[1].get('return_by', '')
                        # employer = QLabel(f"       Employé:       {employer_text}")

                        if is_returned:
                            employer =QLabel(f"       Employer:       {details[1].get('return_by', '')}")
                        else:
                            employer =QLabel(f"       Employer:       {details[1].get('employer', '') }")

                        employer.setFont(font4)
                        employer.setStyleSheet("color: rgb(112, 112, 112);")
                        layout_employer.addWidget(label_date)
                        layout_employer.addWidget(employer)
                        layout_employer.setAlignment(Qt.AlignmentFlag.AlignTop)
                        month_key = paiement_details['paiement_details']['mois']

                        frame_versement_historique = QFrame()
                        layout_versement_historique = QVBoxLayout(frame_versement_historique)
                        layout_versement_historique.setAlignment(Qt.AlignmentFlag.AlignTop)
                        layout_versement_historique.setSpacing(1)
                        layout_versement_historique.setContentsMargins(17,0,0,0)

                        if month_key and details[1].keys() & month_key.keys():
                            is_returned=False
                            common_keys = details[1].keys() & month_key.keys()
                            for index,key in enumerate(sorted(common_keys)):
                              
                                frame_versement = QFrame()
                                layout_versement = QHBoxLayout(frame_versement)
                                layout_versement.setContentsMargins(0,7,0,0)
                                if details[1].get('status') != 'retourné':
                                    label_key = QLabel(f"{str(self.transformer_versement(key))}   (Acquitté)")
                                    label_value = QLabel(f"   {str(details[1].get(key))} {str(details[1]['devise'])}")
                                    layout_versement.addWidget(label_key)
                                    layout_versement.addWidget(label_value)

                                    layout_versement_historique.addWidget(frame_versement)
                                if 'check_echeance' in paiement_details['paiement_details'] and key == sorted(common_keys)[-1] and details[1].get('status') not in ['Acquitté','retourné']  :                                 
                                    if details[1].get('status_paiement'):
                                        # avance_str = next((s for s in latest_entry.get('status_paiement',{}) if s.startswith("Avns:")), None)

                                        label_avance = QLabel(f"  Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur (le) {avances[0] if avances else 'prochain versement'}")
                                    else:
                                        label_avance = QLabel(f" Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur le prochain versement")

                                    # {self.get_next_key(paiement_details['paiement_details']['check_echeance'], str(self.transformer_versement(key)))}

                                    layout_versement_historique.addWidget(label_avance)
                        else:
                            # label_avance = QLabel(f"  Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur (le) prochain versement")
                            label_avance = QLabel(f"  Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur (le) {avances[0] if avances else 'prochain versement'}")
                            layout_versement_historique.addWidget(label_avance)

                        if details and details[1].get('status_paiement') and details[1].get('status') == 'retourné':
                            # print(details[1])
                            if details[1].get('status') == 'retourné':
                                is_returned=True                                    
                                status_paiement = details[1].get('status_paiement', {})
                                avances = status_paiement.get('last_status', [])

                                # avances_text = ", ".join(avances) if avances else "—"
                                avances_text = ", ".join([s.replace("Acqt: ", "").replace("Avns: ", "") for s in avances]) if avances else "—"

                                dates = details[1].get('date_retour', '')
                                label_avance = QLabel(
                                    f"  Ce dépôt de {details[1].get('depot', '')} {details[1].get('devise')} "
                                    f"  pour ({avances_text}) \n"
                                    f"  a été retourné le {dates.split('--')[0]} à {dates.split('--')[1]} \n"
                                    f"  motif: {details[1].get('commentaire', '')}"
                                )

                            else:
                                is_returned=False
                                label_avance = QLabel(f"  Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur (le) {avances[0] if avances else 'prochain versement'} ")
                            layout_versement_historique.addWidget(label_avance)
                        # else:
                        #     label_avance = QLabel(f"  Avance de {details[1].get('depot_et_avance')} {details[1].get('devise')} sur (le) prochain versement")

                        frame_montant = QFrame()
                        layout_montant = QHBoxLayout(frame_montant)
                        layout_montant.setContentsMargins(30,7,0,0)


                        montant_verse_key = QLabel("montant versé ")
                        # montant_verse_key.setForegroundRole(QBrush(QColor(233, 153, 62)))
                        montant_verse_value = QLabel(f"{str(details[1]['depot'])} {str(details[1]['devise'])}")

                        frame_action = QFrame()
                        layout_action = QHBoxLayout(frame_action)

                        edit = QPushButton('Modifier')
                        imprimer = QPushButton('Imprimer')
                        supprimer = QPushButton('Retourner' if not is_returned else 'Retourné')

                        supprimer.setEnabled(not is_returned)

                        id_pay=show_paiement['show_paiement']['id']
                        
                        imprimer.clicked.connect(lambda _, id=id_pay, indexs=indexs: self.print_paiement_recu(id, indexs))

                        # edit.clicked.connect(lambda _, id=id_etudiant, indexs=details[0], last_depot=details[1]['depot']: self.edit_paiement_recu(id, indexs,last_depot))

                        supprimer.clicked.connect(lambda _, id=id_pay, indexs=details[0]: self.supprimer_paiement_recu(id, indexs))

                        layout_action.setSpacing(8)
                        # layout_action.addWidget(edit)
                        layout_action.addWidget(imprimer)
                        layout_action.addWidget(supprimer)

                        supprimer.setFlat(True)
                        imprimer.setFlat(True)
                        edit.setFlat(True)

                        edit.setStyleSheet("color: rgb(252, 201, 30);font-size:13pt;background:transparent")
                        supprimer.setStyleSheet("color: rgb(234, 67, 49);font-size:13pt;background:transparent")
                        imprimer.setStyleSheet("color: rgb(0, 167, 238);font-size:13pt;background:transparent")
                        layout_action.setAlignment(Qt.AlignmentFlag.AlignHCenter)

                        montant_verse_value.setStyleSheet("color: rgb(252, 201, 30);")
                        montant_verse_key.setStyleSheet("color: rgb(252, 201, 30);")
                        montant_verse_key.setFont(font4)
                        montant_verse_value.setFont(font4)

                        layout_montant.addWidget(montant_verse_key)
                        layout_montant.addWidget(montant_verse_value)
                        layout_employer.addWidget(frame_montant)
                        layout_employer.addWidget(frame_versement_historique)
                        layout_employer.addWidget(frame_action)

                        self.historique_layout.addWidget(historique_frame)
               
                self.ui.scrollAreaWidgetContents_6.setLayout(self.historique_layout)

        # self.overlay.start_loading()
        QTimer.singleShot(200, self.overlay.finish_loading)
        # self.overlay.finish_loading()

    def show_paymengt1(self, show_paiement):
        if show_paiement and 'show_paiement' in show_paiement:
            if 'paiement_details' in show_paiement['show_paiement']:
                paiement_details = show_paiement['show_paiement']['paiement_details']
                font4 = QFont()
                font4.setPointSize(15)
                font4.setBold(True)
                
                
                existing_layout = self.ui.scrollArea_show_paiement.layout()
                if existing_layout:
                    self.clear_layout1(existing_layout)

                
                self.historique_layout = QVBoxLayout()
                self.historique_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.historique_layout.setSpacing(30)

                for indexs, details in enumerate(paiement_details['paiement_details']['info_paiement'].items()):
                    label_date = QLabel(str(details[0]))
                    label_date.setFont(font4)
                    label_date.setStyleSheet("color: rgb(0, 167, 238);")

                    historique_frame = QFrame()
                    layout_employer = QVBoxLayout(historique_frame)
                    layout_employer.setContentsMargins(17,0,0,0)
                    layout_employer.setSpacing(4)

                    employer = QLabel(f"       Employer:       {str(details[1]['employer'])}")
                    employer.setFont(font4)
                    employer.setStyleSheet("color: rgb(31, 40, 55);")

                    layout_employer.addWidget(label_date)
                    layout_employer.addWidget(employer)

                    self.historique_layout.addWidget(historique_frame)

                # Appliquer le layout propre
                self.ui.scrollAreaWidgetContents_6.setLayout(self.historique_layout)


    def print_paiement_recu(self, id, indexs):
        self.overlay.start_loading("Reçu paiement")
        result = self.api_handler_.recu_paiement(id=id, keys=indexs)


    def edit_paiement_recu(self, id, indexs,last_depot): 
        print(f"self.montant_verser ------------{self.montant_verser}  last_depot {last_depot}")
        self.montant_verser.setFocus() 
        self.overlay.start_loading("Modifier paiement")
        self.montant_verser.setText(last_depot)
        self.paiement_index.setText(indexs)
        self.api_handler_.get_student_with_params_payment(etudiant=id)

    # def data_comming_in_direct_params_payment(self, response_data):
    #     if response_data['data']:
    #         self.show_student_for_payment = response_data['data'][-1]

    #         first_info = self.show_student_for_payment
            
    #         self.ui.identifiant.setText(first_info['identifiant'])
    #         self.ui.identifiant.setStyleSheet("""color:#555;font-weight:bold""")
    #         self.ui.fname.setStyleSheet("""color:#555""")
    #         self.ui.lname.setStyleSheet("""color:#555""")
    #         self.ui.classe_actuelle.setStyleSheet("""color:#555""")
    #         self.ui.fname.setText(first_info['nom'])
    #         self.ui.lname.setText(first_info['prenom'])
    #         self.ui.classe_actuelle.setText(first_info['nom_classe'])
    #         profile = self.get_path(os.path.join('assets', 'icons', 'profile.png'))#label.setPixmap(pixmap)
    #         pixmap = QPixmap(profile) 

    #         pixmap = pixmap.scaled(self.ui.imag_ilustrative.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    #         self.ui.imag_ilustrative.setPixmap(pixmap)
   


    def supprimer_paiement_recu(self, id, indexs):
        reply_delete_paiement = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment rembourser le paiement avec l'identifiant '{indexs}' ?",
            QMessageBox.Yes | QMessageBox.No
        )
        self.overlay.start_loading(f"Remboursement du paiement {indexs}")
        if reply_delete_paiement == QMessageBox.Yes:
            self.api_handler_.supprimer_paiement_recu(id, indexs,self.user_connect.text())
        else:
            self.overlay.finish_loading( )

    def get_next_key(self,dictionnaire, key):        
        keys = list(dictionnaire.keys())      
        
        if key in keys:            
            index = keys.index(key)            
            if index + 1 < len(keys):
                next_key = keys[index + 1]
                return next_key#, dictionnaire[next_key]
            else:
                return None 
        return None

    def transformer_versement(self,cle):
        """
        Transforme une clé contenant 'XXX_X_UUID' en '1er XXX', '2ème XXX', etc.
        
        :param cle: Chaîne contenant 'XXX_X_UUID' où X est un nombre.
        :return: Chaîne transformée ('1er XXX', '2ème XXX', etc.), ou None si aucun nombre n'est trouvé.
        """
        match = re.search(r"^([^_]+)_(\d+)_", cle)  # Capture le premier mot et le nombre
        if match:
            premier_element = match.group(1)  # Le texte avant '_X_'
            numero = int(match.group(2))  # Le nombre X

            # Déterminer l'ordinal
            suffixe = "er" if numero == 1 else "ème"
            if premier_element not in ["September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July"]:
                return f"{numero} {suffixe} {premier_element}"
            else:
                return f" {premier_element}"

        return None  # Retourne None si aucun motif trouvé


    
    def next_paiement(self): 
        if self.current_page_paiement < self.total_pages_paiement:
            self.go_to_paiement_page(page=self.current_page_paiement + 1)
            self.set_table_refresh_data_paiement()
            

    def prev_paiement(self): 
        if self.current_page_paiement > 1:
            self.go_to_paiement_page(page=self.current_page_paiement - 1)
            self.set_table_refresh_data_paiement()

    def search_student1(self):
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        dialog = QDialog()
        dialog.setWindowTitle("Rechercher un étudiant")
        dialog.setModal(True)  # Bloque l'interaction avec la fenêtre principale
        dialog.setFixedSize(600, 200)  # Définir une taille

        # Layout principal
        layout = QVBoxLayout()

        # Création des frames
        frame_search = QFrame()
        frame_show = QFrame()

        # Définir des styles pour les frames
        # frame_search.setStyleSheet("background-color: #f0f0f0; border: 1px solid gray;")
        # frame_show.setStyleSheet("background-color: #d0d0d0; border: 1px solid gray;")

        # Définir la taille des frames
        frame_search.setFixedSize(280, 150)
        frame_show.setFixedSize(280, 150)

        # Zone de recherche
        student_input = QLineEdit()
        student_input.setPlaceholderText("Rechercher un étudiant...")

        # Layout vertical pour frame_search
        search_layout = QVBoxLayout()
        search_layout.addWidget(student_input)
        frame_search.setLayout(search_layout)

        # Ajouter les frames et widgets au layout principal
        layout.addWidget(frame_search)
        layout.addWidget(frame_show)

        dialog.setLayout(layout)

        # Appliquer le style général
        dialog.setStyleSheet(
            """
            QLineEdit { width: 200px; min-height: 25px; max-height: 25px; }
            """
        )

        dialog.exec()  # Affichage du dialogue en mode bloquant


# ===========================================  __PAIEMENT__ =========================================



# =======================================  __PROFESSEUR__ ========================================
    def professeur_page(self): 
        # self.restart_disconnect_timer()
        self.overlay.start_loading()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)

        self.set_table_refresh_data_teacher()

        self.go_to_page_teacher(self.current_page_prof)
        self.id_professeur_for_update = QLineEdit()
        self.id_professeur_for_update.setText('')
        self.ui.stackedWidget.setCurrentWidget(self.ui.professeur_page)
        self.ui.stacked_prof.setCurrentWidget(self.ui.index_prof)
        self.fade_in_page(self.ui.index_prof) 

    def add_professeur(self, professeur=None):
        self.clear_professeurs()
        self.ui.enregistrer_prof.setText("Enregistrer")

        self.ui.frame_302.setHidden(True)
        self.ui.frame_313.setHidden(True)

        if professeur: 
            self.ui.frame_313.setHidden(False)
            self.ui.frame_302.setHidden(False)
            self.ui.enregistrer_prof.setText("Modifier")
            self.id_professeur_for_update.setText(str(professeur.get("id","")))
            self.ui.nom_prof.setText(str(professeur.get("nom","")))
            self.ui.telephone_prof.setText(str(professeur.get("telephone","")))
            self.ui.prenom_prof.setText(str(professeur.get("prenom","")))
            self.ui.email_prof.setText(str(professeur.get("email","")))
            self.ui.sexe_prof.setText(str(professeur.get("sexe","")))
            self.ui.adresse_prof.setText(str(professeur.get("adresse","")))
            self.ui.matiere_enseignee.setText(str(professeur.get("matiere_enseignee","")))

            if 'user' in professeur:
                user = professeur.get("user")
                if isinstance(user, dict):
                    is_active = user.get("status")
                    is_active_bool = str(is_active) == '1'
                    status = "Active" if is_active_bool else "Inactive"
                    button_text = "Desactiver" if is_active_bool else "Activer"
                else:
                    is_active_bool = False
                    status = "Inactive"
                    button_text = "Activer"

                self.ui.prof_status.setText(status)
                self.ui.status_prof_change.setText(button_text)

                if is_active_bool:
                    self.ui.prof_status.setStyleSheet("""
                        QLabel {
                            color: green;
                            font-weight: bold;
                        }
                    """)
                    self.ui.status_prof_change.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;  /* Rouge clair */
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                        }
                    """)
                else:
                    self.ui.prof_status.setStyleSheet("""
                        QLabel {
                            color: red;
                            font-weight: bold;
                        }
                    """)
                    self.ui.status_prof_change.setStyleSheet("""
                        QPushButton {
                            background-color: #4caf50;  /* Vert clair */
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #388e3c;
                        }
                    """)           

        self.fancy_modal_show(self.ui.add_prof) 
        self.ui.stacked_prof.setCurrentWidget(self.ui.add_prof)
        # QTimer.singleShot(5, self.request_finished)
        # self.overlay.start_loading()
        self.overlay.finish_loading()

    def show_teacher_and_other_action(self):
        pass 


    def restart_timer_prof(self):
        self.search_timer_prof.start(300)

    def delete_professeur(self):
        print(self.fetch_data_permissions)
        id = self.id_professeur_for_update.text()
        reply_delete_prof = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer  ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply_delete_prof == QMessageBox.Yes: 
            result = self.api_handler_.delete_prof(id)
        else:
            self.overlay.finish_loading()
              

    def active_teacher(self):
        self.overlay.start_loading("Activation du professeur")
        id = self.id_professeur_for_update.text()
        result = self.api_handler_.active_teacher(id=id)


    def sauvegarder_professeur(self):
        self.overlay.start_loading("Enregistrement professeur...")
        teacher_data={
            'id':self.id_professeur_for_update.text(),
            'nom':self.ui.nom_prof.text(),
            'prenom':self.ui.prenom_prof.text(),
            'email':self.ui.email_prof.text(),
            'notification':self.ui.notif_prof.isChecked(),
            'sexe':self.ui.sexe_prof.text(),
            'adresse':self.ui.adresse_prof.text(),
            'matiere_enseignee':self.ui.matiere_enseignee.text(),
            'telephone':self.ui.telephone_prof.text(),
            'user_id':self.user_connect.text()
        } 
        self.api_handler_.enregistrer_professeur(teacher_data)

    # def show_result_after_save_teacher(self, response_data,status):
    #     from Controllers.Validator import ValidatorError
    #     if response_data and 'errors' in response_data:
    #         self.overlay.finish_loading()
    #         ve = ValidatorError()
    #         ve.generic_direct_error_message(response_data=response_data)                
    #     else: 
    #         self.professeur_page()
    #         self.clear_professeurs()
    #         self.fill_teacher_combo()
    #         QMessageBox.information(self, "Success", f"{response_data.get('success','')}")
    #     QTimer.singleShot(200, self.overlay.finish_loading)

    #     # id = self.id_professeur_for_update.text()
    #     # nom = self.ui.nom_prof.text()
    #     # telephone = self.ui.telephone_prof.text()
    #     # prenom = self.ui.prenom_prof.text()
    #     # email = self.ui.email_prof.text()
    #     # sexe = self.ui.sexe_prof.text()
    #     # adresse = self.ui.adresse_prof.text()
    #     # matiere_enseignee = self.ui.matiere_enseignee.text()
    #     # notifiation =self.ui.notif_prof.isChecked()

    #     # response = self.save_data.enregistrer_professeur(id=id,nom=nom,prenom=prenom, telephone=telephone, email=email,sexe=sexe,adresse=adresse,matiere_enseignee=matiere_enseignee,notif_prof=notifiation)



    def clear_professeurs(self):
        self.clear_fields( self.ui.nom_prof, self.ui.telephone_prof, self.ui.prenom_prof, self.ui.email_prof,self.ui.sexe_prof, self.ui.adresse_prof,self.ui.matiere_enseignee  # QComboBox
        )

    def go_to_page_teacher(self, page):
        self.overlay.start_loading("Chargement des professeurs")
        self.current_page_prof = page
        self.api_handler_.all_teacher(self.ui.search_prof.text(), page)

    def set_table_refresh_data_teacher(self, page=1):
        header = ("Id", "Nom", "prénom", "Sexe", 
                  "Email", "Téléphone", 'status')
        self.all_headers_table_labels(
            self.ui.prof_table, header,  "#e2e8f0", 32, 130, 130, 20, 250, 110, 50)
        self.ui.prof_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        colonnes_ordre = ["id", "nom", "prenom", "sexe", "email", "telephone",'status_']
       

        if self.is_data_updating:
            return 
        self.is_data_updating = True
        try:
            # table = self.api_handler_.all_teacher(self.ui.search_prof.text(), page)
            if self.all_teacher_data:
                # self.current_page_prof = table.get("current_page","")
                # self.total_pages_prof = table.get("total_pages","")

                meta = self.all_teacher_data.get("meta", "")
                
                self.current_page_prof = meta.get("current_page",1)
                self.total_pages_prof = meta.get("last_page",1)
        
                self.ui.prof_prev.setEnabled(self.current_page_prof > 1)
                self.ui.prof_next.setEnabled(self.current_page_prof < self.total_pages_prof)
            self.ui.prof_prev.setStyleSheet("""
                QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc; padding: 5px 10px; }
            """)

            self.ui.prof_next.setStyleSheet("""
                QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc; padding: 5px 10px; }
            """)
            self.select_all_populate(self.all_teacher_data['data'], self.ui.prof_table, self.on_row_clicked_prof,_ordre=colonnes_ordre)
        except:
            print('Something went wrong')
        finally: 
            self.is_data_updating = False

    def on_row_clicked_prof(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.prof_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            self.overlay.start_loading()
            show_prof = self.api_handler_.teacher_show(id_item.text())           
       
            return id_item.text()

    def prof_next(self):
        if self.current_page_prof < self.total_pages_prof:
            self.go_to_page_teacher(page=self.current_page_prof + 1)

    def prof_prev(self):
        if self.current_page_prof > 1:
            self.go_to_page_teacher(page=self.current_page_prof - 1)

# ===========================================  PROFESSEUR =========================================

# ===========================================  __COURS__ =========================================
    def cours_page(self):     
        self.ui.class_id.clear()
        # self.restart_disconnect_timer()
        self.overlay.start_loading()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        
       
        self.ui.stackedWidget.setCurrentWidget(self.ui.cours_page)
        self.ui.coursStaked.setCurrentWidget(self.ui.cours_staked_page) 
        self.ui.stackedWidgetCours.setCurrentWidget(self.ui.index_cours) 
        self.fade_in_page(self.ui.index_cours) 
        self.go_to_cours_page(self.current_page_cours)

    def go_to_cours_page(self, page):
        # from .ProgrammeController import all_cours
        self.overlay.start_loading(f"Cours page {self.current_page_cours}")
        self.current_page_cours = page
        self.api_handler_.all_cours(self.ui.search_cours.text(), page)

    def add_cours_page(self):
        self.ui.enregistrer_cours.setText("Sauvegarder")
        self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
        self.ui.stackedWidgetCours.setCurrentWidget(self.ui.add_cours)
        self.fancy_modal_show(self.ui.add_cours) 

    def set_table_refresh_data_cours(self):
        header = ("Id", "Cours", "Type de Matière", "Date")
        self.all_headers_table_labels(
            self.ui.cours_table, header,  "#e2e8f0", 32, 230, 220, 200, 230)
        self.ui.cours_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        if self.is_data_updating:
            return 
        self.is_data_updating = True

        try:
            # table = self.api_handler_.all_cours(self.ui.search_cours.text(), page)

            if self.all_cours_data:
                meta = self.all_cours_data.get('meta', {})
                self.current_page_cours = meta.get('current_page', 1)
                
                self.total_pages_cours = meta.get('last_page', 1)

                self.ui.prev_cours.setEnabled(self.current_page_cours > 1)
                self.ui.next_cours.setEnabled(self.current_page_cours < self.total_pages_cours)

                self.ui.prev_cours.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_cours.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """) 

                self.select_all_populate(self.all_cours_data['data'], self.ui.cours_table, self.on_row_clicked_cours, ['id', 'cours_nom','type_matiere','date'])
                self.ui.next_cours.setText('Suivant')
                self.ui.prev_cours.setText('Précédent')
        except Exception as e:
          print(f'Something went wrong ....{e}')
        finally: 
            self.is_data_updating = False
        # QTimer.singleShot(5, self.request_finished)

    def next_cours(self):
        if self.current_page_cours < self.total_pages_cours:
            self.go_to_cours_page(page=self.current_page_cours + 1)

    def prev_cours(self):
        if self.current_page_cours > 1:
            self.go_to_cours_page(page=self.current_page_cours - 1)


    def on_row_clicked_cours(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        # from .ProgrammeController import cours_show
        id_item = self.ui.cours_table.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_cours = self.api_handler_.cours_show(id_item.text())
            # self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
            # self.add_cours_page()
            # self.add_cours_line(show_cours)
       
            # return id_item.text()


    def add_programme_line(self, show_programme=None): 
        row_frame = QFrame() 
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)
 
        self.niveau_id_in_programme = QComboBox()
        self.cours_ids = QComboBox()
        self.programme_faculte_id = QComboBox()
        self.programme_faculte_id.setHidden(True)
        professeur_id = QComboBox()
        jours = QComboBox()
        jours.addItems(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"])
        annee_academique = QComboBox()
        self.session_in_programme = QComboBox()
        self.session_in_programme.setPlaceholderText("Session")
        self.session_in_programme.addItems(["1ère", "2ème"])
        self.session_in_programme.setHidden(True)
        self.classe_in_programme = QComboBox()
        heure = QLineEdit() 
        coefficients = QLineEdit() 
         
        supprimer = QPushButton("Supprimer")
        supprimer_de_la_base = QPushButton("Supprimer de la base")
        supprimer.setFlat(True)  

        heure.setPlaceholderText('Heure') 
        jours.setPlaceholderText('Jours') 
        self.cours_ids.setPlaceholderText('Cours') 
        coefficients.setPlaceholderText('Coefficients')
        self.niveau_id_in_programme.setPlaceholderText('Niveau / Cycle') 
        professeur_id.setPlaceholderText('Professeur') 
        self.programme_faculte_id.setPlaceholderText('Faculte / Option') 
        self.classe_in_programme.setPlaceholderText('Classe') 
        self.session_in_programme.setPlaceholderText('Session') 
        annee_academique.setPlaceholderText('Année Académique') 
        note_de_passage = QLineEdit()
        note_de_passage.setPlaceholderText('Note de passage')
        note_de_passage.setObjectName("note_de_passage")
        note_de_passage.setHidden(True)

        supprimer.setObjectName("supprimer")  
        supprimer_de_la_base.setObjectName("supprimer_de_la_base")  
        row_frame.setObjectName("row_frame")

        id_for_edit_programme =  QLineEdit()
        id_for_edit_programme.setText('')
  
        for niveau in self.niveaux:
            self.niveau_id_in_programme.addItem(niveau.get('name',""), niveau.get('id',"")) 
 
        professeur_id.clear()
        for prof in self.teacherList:
            professeur_id.addItem(f"{prof['nom']} {prof['prenom']}", prof['id'])
 
        self.cours_ids.clear()
        cours_ = self.data_combo_cours  
        for cours in cours_: 
            self.cours_ids.addItem(cours.get('cours_nom',""), cours.get('id','')) 

        annee_academique.clear()
        annee__ = self.annee_acades
        for annee_acade in annee__:
            annee_academique.addItem(annee_acade.get('annee_academique'), annee_acade.get('id'))
 
        if show_programme:
            id_for_edit_programme.setText(show_programme.get("id",""))
            print(show_programme.get("coefficients",""))
            coefficients.setText(str(show_programme.get("coefficients",0)))
            note_de_passage.setText(str(show_programme.get("note_de_passage",0)))
                # def fill_commbo_with_data(self,name_combo, default_value):
            index = self.niveau_id_in_programme.findData(show_programme.get("niveau_id",""))
            if index >= 0:
                self.niveau_id_in_programme.setCurrentIndex(index)

            self.niveau_id_in_programme.currentIndexChanged.connect(self.selection_changed_niveau_for_combo)

            self.fill_commbo_with_data(self.cours_ids,show_programme.get("Cours_id",""))
            self.fill_commbo_with_data(self.programme_faculte_id,show_programme.get("Faculte_id",""))
            self.fill_commbo_with_data(professeur_id,show_programme.get("professeur_id",""))
            self.fill_combo_box(jours,show_programme.get("jours",""))

            self.fill_commbo_with_data(annee_academique,show_programme.get("annee_academique_id",""))
            self.fill_combo_box(self.session_in_programme,show_programme.get("session",""))

            self.classe_in_programme.clear() 
             
            classe_ =  self.classes_combo # or 
            for item in classe_:
                self.classe_in_programme.addItem(item['nom_classe'], item['id'])  

            # index = self.niveau_id_in_programme.findData(show_programme.get("niveau_id",""))
            # if index >= 0:
            #     self.niveau_id_in_programme.setCurrentIndex(index)    

            self.fill_commbo_with_data(self.classe_in_programme,show_programme.get("class_",""))

            heure.setText(show_programme.get("heure",""))
            self.ui.enregistrer_programme.setText('Modifier')
            supprimer.setText("Annuler")

        def update_classe_in_programme():
            niveau_selected = self.niveau_id_in_programme.currentData() 
            self.classe_in_programme.clear()
            if self.classes_combo:
                filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == niveau_selected]
                for classe in filtered_classes:
                    self.classe_in_programme.addItem(classe.get('nom_classe'), classe.get('id'))

            if self.niveau_id_in_programme.currentText() == 'Universitaire' or self.niveau_id_in_programme.currentText() == 'Technique':
                self.programme_faculte_id.setHidden(False)
                self.session_in_programme.setHidden(False)
                self.programme_faculte_id.setDuplicatesEnabled(False)
                self.session_in_programme.setDuplicatesEnabled(False)
                for fac in self.get_facultes:
                    self.programme_faculte_id.addItem(fac.get('nom'), fac.get('id'))
            else:
                self.session_in_programme.setHidden(True)
                self.programme_faculte_id.setHidden(True)

            if self.niveau_id_in_programme.currentText() == 'Technique':
                self.session_in_programme.setHidden(True)


        self.niveau_id_in_programme.currentIndexChanged.connect(update_classe_in_programme)#self.selection_changed_niveau_for_combo)
        # self.ui.combo_administratif_niveau.currentIndexChanged.connect(
 
        row_layout.setSpacing(7) 
        row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # Ajouter les widgets à la ligne
        row_layout.addWidget(self.niveau_id_in_programme, 0, 0)
        row_layout.addWidget(self.cours_ids, 0, 1) 
        row_layout.addWidget(professeur_id, 0, 2) 
        row_layout.addWidget(annee_academique, 0, 3)

        row_layout.addWidget(self.classe_in_programme, 1, 0)
        row_layout.addWidget(jours, 1, 1) 
        row_layout.addWidget(heure, 1, 2) 
        row_layout.addWidget(self.session_in_programme, 1, 3)
        row_layout.addWidget(self.programme_faculte_id, 2, 0)
        row_layout.addWidget(coefficients, 2, 1)
        row_layout.addWidget(note_de_passage, 2, 2)
         
        row_layout.addWidget(supprimer, 2, 3)
        
        if id_for_edit_programme.text():
            row_layout.addWidget(supprimer_de_la_base, 3, 3)

        self.ui.widget_8.setStyleSheet(
            """
            QComboBox, QLineEdit, QDateEdit { width: 200px; font-size:13pt}
            #supprimer { color: red; font-size:13pt }
            #supprimer_de_la_base { color: red; font-size:13pt }
            #chose_file { 
                border: 1px solid #b23cfd;
                color: #b23cfd;
                padding: 5px;
                border-radius: 5px;
            }
            #supprimer_de_la_base{color: red; font-size:13pt}
      
            #date_edit,#niveau_id,#line_edit1{
            min-width:200px
            }
            #row_frame{border-bottom:1px solid #555;padding:5px}
            """
        )
   
        self.ui.scrollAreaWidgetContents_4.layout().addWidget(row_frame)   

        # self.cours_row_count += 1
        # supprimer_de_la_base.clicked.connect(lambda id=id_for_edit_programme.text(): self.delete_programme(id))
        supprimer_de_la_base.clicked.connect(lambda: self.delete_programme(id_for_edit_programme.text()))

        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, self.programme_dictionary)) 

        self.donnee= {
        'id' : id_for_edit_programme,
        "frame": row_frame,
        'cours_id' : self.cours_ids,
        'professeur_id' : professeur_id,
        'faculte_id' : self.programme_faculte_id,
        'annee_academique' : annee_academique,
        'coefficients' : coefficients,
        'note_de_passage' : note_de_passage,
        'jours' : jours,
        'heure' : heure,
        'session' : self.session_in_programme,
        'class' : self.classe_in_programme,
        'niveau_id' : self.niveau_id_in_programme,
        }
 
        self.programme_dictionary.append(self.donnee) 
 
    def delete_programme(self, id):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce cours",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            response = self.api_handler_.delete_programme(id)
            # if response:
            #     self.programme_index()
        else:
            self.overlay.finish_loading()

    def add_cours_line(self,show_cours=None):        
        row_frame = QFrame() 
        row_layout = QGridLayout()
        row_layout.setContentsMargins(0,0,0,0)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        row_frame.setLayout(row_layout)

        niveau_id = QComboBox()
        # niveau_id.setPlaceholderText("Niveau / Cycle")

        cours_nom = QLineEdit() 
        note_de_passage = QLineEdit() 
        coefficients = QLineEdit() 
        supprimer = QPushButton("Supprimer")
        supprimer_de_la_base = QPushButton("Supprimer de la base")
        id_for_edit_cours =  QLineEdit()
        id_for_edit_cours.setText('')

        supprimer.setFlat(True)
        cours_nom.setPlaceholderText('Nom du cours') 
        note_de_passage.setPlaceholderText('Note de passage') 
        coefficients.setPlaceholderText('Coefficients') 

        supprimer.setObjectName("supprimer")  
        supprimer_de_la_base.setObjectName("supprimer_de_la_base")  
        cours_nom.setObjectName("cours_nom")
        note_de_passage.setObjectName("note_de_passage")
        # niveau_id.setObjectName("niveau_id")
        coefficients.setObjectName("coefficients")

        type_matiere = QComboBox()
        type_matiere.setPlaceholderText("Type matière")
        type_matiere_data = ["Base","Orale"]
        type_matiere.addItems(type_matiere_data)
        type_matiere.setObjectName("type_matiere")

        for niveau in self.niveaux:
            niveau_id.addItem(niveau['name'], niveau['id']) 

        if show_cours:
            print(show_cours) 
            type_ = show_cours.get("type_matiere","") #.lower() 
            id_for_edit_cours.setText(show_cours.get("id",""))
            self.fill_commbo_with_data(niveau_id, show_cours.get("niveau_id",""))
            note_de_passage.setText(show_cours.get("note_de_passage",""))
            coefficients.setText(show_cours.get("coefficients",""))
            cours_nom.setText(show_cours.get("cours_nom",""))
            self.fill_combo_box(type_matiere,type_)
            self.ui.enregistrer_cours.setText("Modifier")
            supprimer.setText("Annuler")
            
        row_layout.setSpacing(15)
        # row_layout.addWidget(niveau_id, 0, 0)
        row_layout.addWidget(type_matiere,0,2)
        row_layout.addWidget(cours_nom, 0, 0) 
        # row_layout.addWidget(note_de_passage, 0, 2) 
        row_layout.addWidget(supprimer, 0, 3)
        if id_for_edit_cours.text():
            row_layout.addWidget(supprimer_de_la_base, 0, 4) 
        row_frame.setStyleSheet("""
            QLineEdit,QComboBox{ width:180px;font-size:13pt }
            #supprimer { color: #fcbc05; font-size:13pt }
            #supprimer_de_la_base { color: red; font-size:13pt } 
            """)
        

        supprimer_de_la_base.clicked.connect(lambda: self.delete_cours(id_for_edit_cours.text()))

        # print(self.ui.scrollAreaWidgetContents_10.layout())
        self.ui.scrollAreaWidgetContents_10.layout().addWidget(row_frame)

        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, self.cours_dictionary)) 

        # Ajouter un document au dictionnaire avec une clé "frame"
        self.donnee = {
            "frame": row_frame,  # Stocker l'objet
            "id":id_for_edit_cours,
            "niveau_id": niveau_id,
            "cours_nom": cours_nom,
            "note_de_passage": note_de_passage,
            "type_matiere": type_matiere,
            "coefficients": coefficients
        }

        self.cours_dictionary.append(self.donnee)

    def clear_cours_and_prog(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)  # Détache le widget de son parent
                    widget.deleteLater()
        self.cours_dictionary.clear()
        self.programme_dictionary.clear()

    def supprimer_ligne(self, row_frame, dictionary):
        """
        Supprime une ligne de formulaire et met à jour le dictionnaire.
        
        :param row_frame: Le widget contenant la ligne.
        :param dictionary: La liste où les données sont stockées.
        """
        # Trouver l'index de l'élément à supprimer dans le dictionnaire
        index_to_remove = None
        for i, data in enumerate(dictionary):
            if data.get("frame") == row_frame:  # Utiliser .get() pour éviter KeyError
                index_to_remove = i
                break

        if index_to_remove is not None:
            del dictionary[index_to_remove]  # Supprimer l'entrée correspondante

        # Supprimer la ligne de l'interface
        layout = row_frame.parent().layout()
        layout.removeWidget(row_frame)
        row_frame.deleteLater()

    def delete_cours(self, id):
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer ce cours",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            response = self.api_handler_.delete_cours(id)
            # delete-cours
            # if response:
            #     self.cours_page()
        else:
            self.overlay.finish_loading()


    def enregistrer_programme(self):
        self.overlay.start_loading("Enregistrement de Programme")
        dictionaryProgramme = []
        for ligne in self.programme_dictionary: 
                      
            ligne_donnees = {                
                'id' : ligne['id'].text(),
                'cours_id' : ligne['cours_id'].currentData(),
                'professeur_id' : ligne['professeur_id'].currentData(),
                'faculte_id' : ligne['faculte_id'].currentData(),
                'annee_academique' : ligne['annee_academique'].currentData(),
                'jours' : ligne['jours'].currentText(),
                'heure' : ligne['heure'].text(),
                'coefficients' : float(ligne['coefficients'].text() or 0) if (ligne['coefficients'] and ligne['coefficients'].text().lower() != "none") else 0.0,
                # 'note_de_passage' : float(ligne['note_de_passage'].text()) if ligne['note_de_passage'] else 0,
                'note_de_passage' : float(ligne['note_de_passage'].text() or 0) if (ligne['note_de_passage'] and ligne['note_de_passage'].text().lower() != "none") else 0.0, 
                'session' : ligne['session'].currentText(),
                'class' : ligne['class'].currentData(),
                'niveau_id' : ligne['niveau_id'].currentData(),
            }
            
            dictionaryProgramme.append(ligne_donnees) 

      
        response = self.api_handler_.enregistrer_programme(programmeCoursObject=dictionaryProgramme) 


    
    # def show_result_after_save_programme(self,response_dict,status_code):
    #     from Controllers.Validator import ValidatorError
    #     if response_dict and 'errors' in response_dict and status_code != 201:
    #         self.overlay.finish_loading()
    #         ve = ValidatorError()
    #         ve.generic_direct_error_message(response_data=response_dict)
    
        
    #     if response_dict and 'success' in response_dict: 
    #         self.programme_index()
    #         self.clear_layout_(self.ui.scrollAreaWidgetContents_10.layout())
    #         self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
    #         QMessageBox.information(self, "Success", f"{response_dict.get('success','')}") 
    #     self.overlay.finish_loading()

    def clear_layout_(self,layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    # Si c'est un layout imbriqué
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clear_layout(sub_layout)


# ==========================================================================================
    def programme_index(self): 
        # self.ui.niveauId.addItem('Section / Niveau / Cycle', None)
        self.ui.class_id.setPlaceholderText('Veuillez choisir le cycle')

        self.go_to_programme_page(self.current_page_programme) 
        self.ui.coursStaked.setCurrentWidget(self.ui.programme_staked_page)
        self.ui.stackedWidgetProgramme.setCurrentWidget(self.ui.index_programme) 
        self.fade_in_page(self.ui.index_programme) 
        # self.ui.titre_toggle.setText("Programme")

    def restart_timer_programme(self):
        self.search_timer_programme.start(300)

    def add_programme_page(self):      

        self.ui.enregistrer_programme.setText("Sauvegarder")
        self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_4.layout())
        self.ui.stackedWidgetProgramme.setCurrentWidget(self.ui.add_programme)
        self.fancy_modal_show(self.ui.add_programme) 

    def go_to_programme_page(self, page):
        self.overlay.start_loading(f"Programme page {page}") 
        self.current_page_programme = page

        anneeId = self.ui.anneeId.currentData()     
        class_id =self.ui.class_id.currentData()     
        niveauId =self.ui.niveauId.currentData()  
        self.api_handler_.all_programme(self.ui.search_programme.text(), page,anneeId,class_id,niveauId)

    def get_programs_by_anneeId(self):
        self.overlay.start_loading(f"Programme {self.ui.anneeId.currentText()}")
        # anneeId = self.ui.anneeId.currentData()     
        # class_id =self.ui.class_id.currentData()     
        # niveauId =self.ui.niveauId.currentData()
        self.api_handler_.all_programme(search=self.ui.search_programme.text(), page=self.current_page_programme,anneeId=self.ui.anneeId.currentData(),class_id=self.ui.class_id.currentData(),niveauId=self.ui.niveauId.currentData())

    def get_programs_by_class_id(self):
        self.overlay.start_loading(f"Programme {self.ui.class_id.currentText()}")
        # anneeId = self.ui.anneeId.currentData()     
        # class_id =self.ui.class_id.currentData()     
        # niveauId =self.ui.niveauId.currentData()
        self.api_handler_.all_programme(search=self.ui.search_programme.text(), page=self.current_page_programme,anneeId=self.ui.anneeId.currentData(),class_id=self.ui.class_id.currentData(),niveauId=self.ui.niveauId.currentData())
        # self.api_handler_.all_programme(search=self.ui.search_programme.text(), page=self.current_page_programme,anneeId=anneeId,class_id=class_id,niveauId=niveauId)

    def get_programs_by_niveauId(self):
        self.overlay.start_loading(f"Programme {self.ui.niveauId.currentText()}")
        # anneeId = self.ui.anneeId.currentData()     
        # class_id =self.ui.class_id.currentData()     
        # niveauId =self.ui.niveauId.currentData()
        self.api_handler_.class_and_other(self.ui.niveauId.currentData())
        self.api_handler_.all_programme(search=self.ui.search_programme.text(), page=self.current_page_programme,anneeId=self.ui.anneeId.currentData(),class_id=self.ui.class_id.currentData(),niveauId=self.ui.niveauId.currentData())
        # self.api_handler_.all_programme(search=self.ui.search_programme.text(), page=self.current_page_programme,anneeId=anneeId,class_id=class_id,niveauId=niveauId)

    def set_table_refresh_data_programme(self):
        header = ("Id", "Cours", "Nveau", "Professeur", "Classe", "Annee")
        self.all_headers_table_labels(
            self.ui.programme_table, header,  "#e2e8f0", 32, 200, 200, 200, 200,200)
        self.ui.programme_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        if self.is_data_updating:
            return

        # Marque la mise à jour comme en cours
        self.is_data_updating = True

        try:
            
            if self.all_programme_data: 
                meta = self.all_programme_data.get("meta","")
                self.total_pages_programme = meta.get("last_page",1)

                self.current_page_programme = meta.get("current_page",1)

                self.ui.prev_programme.setEnabled(self.current_page_programme > 1)
                self.ui.next_programme.setEnabled(self.current_page_programme < self.total_pages_programme)

                self.ui.prev_programme.setStyleSheet("""
                    QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_programme.setStyleSheet("""
                    QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """) 

                self.select_all_populate(self.all_programme_data['data'], self.ui.programme_table, self.on_row_clicked_programme,['id','cours','niveau_name','professeur','classe','annee_academique'])
                self.ui.next_programme.setText('Suivant')
                self.ui.prev_programme.setText('Précédent')
        except Exception as e:
          print(f'Something went wrong {e}')
        finally: 
            self.is_data_updating = False

    def next_programme(self):
        if self.current_page_programme < self.total_pages_programme:
            self.go_to_programme_page(page=self.current_page_programme + 1)

    def prev_programme(self):
        if self.current_page_programme > 1:
            self.go_to_programme_page(page=self.current_page_programme - 1)

    def on_row_clicked_programme(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        # from .ProgrammeController import programme_show
        id_item = self.ui.programme_table.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_programme = self.api_handler_.programme_show(id_item.text())
  


    def enregistrer_cours(self):
        self.overlay.start_loading("Enregistrement de cours")
        dictionaryCourse = []
        for ligne in self.cours_dictionary:   

            ligne_donnees = {
                # 'CoursesObject':{
                "id" :ligne["id"].text(),
                "cours_nom": ligne["cours_nom"].text(),
                "note_de_passage": ligne["note_de_passage"].text(),            
                "type_matiere": ligne["type_matiere"].currentText(),            
                "niveau_id": ligne["niveau_id"].currentData(),
                "coefficients":ligne["coefficients"].text() 
            # }
            }

            dictionaryCourse.append(ligne_donnees)
             # CoursesObject
        # response = self.save_data.enregistrer_cours(CoursesObject=dictionaryCourse)self.api_handler_
        response = self.api_handler_.enregistrer_cours(CoursesObject=dictionaryCourse)
        
        # if 'error' in response:
        #     erreur = response.get("error","")
        #     QMessageBox.warning(None, "Avertissement", f"{erreur}")
        #     QTimer.singleShot(5, self.request_finished)
        #     return
        
        # if 'errors' in response:
        #     erreur = response.get("error","")
        #     QMessageBox.warning(None, "Avertissement", f"Une erreur s'est produite")
        #     QTimer.singleShot(5, self.request_finished)
        #     return
        
        # if 'success' in response:
        #     success = response.get("success","")
        #     self.clear_layout_(self.ui.scrollAreaWidgetContents_10.layout())
        #     QMessageBox.information(self, "Success", f"{success}")
        #     self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_10.layout())
        #     self.cours_page()
        #     self.loadCours()
        #     QTimer.singleShot(5, self.request_finished)
            # return

    # def show_result_after_save_cours(self, response_dict,status):
    #     from Controllers.Validator import ValidatorError
    #     try:
    #         if response_dict and 'errors' in response_dict and status != 201:
    #             self.overlay.finish_loading()
    #             ve = ValidatorError()
    #             ve.generic_direct_error_message(response_data=response_dict)

    #         if response_dict and 'success' in  response_dict:                
    #             self.cours_page()
    #             self.clear_layout_(self.ui.scrollAreaWidgetContents_4.layout())
    #             self.clear_cours_and_prog(self.ui.scrollAreaWidgetContents_4.layout()) 
    #             self.fill_cours_combo() 

    #             QMessageBox.information(self, "Success", f"{response_dict.get('success','')}")
    #         self.overlay.finish_loading()
    #     except Exception as e:
    #         import traceback
    #         traceback.print_exc()
    #         print(e)


# ===========================================  __COURS__ =========================================

# ===========================================  __NOTES__ =========================================

    def notes_page(self): 
        # self.restart_disconnect_timer()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        self.ui.frame_bulletin.setHidden(True)        
        self.save_data_and_exit=False 
        self.set_table_refresh_data_notes()
        self.go_to_note_page(self.current_page_notes)
        # self.set_table_refresh_data_notes()
        self.ui.stackedWidget.setCurrentWidget(self.ui.notes_page)
        self.ui.stackedNotes.setCurrentWidget(self.ui.index_notes)
        self.fade_in_page(self.ui.index_notes) 

    def show_frame_print_bulletin(self, is_checked): 
        self.ui.frame_bulletin.setHidden(not is_checked)
        # print(self.mois)
        

        # Réinitialiser les champs quand le frame est caché
        # if not is_checked:
        #     self.ui.mois_for_bulletin.clear()
        #     self.ui.annee_for_bulletin.clear()
        #     self.ui.classe_for_bulletin.clear()
        #     return  # Sortir de la fonction si le frame est caché

        # Si le frame est visible, nettoyer et remplir les ComboBox
        self.ui.mois_for_bulletin.clear()
        self.ui.mois_for_bulletin.addItem("Annuel")
        for month in self.mois_:
            self.ui.mois_for_bulletin.addItem(month)
  
        self.ui.annee_for_bulletin.clear()
        annee__ = self.annee_acades  
        for annee_acade in annee__:
            self.ui.annee_for_bulletin.addItem(annee_acade.get('annee_academique'), annee_acade.get('id'))

        self.ui.classe_for_bulletin.clear() 
        classe_ =  self.classes_combo  
        for item in classe_:
            self.ui.classe_for_bulletin.addItem(item.get('nom_classe'), item.get('id'))

        # Appliquer le style uniquement si nécessaire
        self.ui.bulletin_dialog.setStyleSheet("""
                QPushButton:checked {
                    background-color: #ffa900;
                    color:#fff
                }
            """)
        self.fancy_modal_show(self.ui.frame_bulletin) 


    # def show_frame_print_bulletin(self, is_checked):

    #     self.ui.frame_bulletin.setHidden(not is_checked)

    #     if is_checked:
    #         mois = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
    #                 "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

    #         self.ui.mois_for_bulletin.clear()
    #         for month in mois:
    #             self.ui.mois_for_bulletin.addItem(month)

              
    #         self.ui.annee_for_bulletin.clear()
    #         for annee_acade in self.annee_acades:
    #             self.ui.annee_for_bulletin.addItem(annee_acade.get('annee_academique'), annee_acade.get('id'))

    #         self.ui.classe_for_bulletin.clear()
    #         for item in self.classes_combo:
    #             self.ui.classe_for_bulletin.addItem(item.get('nom_classe'), item.get('id'))

            # self.ui.bulletin_dialog.setStyleSheet("""
            #     QPushButton:checked {
            #         background-color: #ffa900;
            #         color:#fff
            #     }
            # """)
        

    def clear_layout__(self, widget):
        layout = widget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                w = child.widget()
                if w and not hasattr(self.ui, w.objectName()):  # skip if it's in self.ui
                    w.deleteLater()

    def go_to_note_page(self, page):
        # from .CoursEtudiantController import all_notes
        self.overlay.start_loading(f"Note page {page}") 
        self.current_page_notes = page 
        self.api_handler_.all_notes(self.ui.search_notes.text(), page)

    def restart_timer_note(self):
        self.search_timer_note.start(300)

    def set_table_refresh_data_notes(self):
        header = ("Id", "Identifiant","Nom", "prénom", "Année", 
                  "Niveau", "Classe")
        self.all_headers_table_labels(
            self.ui.notes_table, header,  "#e2e8f0", 32, 200, 130, 250, 165, 165, 200)
        self.ui.notes_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
            
        if self.all_notes_data:  
            try:

                self.current_page_notes =  self.all_notes_data.get("meta", {}).get("current_page", 1)
                self.total_pages_notes =  self.all_notes_data.get("meta", {}).get("last_page", 1) 

                self.ui.prev_notes.setHidden(self.total_pages_notes < 2)
                self.ui.next_notes.setHidden(self.total_pages_notes < 2)
        
                self.ui.prev_notes.setEnabled(self.current_page_notes > 1)
                self.ui.next_notes.setEnabled(self.current_page_notes < self.total_pages_notes)
        
                self.ui.prev_notes.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """)

                self.ui.next_notes.setStyleSheet("""
                    /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                    QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
                """) 
                self.ui.next_notes.setText('Suivant')
                self.ui.prev_notes.setText('Précédent')
        
                self.select_all_populate(self.all_notes_data['data'], self.ui.notes_table, self.on_row_clicked_notes,['id', 'identifiant', 'fname', 'lname', 'annee_academique', 'name', 'nom_classe']) 

            except Exception as e:
                print(f'Something went wrong ;;;;;{e}')
            finally: 
                pass
                # self.is_data_updating = False

    def on_row_clicked_notes(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.notes_table.item(row, 0)  # Colonne 0 = ID
        id_niveau = self.ui.notes_table.item(row, 5)  # Colonne 0 = ID
        if id_item: 
            # if self.all_notes_data:
            #     show_notes = next((item for item in self.all_notes_data['data'] if item['id'] == id_item.text()), None)
            # else:
            #     show_notes = self.fetch_data_.notes_show(id_item.text()) 
            self.action_on_notes(id_item.text(),id_niveau.text())
       
            # return id_item.text()
        
    def next_notes(self):
        if self.current_page_notes < self.total_pages_notes:            
            self.go_to_note_page(page=self.current_page_notes + 1)

    def prev_notes(self):
        if self.current_page_notes > 1:
            self.go_to_note_page(page=self.current_page_notes - 1)

    def show_dialog_for_notes(self):
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        self.ui.frame_bulletin.setHidden(True)
        self.dialog = QDialog(self)
        # self.dialog.setWindowFlags(self.dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.dialog.setModal(True)  
        self.dialog.setFixedSize(900, 250)
        self.dialog.setWindowTitle("Notes")
        
        self.dialog.setObjectName('dialog')
 

        main_layout = QVBoxLayout(self.dialog)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        main_layout.setSpacing(10)

        search_frame = QFrame()
        search_frame.setStyleSheet(
            """
            QComboBox, QLineEdit, QDateEdit { width: 200px; }
          
      
            #date_edit,#niveau_id,#line_edit1{
            min-width:200px
            }
            """
        )
        search_layout = QHBoxLayout(search_frame)
        # --- Niveau ---
        frame_niveau = QFrame()
        layout_niveau = QVBoxLayout(frame_niveau)
        label_niveau = QLabel('Niveau / Section')
        self.niveau_for_note = QComboBox()
        self.niveau_for_note.setPlaceholderText('Section / Niveau / Cycle')
        layout_niveau.addWidget(label_niveau)
        layout_niveau.addWidget(self.niveau_for_note)

        self.niveau_for_note.clear()
        for n in self.niveaux:
            self.niveau_for_note.addItem(n['name'], n['id'])

        self.niveau_for_note.currentIndexChanged.connect(self.fetch_class_and_course)

        # --- Cours ---
        frame_cours = QFrame()
        label_cours = QLabel('Cours / Matière')
        layout_cours = QVBoxLayout(frame_cours)
        self.cours_for_note = QComboBox() 
        self.cours_for_note.clear()
        layout_cours.addWidget(label_cours)
        layout_cours.addWidget(self.cours_for_note)

        # --- Classe ---
        frame_classe = QFrame()
        layout_classe = QVBoxLayout(frame_classe)
        label_classe = QLabel('Classe')
        self.class_for_note = QComboBox()
        layout_classe.addWidget(label_classe)
        layout_classe.addWidget(self.class_for_note)

        # Ajout des cadres au layout principal
        search_layout.addWidget(frame_niveau)
        search_layout.addWidget(frame_cours)
        search_layout.addWidget(frame_classe)

        search_layout.setContentsMargins(0, 0, 0, 0)




        frame_line2 = QFrame()
        frame_line2.setStyleSheet(
            """
            QComboBox, QLineEdit, QDateEdit { width: 200px; }  
              #date_edit,#niveau_id,#line_edit1{
            min-width:200px
            }
            """
        )
        layout_line2 = QHBoxLayout(frame_line2)
        # --- annee_academique ---
        frame_annee_academique = QFrame()
        layout_annee_academique = QVBoxLayout(frame_annee_academique)
        label_annee_academique = QLabel('Annee Academique')
        self.annee_academique_id_for_notes = QComboBox()
        self.annee_academique_id_for_notes.clear()
        annee_acade_ = self.annee_acades
        for annee in annee_acade_:
            self.annee_academique_id_for_notes.addItem(annee['annee_academique'], annee['id'])
        layout_annee_academique.addWidget(label_annee_academique)
        layout_annee_academique.addWidget(self.annee_academique_id_for_notes)

        # --- faculte ---
        # if self.niveau_for_note.currentText() == 'Universitaire':#Universitaire
        self.frame_faculte = QFrame()
        layout_faculte = QVBoxLayout(self.frame_faculte)
        label_faculte = QLabel('Faculté / Option')
        self.faculte__ = QComboBox()
        layout_faculte.addWidget(label_faculte)
        layout_faculte.addWidget(self.faculte__)

        # --- session ---
        self.frame_session = QFrame()
        layout_session = QVBoxLayout(self.frame_session)
        label_session = QLabel('Session')
        self.session__ = QComboBox()
        self.session__.setDuplicatesEnabled(False)
        self.session__.setPlaceholderText("Session")
        self.session__.addItems(["1ère", "2ème"])
        layout_session.addWidget(label_session)
        layout_session.addWidget(self.session__)

        self.frame_faculte.setHidden(True)
        self.frame_session.setHidden(True)

        # Ajout des cadres au layout principal
        search_layout.addWidget(frame_niveau)
        search_layout.addWidget(frame_cours)
        search_layout.addWidget(frame_classe)

        layout_line2.addWidget(frame_annee_academique)
        # if self.niveau_for_note and self.niveau_for_note == 'Universitaire':
        layout_line2.addWidget(self.frame_faculte)
        layout_line2.addWidget(self.frame_session)

        layout_line2.setContentsMargins(0, 0, 0, 0)

        frame_button = QFrame()
        layout_button = QVBoxLayout(frame_button)
        self.valid_button= QPushButton('Valider')
        self.valid_button.setCursor(Qt.PointingHandCursor)
        layout_button.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_button.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.valid_button.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 5px;
                    min-width:120px;
                                 color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px;
                                 font-size:14pt;
                        font-weight:bold;                }
                                 QPushButton:hover { color: #fff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; background-color:#007bff;font-size:16px}
            """)
        layout_button.addWidget(self.valid_button)

        self.valid_button.clicked.connect(self.search_for_enter_notes)
 

        # main_layout.addWidget(self.header_frame, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(search_frame, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(frame_line2, alignment=Qt.AlignmentFlag.AlignTop)   
        main_layout.addWidget(frame_button)   

        self.dialog.setStyleSheet(
            """
            QDialog { border-radius: 10px; background-color: white; }

             QComboBox{ width: 400px; min-height: 32px; max-height: 32px;border: 1px solid #999; border-radius:5px;padding-left:7px}

                         QComboBox:hover,QComboBox:focus {
                
                border: 1px solid #007bff;
            }
                        QComboBox:disabled::drop-down{
               
                color:#555
            }
                        QComboBox:disabled::drop-down, QDateEdit:disabled::drop-down{
                background: transparent;
            }
            QLabel,QComboBox{font-size:14pt}
            """
        )
        self.fade_in_page(self.dialog)
        self.dialog.show()

    
    def on_radio_controle_university_changed(self):
        radio = self.sender()
        if radio.isChecked():
            self.control_university = radio.text()
            print(f"Vous avez sélectionné : {radio.text()}")
    
    def fetch_class_and_course(self, index):        
        selected_id = self.niveau_for_note.currentData() 
      
        if selected_id is None:
            print("No data associated with the selected item.")
            return
         
        self.class_for_note.clear()
        if self.classes_combo:
            filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == selected_id]
            for classe in filtered_classes:
                self.class_for_note.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(selected_id)
            
        #     for classe in self.classes_combo:
        #         self.class_for_note.addItem(classe.get('nom_classe'), classe.get('id')) 

        self.cours_for_note.clear()
        self.course = self.data_combo_cours        
        if self.course:
            for cours in self.course:
                self.cours_for_note.addItem(cours['cours_nom'], cours['id']) 
        else:
            QMessageBox.warning(None, "Avertissement", "Erreur Cours")

        if self.niveau_for_note.currentText() == 'Universitaire' or self.niveau_for_note.currentText() == 'Technique':
            self.frame_faculte.setHidden(False)
            self.frame_session.setHidden(False)
            if self.get_facultes:            
                for faculte in self.get_facultes:
                    self.faculte__.addItem(faculte['nom'], faculte['id']) 
        else:
            self.frame_faculte.setHidden(True)
            self.frame_session.setHidden(True)

        if self.niveau_for_note.currentText() == 'Technique':
            self.frame_session.setHidden(True)

    def show_data_after_search_for_insert_notes(self, response_data):
        
        if response_data and response_data is not None:
            if response_data.get('errors'): 
                erreurs =response.get('errors')
                # self.appliquer_erreurs(erreurs, 
                #     ('cours', self.cours_for_note),
                #     ('class', self.class_for_note),
                #     ('niveau', self.niveau_for_note),
                #     ('annee_academique', self.annee_academique_id_for_notes),
                    
                # )
                
                # if response.get('errors').startswith("Les paramètres des évaluation"):
                #     QMessageBox.warning(None, "Avertissement", f"{erreurs}")
                
                # if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
                #     QMessageBox.warning(None, "Avertissement", erreurs)
                # else:
                #     errors = erreurs or erreurs.get("warning","")
                #     QMessageBox.warning(None, "Erreur", errors)
                if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
                    QMessageBox.warning(None, "Avertissement", erreurs)
                else:
                    # S'assurer que 'erreurs' est un dict et récupérer la clé "warning"
                    if isinstance(erreurs, dict):
                        errors = erreurs.get("warning", str(erreurs))  # par défaut: tout convertir en str
                    else:
                        errors = str(erreurs)

                    QMessageBox.warning(None, "Erreur", errors)
                self.overlay.finish_loading()
            else:
                response = response_data['datas']
                print(response)
                self.data_cours_list = {}
                self.ui.stackedNotes.setCurrentWidget(self.ui.add_notes)
                self.fancy_modal_show(self.ui.add_notes) 
                print(response['session'])
                if 'result' in response:
               
                    if self.ui.widget_notes.layout():
                        self.clear_layout(self.ui.widget_notes.layout()) 
                    else:
                        self.layouts = QVBoxLayout(self.ui.widget_notes)  # Crée un nouveau layout
                    
                    self.ui.frame_355.setHidden(True)
                    self.ui.intra_button.setHidden(True)
                    self.ui.finale_button.setHidden(True)
                    self.ui.combo_evaluation.setHidden(True)

                    if response['examEcheance'] is not None:
                        if response['examEcheance']['evaluation_par']=='Mois' or 'mois':
                            self.controle = 'mois'

                            mois = response['month'] or  self.mois_
                            # for month in response['month']:
                            self.ui.combo_evaluation.setHidden(False)
                            self.ui.combo_evaluation.setPlaceholderText("Evaluation")
                            self.ui.combo_evaluation.clear()
                            for month in mois:
                                self.ui.combo_evaluation.addItem(month)

                        
                    else:
                        self.ui.frame_355.setHidden(False)
                        self.ui.intra_button.setHidden(False)
                        self.ui.finale_button.setHidden(False)
                        self.controle = ''

                    self.ui.change_cours.setPlaceholderText("Cours / Matière")
                    self.get_list_cours = response.get("list_cours","")
                    self.ui.change_cours.clear()
 
                    for cours_ in self.get_list_cours:
                        self.ui.change_cours.addItem(cours_['cours_nom'], cours_['id'])   

                    try:
                        self.ui.change_cours.currentIndexChanged.disconnect()
                    except TypeError as e:
                        print(f"signal__ {e}")
                        pass  # Aucun signal n'était connecté

                    self.ui.change_cours.currentIndexChanged.connect(lambda index, cours_=response['list_cours']: self.get_data_cours_list(cours_))

                    # if response['examEcheance'] in None: # ['name'] != 'Universitaire':
                    #     self.ui.frame_355.setHidden(True)
                    #     self.ui.intra_button.setHidden(True)
                    #     self.ui.finale_button.setHidden(True)
                    # else:
                    #     self.ui.combo_evaluation.setHidden(True)

                
                    self.ui.affiche_cours.setText('----')
                    # self.ui.affiche_cours.setText(response['cours']['cours_nom'])
                    classe_and_annee = response.get('annee','')
                    nom_classe = response['cours'].get("nom_classe", "")
                    session_0 = response['cours'].get("session", "")
                    self.sesson_in_cours = response['cours'].get("session", "")
                    self.ui.affiche_classe.setText(f"{nom_classe}  -  {classe_and_annee} ")
                    # Création du bouton
                    frame_button_note = QFrame()
                    layouts_button_note = QHBoxLayout(frame_button_note) 
                    layouts_button_note.setAlignment(Qt.AlignmentFlag.AlignRight)

                    self.button_q = QPushButton("Enregistrer et quitter")
                    self.button = QPushButton("Enregistrer les notes")
                    layouts_button_note.addWidget(self.button_q)
                    layouts_button_note.addWidget(self.button)
                    if isinstance(response['examEcheance'], str):
                        evaluation_par = json.loads(evaluation_par)

                    if 'session' in response and isinstance(response['session'], str):
                        session = json.loads(response['session']) if response['session'] else None

                    try:
                        self.ui.combo_evaluation.currentIndexChanged.disconnect()
                    except TypeError as e:
                        print(f"signal {e}")
                        pass  # Aucun signal n'était connecté

                    if response['examEcheance'] is not None:
                        if response['examEcheance']['name'] !='Universitaire':
                            session_0=None
                        # if response['examEcheance']['name'] !='Technique':

                    self.ui.combo_evaluation.currentIndexChanged.connect(lambda index, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle: self.edit_data_note_all(session, annee_academique,evaluation_par))
 

                    self.button.clicked.connect(
                        lambda checked, session=session_0,
                            annee_academique=response['annee'],
                            evaluation_par=self.controle,
                            save_data_and_exit=False:
                            self.enregistrer_notes(session, annee_academique, evaluation_par, save_data_and_exit=False)
                    )

                    self.button_q.clicked.connect(lambda checked, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle, save_data_and_exit=True : self.enregistrer_notes(session, annee_academique,evaluation_par,save_data_and_exit=True))
                    
                    self.button.setCheckable(True)
                    self.table_view = QTableView()

                    # Création du modèle de table
                    self.model = QStandardItemModel(len(response['result']), 5)

                    delegate = EnterKeyDelegate(self.table_view)
                    self.table_view.setItemDelegateForColumn(4, delegate)

                    self.model.setHorizontalHeaderLabels(["Id", "Identifiant", "Nom", "Prenom", "Note"])
                    self.table_view.setModel(self.model)
                    self.table_view.setAlternatingRowColors(True)
                    self.table_view.horizontalHeader().setStretchLastSection(True)
                    self.table_view.verticalHeader().setVisible(False)
                    self.table_view.setColumnHidden(0, True) 
                    self.table_view.setColumnWidth(1, 200)
                    self.table_view.setColumnWidth(2, 220)
                    self.table_view.setColumnWidth(3, 300)
                    self.table_view.setColumnWidth(4, 100)  
                    
                    self.table_view.horizontalHeader().setStyleSheet("""
                        QHeaderView::section {
                            background-color: #4b5564;  
                            font-size:13pt;
                            color: white;
                            font-weight: bold;
                            padding: 4px;  
                        }
                    """)

                    self.table_view.setStyleSheet("""
                        alternate-background-color: #e2e8f0;
                                                font-size:12pt;
                        background-color: #fff;
                    """)

                    self.button.setStyleSheet("""
                        QPushButton {
                            text-align: center;
                            padding: 5px;
                            min-width:120px;
                                        color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px;
                                        font-size:14pt;
                                font-weight:bold;                }
                                        QPushButton:hover { color: #fff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; background-color:#007bff;font-size:16px}
                    """)

                    self.button_q.setStyleSheet("""
                        QPushButton {
                            text-align: center;
                            padding: 5px;
                            min-width:120px;
                                        color: #fcbc05; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px;
                                        font-size:14pt;
                                font-weight:bold;                }
                                        QPushButton:hover { color: #fff; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px; background-color:#fcbc05;font-size:16px}
                    """)

                    # Ajout des données à la table
                    for row, data in enumerate(response['result']):
                        item_id = QStandardItem(str(data.get('id', '')))
                        item_identifiant = QStandardItem(str(data.get('identifiant', '')))
                        item_nom = QStandardItem(str(data.get('nom', '')))
                        item_prenom = QStandardItem(str(data.get('prenom', '')))
                        item_note = QStandardItem("")  
                        
                        item_id.setEditable(False)
                        item_identifiant.setEditable(False)
                        item_nom.setEditable(False)
                        item_prenom.setEditable(False)
                        # item_note.setEditable(True)

                        # Aligner le texte au centre pour toutes les cellules
                        for item in [item_id, item_identifiant, item_nom, item_prenom]:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            
                            item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            font = QFont()
                            font.setBold(True)
                            font.setPointSize(15)
                            item_note.setFont(font)  

                            
                            palette = QPalette()
                            palette.setColor(QPalette.Active, QPalette.Text, QColor(0, 0, 255))  # Bleu
                            palette.setColor(QPalette.Inactive, QPalette.Text, QColor(0, 0, 255))  # Bleu si inactif

                            item_note.setForeground(QBrush(QColor(0, 167, 238))) 


                            item_note.setFont(font)

                        self.model.setItem(row, 0, item_id)
                        self.model.setItem(row, 1, item_identifiant)
                        self.model.setItem(row, 2, item_nom)
                        self.model.setItem(row, 3, item_prenom)
                        self.model.setItem(row, 4, item_note)

                    self.layouts.setContentsMargins(20,0,20,5)
                    self.layouts.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                    self.layouts.addWidget(self.table_view)
                    # self.layouts.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight) 
                    self.layouts.addWidget(frame_button_note) 
                    self.overlay.finish_loading()

                self.ui.notes_dialog.disconnect
                self.dialog.close()


    def search_for_enter_notes(self):
        self.overlay.start_loading()
        response = self.api_handler_.students_for_notes(niveau=self.niveau_for_note.currentData(),cours=self.cours_for_note.currentData(),classe=self.class_for_note.currentData(),annee_academique=self.annee_academique_id_for_notes.currentData(), faculte=self.faculte__.currentData(), session=self.session__.currentText())


    def show_result_student_for_notes(self,response):
        from .Validator import ValidatorError
        if response and 'errors' in response:
            self.overlay.finish_loading()
            ve = ValidatorError()
            ve.generic_direct_error_message(response_data=response)
            return
        
        self.show_data_after_search_for_insert_notes(response)
        self.overlay.finish_loading()

        # if response and 'errors' in response:
        #     erreur = response.get('error')
        #     QMessageBox.warning(None, "Avertissement", f"{erreur}") 
        #     self.overlay.finish_loading()
        #     return
        
#         if response and response is not None:
#             if response.get('errors'): 
#                 erreurs =response.get('errors')
#                 self.appliquer_erreurs(erreurs, 
#                     ('cours', self.cours_for_note),
#                     ('class', self.class_for_note),
#                     ('niveau', self.niveau_for_note),
#                     ('annee_academique', self.annee_academique_id_for_notes),
                    
#                 )
                
#                 # if response.get('errors').startswith("Les paramètres des évaluation"):
#                 #     QMessageBox.warning(None, "Avertissement", f"{erreurs}")
                
#                 # if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
#                 #     QMessageBox.warning(None, "Avertissement", erreurs)
#                 # else:
#                 #     errors = erreurs or erreurs.get("warning","")
#                 #     QMessageBox.warning(None, "Erreur", errors)
#                 if isinstance(erreurs, str) and erreurs.startswith("Les paramètres des évaluation"):
#                     QMessageBox.warning(None, "Avertissement", erreurs)
#                 else:
#                     # S'assurer que 'erreurs' est un dict et récupérer la clé "warning"
#                     if isinstance(erreurs, dict):
#                         errors = erreurs.get("warning", str(erreurs))  # par défaut: tout convertir en str
#                     else:
#                         errors = str(erreurs)

#                     QMessageBox.warning(None, "Erreur", errors)
#                 self.overlay.finish_loading()
#             else:
#                 self.data_cours_list = {}
#                 self.ui.stackedNotes.setCurrentWidget(self.ui.add_notes)
#                 # print(response)
#                 if 'result' in response:
#                     # try:
#                     #     self.valid_button.clicked.disconnect()
#                     # except:
#                     #     pass

#                     if self.ui.widget_notes.layout():
#                         self.clear_layout(self.ui.widget_notes.layout()) 
#                     else:
#                         self.layouts = QVBoxLayout(self.ui.widget_notes)  # Crée un nouveau layout
                    
#                     self.ui.frame_355.setHidden(True)
#                     self.ui.intra_button.setHidden(True)
#                     self.ui.finale_button.setHidden(True)
#                     self.ui.combo_evaluation.setHidden(True)

#                     if response['examEcheance'] is not None:
#                         if response['examEcheance']['evaluation_par']=='Mois' or 'mois':
#                             self.controle = 'mois'

#                             mois = response['month'] or  self.mois_
#                             # for month in response['month']:
#                             print("\n\n\n  self.ui.combo_evaluation.setHidden(False)\n\n\n")
#                             self.ui.combo_evaluation.setHidden(False)
#                             self.ui.combo_evaluation.setPlaceholderText("Evaluation")
#                             self.ui.combo_evaluation.clear()
#                             for month in mois:
#                                 self.ui.combo_evaluation.addItem(month)
#                     else:
#                         self.ui.frame_355.setHidden(False)
#                         self.ui.intra_button.setHidden(False)
#                         self.ui.finale_button.setHidden(False)
#                         self.controle = ''

#                     self.ui.change_cours.setPlaceholderText("Cours / Matière")
#                     list_cours = response.get("list_cours","")
#                     self.ui.change_cours.clear()
#                     for cours_ in list_cours:
#                         self.ui.change_cours.addItem(cours_['cours_nom'], cours_['id'])   

#                     try:
#                         self.ui.change_cours.currentIndexChanged.disconnect()
#                     except TypeError as e:
#                         print(f"signal__ {e}")
#                         pass  # Aucun signal n'était connecté

#                     self.ui.change_cours.currentIndexChanged.connect(lambda index, cours_=response['list_cours']: self.get_data_cours_list(cours_))

#                     # if response['examEcheance'] in None: # ['name'] != 'Universitaire':
#                     #     self.ui.frame_355.setHidden(True)
#                     #     self.ui.intra_button.setHidden(True)
#                     #     self.ui.finale_button.setHidden(True)
#                     # else:
#                     #     self.ui.combo_evaluation.setHidden(True)

                
#                     self.ui.affiche_cours.setText('----')
#                     # self.ui.affiche_cours.setText(response['cours']['cours_nom'])
#                     classe_and_annee = response.get('annee','')
#                     nom_classe = response['cours'].get("nom_classe", "")
#                     session_0 = response['cours'].get("session", "")
#                     self.sesson_in_cours = response['cours'].get("session", "")
#                     self.ui.affiche_classe.setText(f"{nom_classe}  -  {classe_and_annee} ")
#                     # Création du bouton
#                     frame_button_note = QFrame()
#                     layouts_button_note = QHBoxLayout(frame_button_note) 
#                     layouts_button_note.setAlignment(Qt.AlignmentFlag.AlignRight)

#                     self.button_q = QPushButton("Enregistrer et quitter")
#                     self.button = QPushButton("Enregistrer les notes")
#                     layouts_button_note.addWidget(self.button_q)
#                     layouts_button_note.addWidget(self.button)
#                     if isinstance(response['examEcheance'], str):
#                         evaluation_par = json.loads(evaluation_par)

#                     if isinstance(response['session'], str):
#                         session = json.loads(response['session'])

#                     try:
#                         self.ui.combo_evaluation.currentIndexChanged.disconnect()
#                     except TypeError as e:
#                         print(f"signal {e}")
#                         pass  # Aucun signal n'était connecté
# #  cours=response['cours'],
#                     self.ui.combo_evaluation.currentIndexChanged.connect(lambda index, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle: self.edit_data_note_all(session, annee_academique,evaluation_par))
# # cours=response['cours']

#                     self.button.clicked.connect(
#                         lambda checked, session=session_0,
#                             annee_academique=response['annee'],
#                             evaluation_par=self.controle,
#                             save_data_and_exit=False:
#                             self.enregistrer_notes(session, annee_academique, evaluation_par, save_data_and_exit)
#                     )

#                     self.button_q.clicked.connect(lambda checked, session=session_0, annee_academique=response['annee'],evaluation_par=self.controle, save_data_and_exit=True : self.enregistrer_notes(session, annee_academique,evaluation_par,save_data_and_exit))
                    
#                     self.button.setCheckable(True)
#                     self.table_view = QTableView()

#                     # Création du modèle de table
#                     self.model = QStandardItemModel(len(response['result']), 5)

#                     delegate = EnterKeyDelegate(self.table_view)
#                     self.table_view.setItemDelegateForColumn(4, delegate)

#                     self.model.setHorizontalHeaderLabels(["Id", "Identifiant", "Nom", "Prenom", "Note"])
#                     self.table_view.setModel(self.model)
#                     self.table_view.setAlternatingRowColors(True)
#                     self.table_view.horizontalHeader().setStretchLastSection(True)
#                     self.table_view.verticalHeader().setVisible(False)
#                     self.table_view.setColumnHidden(0, True) 
#                     self.table_view.setColumnWidth(1, 200)
#                     self.table_view.setColumnWidth(2, 220)
#                     self.table_view.setColumnWidth(3, 300)
#                     self.table_view.setColumnWidth(4, 100)  
                    
#                     self.table_view.horizontalHeader().setStyleSheet("""
#                         QHeaderView::section {
#                             background-color: #4b5564;  
#                             font-size:13pt;
#                             color: white;
#                             font-weight: bold;
#                             padding: 4px;  
#                         }
#                     """)

#                     self.table_view.setStyleSheet("""
#                         alternate-background-color: #e2e8f0;
#                                                   font-size:12pt;
#                         background-color: #fff;
#                     """)

#                     self.button.setStyleSheet("""
#                         QPushButton {
#                             text-align: center;
#                             padding: 5px;
#                             min-width:120px;
#                                         color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px;
#                                         font-size:14pt;
#                                 font-weight:bold;                }
#                                         QPushButton:hover { color: #fff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; background-color:#007bff;font-size:16px}
#                     """)

#                     self.button_q.setStyleSheet("""
#                         QPushButton {
#                             text-align: center;
#                             padding: 5px;
#                             min-width:120px;
#                                         color: #fcbc05; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px;
#                                         font-size:14pt;
#                                 font-weight:bold;                }
#                                         QPushButton:hover { color: #fff; border: 1px solid #fcbc05; border-radius: 5px; padding: 5px 10px; background-color:#fcbc05;font-size:16px}
#                     """)

#                     # Ajout des données à la table
#                     for row, data in enumerate(response['result']):
#                         item_id = QStandardItem(str(data.get('id', '')))
#                         item_identifiant = QStandardItem(str(data.get('identifiant', '')))
#                         item_nom = QStandardItem(str(data.get('nom', '')))
#                         item_prenom = QStandardItem(str(data.get('prenom', '')))
#                         item_note = QStandardItem("")  
                        
#                         item_id.setEditable(False)
#                         item_identifiant.setEditable(False)
#                         item_nom.setEditable(False)
#                         item_prenom.setEditable(False)
#                         # item_note.setEditable(True)

#                         # Aligner le texte au centre pour toutes les cellules
#                         for item in [item_id, item_identifiant, item_nom, item_prenom]:
#                             item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
#                             item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            
#                             item_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

#                             font = QFont()
#                             font.setBold(True)
#                             font.setPointSize(15)
#                             item_note.setFont(font)  

                            
#                             palette = QPalette()
#                             palette.setColor(QPalette.Active, QPalette.Text, QColor(0, 0, 255))  # Bleu
#                             palette.setColor(QPalette.Inactive, QPalette.Text, QColor(0, 0, 255))  # Bleu si inactif

#                             item_note.setForeground(QBrush(QColor(0, 167, 238))) 


#                             item_note.setFont(font)

#                         self.model.setItem(row, 0, item_id)
#                         self.model.setItem(row, 1, item_identifiant)
#                         self.model.setItem(row, 2, item_nom)
#                         self.model.setItem(row, 3, item_prenom)
#                         self.model.setItem(row, 4, item_note)

#                     self.layouts.setContentsMargins(20,0,20,5)
#                     self.layouts.setAlignment(Qt.AlignmentFlag.AlignHCenter)
#                     self.layouts.addWidget(self.table_view)
#                     # self.layouts.addWidget(self.button, alignment=Qt.AlignmentFlag.AlignRight) 
#                     self.layouts.addWidget(frame_button_note) 
#                     self.overlay.finish_loading()

#                 self.ui.notes_dialog.disconnect
#                 self.dialog.close()
#         # QTimer.singleShot(5, self.request_finished)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater() 
                else:
                    layout.removeItem(item) 
                    print(f"layout to delete {layout}")

    def get_data_cours_list(self, cours_list):
        if cours_list:
            self.data_cours_list = next((item for item in cours_list if item['id'] == self.ui.change_cours.currentData()), None)
            self.ui.combo_evaluation.setPlaceholderText("Evaluation")
            self.ui.combo_evaluation.clear()
            for month in self.mois_:
                self.ui.combo_evaluation.addItem(month)
            if self.data_cours_list:
                self.ui.affiche_cours.setText(self.data_cours_list.get('cours_nom'))

            for row in range(self.model.rowCount()):
                item_id = self.model.item(row, 0).text()  
                item_identifiant = self.model.item(row, 1).text()  
                item_note = self.model.item(row, 4).setText('') 

    def edit_data_note_all(self, session, annee_academique,evaluation_par):
    # def edit_data_note_all(self, cours, session, annee_academique,evaluation_par):
        # print(f"self.ui.combo_evaluation.currentText()  {self.ui.combo_evaluation.currentText()}")
        self.overlay.start_loading()
        if not self.ui.change_cours.currentText():
            QMessageBox.warning(None, "Avertissement", "Vous devez choisir dans le champs cours / matière")
            QTimer.singleShot(100, self.overlay.finish_loading)
            return
        # self.overlay.finish_loading()
        notes = []
        evaluation_examen = self.ui.combo_evaluation.currentText()

        
        for row in range(self.model.rowCount()):
            item_id = self.model.item(row, 0).text()  
            item_identifiant = self.model.item(row, 1).text()  
            item_note = self.model.item(row, 4).text()  
            try:
                note = float(item_note)  
            except ValueError:
                note = 0 

            notes.append({"id": item_id,'identifiant':item_identifiant})
        # print(notes,evaluation_examen,cours,annee_academique)
        cours_ = self.data_cours_list.get("cours_nom", "")
        cours_type = self.data_cours_list.get("type_matiere", "")
        response = self.api_handler_.fetch_data_note_for_edit(notes,evaluation_examen,cours_,annee_academique,cours_type)


    def fill_notes_data_for_add_or_edit(self, response_data):
        if self.ui.combo_evaluation.currentText():
            # print(response_data)
            if response_data and 'errors' in response_data:
                self.overlay.finish_loading()
                QMessageBox.warning(None, "Avertissement", 'Erreur !!!')
                return
            
        if response_data and 'success' in response_data:
            notes_dict = {item['etudiant_id']: item['note'] for item in response_data.get('success', [])} 
            for row in range(self.model.rowCount()):
                etudiant_id = self.model.item(row, 0).text()

                if etudiant_id in notes_dict:
                    note_value = str(notes_dict[etudiant_id])
                    self.model.setItem(row, 4, QStandardItem(note_value))
        # self.overlay.start_loading()
        self.overlay.finish_loading()

    def enregistrer_notes(self, session, annee_academique,evaluation_par,save_data_and_exit):
   
        self.overlay.start_loading("Enregistrement des notes") 
        notes = []
        self.save_data_and_exit=save_data_and_exit
        for row in range(self.model.rowCount()):
            item_id = self.model.item(row, 0).text()  
            item_identifiant = self.model.item(row, 1).text()  
            item_note = self.model.item(row, 4).text()  
            try:
                note = float(item_note)  
            except ValueError:
                note = 0 

            notes.append({"id": item_id,'identifiant':item_identifiant, "note": note})
        
        if not self.data_cours_list:
            QTimer.singleShot(100, self.overlay.finish_loading)
            QMessageBox.warning(None, "Avertissement", "Vous devez choisir un cours")
            return
            
        response = self.api_handler_.enregistrer_cours_notes(
                # controle=evaluation_par if evaluation_par is not None or evaluation_par != '' else self.control_university,
                controle = evaluation_par if evaluation_par else self.control_university,
                examen=self.ui.combo_evaluation.currentText(),
                cours=self.data_cours_list.get('cours_nom',''),
                type_matiere=self.data_cours_list.get('type_matiere',''),
                coefficients=self.data_cours_list.get('coefficients',0),
                session=session,  # ou str(session.get('session']) si besoin
                note_de_passage=self.data_cours_list.get('note_de_passage',0.0),
                professeur_id=self.data_cours_list.get('professeur_id',''),
                annee_academique=annee_academique,
                notes=notes
            )



    def show_result_after_save_notes(self,response):
        print(response)
        if response and 'success' in response:
            if self.save_data_and_exit:
                self.notes_page()
                self.clear_layout(self.ui.widget_notes.layout())
            else:
                self.restart_disconnect_timer()
                # self.get_data_cours_list(self.data_cours_list)
                self.ui.combo_evaluation.setPlaceholderText("Evaluation")
                self.ui.combo_evaluation.clear()
                for month in self.mois_:
                    self.ui.combo_evaluation.addItem(month)
                # self.ui.affiche_cours.setText(self.data_cours_list.get('cours_nom'))

                self.ui.change_cours.setPlaceholderText("Cours / Matière")
                self.ui.change_cours.clear()
                for cours_ in self.get_list_cours:
                    self.ui.change_cours.addItem(cours_['cours_nom'], cours_['id']) 

                self.ui.affiche_cours.setText('----')

                for row in range(self.model.rowCount()):
                    item_id = self.model.item(row, 0).text()  
                    item_identifiant = self.model.item(row, 1).text()  
                    item_note = self.model.item(row, 4).setText('0') 
            QMessageBox.information(self, "Success", f"{response.get('success','')}")
        else:
            self.generic_direct_error_message(response)            
        QTimer.singleShot(200, self.overlay.finish_loading)


    def action_print_bulletin(self):
        self.overlay.start_loading(f"Bulletin pour le mois de {self.ui.mois_for_bulletin.currentText()} ")
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        annee_for_bulletin = self.ui.annee_for_bulletin.currentText()
        classe_for_bulletin = self.ui.classe_for_bulletin.currentData()
        mois_for_bulletin = self.ui.mois_for_bulletin.currentText()

        if not annee_for_bulletin or not classe_for_bulletin or not mois_for_bulletin:
            self.overlay.finish_loading()
            QMessageBox.warning(None, "Avertissement", "Les champs obligatoire ne sont pas remplis")
            return
        response = self.api_handler_.student_print_mas_bulletin(annee_academique=annee_for_bulletin, mois=mois_for_bulletin, classe=classe_for_bulletin)

    # def print_direct_mas_bulletin(self, data): 
    #     try:
    #         self.run_async_direct_pdf(self.generate_direct_pdf,"B_mas.html", data)
    #     except Exception as e:
    #         print(e)
    #         import traceback
    #         traceback.print_exc()
    #         self.overlay.finish_loading()


    def action_on_notes(self, id, niveau):
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        if self.dialogs is not None:
            print("Un dialogue existe déjà, il sera fermé.")
            self.dialogs.close()
            self.dialogs.deleteLater()
            self.dialogs = None  # Réinitialisation explicite
            print("Ancien dialog supprimé.") 

        if not hasattr(self, 'dialogs') or self.dialogs is None:
            print("Création d'un nouveau dialogue.")
            self.dialogs = QDialog(self)

            # self.dialogs.setWindowFlags(self.dialogs.windowFlags() | Qt.WindowType.FramelessWindowHint)
            self.dialogs.setModal(True)  
            self.dialogs.setFixedSize(750, 150)
            self.dialogs.setWindowTitle("Bulletin")
            # self.dialogs.setObjectName('dialog_notes')

            main_layout = QVBoxLayout(self.dialogs)

            # Bouton de fermeture
            close_button = QPushButton()
            close_button.clicked.connect(self.dialogs.accept)  

            # Frame pour la recherche
            action_frame = QFrame()
            action_layout = QHBoxLayout(action_frame)
            action_layout.setSpacing(17)
            action_layout.setContentsMargins(10, 0, 10, 0)
            

            self.student_print = QComboBox()
            self.student_print.setPlaceholderText("choisir et imprimer")
            self.student_print.setObjectName("combo_student")
            self.student_print.clear()
            if niveau != 'Universitaire':
                self.student_print.addItem('all')
                for month in self.mois_:
                    self.student_print.addItem(month)
            else:
                # _session = {"1ère":"1ère session", "2ème":"2ème session"}
                self.student_print.addItems(["1ère session", "2ème session"])
                # self.student_print.addItem(month)

            view_button = QPushButton('Voir')
            view_button.setObjectName("view_button")
            # view_button.setCheckable(True)
            # view_button.setAutoExclusive(True)
            view_button.clicked.connect(lambda: self.voir_notes(id))

            edit_button = QPushButton('Modifier')
            edit_button.setObjectName("edit_button")

            delete_button = QPushButton('Supprimer')
            delete_button.setObjectName("delete_button")
            icon_path_close = os.path.join(self.project_dir, 'assets', 'icons', 'close.png')
            close_button.setIcon(QIcon(icon_path_close))

            close_button.setCursor(Qt.PointingHandCursor)
            view_button.setCursor(Qt.PointingHandCursor)
            edit_button.setCursor(Qt.PointingHandCursor)
            delete_button.setCursor(Qt.PointingHandCursor)
            close_button.setFlat(True)

            
            try:
                self.student_print.currentIndexChanged.disconnect()
            except TypeError as e:
                print(f"signal {e}")
                pass 
            self.student_print.currentIndexChanged.connect(lambda indexChange, ids=id: self.print_bulletin(ids))
            action_layout.addWidget(self.student_print)
            action_layout.addWidget(view_button)
            action_layout.addWidget(edit_button)
            action_layout.addWidget(delete_button)

            

            main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
            main_layout.addWidget(action_frame)  

            self.dialogs.setStyleSheet(
                """

                QComboBox{ width: 300px; min-height: 32px; max-height: 32px;border: 1px solid #999;            border-radius:5px;padding-left:7px; font-size:14pt}

                QComboBox:hover,QComboBox:focus {                
                    border: 1px solid #007bff;
                }

                QComboBox:disabled::drop-down{               
                    color:#555
                }
                QComboBox:disabled::drop-down, QDateEdit:disabled::drop-down{
                    background: transparent;
                }

                #view_button {
                        text-align: center;
                        padding: 5px;
                        min-width:100px;
                                    color: #4d8c3f; border: 1px solid #4d8c3f; border-radius: 5px; padding: 5px 10px;
                                    font-size:14pt;
                            font-weight:bold; 
                }
                #view_button:hover { color: #fff; border: 1px solid #4d8c3f; border-radius: 5px; padding: 5px 10px; background-color:#4d8c3f;font-size:16px}

                #edit_button {
                        text-align: center;
                        padding: 5px;
                        min-width:100px;
                                    color: #eb983f; border: 1px solid #eb983f; border-radius: 5px; padding: 5px 10px;
                                    font-size:14pt;
                            font-weight:bold;
                }
                #edit_button:hover { color: #fff; border: 1px solid #eb983f; border-radius: 5px; padding: 5px 10px; background-color:#eb983f;font-size:16px}

                #delete_button {
                        text-align: center;
                        padding: 5px;
                        min-width:100px;
                                    color: #ea4331; border: 1px solid #ea4331; border-radius: 5px; padding: 5px 10px;
                                    font-size:14pt;
                            font-weight:bold; 
                }
                #delete_button:hover { color: #fff; border: 1px solid #ea4331; border-radius: 5px; padding: 5px 10px; background-color:#ea4331;font-size:16px}
                """
            )
               
            self.dialogs.show()
        else:
            print("Un dialogue est déjà ouvert. Aucune action prise.")

    def voir_notes(self, ids):
        if hasattr(self, 'dialogs') and self.dialogs:
            print(f"Fermeture de l'ancien dialog voir_notes: {self.dialogs}")
            self.dialogs.close() 
            self.dialogs.deleteLater()
            del self.dialogs  
            self.dialogs = None  
            print("Ancien dialog supprimé voir_notes")
        QCoreApplication.processEvents() 


        note = self.api_handler_.notes_show(ids)

        if note and 'coursEtudiant' in note and 'mois' in note:
            note_view_frame = QFrame()

            self.note_view_layout = QVBoxLayout(note_view_frame)
            self.note_view_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.table_note_view = QTableView()

            
            mois_list = list(note['mois'].keys())
            entetes = ["Matière", "Coeff."] + mois_list  

            
            nombre_colonnes = len(entetes)
            self.table_note_view_model = QStandardItemModel(0, nombre_colonnes)

            self.table_note_view_model.setHorizontalHeaderLabels(entetes)

            self.table_note_view.setModel(self.table_note_view_model)
            self.table_note_view.setAlternatingRowColors(True)
            self.table_note_view.horizontalHeader().setStretchLastSection(True)
            self.table_note_view.verticalHeader().setVisible(False)
            self.table_note_view.setColumnWidth(0, 150)

            key = note['coursEtudiant']['identifiant']
            data_etudiant = json.loads(note['coursEtudiant']['data_etudiant'])

            if isinstance(data_etudiant, dict) and key in data_etudiant:
                row = 0 

                if 'base' in data_etudiant[key]:
                    for matiere, infos in data_etudiant[key]['base'].items():

                        item_matiere = QStandardItem(str(matiere))
                        item_coeff = QStandardItem(str(infos.get("coefficients", "")))

                       
                        item_matiere.setEditable(False)
                        item_coeff.setEditable(False)

                       
                        self.table_note_view_model.setItem(row, 0, item_matiere)
                        self.table_note_view_model.setItem(row, 1, item_coeff)

                       
                        notes = infos.get("notes", {})
                        for col, mois in enumerate(mois_list, start=2): 
                            note_value = notes.get(mois, "0") 
                            item_note = QStandardItem(str(note_value)) 
                            item_note.setEditable(True) 
                            self.table_note_view_model.setItem(row, col, item_note)  

                        row += 1 

                
                if 'orale' in data_etudiant[key]:
                    for matiere_orale, infos_orale in data_etudiant[key]['orale'].items():

                       
                        item_matiere_orale = QStandardItem(str(matiere_orale))
                        item_coeff_orale = QStandardItem(str(infos_orale.get("coefficients", "")))

                        
                        item_matiere_orale.setEditable(False)
                        item_coeff_orale.setEditable(False)

                       
                        self.table_note_view_model.setItem(row, 0, item_matiere_orale)
                        self.table_note_view_model.setItem(row, 1, item_coeff_orale)

                        # Insérer les notes en fonction des mois définis dans `note['mois']`
                        notes_orale = infos_orale.get("notes", {})
                        for col, mois in enumerate(mois_list, start=2):  # Commencer à la colonne 2
                            note_orale = notes_orale.get(mois, "0")  # Utilise "0" si la note est absente
                            item_note_orale = QStandardItem(str(note_orale))  # Créer un item pour chaque note orale
                            item_note_orale.setEditable(True)  # Permettre l'édition des notes
                            self.table_note_view_model.setItem(row, col, item_note_orale)

                        row += 1  

                
                self.ui.stackedNotes.setCurrentWidget(self.ui.show_note)
                # self.dialogs.close()
                
            else:
                print("Erreur : data_etudiant n'est pas un dict ou la clé est absente")
                QMessageBox.warning(None, "Avertissement", f"Aucune Note trouvée")


            button_layout = QHBoxLayout()
            for col, mois in enumerate(mois_list, start=2):
                button = QPushButton(f"M. {mois}")
                button.setFlat(True)
                button.clicked.connect(lambda checked, col_index=col, col_key=mois: self.handle_column_button_click(col_index, col_key))
                button_layout.addWidget(button)

            # Ajouter le tableau et la ligne des boutons
            self.note_view_layout.addWidget(self.table_note_view)
            self.note_view_layout.addLayout(button_layout)
            self.ui.scrollArea_3.setWidget(note_view_frame)
        else:
            print("Erreur : data_etudiant n'est pas un dict ou la clé est absente")
            QMessageBox.warning(None, "Avertissement", f"Aucune Note trouvée")   

    def handle_column_button_click(self,col_index, col_key): 
        valeurs = {}
        for row in range(self.table_note_view_model.rowCount() - 1): 
            matiere_item = self.table_note_view_model.item(row, 0) 
            valeur_item = self.table_note_view_model.item(row, col_index) 

            if matiere_item and valeur_item:
                matiere = matiere_item.text()
                valeur = valeur_item.text()
                valeurs[matiere] = valeur

        print(f"Modification demandée pour {col_key}: {valeurs}") 

       
    def print_bulletin(self,ids):
        self.overlay.start_loading('Bulletin')
        self.dialogs.close()
        mois = None
        session = None

        if self.student_print.currentText() in self.mois_ or self.student_print.currentText()=='all':
            mois = self.student_print.currentText()
        elif self.student_print.currentText() in ["1ère session", "2ème session"]:
            session = self.student_print.currentText() 
        
        response =self.api_handler_.student_print(ids, mois=mois, session=session)
     

# ===========================================  __NOTES__ =========================================
    def clear_layouts_promus(self):
        if hasattr(self, 'layouts_promus') and self.layouts_promus.layout():
            self.clear_layout(self.layouts_promus.layout())
        else:
            print("layouts_promus n'est pas défini ou n'a pas de layout associé.")
            

    def promus_page(self):
        # self.restart_disconnect_timer()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        self.ui.frame_322.setHidden(True)
        self.ui.niveau_for_promus.clear()
        self.clear_layouts_promus()

        for niveau in self.niveaux:
            self.ui.niveau_for_promus.addItem(niveau['name'], niveau['id'])
        self.ui.niveau_for_promus.currentIndexChanged.connect(self.clear_layouts_promus)
        self.ui.classe_for_promus.currentIndexChanged.connect(self.clear_layouts_promus)

        self.ui.niveau_promus.clear()
        for niveau in self.niveaux:
            self.ui.niveau_promus.addItem(niveau['name'], niveau['id'])

        self.ui.niveau_for_promus.currentIndexChanged.connect(self.change_class_for_promus)
        self.ui.niveau_promus.currentIndexChanged.connect(self.change_class_promus)

        self.annee_ = self.annee_acades
        self.ui.annee_for_promus.clear()
        for annee_acade in self.annee_:
            self.ui.annee_for_promus.addItem(annee_acade['annee_academique'], annee_acade['id']) 
        self.ui.annee_for_promus.currentIndexChanged.connect(self.clear_layouts_promus)

        self.ui.annee_promus.clear()
        for annee_acade in self.annee_:
            self.ui.annee_promus.addItem(annee_acade['annee_academique'], annee_acade['id']) 

        self.ui.stackedWidget.setCurrentWidget(self.ui.promus_page)
        # self.ui.titre_toggle.setText("Promus")

    def change_class_for_promus(self):
        niveau_selected = self.ui.niveau_for_promus.currentData()

        self.ui.classe_for_promus.clear()
        if self.classes_combo:
            filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == niveau_selected]
            for classe in filtered_classes:
                self.ui.classe_for_promus.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(niveau_selected)
            # for classe in classes:
            #     self.ui.classe_for_promus.addItem(classe.get('nom_classe'), classe.get('id'))
                              

    def change_class_promus(self):
        niveau_selected = self.ui.niveau_promus.currentData()
                
        self.ui.classe_promus.clear()
        if self.classes_combo:
            filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == niveau_selected]
            for classe in filtered_classes:
                self.ui.classe_promus.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(niveau_selected)
            # for classe in classes:
            #     self.ui.classe_promus.addItem(classe.get('nom_classe'), classe.get('id'))  


    def rechercher_for_promus(self):
        annee = self.ui.annee_for_promus.currentData()
        niveau = self.ui.niveau_for_promus.currentData()
        classe = self.ui.classe_for_promus.currentData()
        self.overlay.start_loading(f"Recherche pour {self.ui.classe_for_promus.currentText()}")
        response =  self.api_handler_.get_promus(annee=annee, niveau=niveau, classe=classe)


        # if response and 'errors' in response:
        #     self.clear_layouts_promus()
        #     erreurs = response.get('errors', {})

        #     if isinstance(erreurs, dict):
        #         for key, messages in erreurs.items():
        #             if isinstance(messages, list):
        #                 for message in messages:
        #                     QMessageBox.warning(None, f"Avertissement: {key}", message)
        #             else:
        #                 QMessageBox.warning(None, f"Avertissement: {key}", str(messages))
        #     else:
        #         # Gérer le cas où 'errors' est une simple chaîne
        #         QMessageBox.warning(None, "Avertissement", str(erreurs))
        #     return

        
        # if response and 'errors' in response:
        #     self.clear_layouts_promus()
        #     erreurs = response.get('errors', {})
        #     for key, messages in erreurs.items():
        #         if isinstance(messages, list):
        #             for message in messages:
        #                 QMessageBox.warning(None, f"Avertissement: {key}", message)
        #         else:
        #             QMessageBox.warning(None, f"Avertissement: {key}", str(messages))
        #     return
# get-promus
#         if response and 'result' in response:
#             # self.clear_layouts_promus()
#             data = response['result']

#             if not data:
#                 self.ui.frame_322.setHidden(True)
#                 QMessageBox.warning(None, "Avertissement", "Aucune donnée trouvée pour les paramètres fournis")
#                 return

#             if data:
#                 layout = self.ui.frame_321.layout()
#                 if layout is not None:
#                     self.layouts_promus = layout
#                 else:
#                     self.layouts_promus = QVBoxLayout(self.ui.frame_321)

#                 self.table_view_promus = QTableView()
#                 # Création du modèle de table
#                 self.model_promus = QStandardItemModel(len(response['result']), 7)

#                 self.model_promus.setHorizontalHeaderLabels(["Id", "Nom", "Prénom","Total N.", "Total Coéff",  "Moy G.", "Status"])
#                 self.table_view_promus.setModel(self.model_promus)
#                 self.table_view_promus.setAlternatingRowColors(True)
#                 self.table_view_promus.horizontalHeader().setStretchLastSection(True)
#                 self.table_view_promus.verticalHeader().setVisible(False)
#                 self.table_view_promus.setColumnHidden(0, True) 
#                 self.table_view_promus.setColumnWidth(0, 22)
#                 self.table_view_promus.setColumnWidth(1, 220)
#                 self.table_view_promus.setColumnWidth(2, 220)
#                 self.table_view_promus.setColumnWidth(3, 100)
#                 self.table_view_promus.setColumnWidth(4, 100)  
#                 self.table_view_promus.setColumnWidth(5, 100)
#                 self.table_view_promus.setColumnWidth(6, 120)
                
#                 self.table_view_promus.horizontalHeader().setStyleSheet("""
#                     QHeaderView::section {
#                         background-color: #4b5564;  
#                         font-size:13pt;
#                         color: white;
#                         font-weight: bold;
#                         padding: 4px;  
#                     }
#                 """)

#                 self.table_view_promus.setStyleSheet("""
#                     alternate-background-color: #e2e8f0;
#                                                 font-size:12pt;
#                     background-color: #fff;
#                 """)


#                 for row, data in enumerate(response['result']):
#                     item_id = QStandardItem(str(data.get('id', '')))
#                     item_nom = QStandardItem(str(data.get('nom', '')))
#                     item_prenom = QStandardItem(str(data.get('prenom', '')))
#                     item_note = QStandardItem(str(data.get('note', '')))
#                     item_max = QStandardItem(str(data.get('max', '')))
#                     item_moyenne = QStandardItem(str(data.get('moyenne', '')))
#                     item_status = QStandardItem(str(data.get('status', '')))  
                    
#                     item_id.setEditable(False)
#                     item_moyenne.setEditable(False)
#                     item_nom.setEditable(False)
#                     item_prenom.setEditable(False)

#                     for item in [item_id, item_nom, item_prenom,item_note,item_max,item_moyenne,item_status]:
#                         item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

#                         font = QFont()
#                         font.setPointSize(14)
#                         item_moyenne.setFont(font)  


                        
#                         # if float(item_moyenne.text()) >= 6:
#                         if item_status.text() == 'Succès':
#                             item_moyenne.setForeground(QBrush(QColor(0, 167, 238))) 
#                             item_status.setForeground(QBrush(QColor(0, 255, 0)))
#                         else:
#                             item_moyenne.setForeground(QBrush(QColor(255, 0, 0)))
#                             item_status.setForeground(QBrush(QColor(255, 0, 0)))


#                         item_status.setFont(font)

#                     self.model_promus.setItem(row, 0, item_id)
#                     self.model_promus.setItem(row, 1, item_nom)
#                     self.model_promus.setItem(row, 2, item_prenom)
#                     self.model_promus.setItem(row, 3, item_note)
#                     self.model_promus.setItem(row, 4, item_max)
#                     self.model_promus.setItem(row, 5, item_moyenne)
#                     self.model_promus.setItem(row, 6, item_status)

#                 self.ui.frame_322.setHidden(False)
#                 self.layouts_promus.addWidget(self.table_view_promus)
            

    def promus_to(self):
        annee_actuelle = self.ui.annee_for_promus.currentData()
        niveau_actuel = self.ui.niveau_for_promus.currentData()
        classe_actuelle = self.ui.classe_for_promus.currentData()

        annee_f = self.ui.annee_promus.currentData()
        niveau_f = self.ui.niveau_promus.currentData()
        classe_f = self.ui.classe_promus.currentData()
    
        self.overlay.start_loading(f"Promus à la classe {self.ui.classe_promus.currentText()}")
        response =  self.api_handler_.etudiant_promus_to(annee_actuelle=annee_actuelle,niveau_actuel=niveau_actuel,classe_actuelle=classe_actuelle,annee_f=annee_f,niveau_f=niveau_f,classe_f=classe_f)        

    
    def cancel_promus_to(self):
        self.promus_page()

    
    def rapport_page(self):
        # self.restart_disconnect_timer()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(True)
        self.ui.frame_160.setHidden(True)
        self.ui.pedagogique_identifiant.setHidden(True)
        self.overlay.start_loading() 
        self.ui.global_date_debut.setDate(QDate.currentDate())
        self.ui.global_date_fin.setDate(QDate.currentDate())

        self.ui.date_debut_financier.setDate(QDate.currentDate())
        self.ui.date_fin_financier.setDate(QDate.currentDate())

        
        self.ui.administrafif_identifiant.setChecked(True)
        self.ui.combo_administratif_niveau.clear()
        self.ui.combo_pedagogique_niveau.clear()

        for niveau in self.niveaux:
            self.ui.combo_administratif_niveau.addItem(niveau['name'],niveau['id'])
            self.ui.combo_pedagogique_niveau.addItem(niveau['name'],niveau['id'])

        self.ui.combo_administratif_annee.clear()
        self.ui.combo_pedagogique_annee.clear()
        self.ui.combo_pedagogique_mois.clear()

        self.ui.combo_financier_annee.clear()
        self.ui.combo_financier_classe.clear()

        annee_ = self.annee_acades 

        self.ui.combo_financier_annee.addItems([
            "tous les versements",
            "1er Versement",
            "2ème Versement",
            "3ème Versement",
            "4ème Versement"
        ])
        
        self.ui.combo_pedagogique_mois.addItem('Tous les mois')
        for mois in self.mois_:
            self.ui.combo_pedagogique_mois.addItem(mois)

        def update_classes1():
            level_id = self.ui.combo_administratif_niveau.currentData()
            self.ui.combo_administratif_classe.clear()
            self.ui.combo_administratif_classe.addItem('Toutes les classes', 'Toutes les classes')
            filtered = [c for c in self.classes_combo if c.get('niveau_id') == level_id]
            for c in filtered:
                self.ui.combo_administratif_classe.addItem(c.get("nom_classe",""), c.get("id",""))

        def update_classes():
            level_id = self.ui.combo_pedagogique_niveau.currentData()
            self.ui.combo_pedagogique_classe.clear() 
            self.ui.combo_pedagogique_classe.addItem('Toutes les classes', 'Toutes les classes')
            # On filtre les classes qui appartiennent à ce level_id
            filtered = [c for c in self.classes_combo if c.get('niveau_id') == level_id]
            for c in filtered:
                self.ui.combo_pedagogique_classe.addItem(c.get("nom_classe",""), c.get("id",""))

        self.ui.combo_administratif_niveau.currentIndexChanged.connect(update_classes1)
        self.ui.combo_pedagogique_niveau.currentIndexChanged.connect(update_classes)

        # self.ui.repport_type.addItems(['Global','Livres', 'Tissus', 'Fournitures', 'Arriéré'
        # ])

        # self.ui.repport_type.textChanged.connect(self.change_repport_type)
        # self.ui.repport_type.clear()

        self.ui.label_repport_type.setText(self.ui.repport_type.currentText())

        # On initialise une variable pour stocker l'index de l'année active
        active_index = -1
        current_count = 0

        for annee_acade in annee_:
            self.ui.combo_administratif_annee.addItem(annee_acade['annee_academique'], annee_acade['id'])
            self.ui.combo_pedagogique_annee.addItem(annee_acade['annee_academique'], annee_acade['id'])
            # self.ui.combo_financier_annee.addItem(annee_acade['annee_academique'], annee_acade['id'])
            self.ui.financier_annee_academique.addItem(annee_acade['annee_academique'], annee_acade['id'])
            
            # Si le status est égal à 1 (ou "1" selon ton API), on mémorise l'index actuel
            if str(annee_acade.get('status')) == "1":
                active_index = current_count
            
            current_count += 1

        # Après la boucle, si une année active a été trouvée, on positionne les combos dessus
        if active_index != -1:
            self.ui.combo_administratif_annee.setCurrentIndex(active_index)
            self.ui.combo_pedagogique_annee.setCurrentIndex(active_index)
            self.ui.combo_financier_annee.setCurrentIndex(active_index)
            self.ui.financier_annee_academique.setCurrentIndex(active_index)
 

        classe_ =  self.classes_combo 
        if classe_:
            self.ui.combo_financier_classe.addItem("All", "All") 
            for classe in classe_:
                self.ui.combo_financier_classe.addItem(classe.get('nom_classe'), classe.get('id'))
                # self.ui.combo_administratif_classe.addItem(classe.get('nom_classe'), classe.get('id'))
                # self.ui.combo_pedagogique_classe.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(self.ui.combo_administratif_niveau.currentData())
            # for classe in classes: 
            #     self.ui.combo_financier_classe.addItem(classe.get('nom_classe'), classe.get('id')) 
            #     self.ui.combo_administratif_classe.addItem(classe.get('nom_classe'), classe.get('id')) 
            #     self.ui.combo_pedagogique_classe.addItem(classe.get('nom_classe'), classe.get('id')) 
       
        self.overlay.finish_loading()
        self.ui.stackedWidget.setCurrentWidget(self.ui.rapport_page)
        self.fade_in_page(self.ui.rapport_page) 


    def change_repport_type(self):
        
        self.ui.label_repport_type.setText(self.ui.repport_type.currentText()) 
# =======================================================SOU PAJ ELEV==================================

# ======================================  FONKCYON POU KOMBO BOX YO=================================
    def selection_changed_niveau(self, index):        
        selected_id = self.ui.niveau_id.currentData()
        # selected_id = self.ui.niveau_id.itemData(index)
        
        if selected_id is None:
            print("No data associated with the selected item.")
            return
        self.ui.classe_actuelle_id.clear()
        # self.classes = self.api_handler_.class_and_other(selected_id)
       
        # for classe in self.classes:
        #     self.ui.classe_actuelle_id.addItem(classe['nom_classe'], classe['id']) 
        #         self.class_for_note.clear()
        if self.ui.niveau_id.currentText() == 'Universitaire' or self.ui.niveau_id.currentText() == 'Technique':
            self.ui.faculte_id.setHidden(False)
            self.ui.label_146.setHidden(False)
        else:
            self.ui.faculte_id.setHidden(True)
            self.ui.label_146.setHidden(True)
            # self.api_handler_.get_all_faculte()

        if self.classes_combo:
            filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == selected_id]
            for classe in filtered_classes:
                self.ui.classe_actuelle_id.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(selected_id)
        
        if not hasattr(self, "combo_administratif_niveau") or not isValid(self.ui.combo_administratif_niveau):
            selected = self.ui.combo_administratif_niveau.currentData()
            if self.classes_combo:
                filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == selected]
                for classe in filtered_classes:
                    self.ui.combo_administratif_classe.addItem(classe.get('nom_classe'), classe.get('id'))
            else:
                classes = self.api_handler_.class_and_other(selected)

        if not hasattr(self, "combo_pedagogique_niveau") or not isValid(self.ui.combo_pedagogique_niveau):
            selected = self.ui.combo_pedagogique_niveau.currentData()
            if self.classes_combo:
                filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == selected]
                for classe in filtered_classes:
                    self.ui.combo_pedagogique_classe.addItem(classe.get('nom_classe'), classe.get('id'))
            else:
                classes = self.api_handler_.class_and_other(selected)



    def selection_changed(self, source_combobox, target_combobox, data_function):       
        index = source_combobox.currentIndex()
        selected_id = source_combobox.itemData(index)

        if selected_id is None:
            print("Aucune donnée associée à l'élément sélectionné.")
            return None

        target_combobox.clear()
        new_data = data_function(selected_id)

        for item in new_data:
            target_combobox.addItem(item['nom'], item['id'])

        return selected_id  # Retourne l'ID sélectionné
    
    def selection_changed_niveau_for_combo(self):
        niveau_selected = self.niveau_id_in_programme.currentData()
        self.classe_in_programme.clear()
        
        if niveau_selected is None:
            QMessageBox.warning(None,"Avertissement", f"Veuillez remplir la deuxième ligne et supprimer la première ligne avant de continuer.")
        
        if self.classes_combo:
            filtered_classes = [c for c in self.classes_combo if c['niveau_id'] == niveau_selected]
            for classe in filtered_classes:
                self.classe_in_programme.addItem(classe.get('nom_classe'), classe.get('id'))
        else:
            classes = self.api_handler_.class_and_other(niveau_selected)
            # niveau-with-class/
            for classe in self.classes_combo:
                self.classe_in_programme.addItem(classe.get('nom_classe'), classe.get('id')) 

        if self.niveau_id_in_programme.currentText() == 'Universitaire' or self.niveau_id_in_programme.currentText() == 'Technique':
            self.programme_faculte_id.setHidden(False)
            self.session_in_programme.setHidden(False)
            self.programme_faculte_id.setDuplicatesEnabled(False)
            self.session_in_programme.setDuplicatesEnabled(False)
            for fac in self.get_facultes:
                self.programme_faculte_id.addItem(fac.get('nom'), fac.get('id'))
        else:
            self.session_in_programme.setHidden(True)
            self.programme_faculte_id.setHidden(True)

        if self.niveau_id_in_programme.currentText() == 'Technique':
            self.session_in_programme.setHidden(True)




    def selection_changed_classe(self, index):
        """Affiche l'ID correspondant à l'élément sélectionné"""
        selected_id = self.ui.classe_actuelle_id.itemData(index)
        self.class_selected = selected_id 

    def selection_changed_role(self, index):
        """Affiche l'ID correspondant à l'élément sélectionné"""
        selected_id = self.ui.admin_role.itemData(index)
        self.role_selected = selected_id 

# ===========================================================================================================

    def all_headers_table_labels(self, table_name, header: tuple, color, size=30, col1=100, col2=100, col3=100, col4=100, col5=100, col6=100, col7=100, col8=100, colors='#fff', colors_='#666',c_header='#4b5564'):
        table_name.setColumnCount(len(header))
        table_name.setHorizontalHeaderLabels(header)
        table_name.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # table_name.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)  # Colonne 0 fixe
        # table_name.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Colonne 1 ajustable


        # Masquer la première colonne (ex : ID)
        table_name.setColumnHidden(0, True)

        # Ajuster la largeur des colonnes
        column_sizes = [col1, col2, col3, col4, col5, col6, col7, col8]
        for i in range(1, min(len(header), len(column_sizes))):
            table_name.setColumnWidth(i, column_sizes[i - 1])

        # Activer l'alternance des couleurs
        table_name.setAlternatingRowColors(True)
        # table_name.setS
        # Appliquer du padding et un fond coloré à l'en-tête
        if colors != '#fff':
            table_name.horizontalHeader().setVisible(False)
        else:
            table_name.horizontalHeader().setVisible(True)

        # table_name.horizontalHeader().setStyleSheet(
        #     f"
        #     QHeaderView::section {
        #         background-color: c_header;  
        #         color: white;
        #         font-weight: bold;
        #         padding: 1px;  /* Padding */
        #         /* border: 1px solid #ddd;*/
        #     }
        #     "
        # )
        table_name.horizontalHeader().setStyleSheet(
    f"""
    QHeaderView::section {{
        background-color: {c_header};
        color: white;
        font-weight: bold;
        padding: 1px;
    }}
    """
)

        table_name.horizontalHeader().setStretchLastSection(True)
        table_name.verticalHeader().setVisible(False)
        
        table_name.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
 
        table_name.horizontalHeader().setFixedHeight(size)
 
        table_name.verticalHeader().setDefaultSectionSize(size)


        table_name.setStyleSheet(
            f"alternate-background-color: {color}; background-color: {colors}; color: {colors_};"
        )


    def select_all_populate(self, table, table_ui, function_click,_ordre=None):
        table_ui.setRowCount(len(table))     

        if _ordre:
            for row_index, etudiant in enumerate(table):
                for col_index, key in enumerate(_ordre):
                    # value = etudiant.get(key, "")

                    items = QTableWidgetItem(str(etudiant[key]))
                    items.setTextAlignment(Qt.AlignCenter)

                    table_ui.setItem(row_index, col_index, items)
                    # table_ui.setItem(row_index, col_index, QTableWidgetItem(str(value)))items
        else:
            for(index_row, row) in enumerate(table):            
                for(index_cell, cell) in enumerate(row):
                    items = QTableWidgetItem(str(row[cell]))
                    items.setTextAlignment(Qt.AlignCenter)
                    table_ui.setItem(
                        index_row, index_cell, items
                    )

        try:
            table_ui.cellClicked.disconnect()
        except TypeError:
            pass
        table_ui.cellClicked.connect(function_click)

    def appliquer_erreurs(self, erreurs, *champs):
        """
        Applique un style d'erreur aux champs ayant une erreur et enlève l'erreur pour les autres.
        
        :param erreurs: Dictionnaire des erreurs retourné par la réponse.
        :param champs: Liste de tuples (nom_du_champ, champ_ui).
        """
        for nom_champ, champ_ui in champs:
            if nom_champ in erreurs and erreurs[nom_champ]:   
                champ_ui.setStyleSheet("border: 1px solid red;")
            else:
                champ_ui.setStyleSheet("border: 1px solid #ccc;")   

 
    def clear_fields(self, *fields):

        for field in fields:
            # Vérifie si le widget existe encore
            if field is None or not isValid(field):
                continue

            if isinstance(field, QLineEdit):
                field.clear()

            elif isinstance(field, QComboBox):
                field.setCurrentIndex(-1)

            elif isinstance(field, QDateEdit):
                field.setDate(field.minimumDate())

 



    # def select_all_populate(self, table, table_ui, function_click):
    #     self.ui.student_table.setRowCount(len(table))
    #     for(index_row, row) in enumerate(table):
    #         # print(row['identifiant'])
    #         for(index_cell, cell) in enumerate(row):
                             
    #             items = QTableWidgetItem(str(row[cell]))
    #             items.setTextAlignment(Qt.AlignCenter)
    #             # items.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
    #             self.ui.student_table.setItem(
    #                 index_row, index_cell, items
    #             )
    #     self.ui.student_table.cellClicked.connect(self.on_row_clicked)
     

   
    
    # def on_row_clicked(self, row, column):
    #     """Récupère l'ID de la ligne cliquée"""
    #     id_item = self.ui.student_table.item(row, 0)  # Colonne 0 = ID
    #     if id_item: 
    #         show_student = student_show(id_item.text())
    #         self.add_student_page(show_student)
       
    #         return id_item.text()


        

    def search_student(self):
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        self.dialog = QDialog(self)
        
        self.dialog.setModal(True)  
        self.dialog.setWindowTitle("Paiement")
        self.dialog.setFixedSize(650, 400)

        main_layout = QVBoxLayout(self.dialog)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter) 
        # === Ici, on redéfinit dynamiquement la méthode keyPressEvent ===
        def keyPressEvent(event): 
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                print("Enter pressé dans le modal ! ✅")
                self.analyse_row_and_fetch_data()
                # tu peux appeler ici ta fonction
                # ex: self.on_enter_pressed()
            else:
                QDialog.keyPressEvent(self.dialog, event)

        # On attache la méthode à l’instance
        self.dialog.keyPressEvent = keyPressEvent


        # Frame pour la recherche
        search_frame = QFrame()
        search_frame.setFixedHeight(50)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)

        if not hasattr(self, "student_live_seach_input") or not isValid(self.student_live_seach_input):
            self.student_live_seach_input = QLineEdit() 
 
        self.student_live_seach_input.setPlaceholderText("Rechercher un étudiant...")
        self.student_live_seach_input.setObjectName("input_student")
        self.student_live_seach_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connexion pour la recherche en temps réel
        self.student_live_seach_input.textChanged.connect(self.set_table_refresh_data_for_live_search)
        
        search_layout.addWidget(self.student_live_seach_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        show_frame = QFrame()
        show_layout = QVBoxLayout(show_frame)
        show_layout.setContentsMargins(0, 0, 0, 0)

        

        # Création initiale du tableau
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Id","Id","Identifiant", "nom", "Prénom","Code"])
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False) 
        self.table.setColumnWidth(0, 80)
        self.table.setColumnHidden(1, True)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 200)
        self.table.setColumnWidth(4, 200)
        self.table.setColumnHidden(5, True)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.table.setStyleSheet(
            f"alternate-background-color: #f1f1f1; background-color: #fff;"
        )
        show_layout.addWidget(self.table)

        # main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(search_frame)
        main_layout.addWidget(show_frame, 1)   

        self.dialog.setStyleSheet(
            """
            #dialog { border-radius: 10px; background-color: white; }
            #input_student { width: 400px; min-height: 32px; max-height: 32px; }
            """
        ) 
        self.fade_in_page(self.dialog)
        self.dialog.exec()

    def analyse_row_and_fetch_data(self):
        texte = self.student_live_seach_input.text().strip().split('#')[1:]
        if texte:
            try:
                # On prend le premier élément comme index
                index = int(texte[0]) - 1
                if 0 <= index < self.table.rowCount():
                    id_item0 = self.table.item(index, 1)
                    id_item1 = self.table.item(index, 2)
                    id_item2 = self.table.item(index, 3)
                    if id_item0:
                        id_value0 = id_item0.text()
                        id_value1 = id_item1.text() if id_item1 else ""
                        id_value2 = id_item2.text() if id_item2 else ""
                        print('ID:', id_value0, 'Col1:', id_value1, 'Col2:', id_value2)
                        self.overlay.start_loading(f"Recherche de paiement pour {id_item2.text()}")
                        self.api_handler_.get_student_with_params_payment(etudiant=id_item0.text()) 
                        self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement)
                        self.fancy_modal_show(self.ui.add_paiement)
                        self.dialog.close()
            except Exception as e:
                print("Erreur lors de l'analyse de la ligne:", e)


    def set_table_refresh_data_for_live_search(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        self.api_handler_.student_live(self.student_live_seach_input.text().split('#')[0]) 
        data = self.live_search_student 

    def show_student_live(self, data):
        if data and 'data' in data:
            self.table.setRowCount(len(data['data'])) 
            for row_idx, row_data in enumerate(data['data']):
                self.table.setItem(row_idx, 0, QTableWidgetItem(f"#{str(row_idx + 1)}"))
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx + 1, QTableWidgetItem(row_data[value]))
            self.table.cellClicked.connect(self.on_row_clicked_live_search)
        else:
            self.table.setRowCount(0)

        try:
            self.table.cellClicked.disconnect()
        except TypeError:
            pass
        self.table.cellClicked.connect(self.on_row_clicked_live_search)

    
    def on_row_clicked_live_search(self, row, column):
        """Récupère l'ID de la ligne cliquée""" 
        id_item = self.table.item(row, 1)
        n2 = self.table.item(row, 2)
        n = self.table.item(row, 3)
        n4 = self.table.item(row, 4)
        if id_item:  
            if self.data_for_other_transac: 
                nom = n.text()
                prenom = n4.text()
                s_id = id_item.text()                
                display_text = f"{nom} {prenom}" 
                self.ui.combo_transact_identifiant.addItem(display_text, s_id)
            else:
                self.overlay.start_loading(f"Recherche de paiement pour {n.text()}")
                self.api_handler_.get_student_with_params_payment(etudiant=id_item.text()) 

                self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement)
                self.fancy_modal_show(self.ui.add_paiement)
                             
            self.dialog.close()

       
            # return id_item.text()



    def add_scroll_bar(self, data_student):
        self.frames = {}  # Dictionnaire pour stocker les frames
        self.buttons = {}
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignLeft)
        layout.setAlignment(Qt.AlignTop)
        # layout.setSpacing(7)

        for index, data in enumerate(data_student):
            button = QPushButton(f"{data['annee_academique']}")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setObjectName(f"{data['annee_academique']}")

            
            # Créer dynamiquement un QFrame pour chaque bouton
            frame = QFrame()
            frame.setObjectName(f"frame_{index}")
            button.setDefault(True)
            
            # Enregistrer le frame dans un dictionnaire avec l'index
            self.frames[index] = frame
            self.buttons[index] = button 

            # button.returnPressed.connect(lambda: button.click())
            # button.setChecked(True)
            button.clicked.connect(lambda checked, d=data, index=index: self.show_info_to_pay(d, index))
                        # Shortcut Enter
            shortcut = QShortcut(QKeySequence("Return"), button)
            shortcut.activated.connect(button.click)
        #     shortcut1 = QShortcut(QKeySequence(Qt.Key_Return), button)
        # shortcut2 = QShortcut(QKeySequence(Qt.Key_Enter), button)
        # shortcut1.activated.connect(button.click)
        # shortcut2.activated.connect(button.click)

            # Style du bouton
            button.setStyleSheet("""
                QPushButton {
                    padding: 5px;
                    text-align: center;
                    max-width: 130px;
                    border-radius: 5px;
                    font-size: 14pt; font-weight:bold;
                    border: 1px solid #ccc;
                    background: white;
                    color: #999;
                }
                QPushButton:hover {
                    background: #00a7ee;
                                 border:1px solid #00a7ee;
                    color: white;
                }
            
                QPushButton:checked{ 
                    background: #4385f5;
                    border:1px solid #4385f5;
                    color: white;
                                 }
            """)

            layout.addWidget(button)
            layout.addWidget(frame)


        # --- Définir le focus sur le dernier bouton ---
        if self.buttons:
            last_index = max(self.buttons.keys())
            last_button = self.buttons[last_index]
            last_button.setFocus()  # focus sur le dernier
            last_button.setChecked(True)  # optionnel : coche-le
            last_button.click() 
            try:
                self.montant_verser.setFocus()
                print(f"\n\n self.montant_verser.setFocus in buttons.,......\n\n")
            except Exception as e:
                if not hasattr(self, "montant_verser") or not isValid(self.montant_verser):
                    self.montant_verser = QLineEdit(self)
                    self.montant_verser.setFocus()
                print(f"\n\n self.montant_verser.setFocus outer buttons .,.....{e}\n\n")

        scroll_widget.setLayout(layout)
        self.ui.scroll_pay.setWidget(scroll_widget)
        self.ui.scroll_pay.setWidgetResizable(True)

        self.fancy_modal_show(scroll_widget)
        self.ui.scroll_pay.update()  


    def is_json(self,value):
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

    def show_info_to_pay(self, data, index):  
        self.overlay.start_loading("Information sur le paiement")
        # self.overlay.finish_loading()
        # self.clear_all_frames()
        # self.status = False
        # self.balanse = 0
        # self.avance = 0
        # self.avance_sur=''

        # frame = self.frames.get(index)

        # if frame:
        #     layout = frame.layout()
        #     if layout is None:
        #         layout = QVBoxLayout(frame)
        #         layout.setContentsMargins(10,10,60,10)
        #         layout.setSpacing(0)
        #         frame.setLayout(layout)

        anneeFromat = data['annee_academique'].replace('/', '-')
        self.data_and_payment_info = data
        self.index_data_and_payment_info = index
        details = self.api_handler_.toggleAccordionAndPay(
            classeId=data['classeId'],
            anneeId=data['anneeId'],
            niveauId=data['niveauId'],
            studentId=data['studentId'],
            annee_academique=anneeFromat,
            faculte_id=data['faculte_id'] if 'faculte_id' in data else None
        )



    def show_last_payment_and_details_if_exist(self, details):
        # print(details)
        self.clear_all_frames()
        self.status = False
        self.balanse = 0
        self.avance = 0
        self.avance_sur=''
        data = self.data_and_payment_info 
        
        index = self.index_data_and_payment_info

        frame = self.frames.get(index)

        if frame:
            layout = frame.layout()
            if layout is None:
                layout = QVBoxLayout(frame)
                layout.setContentsMargins(10,10,60,10)
                layout.setSpacing(0)
                frame.setLayout(layout)

            if details and 'errors' in details:
                return
            
            if details is None:
                QMessageBox.warning(self, "Erreur", "Les paramètres de paiement ne sont pas définis pour cette classe. Veuillez les configurer dans la page des paramètres.")
                return
            
            if details and 'paiement_details' in details:
                if isinstance(details.get('paiement_details'), str):
                    d=json.loads(details.get('paiement_details'))
                else:
                    d=details.get('paiement_details')            

                date_format = "%d-%m-%Y %H:%M"
                info_paiement = (d.get('paiement_details') or {}).get('info_paiement')
                # info_paiement = d['paiement_details']['info_paiement']

                info_paiement_etudiant = (d.get('paiement_details') or {}).get('details_etudiant') #d['paiement_details']['details_etudiant']

                if info_paiement_etudiant:
                    aide_financiere =info_paiement_etudiant.get('aide_financiere','')
                else:
                    aide_financiere=None
                # latest_date = sorted(info_paiement.keys())[-1]  
                # latest_entry = info_paiement[latest_date]
                aide = details.get('aide_financiere','') if details.get('aide_financiere','') != 'Aucune' else ''

                # sorted_dates = sorted(info_paiement.keys(), key=lambda d: datetime.strptime(d, date_format))

                # 1. On s'assure que info_paiement est un dictionnaire et n'est pas vide
                if isinstance(info_paiement, dict) and info_paiement:
                    try:
                        # 2. On trie les clés (dates)
                        # date_format = "%Y-%m-%d" # Assure-toi que c'est le bon format reçu de l'API
                        sorted_dates = sorted(info_paiement.keys(), key=lambda d: datetime.strptime(d, date_format))

                        latest_entry = None
                        for date in reversed(sorted_dates):
                            entry = info_paiement[date]
                            # Vérification supplémentaire pour entry au cas où
                            if isinstance(entry, dict) and entry.get('status') != 'retourné':
                                latest_entry = entry
                                break
                        
                        # 3. Utilisation de latest_entry...
                        if latest_entry:
                            print(f"Dernier paiement valide trouvé pour la date : {date}")
                            
                    except (ValueError, TypeError) as e:
                        print(f"⚠️ Erreur lors du tri des dates ou format de date invalide : {e}")
                        latest_entry = None
                else:
                    print("ℹ️ info_paiement est vide ou invalide. Impossible de trier.")
                    latest_entry = None

                # latest_entry = None
                # for date in reversed(sorted_dates):
                #     entry = info_paiement[date]
                #     if entry.get('status') != 'retourné':
                #         latest_entry = entry
                #         break
                # total_verse = latest_entry.get('total_verse', 0.0) if latest_entry else None
                # total_verse = latest_entry.get('total_annuel', 0.0) if latest_entry else None

                # if total_verse < total_annuel:
                if latest_entry and latest_entry.get('total_verse', 0.0) < latest_entry.get('total_annuel', 0.0):
                    self.avance=latest_entry['depot_et_avance']
                    self.balanse=latest_entry['balance'] 

                    if 'mois' in d['paiement_details']:           
                        month_pays = d['paiement_details']['mois']
                        
                        if month_pays:
                            dev=data.get('devise','')
                            if details.get('echeance','') != 'mois':
                                latest_pay = sorted(month_pays.keys())[-1]
                                self.avance_sur = f"Avance de {self.avance}{dev} sur le (la) {int(latest_pay.split('_')[1])+1}{'re' if latest_pay.split('_')[1]==0 else 'ème'} {latest_pay.split('_')[0]}"
                            else:
                                latest_pay = sorted(month_pays.keys())[-1]
                                avance_str = next((s for s in latest_entry.get('status_paiement',{}) if s.startswith("Avns:")), None)

                                if avance_str:
                                    valeur_avance = avance_str.replace("Avns: ", "")
                                    av=valeur_avance.split(" ")[1]
                                    self.avance_sur = f"Avance de {self.avance} {dev} sur {av}"
                        else:
                            if 'depot_et_avance' in latest_entry:
                                self.avance_sur = f"Avance de {self.avance}{data['devise']} sur le 1re Versement" 
                elif latest_entry and latest_entry.get('total_verse', 0.0) >= latest_entry.get('total_annuel', 0.0):
                    self.status=True
                else:
                    pass
            
            else:
                print("not in details")

            frame_1 = QFrame()
            vh_layout_1 = QHBoxLayout(frame_1)
            vh_layout_1.setSpacing(0)
            vh_layout_1.setContentsMargins(20,0,10,0)
            frame_1.setObjectName('frame_1')
            vh_layout_1.setAlignment(Qt.AlignRight)
            

            frame_1.setStyleSheet(""" QLabel{color:#777; font-size:15pt} 
                                    #frame_1{border-bottom:1px solid #aaa;max-width:650px}""")
            # print(data)
           
            label_value = QLabel(f"{data['nom_classe']} ({aide})", frame_1)

            vh_layout_1.addWidget(label_value)
            frame_1.setLayout(vh_layout_1)          
            layout.addWidget(frame_1) 

            
            frame2 = QFrame()
            vh_layout2 = QVBoxLayout(frame2)
            vh_layout2.setContentsMargins(20,20,20,10)
            label_montant = QLabel('Montant')
            vh_layout2.setSpacing(0)

            
            label_montant.setStyleSheet(""" QLabel{color:#777}""")
            try: 
                self.montant_verser.setFocus()                
            except Exception as e: 
                if not hasattr(self, "montant_verser") or not isValid(self.montant_verser):
                    self.montant_verser = QLineEdit(self)
                    self.montant_verser.setFocus()
                    
            
            if not self.status:
                label_avance = QLabel(f"{self.avance_sur}")
                vh_layout2.addWidget(label_avance)
            else:
                label_avance = QLabel("Acquitté")
                vh_layout2.addWidget(label_avance)


                
            vh_layout2.addWidget(label_montant)
            vh_layout2.addWidget(self.montant_verser)
            frame2.setLayout(vh_layout2)
            layout.addWidget(frame2)

            if details and details == 'null':
                self.montant_verser.setHidden(True)
                vh_layout2.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                frame2.setMinimumHeight(100)
                frame2.setMinimumWidth(400)
                label_montant.setText('Les paramètres de paiement ne sont pas définis pour cette classe. Veuillez les configurer dans la page des paramètres.')
                label_montant.setWordWrap(True)
                label_montant.setStyleSheet("color:red")
                return
            self.montant_verser.setHidden(False)  

            # ======================================ACCESSOIRES=================================================
            self.accessoire_checkboxes = {}
            self.echeance_checkboxes = {}
            if 'accessoires' not in details or details['accessoires'] is None:
                print("⚠ Aucune donnée pour 'accessoires'")
            else:
                if isinstance(details['accessoires'], str):      
                    accessoires=json.loads(details['accessoires'])
                else:
                    accessoires=details['accessoires']
                for accessoire in accessoires:                
                    type_acc = accessoire.get('type_daccessoire', 'Inconnu')
                    prix_acc = accessoire.get('prix', 'N/A')

                    frame_accessoire = QFrame()
                    accessoire_layout = QHBoxLayout(frame_accessoire)
                    accessoire_layout.setSpacing(0)
                    accessoire_layout.setContentsMargins(20,0,60,10)
                    label_acc = QLabel(f"{type_acc} ({prix_acc})")
                    check_acc = QCheckBox()
                    check_acc.setFixedHeight(15)  
                    frame_accessoire.setStyleSheet("""
                                    QCheckBox {
                                        max-width: 13px;
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        padding-right: 18px; 
                                    }
                                                QLabel{
                                                    color:#777}
                                    QCheckBox:checked {
                                        border: 1px solid #40C057;
                                        border-radius: 4px;
                                        padding-left: 18px; 
                                        padding-right: 0px;
                                    }
                                    QCheckBox::indicator {
                                        /*width: 13px;
                                            height: 13px;*/
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        background-color: #666;
                                    }
                                
                                    """)

                                    #     QCheckBox::indicator:checked {
                                    #     background-color: #40C057;
                                    #     border: 1px solid #40C057;
                                    # }

                    check_acc.repaint() 

                    check_acc.setObjectName(type_acc)

                    self.accessoire_checkboxes[type_acc] = check_acc
                    check_acc.stateChanged.connect(self.verifier_checkboxes)
                    

                    accessoire_layout.addWidget(label_acc)
                    accessoire_layout.addWidget(check_acc)
                    layout.addWidget(frame_accessoire)

                # print(details['montant_par'])
                if 'paiement_details' in details:
                    paiement_details = json.loads(details['paiement_details']) if isinstance(details['paiement_details'], str) and self.is_json(details['paiement_details']) else details['paiement_details'] # json.loads(details['paiement_details'])
                  
                    # print(paiement_details['paiement_details'])
                    if 'accessoires' in paiement_details['paiement_details']:
                        accessoires = paiement_details['paiement_details']['accessoires']
                        if 'accessoire' in accessoires:
                            # accessoire_pay = json.loads(accessoires['accessoire']) if isinstance(accessoire_pay, str) else accessoires['accessoire']
                            accessoire_pay = json.loads(accessoires['accessoire']) if isinstance(accessoires['accessoire'], str) and self.is_json(accessoires['accessoire']) else accessoires['accessoire']
                            for accessoir in accessoire_pay:
                                for name, checkbox in self.accessoire_checkboxes.items():
                                    if accessoir == name:
                                        checkbox.setChecked(True)
                                        checkbox.setDisabled(True)
                                        self.accessoires[name]=True
                                        checkbox.setStyleSheet("""
                                        QCheckBox {
                                            max-width: 13px;
                                            border: 1px solid #40C057;
                                            border-radius: 4px;
                                            padding-left: 18px; 
                                                padding-right: 0px;
                                        }
                                        QCheckBox::indicator {
                                            /*width: 13px;
                                            height: 13px;*/
                                            border: 1px solid #40C057;
                                            border-radius: 4px;
                                            background-color: white;
                                        }
                                        QCheckBox::indicator:checked {
                                            background-color: #40C057;
                                            border: 1px solid #40C057;
                                        }
                                        """)

                                        checkbox.repaint() 
                            #             print(f"accessoir to check{accessoir} --- {name} ")
                            #         print(accessoir,checkbox)
                            # print('=====================================ACCESSOIRES=====================================')
                            # print(f"accessoire_pay:==> {accessoire_pay}")
            # ======================================ACCESSOIRES=================================================

            # ======================================ECHEANCE=================================================
            if 'montant_par' in details:
                montant_par = json.loads(details['montant_par']) if isinstance(details['montant_par'], str) and self.is_json(details['montant_par']) else details['montant_par']
                sorted_items = sorted(
                    montant_par.get(details['echeance'],{}).items(), 
                    key=lambda x: int(x[0].split('_')[1])
                )
                mois_ordonnes = dict(sorted_items)
                for idx,echeance in enumerate(mois_ordonnes):#montant_par[details['echeance']]):
                    frame_echeance = QFrame()
                    # print(idx,echeance,details['echeance'])
                    montant_a_payer = montant_par[details['echeance']].get(echeance)

                    # if details.get('echeance','') == 'mois':
                    #     sorted_items = sorted(
                    #         montant_par.get('mois',{}).items(), 
                    #         key=lambda x: int(x[0].split('_')[1])
                    #     )
                    #     mois_ordonnes = dict(sorted_items)

                    devise = details.get("devise")
 
                    echeance_layout = QHBoxLayout(frame_echeance)

                    aide = details.get('aide_financiere','')

                    if details.get('echeance','') != 'mois':
                        label_echeance = QLabel(f"{idx+1}{'er' if idx == 0 else 'ème'} {details['echeance']} - ({montant_a_payer} {devise})")
                    else: 
                        cles_triees = list(mois_ordonnes.keys())
                        if idx < len(cles_triees):
                            ma_cle = cles_triees[idx] 
                            mois = ma_cle.split('_')[0] 
                            montant = mois_ordonnes[ma_cle] 
                            label_echeance = QLabel(f"{mois} - ({montant} {devise})" )

                    echeance_layout.setSpacing(4)
                    echeance_layout.setContentsMargins(10,9,10,10)
                    check_echeance = QCheckBox()
                    check_echeance.setFixedHeight(15)  

                    frame_echeance.setStyleSheet("""
                                    QCheckBox {
                                        max-width: 13px;
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        padding-right: 18px; 
                                    }
                                                    QLabel{
                                                    color:#777}
                                    QCheckBox:checked {
                                        max-width: 13px;
                                        border: 1px solid #40C057;
                                        border-radius: 4px;
                                        padding-left: 18px; 
                                    }
                                    QCheckBox::indicator {
                                        width: 13px;
                                        height: 13px;
                                        border: 1px solid #666666;
                                        border-radius: 4px;
                                        background-color: #666;
                                    }
                                    
                                    """)
                                    #    QCheckBox::indicator:checked {
                                    #     background-color: #40C057;
                                    #     border: 1px solid #40C057;
                                    # }

                    check_echeance.repaint() 

                    check_echeance.setObjectName(echeance)

                    self.echeance_checkboxes[echeance] = check_echeance
                    check_echeance.stateChanged.connect(self.verifier_echeance)
                    

                    echeance_layout.addWidget(label_echeance)
                    echeance_layout.addWidget(check_echeance)
                    layout.addWidget(frame_echeance)
                    
                    
                if 'paiement_details' in details:
                    paiement_details = json.loads(details['paiement_details']) if isinstance(details['paiement_details'], str) and self.is_json(details['paiement_details']) else details['paiement_details']

                    if paiement_details and 'mois' in paiement_details['paiement_details']:
                        
                        month_pays = paiement_details['paiement_details']['mois']
                        # On récupère et trie les items des checkboxes par l'index (split('_')[1])
                        # checkboxes_items = self.echeance_checkboxes.get('check_echeance', {}).items()

                        # sorted_checkboxes = sorted(
                        #     checkboxes_items, 
                        #     key=lambda x: int(x[0].split('_')[1])
                        #     )
                        sorted_items = sorted(
                            self.echeance_checkboxes.items(), 
                            key=lambda x: int(x[0].split('_')[1])
                        )
               
                        # for mois in month_pays:
                        #     for name, checkbox in sorted_items:
                        #         print(f"\n\n\mois  {mois}  name  {name}   {mois == name}\n\n\n\n  ")
                        #         # Si le mois actuel est dans la liste des mois déjà payés
                        #         if mois == name:
                        #             checkbox.setChecked(True)
                        #             checkbox.setDisabled(True)
                        #             self.mois[name] = True  
                        #             checkbox.setStyleSheet("""
                        #                 QCheckBox {
                        #                     max-width: 13px;
                        #                     border: 1px solid #40C057;
                        #                     border-radius: 4px;
                        #                     padding-left: 18px; 
                        #                     padding-right: 0px
                        #                 }
                        #                 QCheckBox::indicator {
                        #                     width: 13px;
                        #                     height: 13px;
                        #                     border: 1px solid #40C057;
                        #                     border-radius: 4px;
                        #                     background-color: white;
                        #                 }
                        #                 QCheckBox::indicator:checked {
                        #                     background-color: #40C057;
                        #                 }
                        #             """)
                        #             checkbox.repaint() 
                                # else:
                                #     # Optionnel : réinitialiser si ce n'est pas payé
                                #     checkbox.setChecked(False)
                                #     checkbox.setEnabled(True)
                                #     checkbox.setStyleSheet("") # Style par défaut
                            
                            # checkbox.blockSignals(False)
                        for name_paye in month_pays:
                            # On demande à la fenêtre principale de trouver l'enfant qui porte ce nom EXACT
                            # C'est beaucoup plus sûr que de passer par un dictionnaire
                            real_checkbox = self.findChild(QCheckBox, name_paye)
                            
                            if real_checkbox:
                                real_checkbox.blockSignals(True)
                                real_checkbox.setChecked(True)
                                real_checkbox.setDisabled(True)
                                real_checkbox.setStyleSheet("background-color: #40C057; border-radius: 4px;border: 1px solid #40C057;")
                                real_checkbox.blockSignals(False)
                            else:
                                print(f"❌ Impossible de trouver le widget nommé : {name_paye}")
      
                        # for mois in month_pays:
                        #     for name, checkbox in self.echeance_checkboxes.items():
                        #         print(f"\n\n\ncheckbox  {checkbox}\n\n\n\n")
                        #         print(f"\n\n\necheance_checkboxes.items()  {self.echeance_checkboxes.items()}\n\n\n\n")
                        #         if mois == name:
                        #             checkbox.setChecked(True)
                        #             checkbox.setDisabled(True)
                        #             self.mois[name]=True
                        #             checkbox.setStyleSheet("""
                        #             QCheckBox {
                        #                 max-width: 13px;
                        #                 border: 1px solid #40C057;
                        #                 border-radius: 4px;
                        #                 padding-left: 18px; 
                        #                 padding-right: 0px
                        #             }
                        #             QCheckBox::indicator {
                        #                 width: 13px;
                        #                 height: 13px;
                        #                 border: 1px solid #40C057;
                        #                 border-radius: 4px;
                        #                 background-color: white;
                        #             }
                        #             QCheckBox::indicator:checked {
                        #                 background-color: #40C057;
                        #                 border: 1px solid #40C057;
                        #             }
                        #             """)

                        #             checkbox.repaint() 
                        
                        self.must_refresh_paiement=False
                        # if len(month_pays) > 1 and aide_financiere != aide:
                        #     self.must_refresh_paiement=True
                        #     self.valider_paiement(d)
                    # ======================================ECHEANCE=================================================



                # for pay_accessoire in details_level_two['accessoires']['accessoire']

            button_frame = QFrame()
            button_layout = QVBoxLayout(button_frame) 
            # print(d)
            # paiement_det = d.get('paiement_details')
            
            # if (isinstance(paiement_det, dict) and 
            #     len(paiement_det.get('mois', [])) > 1 and 
            #     aide_financiere != aide):
            if d and len(d['paiement_details']['mois']) > 1 and aide_financiere != aide:
                self.must_refresh_paiement=True
                notify = Notify()
                notify.title ="Information"
                notify.message = (
                        "Le statut de cet élève a été modifié. "
                        "Veuillez patienter pendant la finalisation de la mise à jour."
                    )
                notify.send()
                self.valider_paiement(data)

            button = QPushButton("Valider")
            if self.status:# and self.paiement_index.text() is None:
                button.setCheckable(False)
                button.setDisabled(True)
            button.setCheckable(True)
            button.setObjectName("valider")
            button.setCursor(Qt.PointingHandCursor)  
            button_layout.setContentsMargins(30,0,10,6)
            button_layout.setSpacing(5)

            self.montant_verser.returnPressed.connect(lambda: button.click())
            button.clicked.connect(lambda checked, d=data: self.valider_paiement(d)) 
            
            # button.setDefault(True)            # 👈 rend le bouton actif avec la touche Entrée
            # button.setAutoDefault(True)

            button.setStyleSheet("""
                QPushButton {
                    text-align: center;
                    padding: 5px;
                    min-width:120px;
                                    color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px;
                                    font-size:14pt;
                                font-weight:bold;                }
                                    QPushButton:hover { color: #fff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; background-color:#007bff;font-size:16px}
            """)

            button_layout.addWidget(button)  
            button_layout.setAlignment(Qt.AlignRight)  

            layout.addWidget(button_frame) 
        # QTimer.singleShot(5, self.request_finished)
        else:
            print('Not frames')
    

    def verifier_checkboxes(self):
        for name, checkbox in self.accessoire_checkboxes.items():
            if isinstance(checkbox, QCheckBox):  
                checked = checkbox.isChecked()  
                self.accessoires[name] = checked  

                # print(f"{name}: {'✔ Sélectionné' if checked else '❌ Non sélectionné'}")  
            else:
                self.accessoires[name] = False
                # print(f"⚠ Erreur: {name} n'est pas un QCheckBox mais {type(checkbox)}")  

        print("État actuel des accessoires:", self.accessoires)  # Debug



    def verifier_echeance(self):
        for name, checkbox in self.echeance_checkboxes.items():
            if checkbox.isChecked():
                if name not in self.mois:
                    self.mois[name] =True  
                # print(self.mois)
                # print(f"{name} sélectionné")           


    def clear_all_frames(self):
        """ Supprime tous les widgets dans tous les frames enregistrés """
        for frame in self.frames.values():
            layout = frame.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()

    def valider_paiement(self,data):  
        self.overlay.start_loading("Enregistrement des données de paiement")
        self.verifier_checkboxes()
        montant = self.montant_verser.text()
        response = self.api_handler_.enregistrer_paiement(montant_verser=montant,niveau_id=data['niveauId'],etudiant_id=data['studentId'],identifiant=data['identifiant'],classe=data['classeId'],echeance=data['echeance'],prenom=data['prenom'],nom=data['nom'],annee_academique=data['annee_academique'],mois=self.mois,accessoires=self.accessoires,must_refresh_paiement=self.must_refresh_paiement, index_paiement=self.paiement_index.text())
            
        # else:
        #     self.overlay.finish_loading()

    # def result_after_validated_payment(self, response_data, status=None):
    #     from Controllers.Validator import ValidatorError
    #     if response_data and 'errors' in response_data and status != 201:
    #         self.overlay.finish_loading()
    #         ve = ValidatorError()
    #         ve.generic_direct_error_message(response_data=response_data)
    #     if status == 201:
    #         permission = response_data.get("permission", "")
    #         self.request_access_for_delete(permission)
    #         return
        
    #     if status == 422:
    #         QMessageBox.information(self, "Error", f"{response_data.get('errors','')}")
    #         return
        
    #     if response_data and 'route' in response_data:
    #         self.paiement_page() 
    #         self.mois={}
    #         self.accessoires={}
    #         # self.restart_disconnect_timer()
    #         response_dict = response_data
    #         id = response_dict.get('id')
    #         keys = response_dict.get('keys')
    #         self.overlay.start_loading("Générer le reçu")
    #         result = self.api_handler_.recu_paiement(id=id, keys=keys)
            
    #         self.ui.stackedPaiement.setCurrentWidget(self.ui.index_paiement)
    #         self.fade_in_page(self.ui.index_paiement)
    #         self.clear_fields(self.montant_verser)
    #         QMessageBox.information(
    #             self, 
    #             "Succès", 
    #             "Succès ! Attendez patiemment le temps qu'on génère le reçu."
    #         )
    #     else:
    #         errors = response_data.get('errors')
    #         QMessageBox.critical(self, "Erreur", f"{errors}")
    #         self.overlay.finish_loading()

    # def print_paiement_recu__(self,data):

    #     # paiement_details = json.loads(data.get("paiement_details", "{}")) \
    #     #     if isinstance(data.get("paiement_details", {}), str) else data.get("paiement_details", {})
        
    #     # paiement = paiement_details.get('paiement_details', {})
    #     # etudiant = paiement.get('details_etudiant', {})
    #     # mois = paiement.get('mois', {})
    #     # echeance = list(paiement.get('check_echeance', {}).keys())
 

    #     # info_items = list(paiement.get('info_paiement', {}).items())

    #     # if 0 <= keys < len(info_items):
    #     #     date_clef, paiement = info_items[keys] 
    #     # else:
    #     #     print("Index hors limites")
        
        
    #     # data = {
    #     #     "info": self.config_data['data'], 
    #     #     "date": date_clef, 
    #     #     "payment": paiement,
    #     #     "mois" : mois,
    #     #     "echeance_keys":echeance,
    #     #     'etudiant':etudiant,
    #     #     'logo_path':self.icon_path_logo
    #     #     } 

    #     try: 
    #         self.run_async_direct_pdf(self.generate_direct_pdf_with_per,'paiement_recu.html', data)
    #         # env = Environment(loader=FileSystemLoader("templates"))
    #         # template = env.get_template("paiement_recu.html")

    #         # custom_css = CSS(string='''
    #         # @page {
    #         #     size: 11in 8.5in;  /* largeur 11", hauteur 8.5" = paysage */
    #         #     margin: 15mm;
    #         # }
    #         # ''')
        
    #         # rendered_html = template.render(info=data['info'],etudiant=etudiant,date=data["date"],payment=data['paiement'], echeance_keys=data['echeance_keys'],mois=data['mois'])

    #         # HTML(string=rendered_html).write_pdf("recu_paie.pdf", stylesheets=[custom_css])
    #         # print("recu_paie.pdf")
    #         # os.startfile("recu_paie.pdf") 
    #     except Exception as e:
    #         print(e)
    #         import traceback
    #         traceback.print_exc()
    #     self.overlay.finish_loading()



    def save_pdf1(self, pdf_data):
        if not pdf_data:
            print("Données PDF vides, impossible de sauvegarder.")
            return

        # Ouvre une boîte de dialogue pour choisir l'emplacement de sauvegarde
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Enregistrer le bulletin", "bulletin.pdf", "PDF Files (*.pdf)")

        if file_path:
            try:
                with open(file_path, "wb") as f:
                    f.write(pdf_data)
                self.open_pdf(file_path)
                print(f"PDF sauvegardé avec succès à : {file_path}")
            except Exception as e:
                print(f"Erreur lors de la sauvegarde du PDF : {e}")
        else:
            print("Sauvegarde annulée par l'utilisateur.")


    # def open_pdf(filename="bulletin.pdf"):
    #     path = os.path.abspath(filename)  
    #     webbrowser.open(f"file://{path}")
    def open_pdf(self,path):
        # path = os.path.abspath(filename)  
        webbrowser.open(f"file://{path}")


    def open_pdf_directly1(self, pdf_data):
        # import time
        if not pdf_data:
            print("Données PDF vides, impossible de sauvegarder.")
            return

        try:
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_data)
                temp_path = temp_file.name  
         
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                print("Le fichier PDF n'a pas été correctement généré.")
                return
            
            # 
            #time.sleep(0.5) # 
             
            if sys.platform == "win32":
                os.startfile(temp_path)  # Windows
            elif sys.platform == "darwin":
                os.system(f"open \"{temp_path}\"")  # macOS
            else:
                os.system(f"xdg-open \"{temp_path}\"")  # Linux

            print(f"PDF ouvert temporairement : {temp_path}")

        except Exception as e:
            print(f"Erreur lors de l'ouverture du PDF : {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le PDF : {e}")

    def open_pdf_directly2(self, pdf_data):
        if not pdf_data:
            QMessageBox.warning(self, "Erreur", "Données PDF vides, impossible d'ouvrir le fichier.")
            return

        try:
            # Création d'un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_data)
                temp_path = temp_file.name
            
            # Vérification que le fichier a bien été créé
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                QMessageBox.warning(self, "Erreur", "Le fichier PDF n'a pas été correctement généré.")
                return
            
            # Ouverture avec l'application par défaut selon l'OS
            if sys.platform == "win32":
                os.startfile(temp_path)  # Méthode native Windows
            elif sys.platform == "darwin":
                subprocess.run(["open", temp_path], check=True)  # macOS
            else:
                subprocess.run(["xdg-open", temp_path], check=True)  # Linux

            print(f"PDF ouvert avec l'application par défaut: {temp_path}")

        except Exception as e:
            print(f"Erreur lors de l'ouverture du PDF : {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le PDF : {e}")
        finally:
            # Option: supprimer le fichier temporaire plus tard
            pass

    
    def open_pdf_directly(self, pdf_data):

        if not pdf_data:            
            QMessageBox.warning(self, "Erreur", "Aucune donnée PDF reçue.")
            return

        try: 
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_data)
                temp_path = temp_file.name
 
            if os.path.getsize(temp_path) == 0:
                os.remove(temp_path)
                QMessageBox.warning(self, "Erreur", "Le PDF est vide.")
                return 
            if sys.platform == "win32": 
                
                try:
                    os.startfile(temp_path)
                    print("Solution 1: Utilisation de startfile avec vérification")
                    # filename = tempfile.mktemp (".txt")
                    # open (filename, "w").write ("This is a test")
                    # win32api.ShellExecute (
                    # 0,
                    # "print",
                    # temp_path,
                    # '/d:"%s"' % win32print.GetDefaultPrinter (),
                    # ".",
                    # 0
                    # )
                except WindowsError:
                    print("Solution 2: Méthode alternative si startfile échoue")
                    import subprocess
                    subprocess.Popen([temp_path], shell=True)
            else:
                # Mac/Linux : équivalent cross-platform de os.startfile.
                QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec d'ouverture : {str(e)}")
        finally:
            pass

    def open_file_directly(self, file_data, file_type="pdf"):
        """
        file_type peut être "pdf" ou "xlsx"
        """
        if not file_data:            
            QMessageBox.warning(self, "Erreur", "Aucune donnée reçue.")
            return

        try: 
            # On définit l'extension selon le type
            suffix = ".pdf" if file_type == "pdf" else ".xlsx"
            
            # Création du fichier temporaire avec la BONNE extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
    
            if os.path.getsize(temp_path) == 0:
                os.remove(temp_path)
                QMessageBox.warning(self, "Erreur", "Le fichier est vide.")
                return 

            if sys.platform == "win32":
                try:
                    # os.startfile lancera Excel pour un .xlsx et Acrobat pour un .pdf
                    os.startfile(temp_path)
                except WindowsError:
                    import subprocess
                    subprocess.Popen([temp_path], shell=True)
            else:
                # Mac/Linux : QDesktopServices.openUrl ouvre avec l'application
                # par défaut de l'OS (Preview/Acrobat pour un PDF, Excel/Numbers
                # pour un xlsx), équivalent cross-platform de os.startfile.
                QDesktopServices.openUrl(QUrl.fromLocalFile(temp_path))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec d'ouverture : {str(e)}")

# =========================================================================================================
#                                           PARAMETRES                                                      
# ==========================================================================================================
    def actualiser_page(self):
        self.api_handler_.teacher_combo()
        self.api_handler_.cours_combo()
        self.api_handler_.annee_academique()
        self.api_handler_.niveau_index()
        self.api_handler_.classes_show_check()
        # self.api_handler_.all_student_()
        self.api_handler_.get_data_user_for_loans()
        self.api_handler_.get_all_faculte()
        self.api_handler_.roles()
        self.api_handler_.permissions()


    def settings_page(self):
        self.restart_disconnect_timer()
        self.overlay.start_loading()
        self.ui.frame_350.setHidden(True)
        self.ui.frame_408.setHidden(False)
        self.ui.tab_faculte.setHidden(True) 
        
        # self.go_to_paiement_param_page(self.current_page_paiement_params)
        # self.set_table_refresh_data_paiement_params()
        self.ui.stackedWidget.setCurrentWidget(self.ui.param_page)
        # self.fade_in_page(self.ui.param_page)

        # self.ui.tabWidget_params.setCurrentWidget(self.ui.paiement_params)
        self.paiement_params_page()
        

    def paiement_params_page(self):
        self.overlay.start_loading()
        self.go_to_paiement_param_page(self.current_page_paiement_params)
        # self.set_table_refresh_data_paiement_params()
        self.ui.tabWidget_params.setCurrentWidget(self.ui.paiement_params)
        self.fade_in_page(self.ui.paiement_params)
        # self.overlay.finish_loading()
    
    def exam_params_page(self):
        self.overlay.start_loading()
        self.go_to_params_exam_page(self.current_page_param_exam)
        # self.set_table_refresh_data_param_exam()
        self.ui.tabWidget_params.setCurrentWidget(self.ui.ezam_params)
        self.fade_in_page(self.ui.ezam_params)
        # self.overlay.finish_loading()

    def frais_params_page(self):
        self.overlay.start_loading()
        # self.set_table_refresh_data_frais()
        self.go_to_frais_page(self.current_page_frais)
        self.ui.tabWidget_params.setCurrentWidget(self.ui.tab_frais)
        self.fade_in_page(self.ui.tab_frais)
        self.overlay.finish_loading()

    def frais_divers_params_page(self):
        self.overlay.start_loading()
        self.set_table_refresh_data_frais_divers()
        self.ui.tabWidget_params.setCurrentWidget(self.ui.tab_frais_divers)
        self.fade_in_page(self.ui.tab_frais_divers)
        self.overlay.finish_loading()

    def set_table_refresh_data_frais_divers(self, page=1):
        header = ("Id", "Description ",'Niveau','Année','Prix')
        self.all_headers_table_labels(
            self.ui.table_frais_divers, header,  "#e2e8f0", 32, 270, 250, 250, 180)
        self.ui.table_frais.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        table = self.api_handler_.all_frais_divers_param(page=page)
        if self.all_frais_divers:
            self.current_page_frais_divers = self.all_frais_divers.get("current_page","")
            self.total_pages_frais_divers = self.all_frais_divers.get("total_pages","")

            # self.ui.prev_frais_divers.setHidden(self.total_pages_frais_divers < 2)
            # self.ui.next_frais_divers.setHidden(self.total_pages_frais_divers < 2)
    
            # self.ui.prev_frais_divers.setEnabled(self.current_page_frais_divers > 1)
            # self.ui.next_frais_divers.setEnabled(self.current_page_frais_divers < self.total_pages_frais_divers)
    
            self.ui.prev_frais_divers.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_frais_divers.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_frais_divers.setText('Suivant')
            self.ui.prev_frais_divers.setText('Précédent')
    
            self.select_all_populate(self.all_frais_divers['data'], self.ui.table_frais_divers, self.on_row_clicked_frais_divers,['id','description','niveau','annee_academique','prix' ])

    def on_row_clicked_frais_divers(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_frais_divers.item(row, 0)  # Colonne 0 = ID
        if id_item:
            self.api_handler_.frais_divers_param_show(id_item.text())
            # self.add_frais_divers(show_frais_divers)frais-divers-show

    def faculte_params_page(self):
        self.overlay.start_loading()
        self.set_table_refresh_data_faculte()
        self.go_to_faculte_page(self.current_page_faculte)
        self.ui.tabWidget_params.setCurrentWidget(self.ui.tab_faculte)
        self.fade_in_page(self.ui.tab_faculte)
        self.overlay.finish_loading()

    def go_to_faculte_page(self, page):
        self.current_page_faculte = page
        table = self.api_handler_.all_faculte(page=page)

    def set_table_refresh_data_faculte(self, page=1):
        header = ("Id", "Nom ",'Nbres d\'Année / Session','Statut')
        self.all_headers_table_labels(
            self.ui.table_faculte, header,  "#e2e8f0", 32, 300, 300, 200)
        self.ui.table_frais.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        if self.all_faculte:

            # meta = self.all_faculte.get("meta", "")
            # self.current_page_faculte = meta.get("current_page",1)
            # self.total_pages_faculte = meta.get("last_page",1)

            self.current_page_faculte = self.all_faculte.get("meta", {}).get("current_page", 1)
            self.total_pages_faculte = self.all_faculte.get("meta", {}).get("total_pages", 1)#.get("total_pages","")

            # self.ui.prev_faculte.setHidden(self.total_pages_faculte < 2)
            # self.ui.next_faculte.setHidden(self.total_pages_faculte < 2)
    
            # self.ui.prev_faculte.setEnabled(self.current_page_faculte > 1)
            # self.ui.next_faculte.setEnabled(self.current_page_faculte < self.total_pages_faculte)
    
            self.ui.prev_faculte.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_faculte.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_faculte.setText('Suivant')
            self.ui.prev_faculte.setText('Précédent')
    
            self.select_all_populate(self.all_faculte['data'], self.ui.table_faculte, self.on_row_clicked_faculte,['id','nom','nb_annee','status_text'])

    def on_row_clicked_faculte(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_faculte.item(row, 0)  # Colonne 0 = ID
        if id_item:
            self.api_handler_.faculte_param_show(id_item.text())
            #self.add_faculte(show_faculte)

    def annee_params_page(self):
        self.overlay.start_loading()
        self.go_to_anneeAcademique_page(self.current_page_annee)
        self.ui.tabWidget_params.setCurrentWidget(self.ui.tab_annee)
        self.fade_in_page(self.ui.tab_annee)

        # self.api_handler_.annee_academique()
        # self.overlay.finish_loading()

    def class_params_page(self):
        self.overlay.start_loading()
        self.go_to_classes_page(self.current_page_class)
        
        self.ui.tabWidget_params.setCurrentWidget(self.ui.tab_classe)
        self.fade_in_page(self.ui.tab_classe)
        # self.overlay.finish_loading()

#====================================ANNEE ACADEMIQUE=======================================
    def add_year(self, year_edit=None):
        self.overlay.start_loading()
        self.year = Annee_Academique(year_edit)
        self.fancy_modal_show(self.year)
        self.year.ajouter_annee_academique(self.niveaux)
        self.year.ligne_ajoutee.connect(self.set_table_refresh_data_annee_academique)
        # self.overlay.finish_loading()
        self.go_to_anneeAcademique_page(self.current_page_annee)

    def go_to_anneeAcademique_page(self, page):
        self.current_page_annee = page
        self.api_handler_.all_year(page=page)

    def set_table_refresh_data_annee_academique(self, page=1):
        header = ("Id", "Debut","Fin", "A. Académique", 
                  "status")
        self.all_headers_table_labels(
            self.ui.table_annee, header,  "#e2e8f0", 32, 230, 240, 250, 205)
        self.ui.table_annee.setSelectionBehavior(
            QAbstractItemView.SelectRows)
          
        if self.all_anneeAcademique:
            self.current_page_annee = self.all_anneeAcademique.get("meta", {}).get("current_page", 1)
            self.total_pages_annee = self.all_anneeAcademique.get("meta", {}).get("last_page", 1)

            self.ui.prev_annee.setHidden(self.total_pages_annee < 2)
            self.ui.next_annee.setHidden(self.total_pages_annee < 2)
    
            self.ui.prev_annee.setEnabled(self.current_page_annee > 1)
            self.ui.next_annee.setEnabled(self.current_page_annee < self.total_pages_annee)
    
            self.ui.prev_annee.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_annee.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_annee.setText('Suivant')
            self.ui.prev_annee.setText('Précédent')
    
            self.select_all_populate(self.all_anneeAcademique['data'], self.ui.table_annee, self.on_row_clicked_annee,['id',
            'date_debut',
            'date_fin',
            'annee_academique',
            'status'])

    def on_row_clicked_annee(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_annee.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_year = self.api_handler_.year_show(id_item.text())
            # self.add_year(show_year)
            
        
    def next_annee(self):
        if self.current_page_annee < self.total_pages_annee:
            self.go_to_anneeAcademique_page(page=self.current_page_annee + 1)

    def prev_annee(self):
        if self.current_page_annee > 1:
            self.go_to_anneeAcademique_page(page=self.current_page_annee - 1)

#=========================================== CALSSE =================================================
    def add_classe(self, class_to_edit=None):
        self.add_classe_dialog = Add_classe_Dialog(class_to_edit)
        self.fancy_modal_show(self.add_classe_dialog)
        self.add_classe_dialog.enregistrer_classe(self.niveaux)
        self.add_classe_dialog.ligne_ajoutee.connect(self.set_table_refresh_data_classe)
        # self.fill_classe_combo()
        self.go_to_classes_page(self.current_page_class)
 
        
    def go_to_classes_page(self, page):
        self.current_page_class = page
        self.api_handler_.all_classes(page=page)

    def delete_param_classe_from_db(self, row, table_widget):
        """ Action de suppression pour une ligne générique """
        item_id = table_widget.item(row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer la classe l'ID {item_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            response = self.api_handler_.delete_classe(item_id)
           
            table_widget.removeRow(row)
        else:
            self.overlay.finish_loading()
        

    def set_table_refresh_data_classe(self, page=1):
        header = ("Id", "Section/ Cycle / Niveau ","Classe")
        self.all_headers_table_labels(
            self.ui.table_class, header,  "#e2e8f0", 32, 400, 200)
        self.ui.table_class.setSelectionBehavior(
            QAbstractItemView.SelectRows)

        self.ui.table_class.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.table_class.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.ui.table_class, delete_callback=self.delete_param_classe_from_db)
                )
          
        if self.all_classes_paginate:         
            self.current_page_class = self.all_classes_paginate.get("meta", {}).get("current_page", 1)
            self.total_pages_class = self.all_classes_paginate.get("meta", {}).get("last_page", 1)

            self.ui.prev_class.setHidden(self.total_pages_class<2 )
            self.ui.next_class.setHidden(self.total_pages_class<2)
    
            self.ui.prev_class.setEnabled(self.current_page_class > 1)
            self.ui.next_class.setEnabled(self.current_page_class < self.total_pages_class)
    
            self.ui.prev_class.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_class.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_class.setText('Suivant')
            self.ui.prev_class.setText('Précédent')
    
            self.select_all_populate(self.all_classes_paginate['data'], self.ui.table_class, self.on_row_clicked_class, ['id',
            'niveau',
            'nom_classe'])

    def on_row_clicked_class(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_class.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_class = self.api_handler_.classes_show(id_item.text())
            # print(f"show_class === {show_class} \n\n id: {id_item.text()}")
            # self.add_classe(show_class)
        
    def next_class(self):
        if self.current_page_class < self.total_pages_class:
            self.go_to_classes_page(page=self.current_page_class + 1)

    def prev_class(self):
        if self.current_page_class > 1:
            self.go_to_classes_page(page=self.current_page_class - 1)

#=========================================== FRAIS =================================================
    def add_frais(self, frais_edit=None):
        self.frais = Frais_dinscritipn(frais_edit)
        self.fancy_modal_show(self.frais)
        self.frais.enregistrer_frais_inscription(self.niveaux, self.annee_acades)
        self.frais.ligne_ajoutee.connect(self.set_table_refresh_data_frais)
        self.go_to_frais_page(self.current_page_frais)

    def go_to_frais_page(self, page):
        self.current_page_frais = page
        self.api_handler_.all_register_fee(page=page)

        # self.api_handler_.all_classes(page=page)
        

    def set_table_refresh_data_frais(self, page=1):
        header = ("Id", "Section/ Cycle / Niveau ",'Année A.',"frais")
        self.all_headers_table_labels(
            self.ui.table_frais, header,  "#e2e8f0", 32, 300, 300,150)
        self.ui.table_frais.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        # table = self.api_handler_.all_register_fee(page=page)
        if self.all_fee_paginate: 
            meta = self.all_fee_paginate.get("meta", "")

            self.current_page_frais = meta.get("current_page",1)
            self.total_pages_frais = meta.get("last_page",1)

            # self.current_page_frais = table.get("current_page","")
            # self.total_pages_frais = table.get("total_pages","")

            self.ui.prev_frais.setHidden(self.total_pages_frais < 2)
            self.ui.next_frais.setHidden(self.total_pages_frais < 2)
    
            self.ui.prev_frais.setEnabled(self.current_page_frais > 1)
            self.ui.next_frais.setEnabled(self.current_page_frais < self.total_pages_frais)
    
            self.ui.prev_frais.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_frais.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_frais.setText('Suivant')
            self.ui.prev_frais.setText('Précédent')
    
            self.select_all_populate(self.all_fee_paginate['data'], self.ui.table_frais, self.on_row_clicked_frais, ['id','niveau', 'annee_academique','prix'])

    def on_row_clicked_frais(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_frais.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_frais = self.api_handler_.register_fee_show(id_item.text())
            # self.add_frais(show_frais)
        
    def next_frais(self):
        if self.current_page_frais < self.total_pages_frais:
            self.set_table_refresh_data_frais(page=self.current_page_frais + 1)

    def prev_frais(self):
        if self.current_page_frais > 1:
            self.set_table_refresh_data_frais(page=self.current_page_frais - 1)
#=========================================== FRAIS Divers =================================================
    def add_frais_divers(self, frais_divers_edit=None):
        self.frais_divers = Frais_divers(frais_divers_edit)
        self.fancy_modal_show(self.frais_divers)
        self.frais_divers.enregistrer_frais_divers(self.niveaux, self.annee_acades)
        self.frais_divers.ligne_ajoutee.connect(self.set_table_refresh_data_frais_divers)
    
    def add_faculte(self, faculte_edit=None):
        self.faculte = Faculte(faculte_edit)
        self.fancy_modal_show(self.faculte)
        self.faculte.enregistrer_faculte(self.niveaux)
        self.faculte.ligne_ajoutee.connect(self.set_table_refresh_data_faculte)

#========================================= PARAMS EXAM =============================================
    def add_param_exam(self, exam_to_edit=None):
        self.param_exam = Param_Exam(exam_to_edit)
        self.fancy_modal_show(self.param_exam)
        self.exam = self.param_exam.enregistrer_parametres_examen(self.niveaux, self.annee_acades)
        self.param_exam.ligne_ajoutee.connect(self.set_table_refresh_data_param_exam)
        self.go_to_params_exam_page(self.current_page_param_exam)

    def go_to_params_exam_page(self, page):
        self.current_page_param_exam = page
        self.api_handler_.all_params_exam(page=page)
        

    def set_table_refresh_data_param_exam(self, page=1):
        header = ("Id", "Section/ Cycle / Niveau ","Evaluation /","Année A.")
        self.all_headers_table_labels(
            self.ui.table_param_exam, header,  "#e2e8f0", 32, 300, 300,100)
        self.ui.table_param_exam.setSelectionBehavior(
            QAbstractItemView.SelectRows)
 

        self.ui.table_param_exam.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.table_param_exam.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(pos, self.ui.table_param_exam, delete_callback=self.delete_param_exam_from_db)
                )
          

        if self.all_params_exam:        
            self.current_page_param_exam = self.all_params_exam.get("meta", {}).get("current_page", 1)
            self.total_pages_param_exam = self.all_params_exam.get("meta", {}).get("last_page", 1)

            self.ui.prev_param_exam.setHidden(self.total_pages_param_exam < 2)
            self.ui.next_param_exam.setHidden(self.total_pages_param_exam < 2)
    
            self.ui.prev_param_exam.setEnabled(self.current_page_param_exam > 1)
            self.ui.next_param_exam.setEnabled(self.current_page_param_exam < self.total_pages_param_exam)
    
            self.ui.prev_param_exam.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_param_exam.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_param_exam.setText('Suivant')
            self.ui.prev_param_exam.setText('Précédent')
    
            self.select_all_populate(self.all_params_exam['data'], self.ui.table_param_exam, self.on_row_clicked_param_exam, ['id',
            'niveau_name',
            'evaluation_par',
            'annee_academique'])

    def delete_param_exam_from_db(self, row, table_widget):
        """ Action de suppression pour une ligne générique """
        item_id = table_widget.item(row, 0).text()  # Suppose que l'ID est dans la première colonne
        
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Voulez-vous vraiment supprimer l'examen avec l'ID {item_id} ?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            response = self.api_handler_.delete_params_exam(item_id)
           
            table_widget.removeRow(row)
        else:
            self.overlay.finish_loading()

    def on_row_clicked_param_exam(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_param_exam.item(row, 0)  # Colonne 0 = ID
        if id_item:
            show_param_exam = self.api_handler_.params_exam_show(id_item.text())
            # self.add_param_exam(show_param_exam)
            


    def next_param_exam(self):
        if self.current_page_param_exam < self.total_pages_param_exam:
            self.go_to_params_exam_page(page=self.current_page_param_exam + 1)

    def prev_param_exam(self):
        if self.current_page_param_exam > 1:
            self.go_to_params_exam_page(page=self.current_page_param_exam - 1)


#=========================================== PAIEMENT PARAMS =================================================
    def add_paiement_params(self, data=None):
        self.pay = Main_payment(data, self.get_facultes)
        # self.fancy_modal_show(self.pay)
        self.pay.ouvrir_dialog_paiement(self.niveaux, self.annee_acades)
        self.pay.ligne_ajoutee.connect(self.set_table_refresh_data_paiement_params)
        # self.overlay.finish_loading()
        self.go_to_paiement_param_page(self.current_page_paiement_params)
        
    def go_to_paiement_param_page(self, page):
        # self.overlay.finish_loading()
        self.current_page_paiement_params = page
        self.api_handler_.all_payment_param(page=page)

    def set_table_refresh_data_paiement_params(self, page=1):
        header = ("Id", 'Montant',"Section/ Cycle / Niveau ",'Classe',"Paiement par","Année A.")
        self.all_headers_table_labels(
            self.ui.table_paiement_params, header,  "#e2e8f0", 32, 250, 200, 250, 200,130)
        self.ui.table_paiement_params.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        # self.ui.table_paiement_params.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.ui.table_paiement_params.customContextMenuRequested.connect(self.show_context_menu)


        if self.all_paiement_params:            
            self.current_page_paiement_params = self.all_paiement_params.get("meta", {}).get("current_page", 1)
            self.total_pages_paiement_params = self.all_paiement_params.get("meta", {}).get("last_page", 1)


            self.ui.prev_paiement_params.setHidden(self.total_pages_paiement_params < 2)
            self.ui.next_paiement_params.setHidden(self.total_pages_paiement_params < 2)
    
            self.ui.prev_paiement_params.setEnabled(self.current_page_paiement_params > 1)
            self.ui.next_paiement_params.setEnabled(self.current_page_paiement_params < self.total_pages_paiement_params)
    
            self.ui.prev_paiement_params.setStyleSheet("""
            /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """)

            self.ui.next_paiement_params.setStyleSheet("""
                /* QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; } */
                QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
            """) 
            self.ui.next_paiement_params.setText('Suivant')
            self.ui.prev_paiement_params.setText('Précédent')
    
            self.select_all_populate(self.all_paiement_params['data'], self.ui.table_paiement_params, self.on_row_clicked_paiement_params, ['id',
            'montant',
            'niveau_name',
            'classe',
            'paiement_par',
            'anneeAc'])

    def on_row_clicked_paiement_params(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.table_paiement_params.item(row, 0) 
        if id_item:
            show_paiement_params = self.api_handler_.payment_param_show(id_item.text())
            # self.add_paiement_params(show_paiement_params)
            # self.ui.table_paiement_params.setContextMenuPolicy(Qt.CustomContextMenu)
            # self.ui.table_paiement_params.customContextMenuRequested.connect(self.show_context_menu)
            # print(show_notes, id_item.text())
            # self.action_on_notes(show_notes['mois'] if 'mois' in show_notes else{}, show_notes['coursEtudiant']['id'] if 'coursEtudiant' in show_notes else{})
       
            # return id_item.text()
        
    def next_paiement_params(self):
        # print(self.current_page_paiement_params + 1)
        if self.current_page_paiement_params < self.total_pages_paiement_params:
            self.go_to_paiement_param_page(page=self.current_page_paiement_params + 1)

    def prev_paiement_params(self):
        if self.current_page_paiement_params > 1:
            self.go_to_paiement_param_page(page=self.current_page_paiement_params - 1)


# ============================================RAPPORT__ ================================================

    def print_global_report(self):
        type_ = self.ui.repport_type.currentText()
        self.overlay.start_loading(f"Rapport {type_}")

        response = self.api_handler_.global_rapport(self.ui.global_date_debut.date().toString("yyyy-MM-dd"), self.ui.global_date_fin.date().toString("yyyy-MM-dd"), type_)


    def administratif_imprimer(self):
        self.overlay.start_loading("Rapport administratif")
        check = self.ui.administrafif_identifiant.isChecked()

        response = self.api_handler_.administratif_imprimer_rapport(
        identifiant=check,
        classe=self.ui.combo_administratif_classe.currentData(),
        annee_ac=self.ui.combo_administratif_annee.currentData(),
        cycle=self.ui.combo_administratif_niveau.currentData())
            # pass

    def print_desicion_de_fin_dannee(self):
        self.overlay.start_loading("Désicion de fin d'année") 
        self.api_handler_.desicion_de_fin_dannee( 
        classe=self.ui.combo_pedagogique_classe.currentData(),
        annee_ac=self.ui.combo_pedagogique_annee.currentData(),
        is_excel=False
        )
     
    def print_desicion_de_fin_dannee_excel(self): 
        self.is_excel=True
        self.overlay.start_loading("Désicion de fin d'année Excel") 
        self.api_handler_.desicion_de_fin_dannee( 
        classe=self.ui.combo_pedagogique_classe.currentData(),
        annee_ac=self.ui.combo_pedagogique_annee.currentData(),
        is_excel=True
        )

    def pedagogique_imprimer(self):
        self.overlay.start_loading("Rapport pédagogique pdf")
        check = self.ui.pedagogique_identifiant.isChecked()
         
        response = self.api_handler_.pedagogique_imprimer_rapport(
        identifiant=check,
        classe=self.ui.combo_pedagogique_classe.currentData(),
        annee_ac=self.ui.combo_pedagogique_annee.currentData(),
        cycle=self.ui.combo_pedagogique_niveau.currentData(),
        mois=self.ui.combo_pedagogique_mois.currentText())

    def pedagogique_imprimer_exel(self):
        self.overlay.start_loading("Rapport pédagogique format exel")
        check = self.ui.pedagogique_identifiant.isChecked()
        # if not self.token_manager.get_direct_request():
        response = self.api_handler_.pedagogique_imprimer_rapport_exel(
        identifiant=check,
        classe=self.ui.combo_pedagogique_classe.currentData(),
        annee_ac=self.ui.combo_pedagogique_annee.currentData(),
        cycle=self.ui.combo_pedagogique_niveau.currentData())
 

    def financier_imprimer(self):
        self.overlay.start_loading("Rapport financier")
        annee_financier =self.ui.financier_annee_academique.currentData()
        # annee_financier =self.ui.financier_annee_academique.currentText()
        # self.ui.date_debut_financier.date().toString("yyyy-MM-dd")
        response = self.api_handler_.financier_imprimer_rapport(classe=self.ui.combo_financier_classe.currentText(),date_debut=annee_financier, date_fin=self.ui.date_fin_financier.date().toString("yyyy-MM-dd"), versement=self.ui.combo_financier_annee.currentText())

 

    def show_context_menu(self, pos, table_widget, delete_callback,modify_item=None):
        """ Afficher le menu contextuel lors d'un clic droit """
        
        if not table_widget:
            return 

        # 1. On trouve l'index de la ligne
        index = table_widget.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()

        # --- L'EMPLACEMENT EST ICI ---
        table_widget.selectRow(row) 
        # -----------------------------

        # 2. On crée le menu
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { border: 1px solid #ccc; padding: 5px; }")
        modify_action = QAction("Modifier", self)
        modify_action.triggered.connect(lambda: modify_item(row))
        
        delete_action = QAction("Supprimer", self)
        delete_action.triggered.connect(lambda: delete_callback(row, table_widget))

        menu.addAction(modify_action)
        menu.addAction(delete_action)

        # 3. On affiche le menu
        menu.exec(table_widget.mapToGlobal(pos))

    # Dans Controllers/Main.py
    def activate_window(self):
        if self.isMinimized():
            self.showNormal()  
        self.show()
        self.raise_()
        self.activateWindow()

    # def activate_window(self):
    #     self.show()
    #     self.raise_()
    #     self.activateWindow()


    # def delete_param_exam_from_db(self, row, table_widget):
    #     """ Action de suppression pour une ligne générique """
    #     item_id = table_widget.item(row, 0).text()  # Suppose que l'ID est dans la première colonne
        
    #     reply = QMessageBox.question(
    #         self,
    #         "Confirmation",
    #         f"Voulez-vous vraiment supprimer l'examen avec l'ID {item_id} ?",
    #         QMessageBox.Yes | QMessageBox.No
    #     )

    #     if reply == QMessageBox.Yes:
    #         # Suppression dans la base de données
    #         print(f"Suppression de l'examen avec l'ID {item_id} de la base de données.")
            
    #         # Logique de suppression dans la base de données ici...
            
    #         # Suppression dans la table de l'UI
    #         table_widget.removeRow(row)



    # def show_context_menu(self, pos, delete_callback=None):
    #     """ Afficher un menu contextuel dynamique pour n'importe quel tableau, avec un callback pour suppression """
    #     # Détecter le tableau cible à partir de la position de clic (ici, on suppose qu'il y a un tableau avec un nom unique)
    #     table_widget = self.sender()  # Obtenir le widget de la table qui a déclenché l'événement
        
    #     # Si le tableau est un QTableWidget (ou QTableView si tu veux gérer les deux)
    #     row = table_widget.rowAt(pos.y())  # Récupérer la ligne à la position du clic
    #     column = table_widget.columnAt(pos.x())  # Récupérer la colonne à la position du clic
        
    #     # Créer le menu contextuel
    #     menu = QMenu(self)
        
    #     # Récupérer la donnée à afficher dans le menu (ici, on prend la première cellule de la ligne cliquée)
    #     item_text = table_widget.item(row, column).text() if table_widget.item(row, column) else "Inconnu"
        
    #     # Ajouter des actions génériques
    #     modify_action = QAction(f"Modifier '{item_text}'", self)
    #     modify_action.triggered.connect(lambda: self.modify_item(table_widget, row, column))
        
    #     # Si un callback de suppression est fourni, l'ajouter à l'action de suppression
    #     delete_action = QAction(f"Supprimer '{item_text}'", self)
    #     if delete_callback:
    #         delete_action.triggered.connect(lambda: self.delete_item_with_callback(table_widget, row, delete_callback))
    #     else:
    #         delete_action.triggered.connect(lambda: self.delete_item(table_widget, row))

    #     # Ajouter des actions au menu
    #     menu.addAction(modify_action)
    #     menu.addAction(delete_action)

    #     # Afficher le menu contextuel
    #     menu.exec_(table_widget.mapToGlobal(pos))

    # def modify_item(self, table_widget, row, column):
    #     """ Modifier un élément dans n'importe quel tableau """
    #     item = table_widget.item(row, column)
    #     if item:
    #         new_text, ok = QInputDialog.getText(self, "Modifier l'élément", "Nouvelle valeur:", text=item.text())
    #         if ok and new_text:
    #             item.setText(new_text)  # Modifier le texte de la cellule

    # def delete_item(self, table_widget, row):
    #     """ Supprimer une ligne dans n'importe quel tableau """
    #     reply = QMessageBox.question(
    #         self, 
    #         "Confirmation", 
    #         "Voulez-vous vraiment supprimer cette ligne?",
    #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #     )
        
    #     if reply == QMessageBox.StandardButton.Yes:
    #         table_widget.removeRow(row)  # Supprimer la ligne du tableau

    # def delete_item_with_callback(self, table_widget, row, callback):
    #     """ Supprimer une ligne dans n'importe quel tableau et appliquer le callback pour supprimer la ligne de la base de données """
    #     reply = QMessageBox.question(
    #         self, 
    #         "Confirmation", 
    #         "Voulez-vous vraiment supprimer cette ligne et la base de données?",
    #         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    #     )
        
    #     if reply == QMessageBox.StandardButton.Yes:
    #         # Supprimer la ligne du tableau
    #         table_widget.removeRow(row)

    #         # Appeler le callback pour supprimer la ligne dans la base de données (envoi de l'ID ou autre donnée)
    #         item_id = table_widget.item(row, 0).text()  # Supposons que l'ID de la ligne soit dans la première colonne
    #         callback(item_id)  # Appeler le callback pour supprimer la ligne de la base de données



class LoadingDialog(QDialog):
    def __init__(self, message="Chargement en cours...", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lancement de l'application, Veuillez patienter svp...")
        
        #self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        layout = QVBoxLayout()
        layout.addWidget(QLabel(message))
        self.setLayout(layout)
        self.setFixedSize(300, 2)



class EnterKeyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = super().createEditor(parent, option, index)
        if editor:
            editor.installEventFilter(self)
        return editor

    def eventFilter(self, editor, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.commitData.emit(editor)
            self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)  # Empêche le focus auto

            # Accéder à la table view et forcer focus à la cellule [row+1, 4]
            current_index = self.parent().currentIndex()
            row = current_index.row()
            column = current_index.column()
            model = current_index.model()

            if row + 1 < model.rowCount():
                next_index = model.index(row + 1, column)
                self.parent().setCurrentIndex(next_index)
                self.parent().edit(next_index)
            return True
        return super().eventFilter(editor, event)

class LogDetailsDialog(QDialog):
    def __init__(self, action, model, old_data, new_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Log : {action.upper()} - {model}")
        self.setMinimumSize(800, 600)
        self.model = model
        layout = QVBoxLayout()

        # Action et modèle
        header = QLabel(f"<b>Action :</b> {action} | <b>Modèle :</b> {model}")
        header.setStyleSheet("font-size:11pt")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Section OLD DATA
        old_label = QLabel("Ancien contenu :")
        old_label.setStyleSheet("font-weight: bold; color: red;font-size:13pt")
        layout.addWidget(old_label)

        self.old_text = QTextEdit()
        self.old_text.setReadOnly(True)
        self.old_text.setText(self.format_json(old_data) if old_data else None)
        self.old_text.setStyleSheet("font-size:11pt")
        layout.addWidget(self.old_text)

        # Section NEW DATA
        new_label = QLabel("Nouveau contenu :")
        new_label.setStyleSheet("font-weight: bold; color: green;font-size:13pt")
        layout.addWidget(new_label)

        self.new_text = QTextEdit()
        self.new_text.setReadOnly(True)
        self.new_text.setText(self.format_json(new_data))
        self.new_text.setStyleSheet("font-size:11pt")
        layout.addWidget(self.new_text)

        # Boutons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def format_json(self, data):
        """Formate une chaîne JSON de manière lisible."""
        print(self.model)
        if 'App\\Models\\Paiement' in  self.model:
            print('self.model')
            try:
                return self.extract_paiement_info(data)
            except Exception as e:
                print(f'return str(data) {e}')

        else:
            try:
                obj = json.loads(data) if isinstance(data, str) else data
                return json.dumps(obj, indent=4, ensure_ascii=False)
            except:
                return str(data)



    def extract_paiement_info(self, log_data):
        print(log_data, type(log_data))
        try:
            
            if isinstance(log_data, str):
                log_data = json.loads(log_data)

            print(f"\n\n\n log_data ===={log_data}", type(log_data))
            paiement_details = log_data.get('paiement_details', {})

            if isinstance(paiement_details, str):
                paiement_details = json.loads(paiement_details)

            inner_details = paiement_details.get('paiement_details', {})
            if isinstance(inner_details, str):
                inner_details = json.loads(inner_details)

            info_raw = inner_details.get('info_paiement', {})


            if not isinstance(info_raw, dict):
                raise ValueError("info_paiement n'est pas un dictionnaire")


            new_info = list(info_raw.items())[-1]
            
            return json.dumps(new_info, indent=4, ensure_ascii=False)
            # return {
            #     "date": new_info[0],
            #     **new_info[1]
            # }

        except Exception as e:
            print(f"--ttt---- : {e}")
            import traceback
            traceback.print_exc()

class FrameWithBackground(QFrame):
    def __init__(self, background_image, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap(background_image)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.background_image)


class CertificateManager:
    # Cette vérification fonctionne avec les certificats auto-signés
# Get-AuthenticodeSignature "C:\Program Files\gestion ecole\app.exe" | Format-List
# ooo
    # "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x86\signtool.exe" verify /v "C:\Program Files\gestion ecole\app.exe"

    # Extraire le certificat depuis le PFX
# $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
# $cert.Import("C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx", "@#Janvier21", "Exportable,PersistKeySet")

# # Exporter en .cer
# $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
# [System.IO.File]::WriteAllBytes("C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.cer", $certBytes)

# Write-Host "✅ Certificat exporté avec succès"

# Générer un certificat avec un nom plus professionnel
# $cert = New-SelfSignedCertificate `
#     -Subject "CN=Gestion server, O=Infini software, C=FR" `
#     -DnsName "infini-sofware.cloud" `
#     -Type CodeSigning `
#     -KeyUsage DigitalSignature `
#     -KeyExportPolicy Exportable `
#     -KeyLength 2048 `
#     -HashAlgorithm SHA256 `
#     -CertStoreLocation "Cert:\CurrentUser\My" `
#     -NotAfter (Get-Date).AddYears(20)

# $pwd = ConvertTo-SecureString -String "@#Janvier21" -Force -AsPlainText
# Export-PfxCertificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-server.pfx" -Password $pwd
# Export-Certificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-server.cer"

# # Installer dans le magasin racine de confiance
# $Password = ConvertTo-SecureString '@#Janvier21' -AsPlainText -Force
# Import-PfxCertificate -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx" -CertStoreLocation "Cert:\LocalMachine\Root" -Password $Password

# "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x86\signtool.exe" sign /f "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx" /p "@#Janvier21" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "C:\Users\fritz\OneDrive\Desktop\school_client\build\app.exe"

# # Signer avec le nouveau certificat
# $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
# $cert.Import("C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx", "@#Janvier21", "Exportable,PersistKeySet")
# Set-AuthenticodeSignature -FilePath "C:\Program Files\gestion ecole\app.exe" -Certificate $cert -HashAlgorithm SHA256



# "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x86\signtool.exe" sign /f "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx" /p "@#Janvier21" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "C:\Users\fritz\OneDrive\Desktop\school_client\build\app.exe"

# Générer un certificat avec plus de propriétés
# $cert = New-SelfSignedCertificate `
#     -DnsName "app.exe" `
#     -Subject "CN=app.exe, O=My Company, C=FR" `
#     -Type CodeSigningCert `
#     -KeyExportPolicy Exportable `
#     -KeyLength 2048 `
#     -KeyAlgorithm RSA `
#     -HashAlgorithm SHA256 `
#     -CertStoreLocation "Cert:\CurrentUser\My" `
#     -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
#     -KeyUsage DigitalSignature,KeyEncipherment

# $pwd = ConvertTo-SecureString -String "@#Janvier21" -Force -AsPlainText
# Export-PfxCertificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx" -Password $pwd
# Export-Certificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.cer"

    def __init__(self,
                 subject_name="CN=Lekol360.exe",
                 pfx_path=r"C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-Lekol360.pfx",
                 pfx_password="@#Janvier21"):
        self.subject_name = subject_name
        self.pfx_path = pfx_path
        self.pfx_password = pfx_password
        self.path_exe=r"C:\Program Files\gestion ecole\Lekol360.exe"
        self.run_as_admin()
        # Création du dossier si inexistant
        os.makedirs(os.path.dirname(self.pfx_path), exist_ok=True)

    def run_as_admin(self):
        """ Relance le script en mode administrateur si ce n'est pas déjà le cas. """
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True  # Déjà en mode admin, on continue

        print(" Ce script nécessite les droits administrateur. Redémarrage en mode administrateur...")
        params = " ".join([f'"{arg}"' for arg in sys.argv] + ["--as-admin"])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit(0)

    def certificat_existe(self) -> bool:
        """
        Vérifie si le certificat est déjà dans Cert:\LocalMachine\Root
        """
        cmd = [
            "powershell",
            "-Command",
            f"Get-ChildItem -Path Cert:\\LocalMachine\\Root | Where-Object {{ $_.Subject -eq '{self.subject_name}' }}"
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print("❌ Erreur lors de la vérification du certificat :", e.stderr)
            return False

    def generer_certificat(self):
        """
        Génère un certificat auto-signé et l'exporte en .pfx
        """
        cmd = [
            "powershell",
            "-Command",
            (
                f"$cert = New-SelfSignedCertificate "
                f"-Type CodeSigningCert "
                f"-Subject '{self.subject_name}' "
                f"-KeyExportPolicy Exportable "
                f"-KeyLength 2048 "
                f"-KeyAlgorithm RSA "
                f"-HashAlgorithm SHA256 "
                f"-CertStoreLocation 'Cert:\\CurrentUser\\My'; "
                f"$pwd = ConvertTo-SecureString -String '{self.pfx_password}' -Force -AsPlainText; "
                f"Export-PfxCertificate -Cert $cert -FilePath '{self.pfx_path}' -Password $pwd"
            )
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Certificat généré et exporté vers {self.pfx_path}")
        except subprocess.CalledProcessError as e:
            print("❌ Erreur lors de la génération du certificat :", e.stderr)

    def installer_certificat(self):
        """
        Installe le certificat PFX dans Cert:\LocalMachine\Root
        ⚠️ Nécessite d'exécuter Python en Administrateur
        """
        cmd = [
            "powershell",
            "-Command",
            (
                f"$Password = ConvertTo-SecureString '{self.pfx_password}' -AsPlainText -Force; "
                f"Import-PfxCertificate -FilePath '{self.pfx_path}' "
                f"-CertStoreLocation 'Cert:\\LocalMachine\\Root' "
                f"-Password $Password | Out-Null"
            )
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.signer_exe(self.path_exe)
            print("✅ Certificat installé avec succès dans LocalMachine\\Root")
        except subprocess.CalledProcessError as e:
            print("❌ Erreur lors de l'installation du certificat :", e.stderr)



    def signer_exe(self, exe_path):
        """
        Signe un .exe avec Set-AuthenticodeSignature en chargeant le .pfx correctement
        """
        ps_command = f"""
        $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2
        $cert.Import('{self.pfx_path}', '{self.pfx_password}', 'Exportable,PersistKeySet')
        Set-AuthenticodeSignature -FilePath '{exe_path}' -Certificate $cert -HashAlgorithm 'SHA256'
        """

        try:
            subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Fichier signé avec succès : {exe_path}")
        except subprocess.CalledProcessError as e:
            print("❌ Erreur lors de la signature :", e.stderr)








# result = extract_paiement_info(data['data'])
# print(json.dumps(result, indent=4, ensure_ascii=False))



    
# class PDFViewer(QWidget):
#     def __init__(self, pdf_data):
#         super().__init__()
#         self.setWindowTitle("Aperçu du Bulletin")

#         # Affichage du PDF
#         self.web_view = QWebEngineView()
#         self.web_view.setHtml(f'<embed src="data:application/pdf;base64,{pdf_data}" type="application/pdf" width="100%" height="100%"/>')

#         layout = QVBoxLayout()
#         layout.addWidget(self.web_view)
#         self.setLayout(layout)

# class PDFViewer(QWidget):
#     def __init__(self, pdf_base64, widget):
#         super().__init__()
#         self.setWindowTitle("Aperçu du Bulletin")
#         self.resize(800, 600)

#         # Créer le navigateur intégré
#         self.web_view = QWebEngineView()
#         # Charger le PDF en tant qu'URL data
#         pdf_html = f'<embed src="data:application/pdf;base64,{pdf_base64}" type="application/pdf" width="100%" height="100%"/>'
#         self.web_view.setHtml(pdf_html)
#         print(pdf_html)

#         layout = QVBoxLayout(widget)
#         layout.addWidget(self.web_view)
#         self.setLayout(layout)


# from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
# from PySide6.QtCore import Qt, QVariantAnimation, QRectF, QEvent
# from PySide6.QtGui import QPainter, QPen, QColor




from PySide6.QtCore import QAbstractAnimation

class LoaderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(70, 70)
        self.angle = 0

        self.animation = QVariantAnimation()
        self.animation.setStartValue(0)
        self.animation.setEndValue(360)
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.update_angle)

        # Configuration visuelle
        self.color = QColor("#3498db")
        self.pen_width = 5
        self.size = 60

    def update_angle(self, value):
        self.angle = value
        self.update()

    def start(self):
        if self.animation.state() != QAbstractAnimation.Running:
            self.animation.start()

    def stop(self):
        if self.animation.state() == QAbstractAnimation.Running:
            self.animation.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        x = (self.width() - self.size) / 2
        y = (self.height() - self.size) / 2
        pen = QPen()
        pen.setWidth(self.pen_width)
        pen.setColor(self.color)
        painter.setPen(pen)
        rectangle = QRectF(x, y, self.size, self.size)
        painter.drawArc(rectangle, self.angle * 16, 270 * 16)

class LoadingOverlay_(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 90);padding:5px")

        self.loader = LoaderWidget()
        self.label = QLabel("Chargement...", self)
        self.label.setStyleSheet("color: white; font-size: 15px;")
        self.label.setAlignment(Qt.AlignCenter)

        self.layouts = QVBoxLayout(self)
        self.layouts.addStretch()
        self.layouts.addWidget(self.loader, alignment=Qt.AlignCenter)
        self.layouts.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layouts.addStretch()
        self.setLayout(self.layouts)

        self.hide()

    def start_loading(self, message="Chargement...!!!"):
        self.label.setText(message)
        self.resize(self.parent().size())

        if not self.isVisible():
            self.loader.start()
            self.show()

    def finish_loading(self):
        if self.isVisible():
            self.loader.stop()
            self.hide()


              # certutil -addstore -f "Root" "C:\ecole_1\mysql-8.0.41-winx64\certs\ca.pem"

            #   certutil -delstore "Root" "Ecole CA"

            # certutil -delstore "Root" 23b4b1f1ac3c0ee85192c1bd019b422aba5c65bd


            # certutil -store "Root"

#             ================ Certificate 2 ================
# Serial Number: 23b4b1f1ac3c0ee85192c1bd019b422aba5c65bd
# Issuer: CN=Ecole CA
#  NotBefore: 8/7/2025 10:36 AM
#  NotAfter: 8/5/2035 10:36 AM
# Subject: CN=Ecole CA
# Signature matches Public Key
# Root Certificate: Subject matches Issuer
# Cert Hash(sha1): a80ad7c9449dd7e6209a42c7ed0403f4dc30abd7
# No key provider information
# Cannot find the certificate and private key for decryption.


# [Peer]                                                                                          
# PublicKey =uIBJfGIC4Sl/8F10+F1caqT8pIUSFXExvu18mexlThE=
# AllowedIPs = 10.10.0.3/32  


# Remplace :
# -DnsName "infini-software.cloud" `
# -Subject "CN=Infini Software, O=Infini Software, C=FR" `

# Générer un certificat avec plus de propriétés
# $cert = New-SelfSignedCertificate `
#     -DnsName "infini-software.cloud" `
#     -Subject "CN=Infini Software, O=Infini Software, C=FR" `
#     -Type CodeSigningCert `
#     -KeyExportPolicy Exportable `
#     -KeyLength 2048 `
#     -KeyAlgorithm RSA `
#     -HashAlgorithm SHA256 `
#     -CertStoreLocation "Cert:\CurrentUser\My" `
#     -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
#     -KeyUsage DigitalSignature,KeyEncipherment

# $pwd = ConvertTo-SecureString -String "@#Janvier21" -Force -AsPlainText
# Export-PfxCertificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.pfx" -Password $pwd
# Export-Certificate -Cert $cert -FilePath "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-test.cer"


# "C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe" sign /fd SHA256 /f "C:\Users\fritz\OneDrive\Documents\setup gestion ecole\cert\codesign-Lekol360.pfx" /p "@#Janvier21" /tr http://timestamp.digicert.com /td SHA256 $f