from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QDateEdit, QComboBox, QLabel, QFrame,QMessageBox,QLineEdit
from PySide6.QtCore import Qt, QDate,Signal
from PySide6.QtGui import QCursor
# from datetime import datetime, date
import datetime
# from Models.enregistrement import enregistrer_annee_academique
from Models.enregistrement import Save_data
from Helper.applique_erreurs import appliquer_erreurs
from Models.AsyncDataHandler import AsyncDataHandler
from Helper.LoadingOverlay import LoadingOverlay
from Helper.HandlerHerror.HandlerHerror import HandlerHerror

class Annee_Academique(QDialog):
    ligne_ajoutee = Signal()
    def __init__(self, year_edit):
        super().__init__()
        # self = QDialog()
        self.save_data = Save_data()
        self.setWindowTitle("Année académique") 
        self.year_edit = year_edit 

        self.api_handler_ = AsyncDataHandler()
        self.overlay = LoadingOverlay(self)
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
     


    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def fill_commbo_with_data(self,name_combo, default_value):
        index = name_combo.findData(default_value)
        if index >= 0:
            name_combo.setCurrentIndex(index)

    def ajouter_annee_academique(self, niveaux): 
        self.setModal(True)  
        frame_date_debut = QFrame()
        layout_date_debut = QVBoxLayout(frame_date_debut)
        label_debut = QLabel("Date de début ")
        self.date_debut = QDateEdit()
        layout_date_debut.addWidget(label_debut)
        layout_date_debut.addWidget(self.date_debut)
        self.date_debut.setCalendarPopup(True)
        self.date_debut.setDate(QDate.currentDate())

        # Champs DateEdit (Date de fin)
        frame_date_fin = QFrame()
        layout_date_fin = QVBoxLayout(frame_date_fin)
        label_fin = QLabel("Date de fin ")
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        layout_date_fin.addWidget(label_fin)
        layout_date_fin.addWidget(self.date_fin)

        # ComboBox (Section / Niveau)
        frame_date_section = QFrame()
        layout_date_section = QVBoxLayout(frame_date_section)
        label_compo = QLabel("Section / Niveau")
        label_compo.setHidden(True)
        self.combo_compo = QComboBox()
        self.combo_compo.setHidden(True)
        for niveau in niveaux:
            self.combo_compo.addItem(niveau['name'], niveau['id'])
        layout_date_section.addWidget(label_compo) 
        layout_date_section.addWidget(self.combo_compo) 

        self.id_for_edit = QLineEdit()
        self.id_for_edit.setText("")

        frame_status = QFrame()
        layout_status = QVBoxLayout(frame_status)
        label_status = QLabel("Status") 
        combo_status = QComboBox()
        layout_status.addWidget(label_status) 
        layout_status.addWidget(combo_status)
        status_ = {'Actif': 1, 'Inactif': 0}
        for label, value in status_.items():
            combo_status.addItem(label, value)

 

        if self.year_edit:
            annee_edit = self.year_edit['data'] 
            self.id_for_edit.setText(annee_edit.get("id",""))
            # Pour date_debut
            date_value = annee_edit['date_debut']
            if isinstance(date_value, (datetime.date, datetime.datetime)):
                qdate = QDate(date_value.year, date_value.month, date_value.day)
            else:
                qdate = QDate.fromString(str(date_value), "yyyy-MM-dd")

            self.date_debut.setDate(qdate)

            # Pour date_fin
            date_value2 = annee_edit['date_fin']
            if isinstance(date_value2, (datetime.date, datetime.datetime)):
                qdate2 = QDate(date_value2.year, date_value2.month, date_value2.day)
            else:
                qdate2 = QDate.fromString(str(date_value2), "yyyy-MM-dd")

            self.date_fin.setDate(qdate2)
 

            niveau = self.year_edit.get("niveau","")
            self.fill_combo_box(self.combo_compo, niveau)
            
            status = 'Actif' if annee_edit["status"]==1 else 'Inactif'
            self.fill_combo_box(combo_status, status)
          

        # Bouton "Enregistrer"
        self.save_button = QPushButton('Enregistrer')
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

   
        self.save_button.clicked.connect(lambda: self.enregistrer_annee(self.id_for_edit, self.date_debut, self.date_fin, self.combo_compo,combo_status))

        # Layout pour fermer
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        # close_layout.addWidget(close_button)

        # Layout principal
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.addLayout(close_layout)
        layout.addWidget(frame_date_debut)
        layout.addWidget(frame_date_fin)
        layout.addWidget(frame_date_section)  # Correction ici
        #if self.year_edit:
        layout.addWidget(frame_status)
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)
        self.exec()


    def enregistrer_annee(self,id_for_edit,date_debut_widget, date_fin_widget, niveau_widget,combo_status):
                
        # self.save_button.setDisabled(True)
        # self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.overlay.start_loading("Traitment en cours")
        date_debut = date_debut_widget.date().toString("yyyy-MM-dd")  # Extraction de la valeur
        date_fin = date_fin_widget.date().toString("yyyy-MM-dd")
        niveau = niveau_widget.currentText()
        combo_status = combo_status.currentData()
        id = id_for_edit.text()

     
        response = self.api_handler_.enregistrer_annee_academique(id,date_debut, date_fin, niveau,combo_status) 

        # print(response)


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
        # print(response_data) 
        if response_data and 'success' in response_data:
            self.id_for_edit.setText("")
            self.ligne_ajoutee.emit()
            self.close()
        self.overlay.finish_loading()

    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        # print("Response error content:", response_data, error_msg, endpoint)
        mapping = {
            'date_debut': self.date_debut,
            'date_fin': self.date_fin,
            'niveau_id': self.combo_compo,
          } 

        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=mapping, overlay=self.overlay)
        self.overlay.finish_loading()
