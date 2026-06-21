from PySide6.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit,QMessageBox,QFrame
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt,Signal
from Models.enregistrement import Save_data# enregistrer_classe
from Helper.applique_erreurs import appliquer_erreurs
from Models.AsyncDataHandler import AsyncDataHandler
from Helper.LoadingOverlay import LoadingOverlay
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
 
class Add_classe_Dialog(QDialog):
    ligne_ajoutee = Signal()

    def __init__(self, class_to_edit):
        super().__init__()
        #self = QDialog()
     
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
     

        
        self.setWindowTitle("Classe")
        self.save_data = Save_data()
        self.class_to_edit = class_to_edit
        self.api_handler_ = AsyncDataHandler()
        self.overlay = LoadingOverlay(self)
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)
        
    def enregistrer_classe(self, niveaux): 

        # ComboBox - Section
        self.edit_classe_id = QLineEdit()
        self.edit_classe_id.setText("")

        self.frame_niveau = QFrame()
        layout_niveau = QVBoxLayout(self.frame_niveau)
        layout_niveau.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_niveau.setSpacing(4)

        label_section = QLabel("Section")
        self.combo_section = QComboBox()
        layout_niveau.addWidget(label_section)
        layout_niveau.addWidget(self.combo_section)
        self.combo_section.clear()
        for niveau in niveaux:
            self.combo_section.addItem(niveau['name'], niveau['id'])
        # self.combo_section.addItems(["Maternelle", "Primaire", "Secondaire", "Université"])

        # LineEdit - Nom de la classe
        self.frame_nom_classe = QFrame()
        layout_nom_classe = QVBoxLayout(self.frame_nom_classe)
        layout_nom_classe.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_nom_classe.setSpacing(4)

        label_classe = QLabel("Nom de la classe")
        self.input_classe = QLineEdit()
        layout_nom_classe.addWidget(label_classe)
        layout_nom_classe.addWidget(self.input_classe)
        self.input_classe.setPlaceholderText("Ex: 6ème A, Terminale S...")
        
        # Appliquer du style

        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)

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

        if self.class_to_edit: 
            print(self.class_to_edit)
            data_class_to_edit = self.class_to_edit.get("data","")
            self.edit_classe_id.setText(data_class_to_edit.get("id",""))
            self.input_classe.setText(data_class_to_edit.get("nom_classe",""))
            niveau = data_class_to_edit.get("niveau_id","")
            # niveau = data_class_to_edit.get("niveau","")
            # self.fill_combo_box(self.combo_section, niveau)
            self.fill_commbo_with_data(self.combo_section, niveau)

            self.save_button.setText("Modifier")
        # Fonction de validation
        self.save_button.clicked.connect(self.enregistrer)

        # Layout pour aligner le bouton de fermeture
        save_button_layout = QVBoxLayout()
        save_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        save_button_layout.addWidget(self.save_button)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.frame_niveau)
        layout.addWidget(self.frame_nom_classe)
        # layout.addWidget(label_classe)
        # layout.addWidget(self.input_classe)
        layout.addLayout(save_button_layout)

        self.setLayout(layout)
        self.exec()

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def fill_commbo_with_data(self,name_combo, default_value):
        index = name_combo.findData(default_value)
        if index >= 0:
            name_combo.setCurrentIndex(index)

    def enregistrer(self):
        print('self.save_button.setDisabled')
        self.overlay.start_loading("Enregistrement de la classe ")
        # self.save_button.setDisabled(True)
        # self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        
        section = self.combo_section.currentData()
        nom_classe = self.input_classe.text().strip()
        # response =self.save_data.enregistrer_classe(id=self.edit_classe_id.text(),niveau_id=section, nom_classe=nom_classe)
        # if self.direct_request:
        #     from Controllers.ParametreController import store_classe
        #     from Controllers.Validator import ValidatorError
        #     payload={           
        #         'id':self.edit_classe_id.text(),
        #         'niveau_id':section,
        #         'nom_classe':nom_classe,
        #         'user_id' :  self.user_connect.text()
        #     }
        #     response = store_classe(payload)
        #     if response:
        #         self.overlay.finish_loading()
        #         if response.get('errors'): 
        #             erreurs =response.get('errors')
        #             print(f"erreurs: {erreurs}")           
        #             ve = ValidatorError()
        #             ve.generic_direct_error_message(response_data=response)
        #         if response.get('success'):
        #             self.edit_classe_id.setText("")
        #             self.ligne_ajoutee.emit()
        #             self.close()

        #     self.save_button.setDisabled(False)
        #     self.overlay.finish_loading()
        #     self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # else:
        self.api_handler_.enregistrer_classe(id=self.edit_classe_id.text(),niveau_id=section, nom_classe=nom_classe)


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
        if endpoint.startswith("v1/classes"):
            if response_data and 'success' in response_data:
                self.edit_classe_id.setText("")
                self.ligne_ajoutee.emit()
                self.close()
        self.overlay.finish_loading()

    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        # print("Response error content:", response_data, error_msg, endpoint)
        mapping = {
            'section': self.combo_section,
            'nom_classe': self.input_classe, 
          }  
        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=mapping, overlay=self.overlay)
        self.overlay.finish_loading()