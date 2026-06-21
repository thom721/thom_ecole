from PySide6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QFrame,QGridLayout,QScrollArea,QWidget,QMessageBox
)
from PySide6.QtGui import QCursor
import json
import time
from collections import OrderedDict
from datetime import datetime, timedelta

from PySide6.QtCore import Qt,Signal
from Models.fetch_data import Fech_data  
from Models.enregistrement import Save_data
from Helper.applique_erreurs import appliquer_erreurs
from Models.AsyncDataHandler import AsyncDataHandler
from Helper.LoadingOverlay import LoadingOverlay
from Helper.HandlerHerror.HandlerHerror import HandlerHerror
class Main_payment(QDialog):

    ligne_ajoutee = Signal()

    def __init__(self, data_to_edit, facultes):
        super().__init__()
        # Définition des variables d'instance
        self.dialog = QDialog()
        self.echeance = None
        self.label_paiement_par_1 = None
        self.nb_echeance = None
        self.create_field = 0
        # self.direct_request=direct_request
        # self.user_connect = user_connect

        self.api_handler_ = AsyncDataHandler()
        self.overlay = LoadingOverlay(self)
        self.api_handler_.request_complete.connect(self.handle_api_success)
        self.api_handler_.request_failed.connect(self.handle_api_error)
        # self.overlay.start_loading("Chargement en cours")
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(4)
        self.accessoire=[]
        self.payment_by=[]
        self.row_count=0
        self.facultes = facultes
        self.save_data = Save_data()
        self.fetch_data_ = Fech_data()
        self.data_to_edit = data_to_edit
        self.classes___ =[]
        self.months = []

    def ouvrir_dialog_paiement(self, niveaux, anneeAcademique=None):
        """Ouvre une boîte de dialogue pour configurer les paiements."""
    
        # self.dialog.setFixedSize(800, 500)
        self.dialog.setFixedWidth(900)
        self.dialog.setWindowTitle("Paramètres de Paiement")
        self.dialog.setStyleSheet(
            """
         QDialog{background-color:#fff}
                       QComboBox, QLineEdit, QDateEdit{ width: 300px; min-height: 33px; max-height: 33px;border: 1px solid #ccc; border-radius:5px;padding-left:7px}

                         QComboBox:hover,QComboBox:focus, QLineEdit:hover, QDateEdit:hover, QLineEdit:focus, QDateEdit:focus {
                
                border: 1px solid #007bff;
            }
                        QComboBox:disabled::drop-down{
               
                color:#555
            }
                        QComboBox:disabled::drop-down, QDateEdit:disabled::drop-down{
                background: transparent;
            }
            QLabel,QComboBox{font-size:14pt; color:#999}
            """
        )
        # dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Suppression de la barre de titre

        self.first_frame = QFrame()
        self.first_layout = QHBoxLayout(self.first_frame)

        frame_cycle = QFrame()
        layout_cycle = QVBoxLayout(frame_cycle)

        layout_cycle.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout_cycle.setSpacing(4)
        label_cycle = QLabel("Cycle / niveau / Section")
        self.combo_cycle = QComboBox()
        self.combo_cycle.addItem("Cycle / niveau / Section",None) 

        self.combo_cycle.clear()
        for niveau in niveaux:
            self.combo_cycle.addItem(niveau['name'], niveau['id'])

        layout_cycle.addWidget(label_cycle)
        layout_cycle.addWidget(self.combo_cycle)
        self.combo_cycle.currentIndexChanged.connect(self.load_classe)

        self.frame_faculte = QFrame()
        layout_faculte = QVBoxLayout(self.frame_faculte)
        layout_faculte.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.frame_faculte.setHidden(True)
        # layout_faculte.setContentsMargins(10,0,10,2)
        layout_faculte.setSpacing(4)
        label_faculte = QLabel("Faculté / Domaine d'étude")
        self.combo_faculte = QComboBox()
        self.combo_faculte.addItem("Faculté / Domaine d'étude",None)
        layout_faculte.addWidget(label_faculte)
        layout_faculte.addWidget(self.combo_faculte)
 

        #  Sélection de la Classe
        frame_classe = QFrame()
        layout_classe = QVBoxLayout(frame_classe)
        layout_classe.setSpacing(2)
        layout_classe.setAlignment(Qt.AlignmentFlag.AlignTop)
        # layout_classe.setContentsMargins(10,0,10,2)
        label_classe = QLabel("Classe")
        self.combo_classe = QComboBox()
        self.combo_classe.addItem("Classe",None)
        layout_classe.addWidget(label_classe)
        layout_classe.addWidget(self.combo_classe)

        # Sélection de l'Année Académique
        frame_annee = QFrame()
        layout_annee = QVBoxLayout(frame_annee)
        # layout_annee.setContentsMargins(10,0,10,2)
        layout_annee.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_annee = QLabel("Année Académique")
        self.combo_annee = QComboBox()
        self.combo_annee.setPlaceholderText("Année Académique")
        self.combo_annee.clear()
        self.combo_annee.addItem("Année Académique", None)

        for annee in anneeAcademique: 
            self.combo_annee.addItem(annee['annee_academique'], annee['id'])

        layout_annee.addWidget(label_annee)
        layout_annee.addWidget(self.combo_annee)
        self.combo_annee.currentIndexChanged.connect(self.reset_echeance_data)

        def list_months_between():
            self.months = []
            data_list = anneeAcademique
            print(data_list)
            if isinstance(data_list, str):
                try:
                    data_list = json.loads(data_list)
                except json.JSONDecodeError:
                    print("Erreur: anneeAcademique n'est pas un JSON valide")

            selected_id = self.combo_annee.currentData()

             
            matches = [c for c in data_list if c['id'] == selected_id]
            
            if matches:
                data = matches[0]  
                 
                start_dt = datetime.strptime(data['date_debut'], '%Y-%m-%d')
                end_dt = datetime.strptime(data['date_fin'], '%Y-%m-%d')
                
                current_date = start_dt
                 
                while current_date <= end_dt:
                    self.months.append(current_date.strftime("%B")) # Ajoute le nom du mois
                     
                    next_month = current_date.replace(day=28) + timedelta(days=4)
                    current_date = next_month.replace(day=1)
                    
                print(f"Mois générés : {self.months}")
                return self.months

  
        self.combo_annee.currentIndexChanged.connect(list_months_between)


        self.horizontal_frame = QFrame()
        horizontal_layout = QHBoxLayout(self.horizontal_frame)

        horizontal_layout.setContentsMargins(0,0,0,0)
        # Mode de Paiement
        frame_payer_par = QFrame()
        layout_payer_par = QVBoxLayout(frame_payer_par)
        layout_payer_par.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_paiement_par = QLabel("Payer par")
        self.echeance = QComboBox()
        self.echeance.addItem("Payer par",None)
        self.echeance.addItems(["mois", "Trimestre", "Versement", "Session"])
        layout_payer_par.addWidget(label_paiement_par)
        layout_payer_par.addWidget(self.echeance)

        # Nombre de Paiements
        self.frame_payer_par_1 = QFrame()
        self.layout_payer_par_1 = QVBoxLayout(self.frame_payer_par_1)
        # self.layout_payer_par_1.setContentsMargins(10,0,10,2)
        self.layout_payer_par_1.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label_paiement_par_1 = QLabel(f"Nbres de {self.echeance.currentText()}")
        self.nb_echeance = QComboBox()
        self.nb_echeance.addItems([str(i) for i in range(1, 6)])
        self.layout_payer_par_1.addWidget(self.label_paiement_par_1)
        self.layout_payer_par_1.addWidget(self.nb_echeance)

        
        horizontal_layout.addWidget(frame_annee)
        horizontal_layout.addWidget(frame_payer_par)
        horizontal_layout.addWidget(self.frame_payer_par_1)

        self.nb_echeance.currentIndexChanged.connect(self.create_other_fiels)

        # Connexion du signal
        self.echeance.currentIndexChanged.connect(self.controle_other)

        if self.echeance.currentText() !='mois':
            self.create_other_fiels()

        self.frame_accessoire = QFrame()
        layout_accesssoire = QVBoxLayout(self.frame_accessoire)
        self.add_accessoire = QPushButton("Ajouter Accessoire")
        self.add_accessoire.setStyleSheet("""
                QPushButton {
                text-align: center;
                padding: 5px;
                min-width: 150px;
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
        layout_accesssoire.addWidget(self.add_accessoire)
        layout_accesssoire.setContentsMargins(10,2,10,2)
        self.add_accessoire.clicked.connect(self.ajouter_accessoir)
        layout_accesssoire.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.last_frame = QFrame()
        self.last_layout = QHBoxLayout(self.last_frame)

        #Frais dentre
        self.frame_frai_dentre_montant = QFrame()
        layout_frai_dentre_montant = QVBoxLayout(self.frame_frai_dentre_montant)
        layout_frai_dentre_montant.setAlignment(Qt.AlignmentFlag.AlignTop)
        first_month = self.months[0] if len(self.months) > 1 else "Premier mois"
        label_frais_dentre = QLabel(f"Frais d'entre (+) {first_month}")
        self.input_frais_dentre = QLineEdit()
        self.input_frais_dentre.setPlaceholderText("Frais dentre")
        layout_frai_dentre_montant.addWidget(label_frais_dentre)
        layout_frai_dentre_montant.addWidget(self.input_frais_dentre)
            
        #Montant
        self.frame_payer_montant = QFrame()
        layout_payer_montant = QVBoxLayout(self.frame_payer_montant)        
        layout_payer_montant.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_montant = QLabel("Montant")
        self.input_montant = QLineEdit()
        self.input_montant.setPlaceholderText("Saisir le montant")
        layout_payer_montant.addWidget(label_montant)
        layout_payer_montant.addWidget(self.input_montant)
        


        # Devise
        frame_payer_devise = QFrame()
        layout_payer_devise = QVBoxLayout(frame_payer_devise)
        layout_payer_devise.setAlignment(Qt.AlignmentFlag.AlignTop)
        label_devise = QLabel("Devise")
        self.input_devise = QComboBox()
        self.input_devise.addItems(["GDES", "USD"])
        layout_payer_devise.addWidget(label_devise)
        layout_payer_devise.addWidget(self.input_devise)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setObjectName("btn_annuler")
        btn_annuler.clicked.connect(self.dialog.close)

        self.btn_enregistrer = QPushButton("Enregistrer")
        self.btn_enregistrer.setObjectName("btn_enregistrer")
        self.btn_enregistrer.clicked.connect(self.save_payment_params)
        # self.btn_enregistrer.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.btn_enregistrer.setStyleSheet("""
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

        self.input_edit_params_payment = QLineEdit()
        self.input_edit_params_payment.setText("")
        self.index_classe=None
        print(anneeAcademique)
        if self.data_to_edit:
            # print(self.data_to_edit)
            data = self.data_to_edit.get('data',{})
            # print(data)
            self.btn_enregistrer.setText("Modifier")
            self.input_edit_params_payment.setText(data.get("id",""))
            niveau_id = data.get("niveau_id","")
            classe = data.get("classe","")
            self.index_classe=classe
            anneeAcad = data.get("anneeAcademique","")
            self.input_montant.setText(str(data.get("montant","")))
            nb_echeance = data.get("nb_echeance","")

            self.fill_combo_box(self.input_devise, data.get("devise",""))
            self.fill_combo_box(self.echeance, data.get("echeance",""))
            
            try:
                self.create_field = int(self.nb_echeance.currentText().strip() or 0)
            except ValueError:
                self.create_field = 0
            self.fill_combo_box(self.nb_echeance, nb_echeance) 
            

            self.fill_commbo_with_data(self.combo_cycle, niveau_id)

            self.fill_commbo_with_data(self.combo_classe, classe)
            self.fill_commbo_with_data(self.combo_annee, anneeAcad)
            # self.combo_annee.currentIndexChanged.connect(list_months_between)
            data_json = json.loads(data.get('montant_par', {})) if isinstance(data.get('montant_par', {}), str) else data.get('montant_par', {})

            if self.echeance and self.echeance.currentText() != 'mois':
                # self.create_field = self.nb_echeance.currentText()
                self.create_field = int(nb_echeance) #int(self.nb_echeance.currentText())
                
                if hasattr(self, 'dynamic_frame'):
                    while self.dynamic_frame.layout().count():
                        item = self.dynamic_frame.layout().takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    self.dynamic_frame.deleteLater()
                    del self.dynamic_frame

                versements = data_json.get('Versement', {}) if isinstance(data_json.get('Versement', {}), str) else data_json.get('Versement', {}) 


                self.dynamic_frame = QFrame()
                dynamic_fields_layout = QHBoxLayout(self.dynamic_frame)
                dynamic_fields_layout.setSpacing(2)
                dynamic_fields_layout.setContentsMargins(10, 0, 10, 2)

                self.payment_by = []

                for i in range(self.create_field):
                    field_frame = QFrame()
                    field_layout = QVBoxLayout(field_frame)
                    field_layout.setContentsMargins(10, 0, 10, 2)

                    label_text = f"{self.echeance.currentText()} {i + 1}"
                    field_label = QLabel(label_text)

                    object_name = f"{self.echeance.currentText()}_{i + 1}"
                    field_input = QLineEdit()
                    field_input.setStyleSheet("""font-size:13pt""")
                    field_input.setObjectName(object_name)
                    field_input.setPlaceholderText(label_text)

                    # Recherche dans le JSON une clé qui commence par object_name
                    matching_value = ""
                    for key, value in versements.items():
                        if key.startswith(object_name):
                            matching_value = value
                            break

                    field_input.setText(str(matching_value))

                    field_layout.addWidget(field_label)
                    field_layout.addWidget(field_input)

                    field_frame.setLayout(field_layout)
                    dynamic_fields_layout.addWidget(field_frame)

                    # self.payment_by.append(field_input)
                    self.payment_by.append({f"{self.echeance.currentText()}_{i + 1}_{self.combo_annee.currentData()}": field_input})

                self.dynamic_frame.setLayout(dynamic_fields_layout)
            else:
                mois_dict = data_json.get('mois', {}) if isinstance(data_json.get('mois', {}), str) else data_json.get('mois', {})

                sorted_items = sorted(
                    mois_dict.items(), 
                    key=lambda x: int(x[0].split('_')[1])
                )

                mois_ordonnes = dict(sorted_items)
                premiere_valeur = next(iter(mois_ordonnes.values()))
                self.input_frais_dentre.setText(str(premiere_valeur))



        btn_annuler.setStyleSheet("""
                QPushButton {
                text-align: center;
                padding: 5px;
                min-width: 100px;
                color: red; 
                border: 1px solid red; 
                border-radius: 5px; 
                font-size: 13pt;
            }
            QPushButton:hover { 
                color: #fff; 
                background-color: red;
            }
        """)

        button_layout.addWidget(btn_annuler)
        button_layout.addWidget(self.btn_enregistrer)

        # Ajout des widgets au layout principal
        self.first_layout.addWidget(frame_cycle)
        # self.layout.addWidget(frame_cycle)
        self.first_layout.addWidget(self.frame_faculte)
        self.first_layout.addWidget(frame_classe)        
        # self.layout.addWidget(self.frame_faculte)
        # self.layout.addWidget(frame_classe)
        self.layout.addWidget(self.first_frame)
        
        self.layout.addWidget(self.horizontal_frame)

        if self.data_to_edit and self.echeance.currentText() != 'mois':
            self.layout.addWidget(self.dynamic_frame)


        self.layout.addWidget(self.frame_accessoire)

        self.last_layout.addWidget(self.frame_frai_dentre_montant)
        self.last_layout.addWidget(self.frame_payer_montant)
        self.last_layout.addWidget(frame_payer_devise)

        self.layout.addWidget(self.last_frame)

        # self.layout.addWidget(frame_payer_devise)
        self.layout.addStretch()
        self.layout.addLayout(button_layout)
        self.dialog.setLayout(self.layout)
        self.fancy_modal_show(self.dialog)
        
        self.dialog.exec()

    def reset_echeance_data(self, anneeAcademique):
        if hasattr(self, 'dynamic_frame'):
            while self.dynamic_frame.layout().count():
                item = self.dynamic_frame.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.dynamic_frame.deleteLater()
            del self.dynamic_frame
        self.montant_par = {}
        self.payment_by = {}
        self.create_other_fiels()



    def controle_other(self):
        """Met à jour dynamiquement le label selon le mode de paiement choisi."""
        if self.echeance.currentText() and self.label_paiement_par_1:
            self.nb_echeance.setCurrentIndex(0)
            if self.echeance.currentText() != 'mois':                
                self.frame_payer_montant.setHidden(True) 
                self.frame_frai_dentre_montant.setHidden(True) 

                self.create_other_fiels()
            else:
                self.frame_payer_montant.setHidden(False)
                self.frame_frai_dentre_montant.setHidden(False)
                if hasattr(self, 'dynamic_frame'):
                    while self.dynamic_frame.layout().count():
                        item = self.dynamic_frame.layout().takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                    self.dynamic_frame.deleteLater()
                    del self.dynamic_frame
                self.montant_par = {}
                self.payment_by = {}


    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def fill_commbo_with_data(self,name_combo, default_value):
        index = name_combo.findData(default_value)
        if index >= 0:
            name_combo.setCurrentIndex(index)

    def create_other_fiels(self):
        """ Crée dynamiquement les champs de paiement selon l'échéance sélectionnée. """
       
        if self.echeance and self.echeance.currentText() != 'mois':
            self.create_field = int(self.nb_echeance.currentText())
            
            if hasattr(self, 'dynamic_frame'):
                while self.dynamic_frame.layout().count():
                    item = self.dynamic_frame.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                self.dynamic_frame.deleteLater()
                del self.dynamic_frame

           
            self.dynamic_frame = QFrame()
            dynamic_fields_layout = QHBoxLayout(self.dynamic_frame)
            dynamic_fields_layout.setSpacing(2)
            dynamic_fields_layout.setContentsMargins(10, 0, 10, 2)

            self.payment_by = [] 

            for i in range(self.create_field):
                field_frame = QFrame()
                field_layout = QVBoxLayout(field_frame)
                field_layout.setContentsMargins(10, 0, 10, 2)

                field_label = QLabel(f"{self.echeance.currentText()} {i + 1}")
                field_input = QLineEdit(field_frame) 
                field_input.setObjectName(f"{self.echeance.currentText()}_{i + 1}")
                field_input.setPlaceholderText(f"{self.echeance.currentText()} {i + 1}")

                field_layout.addWidget(field_label)
                field_layout.addWidget(field_input)
                field_frame.setLayout(field_layout)

                
                self.payment_by.append({f"{self.echeance.currentText()}_{i + 1}_{self.combo_annee.currentData()}": field_input})
                
                dynamic_fields_layout.addWidget(field_frame)
                
            for i in range(self.layout.count()):
                widget = self.layout.itemAt(i).widget()
                
                if widget == self.horizontal_frame:
                    self.layout.insertWidget(i + 1, self.dynamic_frame)
                    break

          
            self.layout.update()
            dialog = self.layout.parent()

            if dialog:
                dialog.adjustSize()


    def load_classe(self):
        selected_id = self.combo_cycle.currentData()
        self.combo_classe.clear() 
        self.combo_faculte.clear()  
     
        self.api_handler_.class_and_other(selected_id)
        



    def ajouter_accessoir(self):
        # Vérifier si le QScrollArea existe déjà, sinon le créer
        if not hasattr(self, "scroll_area"):
            self.scroll_area = QScrollArea()
            self.scroll_area.setStyleSheet("""
             background-color:#9e9e9e
        """)
            self.scroll_area.setWidgetResizable(True)
                        
            self.scroll_widget = QWidget()
            
            self.scroll_layout = QVBoxLayout(self.scroll_widget) 
            # self.scroll_layout.minimumSize()
            self.scroll_area.setWidget(self.scroll_widget)
            self.scroll_layout.setSpacing(0)

            # Ajouter le scroll_area à ton layout principal après frame_accessoire
            for i in range(self.layout.count()):
                widget = self.layout.itemAt(i).widget()
                if widget == self.frame_accessoire:
                    self.layout.insertWidget(i + 1, self.scroll_area)
                    # self.layout.setContentsMargins(20, 0, 20, 0) 
                    break
 
        self.scroll_area.setFixedHeight(400) 

        row_frame = QFrame()
        row_layout = QGridLayout(row_frame)
        
        combo_box = QComboBox()
        line_edit1 = QLineEdit()
        supprimer = QPushButton("Supprimer")

        combo_box.addItem("Sélectionner un accessoire")
        combo_box.setItemData(0, 0, Qt.ItemDataRole.UserRole - 1) 

        combo_box.addItems(['Maillot', 'Badge', 'Tenue de Sport', 'Initiale'])

        self.scroll_widget.setStyleSheet("""
        QComboBox, QLineEdit{ width: 200px; background-color:#2e2e2e}
        """)

        supprimer.setFlat(True)
        line_edit1.setPlaceholderText('Prix')

        row_layout.setSpacing(15)

        # Ajouter les widgets au QFrame
        row_layout.addWidget(combo_box, 0, 0)
        row_layout.addWidget(line_edit1, 0, 1)
        row_layout.addWidget(supprimer, 0, 2)

        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame))

        donnee = {
            "type_daccessoire": combo_box,
            "prix": line_edit1,
        }
        self.accessoire.append(donnee)  # Ajouter à la liste

        # Ajouter le QFrame à la zone de scroll
        self.scroll_layout.addWidget(row_frame)

        # Forcer la mise à jour
        self.scroll_layout.update()
        self.scroll_area.update()
        self.scroll_widget.adjustSize()
        self.scroll_area.ensureVisible(0, self.scroll_widget.height())  

    def supprimer_ligne(self, frame):
        """ Supprime une ligne en retirant le QFrame du layout """
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget == frame:
                self.scroll_layout.removeWidget(frame)
                frame.deleteLater()
                break


        self.accessoire = [item for item in self.accessoire if item["type_daccessoire"].parent() != frame]

        # Mettre à jour la vue
        self.scroll_layout.update()
        self.scroll_area.update()
        


    def save_payment_params(self):
        self.btn_enregistrer.setDisabled(True)
        # self.btn_enregistrer.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.overlay.start_loading("Traitment en cours")
        self.montant_par = {}
        self.accessoires = []
        
        print(self.months)
        if self.echeance.currentText() == "mois":
            # if len(self.months) < 1:
            #     self.btn_enregistrer.setDisabled(False)
            #     return 
            for index, month in enumerate(self.months):
                # Création d'une clé unique pour chaque mois
                key = f"{month}_{index + 1}_{self.combo_annee.currentData()}"
                 
                if index == 0: 
                    self.montant_par[key] = float(self.input_frais_dentre.text() or 0)
                else: 
                    self.montant_par[key] = float(self.input_montant.text() or 0)

                # print(f"Répartition générée : {self.montant_par}")
        else:
            for line in self.payment_by:
                for key, value in line.items():
                    self.montant_par[key] = value.text()

        

                
        for ligne in self.accessoire:            
            ligne_donnees = {
                "type_daccessoire": ligne["type_daccessoire"].currentText(),
                "prix": ligne["prix"].text(),
            }
            self.accessoires.append(ligne_donnees)  
 
        response = self.api_handler_.enregistrer_parametre_de_paiement(id=self.input_edit_params_payment.text(),niveau_id= self.combo_cycle.currentData(),
        faculte_id= self.combo_faculte.currentData(),
                                                    
        classe= self.combo_classe.currentData(),
        echeance= self.echeance.currentText(),
        devise= self.input_devise.currentText(),
        anneeAcademique= self.combo_annee.currentData(),
        nb_echeance= self.nb_echeance.currentText(),
        montant= self.input_montant.text() if self.input_montant else None,
        montant_par= self.montant_par,  
        accessoires= self.accessoires,
        )
    #    self.months
    #     self.input_frais_dentre


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
        self.btn_enregistrer.setDisabled(False)
        if endpoint.startswith("v1/niveau-with-class"):
            self.classes___=response_data
            self.combo_classe.clear()
            for classe in response_data['classe_actuelle']:
                self.combo_classe.addItem(classe['nom_classe'], classe['id']) 
            
            if self.index_classe:
                self.fill_commbo_with_data(self.combo_classe, self.index_classe)

            if self.combo_cycle.currentText() != 'Universitaire' and self.combo_cycle.currentText() != 'Technique':
                self.frame_faculte.setHidden(True)
            else:
                self.frame_faculte.setHidden(False)
                self.combo_faculte.clear()
                for faculte in response_data['facultes']:
                    self.combo_faculte.addItem(faculte['nom'], faculte['id'])
                # if response_data and 'classe_actuelle' in response_data: 

        if response_data and 'success' in response_data:
            self.input_edit_params_payment.setText("")
            self.ligne_ajoutee.emit()
            self.dialog.close()
        self.overlay.finish_loading()

    def generic_error_handler(self, endpoint, method, error_msg, response_data):
        self.btn_enregistrer.setDisabled(False)
        print("Response error content:", response_data, error_msg, endpoint)
        mapping = {
            'niveau_id': self.combo_cycle,
        'faculte_id': self.combo_faculte,
                                                    
        'classe': self.combo_classe,
        'echeance': self.echeance,
        'devise': self.input_devise,
        'anneeAcademique': self.combo_annee,
        'montant_par': self.nb_echeance,
        'montant': self.input_montant,
        'montant_par': self.echeance, #self.payment_by,  
        'accessoires': self.accessoires
          }  

        HandlerHerror().show_erros(error_msg=error_msg, response_data=response_data,mapping_field=mapping, overlay=self.overlay)
        self.overlay.finish_loading()

    def fancy_modal_show(self, widget):
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup
        from PySide6.QtWidgets import QGraphicsOpacityEffect, QApplication

        # 1. Préparation de l'état initial (invisible et décalé)
        eff = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(eff)
        eff.setOpacity(0)
        
        widget.show()
        widget.raise_()
        
        # Forcer le calcul du layout pour obtenir la position finale réelle
        widget.adjustSize()
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

    # def fancy_modal_show(self, widget):
    #     from PySide6.QtCore import QPropertyAnimation, QEasingCurve,QPoint
    #     from PySide6.QtWidgets import QGraphicsOpacityEffect,QApplication

    #     widget.show()
    #     widget.raise_()
    #     widget.activateWindow()

    #     # ⚠️ Forcer Qt à calculer la vraie position
    #     widget.adjustSize()
    #     widget.repaint()
    #     QApplication.processEvents()
        
    #     final_pos = widget.pos()
    #     start_pos = final_pos + QPoint(0, 30)

    #     # --- Opacité ---
    #     eff = QGraphicsOpacityEffect(widget)
    #     widget.setGraphicsEffect(eff)

    #     anim_op = QPropertyAnimation(eff, b"opacity")
    #     anim_op.setDuration(600)
    #     anim_op.setStartValue(0)
    #     anim_op.setEndValue(1)

    #     # --- Slide ---
    #     anim_pos = QPropertyAnimation(widget, b"pos")
    #     anim_pos.setDuration(600)
    #     anim_pos.setStartValue(start_pos)
    #     anim_pos.setEndValue(final_pos)
    #     anim_pos.setEasingCurve(QEasingCurve.OutCubic)

    #     # --- Start ---
    #     time.sleep(0.1)
    #     anim_op.start()
    #     anim_pos.start()

    #     anim_op.finished.connect(lambda: widget.setGraphicsEffect(None))

    #     # Garder références
    #     self._modal_anim = [anim_op, anim_pos]


