# import cv2
# import numpy as np


import cv2
import numpy as np
# from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
#                             QPushButton, QLineEdit, QFileDialog, QColorDialog, 
#                             QFontDialog, QMessageBox, QSlider, QComboBox)
# from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPen, QBrush
# from PyQt5.QtCore import Qt, QTimer, QPoint, QRect

class BadgeDesignDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Concepteur de badge avancé")
        self.setFixedSize(1000, 700)
        
        # Variables de personnalisation
        self.template_image = None
        self.student_photo = None
        self.current_font = QFont("Arial", 12)
        self.text_color = QColor(0, 0, 0)
        self.student_data = {}
        
        # Initialisation webcam
        self.cap = cv2.VideoCapture(0)
        self.camera_active = False
        
        self.init_ui()
        
    def init_ui(self):
        # Création des layouts
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        
        # Section template
        self.template_group = QGroupBox("Template du badge")
        template_layout = QVBoxLayout()
        
        self.template_label = QLabel()
        self.template_label.setFixedSize(400, 400)
        self.template_label.setStyleSheet("border: 1px solid #aaa; background-color: white;")
        self.template_label.setAlignment(Qt.AlignCenter)
        
        self.load_template_btn = QPushButton("Choisir un template")
        
        template_layout.addWidget(self.template_label)
        template_layout.addWidget(self.load_template_btn)
        self.template_group.setLayout(template_layout)
        
        # Section photo étudiant
        self.photo_group = QGroupBox("Photo de l'étudiant")
        photo_layout = QVBoxLayout()
        
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(200, 200)
        self.photo_label.setStyleSheet("border: 1px solid #aaa;")
        self.photo_label.setAlignment(Qt.AlignCenter)
        
        # Boutons photo
        self.btn_layout = QHBoxLayout()
        self.webcam_btn = QPushButton("Activer Webcam")
        self.snapshot_btn = QPushButton("Prendre photo")
        self.load_photo_btn = QPushButton("Charger fichier")
        
        self.btn_layout.addWidget(self.webcam_btn)
        self.btn_layout.addWidget(self.snapshot_btn)
        self.btn_layout.addWidget(self.load_photo_btn)
        
        photo_layout.addWidget(self.photo_label)
        photo_layout.addLayout(self.btn_layout)
        self.photo_group.setLayout(photo_layout)
        
        # Recherche étudiant
        self.search_group = QGroupBox("Recherche étudiant")
        search_layout = QVBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nom ou ID étudiant")
        self.search_btn = QPushButton("Rechercher")
        self.student_info = QLabel("Aucun étudiant sélectionné")
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)
        search_layout.addWidget(self.student_info)
        self.search_group.setLayout(search_layout)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.font_btn = QPushButton("Choisir police")
        self.text_color_btn = QPushButton("Couleur du texte")
        
        # Position des éléments
        self.position_group = QGroupBox("Position des éléments")
        position_layout = QVBoxLayout()
        
        self.photo_pos_btn = QPushButton("Définir position photo")
        self.name_pos_btn = QPushButton("Définir position nom")
        self.id_pos_btn = QPushButton("Définir position ID")
        
        position_layout.addWidget(self.photo_pos_btn)
        position_layout.addWidget(self.name_pos_btn)
        position_layout.addWidget(self.id_pos_btn)
        self.position_group.setLayout(position_layout)
        
        options_layout.addWidget(self.font_btn)
        options_layout.addWidget(self.text_color_btn)
        options_layout.addWidget(self.position_group)
        options_group.setLayout(options_layout)
        
        # Boutons validation
        self.save_btn = QPushButton("Générer le badge")
        self.cancel_btn = QPushButton("Annuler")
        
        # Assemblage layout
        left_layout.addWidget(self.template_group)
        left_layout.addWidget(self.photo_group)
        
        right_layout.addWidget(self.search_group)
        right_layout.addWidget(options_group)
        right_layout.addStretch()
        right_layout.addWidget(self.save_btn)
        right_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        
        # Connexions
        self.load_template_btn.clicked.connect(self.load_template)
        self.webcam_btn.clicked.connect(self.toggle_webcam)
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        self.load_photo_btn.clicked.connect(self.load_student_photo)
        self.font_btn.clicked.connect(self.choose_font)
        self.text_color_btn.clicked.connect(self.choose_text_color)
        self.search_btn.clicked.connect(self.search_student)
        self.photo_pos_btn.clicked.connect(lambda: self.set_position('photo'))
        self.name_pos_btn.clicked.connect(lambda: self.set_position('name'))
        self.id_pos_btn.clicked.connect(lambda: self.set_position('id'))
        self.save_btn.clicked.connect(self.generate_badge)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Positions par défaut
        self.positions = {
            'photo': QPoint(50, 50),
            'name': QPoint(300, 100),
            'id': QPoint(300, 150)
        }
        
        # Timer pour preview webcam
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_webcam_preview)

    def load_template(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Charger un template", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.template_image = cv2.imread(file_path)
            if self.template_image is not None:
                self.update_template_display()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger le template")

    def update_template_display(self):
        if self.template_image is not None:
            rgb_image = cv2.cvtColor(self.template_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.template_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.template_label.width(), self.template_label.height(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def load_student_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Charger une photo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.student_photo = cv2.imread(file_path)
            if self.student_photo is not None:
                self.update_student_photo_display()
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de charger la photo")

    def update_student_photo_display(self):
        if self.student_photo is not None:
            rgb_image = cv2.cvtColor(self.student_photo, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
                self.photo_label.width(), self.photo_label.height(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def toggle_webcam(self):
        if not self.camera_active:
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    QMessageBox.warning(self, "Erreur", "Webcam non disponible")
                    return
            self.camera_active = True
            self.timer.start(30)
            self.webcam_btn.setText("Désactiver Webcam")
        else:
            self.camera_active = False
            self.timer.stop()
            self.webcam_btn.setText("Activer Webcam")

    def update_webcam_preview(self):
        ret, frame = self.cap.read()
        if ret:
            self.student_photo = frame.copy()
            self.update_student_photo_display()

    def take_snapshot(self):
        if self.camera_active and self.student_photo is not None:
            self.toggle_webcam()
            QMessageBox.information(self, "Succès", "Photo enregistrée avec succès")

    def search_student(self):
        search_term = self.search_input.text().strip()
        if not search_term:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nom ou ID")
            return
        
        # Ici vous devriez implémenter la recherche dans votre base de données
        # Ceci est un exemple simulé
        self.student_data = {
            'id': 'STU2023',
            'last_name': 'DUPONT',
            'first_name': 'Jean',
            'class': 'Terminale A'
        }
        
        if self.student_data:
            self.student_info.setText(
                f"Nom: {self.student_data['last_name']}\n"
                f"Prénom: {self.student_data['first_name']}\n"
                f"Classe: {self.student_data['class']}\n"
                f"ID: {self.student_data['id']}"
            )
        else:
            QMessageBox.warning(self, "Erreur", "Étudiant non trouvé")

    def set_position(self, element_type):
        # if not self.template_image:
        if self.template_image is None or self.template_image.size == 0:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger un template")
            return
        
        # Ici vous pourriez implémenter un système de clic sur l'image
        # Pour simplifier, nous utilisons des positions prédéfinies
        QMessageBox.information(self, "Information", 
                              f"Cliquez sur le template pour positionner {element_type}")
        
        # Enregistrer la position (dans une vraie implémentation, vous captureriez le clic)
        if element_type == 'photo':
            self.positions['photo'] = QPoint(50, 50)
        elif element_type == 'name':
            self.positions['name'] = QPoint(300, 100)
        elif element_type == 'id':
            self.positions['id'] = QPoint(300, 150)
        
        QMessageBox.information(self, "Succès", f"Position {element_type} définie")

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.current_font = font

    def choose_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color

    def generate_badge(self):
        if not self.template_image:
            QMessageBox.warning(self, "Erreur", "Veuillez charger un template")
            return
            
        if not self.student_photo:
            QMessageBox.warning(self, "Erreur", "Veuillez ajouter une photo")
            return
            
        if not self.student_data:
            QMessageBox.warning(self, "Erreur", "Veuillez rechercher un étudiant")
            return

        # Créer une copie du template
        badge_image = self.template_image.copy()
        
        # Convertir en format Qt pour le dessin
        rgb_image = cv2.cvtColor(badge_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        badge = QPixmap.fromImage(qt_image)
        
        painter = QPainter(badge)
        painter.setFont(self.current_font)
        painter.setPen(self.text_color)
        
        # Ajouter la photo de l'étudiant
        if self.student_photo is not None:
            rgb_photo = cv2.cvtColor(self.student_photo, cv2.COLOR_BGR2RGB)
            h_photo, w_photo, _ = rgb_photo.shape
            qt_photo = QImage(rgb_photo.data, w_photo, h_photo, bytes_per_line, QImage.Format_RGB888)
            photo = QPixmap.fromImage(qt_photo).scaled(150, 150, Qt.KeepAspectRatio)
            painter.drawPixmap(self.positions['photo'], photo)
        
        # Ajouter le texte (nom en majuscule + prénom)
        full_name = f"{self.student_data['last_name']} {self.student_data['first_name']}"
        painter.drawText(self.positions['name'], full_name)
        painter.drawText(self.positions['id'], f"ID: {self.student_data['id']}")
        
        painter.end()
        
        # Enregistrer le badge
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le badge", "", "PNG (*.png)")
        if path:
            badge.save(path)
            QMessageBox.information(self, "Succès", "Badge généré avec succès")
            self.accept()
    
    def closeEvent(self, event):