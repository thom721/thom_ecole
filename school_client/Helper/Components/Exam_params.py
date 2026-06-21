from PySide6.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QComboBox, QLabel,QLineEdit,QMessageBox
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt,Signal
# from Models.fetch_data import annee_academique
from Models.fetch_data import Fech_data
# from Models.enregistrement import enregistrer_param_exams
from Models.enregistrement import Save_data
from Helper.applique_erreurs import appliquer_erreurs
from Models.AsyncDataHandler import AsyncDataHandler
from Helper.LoadingOverlay import LoadingOverlay
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
class Param_Exam(QDialog):
    ligne_ajoutee = Signal()

    def __init__(self,exam_to_edit):
        super().__init__()
        # self = QDialog()

        self.api_handler_ = AsyncDataHandler()
        self.overlay = LoadingOverlay(self)
        # self.direct_request=direct_request
        # self.user_connect = user_connect
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)
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
     

        
        self.save_data = Save_data()
        self.fetch_data_ = Fech_data()
        self.setWindowTitle("Paramètres des examens")
        self.exam_to_edit = exam_to_edit

    def enregistrer_parametres_examen(self, niveaux, AnneAcademique):
  
        # ComboBox 1 - Type d'examen
        label_type = QLabel("Cycle / Section / Niveau")
        self.combo_niveau = QComboBox()
        self.combo_niveau.setPlaceholderText('Cycle / Section / Niveau')
        self.combo_niveau.clear()
        for niveau in niveaux:
            self.combo_niveau.addItem(niveau['name'], niveau['id'])
        # combo_niveau.addItems(["Interrogation", "Devoir", "Examen final"])

        label_annee = QLabel("Année Académique")
        self.combo_annee = QComboBox()
        self.combo_annee.setPlaceholderText('Choisir l\'année académique')
        self.combo_annee.clear()
        for annee in AnneAcademique: # self.fetch_data_.annee_academique():
            self.combo_annee.addItem(annee['annee_academique'], annee['id'])

        # ComboBox 2 - Durée
        label_evaluation = QLabel("Evaluation / Examen par")
        self.combo_evaluation = QComboBox()
        self.combo_evaluation.setPlaceholderText('Méthode d\'évaluation')
        self.combo_evaluation.addItems(["Mois","Trimestre", "Controle", "Session"])



        # Bouton "Enregistrer"
        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
          QPushButton {
                text-align: center;
                padding: 5px;
                min-width: 100px;
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

        self.id_exam_edit = QLineEdit()
        self.id_exam_edit.setText("")
        save_button_layout = QVBoxLayout()
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        if self.exam_to_edit: 
            print(f"exam_to_edit  {self.exam_to_edit}")           
            data = self.exam_to_edit.get("data","")
            niveau = data.get("niveau_id","")
            id = data.get("id","")
            self.id_exam_edit.setText(id)
            evaluation = data.get("evaluation_par","")
            annee = data.get("annee_academique_id","")
            self.fill_commbo_with_data(self.combo_niveau,niveau)
            # self.fill_commbo_with_data(combo_evaluation,evaluation)
            self.fill_commbo_with_data(self.combo_annee,annee)

            # self.fill_combo_box(combo_niveau,niveau)
            self.fill_combo_box(self.combo_evaluation,evaluation)
            # self.fill_combo_box(combo_annee,annee)
            
            self.save_button.setText("Modifier")

        self.save_button.clicked.connect(lambda: self.enregistrer())

        save_button_layout.addWidget(self.save_button)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(label_type)
        layout.addWidget(self.combo_niveau)

        layout.addWidget(label_evaluation)
        layout.addWidget(self.combo_evaluation)

        layout.addWidget(label_annee)
        layout.addWidget(self.combo_annee)
        
        layout.addLayout(save_button_layout)

        self.setLayout(layout)
        self.exec()

    def fill_commbo_with_data(self,name_combo, default_value):
        index = name_combo.findData(default_value)
        if index >= 0:
            name_combo.setCurrentIndex(index)

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def enregistrer(self):
        # self.save_button.setDisabled(True)
        # self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.overlay.start_loading("Traitment en cours")
 
        response = self.api_handler_.enregistrer_param_exams(id=self.id_exam_edit.text(),niveau_id=self.combo_niveau.currentData(), annee_academique_id=self.combo_annee.currentData(), evaluation_par=self.combo_evaluation.currentText())


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
        print(response_data)
        # if endpoint.startswith("classes"):
        if response_data and 'success' in response_data:
            self.id_exam_edit.setText("")
            self.ligne_ajoutee.emit()
            self.close()
        self.overlay.finish_loading()

    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        # print("Response error content:", response_data, error_msg, endpoint)
        mapping = {
            'niveau_id': self.combo_niveau,
            'annee_academique_id': self.combo_annee, 
            'evaluation_par': self.combo_evaluation, 
          }  
        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data, mapping_field=mapping,overlay=self.overlay)
        self.overlay.finish_loading()
        
