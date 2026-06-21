import sys
import requests
import os
import base64
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QAbstractItemView, QFrame, QHBoxLayout, QHeaderView,QGridLayout,QLineEdit,QComboBox,QDateEdit,QPushButton,QLabel,QFrame, QVBoxLayout,QFileDialog,QGraphicsDropShadowEffect,QScrollArea,QDialog,QTableWidget,QWidget,QCheckBox
from PySide6.QtGui import *  
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QColor, QGraphicsBlurEffect

from PySide6.QtCore import * 
from io import BytesIO

from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PySide6.QtCore import QUrl, QByteArray
from Helper.Token_manager import TokenManager


# from Helper.Check import check_internet
from Helper.Check_data import verifier_donnees, config_donnees
from Models.connection import connect
from Models.enregistrement import enregistrer_etudiant, enregistrer_admin, enregistrer_professeur,enregistrer_cours
from Models.fetch_data import niveau_index,class_and_other,annee_academique,all_student,student_show,all_admin,admin_show, all_teacher, teacher_show,roles, all_cours, cours_show,all_programme,programme_show,teacher_combo,cours_combo,all_paiement,paiement_show,student_live,get_student_with_params_payment

from Views.main_view import Ui_MainWindow

documentTypes = [
    'Attestation', 'Certificat', 'Certificat de naissance',
    'Carte d\'identité',
    'Diplôme',
    'Relevé de notes',
    'Photo d\'identité', 'Autre',
]

sexe = {"Sexe", "M", "F"}

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.network_manager = QNetworkAccessManager(self)
        
        self.token_manager = TokenManager() 

 
                # Retirer les bordures
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1180, 690)
 
        shadow = QGraphicsDropShadowEffect(self)
        header = QGraphicsDropShadowEffect(self)
        widget = QGraphicsDropShadowEffect(self)

        widget.setBlurRadius(20)  
        widget.setColor(QColor(190, 190, 190,150))   
        widget.setOffset(0, 0)  

        header.setBlurRadius(30)  
        header.setColor(QColor(180, 180, 180,150))   
        header.setOffset(0, 5) 

        shadow.setBlurRadius(30)  
        shadow.setColor(QColor(0, 0, 0, 150))   
        shadow.setOffset(5, 5)   

        # Appliquer l'effet d'ombre à la fenêtre
        self.ui.centralwidget.setGraphicsEffect(shadow)
        self.ui.header.setGraphicsEffect(header)

        self.ui.etudiant_dash.setGraphicsEffect(widget)
        self.ui.professeur_dash.setGraphicsEffect(widget)
        self.ui.personnel_dash.setGraphicsEffect(widget)
        self.ui.classe_dash.setGraphicsEffect(widget)


        self.setStyleSheet("""
            /* Style pour la fenêtre principale */
            QMainWindow {
                background: transparent;
                border-radius: 15px;  
            }

            /* Style pour les QFrame */
            QFrame {
                background: transparent;
                
            }

            /* Style pour un QFrame spécifique avec l'objectName "frame" */
            #frame {
                background: transparent;  
            }
        """)
              # Variables pour le déplacement
        self.is_dragging = False
        self.drag_position = QPoint()

# ==========================DONNEE DEPUIS L'API==================================================
        self.niveau_selected = ''
        self.class_selected = ''
        self.annee_selected = ''
        self.role_selected = ''

        # self.row_count = 0  
        # self.cours_row_count = 0  
        
        self.main_layout = QVBoxLayout() 
        self.documents=[]
        self.cours_dictionary = []
        self.programme_dictionary = []
        self.student_live_search_table =QTableWidget()
        self.student_live_seach_input=''

        self.ui.widget_piece_inner.setLayout(self.main_layout)  

# =======================================RECHERCHER=================================================
        # self.ui.sesrch_student.textChanged.connect(lambda: all_student(self.ui.sesrch_student.text()))
        self.ui.sesrch_student.textChanged.connect(lambda: self.set_table_refresh_data_student())
        self.ui.search_admin.textChanged.connect(lambda: self.set_table_refresh_data_admin())
        self.ui.search_prof.textChanged.connect(lambda: self.set_table_refresh_data_teacher())
        self.ui.search_paiement.textChanged.connect(lambda: self.set_table_refresh_data_paiement())
        
# =======================================RECHERCHER=================================================

# ====================================PAGINATION========================================================
        self.current_page_student = 1
        self.total_pages_student = 1

        self.current_page_prof = 1
        self.total_pages_prof = 1

        self.current_page_admin = 1
        self.total_pages_admin = 1

        self.current_page_cours = 1
        self.total_pages_cours = 1

        self.current_page_programme = 1
        self.total_pages_programme = 1

        self.current_page_paiement = 1
        self.total_pages_paiement = 1
# ====================================PAGINATION========================================================


        self.ui.sexe.addItems(sexe)
        self.ui.sexe.setCurrentIndex(0)

        self.niveau = niveau_index()
        for niveau in self.niveau:
            self.ui.niveau_id.addItem(niveau['name'], niveau['id'])

        self.roles = roles() 
 
        self.annee_acades = annee_academique()
        for annee_acade in self.annee_acades:
            self.ui.annee_academique_id.addItem(annee_acade['annee_academique'], annee_acade['id']) 

        # Afficher l'ID sélectionné lors d'un changement
        self.ui.niveau_id.currentIndexChanged.connect(self.selection_changed_niveau)
        self.ui.annee_academique_id.currentIndexChanged.connect(self.selection_changed_annee_academique)
        self.ui.classe_actuelle_id.currentIndexChanged.connect(self.selection_changed_classe)
        self.ui.admin_role.currentIndexChanged.connect(self.selection_changed_role)

        self.ui.next_page_student.clicked.connect(self.next_page_student)
        self.ui.prev_page_student.clicked.connect(self.prev_page_student)

        self.ui.next_paiement.clicked.connect(self.next_paiement)
        self.ui.prev_paiement.clicked.connect(self.prev_paiement)

        self.ui.btn_close.clicked.connect(lambda: self.close())
        self.ui.btn_min.clicked.connect(self.toggle_maximize)
        self.ui.minimize.clicked.connect(self.showMinimized)

        current_dir = os.path.dirname(__file__)
        self.project_dir = os.path.dirname(current_dir)

        # Construct the full path to the icon
        icon_path_close = os.path.join(self.project_dir, 'assets', 'icons', 'close.png')
        icon_path_reduire = os.path.join(self.project_dir, 'assets', 'icons', 'reduire.png')
        minimize = os.path.join(self.project_dir, 'assets', 'icons', 'hide.png')
   
        
        self.ui.btn_close.setIcon(QIcon(icon_path_close))
        self.ui.btn_min.setIcon(QIcon(icon_path_reduire))
        self.ui.minimize.setIcon(QIcon(minimize))

        
        # self.token_manager.delete_token()
        if self.token_manager.get_token(): 
            image_url = config_donnees()['data'][0]['logo_image_url']
            self.load_image_from_url_for_dash(image_url, self.ui.logo_2)

            self.ui.main_with_shadow.setCurrentIndex(2)
            self.ui.stackedWidget.setCurrentIndex(0)
            # for i in range(self.ui.stackedWidget.count()):
            #     print(f"Index {i} -> {self.ui.stackedWidget.widget(i)}")
 
            # self.ui.main_with_shadow.setCurrentWidget(self.ui.shadow_windowPage1)  
            
            self.connect_buttons()

        else:
            if verifier_donnees(): 
                image_url = config_donnees()['data'][0]['logo_image_url']
                self.load_image_from_url(image_url, self.ui.logo)
                self.ui.main_with_shadow.setCurrentWidget(self.ui.connexion_page)
            else:
                self.ui.main_with_shadow.setCurrentWidget(self.ui.welcome)


        self.ui.btn_connexion.clicked.connect(self.se_connecter)
 
    def load_image_from_url(self, url, label):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Vérifie si la requête a réussi

            print(response)
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            
            if pixmap.loadFromData(image_data.read()): 
                # pixmap = pixmap.scaled(label.size())
                pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                 
                label.setStyleSheet("border-radius: 75px;") 
                print("Image chargée avec succès !")
            else:
                print("Erreur lors du chargement de l'image")

        except requests.exceptions.RequestException as e:
            print("Erreur de chargement d'image :", e)

    def load_image_from_url_for_dash(self, url, label):
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


    def connect_buttons(self):
          # self.ui.main_with_shadow.setCurrentWidget(self.ui.shadow_windowPage1) 
        self.ui.main_with_shadow.setCurrentIndex(2)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.btn_left_deconnexion.clicked.connect(self.deconnexion)

        self.ui.btn_left_home.clicked.connect(self.dash_page)
        self.ui.btn_left_admin.clicked.connect(self.admin_page)
        self.ui.btn_left_etudiant.clicked.connect(self.etudiant_page)

        self.ui.btn_left_paiement.clicked.connect(self.paiement_page)
        self.ui.paiement_dialog.clicked.connect(self.search_student)

        self.ui.btn_left_prof.clicked.connect(self.professeur_page)

        self.ui.btn_left_cours.clicked.connect(self.cours_page)
        self.ui.cours_stack.clicked.connect(self.cours_page)
        self.ui.addCours.clicked.connect(self.add_cours_page)
        self.ui.add_course_line.clicked.connect(self.add_cours_line)
        self.ui.enregistrer_cours.clicked.connect(self.enregistrer_cours)

        self.ui.programme_stack.clicked.connect(self.programme_index)
        self.ui.addProgramme.clicked.connect(self.add_programme_page)
        self.ui.add_programme_line.clicked.connect(self.add_programme_line)
        self.ui.enregistrer_programme.clicked.connect(self.enregistrer_programme)

        self.ui.btn_left_notes.clicked.connect(self.notes_page)
        self.ui.btn_left_promus.clicked.connect(self.promus_page)
        self.ui.btn_left_vente.clicked.connect(self.vente_page)
        self.ui.btn_left_rapport.clicked.connect(self.rapport_page)

        self.ui.add_student.clicked.connect(self.add_student_page)
        self.ui.suivant_1.clicked.connect(self.responsable_info)
        self.ui.suivant_2.clicked.connect(self.pieces_soumise)
        self.ui.ajouter_document.clicked.connect(self.ajouter_document)
        self.ui.enregistre.clicked.connect(self.sauvegarde_etudiant)

        self.ui.add_personnel.clicked.connect(self.add_personnel)
        self.ui.enregistrer_admin.clicked.connect(self.sauvegarder_admin)

        self.ui.add_prof_button.clicked.connect(self.add_professeur)
        self.ui.enregistrer_prof.clicked.connect(self.sauvegarder_professeur)

    def deconnexion(self):
        self.token_manager.delete_token()


    def se_connecter(self):
        email = self.ui.email_2.text()
        password = self.ui.password_2.text()
        
        
        if not email or not password:
            self.ui.error_message.setText("Veuillez remplir tous les champs.")            
            return
         
        response = connect(email, password)
        # print(response)
        if 'errors' in response:
            self.ui.password_2.setText('')
            self.ui.error_message.setText(response["errors"]['email'][0]) 
            return

        if response or self.token_manager.get_token():
            image_url = config_donnees()['data'][0]['logo_image_url']
            self.load_image_from_url_for_dash(image_url, self.ui.logo_2)

            # self.ui.main_with_shadow.setCurrentWidget(self.ui.shadow_windowPage1)
            self.ui.main_with_shadow.setCurrentIndex(2)
 
            self.token_manager.save_token(response["token"])

            self.connect_buttons()
             

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

        supprimer.setObjectName("supprimer")
        chose_file.setObjectName("chose_file")
        label_file.setObjectName("label_file")
        line_edit1.setObjectName("line_edit1")
        line_path.setObjectName("line_path")
        combo_box.setObjectName("combo_box")
        date_edit.setObjectName("date_edit")

        # label_file.setText('Image Choisie')
 
        combo_box.addItems(documentTypes)
        row_layout.setSpacing(15)
        # Ajouter les widgets à la ligne
        row_layout.addWidget(combo_box, 0, 0)
        row_layout.addWidget(line_edit1, 0, 1) 
        row_layout.addWidget(line_path, 1, 0) 
        row_layout.addWidget(date_edit, 0, 2)
        row_layout.addWidget(chose_file, 0, 3)
        row_layout.addWidget(label_file, 0, 4)
        row_layout.addWidget(supprimer, 0, 5)

        self.ui.widget_piece_inner.setStyleSheet(
            """
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
                min-width:20px
                border-radius: 5px;
            }

            #date_edit,#combo_box,#line_edit1{
            min-width:200px
            }
            """
        )
   
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

        self.row_count += 1
        # document_id = f"document_{len(self.documents) + 1}"

 
        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame))
        chose_file.clicked.connect(lambda: self.choisir_image(label_file,line_path))

        # Ajouter un document au dictionnaire avec une clé unique
        self.donnee= {
            "type_de_document" :combo_box,
            "document_numero" : line_edit1,
            "document_date_dexpiration" : date_edit,
            "document_image" :line_path
        }
        self.documents.append(self.donnee) 
 

    def supprimer_ligne(self, frame):
        """ Supprime une ligne en retirant le QFrame du layout """
        print('Suppression d\'une ligne')
        self.ui.widget_piece_inner.layout().removeWidget(frame)
        frame.deleteLater()

    def choisir_image(self, label_file,line_path):
        """ Ouvre un fichier image avec QFileDialog et affiche l'image dans le QLabel """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.xpm *.jpg *.jpeg *.gif *.bmp)", options=options)
        
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

    def mousePressEvent(self, event):
        # Lorsque l'on clique pour déplacer la fenêtre
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        # Déplacer la fenêtre si on fait glisser
        if self.is_dragging:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(self.pos() + delta)
            self.drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):  
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def toggle_maximize(self):  
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

# ==============================enregistre les etudiant============================================

    def sauvegarde_etudiant(self): 
        nom = self.ui.nom.text()
        prenom = self.ui.prenom.text()
        telephone = self.ui.telephone.text()
        sexe = self.ui.sexe.currentText()
        date_de_naissance = self.ui.date_de_naissance.text()
        adresse = self.ui.adresse.text()
        lieu_de_naissance = self.ui.lieu_de_naissance.text()
        religion = self.ui.religion.text()
        niveau_id = self.niveau_selected
        classe_actuelle_id = self.class_selected
        annee_academique_id = self.annee_selected
        faculte_id = self.ui.faculte_id.currentText()
        email = self.ui.email_3.text()
        nom_responsable = self.ui.nom_responsable.text()
        prenom_responsable = self.ui.prenom_responsable.text()
        email_responsable = self.ui.email_responsable.text()
        sexe_responsable = self.ui.sexe_responsable.text()
        telephone_responsable = self.ui.telephone_responsable.text()
        adresse_responsable =self.ui.adresse_responsable.text()

        documentss = []
        for ligne in self.documents:            
            ligne_donnees = {
                "document_numero": ligne["document_numero"].text(),
                "document_date_dexpiration": ligne["document_date_dexpiration"].date().toString("yyyy-MM-dd"),
                "type_de_document": ligne["type_de_document"].currentText(),
                # "document_image":ligne["document_image"].text()
                "document_image": self.convertir_image_en_base64(ligne["document_image"].text())
            }
            documentss.append(ligne_donnees)
        # print(documentss) 

        response = enregistrer_etudiant(nom,prenom,telephone,sexe,date_de_naissance, adresse,lieu_de_naissance,  religion,niveau_id,classe_actuelle_id,annee_academique_id,faculte_id,email,nom_responsable,prenom_responsable,email_responsable,sexe_responsable,telephone_responsable,adresse_responsable,documentss)

        print(response)

    def convertir_image_en_base64(self,chemin_image):
        """Convertit une image en Base64"""
        with open(chemin_image, "rb") as image_file:
            image_data = image_file.read()
        
            encoded_string = base64.b64encode(image_data).decode("utf-8", errors="ignore")  # Ignorer erreurs d'encodage
            extension = chemin_image.split('.')[-1].lower()
            print(f"data:image/{extension};base64,{encoded_string}")

        return f"data:image/{extension};base64,{encoded_string}"
        # with open(chemin_image, "rb") as image_file:
            # Lit l'image en binaire
            # encoded_string = base64.b64encode(image_file.read()).decode("utf-8")   
            # encoded_string = base64.b64encode(image_file.read()).decode("utf-8")  
            # print(encoded_string) 
        # return f"data:image/png;base64,{encoded_string}"
        # return encoded_string
# ==============================enregistre les etudiant============================================


            # Naviguer entrer les pages principales
    def dash_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.dash_page)
        self.ui.titre_toggle.setText("Dashboard")

# ==============================================__ADMINISTRATION__====================================

    def admin_page(self):
        self.set_table_refresh_data_admin()
        self.ui.stackedWidget.setCurrentWidget(self.ui.admin_page)
        self.ui.admin_stacked.setCurrentWidget(self.ui.index_admin)
        self.ui.titre_toggle.setText("Admin")

    def sauvegarder_admin(self):
        nom = self.ui.admin_nom.text()
        telephone = self.ui.admin_telephone.text()
        prenom = self.ui.admin_prenom.text()
        email = self.ui.admin_email.text()
        sexe = self.ui.admin_sexe.text()
        adresse = self.ui.admin_adresse.text()
        role = self.role_selected

        response = enregistrer_admin(nom=nom,prenom=prenom, telephone=telephone, email=email,sexe=sexe,adresse=adresse,role=role)

        if response.get('errors'): 
            erreurs =response.get('errors')
            self.appliquer_erreurs(erreurs, 
                ('prenom', self.ui.admin_prenom),
                ('nom', self.ui.admin_nom),
                ('email', self.ui.admin_email),
                ('adresse', self.ui.admin_adresse),
                ('telephone', self.ui.admin_telephone),
                ('role', self.ui.admin_role)
            )
        else:
            self.admin_page()
            self.clear_fields( self.ui.admin_nom, self.ui.admin_telephone, self.ui.admin_prenom, self.ui.admin_email,self.ui.admin_sexe, self.ui.admin_adresse,self.ui.admin_role  # QComboBox
        )
            # self.clear_admin()

    # def clear_admin(self):
        # self.ui.admin_nom.setText('')
        # self.ui.admin_telephone.setText('')
        # self.ui.admin_prenom.setText('')
        # self.ui.admin_email.setText('')
        # self.ui.admin_sexe.setText('')
        # self.ui.admin_adresse.setText('')
        # self.ui.admin_role.setCurrentIndex(0) 

        self.clear_fields(
            self.ui.admin_nom,
            self.ui.admin_telephone,
            self.ui.admin_prenom,
            self.ui.admin_email,
            self.ui.admin_sexe,
            self.ui.admin_adresse,
            self.ui.admin_role  # QComboBox
        )


    def add_personnel(self, personnel=None):
        for role in self.roles:
            self.ui.admin_role.addItem(role['name'], role['id'])
        self.ui.admin_stacked.setCurrentWidget(self.ui.add_admin)

    def set_table_refresh_data_admin(self, page=1):
        header = ("Id", "Nom", "prénom", "Sexe", 
                  "Email", "Téléphone",'Adresse', 'status')
        self.all_headers_table_labels(
            self.ui.admin_table, header,  "#e2e8f0", 32, 130, 150, 40, 195, 165, 180, 100)
        self.ui.admin_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
         
        table = all_admin(self.ui.search_admin.text(), page)
        self.current_page_admin = table["current_page"]
        self.total_pages_admin = table["total_pages"]
 
        # self.ui.prev_page_student.setEnabled(self.current_page_prof > 1)
        # self.ui.next_page_student.setEnabled(self.current_page_prof < self.total_pages_prof)
 
        # self.ui.prev_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """)

        # self.ui.next_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """) 
  
        self.select_all_populate(table['data'], self.ui.admin_table, self.on_row_clicked_admin)

    def on_row_clicked_admin(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.admin_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_admin = admin_show(id_item.text())
            self.add_personnel(show_admin)
       
            return id_item.text()

# ============================================== __ADMINISTRATION__====================================



# ================================================== __ETUDIANT__ ======================================
    def etudiant_page(self): 
        self.set_table_refresh_data_student()        
        self.ui.stackedWidget.setCurrentWidget(self.ui.etudiant_page)
        self.ui.stackedStudent.setCurrentWidget(self.ui.index_student)
        self.ui.titre_toggle.setText("Etudiant")

    def set_table_refresh_data_student(self, page=1):
        header = ("Id", "Identifiant", "Nom", "prénom", "Sexe", "Date de Naissance",
                  "Email", "Téléphone")
        self.all_headers_table_labels(
            self.ui.student_table, header,  "#e2e8f0", 32, 130, 110, 165, 40, 155, 190, 100, 100)
        self.ui.student_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
         
        table = all_student(self.ui.sesrch_student.text(), page)
        self.current_page_student = table["current_page"]
        self.total_pages_student = table["total_pages"]
 
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


        self.select_all_populate(table['data'],self.ui.student_table, self.on_row_clicked)

    def add_student_page(self, show_student=None):
        if show_student:
            self.ui.nom.setText(show_student['nom'])
            self.ui.prenom.setText(show_student['prenom'])
            self.fill_combo_box(self.ui.sexe, str(show_student['sexe']))
            self.ui.telephone.setText(show_student['telephone'])
            self.ui.adresse.setText(show_student['adresse'])   
            self.ui.lieu_de_naissance.setText(show_student['lieu_de_naissance'])
            self.ui.religion.setText(show_student['religion'])
            self.ui.email_3.setText(show_student['email'])
            
            date_str = show_student['date_de_naissance']   
            date_obj = QDate.fromString(date_str, "yyyy-MM-dd")

            if show_student['responsable']:
                self.ui.email_responsable.setText(show_student['responsable']['email_responsable'])
                self.ui.nom_responsable.setText(show_student['responsable']['nom_responsable'])
                self.ui.prenom_responsable.setText(show_student['responsable']['prenom_responsable'])
                self.ui.adresse_responsable.setText(show_student['responsable']['adresse_responsable'])
                self.ui.telephone_responsable.setText(show_student['responsable']['telephone_responsable'])
                self.ui.sexe_responsable.setText(show_student['responsable']['sexe_responsable'])

            # if show_student['classes']:
            #     last_class_id = show_student['classes'][-1]['id'] 
            #     self.fill_combo_box(self.ui.classe_actuelle_id, str(last_class_id))

            if show_student['classe_etudiant'] and 'niveaux' in show_student['classe_etudiant'][-1]:
                if show_student['classe_etudiant'][-1]['niveaux']:
                    niveau_name = show_student['classe_etudiant'][-1]['niveaux'][0]['name']  
                    self.fill_combo_box(self.ui.niveau_id, str(niveau_name))
                    print(self.ui.niveau_id.currentIndex())
                    self.selection_changed_niveau(self.ui.niveau_id.currentIndex())

                if show_student['classe_etudiant'][-1]['classes']:
                    nom_classe = show_student['classe_etudiant'][-1]['classes'][0]['nom_classe'] 
                    print(nom_classe) 
                    self.fill_combo_box(self.ui.classe_actuelle_id, str(nom_classe))

                if show_student['classe_etudiant'][-1]['annee_academiques']:
                    annee_academique = show_student['classe_etudiant'][-1]['annee_academiques'][0]['annee_academique']  
                    print(annee_academique)
                    self.fill_combo_box(self.ui.classe_actuelle_id, str(annee_academique))

            if show_student['etudiant_facultes'] and 'niveaux' in show_student['etudiant_facultes'][-1]:
                if show_student['etudiant_facultes'][-1]['niveaux']:
                    niveau_name = show_student['etudiant_facultes'][-1]['niveaux'][0]['name']  
                    self.fill_combo_box(self.ui.niveau_id, str(niveau_name))
 
              

            # Appliquer la date au widget QDateEdit
            self.ui.date_de_naissance.setDate(date_obj)

        # self.ui.stackedStudent.add_student_page.setCurrentWidget(self.ui.personnel_info)
        # self.ui.tabWidget.setCurrentWidget(self.ui.responsable_info) 

        #     self.ui.stackedWidget.addWidget(self.ui.personnel_info) 

        try:
            self.ui.stackedStudent.setCurrentWidget(self.ui.add_student_page)  
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.titre_toggle.setText("Ajouter Etudiant")
        except Exception as e:
            print(f"errors {e}")

    def fill_combo_box(self, name_combo, text):
        text_index = name_combo.findText(str(text))
        name_combo.setCurrentIndex(text_index)

    def pieces_soumise(self):
        # self.ui.type_de_document.addItems(documentTypes)
        # self.ui.type_de_document.setCurrentIndex(0)
        self.ui.tabWidget.setCurrentWidget(self.ui.pieces)

    def responsable_info(self):
        # self.ui.tabWidget.setCurrentIndex(1)responsable_info
        self.ui.tabWidget.setCurrentWidget(self.ui.responsable_info)

    def on_row_clicked(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.student_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_student = student_show(id_item.text())
            self.add_student_page(show_student)
       
            return id_item.text()

    def next_page_student(self):
        print(f"self.current_page_student {self.current_page_student} --- self.total_pages_student {self.total_pages_student}")
        if self.current_page_student < self.total_pages_student:
            self.set_table_refresh_data_student(page=self.current_page_student + 1)

    def prev_page_student(self):
        if self.current_page_student > 1:
            self.set_table_refresh_data_student(page=self.current_page_student - 1)
# ===================================================== __ETUDIANT__ ====================================

# ===========================================  __PAIEMENT__ =========================================

    def paiement_page(self):
        self.set_table_refresh_data_paiement()
      
        self.ui.stackedWidget.setCurrentWidget(self.ui.paiement_page)
        self.ui.stackedPaiement.setCurrentWidget(self.ui.index_paiement)
        self.ui.titre_toggle.setText("Paiement")

    def set_table_refresh_data_paiement(self, page=1):
        header = ("Id", "Identifiant","Nom", "prénom", "Année", 
                  "Niveau", "Classe")
        self.all_headers_table_labels(
            self.ui.paiement_table, header,  "#e2e8f0", 32, 200, 130, 250, 165, 165, 200)
        self.ui.paiement_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
         
        table = all_paiement(self.ui.search_paiement.text(), page)
        self.current_page_paiement = table["current_page"]
        self.total_pages_paiement = table["total_pages"]

        self.ui.prev_paiement.setHidden(self.total_pages_paiement < 12)
        self.ui.next_paiement.setHidden(self.total_pages_paiement < 12)
 
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
  
        self.select_all_populate(table['data'], self.ui.paiement_table, self.on_row_clicked_paiement)

    def on_row_clicked_paiement(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.paiement_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_paiement = paiement_show(id_item.text())
            # self.add_professeur(show_prof)
       
            return id_item.text()
        
    def next_paiement(self):
        if self.current_page_paiement < self.total_pages_paiement:
            self.set_table_refresh_data_paiement(page=self.current_page_paiement + 1)

    def prev_paiement(self):
        if self.current_page_paiement > 1:
            self.set_table_refresh_data_paiement(page=self.current_page_paiement - 1)

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



# ===========================================  __PROFESSEUR__ =========================================
    def professeur_page(self):
        self.set_table_refresh_data_teacher()
        self.ui.stackedWidget.setCurrentWidget(self.ui.professeur_page)
        self.ui.stacked_prof.setCurrentWidget(self.ui.index_prof)
        self.ui.titre_toggle.setText("Professeur")

    def add_professeur(self, professeur=None):
        self.ui.stacked_prof.setCurrentWidget(self.ui.add_prof)

    def sauvegarder_professeur(self):
        nom = self.ui.nom_prof.text()
        telephone = self.ui.telephone_prof.text()
        prenom = self.ui.prenom_prof.text()
        email = self.ui.email_prof.text()
        sexe = self.ui.sexe_prof.text()
        adresse = self.ui.adresse_prof.text()
        matiere_enseignee = self.ui.matiere_enseignee.text()

        response = enregistrer_professeur(nom=nom,prenom=prenom, telephone=telephone, email=email,sexe=sexe,adresse=adresse,matiere_enseignee=matiere_enseignee)

        # self.professeur_page()
        print(response)
        if response.get('errors'): 
            erreurs =response.get('errors')
            self.appliquer_erreurs(erreurs, 
                ('prenom', self.ui.prenom_prof),
                ('nom', self.ui.nom_prof),
                ('email', self.ui.email_prof),
                ('sexe', self.ui.sexe_prof),
                ('adresse', self.ui.adresse_prof),
                ('telephone', self.ui.telephone_prof),
                ('matiere_enseignee', self.ui.matiere_enseignee)
            )
        else:
            self.professeur_page()
            self.clear_fields( self.ui.nom_prof, self.ui.telephone_prof, self.ui.prenom_prof, self.ui.email_prof,self.ui.sexe_prof, self.ui.adresse_prof,self.ui.matiere_enseignee  # QComboBox
        )

    def set_table_refresh_data_teacher(self, page=1):
        header = ("Id", "Nom", "prénom", "Sexe", 
                  "Email", "Téléphone", 'status')
        self.all_headers_table_labels(
            self.ui.prof_table, header,  "#e2e8f0", 32, 130, 130, 40, 165, 165, 100)
        self.ui.prof_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
         
        table = all_teacher(self.ui.search_prof.text(), page)
        self.current_page_prof = table["current_page"]
        self.total_pages_prof = table["total_pages"]
 
        # self.ui.prev_page_student.setEnabled(self.current_page_prof > 1)
        # self.ui.next_page_student.setEnabled(self.current_page_prof < self.total_pages_prof)
 
        # self.ui.prev_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """)

        # self.ui.next_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """) 
  
        self.select_all_populate(table['data'], self.ui.prof_table, self.on_row_clicked_prof)

    def on_row_clicked_prof(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.prof_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_prof = teacher_show(id_item.text())
            self.add_professeur(show_prof)
       
            return id_item.text()

# ===========================================  PROFESSEUR =========================================

# ===========================================  __COURS__ =========================================
    def cours_page(self):
        self.prof_combo = teacher_combo()
        self.cours = cours_combo()
        self.set_table_refresh_data_cours()
       
        self.ui.stackedWidget.setCurrentWidget(self.ui.cours_page)
        self.ui.coursStaked.setCurrentWidget(self.ui.cours_staked_page)
        self.ui.stackedWidgetCours.setCurrentWidget(self.ui.index_cours)
        self.ui.titre_toggle.setText("Cours")

    def add_cours_page(self):
        self.ui.stackedWidgetCours.setCurrentWidget(self.ui.add_cours)

    def set_table_refresh_data_cours(self, page=1):
        header = ("Id", "Cours", "Note de passage", "Coéfficient")
        self.all_headers_table_labels(
            self.ui.cours_table, header,  "#e2e8f0", 32, 200, 200, 200, 200)
        self.ui.cours_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        table = all_cours(self.ui.search_cours.text(), page)
        self.current_page_cours = table["current_page"]
        self.total_pages_cours = table["total_pages"]

        # self.ui.prev_page_student.setEnabled(self.current_page_prof > 1)
        # self.ui.next_page_student.setEnabled(self.current_page_prof < self.total_pages_prof)

        # self.ui.prev_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """)

        # self.ui.next_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """) 

        self.select_all_populate(table['data'], self.ui.cours_table, self.on_row_clicked_cours)

    def on_row_clicked_cours(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.cours_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_cours = cours_show(id_item.text())
            # self.add_cours(show_cours)
            self.add_cours_page()
       
            return id_item.text()


    def add_programme_line(self): 
        row_frame = QFrame() 
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)

        # Déclaration des widgets
        niveau_id = QComboBox()
        cours_id = QComboBox()
        faculte_id = QComboBox()
        professeur_id = QComboBox()
        jours = QComboBox()
        annee_academique = QComboBox()
        session = QComboBox()
        classe = QComboBox()
        heure = QLineEdit() 
         
        supprimer = QPushButton("Supprimer")
        supprimer.setFlat(True)  

        heure.setPlaceholderText('Heure') 
        jours.setPlaceholderText('Jours') 
        cours_id.setPlaceholderText('Cours') 
        niveau_id.setPlaceholderText('Niveau') 
        professeur_id.setPlaceholderText('Professeur') 
        faculte_id.setPlaceholderText('Faculte') 
        classe.setPlaceholderText('Classe') 
        session.setPlaceholderText('Session') 
        annee_academique.setPlaceholderText('Annee Academique') 

        supprimer.setObjectName("supprimer")  
        # cours_nom.setObjectName("cours_nom")
        # note_de_passage.setObjectName("note_de_passage")
        # niveau_id.setObjectName("niveau_id")
        # coefficients.setObjectName("coefficients")


        for niveau in self.niveau:
            niveau_id.addItem(niveau['name'], niveau['id']) 

        for prof in self.prof_combo:
            professeur_id.addItem(prof['nom'], prof['id'])

        for cours in self.cours:
            cours_id.addItem(cours['cours_nom'], cours['id'])  

        #         self.ui.classe_actuelle_id.clear()
        # self.classes = class_and_other(selected_id)
        # for classe in self.classes:
        #     self.ui.classe_actuelle_id.addItem(classe['nom_classe'], classe['id']) 
        # return selected_id

        niveau_id.currentIndexChanged(self.selection_changed_niveau_for_combo(niveau_id=niveau_id, classe=classe))

        print(f"Niveau: {niveau_id.currentData()}") 
        row_layout.setSpacing(10)
        # Ajouter les widgets à la ligne
        row_layout.addWidget(niveau_id, 0, 0)
        row_layout.addWidget(cours_id, 0, 1) 
        row_layout.addWidget(professeur_id, 0, 2) 
        row_layout.addWidget(annee_academique, 0, 3)

        row_layout.addWidget(classe, 1, 0)
        row_layout.addWidget(jours, 1, 1) 
        row_layout.addWidget(heure, 1, 2) 
        row_layout.addWidget(session, 1, 3)
        row_layout.addWidget(faculte_id, 2, 0)
         
        row_layout.addWidget(supprimer, 2, 3)

        self.ui.widget_8.setStyleSheet(
            """
            QComboBox, QLineEdit, QDateEdit { width: 200px; }
            #supprimer { color: red; }
            #chose_file { 
                border: 1px solid #b23cfd;
                color: #b23cfd;
                padding: 5px;
                border-radius: 5px;
            }
      
            #date_edit,#niveau_id,#line_edit1{
            min-width:200px
            }
            """
        )
   
        self.ui.widget_8.layout().addWidget(row_frame)

    

        # self.cours_row_count += 1
        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, self.cours_dictionary)) 

        # Ajouter un document au dictionnaire avec une clé unique
        self.donnee= {
        'cours_id' : cours_id,
        'professeur_id' : professeur_id,
        'faculte_id' : faculte_id,
        'annee_academique' : annee_academique,
        'jours' : jours,
        'heure' : heure,
        'session' : session,
        'class' : classe,
        'niveau_id' : niveau_id,
        }
 
# niveau_id
# 
        self.programme_dictionary.append(self.donnee) 
 

    def add_dynamic_row(self, target_widget, data_list, fields, dictionary):
        row_frame = QFrame()
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)

        niveau_id = QComboBox()
        for item in data_list:
            niveau_id.addItem(item['name'], item['id'])

        input_fields = {}
        for idx, field_name in enumerate(fields):
            field = QLineEdit()
            field.setPlaceholderText(field_name.replace("_", " ").capitalize())
            field.setObjectName(field_name)
            input_fields[field_name] = field
            row_layout.addWidget(field, 0, idx + 1)

        supprimer = QPushButton("Supprimer")
        supprimer.setFlat(True)
        supprimer.setObjectName("supprimer")
        row_layout.addWidget(niveau_id, 0, 0)
        row_layout.addWidget(supprimer, 0, len(fields) + 1)

        target_widget.layout().addWidget(row_frame)

        # Ajout au dictionnaire avec référence au row_frame
        row_data = {"row_frame": row_frame, "niveau_id": niveau_id, **input_fields}
        dictionary.append(row_data)

        # Connecter le bouton supprimer
        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, dictionary))

        """
        Ajoute dynamiquement une ligne de formulaire avec des champs personnalisables.
        
        :param target_widget: Le widget contenant les lignes (ex: `self.ui.widget_7`).
        :param data_list: La liste de données pour le QComboBox (ex: niveaux).
        :param fields: Liste des champs (ex: `["cours_nom", "note_de_passage", "coefficients"]`).
        :param dictionary: Le dictionnaire stockant les entrées.
        """
        row_frame = QFrame()
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)

        # Déclaration des widgets
        niveau_id = QComboBox()
        for item in data_list:
            niveau_id.addItem(item['name'], item['id'])

        # Création dynamique des champs
        input_fields = {}
        for idx, field_name in enumerate(fields):
            field = QLineEdit()
            field.setPlaceholderText(field_name.replace("_", " ").capitalize())
            field.setObjectName(field_name)
            input_fields[field_name] = field
            row_layout.addWidget(field, 0, idx + 1)

        # Bouton supprimer
        supprimer = QPushButton("Supprimer")
        supprimer.setFlat(True)
        supprimer.setObjectName("supprimer")
        row_layout.addWidget(niveau_id, 0, 0)
        row_layout.addWidget(supprimer, 0, len(fields) + 1)

        # Ajout de la ligne au widget cible
        target_widget.layout().addWidget(row_frame)

        # Suppression de la ligne
        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, dictionary))

        # Ajout au dictionnaire
        row_data = {"niveau_id": niveau_id, **input_fields}
        dictionary.append(row_data)

    # def add_cours_line(self):
    #     fields = ["cours_nom", "note_de_passage", "coefficients"]
    #     self.add_dynamic_row(self.ui.widget_7, self.niveau, fields, self.cours_dictionary)

    def add_cours_line(self): 
        
        row_frame = QFrame() 
        row_layout = QGridLayout()
        row_frame.setLayout(row_layout)

        niveau_id = QComboBox()
        cours_nom = QLineEdit() 
        note_de_passage = QLineEdit() 
        coefficients = QLineEdit() 
        supprimer = QPushButton("Supprimer")

        supprimer.setFlat(True)
        cours_nom.setPlaceholderText('Nom du cours') 
        note_de_passage.setPlaceholderText('Note de passage') 
        coefficients.setPlaceholderText('Coefficients') 

        supprimer.setObjectName("supprimer")  
        cours_nom.setObjectName("cours_nom")
        note_de_passage.setObjectName("note_de_passage")
        niveau_id.setObjectName("niveau_id")
        coefficients.setObjectName("coefficients")

        for niveau in self.niveau:
            niveau_id.addItem(niveau['name'], niveau['id']) 

        row_layout.setSpacing(15)
        row_layout.addWidget(niveau_id, 0, 0)
        row_layout.addWidget(cours_nom, 0, 1) 
        row_layout.addWidget(note_de_passage, 0, 2) 
        row_layout.addWidget(coefficients, 0, 3) 
        row_layout.addWidget(supprimer, 0, 4)

        self.ui.widget_7.layout().addWidget(row_frame)

        supprimer.clicked.connect(lambda: self.supprimer_ligne(row_frame, self.cours_dictionary)) 

        # Ajouter un document au dictionnaire avec une clé "frame"
        self.donnee = {
            "frame": row_frame,  # Stocker l'objet
            "niveau_id": niveau_id,
            "cours_nom": cours_nom,
            "note_de_passage": note_de_passage,
            "coefficients": coefficients
        }

        self.cours_dictionary.append(self.donnee)



    # def supprimer_ligne_cours(self, frame):
    #     """ Supprime une ligne en retirant le QFrame du layout """
    #     print('Suppression d\'une ligne')
    #     self.ui.widget_piece_inner.layout().removeWidget(frame)
    #     frame.deleteLater()

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



    def enregistrer_cours(self):
        dictionaryCourse = []
        for ligne in self.cours_dictionary:            
            ligne_donnees = {
                "cours_nom": ligne["cours_nom"].text(),
                "note_de_passage": ligne["note_de_passage"].text(),            
                "niveau_id": ligne["niveau_id"].currentData(),
                "coefficients":ligne["coefficients"].text() 
            }

            dictionaryCourse.append(ligne_donnees)
             # CoursesObject
        response = enregistrer_cours(CoursesObject=dictionaryCourse)
        print(response)

# ==========================================================================================
    def programme_index(self):
        self.set_table_refresh_data_programme()
        print(all_programme())
        self.ui.coursStaked.setCurrentWidget(self.ui.programme_staked_page)
        self.ui.stackedWidgetProgramme.setCurrentWidget(self.ui.index_programme)
        self.ui.titre_toggle.setText("Programme")

    def add_programme_page(self):
        self.ui.stackedWidgetProgramme.setCurrentWidget(self.ui.add_programme)

    def set_table_refresh_data_programme(self, page=1):
        header = ("Id", "Cours", "Nveau", "Professeur", "Classe", "Annee")
        self.all_headers_table_labels(
            self.ui.programme_table, header,  "#e2e8f0", 32, 200, 200, 200, 200,200)
        self.ui.programme_table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        
        table = all_programme(self.ui.search_programme.text(), page)
        self.current_page_programme = table["current_page"]
        self.total_pages_programme = table["total_pages"]

        # self.ui.prev_page_student.setEnabled(self.current_page_prof > 1)
        # self.ui.next_page_student.setEnabled(self.current_page_prof < self.total_pages_prof)

        # self.ui.prev_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border: 1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """)

        # self.ui.next_page_student.setStyleSheet("""
        #     QPushButton { color: #007bff; border:  1px solid #007bff; border-radius: 5px; padding: 5px 10px; }
        #     QPushButton:disabled { border: #cccccc; color: #666666; border: 1px solid #cccccc;padding: 5px 10px; }
        # """) 

        self.select_all_populate(table['data'], self.ui.programme_table, self.on_row_clicked_programme)

    def on_row_clicked_programme(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.ui.programme_table.item(row, 0)  # Colonne 0 = ID
        if id_item: 
            show_programme = programme_show(id_item.text())
            # self.add_cours(show_cours)
            self.add_programme_page()
       
            return id_item.text()


    def enregistrer_programme(self):
        pass

# ===========================================  __COURS__ =========================================

    def notes_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.notes_page)
        self.ui.titre_toggle.setText("Notes")

    def promus_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.promus_page)
        self.ui.titre_toggle.setText("Promus")

    def vente_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.vente_page)
        self.ui.titre_toggle.setText("Vente")

    def rapport_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.rapport_page)
        self.ui.titre_toggle.setText("Rapport")



# =======================================================SOU PAJ ELEV==================================

# ======================================  FONKCYON POU KOMBO BOX YO=================================
    def selection_changed_niveau(self, index):
        
        selected_id = self.ui.niveau_id.itemData(index)
        if selected_id is None:
            print("No data associated with the selected item.")
            return
        self.ui.classe_actuelle_id.clear()
        self.classes = class_and_other(selected_id)
        for classe in self.classes:
            self.ui.classe_actuelle_id.addItem(classe['nom_classe'], classe['id']) 
        # return selected_id
        self.niveau_selected = selected_id

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
    
    def selection_changed_niveau_for_combo(self, index,niveau_id, classe):
        self.selection_changed(niveau_id, classe, class_and_other)
        self.niveau_selected = self.ui.niveau_id.itemData(index)




    def selection_changed_annee_academique(self, index):
        """Affiche l'ID correspondant à l'élément sélectionné"""
        selected_id = self.ui.annee_academique_id.itemData(index)
        self.annee_selected = selected_id
        print(f"ID sélectionné : {selected_id}")

    def selection_changed_classe(self, index):
        """Affiche l'ID correspondant à l'élément sélectionné"""
        selected_id = self.ui.classe_actuelle_id.itemData(index)
        self.class_selected = selected_id 

    def selection_changed_role(self, index):
        """Affiche l'ID correspondant à l'élément sélectionné"""
        selected_id = self.ui.admin_role.itemData(index)
        self.role_selected = selected_id 

# ===========================================================================================================

    def all_headers_table_labels(self, table_name, header: tuple, color, size=30, col1=100, col2=100, col3=100, col4=100, col5=100, col6=100, col7=100, col8=100):
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

        # Appliquer du padding et un fond coloré à l'en-tête
        table_name.horizontalHeader().setStyleSheet(
            """
            QHeaderView::section {
                background-color: #4b5564;  /* Vert */
                color: white;
                font-weight: bold;
                padding: 1px;  /* Padding */
                /* border: 1px solid #ddd;*/
            }
            """
        )
 
        table_name.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
 
        table_name.horizontalHeader().setFixedHeight(size)
 
        table_name.verticalHeader().setDefaultSectionSize(size)


        table_name.setStyleSheet(
            f"alternate-background-color: {color}; background-color: #fff;"
        )


    def select_all_populate(self, table, table_ui, function_click):
        table_ui.setRowCount(len(table))
        for(index_row, row) in enumerate(table):
            
            for(index_cell, cell) in enumerate(row):
                # print(row[cell])
                items = QTableWidgetItem(str(row[cell]))
                items.setTextAlignment(Qt.AlignCenter)
                table_ui.setItem(
                    index_row, index_cell, items
                )
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

    # from PyQt5.QtWidgets import QLineEdit, QComboBox, QTextEdit, QSpinBox, QDateEdit
    def clear_fields(self, *fields):
    
        for field in fields:
            if isinstance(field, QLineEdit):
                field.setText('')  # Efface le texte
            # elif isinstance(field, QTextEdit):
                # field.clear()  # Efface le contenu d'un QTextEdit
            elif isinstance(field, QComboBox):
                field.setCurrentIndex(0)  # Remet à l'index par défaut
            # elif isinstance(field, QSpinBox):
            #     field.setValue(field.minimum())  # Réinitialise à la valeur minimale
            elif isinstance(field, QDateEdit):
                field.setDate(field.minimumDate())  # Remet à la date minimale



     

   
    

        

        


   


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


    def search_student2(self):
        """Affiche une boîte de dialogue pour rechercher un étudiant et empêche l'interaction avec la fenêtre principale."""
        self.dialog = QDialog(self)
         
        self.dialog.setWindowFlags(self.dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
        
        self.dialog.setModal(True)  
        self.dialog.setFixedSize(600, 400)
 
        main_layout = QVBoxLayout(self.dialog)
 
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.dialog.close)  
    
        search_frame = QFrame()
        search_frame.setFixedHeight(50)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
 
        self.student_live_seach_input = QLineEdit()
        self.student_live_seach_input.setPlaceholderText("Rechercher un étudiant...")
        self.student_live_seach_input.setObjectName("input_student")
        self.dialog.setObjectName("dialog")
        # self.student_live_seach_input.setFixedWidth(300)
        self.student_live_seach_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dialog.setStyleSheet(
            """
            #dialog{border-radius:10px}
            #input_student { width: 400px; min-height: 32px; max-height: 32px; }
            """
        )
        search_layout.addWidget(self.student_live_seach_input, alignment=Qt.AlignmentFlag.AlignHCenter)
        if self.student_live_seach_input != '':
            self.student_live_seach_input.textChanged.connect(self.set_table_refresh_data_for_live_search)


        show_frame = QFrame()
        show_layout = QVBoxLayout(show_frame)
        show_layout.setContentsMargins(0, 0, 0, 0)
        data = student_live(self.student_live_seach_input.text())
        print(data, self.student_live_seach_input.text())
        if data is not None and 'data' in data:
            if data['data'] is not None:
                table = QTableWidget() 
                table.setHorizontalHeaderLabels(["Nom", "Prénom", "Classe"])
                table.horizontalHeader().setStretchLastSection(True)
                show_layout.addWidget(table)
        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(search_frame)
        main_layout.addWidget(show_frame, 1)   

        self.dialog.exec()

    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



    def search_student(self):
        """Affiche une boîte de dialogue pour rechercher un étudiant."""
        self.dialog = QDialog(self)
        self.dialog.setWindowFlags(self.dialog.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.dialog.setModal(True)  
        self.dialog.setFixedSize(600, 400)

        main_layout = QVBoxLayout(self.dialog)

        # Bouton de fermeture
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.dialog.close)  

        # Frame pour la recherche
        search_frame = QFrame()
        search_frame.setFixedHeight(50)
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.student_live_seach_input = QLineEdit()
        self.student_live_seach_input.setPlaceholderText("Rechercher un étudiant...")
        self.student_live_seach_input.setObjectName("input_student")
        self.student_live_seach_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connexion pour la recherche en temps réel
        self.student_live_seach_input.textChanged.connect(self.set_table_refresh_data_for_live_search)

        search_layout.addWidget(self.student_live_seach_input, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Frame pour les résultats
        show_frame = QFrame()
        show_layout = QVBoxLayout(show_frame)
        show_layout.setContentsMargins(0, 0, 0, 0)

        # Création initiale du tableau
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Id","Identifiant", "nom", "Prénom"])
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False) 
        self.table.setColumnHidden(0, True)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 220)
        self.table.setColumnWidth(3, 220)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
 
        # self.table.horizontalHeader().setFixedHeight(QSize)
 
        # self.table.verticalHeader().setDefaultSectionSize(QSize)


        self.table.setStyleSheet(
            f"alternate-background-color: #f1f1f1; background-color: #fff;"
        )
        show_layout.addWidget(self.table)

        main_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(search_frame)
        main_layout.addWidget(show_frame, 1)   

        self.dialog.setStyleSheet(
            """
            #dialog { border-radius: 10px; background-color: white; }
            #input_student { width: 400px; min-height: 32px; max-height: 32px; }
            """
        )

        self.dialog.exec()

    def set_table_refresh_data_for_live_search(self):
        """Mise à jour dynamique du tableau avec les résultats de la recherche."""
        data = student_live(self.student_live_seach_input.text())

        if data and 'data' in data:
            self.table.setRowCount(len(data['data'])) 
            for row_idx, row_data in enumerate(data['data']):
                for col_idx, value in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(row_data[value]))
            self.table.cellClicked.connect(self.on_row_clicked_live_search)
        else:
            self.table.setRowCount(0)  # Vider la table si aucune donnée



    # def on_row_clicked_live_search(self, row, column):
    #     """Récupère l'ID de la ligne cliquée"""
    #     id_item = self.table.item(row, 0)
    #     if id_item: 
    #         show_student_for_payment = get_student_with_params_payment(id_item.text())
    #         first_info = show_student_for_payment[-1]
    #         self.ui.identifiant.setText(first_info['identifiant'])
    #         self.ui.identifiant.setStyleSheet("""color:#555""")
    #         self.ui.fname.setStyleSheet("""color:#555""")
    #         self.ui.lname.setStyleSheet("""color:#555""")
    #         self.ui.classe_actuelle.setStyleSheet("""color:#555""")
    #         self.ui.fname.setText(first_info['nom'])
    #         self.ui.lname.setText(first_info['prenom'])
    #         self.ui.classe_actuelle.setText(first_info['nom_classe'])
    #         profile = os.path.join(self.project_dir, 'assets', 'icons', 'profile.png')#label.setPixmap(pixmap)
    #         pixmap = QPixmap(profile)
    #         # self.add_scroll_bar(show_student_for_payment)
            
    #         if not hasattr(self, "my_widget"):
    #             self.my_widget = MyWidget(self.ui.frame_122)
    #             self.ui.frame_122.layout().addWidget(self.my_widget)  

    #         # Met à jour le contenu avec les nouvelles données
    #         self.my_widget.add_scroll_bar(show_student_for_payment)

    #         self.ui.imag_ilustrative.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
    #         self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement)
    #         self.dialog.close()
       
    #         # return id_item.text()


# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QScrollArea, QLabel, QCheckBox)
# from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
# from PyQt5.QtGui import QPixmap, QTransform


    # def add_scroll_bar(self, data_student):
    #     scroll_widget = QWidget()
    #     layout = QVBoxLayout(scroll_widget)
        # layout.setAlignment(Qt.AlignLeft)
        # layout.setAlignment(Qt.AlignTop)
    #     layout.setSpacing(10)

    #     for data in data_student:
    #         button = QPushButton(f"{data['annee_academique']}")
    #         button.setCheckable(True)
    #         button.setAutoExclusive(True)
    #         button.setObjectName(f"{data['annee_academique']}")
            
    #         self.content_layout= QVBoxLayout()
    #         button.clicked.connect(lambda checked, d=data: self.show_info_to_pay(d))

    #         button.setStyleSheet("""
    #             QPushButton {
    #                 padding: 5px;
    #                 text-align: center;
    #                 max-width: 150px;
    #                 border-radius: 5px;
    #                 font-size: 16px;
    #                 border: 1px solid #ccc;
    #                 background: white;
    #                 color: black;
    #             }
    #             QPushButton:hover {
    #                 background: #ccc;
    #                 color: white;
    #             }
    #         """)

    #         layout.addWidget(button)

    #     scroll_widget.setLayout(layout)
    #     self.ui.scroll_pay.setWidget(scroll_widget)  
    #     self.ui.scroll_pay.setWidgetResizable(True) 

    # def show_info_to_pay(self, data,animated=True):
    #     layout = QVBoxLayout()
    #     self.animation = QPropertyAnimation(self.layout, b"maximumHeight")
    #     self.animation.setDuration(300)
    #     self.animation.setEasingCurve(QEasingCurve.InOutQuad)
    #     layout.addWidget(QLabel("Hello first"))

    #     self.is_expanded = not self.is_expanded
        
    #     if self.is_expanded:
    #         self.animation.setStartValue(0)
    #         self.animation.setEndValue(self.layout.sizeHint().height())
    #         self.arrow.setPixmap(self.arrow.pixmap().transformed(QTransform().rotate(90)))
    #     else:
    #         self.animation.setStartValue(self.layout.height())
    #         self.animation.setEndValue(0)
    #         self.arrow.setPixmap(self.arrow.pixmap().transformed(QTransform().rotate(0)))
        
    #     if animated:
    #         self.animation.start()
    #     else:
    #         self.layout.setMaximumHeight(self.layout.sizeHint().height() if self.is_expanded else 0)
        
    #     self.content_layout.addLayout(layout)
    #     self.layout.setFixedHeight(self.layout.sizeHint().height())


# from PyQt5.QtWidgets import (
#     QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QFrame, QCheckBox
# )
# from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
#     def on_row_clicked_live_search(self, row, column):
#         """Récupère l'ID de la ligne cliquée"""
#         id_item = self.table.item(row, 0)
#         if id_item: 
#             show_student_for_payment = get_student_with_params_payment(id_item.text())
#             first_info = show_student_for_payment[-1]
#             self.ui.identifiant.setText(first_info['identifiant'])
#             self.ui.identifiant.setStyleSheet("""color:#555""")
#             self.ui.fname.setStyleSheet("""color:#555""")
#             self.ui.lname.setStyleSheet("""color:#555""")
#             self.ui.classe_actuelle.setStyleSheet("""color:#555""")
#             self.ui.fname.setText(first_info['nom'])
#             self.ui.lname.setText(first_info['prenom'])
#             self.ui.classe_actuelle.setText(first_info['nom_classe'])
#             profile = os.path.join(self.project_dir, 'assets', 'icons', 'profile.png')#label.setPixmap(pixmap)
#             pixmap = QPixmap(profile)
#             # self.add_scroll_bar(show_student_for_payment)
#             data_student = [
#             {"annee_academique": "2021-2022"},
#             {"annee_academique": "2022-2023"},
#             {"annee_academique": "2023-2024"},
#             ]

#             window = MyWidget(self.ui.frame_122)
#             window.add_scroll_bar(data_student)
#             self.ui.imag_ilustrative.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
#             self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement)
#             self.dialog.close()


# class MyWidget(QWidget):
#     def __init__(self, frame):
#         super().__init__(frame)
#         self.ui = QScrollArea()  # Assuming this is a QScrollArea
#         self.ui.setWidgetResizable(True)
#         self.setup_ui()
#         self.frame = frame

#     def setup_ui(self):
#         self.main_layout = QVBoxLayout(self.frame)
#         self.main_layout.addWidget(self.ui)

#     def add_scroll_bar(self, data_student):
#         scroll_widget = QWidget()
#         layout = QVBoxLayout(scroll_widget)
#         layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#         layout.setSpacing(10)

#         for data in data_student:
#             button = QPushButton(f"{data['annee_academique']}")
#             button.setCheckable(True)
#             button.setAutoExclusive(True)
#             button.setObjectName(f"{data['annee_academique']}")

#             # Connect the button click to show_info_to_pay
#             button.clicked.connect(lambda checked, d=data: self.show_info_to_pay(d))

#             button.setStyleSheet("""
#                 QPushButton { padding: 5px;
#                    
#                     padding: 5px;
#                     text-align: center;
#                     max-width: 150px;
#                     border-radius: 5px;
#                     font-size: 16px;
#                     border: 1px solid #ccc;
#                     background: white;
#                     color: black;
#                 }
#                 QPushButton:hover {
#                     background: #ccc;
#                     color: white;
#                 }
#             """)

#             layout.addWidget(button)

#         scroll_widget.setLayout(layout)
#         self.ui.setWidget(scroll_widget)

#     def show_info_to_pay(self, data):
#         # Create a new frame for the content
#         content_frame = QFrame()
#         content_frame.setStyleSheet("background-color: white; border: 1px solid #ddd;")
#         content_layout = QVBoxLayout(content_frame)
#         content_layout.setContentsMargins(10, 10, 10, 10)

#         # Add sample content
#         content_layout.addWidget(QLabel(f"Information for {data['annee_academique']}"))
#         content_layout.addWidget(QCheckBox("Option 1"))
#         content_layout.addWidget(QCheckBox("Option 2"))

#         # Add the content frame to the main layout
#         self.main_layout.addWidget(content_frame)

#         # Set up animation for the content frame
#         self.animate_content(content_frame)

#     def animate_content(self, widget):
#         animation = QPropertyAnimation(widget, b"maximumHeight")
#         animation.setDuration(300)
#         animation.setEasingCurve(QEasingCurve.InOutQuad)

#         # Collapse if expanded, expand if collapsed
#         if widget.maximumHeight() == 0:
#             widget.setMaximumHeight(16777215)  # Reset to default maximum height
#             animation.setStartValue(0)
#             animation.setEndValue(widget.sizeHint().height())
#         else:
#             animation.setStartValue(widget.height())
#             animation.setEndValue(0)

#         animation.start()
    def on_row_clicked_live_search(self, row, column):
        """Récupère l'ID de la ligne cliquée"""
        id_item = self.table.item(row, 0)
        if id_item: 
            show_student_for_payment = get_student_with_params_payment(id_item.text())
            first_info = show_student_for_payment[-1]
            self.ui.identifiant.setText(first_info['identifiant'])
            self.ui.identifiant.setStyleSheet("""color:#555""")
            self.ui.fname.setStyleSheet("""color:#555""")
            self.ui.lname.setStyleSheet("""color:#555""")
            self.ui.classe_actuelle.setStyleSheet("""color:#555""")
            self.ui.fname.setText(first_info['nom'])
            self.ui.lname.setText(first_info['prenom'])
            self.ui.classe_actuelle.setText(first_info['nom_classe'])
            profile = os.path.join(self.project_dir, 'assets', 'icons', 'profile.png')#label.setPixmap(pixmap)
            pixmap = QPixmap(profile)
            # self.add_scroll_bar(show_student_for_payment)
            
            if not hasattr(self, "my_widget"):
                self.my_widget = MyWidget(self.ui.frame_122)
                self.ui.frame_122.layout().addWidget(self.my_widget)  

            # Met à jour le contenu avec les nouvelles données
            self.my_widget.add_scroll_bar(show_student_for_payment)

            self.ui.imag_ilustrative.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            self.ui.stackedPaiement.setCurrentWidget(self.ui.add_paiement)
            self.dialog.close()
       
            # return id_item.text()

class MyWidget(QWidget):
    def __init__(self, frame):
        super().__init__(frame)
        self.frame = frame
        self.ui = QScrollArea()  
        self.ui.setWidgetResizable(True)
        self.setup_ui()
        self.frames = {}  # Dictionnaire pour stocker les QFrames par index

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)  # Utilise `self` au lieu de `self.frame`
        self.main_layout.addWidget(self.ui)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    def add_scroll_bar(self, data_student):
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.setSpacing(15)

        for index, data in enumerate(data_student):
            button = QPushButton(f"{data['annee_academique']}")
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setObjectName(f"{data['annee_academique']}")
            
            # Créer dynamiquement un QFrame pour chaque bouton
            frame = QFrame()
            frame.setObjectName(f"frame_{index}")
            
            # Enregistrer le frame dans un dictionnaire avec l'index
            self.frames[index] = frame

            button.clicked.connect(lambda checked, d=data, index=index: self.show_info_to_pay(d, index))

            button.setStyleSheet("""
                QPushButton {
                    padding: 7px;
                    text-align: center;
                    max-width: 150px;
                    border-radius: 5px;
                    font-size: 16px;
                    border: 1px solid #ccc;
                    background: white;
                    color: black;
                }
                QPushButton:hover {
                    background: #ccc;
                    color: white;
                }
            """)

            layout.addWidget(button)

        scroll_widget.setLayout(layout)
        self.ui.setWidget(scroll_widget)

    def show_info_to_pay(self, data, index):
      
        frame = self.frames.get(index)

        if frame:
            content_layout = QVBoxLayout(frame)
            content_layout.addWidget(QLabel(f"Information for {data['annee_academique']}"))
            content_layout.addWidget(QCheckBox("Option 1"))
            content_layout.addWidget(QCheckBox("Option 2"))
            
            # Définir le layout de frame
            frame.setLayout(content_layout)

            self.main_layout.addWidget(frame)


            frame.setMaximumHeight(400)  # Ajuste la hauteur à une taille suffisante
            self.animate_content(frame)
            
            self.main_layout.update() 
            frame.update() 
            


    def animate_content(self, widget):
        # Animation pour afficher un QFrame
        animation = QPropertyAnimation(widget, b"maximumHeight")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        widget.setMaximumHeight(400)  
        animation.setStartValue(400)
        animation.setEndValue(100) 

        animation.start()













        
# import sys
# from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
#                               QPushButton, QFrame, QFileDialog, QLineEdit)
# from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QImage, QPen
# from PySide6.QtCore import Qt, QSize, Signal
# import cv2
# from pyzbar.pyzbar import decode
# import qrcode
# from datetime import datetime, timedelta

# class BadgeCreator(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Générateur de Badge")
#         self.setFixedSize(1000, 700)
        
#         # Variables
#         self.student_photo = None
#         self.institution_logo = None
#         self.fetch_data_ = Check_data()
#         self.school_name = 'My School'
#         self.school_adresse = 'Puits Blain'
#         self.school_phone = "+509 4343 34 56"
#         # self.school_name = My School
#         # if self.fetch_data_:
#         config = self.fetch_data_.config_donnees()
#         if config and 'data' in config and config['data']:
#             data = config['data'][0]
#             ligne1 = data['ligne1']
#             self.school_name = data['nom']
#             self.school_adresse = data['adresse']
#             self.school_phone = f"+509 {ligne1}"

        
#         self.init_ui()
#         self.setup_connections()
        
#     def init_ui(self):
#         # Layout principal
#         main_layout = QVBoxLayout()
        
#         # 1. Zone d'institution (première rangée)
#         self.institution_label = QLabel(f"{self.school_name}")
#         self.institution_label.setAlignment(Qt.AlignCenter)
#         self.institution_label.setStyleSheet("""
#             QLabel {
#                 font-size: 28px;
#                 font-weight: bold;
#                 color: #003366;
#                 margin-bottom: 20px;
#             }
#         """)
        
#         # 2. Deuxième rangée (photo + nom)
#         second_row = QHBoxLayout()
        
#         # Frame pour la photo
#         self.photo_frame = QFrame()
#         self.photo_frame.setFrameShape(QFrame.Box)
#         self.photo_frame.setLineWidth(2)
#         self.photo_frame.setStyleSheet("border-color: #aaa;border-radius:7px")
#         self.photo_frame.setFixedSize(200, 250)
        
#         self.photo_label = QLabel()
#         self.photo_label.setAlignment(Qt.AlignCenter)
#         self.photo_label.setStyleSheet("background-color: #f0f0f0;")
        
#         frame_layout = QVBoxLayout()
#         frame_layout.addWidget(self.photo_label)
#         self.photo_frame.setLayout(frame_layout)
        
#         # Zone pour le nom complet
#         self.name_label = QLabel("NOM PRÉNOM")
#         self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
#         self.name_label.setStyleSheet("""
#             QLabel {
#                 font-size: 24px;
#                 font-weight: bold;
#                 margin-left: 30px;
#             }
#         """)
        
#         second_row.addWidget(self.photo_frame)
#         second_row.addWidget(self.name_label)
#         # second_row.setStretch(1, 2)
        
#         # 3. Troisième rangée (ID, expiration, signature)
#         third_row = QHBoxLayout()
        
#         self.id_label = QLabel("ID: ETU00000")
#         self.expiry_label = QLabel(f"Expire: {(datetime.now() + timedelta(days=365)).strftime('%d/%m/%Y')}")
#         self.signature_label = QLabel("Signature")
#         self.signature_label.setFrameShape(QFrame.Box)
#         self.signature_label.setFixedSize(150, 50)
        
#         third_row.addWidget(self.id_label)
#         third_row.addWidget(self.expiry_label)
#         third_row.addWidget(self.signature_label)
        
#         # 4. Quatrième rangée (adresse + QR code)
#         fourth_row = QHBoxLayout()
        
#         self.address_label = QLabel(f"{self.school_adresse}")
#         self.address_label.setAlignment(Qt.AlignLeft)
        
#         self.qrcode_label = QLabel()
#         self.qrcode_label.setFixedSize(100, 100)
#         self.qrcode_label.setFrameShape(QFrame.Box)
        
#         fourth_row.addWidget(self.address_label)
#         fourth_row.addStretch()
#         fourth_row.addWidget(self.qrcode_label)
        
#         # Boutons de contrôle
#         control_layout = QHBoxLayout()
#         self.generate_btn = QPushButton("Générer le Badge")
#         self.capture_btn = QPushButton("Prendre Photo")
#         self.load_btn = QPushButton("Charger Photo")
        
#         control_layout.addWidget(self.generate_btn)
#         control_layout.addWidget(self.capture_btn)
#         control_layout.addWidget(self.load_btn)
        
#         # Assemblage final
#         main_layout.addWidget(self.institution_label)
#         main_layout.addLayout(second_row)
#         main_layout.addLayout(third_row)
#         main_layout.addLayout(fourth_row)
#         main_layout.addStretch()
#         main_layout.addLayout(control_layout)
        
#         self.setLayout(main_layout)
        
#         # Initialisation webcam
#         self.cap = cv2.VideoCapture(0)
#         self.camera_active = False
#         self.timer = QTimer()
        
#     def setup_connections(self):
#         self.generate_btn.clicked.connect(self.generate_badge)
#         self.capture_btn.clicked.connect(self.toggle_camera)
#         self.load_btn.clicked.connect(self.load_photo)
#         self.timer.timeout.connect(self.update_camera_preview)
        
#     def toggle_camera(self):
#         if not self.camera_active:
#             self.camera_active = True
#             self.timer.start(30)
#             self.capture_btn.setText("Capturer")
#         else:
#             self.capture_photo()
    
#     def update_camera_preview(self):
#         ret, frame = self.cap.read()
#         if ret:
#             rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             h, w, ch = rgb_image.shape
#             bytes_per_line = ch * w
#             qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#             self.photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
#                 200, 250, Qt.KeepAspectRatio))
    
#     def capture_photo(self):
#         ret, frame = self.cap.read()
#         if ret:
#             self.student_photo = frame
#             self.update_photo_display()
#             self.camera_active = False
#             self.timer.stop()
#             self.capture_btn.setText("Prendre Photo")
    
#     def load_photo(self):
#         file_path, _ = QFileDialog.getOpenFileName(self, "Charger une photo", "", "Images (*.png *.jpg *.jpeg)")
#         if file_path:
#             self.student_photo = cv2.imread(file_path)
#             self.update_photo_display()
    
#     def update_photo_display(self):
#         if self.student_photo is not None:
#             rgb_image = cv2.cvtColor(self.student_photo, cv2.COLOR_BGR2RGB)
#             h, w, ch = rgb_image.shape
#             bytes_per_line = ch * w
#             qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#             self.photo_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
#                 200, 250, Qt.KeepAspectRatio))
    
#     def generate_qrcode(self, data):
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=4,
#             border=1,
#         )
#         qr.add_data(data)
#         qr.make(fit=True)
#         img = qr.make_image(fill_color="black", back_color="white")
        
#         # Convertir en QPixmap
#         img = img.convert("RGB")
#         qimg = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888)
#         return QPixmap.fromImage(qimg)
    
#     def generate_badge(self):
        # Création du badge final
        badge = QPixmap(QSize(1013, 638))  # Taille en pixels (8.5x5.1cm @300DPI)
        badge.fill(Qt.white)
        
        painter = QPainter(badge)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 1. Fond avec bordure
        # painter.setPen(QPen(QColor(0, 51, 102), 4))
        # painter.setBrush(QColor(240, 248, 255))  # Bleu très clair
        painter.drawRoundedRect(0, 0, 1013, 638,0,0)
        
        # 2. En-tête institution
        painter.setFont(QFont("Arial", 28, QFont.Bold))
        painter.setPen(QColor(0, 51, 102))
        painter.drawText(0, 40, 1013, 50, Qt.AlignCenter, f"{self.school_name}")
        

        frame_rect = QRect(70, 150, 200, 200)

# 1. Dessiner le cadre
        painter.setPen(QPen(Qt.black, 2))
        painter.drawRect(frame_rect)

        # 2. Remplir avec la photo (sans déformation)
        if self.student_photo is not None:
            photo_pixmap = self.photo_label.pixmap()
            filled = photo_pixmap.scaled(
                frame_rect.size().expandedTo(photo_pixmap.size()),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            painter.drawPixmap(frame_rect, filled)
        
        # 4. Informations étudiant
        painter.setFont(QFont("Arial", 24, QFont.Bold))
        # painter.drawText(300, 270, "DUPONT Jean")  # À remplacer par les données réelles
        painter.drawText(100, 150, 1013, 200, Qt.AlignCenter, "DUPONT Jean")
        
        # 5. Détails (ID, expiration)
        painter.setFont(QFont("Arial", 17))
        painter.drawText(60, 435, "ID No")
        painter.drawText(60, 465, " ETU2023001")

        painter.drawText(400, 435, "Date d'Exp.")
        painter.drawText(400, 465, f" {(datetime.now() + timedelta(days=365)).strftime('%d/%m/%Y')}")
        
        # 6. Signature
        painter.setPen(QPen(Qt.black, 1))
        # painter.drawRect(700, 250, 150, 50)
        painter.drawText(800, 435, "Signature")
        
        # 7. Adresse + QR Code
        painter.setFont(QFont("Arial", 16))
        painter.drawText(360, 570, f"{self.school_adresse}")
        painter.drawText(360, 600, f"{self.school_phone}")
        
        qr_pixmap = self.generate_qrcode("ETU2023001")
        painter.drawPixmap(850, 500, qr_pixmap)
        
        painter.end()
        
        # Sauvegarde du badge
        file_path, _ = QFileDialog.getSaveFileName(self, "Enregistrer le badge", "", "PNG (*.png)")
        if file_path:
            badge.save(file_path)
            QMessageBox.information(self, "Succès", "Badge généré avec succès !")

