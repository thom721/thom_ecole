from PySide6.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QComboBox, QLabel, QLineEdit,QMessageBox, QFrame,QGraphicsDropShadowEffect
)
from PySide6.QtGui import QCursor,QColor
from PySide6.QtCore import Qt,Signal   

from Models.fetch_data import Fech_data#annee_academique
# from Models.enregistrement import enregistrer_frais_dinscription
from Models.enregistrement import Save_data
from Models.AsyncDataHandler import AsyncDataHandler

from Helper.applique_erreurs import appliquer_erreurs
from Helper.LoadingOverlay import LoadingOverlay
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
class Faculte(QDialog):
    ligne_ajoutee = Signal()

    def __init__(self,faculte_edit):
        super().__init__() 
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.overlay = LoadingOverlay(self)
        self.container = QFrame()
        # self.direct_request=direct_request
        # self.user_connect = user_connect
        self.container.setStyleSheet("""
            background: white;
            border-radius: 5px;
            border: none;
        """)
    # Définir le styleSheet une seule fois ici
        self.setStyleSheet("""
        QDialog {
            background: #fff;
        }
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
     

        
        self.setWindowTitle("Faculté")
        self.save_data = Save_data()
        self.fetch_data_ = Fech_data()
        self.api_handler_ = AsyncDataHandler()
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)
        self.faculte_edit = faculte_edit


    def enregistrer_faculte(self, niveaux):
  
    
        # self.frame_niveau = QFrame()
        # layout_niveau = QVBoxLayout(self.frame_niveau)
        # layout_niveau.setAlignment(Qt.AlignmentFlag.AlignTop) 
        # layout_niveau.setSpacing(4)
        # label_niveau = QLabel("Cycle / Section / Niveau")
        # self.combo_niveau = QComboBox()
        # layout_niveau.addWidget(label_niveau)
        # layout_niveau.addWidget(self.combo_niveau)
        # self.combo_niveau.setPlaceholderText('Cycle / Section / Niveau')
        # self.combo_niveau.clear()
        # for niveau in niveaux:
        #     self.combo_niveau.addItem(niveau['name'], niveau['id'])
        

        # self.frame_annee = QFrame()
        # layout_annee = QVBoxLayout(self.frame_annee)
        # layout_annee.setAlignment(Qt.AlignmentFlag.AlignTop) 
        # layout_annee.setSpacing(4)
        # label_annee = QLabel("Année Académique")
        # self.combo_annee = QComboBox()
        # layout_annee.addWidget(label_annee)
        # layout_annee.addWidget(self.combo_annee)
        # self.combo_annee.setPlaceholderText('Choisir l\'année académique')

        # self.combo_annee.clear()
        # for annee in self.fetch_data_.annee_academique():
        #     self.combo_annee.addItem(annee['annee_academique'], annee['id'])

        self.frame_nom = QFrame()
        layout_nom = QVBoxLayout(self.frame_nom)
        layout_nom.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_nom.setSpacing(4)

        label_nom = QLabel("Nom")
        self.input_faculte_nom = QLineEdit()
        layout_nom.addWidget(label_nom)
        layout_nom.addWidget(self.input_faculte_nom)
        self.input_faculte_nom.setPlaceholderText("Ex: Infirmière")
        # self.input_nb_annee.setPlaceholderText("Ex: 1000gdes")

        # LineEdit - Montant des frais
        self.frame_nb_annee = QFrame()
        layout_nb_annee = QVBoxLayout(self.frame_nb_annee)
        layout_nb_annee.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_nb_annee.setSpacing(4)
        label_nb_annee = QLabel("Nbre d'année / Session")
        
        layout_nb_annee.addWidget(label_nb_annee)        
        self.input_nb_annee = QLineEdit()
        layout_nb_annee.addWidget(self.input_nb_annee)
        self.id_input_faculte = QLineEdit()
        self.id_input_faculte.setText("")
        self.input_nb_annee.setPlaceholderText("Ex: 4 ans")



        # Bouton "Enregistrer"
        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)
        print(f"self.faculte_edit   {self.faculte_edit}")
        if self.faculte_edit:
            print(self.faculte_edit)
            frais_to_edit = self.faculte_edit.get('data','')
            self.id_input_faculte.setText(frais_to_edit.get("id",""))
            self.input_faculte_nom.setText(frais_to_edit.get("nom",""))
            self.input_nb_annee.setText(frais_to_edit.get("nb_annee",""))
            # annee = frais_to_edit.get("annee_academique","")
            # niveau = frais_to_edit.get("niveau","")
            # self.fill_combo_box(self.combo_annee, annee)
            # self.fill_combo_box(self.combo_niveau, niveau)

            self.save_button.setText("Modifier")
            
        self.save_button.setStyleSheet("""
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
        
        self.save_button.clicked.connect(self.enregistrer)

        # Layout pour aligner le bouton de fermeture
        save_button_layout = QVBoxLayout()
        save_button_layout.addWidget(self.save_button)
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Layout principal
        layout = QVBoxLayout(self.container) 
        # layout.addWidget(self.frame_niveau)
 
        # layout.addWidget(self.frame_annee)
 
        layout.addWidget(self.frame_nom) 
        layout.addWidget(self.frame_nb_annee) 

        layout.addLayout(save_button_layout)

        self.setLayout(layout)
        self.exec()

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def enregistrer(self):
        # self.save_button.setDisabled(True)
        # self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.overlay.start_loading("Traitment en cours")
        # annee = self.combo_annee.currentData()
        # niveau = self.combo_niveau.currentData()
        nom = self.input_faculte_nom.text().strip()
        nb_annee = self.input_nb_annee.text().strip()
      
        response = self.api_handler_.enregistrer_faculte(id=self.id_input_faculte.text(),nom=nom, nb_annee=nb_annee)
  

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
        print("Response error content:", response_data, type(response_data), endpoint)
        if endpoint.startswith("v1/post-faculte"):
            self.id_input_faculte.setText("")
            self.save_button.setDisabled(False)
            self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.ligne_ajoutee.emit()
            self.close()

    
    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        print("Response error content:", response_data, type(response_data), error_msg, endpoint)
        mapping = {
            'nom': self.input_faculte_nom,
            'nb_annee': self.input_nb_annee, 
          }  
        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=mapping, overlay=self.overlay)
        self.overlay.finish_loading()
 