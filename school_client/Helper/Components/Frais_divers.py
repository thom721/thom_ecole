from PySide6.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QComboBox, QLabel, QLineEdit,QMessageBox, QFrame,QGraphicsDropShadowEffect
)
from PySide6.QtGui import QCursor,QColor
from PySide6.QtCore import Qt,Signal   

from Models.fetch_data import Fech_data#annee_academique
# from Models.enregistrement import enregistrer_frais_dinscription
from Models.enregistrement import Save_data
from Models.AsyncDataHandler import AsyncDataHandler
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
from Helper.applique_erreurs import appliquer_erreurs
from Helper.LoadingOverlay import LoadingOverlay

class Frais_divers(QDialog):
    ligne_ajoutee = Signal()

    def __init__(self,frais_edit):
        super().__init__() 
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.container = QFrame()
        self.overlay = LoadingOverlay(self) 
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
     

        
        self.setWindowTitle("Frais divers")
        self.save_data = Save_data()
        self.fetch_data_ = Fech_data()
        self.api_handler_ = AsyncDataHandler()
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)
        self.frais_edit = frais_edit


    def enregistrer_frais_divers(self, niveaux, anneeAcademique): 
    
        self.frame_niveau = QFrame()
        layout_niveau = QVBoxLayout(self.frame_niveau)
        layout_niveau.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_niveau.setSpacing(4)
        label_niveau = QLabel("Cycle / Section / Niveau")
        self.combo_niveau = QComboBox()
        layout_niveau.addWidget(label_niveau)
        layout_niveau.addWidget(self.combo_niveau)
        self.combo_niveau.setPlaceholderText('Cycle / Section / Niveau')
        self.combo_niveau.clear()
        for niveau in niveaux:
            self.combo_niveau.addItem(niveau['name'], niveau['id'])
        

        self.frame_annee = QFrame()
        layout_annee = QVBoxLayout(self.frame_annee)
        layout_annee.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_annee.setSpacing(4)
        label_annee = QLabel("Année Académique")
        self.combo_annee = QComboBox()
        layout_annee.addWidget(label_annee)
        layout_annee.addWidget(self.combo_annee)
        self.combo_annee.setPlaceholderText('Choisir l\'année académique')

        self.combo_annee.clear()
        for annee in anneeAcademique: # self.fetch_data_.annee_academique():
            self.combo_annee.addItem(annee['annee_academique'], annee['id'])

        self.frame_description = QFrame()
        layout_description = QVBoxLayout(self.frame_description)
        layout_description.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_description.setSpacing(4)

        label_description = QLabel("Description")
        self.input_description = QLineEdit()
        layout_description.addWidget(label_description)
        layout_description.addWidget(self.input_description)
        # self.input_description.setPlaceholderText("Ex: 1000gdes")

        # LineEdit - Montant des frais
        self.frame_frais = QFrame()
        layout_frais = QVBoxLayout(self.frame_frais)
        layout_frais.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_frais.setSpacing(4)
        label_frais = QLabel("Prix")
        self.input_frais = QLineEdit()
        layout_frais.addWidget(label_frais)
        layout_frais.addWidget(self.input_frais)
        self.id_input_frais = QLineEdit()
        self.id_input_frais.setText("")
        self.input_frais.setPlaceholderText("Ex: 1000gdes")



        # Bouton "Enregistrer"
        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)

        if self.frais_edit:
            frais_to_edit = self.frais_edit.get('data','')
            self.id_input_frais.setText(frais_to_edit.get("id",""))
            self.input_frais.setText(frais_to_edit.get("prix",""))
            self.input_description.setText(frais_to_edit.get("description",""))
            annee = frais_to_edit.get("annee_academique","")
            niveau = frais_to_edit.get("niveau","")
            self.fill_combo_box(self.combo_annee, annee)
            self.fill_combo_box(self.combo_niveau, niveau)

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
        layout.addWidget(self.frame_niveau)
 
        layout.addWidget(self.frame_annee)
 
        layout.addWidget(self.frame_description) 
        layout.addWidget(self.frame_frais) 

        layout.addLayout(save_button_layout)

        self.setLayout(layout)
        self.exec()

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def enregistrer(self):
        self.save_button.setDisabled(True)
        self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.overlay.start_loading("Frais divers")
        annee = self.combo_annee.currentData()
        niveau = self.combo_niveau.currentData()
        montant = self.input_frais.text().strip()
        description = self.input_description.text().strip()

        response = self.api_handler_.enregistrer_frais_divers(id=self.id_input_frais.text(),prix=montant, description=description,niveau_id=niveau, anneeAc=annee)
       

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
        if endpoint.startswith("v1/frais-divers-store"):
            self.save_button.setDisabled(False)
            self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.ligne_ajoutee.emit()
            self.close()

    
    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        print("Response error content:", response_data, type(response_data), error_msg, endpoint)
        mapping = {
            'prix': self.input_frais,
            'anneeAc': self.combo_annee,
            'niveau_id': self.combo_niveau,
            'classes_id': self.input_description
          } 
        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=mapping, overlay=self.overlay)
        self.overlay.finish_loading()

