from PySide6.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, QComboBox, QLabel, QLineEdit, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtGui import QCursor, QColor
from PySide6.QtCore import Qt, Signal   

from Models.fetch_data import Fech_data
from Models.enregistrement import Save_data
from Helper.applique_erreurs import appliquer_erreurs

class Frais_divers(QDialog):
    ligne_ajoutee = Signal()

    def __init__(self, frais_edit):
        super().__init__()
        
        # Configuration de la fenêtre sans bordure et transparente
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Création du conteneur principal avec ombre
        self.container = QFrame()
        self.container.setStyleSheet("""
            background: white;
            border-radius: 5px;
            border: none;
        """)
        
        # Configuration de l'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        # shadow.setColor(QColor(190, 190, 190,150)) 
        # shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(5, 5)
        self.container.setGraphicsEffect(shadow)
        
        # Style global
        self.setStyleSheet("""
            QFrame {
                background: white;
            }
            QComboBox, QLineEdit { 
                width: 400px; 
                min-height: 33px; 
                max-height: 33px;
                border: 1px solid #999; 
                border-radius: 5px;
                padding-left: 7px;
                font-size: 13pt;
            }
            QComboBox:hover, QComboBox:focus, 
            QLineEdit:hover, QLineEdit:focus {
                border: 1px solid #007bff;
            }
            QLabel {
                font-size: 13pt;
            }
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
        self.frais_edit = frais_edit
        
        # Variables pour le déplacement de la fenêtre
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self._drag_pos)
            self._drag_pos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def enregistrer_frais_divers(self, niveaux):
        # Layout principal du conteneur
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Frame et layout pour le niveau
        self.frame_niveau = QFrame()
        layout_niveau = QVBoxLayout(self.frame_niveau)
        layout_niveau.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_niveau.setSpacing(4)
        
        label_niveau = QLabel("Cycle / Section / Niveau")
        self.combo_niveau = QComboBox()
        self.combo_niveau.setPlaceholderText('Cycle / Section / Niveau')
        self.combo_niveau.clear()
        
        for niveau in niveaux:
            self.combo_niveau.addItem(niveau['name'], niveau['id'])
        
        layout_niveau.addWidget(label_niveau)
        layout_niveau.addWidget(self.combo_niveau)
        main_layout.addWidget(self.frame_niveau)

        # Frame et layout pour l'année académique
        self.frame_annee = QFrame()
        layout_annee = QVBoxLayout(self.frame_annee)
        layout_annee.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_annee.setSpacing(4)
        
        label_annee = QLabel("Année Académique")
        self.combo_annee = QComboBox()
        self.combo_annee.setPlaceholderText('Choisir l\'année académique')
        self.combo_annee.clear()
        
        for annee in self.fetch_data_.annee_academique():
            self.combo_annee.addItem(annee['annee_academique'], annee['id'])
        
        layout_annee.addWidget(label_annee)
        layout_annee.addWidget(self.combo_annee)
        main_layout.addWidget(self.frame_annee)

        # Frame et layout pour la description
        self.frame_description = QFrame()
        layout_description = QVBoxLayout(self.frame_description)
        layout_description.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_description.setSpacing(4)
        
        label_description = QLabel("Description")
        self.input_description = QLineEdit()
        self.input_description.setPlaceholderText("Ex: 1000gdes")
        
        layout_description.addWidget(label_description)
        layout_description.addWidget(self.input_description)
        main_layout.addWidget(self.frame_description)

        # Frame et layout pour le prix
        self.frame_frais = QFrame()
        layout_frais = QVBoxLayout(self.frame_frais)
        layout_frais.setAlignment(Qt.AlignmentFlag.AlignTop) 
        layout_frais.setSpacing(4)
        
        label_frais = QLabel("Prix")
        self.input_frais = QLineEdit()
        self.input_frais.setPlaceholderText("Ex: 1000gdes")
        self.id_input_frais = QLineEdit()
        self.id_input_frais.setText("")
        self.id_input_frais.setVisible(False)  # Champ caché pour l'ID
        
        layout_frais.addWidget(label_frais)
        layout_frais.addWidget(self.input_frais)
        layout_frais.addWidget(self.id_input_frais)
        main_layout.addWidget(self.frame_frais)

        # Bouton Enregistrer/Modifier
        self.save_button = QPushButton("Enregistrer")
        self.save_button.setCursor(Qt.PointingHandCursor)

        if self.frais_edit:
            frais_to_edit = self.frais_edit.get('data', '')
            self.id_input_frais.setText(frais_to_edit.get("id", ""))
            self.input_frais.setText(frais_to_edit.get("prix", ""))
            self.input_description.setText(frais_to_edit.get("description", ""))
            annee = frais_to_edit.get("annee_academique", "")
            niveau = frais_to_edit.get("niveau", "")
            self.fill_combo_box(self.combo_annee, annee)
            self.fill_combo_box(self.combo_niveau, niveau)
            self.save_button.setText("Modifier")
        
        self.save_button.clicked.connect(self.enregistrer)
        
        # Layout pour le bouton
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(button_layout)

        # Layout principal de la fenêtre
        window_layout = QVBoxLayout(self)
        window_layout.addWidget(self.container)
        window_layout.setContentsMargins(15, 15, 15, 15)
        # window_layout.setContentsMargins(10, 10, 10, 10)  # Espace pour l'ombre
        
        self.exec()

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def enregistrer(self):
        self.save_button.setDisabled(True)
        self.save_button.setCursor(QCursor(Qt.CursorShape.WaitCursor))
    
        annee = self.combo_annee.currentData()
        niveau = self.combo_niveau.currentData()
        montant = self.input_frais.text().strip()
        description = self.input_description.text().strip()
        
        response = self.save_data.enregistrer_frais_divers(
            id=self.id_input_frais.text(),
            prix=montant, 
            description=description,
            niveau_id=niveau, 
            anneeAc=annee
        )
        
        if response:
            if response.get('errors'): 
                erreurs = response.get('errors')
                print(f"erreurs: {erreurs}")
                appliquer_erreurs(erreurs,        
                    ("niveau_id", self.combo_niveau),
                    ("anneeAc", self.combo_annee), 
                    ("prix", self.input_frais), 
                )
            if response.get('success'):
                self.ligne_ajoutee.emit()
                self.close()

        self.save_button.setDisabled(False)
        self.save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))