# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_school1.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QAbstractSpinBox, QApplication,
    QCheckBox, QComboBox, QDateEdit, QDateTimeEdit,
    QFrame, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1163, 640)
        MainWindow.setMinimumSize(QSize(1163, 640))
        MainWindow.setStyleSheet(u"/*QMainWindow,#centralwidget{background: transparent}\n"
"*, #shadow_windowPage1{background-color: #fefefe}*/\n"
"\n"
"QMainWindow,#centralwidget{background-color: #fefefe}")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(0, 640))
        font = QFont()
        font.setFamilies([u"Inter"])
        font.setPointSize(13)
        font.setBold(True)
        self.centralwidget.setFont(font)
        self.centralwidget.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.centralwidget.setStyleSheet(u" \n"
"*, #shadow_windowPage1{background-color: #fefefe}\n"
"#btn_about{background: transparent}\n"
"\n"
"QWidget {\n"
"    font-family: \"Inter\", \"Segoe UI\", sans-serif;\n"
"    font-size: 13pt;\n"
"    color: #334155; /* Gris ardoise fonc\u00e9 */\n"
"    background-color: #f8fafc; /* Fond tr\u00e8s clair */\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #e2e8f0;\n"
"}\n"
"\n"
"QPushButton {\n"
"    /* ... ton code pr\u00e9c\u00e9dent ... */\n"
"    outline: none; /* Supprime le rectangle de focus par d\u00e9faut */\n"
"}\n"
"\n"
" #frame_136{background-color: #e1e1e1;}\n"
"\n"
"#live_log{\n"
"    color: #28b446;\n"
"    border: 1px solid #000;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"#widget_20,#tab_loans_form{ background-color: #fff; border-radius: 10px}\n"
"#live_log:hover{\n"
"   background-color: #000; \n"
"}\n"
"#generate_btn{color:#f93154;}\n"
"#capture_btn{color: #fbbb00;}\n"
"#load_btn{color: #4b8df0;}\n"
"\n"
"#log_grafic{\n"
"    color: #28b446;\n"
"    border: "
                        "1px solid #fff;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#log_grafic:hover{\n"
"   background-color: #fff; \n"
"}\n"
"\n"
"#frame_385{\n"
"    color: #28b446; \n"
"    padding: 5px;\n"
"    border-radius: 5px;\n"
"background-color: #000; \n"
"}\n"
"\n"
"QCalendarWidget QToolButton {\n"
"/*height: 60px;\n"
"width: 150px;*/\n"
"color: white;\n"
"font-size: 15px;\n"
"icon-size: 36px, 36px;\n"
"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 #cccccc, stop: 1 #333333);\n"
"}\n"
"QCalendarWidget QMenu {\n"
"/*width: 150px;\n"
"left: 20px;*/\n"
"color: white;\n"
"font-size: 14px;\n"
"background-color: rgb(100, 100, 100);\n"
"}\n"
"QCalendarWidget QSpinBox {\n"
"/*width: 150px;\n"
"font-size:24px;*/\n"
"color: white;\n"
"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 #cccccc, stop: 1 #333333);\n"
"selection-background-color: rgb(136, 136, 136);\n"
"selection-color: rgb(255, 255, 255);\n"
"}\n"
"QCalendarWidget QSpinBox::up-button { subcontrol-origin: border; "
                        "subcontrol-position: top right; width:30px; }\n"
"QCalendarWidget QSpinBox::down-button {subcontrol-origin: border; subcontrol-position: bottom right; width:30px;}\n"
"QCalendarWidget QSpinBox::up-arrow { width:56px; height:20px; }\n"
"QCalendarWidget QSpinBox::down-arrow { width:56px; height:20px; }\n"
"\n"
"/* header row */\n"
"QCalendarWidget QWidget { alternate-background-color: rgb(128, 128, 128); }\n"
"\n"
"/* normal days */\n"
"QCalendarWidget QAbstractItemView:enabled\n"
"{\n"
"font-size:14px;\n"
"color: rgb(180, 180, 180);\n"
"background-color: black;\n"
"selection-background-color: rgb(64, 64, 64);\n"
"selection-color: rgb(0, 255, 0);\n"
"}\n"
"\n"
"/* days in other months */\n"
"/* navigation bar */\n"
"QCalendarWidget QWidget#qt_calendar_navigationbar\n"
"{\n"
"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop: 0 #cccccc, stop: 1 #333333);\n"
"}\n"
"\n"
"QCalendarWidget QAbstractItemView:disabled\n"
"{\n"
"color: rgb(64, 64, 64);\n"
"}\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
""
                        "\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"\n"
"QWidget,QFrame, #frame,frame{\n"
"background: transparent;\n"
"}\n"
"QWidget,QFrame, #frame,frame{\n"
"border: transparent;\n"
"border: none;\n"
"}\n"
"\n"
"#frame_236,#frame_237,#frame_235{border:1px solid #ccc;border-radius:7px}\n"
"\n"
"#frame_172{border-bottom:1px solid #ffa900; border-top:1px solid #ffa900}\n"
"\n"
"#frame_173{border-bottom:1px solid #228BE6; border-top:1px solid #228BE6}\n"
"\n"
"#frame_165{border-bottom:1px solid #40C057; border-top:1px solid #40C057}\n"
"\n"
"#frame_170{border-bottom:1px solid #b23cfd; border-top:1px solid #b23cfd}\n"
"\n"
"#main{ border-top:1px solid #ccc; background-color: #fdfdfd;}\n"
"\n"
"#label_commande_number{color:red;}\n"
"#frame_276{background-color: #fff;}\n"
"\n"
"#frame_108{border:1px solid #777; border-radius:7px}\n"
"/*#image_path{border:2px solid #999; border-radius:8px;x}\n"
"/*#label_commande_number{width:16px;height:6px;background-color:red;color:white;border-radius:3px}*/\n"
"\n"
"#label_71,#lab"
                        "el_70,#label_69,#label_4,#label_15,#label_67,#label_13{color:#122a55; font-size:17pt}\n"
"\n"
"#btn_param_paiement,#btn_param_exam,#btn_frais,#btn_classe,#btn_annee,#recherche_user_role,#recherche_user_permission,#btn_permission_page,#btn_role_page,#btn_frais_divers,#btn_param_faculte{color:#374151}\n"
"\n"
"#btn_param_paiement:hover,#btn_param_exam:hover,#btn_frais:hover,#btn_classe:hover,#btn_annee:hover,#recherche_user_role:hover,#recherche_user_permission:hover,#btn_permission_page:hover,#btn_role_page:hover,#btn_frais_divers:hover,#btn_param_faculte:hover{color:#228BE6}\n"
"#intra_button:checked, #finale_button:checked{color:#228BE6;font-size:13p}\n"
"#btn_param_paiement:checked,#btn_param_exam:checked,#btn_frais:checked,#btn_classe:checked,#btn_annee:checked,#btn_permission_page:checked,#btn_role_page:checked, #btn_frais_divers:checked,#btn_param_faculte:checked{color:#228BE6;font-size:13pt}\n"
"\n"
"\n"
"#label_75{\n"
"font-size:14pt;\n"
"color:#eb983f\n"
"}\n"
"#user_email{color:#228BE6;font-size:14pt;"
                        "}\n"
"\n"
"#permission_page,#role_page{color:#777}\n"
"#permission_page:hover,#role_page:hover{color:#b23cfd}\n"
"#permission_page:checked,#role_page:checked{color:#b23cfd}\n"
"\n"
"QLabel{\n"
"font-size:14pt;\n"
"font-family: \"Inter\";\n"
"color:#4b5563\n"
"}\n"
"QScrollArea{border:none}\n"
" \n"
"#show_frame_ip{color:#4b5563}\n"
"#show_frame_ip:hover{color:#228BE6}\n"
"#show_frame_ip:checked{color:red}\n"
"\n"
"#personnel_info,\n"
"#widget_4,\n"
"#widget_11,\n"
"#widget_piece,\n"
"#widget_global,\n"
"#widget_financier,\n"
"#widget_administratif,\n"
"#widget_faculte,#widget_classe,#widget_frais,#widget_param_exam,#widget_annee_academique,#widget_parametre_paiement,#param_page\n"
"{background-color:#fff; border-radius:10px}\n"
"\n"
"QFrame, #frame{\n"
"background: transparent;\n"
"border: transparent;\n"
"}\n"
"\n"
"#main_with_shadow {\n"
"    background-color: #fefefe;\n"
"  border-radius: 10px\n"
"}\n"
"\n"
"\n"
"#logo,\n"
"#logo_2,\n"
"#image_3 {\n"
"    border-radius: 50px\n"
"}\n"
"\n"
"#header,\n"
"#hea"
                        "der_connexion,\n"
"#header_welcome ,\n"
"#header_connexion_error{\n"
"    border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"border-bottom:1px solid #c1c1c1;\n"
"background-color:#fff\n"
"}\n"
"\n"
"#leftmenu {\n"
"    border-top-left-radius: 7px;\n"
"    border-bottom-left-radius: 7px;\n"
"}\n"
"\n"
"\n"
"#prog_cours {\n"
"    border-bottom-right-radius: 7px;\n"
"    border-bottom-left-radius: 7px\n"
"}\n"
"\n"
"#leftmenu,\n"
"#left_frame {\n"
"    background-color: #374151;\n"
"/*background-color:#333;*/\n"
"/*  background-color: #228BE6; 00a7ee*/\n"
"}\n"
"\n"
"#footer {\n"
"    background: transparent;  \n"
" border-radius: 10px   \n"
"\n"
"}\n"
"\n"
"\n"
"\n"
"#widget_gestion_free,\n"
"#widget_gestion_annee,\n"
"#widget_gestion_faculte,\n"
"#widget_gestion_niveau,\n"
"#widget_paiement,\n"
"#frame_paiement_shadow,\n"
"#admin,\n"
"#prog_cours {\n"
"    background-color: #fff\n"
"}\n"
"\n"
"#widget_gestion_free,\n"
"#widget_gestion_annee,\n"
"#widget_gestion_faculte,\n"
"#widget_gestion_n"
                        "iveau,\n"
"#widget_paiement,\n"
"#frame_paiement_shadow {\n"
"    border-radius: 10px\n"
"}\n"
"\n"
"#btn_close,\n"
"#btn_min,\n"
"#btn_profile,\n"
"#minimize,\n"
"#btn_toggle,\n"
"#btn_admin,\n"
"#btn_pro,\n"
"#btn_etudiant,\n"
"#btn_user,\n"
"#logout,\n"
"#myprofile {\n"
"    background: transparent\n"
"}\n"
"\n"
"#titre_toggle,\n"
"#header_titre {\n"
"    color: #e9993e;\n"
"}\n"
"\n"
"#admin,\n"
"#etudiant,\n"
"#professeur,\n"
"#user,\n"
"#cours,\n"
"#employee,\n"
"#faculte,\n"
"#total,\n"
"#frame {\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"\n"
"#frame_msg {\n"
"    background-color: #fed6dd;\n"
"    border-top-right-radius: 10px;\n"
"    border-top-left-radius: 10px;\n"
"    border-color: #fdc1cc\n"
"}\n"
"\n"
"#label_msg {\n"
"    color: #951d32\n"
"}\n"
"\n"
"/*QComboBox {\n"
"    padding-left: 5px;\n"
"background-color:transparent;\n"
"}\n"
"\n"
"/*QComboBox::drop-down {\n"
"background-color:#fff;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"border-radius:3px;\n"
"height:"
                        "15px;\n"
"margin-right:5px;\n"
"margin-bottom:3px;\n"
"background-color:#fff;\n"
"}\n"
"\n"
"QComboBox QListView {\n"
"    font-size: 12px;\n"
"    padding: 4px;\n"
"    background-color: #fff;\n"
"}\n"
"\n"
"QComboBox QListView:item {\n"
"    padding-left: 8px;\n"
"    background-color: #fff;\n"
"}\n"
"\n"
"QComboBox QListView:item:hover {\n"
"    padding-left: 8px;\n"
"    color: #fff;\n"
"    background: #228BE6;\n"
"}\n"
"\n"
"\n"
"QComboBox QListView:item {\n"
"    padding-left: 8px;\n"
"    background: #228BE6;\n"
"}\n"
"\n"
"QComboBox QListView:item:hover {\n"
"    padding-left: 8px;\n"
"    color: #fff;\n"
"    background: #228BE6;\n"
"}*/\n"
"\n"
"#search_table_admin {\n"
"    border: none\n"
"}\n"
"\n"
"#btn_admin {\n"
"    color: #FAB005;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_user {\n"
"    color: #228BE6;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_pro {\n"
"    color: #40C057;\n"
"    background-color: #fff;\n"
""
                        "    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_etudiant {\n"
"    color: #FA5252;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_cours {\n"
"    color: #0dcaf0;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_faculte {\n"
"    color: #dc3545;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_employee {\n"
"    color: #ffc107;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#btn_total {\n"
"    color: #b23cfd;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#professeur_dash {\n"
"    border: 1px solid #FAB005;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#label_professeur{color:#FAB005; font-size:15pt}\n"
"\n"
"#etudiant_dash {\n"
"    border: 1px solid #228BE6;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"\n"
"}\n"
"\n"
"#label_etudiant_dash{color:#228BE6; font-size:15pt}\n"
""
                        "\n"
"#personnel_dash {\n"
"    border: 1px solid #40C057;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#label_personnel_dash{color:#40C057; font-size:15pt}\n"
"\n"
"#classe_dash {\n"
"    border: 1px solid #FA5252;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#label_classe_dash{color:#FA5252; font-size:15pt}\n"
"\n"
"#cours_dash {\n"
"    border: 1px solid #0dcaf0;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#label_cours{color:#0dcaf0; font-size:15pt}\n"
"\n"
"#faculte_dash {\n"
"    border: 1px solid #dc3545;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#notes_dash {\n"
"    border: 1px solid #f6903f;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"#label_notes_2{color:#f6903f; font-size:15pt}\n"
"\n"
"#paiement_dash {\n"
"    border: 1px solid #b23cfd;\n"
"    background-color: #fff;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#label_paiement_2{color:#b23cfd; fon"
                        "t-size:15pt}\n"
"\n"
"/*#admin:hover {background-color:#FAB005; color:#fff}\n"
"#frame:hover{color:#fff}*/\n"
"\n"
"#btn_left_admin,\n"
"#btn_left_cours,\n"
"#btn_left_etudiant,\n"
"#btn_left_prof,\n"
"#btn_left_home,\n"
"#btn_left_paiement,\n"
"#btn_settings,\n"
"#gestion_des_compte,\n"
"#btn_actualiser,\n"
"#btn_log,\n"
"#btn_a_propos,\n"
"#btn_left_notes,\n"
"#btn_left_rapport,\n"
"#btn_left_vente,\n"
"#btn_left_promus,\n"
"#btn_settings,\n"
"#btn_left_deconnexion,#btn_left_profile {\n"
"    color: #9ca3af;  \n"
"	text-align:left;\n"
"padding:2px 5px;\n"
"padding-left:5px;\n"
"}\n"
"\n"
"#btn_left_deconnexion:focus {\n"
"    background: transparent;\n"
"}\n"
"\n"
"\n"
"\n"
"#btn_left_admin:hover,\n"
"#btn_left_cours:hover,\n"
"#btn_left_etudiant:hover,\n"
"#btn_left_prof:hover,\n"
"#btn_left_home:hover,\n"
"#btn_left_paiement:hover,\n"
"#btn_left_notes:hover,\n"
"#btn_left_rapport:hover,\n"
"#btn_left_vente:hover,\n"
"#btn_left_promus:hover,\n"
"#btn_left_etudiant:hover,\n"
"#btn_left_deconnexion:hover,\n"
""
                        "#btn_settings:hover,\n"
"#btn_actualiser:hover,\n"
"#btn_log:hover,\n"
"#gestion_des_compte:hover,\n"
"#btn_a_propos:hover,#btn_left_profile:hover{\n"
"	background-color: #1f2937;\n"
"padding:5px;\n"
"padding-left:8px;\n"
"    color: #fff;\n"
"}\n"
"/*4b5563*/\n"
"\n"
"#btn_left_admin:checked,\n"
"#btn_left_cours:checked,\n"
"#btn_left_etudiant:checked,\n"
"#btn_left_prof:checked,\n"
"#btn_left_home:checked,\n"
"#btn_left_paiement:checked,\n"
"#btn_left_notes:checked,\n"
"#btn_left_rapport:checked,\n"
"#btn_left_vente:checked,\n"
"#btn_left_promus:checked,\n"
"#btn_log:checked,\n"
"#btn_left_etudiant:checked,\n"
"#btn_left_deconnexion:checked,\n"
"#btn_settings:checked,\n"
"#btn_a_propos:checked,#btn_left_profile:checked\n"
" {\n"
" 	background-color: #1f2937;\n"
"    color: #fff;\n"
"padding:5px;\n"
"padding-left:8px;\n"
"  font-weight: bold;\n"
"    border-top-left-radius: 5px;\n"
"    border-bottom-left-radius: 5px\n"
"}\n"
"\n"
"#btn_min:hover,\n"
"#btn_close:hover,\n"
"#minimize:hover {\n"
"    background"
                        "-color: #eee;\n"
"    border-radius: 5px;\n"
"	padding:5px\n"
"}\n"
"\n"
"#profileCount,\n"
"#frame_8 {\n"
"    background-color: #fdfdfd;\n"
"    border-radius: 15px;\n"
"}\n"
" /*\n"
"#affiche_entre_table_student,\n"
"#search_admin,\n"
"#entry_admin,\n"
"#frame_search_cours,\n"
"#combo_entry_cours,\n"
"#combo_faculte,\n"
"#combo_annee,\n"
"#combo_niveau,\n"
"#entry_professeur,\n"
"#search_professeur,\n"
"#combo_entry_programme,\n"
"#frame_search_programme,\n"
"#frame_search_paiement,\n"
"#entry_paiement,\n"
"#id_etudiant,\n"
"#combo_id_prof,\n"
"#combo_annee_prog,\n"
"#combo_fac,\n"
"#combo_niveau_prog,\n"
"#combo_cours_prog,\n"
"#combo_jours {\n"
"    border: none;\n"
"    border-bottom: 2px solid#1266f1;\n"
"}\n"
"\n"
"\n"
"#search,\n"
"#seach_cours,\n"
"#search_programme,\n"
"#search_paiement {\n"
"    border: none;\n"
"}*/\n"
"#cours_stack{    color: #fcbc05;\n"
"    border: 1px solid #fcbc05;\n"
"    padding: 4px; border-radius: 5px\n"
"}\n"
"#programme_stack{    color: #4385f5;\n"
"    border: 1px soli"
                        "d #4385f5;\n"
"    padding: 4px; border-radius: 5px}\n"
"\n"
"#cours_stack:hover{    color: #fff;\n"
"    border: 1px solid #ff8c00; \n"
"    background-color: #ff8c00;\n"
" border-radius: 5px;\n"
"    padding: 4px;}\n"
"\n"
"#programme_stack:hover{    color: #fff;\n"
"    border: 1px solid #228BE6; \n"
"    background-color: #228BE6;\n"
" border-radius: 5px;\n"
"    padding: 4px;}\n"
"\n"
"#cours_stack:checked{\n"
"  color: #fff;\n"
"    border: 1px solid #fcbc05;\n"
"	border-bottom:0px;\n"
"    background-color: #fcbc05;\n"
"    padding: 4px;\n"
"}\n"
"#programme_stack:checked{    color: #fff;\n"
"    border: 1px solid #228BE6;\n"
"	border-bottom:0px;\n"
"    background-color: #228BE6;\n"
"    padding: 4px;}\n"
"\n"
"#add_student, \n"
"#add_personnel, \n"
"#add_professeur,\n"
"#suivant_1,\n"
"#suivant_2,\n"
"#enregistre,\n"
"#enregistrer_admin,\n"
"#enregistrer_prof,\n"
"#add_prof_button,\n"
"#enregistrer_cours,\n"
"#addCours,\n"
"#addProgramme,\n"
"#enregistrer_programme , \n"
"#next_paiement,\n"
"#prev_pai"
                        "ement,\n"
"#next_notes,\n"
"#prev_notes,\n"
"#paiement_dialog,#notes_dialog,#imprimer_etudiant,\n"
"#valider_id_server,#change_ip,#valider_profile,\n"
"#btn_modifier_permission,#btn_modifier_roles,\n"
"#btn_promus,#btn_for_promus,\n"
"#btn_vente_page,#ajouter_vente,#passer_la_commande,#format_word_financier,#format_word_administratif,#enregistrer_depense,#save_transac{\n"
"    color: #228BE6;\n"
"    border: 1px solid #228BE6;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#add_student:hover ,#enregistrer_depense:hover,#save_transac:hover,\n"
"#add_personnel:hover,\n"
"#format_word_financier:hover,#format_word_administratif:hover\n"
"#add_professeur:hover ,\n"
"#suivant_1:hover,\n"
"#suivant_2:hover,\n"
"#enregistre:hover,\n"
"#enregistrer_admin:hover,\n"
"#enregistrer_prof:hover,\n"
"#add_prof_button:hover,\n"
"#enregistrer_cours:hover,\n"
"#btn_promus:hover,#btn_for_promus:hover,\n"
"#addCours:hover,\n"
"#addProgramme:hover,\n"
"#enregistrer_programme:hover,\n"
"#next_paiement:hover,#prev_pa"
                        "iement:hover,#paiement_dialog:hover,\n"
"#notes_dialog:hover,#next_notes:hover,#prev_notes:hover,#imprimer_etudiant:hover,\n"
"#valider_id_server:hover,#change_ip:hover,#valider_profile:hover,\n"
"#btn_modifier_permission:hover,#btn_modifier_roles:hover,\n"
"#btn_vente_page:hover,#ajouter_vente:hover,#passer_la_commande:hover\n"
" {\n"
"    color: #fff;\n"
"    border: 1px solid #228BE6;\n"
"    background-color: #228BE6;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"/*\n"
"#add_faculte,\n"
"#add_annee,\n"
"#add_frais,\n"
"#add_niveau,\n"
"#paiement_mobile {\n"
"    color: #228BE6;\n"
"    border: 1px solid #228BE6;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#add_faculte:hover,\n"
"#add_annee:hover,\n"
"#add_frais:hover,\n"
"#add_niveau:hover,\n"
"#paiement_mobile:hover {\n"
"    background-color: #228BE6;\n"
"    color: #fff;\n"
"    border: 1px solid #228BE6;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}*/\n"
"\n"
"#fac_active,\n"
"#annee_en_cour,\n"
"#paiement"
                        "_electronique {\n"
"    color: #00b74a;\n"
"    border: 1px solid #00b74a;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#fac_active:hover,\n"
"#annee_en_cour:hover,\n"
"#paiement_electronique:hover {\n"
"    background-color: #00b74a;\n"
"    color: #fff;\n"
"    border: 1px solid #00b74a;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#fac_inactive,\n"
"#universite,\n"
"#paiement {\n"
"    color: #ffa900;\n"
"    border: 1px solid #ffa900;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#fac_inactive:hover,\n"
"#universite:hover,\n"
"#paiement:hover {\n"
"    background-color: #ffa900;\n"
"    color: #fff;\n"
"    border: 1px solid #ffa900;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_cours,\n"
"#primaire {\n"
"    color: #39c0ed;\n"
"    border: 1px solid #39c0ed;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_cours:hover,\n"
"#primaire:hover {\n"
"    background-color: #39c0ed;\n"
"    color: #fff;\n"
""
                        "    border: 1px solid #39c0ed;\n"
"    padding: 4px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_session,\n"
"#secondaire {\n"
"    color: #00b74a;\n"
"    border: 1px solid #00b74a;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_session:hover,\n"
"secondaire:hover {\n"
"    background-color: #00b74a;\n"
"    color: #fff;\n"
"    border: 1px solid #00b74a;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_annee {\n"
"    color: #ffa900;\n"
"    border: 1px solid #ffa900;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#frais_par_annee:hover {\n"
"    background-color: #ffa900;\n"
"    color: #fff;\n"
"    border: 1px solid #ffa900;\n"
"    padding: 3px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_add_note,\n"
"#btn_edit_note,\n"
"#aff_admin,\n"
"#btn_afficher_cours,\n"
"#btn_importer,\n"
"#btn_importer_exel,\n"
"#bulletin_dialog,\n"
"#btn_connexion,#btn_reset_password,\n"
"#reinitialiser_mot_de_passe,#btn_reset_password_prof,\n"
""
                        "#modifier_etudiant,#loans,#edit_transact,#btn_importer_exel{\n"
"    color: #ffa900;\n"
"    border: 1px solid #ffa900;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_add_note:hover,\n"
"#btn_edit_note:hover,\n"
"#aff_admin:hover,\n"
"#bulletin_dialog:hover,\n"
"#btn_afficher_cours:hover,\n"
"#reinitialiser_mot_de_passe:hover,\n"
"#btn_connexion:hover,#btn_reset_password:hover,#btn_reset_password_prof:hover,\n"
"#btn_importer:hover,#modifier_etudiant:hover ,#loans:hover,#edit_transact:hover,#btn_importer_exel:hover{\n"
"    color: #fff;\n"
"    border: 1px solid #ffa900;\n"
"    background-color: #ffa900;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"\n"
"#btn_diplome,#save_badge,\n"
"#affiche_entre_table_student,\n"
"#autre_transaction,\n"
"#aff_user,#accorder_un_pret,\n"
"#btn_programmer_cours,#format_excel_financier,#format_excel_administratif,#format_excel_pedagogique,#faire_un_remboursement,#valider_loans,#desicion_finale_exel{\n"
"    color: #40C057;\n"
"    border"
                        ": 1px solid #40C057;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_diplome:hover,#faire_un_remboursement:hover,#accorder_un_pret:hover,#save_badge:hover,\n"
"#aff_user:hover,#autre_transaction:hover,\n"
"#btn_programmer_cours:hover,#format_excel_financier:hover,#format_excel_administratif:hover,#format_excel_administratif:hover ,#valider_loans:hover,#desicion_finale_exel:hover{\n"
"    color: #fff;\n"
"    border: 1px solid #40C057;\n"
"    background-color: #40C057;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_certificat,\n"
"#ajouter_document,\n"
" #chose_image,\n"
"#add_course_line,\n"
"#add_programme_line,#btn_vente_back,#imprimer_bulletin,#recu_inscrit {\n"
"    border: 1px solid #b23cfd;\n"
"color: #b23cfd;\n"
"padding: 5px;\n"
"border-radius: 5px\n"
"\n"
"}\n"
"\n"
"#choise_profile_image, #template_diplome, #template_certificat, #template_badge_1, #template_badge_2 {\n"
"color: #b23cfd;\n"
"}\n"
"\n"
"#btn_certificat:hover,\n"
"#ajouter_document:hover,\n"
""
                        "#chose_image:hover,\n"
"#add_course_line:hover,\n"
"#add_programme_line:hover ,#btn_vente_back:hover,#imprimer_bulletin:hover,#recu_inscrit:hover{\n"
"    color:#fff;\n"
"    border: 1px solid #b23cfd;\n"
"    background-color: #b23cfd;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"\n"
"}\n"
"\n"
"#aff_employe {\n"
"    color: #0dcaf0;\n"
"    padding: 5px;\n"
"    border: 1px solid #0dcaf0;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#aff_employe:hover {\n"
"    color: #fff;\n"
"    border: 1px solid #0dcaf0;\n"
"    background-color: #0dcaf0;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_badge, #back_1,#back_2 ,#supprimer_etudiant,#delete_vente,#delete_admin,#delete_prof,#cancel_promus,#depense_btn,#delete_depense,#faire_un_remboursement3,#delete_transact,#desicion_finale {\n"
"    color: #dc3545;\n"
"    padding: 5px;\n"
"    border: 1px solid #dc3545;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_badge:hover, #back_1:hover,#back_2:hover,#depense_btn:hover,#faire_un_remboursemen"
                        "t3:hover ,#supprimer_etudiant:hover,#delete_vente:hover,#delete_admin:hover,#delete_prof:hover,#cancel_promus:hover,#delete_depense:hover,#delete_transact:hover,#desicion_finale:hover{\n"
"    color: #fff;\n"
"    border: 1px solid #dc3545;\n"
"    background-color: #dc3545;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_attestation,\n"
"#btn_bultin {\n"
"    color: #FA5252;\n"
"    padding: 5px;\n"
"    border: 1px solid #FA5252;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#btn_attestation:hover,\n"
"#btn_bultin:hover {\n"
"    color: #fff;\n"
"    border: 1px solid #FA5252;\n"
"    background-color: #FA5252;\n"
"    padding: 5px;\n"
"    border-radius: 5px\n"
"}\n"
"\n"
"#add_admin,\n"
"#aff_user,\n"
"#aff_admin,\n"
"#aff_employe {\n"
"    background-color: #fff\n"
"}\n"
"\n"
"#widget_tab_cours,\n"
"#widget_tab_programme {\n"
"    background-color: #fff\n"
"}\n"
"\n"
"#next_page_student1,\n"
"#prev_page_student1 {\n"
"    color: #1266f1\n"
"}\n"
"\n"
"#next_page_student:hover1,\n"
"#prev_"
                        "page_student:hover1 {\n"
"    color: #fff;\n"
"    border: 1px solid #1266f1;\n"
"\n"
"    padding: 3px;\n"
"    border-radius: 4px\n"
"}\n"
"\n"
"#next2,\n"
"#next1,\n"
"#next3,\n"
"#prev1,\n"
"#next_2,\n"
"#annee1,\n"
"#annee2,\n"
"#annee3,\n"
"#annee_next,\n"
"#annee_prev,\n"
"#frais_next,\n"
"#frais_prev,\n"
"#frais_next1,\n"
"#frais_next2,\n"
"#frais_next2,\n"
"#frais_next3 {\n"
"    color: #1266f1;\n"
"    padding: 0px 8px;\n"
"}\n"
"\n"
"#next2:hover,\n"
"#next1:hover,\n"
"#next3:hover,\n"
"#prev1:hover,\n"
"#next_2:hover,\n"
"#annee1:hover,\n"
"#annee2:hover,\n"
"#annee3:hover,\n"
"#annee_next:hover,\n"
"#annee_prev:hover,\n"
"#frais_prev:hover,\n"
"#frais_next:hover,\n"
"#frais_next1:hover,\n"
"#frais_next2:hover,\n"
"#frais_next3:hover {\n"
"    color: #fff;\n"
"    background-color: #1266f1;\n"
"    border-radius: 4px;\n"
"    border: 1px solid #1266f1\n"
"}\n"
"\n"
"#frame_94,\n"
"#frame_95,\n"
"#frame_96,\n"
"#frame_97 {\n"
"    padding: 0px\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    background"
                        "-color: #39c0ed;\n"
"    font-weight: bold;\n"
"    font-size: 12pt;\n"
"    border: none;\n"
"    color: #fff;\n"
"}\n"
"QTableWidget{border:none; \n"
"font-size:13pt;\n"
" color:#4b5563;\n"
"/*font-weight:bold;*/\n"
"}\n"
"\n"
"/*QTableWidget{border:none; border-radius:7px; border: 2px solid #b1b1b1}*/\n"
"\n"
"/*QHeaderView::section:horizontal\n"
"{\n"
"    border-top: 1px solid #fffff8;\n"
"}\n"
"\n"
"QHeaderView::section:vertical\n"
"{\n"
"    border-left: 1px solid #fffff8;\n"
"}\n"
"\n"
"#admin_table::section {\n"
"    background-color: #228BE6;\n"
"	color:#fff;\n"
"	font-weight:bold;\n"
"    font-size: 11pt;\n"
"    border-style: none;\n"
"}\n"
"\n"
"#admin_table{border:none; border-radius:7px; border: 2px solid #FAB005}*/\n"
"\n"
"QTabWidget::pane {\n"
"    border: none;\n"
"    top: -14px\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"    border: none;\n"
"    color: #fff\n"
"}\n"
"\n"
"QTabBar::tab:only-one {\n"
"    margin: 0;\n"
"}\n"
"\n"
"/*Welcome Page*/\n"
"\n"
"QLineEdit,\n"
"QComboBox,\n"
"QDateEdit {\n"
""
                        "    background: #fff\n"
"}\n"
"\n"
"QComboBox QListView {\n"
"    font-size: 12px;\n"
"    padding: 4px;\n"
"    background-color: #fefefe;\n"
"}\n"
"\n"
"QLineEdit,QComboBox {\n"
"    border: none;\n"
"    border-bottom: 2px solid #1266f1\n"
"}\n"
"\n"
"#welcome,\n"
"#header_welcome {\n"
"    background-color: #fff\n"
"}\n"
"\n"
"\n"
"#btn_welcome_valider {\n"
"    border: 1px solid #1266f1;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #1266f1;\n"
"    width: 50px\n"
"}\n"
"\n"
"#btn_welcome_fermer {\n"
"    border: 1px solid #f74a4a;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #f74a4a;\n"
"    width: 50px\n"
"}\n"
"\n"
"#error_message {\n"
"    color: #f74a4a;\n"
"}\n"
"\n"
"#btn_welcome_valider:hover {\n"
"    border: 1px solid #1266f1;\n"
"    background-color: #1266f1;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    width: 50px\n"
"}\n"
"\n"
"#btn_welcome_fermer:hover {\n"
"    border: 1px solid #f74a4a;\n"
"    background-color: #f74"
                        "a4a;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    width: 50px\n"
"}\n"
"\n"
"\n"
"/* Connexion Page*/\n"
"#connexion,\n"
"#header_connexion,\n"
"cours_prog {\n"
"    background-color: #fff;\n"
"border-bottom:1px solid #1f2837\n"
"}\n"
"\n"
"#connexion_page {\n"
"    background-color: #fefefe\n"
"}\n"
"\n"
"#connexion {\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"#btn_connexion_valider,\n"
"#valider_prog,\n"
"#modifier_prog {\n"
"    border: 1px solid #1266f1;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #1266f1;\n"
"    width: 50px\n"
"}\n"
"\n"
"#btn_fermer_connexion,\n"
"#annuler_prog {\n"
"    border: 1px solid #f74a4a;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #f74a4a;\n"
"    width: 50px\n"
"}\n"
"\n"
"#supprimer{\n"
"color: #f74a4a;\n"
" background:transparent\n"
"}\n"
"\n"
"#btn_connexion_valider,\n"
"#modifier_prog,\n"
"#valider_prog:hover {\n"
"    border: 1px solid #1266f1;\n"
"    background-color: #1266f1;\n"
"    padding:"
                        " 4px;\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    width: 50px\n"
"}\n"
"\n"
"#btn_fermer_connexion,\n"
"#annuler_prog:hover {\n"
"    border: 1px solid #f74a4a;\n"
"    background-color: #f74a4a;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #fff;\n"
"    width: 50px\n"
"}\n"
"\n"
"#label_57 {\n"
"    color: #951d32;\n"
"}\n"
"\n"
"\n"
"QComboBox,QLineEdit,QDateEdit {\n"
"               \n"
"                border: 1px solid #ccc;\n"
"                border-radius:5px;\n"
"                padding: 5px;\n"
"min-height:25px;\n"
"max-height:25px; \n"
"background-color: #ffffff;\n"
"    color: #1e293b; /* Texte que l'utilisateur tape */\n"
"    font-size: 14pt;\n"
"            }\n"
"\n"
"QLineEdit::placeholder {\n"
"    color: #94a3b8; /* Gris bleut\u00e9 doux (Slate 400) */\n"
"    font: italic; /* Optionnel : pour bien diff\u00e9rencier du texte saisi */\n"
"font-size: 11pt; \n"
"}\n"
"QCheckBox{\n"
"background-color: #ffffff;\n"
"    color: #1e293b; /* Texte que l'utilisateur tap"
                        "e */\n"
"    font-size: 14px;\n"
"                border: 1px solid #aaa;\n"
"                border-radius:2px; \n"
"}\n"
"            \n"
"            QComboBox:hover,QDateEdit:focus,QLineEdit:focus,QComboBox:focus,QCheckBox:focus {\n"
"                \n"
"                border: 1px solid #007bff;\n"
"            }\n"
"                                        \n"
"            QComboBox:disabled::drop-down, QDateEdit:disabled::drop-down{\n"
"                background: transparent;\n"
"            }\n"
"\n"
"            \n"
"            QComboBox:disabled {\n"
"                background-color: #afafaf;  /* Gris clair */\n"
"                color: #f0f0f0;  /* Texte gris\u00e9 */\n"
"                border: 1px solid #dcdcdc;\n"
"            }\n"
"\n"
"#add_year,#add_frais,#add_paiement_params,#add_faculte,#add_param_exam,#add_class,#global_rapport_imprimer,#administratif_imprimer,#pedagogique_imprimer,#financier_imprimer, #add_frais_divers{color:#1f2837;border:1px solid #1f2837;padding: 3px;padding-left:5px"
                        ";padding-right:5px;border-radius:5px}\n"
"\n"
"#add_year:hover,\n"
"#add_frais:hover,\n"
"#add_paiement_params:hover,\n"
"#add_faculte:hover,\n"
"#add_param_exam:hover,\n"
"#add_class:hover,#global_rapport_imprimer:hover,#administratif_imprimer:hover,#pedagogique_imprimer:hover,#financier_imprimer:hover, #add_frais_divers:hover\n"
"{\n"
"background-color:#1f2837;\n"
"color:#fff;\n"
"/*border:1px solid #1f2837;*/\n"
"border:0px;\n"
"font-weight:bold;\n"
"padding:5px\n"
"}")
        self.centralwidget.setInputMethodHints(Qt.ImhExclusiveInputMask)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.main_with_shadow = QStackedWidget(self.centralwidget)
        self.main_with_shadow.setObjectName(u"main_with_shadow")
        self.main_with_shadow.setMinimumSize(QSize(0, 640))
        self.connexion_error = QWidget()
        self.connexion_error.setObjectName(u"connexion_error")
        self.connexion_error.setMaximumSize(QSize(16777215, 640))
        self.verticalLayout_168 = QVBoxLayout(self.connexion_error)
        self.verticalLayout_168.setObjectName(u"verticalLayout_168")
        self.verticalLayout_168.setContentsMargins(0, 0, 0, 0)
        self.header_connexion_error = QWidget(self.connexion_error)
        self.header_connexion_error.setObjectName(u"header_connexion_error")
        self.horizontalLayout_87 = QHBoxLayout(self.header_connexion_error)
        self.horizontalLayout_87.setSpacing(0)
        self.horizontalLayout_87.setObjectName(u"horizontalLayout_87")
        self.horizontalLayout_87.setContentsMargins(0, 5, 0, 5)
        self.frame_222 = QFrame(self.header_connexion_error)
        self.frame_222.setObjectName(u"frame_222")
        self.frame_222.setMaximumSize(QSize(16777215, 50))
        self.frame_222.setFrameShape(QFrame.StyledPanel)
        self.frame_222.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_163 = QHBoxLayout(self.frame_222)
        self.horizontalLayout_163.setSpacing(0)
        self.horizontalLayout_163.setObjectName(u"horizontalLayout_163")
        self.horizontalLayout_163.setContentsMargins(0, 0, 0, 0)
        self.frame_223 = QFrame(self.frame_222)
        self.frame_223.setObjectName(u"frame_223")
        self.frame_223.setFrameShape(QFrame.StyledPanel)
        self.frame_223.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_164 = QHBoxLayout(self.frame_223)
        self.horizontalLayout_164.setObjectName(u"horizontalLayout_164")
        self.horizontalLayout_164.setContentsMargins(0, 0, 0, -1)
        self.label_72 = QLabel(self.frame_223)
        self.label_72.setObjectName(u"label_72")

        self.horizontalLayout_164.addWidget(self.label_72)


        self.horizontalLayout_163.addWidget(self.frame_223)

        self.frame_227 = QFrame(self.frame_222)
        self.frame_227.setObjectName(u"frame_227")
        self.frame_227.setMinimumSize(QSize(430, 0))
        self.frame_227.setFrameShape(QFrame.StyledPanel)
        self.frame_227.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_165 = QHBoxLayout(self.frame_227)
        self.horizontalLayout_165.setObjectName(u"horizontalLayout_165")
        self.horizontalLayout_165.setContentsMargins(0, 0, 0, 0)
        self.label_73 = QLabel(self.frame_227)
        self.label_73.setObjectName(u"label_73")

        self.horizontalLayout_165.addWidget(self.label_73)

        self.label_connect_4 = QLabel(self.frame_227)
        self.label_connect_4.setObjectName(u"label_connect_4")
        font1 = QFont()
        font1.setFamilies([u"Inter"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.label_connect_4.setFont(font1)

        self.horizontalLayout_165.addWidget(self.label_connect_4)

        self.label_74 = QLabel(self.frame_227)
        self.label_74.setObjectName(u"label_74")

        self.horizontalLayout_165.addWidget(self.label_74)


        self.horizontalLayout_163.addWidget(self.frame_227)

        self.frame_228 = QFrame(self.frame_222)
        self.frame_228.setObjectName(u"frame_228")
        self.frame_228.setFrameShape(QFrame.StyledPanel)
        self.frame_228.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_166 = QHBoxLayout(self.frame_228)
        self.horizontalLayout_166.setSpacing(10)
        self.horizontalLayout_166.setObjectName(u"horizontalLayout_166")
        self.horizontalLayout_166.setContentsMargins(0, 0, 0, 0)
        self.min_error = QPushButton(self.frame_228)
        self.min_error.setObjectName(u"min_error")
        icon = QIcon()
        icon.addFile(u"../../../../../../.designer/assets/icons/icons8-subtract-96.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.min_error.setIcon(icon)
        self.min_error.setIconSize(QSize(20, 20))
        self.min_error.setFlat(True)

        self.horizontalLayout_166.addWidget(self.min_error)

        self.close_error = QPushButton(self.frame_228)
        self.close_error.setObjectName(u"close_error")
        icon1 = QIcon()
        icon1.addFile(u"../../../../../../.designer/assets/icons/icons8-close-48.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.close_error.setIcon(icon1)
        self.close_error.setIconSize(QSize(20, 20))
        self.close_error.setFlat(True)

        self.horizontalLayout_166.addWidget(self.close_error)


        self.horizontalLayout_163.addWidget(self.frame_228, 0, Qt.AlignRight|Qt.AlignVCenter)


        self.horizontalLayout_87.addWidget(self.frame_222)


        self.verticalLayout_168.addWidget(self.header_connexion_error, 0, Qt.AlignTop)

        self.frame_27 = QFrame(self.connexion_error)
        self.frame_27.setObjectName(u"frame_27")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_27.sizePolicy().hasHeightForWidth())
        self.frame_27.setSizePolicy(sizePolicy)
        self.frame_27.setFrameShape(QFrame.StyledPanel)
        self.frame_27.setFrameShadow(QFrame.Raised)
        self.verticalLayout_204 = QVBoxLayout(self.frame_27)
        self.verticalLayout_204.setObjectName(u"verticalLayout_204")
        self.frame_232 = QFrame(self.frame_27)
        self.frame_232.setObjectName(u"frame_232")
        self.frame_232.setFrameShape(QFrame.StyledPanel)
        self.frame_232.setFrameShadow(QFrame.Raised)
        self.verticalLayout_207 = QVBoxLayout(self.frame_232)
        self.verticalLayout_207.setObjectName(u"verticalLayout_207")
        self.frame_233 = QFrame(self.frame_232)
        self.frame_233.setObjectName(u"frame_233")
        self.frame_233.setFrameShape(QFrame.StyledPanel)
        self.frame_233.setFrameShadow(QFrame.Raised)
        self.verticalLayout_208 = QVBoxLayout(self.frame_233)
        self.verticalLayout_208.setObjectName(u"verticalLayout_208")
        self.verticalLayout_208.setContentsMargins(-1, 0, 0, 0)
        self.label = QLabel(self.frame_233)
        self.label.setObjectName(u"label")

        self.verticalLayout_208.addWidget(self.label)

        self.server_ip = QLineEdit(self.frame_233)
        self.server_ip.setObjectName(u"server_ip")
        self.server_ip.setMinimumSize(QSize(500, 37))

        self.verticalLayout_208.addWidget(self.server_ip)


        self.verticalLayout_207.addWidget(self.frame_233)

        self.frame_234 = QFrame(self.frame_232)
        self.frame_234.setObjectName(u"frame_234")
        self.frame_234.setFrameShape(QFrame.StyledPanel)
        self.frame_234.setFrameShadow(QFrame.Raised)
        self.verticalLayout_209 = QVBoxLayout(self.frame_234)
        self.verticalLayout_209.setObjectName(u"verticalLayout_209")
        self.valider_id_server = QPushButton(self.frame_234)
        self.valider_id_server.setObjectName(u"valider_id_server")
        self.valider_id_server.setMinimumSize(QSize(110, 0))
        self.valider_id_server.setFont(font)
        self.valider_id_server.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.valider_id_server.setFlat(True)

        self.verticalLayout_209.addWidget(self.valider_id_server)


        self.verticalLayout_207.addWidget(self.frame_234, 0, Qt.AlignRight)


        self.verticalLayout_204.addWidget(self.frame_232, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_229 = QFrame(self.frame_27)
        self.frame_229.setObjectName(u"frame_229")
        self.frame_229.setFrameShape(QFrame.StyledPanel)
        self.frame_229.setFrameShadow(QFrame.Raised)
        self.verticalLayout_205 = QVBoxLayout(self.frame_229)
        self.verticalLayout_205.setSpacing(15)
        self.verticalLayout_205.setObjectName(u"verticalLayout_205")
        self.frame_230 = QFrame(self.frame_229)
        self.frame_230.setObjectName(u"frame_230")
        self.frame_230.setMinimumSize(QSize(500, 300))
        self.frame_230.setMaximumSize(QSize(500, 300))
        self.frame_230.setFrameShape(QFrame.StyledPanel)
        self.frame_230.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_90 = QHBoxLayout(self.frame_230)
        self.horizontalLayout_90.setSpacing(0)
        self.horizontalLayout_90.setObjectName(u"horizontalLayout_90")
        self.horizontalLayout_90.setContentsMargins(0, 0, 0, 0)
        self.gif_animate = QLabel(self.frame_230)
        self.gif_animate.setObjectName(u"gif_animate")
        self.gif_animate.setMinimumSize(QSize(500, 300))
        self.gif_animate.setMaximumSize(QSize(500, 300))
        self.gif_animate.setScaledContents(True)
        self.gif_animate.setWordWrap(True)

        self.horizontalLayout_90.addWidget(self.gif_animate, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_205.addWidget(self.frame_230, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_231 = QFrame(self.frame_229)
        self.frame_231.setObjectName(u"frame_231")
        self.frame_231.setMinimumSize(QSize(600, 0))
        self.frame_231.setFrameShape(QFrame.StyledPanel)
        self.frame_231.setFrameShadow(QFrame.Raised)
        self.verticalLayout_206 = QVBoxLayout(self.frame_231)
        self.verticalLayout_206.setObjectName(u"verticalLayout_206")
        self.label_75 = QLabel(self.frame_231)
        self.label_75.setObjectName(u"label_75")
        self.label_75.setMinimumSize(QSize(700, 0))
        font2 = QFont()
        font2.setFamilies([u"Inter"])
        font2.setPointSize(14)
        self.label_75.setFont(font2)
        self.label_75.setWordWrap(True)

        self.verticalLayout_206.addWidget(self.label_75)


        self.verticalLayout_205.addWidget(self.frame_231)


        self.verticalLayout_204.addWidget(self.frame_229, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_168.addWidget(self.frame_27)

        self.main_with_shadow.addWidget(self.connexion_error)
        self.reset_password = QWidget()
        self.reset_password.setObjectName(u"reset_password")
        self.verticalLayout_285 = QVBoxLayout(self.reset_password)
        self.verticalLayout_285.setObjectName(u"verticalLayout_285")
        self.body_connect_2 = QWidget(self.reset_password)
        self.body_connect_2.setObjectName(u"body_connect_2")
        self.horizontalLayout_111 = QHBoxLayout(self.body_connect_2)
        self.horizontalLayout_111.setSpacing(0)
        self.horizontalLayout_111.setObjectName(u"horizontalLayout_111")
        self.horizontalLayout_111.setContentsMargins(0, 0, 0, 0)
        self.connexion_4 = QWidget(self.body_connect_2)
        self.connexion_4.setObjectName(u"connexion_4")
        self.connexion_4.setEnabled(True)
        self.horizontalLayout_156 = QHBoxLayout(self.connexion_4)
        self.horizontalLayout_156.setSpacing(14)
        self.horizontalLayout_156.setObjectName(u"horizontalLayout_156")
        self.horizontalLayout_156.setContentsMargins(9, 9, 9, 9)
        self.frame_303 = QFrame(self.connexion_4)
        self.frame_303.setObjectName(u"frame_303")
        self.frame_303.setMinimumSize(QSize(50, 0))
        self.frame_303.setFrameShape(QFrame.StyledPanel)
        self.frame_303.setFrameShadow(QFrame.Raised)
        self.verticalLayout_81 = QVBoxLayout(self.frame_303)
        self.verticalLayout_81.setSpacing(0)
        self.verticalLayout_81.setObjectName(u"verticalLayout_81")
        self.verticalLayout_81.setContentsMargins(0, 0, 0, 0)
        self.title_4 = QFrame(self.frame_303)
        self.title_4.setObjectName(u"title_4")
        self.title_4.setFrameShape(QFrame.StyledPanel)
        self.title_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_167 = QHBoxLayout(self.title_4)
        self.horizontalLayout_167.setSpacing(0)
        self.horizontalLayout_167.setObjectName(u"horizontalLayout_167")
        self.horizontalLayout_167.setContentsMargins(0, 0, 0, 0)
        self.label_89 = QLabel(self.title_4)
        self.label_89.setObjectName(u"label_89")
        self.label_89.setFont(font1)

        self.horizontalLayout_167.addWidget(self.label_89, 0, Qt.AlignHCenter)


        self.verticalLayout_81.addWidget(self.title_4)

        self.frame_304 = QFrame(self.frame_303)
        self.frame_304.setObjectName(u"frame_304")
        sizePolicy.setHeightForWidth(self.frame_304.sizePolicy().hasHeightForWidth())
        self.frame_304.setSizePolicy(sizePolicy)
        self.frame_304.setMaximumSize(QSize(700, 16777215))
        self.frame_304.setFrameShape(QFrame.StyledPanel)
        self.frame_304.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_168 = QHBoxLayout(self.frame_304)
        self.horizontalLayout_168.setSpacing(20)
        self.horizontalLayout_168.setObjectName(u"horizontalLayout_168")
        self.horizontalLayout_168.setContentsMargins(0, 0, 0, 0)
        self.form_4 = QFrame(self.frame_304)
        self.form_4.setObjectName(u"form_4")
        self.form_4.setFrameShape(QFrame.StyledPanel)
        self.form_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_278 = QVBoxLayout(self.form_4)
        self.verticalLayout_278.setSpacing(9)
        self.verticalLayout_278.setObjectName(u"verticalLayout_278")
        self.verticalLayout_278.setContentsMargins(0, 0, 0, 0)
        self.error_message_2 = QLabel(self.form_4)
        self.error_message_2.setObjectName(u"error_message_2")
        palette = QPalette()
        brush = QBrush(QColor(75, 85, 99, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush)
#endif
        self.error_message_2.setPalette(palette)
        font3 = QFont()
        font3.setFamilies([u"Inter"])
        font3.setPointSize(14)
        font3.setBold(False)
        self.error_message_2.setFont(font3)

        self.verticalLayout_278.addWidget(self.error_message_2, 0, Qt.AlignHCenter)

        self.frame_user_connexion_4 = QFrame(self.form_4)
        self.frame_user_connexion_4.setObjectName(u"frame_user_connexion_4")
        self.frame_user_connexion_4.setFrameShape(QFrame.StyledPanel)
        self.frame_user_connexion_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_170 = QHBoxLayout(self.frame_user_connexion_4)
        self.horizontalLayout_170.setObjectName(u"horizontalLayout_170")
        self.horizontalLayout_170.setContentsMargins(0, -1, 0, -1)
        self.password_for_reset = QLineEdit(self.frame_user_connexion_4)
        self.password_for_reset.setObjectName(u"password_for_reset")
        self.password_for_reset.setMinimumSize(QSize(400, 37))
        self.password_for_reset.setFont(font2)
        self.password_for_reset.setEchoMode(QLineEdit.Password)

        self.horizontalLayout_170.addWidget(self.password_for_reset)


        self.verticalLayout_278.addWidget(self.frame_user_connexion_4)

        self.frame_password_connect_4 = QFrame(self.form_4)
        self.frame_password_connect_4.setObjectName(u"frame_password_connect_4")
        self.frame_password_connect_4.setFrameShape(QFrame.StyledPanel)
        self.frame_password_connect_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_279 = QVBoxLayout(self.frame_password_connect_4)
        self.verticalLayout_279.setSpacing(0)
        self.verticalLayout_279.setObjectName(u"verticalLayout_279")
        self.verticalLayout_279.setContentsMargins(0, 15, 0, 0)
        self.confirm_password = QLineEdit(self.frame_password_connect_4)
        self.confirm_password.setObjectName(u"confirm_password")
        self.confirm_password.setMinimumSize(QSize(400, 37))
        self.confirm_password.setFont(font2)
        self.confirm_password.setInputMethodHints(Qt.ImhHiddenText|Qt.ImhNoAutoUppercase|Qt.ImhNoPredictiveText|Qt.ImhSensitiveData)
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setCursorPosition(0)
        self.confirm_password.setCursorMoveStyle(Qt.VisualMoveStyle)

        self.verticalLayout_279.addWidget(self.confirm_password)


        self.verticalLayout_278.addWidget(self.frame_password_connect_4)

        self.frame_306 = QFrame(self.form_4)
        self.frame_306.setObjectName(u"frame_306")
        self.frame_306.setFrameShape(QFrame.StyledPanel)
        self.frame_306.setFrameShadow(QFrame.Raised)
        self.verticalLayout_281 = QVBoxLayout(self.frame_306)
        self.verticalLayout_281.setSpacing(0)
        self.verticalLayout_281.setObjectName(u"verticalLayout_281")
        self.verticalLayout_281.setContentsMargins(0, 0, 0, 0)
        self.frame_307 = QFrame(self.frame_306)
        self.frame_307.setObjectName(u"frame_307")
        self.frame_307.setFrameShape(QFrame.StyledPanel)
        self.frame_307.setFrameShadow(QFrame.Raised)
        self.verticalLayout_282 = QVBoxLayout(self.frame_307)
        self.verticalLayout_282.setSpacing(0)
        self.verticalLayout_282.setObjectName(u"verticalLayout_282")
        self.verticalLayout_282.setContentsMargins(0, 0, 0, 0)
        self.frame_308 = QFrame(self.frame_307)
        self.frame_308.setObjectName(u"frame_308")
        self.frame_308.setFrameShape(QFrame.StyledPanel)
        self.frame_308.setFrameShadow(QFrame.Raised)
        self.verticalLayout_283 = QVBoxLayout(self.frame_308)
        self.verticalLayout_283.setSpacing(0)
        self.verticalLayout_283.setObjectName(u"verticalLayout_283")
        self.verticalLayout_283.setContentsMargins(0, 0, 0, 0)
        self.user_id_for_change_password = QLineEdit(self.frame_308)
        self.user_id_for_change_password.setObjectName(u"user_id_for_change_password")
        self.user_id_for_change_password.setFont(font2)

        self.verticalLayout_283.addWidget(self.user_id_for_change_password)


        self.verticalLayout_282.addWidget(self.frame_308)


        self.verticalLayout_281.addWidget(self.frame_307)


        self.verticalLayout_278.addWidget(self.frame_306)

        self.frame_button_4 = QFrame(self.form_4)
        self.frame_button_4.setObjectName(u"frame_button_4")
        self.frame_button_4.setFrameShape(QFrame.StyledPanel)
        self.frame_button_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_171 = QHBoxLayout(self.frame_button_4)
        self.horizontalLayout_171.setObjectName(u"horizontalLayout_171")
        self.btn_reset_password = QPushButton(self.frame_button_4)
        self.btn_reset_password.setObjectName(u"btn_reset_password")
        self.btn_reset_password.setEnabled(True)
        self.btn_reset_password.setFont(font)
        self.btn_reset_password.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_reset_password.setFlat(True)

        self.horizontalLayout_171.addWidget(self.btn_reset_password)


        self.verticalLayout_278.addWidget(self.frame_button_4)


        self.horizontalLayout_168.addWidget(self.form_4)


        self.verticalLayout_81.addWidget(self.frame_304)


        self.horizontalLayout_156.addWidget(self.frame_303)


        self.horizontalLayout_111.addWidget(self.connexion_4, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_285.addWidget(self.body_connect_2)

        self.main_with_shadow.addWidget(self.reset_password)
        self.welcome = QWidget()
        self.welcome.setObjectName(u"welcome")
        self.welcome.setMaximumSize(QSize(0, 0))
        self.verticalLayout_4 = QVBoxLayout(self.welcome)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.main_with_shadow.addWidget(self.welcome)
        self.connexion_page = QWidget()
        self.connexion_page.setObjectName(u"connexion_page")
        self.verticalLayout_2 = QVBoxLayout(self.connexion_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.header_connexion = QWidget(self.connexion_page)
        self.header_connexion.setObjectName(u"header_connexion")
        self.horizontalLayout = QHBoxLayout(self.header_connexion)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 2, 0, 2)
        self.frame_131 = QFrame(self.header_connexion)
        self.frame_131.setObjectName(u"frame_131")
        self.frame_131.setMaximumSize(QSize(16777215, 50))
        self.frame_131.setFrameShape(QFrame.StyledPanel)
        self.frame_131.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_158 = QHBoxLayout(self.frame_131)
        self.horizontalLayout_158.setSpacing(2)
        self.horizontalLayout_158.setObjectName(u"horizontalLayout_158")
        self.horizontalLayout_158.setContentsMargins(0, 0, 0, 2)
        self.frame_132 = QFrame(self.frame_131)
        self.frame_132.setObjectName(u"frame_132")
        self.frame_132.setFrameShape(QFrame.StyledPanel)
        self.frame_132.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_159 = QHBoxLayout(self.frame_132)
        self.horizontalLayout_159.setObjectName(u"horizontalLayout_159")
        self.horizontalLayout_159.setContentsMargins(0, 0, 0, -1)
        self.label_59 = QLabel(self.frame_132)
        self.label_59.setObjectName(u"label_59")

        self.horizontalLayout_159.addWidget(self.label_59)


        self.horizontalLayout_158.addWidget(self.frame_132)

        self.frame_133 = QFrame(self.frame_131)
        self.frame_133.setObjectName(u"frame_133")
        self.frame_133.setMinimumSize(QSize(430, 0))
        self.frame_133.setFrameShape(QFrame.StyledPanel)
        self.frame_133.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_160 = QHBoxLayout(self.frame_133)
        self.horizontalLayout_160.setObjectName(u"horizontalLayout_160")
        self.horizontalLayout_160.setContentsMargins(0, 0, 0, 0)
        self.label_60 = QLabel(self.frame_133)
        self.label_60.setObjectName(u"label_60")

        self.horizontalLayout_160.addWidget(self.label_60)

        self.label_connect_3 = QLabel(self.frame_133)
        self.label_connect_3.setObjectName(u"label_connect_3")
        self.label_connect_3.setFont(font1)

        self.horizontalLayout_160.addWidget(self.label_connect_3)

        self.label_61 = QLabel(self.frame_133)
        self.label_61.setObjectName(u"label_61")

        self.horizontalLayout_160.addWidget(self.label_61)


        self.horizontalLayout_158.addWidget(self.frame_133)

        self.frame_134 = QFrame(self.frame_131)
        self.frame_134.setObjectName(u"frame_134")
        self.frame_134.setFrameShape(QFrame.StyledPanel)
        self.frame_134.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_161 = QHBoxLayout(self.frame_134)
        self.horizontalLayout_161.setSpacing(10)
        self.horizontalLayout_161.setObjectName(u"horizontalLayout_161")
        self.horizontalLayout_161.setContentsMargins(0, 0, 0, 0)
        self.min_4 = QPushButton(self.frame_134)
        self.min_4.setObjectName(u"min_4")
        self.min_4.setIcon(icon)
        self.min_4.setIconSize(QSize(20, 20))

        self.horizontalLayout_161.addWidget(self.min_4)

        self.full_4 = QPushButton(self.frame_134)
        self.full_4.setObjectName(u"full_4")
        icon2 = QIcon()
        icon2.addFile(u"../../../../../../.designer/assets/icons/icons8-full-image-96.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.full_4.setIcon(icon2)
        self.full_4.setIconSize(QSize(20, 20))

        self.horizontalLayout_161.addWidget(self.full_4)

        self.close_4 = QPushButton(self.frame_134)
        self.close_4.setObjectName(u"close_4")
        self.close_4.setIcon(icon1)
        self.close_4.setIconSize(QSize(20, 20))

        self.horizontalLayout_161.addWidget(self.close_4)


        self.horizontalLayout_158.addWidget(self.frame_134, 0, Qt.AlignRight|Qt.AlignVCenter)


        self.horizontalLayout.addWidget(self.frame_131)


        self.verticalLayout_2.addWidget(self.header_connexion)

        self.verticalSpacer = QSpacerItem(20, 169, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.body_connect = QWidget(self.connexion_page)
        self.body_connect.setObjectName(u"body_connect")
        self.verticalLayout_3 = QVBoxLayout(self.body_connect)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.connexion_3 = QWidget(self.body_connect)
        self.connexion_3.setObjectName(u"connexion_3")
        self.connexion_3.setEnabled(True)
        self.horizontalLayout_151 = QHBoxLayout(self.connexion_3)
        self.horizontalLayout_151.setSpacing(14)
        self.horizontalLayout_151.setObjectName(u"horizontalLayout_151")
        self.horizontalLayout_151.setContentsMargins(9, 9, 9, 9)
        self.frame_129 = QFrame(self.connexion_3)
        self.frame_129.setObjectName(u"frame_129")
        self.frame_129.setMinimumSize(QSize(50, 0))
        self.frame_129.setFrameShape(QFrame.StyledPanel)
        self.frame_129.setFrameShadow(QFrame.Raised)
        self.verticalLayout_68 = QVBoxLayout(self.frame_129)
        self.verticalLayout_68.setSpacing(0)
        self.verticalLayout_68.setObjectName(u"verticalLayout_68")
        self.verticalLayout_68.setContentsMargins(0, 0, 0, 0)
        self.title_3 = QFrame(self.frame_129)
        self.title_3.setObjectName(u"title_3")
        self.title_3.setFrameShape(QFrame.StyledPanel)
        self.title_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_152 = QHBoxLayout(self.title_3)
        self.horizontalLayout_152.setSpacing(0)
        self.horizontalLayout_152.setObjectName(u"horizontalLayout_152")
        self.horizontalLayout_152.setContentsMargins(0, 0, 0, 0)
        self.label_49 = QLabel(self.title_3)
        self.label_49.setObjectName(u"label_49")
        self.label_49.setFont(font1)

        self.horizontalLayout_152.addWidget(self.label_49, 0, Qt.AlignHCenter)


        self.verticalLayout_68.addWidget(self.title_3)

        self.frame_130 = QFrame(self.frame_129)
        self.frame_130.setObjectName(u"frame_130")
        sizePolicy.setHeightForWidth(self.frame_130.sizePolicy().hasHeightForWidth())
        self.frame_130.setSizePolicy(sizePolicy)
        self.frame_130.setMaximumSize(QSize(700, 16777215))
        self.frame_130.setFrameShape(QFrame.StyledPanel)
        self.frame_130.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_153 = QHBoxLayout(self.frame_130)
        self.horizontalLayout_153.setSpacing(20)
        self.horizontalLayout_153.setObjectName(u"horizontalLayout_153")
        self.horizontalLayout_153.setContentsMargins(0, 0, 0, 0)
        self.image_3 = QFrame(self.frame_130)
        self.image_3.setObjectName(u"image_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.image_3.sizePolicy().hasHeightForWidth())
        self.image_3.setSizePolicy(sizePolicy1)
        self.image_3.setMinimumSize(QSize(200, 200))
        self.image_3.setFrameShape(QFrame.StyledPanel)
        self.image_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_154 = QHBoxLayout(self.image_3)
        self.horizontalLayout_154.setObjectName(u"horizontalLayout_154")
        self.horizontalLayout_154.setContentsMargins(0, 0, 0, 0)
        self.widget_logo = QWidget(self.image_3)
        self.widget_logo.setObjectName(u"widget_logo")
        self.verticalLayout_11 = QVBoxLayout(self.widget_logo)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.logo = QLabel(self.widget_logo)
        self.logo.setObjectName(u"logo")
        sizePolicy1.setHeightForWidth(self.logo.sizePolicy().hasHeightForWidth())
        self.logo.setSizePolicy(sizePolicy1)
        self.logo.setMinimumSize(QSize(200, 200))
        self.logo.setMaximumSize(QSize(66, 16777215))
        self.logo.setScaledContents(True)
        self.logo.setAlignment(Qt.AlignCenter)

        self.verticalLayout_11.addWidget(self.logo)


        self.horizontalLayout_154.addWidget(self.widget_logo, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.horizontalLayout_153.addWidget(self.image_3, 0, Qt.AlignHCenter)

        self.form_3 = QFrame(self.frame_130)
        self.form_3.setObjectName(u"form_3")
        self.form_3.setFrameShape(QFrame.StyledPanel)
        self.form_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_69 = QVBoxLayout(self.form_3)
        self.verticalLayout_69.setSpacing(9)
        self.verticalLayout_69.setObjectName(u"verticalLayout_69")
        self.verticalLayout_69.setContentsMargins(0, 0, 0, 0)
        self.error_message = QLabel(self.form_3)
        self.error_message.setObjectName(u"error_message")
        palette1 = QPalette()
        brush2 = QBrush(QColor(247, 74, 74, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush2)
#endif
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush2)
#endif
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush2)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush2)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush2)
#endif
        self.error_message.setPalette(palette1)
        self.error_message.setFont(font3)

        self.verticalLayout_69.addWidget(self.error_message, 0, Qt.AlignHCenter)

        self.frame_user_connexion_3 = QFrame(self.form_3)
        self.frame_user_connexion_3.setObjectName(u"frame_user_connexion_3")
        self.frame_user_connexion_3.setFrameShape(QFrame.StyledPanel)
        self.frame_user_connexion_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_155 = QHBoxLayout(self.frame_user_connexion_3)
        self.horizontalLayout_155.setObjectName(u"horizontalLayout_155")
        self.horizontalLayout_155.setContentsMargins(0, -1, 0, -1)
        self.email_2 = QLineEdit(self.frame_user_connexion_3)
        self.email_2.setObjectName(u"email_2")
        self.email_2.setMinimumSize(QSize(400, 37))
        self.email_2.setFont(font2)

        self.horizontalLayout_155.addWidget(self.email_2)


        self.verticalLayout_69.addWidget(self.frame_user_connexion_3)

        self.frame_password_connect_3 = QFrame(self.form_3)
        self.frame_password_connect_3.setObjectName(u"frame_password_connect_3")
        self.frame_password_connect_3.setFrameShape(QFrame.StyledPanel)
        self.frame_password_connect_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_220 = QVBoxLayout(self.frame_password_connect_3)
        self.verticalLayout_220.setSpacing(0)
        self.verticalLayout_220.setObjectName(u"verticalLayout_220")
        self.verticalLayout_220.setContentsMargins(0, 15, 0, 0)
        self.password_2 = QLineEdit(self.frame_password_connect_3)
        self.password_2.setObjectName(u"password_2")
        self.password_2.setMinimumSize(QSize(400, 37))
        self.password_2.setFont(font2)
        self.password_2.setInputMethodHints(Qt.ImhHiddenText|Qt.ImhNoAutoUppercase|Qt.ImhNoPredictiveText|Qt.ImhSensitiveData)
        self.password_2.setEchoMode(QLineEdit.Password)
        self.password_2.setCursorPosition(0)
        self.password_2.setCursorMoveStyle(Qt.VisualMoveStyle)

        self.verticalLayout_220.addWidget(self.password_2)

        self.frame_241 = QFrame(self.frame_password_connect_3)
        self.frame_241.setObjectName(u"frame_241")
        self.frame_241.setMinimumSize(QSize(0, 25))
        self.frame_241.setFrameShape(QFrame.StyledPanel)
        self.frame_241.setFrameShadow(QFrame.Raised)
        self.verticalLayout_219 = QVBoxLayout(self.frame_241)
        self.verticalLayout_219.setSpacing(0)
        self.verticalLayout_219.setObjectName(u"verticalLayout_219")
        self.verticalLayout_219.setContentsMargins(0, 0, 0, 0)
        self.show_frame_ip = QPushButton(self.frame_241)
        self.show_frame_ip.setObjectName(u"show_frame_ip")
        font4 = QFont()
        font4.setFamilies([u"Inter"])
        font4.setPointSize(13)
        self.show_frame_ip.setFont(font4)
        self.show_frame_ip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.show_frame_ip.setCheckable(True)
        self.show_frame_ip.setAutoExclusive(True)

        self.verticalLayout_219.addWidget(self.show_frame_ip)


        self.verticalLayout_220.addWidget(self.frame_241, 0, Qt.AlignRight)


        self.verticalLayout_69.addWidget(self.frame_password_connect_3)

        self.frame_238 = QFrame(self.form_3)
        self.frame_238.setObjectName(u"frame_238")
        self.frame_238.setFrameShape(QFrame.StyledPanel)
        self.frame_238.setFrameShadow(QFrame.Raised)
        self.verticalLayout_215 = QVBoxLayout(self.frame_238)
        self.verticalLayout_215.setSpacing(0)
        self.verticalLayout_215.setObjectName(u"verticalLayout_215")
        self.verticalLayout_215.setContentsMargins(0, 0, 0, 0)
        self.frame_240 = QFrame(self.frame_238)
        self.frame_240.setObjectName(u"frame_240")
        self.frame_240.setFrameShape(QFrame.StyledPanel)
        self.frame_240.setFrameShadow(QFrame.Raised)
        self.verticalLayout_216 = QVBoxLayout(self.frame_240)
        self.verticalLayout_216.setSpacing(0)
        self.verticalLayout_216.setObjectName(u"verticalLayout_216")
        self.verticalLayout_216.setContentsMargins(0, 0, 0, 0)
        self.frame_243 = QFrame(self.frame_240)
        self.frame_243.setObjectName(u"frame_243")
        self.frame_243.setFrameShape(QFrame.StyledPanel)
        self.frame_243.setFrameShadow(QFrame.Raised)
        self.verticalLayout_217 = QVBoxLayout(self.frame_243)
        self.verticalLayout_217.setSpacing(0)
        self.verticalLayout_217.setObjectName(u"verticalLayout_217")
        self.verticalLayout_217.setContentsMargins(0, 0, 0, 0)
        self.label_76 = QLabel(self.frame_243)
        self.label_76.setObjectName(u"label_76")

        self.verticalLayout_217.addWidget(self.label_76)

        self.input_change_ip = QLineEdit(self.frame_243)
        self.input_change_ip.setObjectName(u"input_change_ip")
        self.input_change_ip.setFont(font2)

        self.verticalLayout_217.addWidget(self.input_change_ip)


        self.verticalLayout_216.addWidget(self.frame_243)

        self.frame_242 = QFrame(self.frame_240)
        self.frame_242.setObjectName(u"frame_242")
        self.frame_242.setFrameShape(QFrame.StyledPanel)
        self.frame_242.setFrameShadow(QFrame.Raised)
        self.verticalLayout_218 = QVBoxLayout(self.frame_242)
        self.verticalLayout_218.setSpacing(0)
        self.verticalLayout_218.setObjectName(u"verticalLayout_218")
        self.verticalLayout_218.setContentsMargins(0, 6, 0, 0)
        self.change_ip = QPushButton(self.frame_242)
        self.change_ip.setObjectName(u"change_ip")
        self.change_ip.setMinimumSize(QSize(100, 0))
        self.change_ip.setFont(font4)
        self.change_ip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_218.addWidget(self.change_ip)


        self.verticalLayout_216.addWidget(self.frame_242, 0, Qt.AlignRight)


        self.verticalLayout_215.addWidget(self.frame_240)


        self.verticalLayout_69.addWidget(self.frame_238)

        self.frame_button_3 = QFrame(self.form_3)
        self.frame_button_3.setObjectName(u"frame_button_3")
        self.frame_button_3.setFrameShape(QFrame.StyledPanel)
        self.frame_button_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_157 = QHBoxLayout(self.frame_button_3)
        self.horizontalLayout_157.setObjectName(u"horizontalLayout_157")
        self.horizontalLayout_157.setContentsMargins(0, 9, 0, -1)
        self.btn_connexion = QPushButton(self.frame_button_3)
        self.btn_connexion.setObjectName(u"btn_connexion")
        self.btn_connexion.setEnabled(True)
        self.btn_connexion.setFont(font)
        self.btn_connexion.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_connexion.setFlat(True)

        self.horizontalLayout_157.addWidget(self.btn_connexion)


        self.verticalLayout_69.addWidget(self.frame_button_3)


        self.horizontalLayout_153.addWidget(self.form_3)


        self.verticalLayout_68.addWidget(self.frame_130)


        self.horizontalLayout_151.addWidget(self.frame_129)


        self.verticalLayout_3.addWidget(self.connexion_3, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_2.addWidget(self.body_connect)

        self.verticalSpacer_2 = QSpacerItem(20, 157, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.main_with_shadow.addWidget(self.connexion_page)
        self.shadow_windowPage1 = QWidget()
        self.shadow_windowPage1.setObjectName(u"shadow_windowPage1")
        self.shadow_windowPage1.setMinimumSize(QSize(0, 0))
        self.shadow_windowPage1.setStyleSheet(u"")
        self.horizontalLayout_4 = QHBoxLayout(self.shadow_windowPage1)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.leftmenu = QWidget(self.shadow_windowPage1)
        self.leftmenu.setObjectName(u"leftmenu")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(3)
        sizePolicy2.setHeightForWidth(self.leftmenu.sizePolicy().hasHeightForWidth())
        self.leftmenu.setSizePolicy(sizePolicy2)
        self.leftmenu.setMinimumSize(QSize(180, 0))
        self.verticalLayout_7 = QVBoxLayout(self.leftmenu)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.left_frame = QFrame(self.leftmenu)
        self.left_frame.setObjectName(u"left_frame")
        self.left_frame.setMinimumSize(QSize(180, 0))
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.left_frame)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.left_frame)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(50, 50))
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 5, 0, 0)
        self.logo_2 = QLabel(self.frame_5)
        self.logo_2.setObjectName(u"logo_2")
        self.logo_2.setMinimumSize(QSize(50, 50))
        self.logo_2.setFont(font1)
        self.logo_2.setPixmap(QPixmap(u"../../../../../../.designer/assets/icons/icons8-b\u00e2timent-scolaire-64.png"))

        self.horizontalLayout_12.addWidget(self.logo_2)


        self.verticalLayout_12.addWidget(self.frame_5, 0, Qt.AlignHCenter)

        self.frame_7 = QFrame(self.left_frame)
        self.frame_7.setObjectName(u"frame_7")
        sizePolicy.setHeightForWidth(self.frame_7.sizePolicy().hasHeightForWidth())
        self.frame_7.setSizePolicy(sizePolicy)
        self.frame_7.setMinimumSize(QSize(180, 0))
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_7)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.frame_6 = QFrame(self.frame_7)
        self.frame_6.setObjectName(u"frame_6")
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setMinimumSize(QSize(166, 0))
        self.frame_6.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.frame_6.setStyleSheet(u"")
        self.frame_6.setFrameShape(QFrame.Box)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.frame_6)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.btn_left_home = QPushButton(self.frame_6)
        self.btn_left_home.setObjectName(u"btn_left_home")
        self.btn_left_home.setMinimumSize(QSize(180, 34))
        self.btn_left_home.setMaximumSize(QSize(16777215, 16777215))
        font5 = QFont()
        font5.setFamilies([u"Inter"])
        font5.setPointSize(13)
        font5.setBold(False)
        self.btn_left_home.setFont(font5)
        self.btn_left_home.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_home.setCheckable(True)
        self.btn_left_home.setChecked(True)
        self.btn_left_home.setAutoRepeat(False)
        self.btn_left_home.setAutoExclusive(True)
        self.btn_left_home.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_home)

        self.btn_left_admin = QPushButton(self.frame_6)
        self.btn_left_admin.setObjectName(u"btn_left_admin")
        self.btn_left_admin.setMinimumSize(QSize(180, 34))
        self.btn_left_admin.setFont(font5)
        self.btn_left_admin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_admin.setAutoFillBackground(False)
        self.btn_left_admin.setCheckable(True)
        self.btn_left_admin.setAutoExclusive(True)
        self.btn_left_admin.setAutoDefault(False)
        self.btn_left_admin.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_admin)

        self.btn_left_etudiant = QPushButton(self.frame_6)
        self.btn_left_etudiant.setObjectName(u"btn_left_etudiant")
        self.btn_left_etudiant.setMinimumSize(QSize(180, 34))
        self.btn_left_etudiant.setMaximumSize(QSize(100, 16777215))
        self.btn_left_etudiant.setFont(font5)
        self.btn_left_etudiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_etudiant.setCheckable(True)
        self.btn_left_etudiant.setAutoExclusive(True)
        self.btn_left_etudiant.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_etudiant)

        self.btn_left_promus = QPushButton(self.frame_6)
        self.btn_left_promus.setObjectName(u"btn_left_promus")
        self.btn_left_promus.setEnabled(True)
        self.btn_left_promus.setMinimumSize(QSize(180, 34))
        self.btn_left_promus.setMaximumSize(QSize(16777215, 16777215))
        self.btn_left_promus.setFont(font5)
        self.btn_left_promus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_promus.setCheckable(True)
        self.btn_left_promus.setAutoExclusive(True)
        self.btn_left_promus.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_promus)

        self.btn_left_prof = QPushButton(self.frame_6)
        self.btn_left_prof.setObjectName(u"btn_left_prof")
        self.btn_left_prof.setMinimumSize(QSize(180, 34))
        self.btn_left_prof.setFont(font5)
        self.btn_left_prof.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_prof.setCheckable(True)
        self.btn_left_prof.setAutoExclusive(True)
        self.btn_left_prof.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_prof)

        self.btn_left_cours = QPushButton(self.frame_6)
        self.btn_left_cours.setObjectName(u"btn_left_cours")
        self.btn_left_cours.setEnabled(True)
        self.btn_left_cours.setMinimumSize(QSize(180, 34))
        self.btn_left_cours.setFont(font5)
        self.btn_left_cours.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_cours.setText(u"Cours")
        self.btn_left_cours.setCheckable(True)
        self.btn_left_cours.setAutoExclusive(True)
        self.btn_left_cours.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_cours)

        self.btn_left_notes = QPushButton(self.frame_6)
        self.btn_left_notes.setObjectName(u"btn_left_notes")
        self.btn_left_notes.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.btn_left_notes.sizePolicy().hasHeightForWidth())
        self.btn_left_notes.setSizePolicy(sizePolicy3)
        self.btn_left_notes.setMinimumSize(QSize(0, 34))
        self.btn_left_notes.setMaximumSize(QSize(16777215, 16777215))
        self.btn_left_notes.setFont(font5)
        self.btn_left_notes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_notes.setCheckable(True)
        self.btn_left_notes.setAutoExclusive(True)
        self.btn_left_notes.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_notes)

        self.btn_left_paiement = QPushButton(self.frame_6)
        self.btn_left_paiement.setObjectName(u"btn_left_paiement")
        self.btn_left_paiement.setMinimumSize(QSize(180, 34))
        self.btn_left_paiement.setFont(font5)
        self.btn_left_paiement.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_paiement.setCheckable(True)
        self.btn_left_paiement.setAutoExclusive(True)
        self.btn_left_paiement.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_paiement)

        self.btn_left_vente = QPushButton(self.frame_6)
        self.btn_left_vente.setObjectName(u"btn_left_vente")
        self.btn_left_vente.setMinimumSize(QSize(180, 34))
        self.btn_left_vente.setFont(font5)
        self.btn_left_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_vente.setInputMethodHints(Qt.ImhSensitiveData)
        self.btn_left_vente.setCheckable(True)
        self.btn_left_vente.setAutoExclusive(True)
        self.btn_left_vente.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_vente)

        self.btn_left_rapport = QPushButton(self.frame_6)
        self.btn_left_rapport.setObjectName(u"btn_left_rapport")
        self.btn_left_rapport.setMinimumSize(QSize(180, 34))
        self.btn_left_rapport.setFont(font5)
        self.btn_left_rapport.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_rapport.setCheckable(True)
        self.btn_left_rapport.setAutoExclusive(True)
        self.btn_left_rapport.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_rapport)

        self.btn_left_profile = QPushButton(self.frame_6)
        self.btn_left_profile.setObjectName(u"btn_left_profile")
        self.btn_left_profile.setMinimumSize(QSize(180, 34))
        self.btn_left_profile.setFont(font4)
        self.btn_left_profile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_profile.setCheckable(True)
        self.btn_left_profile.setAutoExclusive(True)
        self.btn_left_profile.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_profile)

        self.btn_left_deconnexion = QPushButton(self.frame_6)
        self.btn_left_deconnexion.setObjectName(u"btn_left_deconnexion")
        self.btn_left_deconnexion.setMinimumSize(QSize(180, 34))
        self.btn_left_deconnexion.setFont(font5)
        self.btn_left_deconnexion.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_left_deconnexion.setCheckable(True)
        self.btn_left_deconnexion.setAutoExclusive(True)
        self.btn_left_deconnexion.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_left_deconnexion)

        self.verticalSpacer_3 = QSpacerItem(20, 70, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_3)

        self.verticalSpacer_4 = QSpacerItem(20, 200, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_4)

        self.btn_settings = QPushButton(self.frame_6)
        self.btn_settings.setObjectName(u"btn_settings")
        self.btn_settings.setMinimumSize(QSize(180, 35))
        self.btn_settings.setFont(font5)
        self.btn_settings.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(u"../../../../../../.designer/assets/icons/settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_settings.setIcon(icon3)
        self.btn_settings.setIconSize(QSize(25, 25))
        self.btn_settings.setCheckable(True)
        self.btn_settings.setAutoExclusive(True)
        self.btn_settings.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_settings)

        self.btn_log = QPushButton(self.frame_6)
        self.btn_log.setObjectName(u"btn_log")
        self.btn_log.setMinimumSize(QSize(180, 35))
        self.btn_log.setFont(font4)
        self.btn_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_9.addWidget(self.btn_log)

        self.btn_actualiser = QPushButton(self.frame_6)
        self.btn_actualiser.setObjectName(u"btn_actualiser")
        self.btn_actualiser.setMinimumSize(QSize(180, 35))
        self.btn_actualiser.setFont(font4)
        self.btn_actualiser.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_actualiser.setCheckable(True)
        self.btn_actualiser.setFlat(True)

        self.verticalLayout_9.addWidget(self.btn_actualiser)

        self.btn_a_propos = QPushButton(self.frame_6)
        self.btn_a_propos.setObjectName(u"btn_a_propos")
        self.btn_a_propos.setMinimumSize(QSize(180, 35))
        self.btn_a_propos.setFont(font4)
        self.btn_a_propos.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_9.addWidget(self.btn_a_propos)


        self.verticalLayout_17.addWidget(self.frame_6, 0, Qt.AlignVCenter)

        self.frame_59 = QFrame(self.frame_7)
        self.frame_59.setObjectName(u"frame_59")
        self.frame_59.setFrameShape(QFrame.StyledPanel)
        self.frame_59.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_68 = QHBoxLayout(self.frame_59)
        self.horizontalLayout_68.setObjectName(u"horizontalLayout_68")
        self.horizontalLayout_68.setContentsMargins(0, 0, 0, 10)
        self.frame_60 = QFrame(self.frame_59)
        self.frame_60.setObjectName(u"frame_60")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame_60.sizePolicy().hasHeightForWidth())
        self.frame_60.setSizePolicy(sizePolicy4)
        self.frame_60.setFrameShape(QFrame.StyledPanel)
        self.frame_60.setFrameShadow(QFrame.Raised)
        self.verticalLayout_37 = QVBoxLayout(self.frame_60)
        self.verticalLayout_37.setSpacing(0)
        self.verticalLayout_37.setObjectName(u"verticalLayout_37")
        self.verticalLayout_37.setContentsMargins(0, 0, -1, 17)

        self.horizontalLayout_68.addWidget(self.frame_60, 0, Qt.AlignLeft)


        self.verticalLayout_17.addWidget(self.frame_59, 0, Qt.AlignLeft|Qt.AlignBottom)


        self.verticalLayout_12.addWidget(self.frame_7, 0, Qt.AlignLeft)


        self.verticalLayout_7.addWidget(self.left_frame)


        self.horizontalLayout_4.addWidget(self.leftmenu)

        self.main = QWidget(self.shadow_windowPage1)
        self.main.setObjectName(u"main")
        sizePolicy1.setHeightForWidth(self.main.sizePolicy().hasHeightForWidth())
        self.main.setSizePolicy(sizePolicy1)
        self.main.setStyleSheet(u"")
        self.verticalLayout_8 = QVBoxLayout(self.main)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame_318 = QFrame(self.main)
        self.frame_318.setObjectName(u"frame_318")
        self.frame_318.setMinimumSize(QSize(0, 40))
        self.frame_318.setMaximumSize(QSize(16777215, 40))
        self.frame_318.setFrameShape(QFrame.StyledPanel)
        self.frame_318.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_127 = QHBoxLayout(self.frame_318)
        self.horizontalLayout_127.setSpacing(50)
        self.horizontalLayout_127.setObjectName(u"horizontalLayout_127")
        self.horizontalLayout_127.setContentsMargins(0, 6, 40, 0)
        self.frame_408 = QFrame(self.frame_318)
        self.frame_408.setObjectName(u"frame_408")
        self.frame_408.setFrameShape(QFrame.StyledPanel)
        self.frame_408.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_173 = QHBoxLayout(self.frame_408)
        self.horizontalLayout_173.setSpacing(30)
        self.horizontalLayout_173.setObjectName(u"horizontalLayout_173")
        self.frame_409 = QFrame(self.frame_408)
        self.frame_409.setObjectName(u"frame_409")
        self.frame_409.setFrameShape(QFrame.StyledPanel)
        self.frame_409.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_169 = QHBoxLayout(self.frame_409)
        self.horizontalLayout_169.setSpacing(20)
        self.horizontalLayout_169.setObjectName(u"horizontalLayout_169")
        self.horizontalLayout_169.setContentsMargins(0, 0, 0, 0)
        self.label_159 = QLabel(self.frame_409)
        self.label_159.setObjectName(u"label_159")
        self.label_159.setMinimumSize(QSize(140, 0))
        self.label_159.setFont(font2)

        self.horizontalLayout_169.addWidget(self.label_159)

        self.direct_request = QRadioButton(self.frame_409)
        self.direct_request.setObjectName(u"direct_request")
        self.direct_request.setFont(font4)
        self.direct_request.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_169.addWidget(self.direct_request)


        self.horizontalLayout_173.addWidget(self.frame_409)

        self.frame_410 = QFrame(self.frame_408)
        self.frame_410.setObjectName(u"frame_410")
        self.frame_410.setFrameShape(QFrame.StyledPanel)
        self.frame_410.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_172 = QHBoxLayout(self.frame_410)
        self.horizontalLayout_172.setSpacing(20)
        self.horizontalLayout_172.setObjectName(u"horizontalLayout_172")
        self.horizontalLayout_172.setContentsMargins(0, 0, 0, 0)
        self.label_160 = QLabel(self.frame_410)
        self.label_160.setObjectName(u"label_160")
        self.label_160.setMinimumSize(QSize(170, 0))
        self.label_160.setFont(font2)

        self.horizontalLayout_172.addWidget(self.label_160)

        self.domain_or_ip = QRadioButton(self.frame_410)
        self.domain_or_ip.setObjectName(u"domain_or_ip")
        self.domain_or_ip.setFont(font4)
        self.domain_or_ip.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_172.addWidget(self.domain_or_ip)


        self.horizontalLayout_173.addWidget(self.frame_410)


        self.horizontalLayout_127.addWidget(self.frame_408)

        self.frame_350 = QFrame(self.frame_318)
        self.frame_350.setObjectName(u"frame_350")
        self.frame_350.setMinimumSize(QSize(0, 30))
        self.frame_350.setMaximumSize(QSize(16777215, 30))
        self.frame_350.setFont(font4)
        self.frame_350.setFrameShape(QFrame.StyledPanel)
        self.frame_350.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_128 = QHBoxLayout(self.frame_350)
        self.horizontalLayout_128.setSpacing(15)
        self.horizontalLayout_128.setObjectName(u"horizontalLayout_128")
        self.horizontalLayout_128.setContentsMargins(0, 0, 0, 0)
        self.label_134 = QLabel(self.frame_350)
        self.label_134.setObjectName(u"label_134")

        self.horizontalLayout_128.addWidget(self.label_134)

        self.combo_anne_for_dash = QComboBox(self.frame_350)
        self.combo_anne_for_dash.setObjectName(u"combo_anne_for_dash")
        self.combo_anne_for_dash.setMinimumSize(QSize(200, 37))
        self.combo_anne_for_dash.setMaximumSize(QSize(16777215, 37))
        self.combo_anne_for_dash.setFont(font2)
        self.combo_anne_for_dash.setDuplicatesEnabled(False)

        self.horizontalLayout_128.addWidget(self.combo_anne_for_dash)


        self.horizontalLayout_127.addWidget(self.frame_350, 0, Qt.AlignHCenter)

        self.user_email = QLabel(self.frame_318)
        self.user_email.setObjectName(u"user_email")

        self.horizontalLayout_127.addWidget(self.user_email)


        self.verticalLayout_8.addWidget(self.frame_318, 0, Qt.AlignRight)

        self.stackedWidget = QStackedWidget(self.main)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.dash_page = QWidget()
        self.dash_page.setObjectName(u"dash_page")
        self.verticalLayout_14 = QVBoxLayout(self.dash_page)
        self.verticalLayout_14.setSpacing(9)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(-1, 0, -1, -1)
        self.frame_53 = QFrame(self.dash_page)
        self.frame_53.setObjectName(u"frame_53")
        self.frame_53.setMaximumSize(QSize(16777215, 200))
        self.frame_53.setFrameShape(QFrame.StyledPanel)
        self.frame_53.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_34 = QHBoxLayout(self.frame_53)
        self.horizontalLayout_34.setSpacing(20)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.etudiant_dash = QWidget(self.frame_53)
        self.etudiant_dash.setObjectName(u"etudiant_dash")
        self.etudiant_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_15 = QVBoxLayout(self.etudiant_dash)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.frame_4 = QFrame(self.etudiant_dash)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.frame_4)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_etudiant_dash = QLabel(self.frame_4)
        self.label_etudiant_dash.setObjectName(u"label_etudiant_dash")

        self.horizontalLayout_20.addWidget(self.label_etudiant_dash)

        self.btn_plus_eudiant = QPushButton(self.frame_4)
        self.btn_plus_eudiant.setObjectName(u"btn_plus_eudiant")
        self.btn_plus_eudiant.setMaximumSize(QSize(35, 22))
        self.btn_plus_eudiant.setFont(font5)
        self.btn_plus_eudiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_eudiant.setFlat(True)

        self.horizontalLayout_20.addWidget(self.btn_plus_eudiant)


        self.verticalLayout_15.addWidget(self.frame_4)

        self.frame_8 = QFrame(self.etudiant_dash)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_21 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_etudiant_dash = QLabel(self.frame_8)
        self.label_icon_etudiant_dash.setObjectName(u"label_icon_etudiant_dash")

        self.horizontalLayout_21.addWidget(self.label_icon_etudiant_dash)

        self.label_number_etudiant = QLabel(self.frame_8)
        self.label_number_etudiant.setObjectName(u"label_number_etudiant")

        self.horizontalLayout_21.addWidget(self.label_number_etudiant, 0, Qt.AlignRight)


        self.verticalLayout_15.addWidget(self.frame_8)


        self.horizontalLayout_34.addWidget(self.etudiant_dash)

        self.professeur_dash = QWidget(self.frame_53)
        self.professeur_dash.setObjectName(u"professeur_dash")
        self.professeur_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_201 = QVBoxLayout(self.professeur_dash)
        self.verticalLayout_201.setObjectName(u"verticalLayout_201")
        self.frame_211 = QFrame(self.professeur_dash)
        self.frame_211.setObjectName(u"frame_211")
        self.frame_211.setFrameShape(QFrame.StyledPanel)
        self.frame_211.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_57 = QHBoxLayout(self.frame_211)
        self.horizontalLayout_57.setObjectName(u"horizontalLayout_57")
        self.label_professeur = QLabel(self.frame_211)
        self.label_professeur.setObjectName(u"label_professeur")

        self.horizontalLayout_57.addWidget(self.label_professeur)

        self.btn_plus_professeur = QPushButton(self.frame_211)
        self.btn_plus_professeur.setObjectName(u"btn_plus_professeur")
        self.btn_plus_professeur.setMaximumSize(QSize(35, 22))
        self.btn_plus_professeur.setFont(font4)
        self.btn_plus_professeur.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_professeur.setFlat(True)

        self.horizontalLayout_57.addWidget(self.btn_plus_professeur)


        self.verticalLayout_201.addWidget(self.frame_211)

        self.frame_210 = QFrame(self.professeur_dash)
        self.frame_210.setObjectName(u"frame_210")
        self.frame_210.setFrameShape(QFrame.StyledPanel)
        self.frame_210.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_53 = QHBoxLayout(self.frame_210)
        self.horizontalLayout_53.setObjectName(u"horizontalLayout_53")
        self.horizontalLayout_53.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_professeur = QLabel(self.frame_210)
        self.label_icon_professeur.setObjectName(u"label_icon_professeur")

        self.horizontalLayout_53.addWidget(self.label_icon_professeur)

        self.label_number_professeur = QLabel(self.frame_210)
        self.label_number_professeur.setObjectName(u"label_number_professeur")

        self.horizontalLayout_53.addWidget(self.label_number_professeur, 0, Qt.AlignRight)


        self.verticalLayout_201.addWidget(self.frame_210)


        self.horizontalLayout_34.addWidget(self.professeur_dash)

        self.personnel_dash = QWidget(self.frame_53)
        self.personnel_dash.setObjectName(u"personnel_dash")
        self.personnel_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_200 = QVBoxLayout(self.personnel_dash)
        self.verticalLayout_200.setObjectName(u"verticalLayout_200")
        self.frame_213 = QFrame(self.personnel_dash)
        self.frame_213.setObjectName(u"frame_213")
        self.frame_213.setFrameShape(QFrame.StyledPanel)
        self.frame_213.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_62 = QHBoxLayout(self.frame_213)
        self.horizontalLayout_62.setObjectName(u"horizontalLayout_62")
        self.label_personnel_dash = QLabel(self.frame_213)
        self.label_personnel_dash.setObjectName(u"label_personnel_dash")

        self.horizontalLayout_62.addWidget(self.label_personnel_dash)

        self.btn_plus_personnel = QPushButton(self.frame_213)
        self.btn_plus_personnel.setObjectName(u"btn_plus_personnel")
        self.btn_plus_personnel.setMinimumSize(QSize(10, 0))
        self.btn_plus_personnel.setMaximumSize(QSize(35, 22))
        self.btn_plus_personnel.setFont(font4)
        self.btn_plus_personnel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_personnel.setFlat(True)

        self.horizontalLayout_62.addWidget(self.btn_plus_personnel, 0, Qt.AlignRight)


        self.verticalLayout_200.addWidget(self.frame_213)

        self.frame_212 = QFrame(self.personnel_dash)
        self.frame_212.setObjectName(u"frame_212")
        self.frame_212.setFrameShape(QFrame.StyledPanel)
        self.frame_212.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_58 = QHBoxLayout(self.frame_212)
        self.horizontalLayout_58.setObjectName(u"horizontalLayout_58")
        self.horizontalLayout_58.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_personnel = QLabel(self.frame_212)
        self.label_icon_personnel.setObjectName(u"label_icon_personnel")

        self.horizontalLayout_58.addWidget(self.label_icon_personnel)

        self.label_number_personnel = QLabel(self.frame_212)
        self.label_number_personnel.setObjectName(u"label_number_personnel")

        self.horizontalLayout_58.addWidget(self.label_number_personnel, 0, Qt.AlignRight)


        self.verticalLayout_200.addWidget(self.frame_212)


        self.horizontalLayout_34.addWidget(self.personnel_dash)

        self.classe_dash = QWidget(self.frame_53)
        self.classe_dash.setObjectName(u"classe_dash")
        self.classe_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_202 = QVBoxLayout(self.classe_dash)
        self.verticalLayout_202.setObjectName(u"verticalLayout_202")
        self.frame_215 = QFrame(self.classe_dash)
        self.frame_215.setObjectName(u"frame_215")
        self.frame_215.setFrameShape(QFrame.StyledPanel)
        self.frame_215.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_64 = QHBoxLayout(self.frame_215)
        self.horizontalLayout_64.setObjectName(u"horizontalLayout_64")
        self.label_classe_dash = QLabel(self.frame_215)
        self.label_classe_dash.setObjectName(u"label_classe_dash")

        self.horizontalLayout_64.addWidget(self.label_classe_dash)

        self.btn_plus_classe = QPushButton(self.frame_215)
        self.btn_plus_classe.setObjectName(u"btn_plus_classe")
        self.btn_plus_classe.setMaximumSize(QSize(35, 22))
        self.btn_plus_classe.setFont(font4)
        self.btn_plus_classe.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_classe.setCheckable(True)
        self.btn_plus_classe.setFlat(True)

        self.horizontalLayout_64.addWidget(self.btn_plus_classe, 0, Qt.AlignRight)


        self.verticalLayout_202.addWidget(self.frame_215)

        self.frame_214 = QFrame(self.classe_dash)
        self.frame_214.setObjectName(u"frame_214")
        self.frame_214.setFrameShape(QFrame.StyledPanel)
        self.frame_214.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_63 = QHBoxLayout(self.frame_214)
        self.horizontalLayout_63.setObjectName(u"horizontalLayout_63")
        self.horizontalLayout_63.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_classe_dash = QLabel(self.frame_214)
        self.label_icon_classe_dash.setObjectName(u"label_icon_classe_dash")

        self.horizontalLayout_63.addWidget(self.label_icon_classe_dash)

        self.label_number_classe_dash = QLabel(self.frame_214)
        self.label_number_classe_dash.setObjectName(u"label_number_classe_dash")

        self.horizontalLayout_63.addWidget(self.label_number_classe_dash, 0, Qt.AlignRight)


        self.verticalLayout_202.addWidget(self.frame_214)


        self.horizontalLayout_34.addWidget(self.classe_dash)


        self.verticalLayout_14.addWidget(self.frame_53, 0, Qt.AlignTop)

        self.frame_3 = QFrame(self.dash_page)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 80))
        self.frame_3.setMaximumSize(QSize(16777215, 200))
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_19.setSpacing(20)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(-1, -1, -1, 50)
        self.notes_dash = QWidget(self.frame_3)
        self.notes_dash.setObjectName(u"notes_dash")
        self.notes_dash.setMinimumSize(QSize(0, 95))
        self.notes_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_196 = QVBoxLayout(self.notes_dash)
        self.verticalLayout_196.setObjectName(u"verticalLayout_196")
        self.frame_221 = QFrame(self.notes_dash)
        self.frame_221.setObjectName(u"frame_221")
        self.frame_221.setFrameShape(QFrame.StyledPanel)
        self.frame_221.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_85 = QHBoxLayout(self.frame_221)
        self.horizontalLayout_85.setObjectName(u"horizontalLayout_85")
        self.label_notes_2 = QLabel(self.frame_221)
        self.label_notes_2.setObjectName(u"label_notes_2")

        self.horizontalLayout_85.addWidget(self.label_notes_2)

        self.btn_plus_notes = QPushButton(self.frame_221)
        self.btn_plus_notes.setObjectName(u"btn_plus_notes")
        self.btn_plus_notes.setMaximumSize(QSize(35, 22))
        self.btn_plus_notes.setFont(font4)
        self.btn_plus_notes.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_notes.setFlat(True)

        self.horizontalLayout_85.addWidget(self.btn_plus_notes)


        self.verticalLayout_196.addWidget(self.frame_221)

        self.frame_220 = QFrame(self.notes_dash)
        self.frame_220.setObjectName(u"frame_220")
        self.frame_220.setFrameShape(QFrame.StyledPanel)
        self.frame_220.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_84 = QHBoxLayout(self.frame_220)
        self.horizontalLayout_84.setObjectName(u"horizontalLayout_84")
        self.horizontalLayout_84.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_notes = QLabel(self.frame_220)
        self.label_icon_notes.setObjectName(u"label_icon_notes")

        self.horizontalLayout_84.addWidget(self.label_icon_notes)

        self.label_number_notes = QLabel(self.frame_220)
        self.label_number_notes.setObjectName(u"label_number_notes")

        self.horizontalLayout_84.addWidget(self.label_number_notes, 0, Qt.AlignRight)


        self.verticalLayout_196.addWidget(self.frame_220)


        self.horizontalLayout_19.addWidget(self.notes_dash)

        self.paiement_dash = QWidget(self.frame_3)
        self.paiement_dash.setObjectName(u"paiement_dash")
        self.paiement_dash.setMinimumSize(QSize(0, 95))
        self.paiement_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_198 = QVBoxLayout(self.paiement_dash)
        self.verticalLayout_198.setObjectName(u"verticalLayout_198")
        self.frame_219 = QFrame(self.paiement_dash)
        self.frame_219.setObjectName(u"frame_219")
        self.frame_219.setFrameShape(QFrame.StyledPanel)
        self.frame_219.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_83 = QHBoxLayout(self.frame_219)
        self.horizontalLayout_83.setObjectName(u"horizontalLayout_83")
        self.label_paiement_2 = QLabel(self.frame_219)
        self.label_paiement_2.setObjectName(u"label_paiement_2")

        self.horizontalLayout_83.addWidget(self.label_paiement_2)

        self.btn_plus_paiement = QPushButton(self.frame_219)
        self.btn_plus_paiement.setObjectName(u"btn_plus_paiement")
        self.btn_plus_paiement.setMaximumSize(QSize(35, 22))
        self.btn_plus_paiement.setFont(font4)
        self.btn_plus_paiement.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_paiement.setFlat(True)

        self.horizontalLayout_83.addWidget(self.btn_plus_paiement)


        self.verticalLayout_198.addWidget(self.frame_219)

        self.frame_218 = QFrame(self.paiement_dash)
        self.frame_218.setObjectName(u"frame_218")
        self.frame_218.setFrameShape(QFrame.StyledPanel)
        self.frame_218.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_67 = QHBoxLayout(self.frame_218)
        self.horizontalLayout_67.setObjectName(u"horizontalLayout_67")
        self.horizontalLayout_67.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_paiement = QLabel(self.frame_218)
        self.label_icon_paiement.setObjectName(u"label_icon_paiement")

        self.horizontalLayout_67.addWidget(self.label_icon_paiement)

        self.label_number_paiement = QLabel(self.frame_218)
        self.label_number_paiement.setObjectName(u"label_number_paiement")

        self.horizontalLayout_67.addWidget(self.label_number_paiement, 0, Qt.AlignRight)


        self.verticalLayout_198.addWidget(self.frame_218)


        self.horizontalLayout_19.addWidget(self.paiement_dash)

        self.cours_dash = QWidget(self.frame_3)
        self.cours_dash.setObjectName(u"cours_dash")
        self.cours_dash.setMinimumSize(QSize(0, 95))
        self.cours_dash.setMaximumSize(QSize(16777215, 95))
        self.verticalLayout_199 = QVBoxLayout(self.cours_dash)
        self.verticalLayout_199.setObjectName(u"verticalLayout_199")
        self.frame_217 = QFrame(self.cours_dash)
        self.frame_217.setObjectName(u"frame_217")
        self.frame_217.setFrameShape(QFrame.StyledPanel)
        self.frame_217.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_66 = QHBoxLayout(self.frame_217)
        self.horizontalLayout_66.setObjectName(u"horizontalLayout_66")
        self.label_cours = QLabel(self.frame_217)
        self.label_cours.setObjectName(u"label_cours")

        self.horizontalLayout_66.addWidget(self.label_cours)

        self.btn_plus_cours = QPushButton(self.frame_217)
        self.btn_plus_cours.setObjectName(u"btn_plus_cours")
        self.btn_plus_cours.setMaximumSize(QSize(35, 22))
        self.btn_plus_cours.setFont(font4)
        self.btn_plus_cours.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_plus_cours.setFlat(True)

        self.horizontalLayout_66.addWidget(self.btn_plus_cours)


        self.verticalLayout_199.addWidget(self.frame_217)

        self.frame_216 = QFrame(self.cours_dash)
        self.frame_216.setObjectName(u"frame_216")
        self.frame_216.setFrameShape(QFrame.StyledPanel)
        self.frame_216.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_65 = QHBoxLayout(self.frame_216)
        self.horizontalLayout_65.setObjectName(u"horizontalLayout_65")
        self.horizontalLayout_65.setContentsMargins(-1, 0, -1, 0)
        self.label_icon_cours = QLabel(self.frame_216)
        self.label_icon_cours.setObjectName(u"label_icon_cours")

        self.horizontalLayout_65.addWidget(self.label_icon_cours)

        self.label_number_cours = QLabel(self.frame_216)
        self.label_number_cours.setObjectName(u"label_number_cours")

        self.horizontalLayout_65.addWidget(self.label_number_cours, 0, Qt.AlignRight)


        self.verticalLayout_199.addWidget(self.frame_216)


        self.horizontalLayout_19.addWidget(self.cours_dash)

        self.classe_dash_2 = QWidget(self.frame_3)
        self.classe_dash_2.setObjectName(u"classe_dash_2")

        self.horizontalLayout_19.addWidget(self.classe_dash_2)


        self.verticalLayout_14.addWidget(self.frame_3, 0, Qt.AlignTop)

        self.frame_chart_408 = QFrame(self.dash_page)
        self.frame_chart_408.setObjectName(u"frame_chart_408")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.frame_chart_408.sizePolicy().hasHeightForWidth())
        self.frame_chart_408.setSizePolicy(sizePolicy5)
        self.frame_chart_408.setMinimumSize(QSize(0, 0))
        self.frame_chart_408.setMaximumSize(QSize(16777215, 16777215))
        self.frame_chart_408.setFrameShape(QFrame.StyledPanel)
        self.frame_chart_408.setFrameShadow(QFrame.Raised)
        self.verticalLayout_352 = QVBoxLayout(self.frame_chart_408)
        self.verticalLayout_352.setObjectName(u"verticalLayout_352")
        self.verticalLayout_352.setContentsMargins(-1, 9, -1, 9)
        self.frame_chart = QFrame(self.frame_chart_408)
        self.frame_chart.setObjectName(u"frame_chart")
        sizePolicy5.setHeightForWidth(self.frame_chart.sizePolicy().hasHeightForWidth())
        self.frame_chart.setSizePolicy(sizePolicy5)
        self.frame_chart.setFrameShape(QFrame.StyledPanel)
        self.frame_chart.setFrameShadow(QFrame.Raised)
        self.verticalLayout_353 = QVBoxLayout(self.frame_chart)
        self.verticalLayout_353.setSpacing(0)
        self.verticalLayout_353.setObjectName(u"verticalLayout_353")
        self.verticalLayout_353.setContentsMargins(0, 9, 0, 0)

        self.verticalLayout_352.addWidget(self.frame_chart)


        self.verticalLayout_14.addWidget(self.frame_chart_408)

        self.frame_2 = QFrame(self.dash_page)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_295 = QVBoxLayout(self.frame_2)
        self.verticalLayout_295.setSpacing(0)
        self.verticalLayout_295.setObjectName(u"verticalLayout_295")
        self.verticalLayout_295.setContentsMargins(-1, -1, -1, 9)
        self.table_show_number_student = QTableWidget(self.frame_2)
        self.table_show_number_student.setObjectName(u"table_show_number_student")

        self.verticalLayout_295.addWidget(self.table_show_number_student)


        self.verticalLayout_14.addWidget(self.frame_2)

        self.stackedWidget.addWidget(self.dash_page)
        self.ABadge = QWidget()
        self.ABadge.setObjectName(u"ABadge")
        self.verticalLayout_239 = QVBoxLayout(self.ABadge)
        self.verticalLayout_239.setObjectName(u"verticalLayout_239")
        self.verticalLayout_239.setContentsMargins(-1, 0, -1, 10)
        self.widget_18 = QWidget(self.ABadge)
        self.widget_18.setObjectName(u"widget_18")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_18)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.frame_108 = QFrame(self.widget_18)
        self.frame_108.setObjectName(u"frame_108")
        self.frame_108.setMinimumSize(QSize(521, 279))
        self.frame_108.setMaximumSize(QSize(521, 279))
        self.frame_108.setFont(font4)
        self.frame_108.setFrameShape(QFrame.StyledPanel)
        self.frame_108.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_108)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(-1, 0, -1, -1)
        self.frame_110 = QFrame(self.frame_108)
        self.frame_110.setObjectName(u"frame_110")
        self.frame_110.setMinimumSize(QSize(150, 200))
        self.frame_110.setMaximumSize(QSize(200, 200))
        self.frame_110.setFrameShape(QFrame.StyledPanel)
        self.frame_110.setFrameShadow(QFrame.Raised)
        self.verticalLayout_240 = QVBoxLayout(self.frame_110)
        self.verticalLayout_240.setSpacing(0)
        self.verticalLayout_240.setObjectName(u"verticalLayout_240")
        self.verticalLayout_240.setContentsMargins(0, 0, 0, 0)
        self.frame_387 = QFrame(self.frame_110)
        self.frame_387.setObjectName(u"frame_387")
        self.frame_387.setFrameShape(QFrame.StyledPanel)
        self.frame_387.setFrameShadow(QFrame.Raised)
        self.verticalLayout_337 = QVBoxLayout(self.frame_387)
        self.verticalLayout_337.setObjectName(u"verticalLayout_337")
        self.verticalLayout_337.setContentsMargins(40, -1, -1, 15)
        self.image_path = QLabel(self.frame_387)
        self.image_path.setObjectName(u"image_path")
        sizePolicy.setHeightForWidth(self.image_path.sizePolicy().hasHeightForWidth())
        self.image_path.setSizePolicy(sizePolicy)
        self.image_path.setMinimumSize(QSize(120, 119))
        self.image_path.setMaximumSize(QSize(120, 119))

        self.verticalLayout_337.addWidget(self.image_path)


        self.verticalLayout_240.addWidget(self.frame_387)

        self.frame_351 = QFrame(self.frame_110)
        self.frame_351.setObjectName(u"frame_351")
        self.frame_351.setFrameShape(QFrame.StyledPanel)
        self.frame_351.setFrameShadow(QFrame.Raised)
        self.verticalLayout_284 = QVBoxLayout(self.frame_351)
        self.verticalLayout_284.setSpacing(0)
        self.verticalLayout_284.setObjectName(u"verticalLayout_284")
        self.verticalLayout_284.setContentsMargins(15, 0, 0, 16)
        self.student_identifiant = QLabel(self.frame_351)
        self.student_identifiant.setObjectName(u"student_identifiant")

        self.verticalLayout_284.addWidget(self.student_identifiant)


        self.verticalLayout_240.addWidget(self.frame_351, 0, Qt.AlignBottom)


        self.horizontalLayout_6.addWidget(self.frame_110)

        self.frame_111 = QFrame(self.frame_108)
        self.frame_111.setObjectName(u"frame_111")
        sizePolicy1.setHeightForWidth(self.frame_111.sizePolicy().hasHeightForWidth())
        self.frame_111.setSizePolicy(sizePolicy1)
        self.frame_111.setFrameShape(QFrame.StyledPanel)
        self.frame_111.setFrameShadow(QFrame.Raised)
        self.verticalLayout_241 = QVBoxLayout(self.frame_111)
        self.verticalLayout_241.setSpacing(0)
        self.verticalLayout_241.setObjectName(u"verticalLayout_241")
        self.verticalLayout_241.setContentsMargins(0, 0, 0, 0)
        self.frame_113 = QFrame(self.frame_111)
        self.frame_113.setObjectName(u"frame_113")
        self.frame_113.setFrameShape(QFrame.StyledPanel)
        self.frame_113.setFrameShadow(QFrame.Raised)
        self.verticalLayout_243 = QVBoxLayout(self.frame_113)
        self.verticalLayout_243.setObjectName(u"verticalLayout_243")
        self.verticalLayout_243.setContentsMargins(0, 0, 0, 0)
        self.label_45 = QLabel(self.frame_113)
        self.label_45.setObjectName(u"label_45")

        self.verticalLayout_243.addWidget(self.label_45, 0, Qt.AlignHCenter)


        self.verticalLayout_241.addWidget(self.frame_113, 0, Qt.AlignTop)

        self.frame_114 = QFrame(self.frame_111)
        self.frame_114.setObjectName(u"frame_114")
        self.frame_114.setFrameShape(QFrame.StyledPanel)
        self.frame_114.setFrameShadow(QFrame.Raised)
        self.verticalLayout_242 = QVBoxLayout(self.frame_114)
        self.verticalLayout_242.setSpacing(0)
        self.verticalLayout_242.setObjectName(u"verticalLayout_242")
        self.verticalLayout_242.setContentsMargins(0, 0, 0, 0)
        self.full_name = QLabel(self.frame_114)
        self.full_name.setObjectName(u"full_name")

        self.verticalLayout_242.addWidget(self.full_name)

        self.classe = QLabel(self.frame_114)
        self.classe.setObjectName(u"classe")

        self.verticalLayout_242.addWidget(self.classe, 0, Qt.AlignHCenter)


        self.verticalLayout_241.addWidget(self.frame_114, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_115 = QFrame(self.frame_111)
        self.frame_115.setObjectName(u"frame_115")
        self.frame_115.setFrameShape(QFrame.StyledPanel)
        self.frame_115.setFrameShadow(QFrame.Raised)
        self.verticalLayout_244 = QVBoxLayout(self.frame_115)
        self.verticalLayout_244.setSpacing(7)
        self.verticalLayout_244.setObjectName(u"verticalLayout_244")
        self.verticalLayout_244.setContentsMargins(0, 0, 0, 20)
        self.frame_116 = QFrame(self.frame_115)
        self.frame_116.setObjectName(u"frame_116")
        self.frame_116.setFrameShape(QFrame.StyledPanel)
        self.frame_116.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_116)
        self.horizontalLayout_7.setSpacing(7)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.date_dexp = QLabel(self.frame_116)
        self.date_dexp.setObjectName(u"date_dexp")

        self.horizontalLayout_7.addWidget(self.date_dexp)

        self.signature = QLabel(self.frame_116)
        self.signature.setObjectName(u"signature")

        self.horizontalLayout_7.addWidget(self.signature)


        self.verticalLayout_244.addWidget(self.frame_116)

        self.frame_262 = QFrame(self.frame_115)
        self.frame_262.setObjectName(u"frame_262")
        self.frame_262.setFrameShape(QFrame.StyledPanel)
        self.frame_262.setFrameShadow(QFrame.Raised)
        self.verticalLayout_245 = QVBoxLayout(self.frame_262)
        self.verticalLayout_245.setObjectName(u"verticalLayout_245")
        self.shool_adress = QLabel(self.frame_262)
        self.shool_adress.setObjectName(u"shool_adress")

        self.verticalLayout_245.addWidget(self.shool_adress, 0, Qt.AlignHCenter)


        self.verticalLayout_244.addWidget(self.frame_262, 0, Qt.AlignBottom)


        self.verticalLayout_241.addWidget(self.frame_115)


        self.horizontalLayout_6.addWidget(self.frame_111, 0, Qt.AlignVCenter)


        self.horizontalLayout_5.addWidget(self.frame_108)

        self.frame_109 = QFrame(self.widget_18)
        self.frame_109.setObjectName(u"frame_109")
        self.frame_109.setMinimumSize(QSize(400, 0))
        self.frame_109.setMaximumSize(QSize(400, 16777215))
        self.frame_109.setFont(font4)
        self.frame_109.setFrameShape(QFrame.StyledPanel)
        self.frame_109.setFrameShadow(QFrame.Raised)
        self.verticalLayout_246 = QVBoxLayout(self.frame_109)
        self.verticalLayout_246.setObjectName(u"verticalLayout_246")
        self.frame_263 = QFrame(self.frame_109)
        self.frame_263.setObjectName(u"frame_263")
        self.frame_263.setFrameShape(QFrame.StyledPanel)
        self.frame_263.setFrameShadow(QFrame.Raised)
        self.verticalLayout_247 = QVBoxLayout(self.frame_263)
        self.verticalLayout_247.setObjectName(u"verticalLayout_247")
        self.verticalLayout_247.setContentsMargins(0, 0, 0, -1)
        self.search_for_card = QLineEdit(self.frame_263)
        self.search_for_card.setObjectName(u"search_for_card")
        self.search_for_card.setMaximumSize(QSize(16777215, 37))
        self.search_for_card.setFont(font2)

        self.verticalLayout_247.addWidget(self.search_for_card)


        self.verticalLayout_246.addWidget(self.frame_263)

        self.frame_264 = QFrame(self.frame_109)
        self.frame_264.setObjectName(u"frame_264")
        self.frame_264.setMinimumSize(QSize(0, 200))
        self.frame_264.setMaximumSize(QSize(16777215, 200))
        self.frame_264.setFrameShape(QFrame.StyledPanel)
        self.frame_264.setFrameShadow(QFrame.Raised)
        self.verticalLayout_250 = QVBoxLayout(self.frame_264)
        self.verticalLayout_250.setObjectName(u"verticalLayout_250")
        self.tableWidget_2 = QTableWidget(self.frame_264)
        self.tableWidget_2.setObjectName(u"tableWidget_2")
        self.tableWidget_2.setMinimumSize(QSize(0, 200))
        self.tableWidget_2.setMaximumSize(QSize(16777215, 200))
        self.tableWidget_2.setSortingEnabled(True)

        self.verticalLayout_250.addWidget(self.tableWidget_2)


        self.verticalLayout_246.addWidget(self.frame_264, 0, Qt.AlignTop)


        self.horizontalLayout_5.addWidget(self.frame_109)


        self.verticalLayout_239.addWidget(self.widget_18)

        self.widget_19 = QWidget(self.ABadge)
        self.widget_19.setObjectName(u"widget_19")
        self.widget_19.setMinimumSize(QSize(0, 350))
        self.horizontalLayout_9 = QHBoxLayout(self.widget_19)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.frame_265 = QFrame(self.widget_19)
        self.frame_265.setObjectName(u"frame_265")
        self.frame_265.setMinimumSize(QSize(500, 0))
        self.frame_265.setMaximumSize(QSize(500, 16777215))
        self.frame_265.setFrameShape(QFrame.StyledPanel)
        self.frame_265.setFrameShadow(QFrame.Raised)
        self.verticalLayout_249 = QVBoxLayout(self.frame_265)
        self.verticalLayout_249.setObjectName(u"verticalLayout_249")
        self.view_image = QLabel(self.frame_265)
        self.view_image.setObjectName(u"view_image")

        self.verticalLayout_249.addWidget(self.view_image, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.horizontalLayout_9.addWidget(self.frame_265)

        self.frame_266 = QFrame(self.widget_19)
        self.frame_266.setObjectName(u"frame_266")
        self.frame_266.setFrameShape(QFrame.StyledPanel)
        self.frame_266.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.frame_266)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(-1, 0, 0, 0)
        self.frame_267 = QFrame(self.frame_266)
        self.frame_267.setObjectName(u"frame_267")
        self.frame_267.setFrameShape(QFrame.StyledPanel)
        self.frame_267.setFrameShadow(QFrame.Raised)
        self.verticalLayout_248 = QVBoxLayout(self.frame_267)
        self.verticalLayout_248.setSpacing(0)
        self.verticalLayout_248.setObjectName(u"verticalLayout_248")
        self.verticalLayout_248.setContentsMargins(0, 0, 0, 0)
        self.frame_413 = QFrame(self.frame_267)
        self.frame_413.setObjectName(u"frame_413")
        self.frame_413.setMinimumSize(QSize(400, 0))
        self.frame_413.setFrameShape(QFrame.StyledPanel)
        self.frame_413.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_177 = QHBoxLayout(self.frame_413)
        self.horizontalLayout_177.setSpacing(0)
        self.horizontalLayout_177.setObjectName(u"horizontalLayout_177")
        self.horizontalLayout_177.setContentsMargins(0, 0, 0, 0)
        self.line_camera_ip_2 = QLineEdit(self.frame_413)
        self.line_camera_ip_2.setObjectName(u"line_camera_ip_2")
        self.line_camera_ip_2.setFont(font2)

        self.horizontalLayout_177.addWidget(self.line_camera_ip_2)

        self.camera_ip_2 = QPushButton(self.frame_413)
        self.camera_ip_2.setObjectName(u"camera_ip_2")
        self.camera_ip_2.setMinimumSize(QSize(100, 0))
        self.camera_ip_2.setFont(font4)
        self.camera_ip_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.camera_ip_2.setCheckable(True)

        self.horizontalLayout_177.addWidget(self.camera_ip_2)


        self.verticalLayout_248.addWidget(self.frame_413)

        self.frame_412 = QFrame(self.frame_267)
        self.frame_412.setObjectName(u"frame_412")
        self.frame_412.setFrameShape(QFrame.StyledPanel)
        self.frame_412.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_176 = QHBoxLayout(self.frame_412)
        self.horizontalLayout_176.setObjectName(u"horizontalLayout_176")
        self.horizontalLayout_176.setContentsMargins(0, 9, 0, 0)
        self.frame_389 = QFrame(self.frame_412)
        self.frame_389.setObjectName(u"frame_389")
        self.frame_389.setFrameShape(QFrame.StyledPanel)
        self.frame_389.setFrameShadow(QFrame.Raised)
        self.verticalLayout_339 = QVBoxLayout(self.frame_389)
        self.verticalLayout_339.setSpacing(0)
        self.verticalLayout_339.setObjectName(u"verticalLayout_339")
        self.verticalLayout_339.setContentsMargins(0, 0, 0, 0)
        self.label_151 = QLabel(self.frame_389)
        self.label_151.setObjectName(u"label_151")

        self.verticalLayout_339.addWidget(self.label_151)

        self.combo_template = QComboBox(self.frame_389)
        self.combo_template.setObjectName(u"combo_template")
        self.combo_template.setFont(font2)

        self.verticalLayout_339.addWidget(self.combo_template)


        self.horizontalLayout_176.addWidget(self.frame_389)

        self.frame_388 = QFrame(self.frame_412)
        self.frame_388.setObjectName(u"frame_388")
        self.frame_388.setFrameShape(QFrame.StyledPanel)
        self.frame_388.setFrameShadow(QFrame.Raised)
        self.verticalLayout_338 = QVBoxLayout(self.frame_388)
        self.verticalLayout_338.setSpacing(0)
        self.verticalLayout_338.setObjectName(u"verticalLayout_338")
        self.verticalLayout_338.setContentsMargins(0, 0, 0, 0)
        self.label_135 = QLabel(self.frame_388)
        self.label_135.setObjectName(u"label_135")

        self.verticalLayout_338.addWidget(self.label_135)

        self.combo_salle = QComboBox(self.frame_388)
        self.combo_salle.setObjectName(u"combo_salle")
        self.combo_salle.setFont(font2)

        self.verticalLayout_338.addWidget(self.combo_salle)


        self.horizontalLayout_176.addWidget(self.frame_388)


        self.verticalLayout_248.addWidget(self.frame_412)

        self.frame_271 = QFrame(self.frame_267)
        self.frame_271.setObjectName(u"frame_271")
        self.frame_271.setFrameShape(QFrame.StyledPanel)
        self.frame_271.setFrameShadow(QFrame.Raised)
        self.verticalLayout_253 = QVBoxLayout(self.frame_271)
        self.verticalLayout_253.setSpacing(7)
        self.verticalLayout_253.setObjectName(u"verticalLayout_253")
        self.verticalLayout_253.setContentsMargins(0, 9, 0, 0)
        self.frame_391 = QFrame(self.frame_271)
        self.frame_391.setObjectName(u"frame_391")
        self.frame_391.setFrameShape(QFrame.StyledPanel)
        self.frame_391.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_145 = QHBoxLayout(self.frame_391)
        self.horizontalLayout_145.setSpacing(30)
        self.horizontalLayout_145.setObjectName(u"horizontalLayout_145")
        self.horizontalLayout_145.setContentsMargins(0, 0, 0, 0)
        self.frame_392 = QFrame(self.frame_391)
        self.frame_392.setObjectName(u"frame_392")
        self.frame_392.setFrameShape(QFrame.StyledPanel)
        self.frame_392.setFrameShadow(QFrame.Raised)
        self.verticalLayout_341 = QVBoxLayout(self.frame_392)
        self.verticalLayout_341.setObjectName(u"verticalLayout_341")
        self.verticalLayout_341.setContentsMargins(0, 0, 0, 0)
        self.label_152 = QLabel(self.frame_392)
        self.label_152.setObjectName(u"label_152")

        self.verticalLayout_341.addWidget(self.label_152)

        self.camera_selector = QComboBox(self.frame_392)
        self.camera_selector.setObjectName(u"camera_selector")
        self.camera_selector.setMinimumSize(QSize(0, 37))
        self.camera_selector.setMaximumSize(QSize(16777215, 37))
        self.camera_selector.setFont(font2)

        self.verticalLayout_341.addWidget(self.camera_selector)


        self.horizontalLayout_145.addWidget(self.frame_392)

        self.stop_search_cam = QPushButton(self.frame_391)
        self.stop_search_cam.setObjectName(u"stop_search_cam")
        self.stop_search_cam.setMinimumSize(QSize(100, 0))
        self.stop_search_cam.setMaximumSize(QSize(50, 16777215))
        self.stop_search_cam.setFont(font4)
        self.stop_search_cam.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_145.addWidget(self.stop_search_cam, 0, Qt.AlignBottom)


        self.verticalLayout_253.addWidget(self.frame_391)

        self.frame_390 = QFrame(self.frame_271)
        self.frame_390.setObjectName(u"frame_390")
        self.frame_390.setFrameShape(QFrame.StyledPanel)
        self.frame_390.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_144 = QHBoxLayout(self.frame_390)
        self.horizontalLayout_144.setSpacing(20)
        self.horizontalLayout_144.setObjectName(u"horizontalLayout_144")
        self.horizontalLayout_144.setContentsMargins(0, 15, 0, 0)
        self.capture_btn = QPushButton(self.frame_390)
        self.capture_btn.setObjectName(u"capture_btn")
        self.capture_btn.setFont(font4)
        self.capture_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_144.addWidget(self.capture_btn)

        self.load_btn = QPushButton(self.frame_390)
        self.load_btn.setObjectName(u"load_btn")
        self.load_btn.setFont(font4)
        self.load_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_144.addWidget(self.load_btn)

        self.generate_btn = QPushButton(self.frame_390)
        self.generate_btn.setObjectName(u"generate_btn")
        self.generate_btn.setFont(font4)
        self.generate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_144.addWidget(self.generate_btn)


        self.verticalLayout_253.addWidget(self.frame_390)

        self.frame_460 = QFrame(self.frame_271)
        self.frame_460.setObjectName(u"frame_460")
        self.frame_460.setFrameShape(QFrame.StyledPanel)
        self.frame_460.setFrameShadow(QFrame.Raised)
        self.verticalLayout_393 = QVBoxLayout(self.frame_460)
        self.verticalLayout_393.setObjectName(u"verticalLayout_393")
        self.save_badge = QPushButton(self.frame_460)
        self.save_badge.setObjectName(u"save_badge")
        self.save_badge.setFont(font4)
        self.save_badge.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_393.addWidget(self.save_badge)


        self.verticalLayout_253.addWidget(self.frame_460)


        self.verticalLayout_248.addWidget(self.frame_271, 0, Qt.AlignTop)


        self.horizontalLayout_14.addWidget(self.frame_267, 0, Qt.AlignTop)


        self.horizontalLayout_9.addWidget(self.frame_266)


        self.verticalLayout_239.addWidget(self.widget_19)

        self.stackedWidget.addWidget(self.ABadge)
        self.admin_page = QWidget()
        self.admin_page.setObjectName(u"admin_page")
        self.verticalLayout_16 = QVBoxLayout(self.admin_page)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(-1, 0, -1, -1)
        self.admin_stacked = QStackedWidget(self.admin_page)
        self.admin_stacked.setObjectName(u"admin_stacked")
        self.index_admin = QWidget()
        self.index_admin.setObjectName(u"index_admin")
        self.verticalLayout_64 = QVBoxLayout(self.index_admin)
        self.verticalLayout_64.setObjectName(u"verticalLayout_64")
        self.verticalLayout_64.setContentsMargins(-1, 0, -1, -1)
        self.frame_56 = QFrame(self.index_admin)
        self.frame_56.setObjectName(u"frame_56")
        self.frame_56.setFrameShape(QFrame.StyledPanel)
        self.frame_56.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.frame_56)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(-1, 0, -1, 0)
        self.add_personnel = QPushButton(self.frame_56)
        self.add_personnel.setObjectName(u"add_personnel")
        self.add_personnel.setMinimumSize(QSize(170, 32))
        self.add_personnel.setFont(font4)
        self.add_personnel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_personnel.setFlat(True)

        self.horizontalLayout_18.addWidget(self.add_personnel)


        self.verticalLayout_64.addWidget(self.frame_56, 0, Qt.AlignLeft)

        self.frame_57 = QFrame(self.index_admin)
        self.frame_57.setObjectName(u"frame_57")
        self.frame_57.setMinimumSize(QSize(400, 0))
        self.frame_57.setFrameShape(QFrame.StyledPanel)
        self.frame_57.setFrameShadow(QFrame.Raised)
        self.verticalLayout_70 = QVBoxLayout(self.frame_57)
        self.verticalLayout_70.setSpacing(0)
        self.verticalLayout_70.setObjectName(u"verticalLayout_70")
        self.verticalLayout_70.setContentsMargins(0, 0, -1, 0)
        self.search_admin = QLineEdit(self.frame_57)
        self.search_admin.setObjectName(u"search_admin")

        self.verticalLayout_70.addWidget(self.search_admin)


        self.verticalLayout_64.addWidget(self.frame_57, 0, Qt.AlignRight)

        self.frame_55 = QFrame(self.index_admin)
        self.frame_55.setObjectName(u"frame_55")
        sizePolicy.setHeightForWidth(self.frame_55.sizePolicy().hasHeightForWidth())
        self.frame_55.setSizePolicy(sizePolicy)
        self.frame_55.setFrameShape(QFrame.StyledPanel)
        self.frame_55.setFrameShadow(QFrame.Raised)
        self.verticalLayout_67 = QVBoxLayout(self.frame_55)
        self.verticalLayout_67.setSpacing(0)
        self.verticalLayout_67.setObjectName(u"verticalLayout_67")
        self.verticalLayout_67.setContentsMargins(0, 0, 0, 0)
        self.admin_table = QTableWidget(self.frame_55)
        self.admin_table.setObjectName(u"admin_table")
        self.admin_table.setFont(font4)
        self.admin_table.setSortingEnabled(True)
        self.admin_table.horizontalHeader().setMinimumSectionSize(150)
        self.admin_table.horizontalHeader().setStretchLastSection(True)
        self.admin_table.verticalHeader().setVisible(False)
        self.admin_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_67.addWidget(self.admin_table)


        self.verticalLayout_64.addWidget(self.frame_55)

        self.frame = QFrame(self.index_admin)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 15))
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_35 = QHBoxLayout(self.frame)
        self.horizontalLayout_35.setSpacing(15)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.admin_prev = QPushButton(self.frame)
        self.admin_prev.setObjectName(u"admin_prev")
        self.admin_prev.setFlat(True)

        self.horizontalLayout_35.addWidget(self.admin_prev)

        self.admin_label = QLabel(self.frame)
        self.admin_label.setObjectName(u"admin_label")

        self.horizontalLayout_35.addWidget(self.admin_label)

        self.admin_next = QPushButton(self.frame)
        self.admin_next.setObjectName(u"admin_next")
        self.admin_next.setFlat(True)

        self.horizontalLayout_35.addWidget(self.admin_next)


        self.verticalLayout_64.addWidget(self.frame, 0, Qt.AlignRight|Qt.AlignBottom)

        self.admin_stacked.addWidget(self.index_admin)
        self.add_admin = QWidget()
        self.add_admin.setObjectName(u"add_admin")
        self.verticalLayout_71 = QVBoxLayout(self.add_admin)
        self.verticalLayout_71.setSpacing(0)
        self.verticalLayout_71.setObjectName(u"verticalLayout_71")
        self.verticalLayout_71.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_5 = QScrollArea(self.add_admin)
        self.scrollArea_5.setObjectName(u"scrollArea_5")
        self.scrollArea_5.setWidgetResizable(True)
        self.scrollAreaWidgetContents_8 = QWidget()
        self.scrollAreaWidgetContents_8.setObjectName(u"scrollAreaWidgetContents_8")
        self.scrollAreaWidgetContents_8.setGeometry(QRect(0, 0, 336, 564))
        self.verticalLayout_269 = QVBoxLayout(self.scrollAreaWidgetContents_8)
        self.verticalLayout_269.setSpacing(0)
        self.verticalLayout_269.setObjectName(u"verticalLayout_269")
        self.verticalLayout_269.setContentsMargins(0, 0, 0, 0)
        self.frame_58 = QFrame(self.scrollAreaWidgetContents_8)
        self.frame_58.setObjectName(u"frame_58")
        self.frame_58.setFrameShape(QFrame.StyledPanel)
        self.frame_58.setFrameShadow(QFrame.Raised)
        self.verticalLayout_72 = QVBoxLayout(self.frame_58)
        self.verticalLayout_72.setObjectName(u"verticalLayout_72")
        self.verticalLayout_72.setContentsMargins(-1, 0, -1, 0)
        self.widget_3 = QWidget(self.frame_58)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_36 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.horizontalLayout_36.setContentsMargins(-1, 0, -1, 0)
        self.frame_61 = QFrame(self.widget_3)
        self.frame_61.setObjectName(u"frame_61")
        self.frame_61.setFrameShape(QFrame.StyledPanel)
        self.frame_61.setFrameShadow(QFrame.Raised)
        self.verticalLayout_77 = QVBoxLayout(self.frame_61)
        self.verticalLayout_77.setSpacing(0)
        self.verticalLayout_77.setObjectName(u"verticalLayout_77")
        self.verticalLayout_77.setContentsMargins(-1, 0, -1, 0)
        self.frame_64 = QFrame(self.frame_61)
        self.frame_64.setObjectName(u"frame_64")
        self.frame_64.setFrameShape(QFrame.StyledPanel)
        self.frame_64.setFrameShadow(QFrame.Raised)
        self.verticalLayout_78 = QVBoxLayout(self.frame_64)
        self.verticalLayout_78.setObjectName(u"verticalLayout_78")
        self.verticalLayout_78.setContentsMargins(-1, 0, -1, 0)
        self.label_2 = QLabel(self.frame_64)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_78.addWidget(self.label_2)

        self.admin_nom = QLineEdit(self.frame_64)
        self.admin_nom.setObjectName(u"admin_nom")
        self.admin_nom.setFont(font2)
        self.admin_nom.setInputMethodHints(Qt.ImhNone)

        self.verticalLayout_78.addWidget(self.admin_nom)


        self.verticalLayout_77.addWidget(self.frame_64, 0, Qt.AlignTop)

        self.frame_65 = QFrame(self.frame_61)
        self.frame_65.setObjectName(u"frame_65")
        self.frame_65.setFrameShape(QFrame.StyledPanel)
        self.frame_65.setFrameShadow(QFrame.Raised)
        self.verticalLayout_79 = QVBoxLayout(self.frame_65)
        self.verticalLayout_79.setObjectName(u"verticalLayout_79")
        self.verticalLayout_79.setContentsMargins(-1, 0, -1, 0)
        self.label_12 = QLabel(self.frame_65)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_79.addWidget(self.label_12)

        self.admin_sexe = QLineEdit(self.frame_65)
        self.admin_sexe.setObjectName(u"admin_sexe")
        self.admin_sexe.setFont(font2)

        self.verticalLayout_79.addWidget(self.admin_sexe)


        self.verticalLayout_77.addWidget(self.frame_65, 0, Qt.AlignTop)

        self.frame_66 = QFrame(self.frame_61)
        self.frame_66.setObjectName(u"frame_66")
        self.frame_66.setFrameShape(QFrame.StyledPanel)
        self.frame_66.setFrameShadow(QFrame.Raised)
        self.verticalLayout_80 = QVBoxLayout(self.frame_66)
        self.verticalLayout_80.setObjectName(u"verticalLayout_80")
        self.verticalLayout_80.setContentsMargins(-1, 0, -1, 0)
        self.label_14 = QLabel(self.frame_66)
        self.label_14.setObjectName(u"label_14")

        self.verticalLayout_80.addWidget(self.label_14)

        self.admin_telephone = QLineEdit(self.frame_66)
        self.admin_telephone.setObjectName(u"admin_telephone")
        self.admin_telephone.setFont(font2)

        self.verticalLayout_80.addWidget(self.admin_telephone)


        self.verticalLayout_77.addWidget(self.frame_66, 0, Qt.AlignTop)


        self.horizontalLayout_36.addWidget(self.frame_61)

        self.frame_62 = QFrame(self.widget_3)
        self.frame_62.setObjectName(u"frame_62")
        self.frame_62.setFrameShape(QFrame.StyledPanel)
        self.frame_62.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_36.addWidget(self.frame_62)

        self.frame_63 = QFrame(self.widget_3)
        self.frame_63.setObjectName(u"frame_63")
        self.frame_63.setFrameShape(QFrame.StyledPanel)
        self.frame_63.setFrameShadow(QFrame.Raised)
        self.verticalLayout_73 = QVBoxLayout(self.frame_63)
        self.verticalLayout_73.setSpacing(0)
        self.verticalLayout_73.setObjectName(u"verticalLayout_73")
        self.verticalLayout_73.setContentsMargins(-1, 0, -1, 0)
        self.frame_67 = QFrame(self.frame_63)
        self.frame_67.setObjectName(u"frame_67")
        self.frame_67.setFrameShape(QFrame.StyledPanel)
        self.frame_67.setFrameShadow(QFrame.Raised)
        self.verticalLayout_74 = QVBoxLayout(self.frame_67)
        self.verticalLayout_74.setObjectName(u"verticalLayout_74")
        self.verticalLayout_74.setContentsMargins(-1, 0, -1, 0)
        self.label_16 = QLabel(self.frame_67)
        self.label_16.setObjectName(u"label_16")

        self.verticalLayout_74.addWidget(self.label_16)

        self.admin_prenom = QLineEdit(self.frame_67)
        self.admin_prenom.setObjectName(u"admin_prenom")
        self.admin_prenom.setFont(font2)

        self.verticalLayout_74.addWidget(self.admin_prenom)


        self.verticalLayout_73.addWidget(self.frame_67, 0, Qt.AlignTop)

        self.frame_68 = QFrame(self.frame_63)
        self.frame_68.setObjectName(u"frame_68")
        self.frame_68.setFrameShape(QFrame.StyledPanel)
        self.frame_68.setFrameShadow(QFrame.Raised)
        self.verticalLayout_75 = QVBoxLayout(self.frame_68)
        self.verticalLayout_75.setObjectName(u"verticalLayout_75")
        self.verticalLayout_75.setContentsMargins(-1, 0, -1, 0)
        self.label_17 = QLabel(self.frame_68)
        self.label_17.setObjectName(u"label_17")

        self.verticalLayout_75.addWidget(self.label_17)

        self.admin_email = QLineEdit(self.frame_68)
        self.admin_email.setObjectName(u"admin_email")
        self.admin_email.setFont(font2)

        self.verticalLayout_75.addWidget(self.admin_email)


        self.verticalLayout_73.addWidget(self.frame_68, 0, Qt.AlignTop)

        self.frame_69 = QFrame(self.frame_63)
        self.frame_69.setObjectName(u"frame_69")
        self.frame_69.setFrameShape(QFrame.StyledPanel)
        self.frame_69.setFrameShadow(QFrame.Raised)
        self.verticalLayout_76 = QVBoxLayout(self.frame_69)
        self.verticalLayout_76.setObjectName(u"verticalLayout_76")
        self.verticalLayout_76.setContentsMargins(-1, 0, -1, 0)
        self.label_18 = QLabel(self.frame_69)
        self.label_18.setObjectName(u"label_18")

        self.verticalLayout_76.addWidget(self.label_18)

        self.admin_adresse = QLineEdit(self.frame_69)
        self.admin_adresse.setObjectName(u"admin_adresse")
        self.admin_adresse.setFont(font2)

        self.verticalLayout_76.addWidget(self.admin_adresse)


        self.verticalLayout_73.addWidget(self.frame_69, 0, Qt.AlignTop)


        self.horizontalLayout_36.addWidget(self.frame_63)


        self.verticalLayout_72.addWidget(self.widget_3)

        self.frame_89 = QFrame(self.frame_58)
        self.frame_89.setObjectName(u"frame_89")
        self.frame_89.setFrameShape(QFrame.StyledPanel)
        self.frame_89.setFrameShadow(QFrame.Raised)
        self.verticalLayout_98 = QVBoxLayout(self.frame_89)
        self.verticalLayout_98.setObjectName(u"verticalLayout_98")
        self.verticalLayout_98.setContentsMargins(30, 0, 30, -1)
        self.label_26 = QLabel(self.frame_89)
        self.label_26.setObjectName(u"label_26")

        self.verticalLayout_98.addWidget(self.label_26)

        self.admin_role = QComboBox(self.frame_89)
        self.admin_role.setObjectName(u"admin_role")
        self.admin_role.setFont(font2)
        self.admin_role.setInputMethodHints(Qt.ImhMultiLine)

        self.verticalLayout_98.addWidget(self.admin_role)


        self.verticalLayout_72.addWidget(self.frame_89, 0, Qt.AlignTop)

        self.frame_70 = QFrame(self.frame_58)
        self.frame_70.setObjectName(u"frame_70")
        self.frame_70.setFrameShape(QFrame.StyledPanel)
        self.frame_70.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_110 = QHBoxLayout(self.frame_70)
        self.horizontalLayout_110.setSpacing(29)
        self.horizontalLayout_110.setObjectName(u"horizontalLayout_110")
        self.horizontalLayout_110.setContentsMargins(-1, -1, 40, -1)
        self.delete_admin = QPushButton(self.frame_70)
        self.delete_admin.setObjectName(u"delete_admin")
        self.delete_admin.setMinimumSize(QSize(100, 0))
        self.delete_admin.setFont(font4)
        self.delete_admin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_110.addWidget(self.delete_admin)

        self.enregistrer_admin = QPushButton(self.frame_70)
        self.enregistrer_admin.setObjectName(u"enregistrer_admin")
        self.enregistrer_admin.setMinimumSize(QSize(140, 32))
        self.enregistrer_admin.setFont(font4)
        self.enregistrer_admin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.enregistrer_admin.setFlat(True)

        self.horizontalLayout_110.addWidget(self.enregistrer_admin)


        self.verticalLayout_72.addWidget(self.frame_70, 0, Qt.AlignRight)


        self.verticalLayout_269.addWidget(self.frame_58)

        self.frame_305 = QFrame(self.scrollAreaWidgetContents_8)
        self.frame_305.setObjectName(u"frame_305")
        self.frame_305.setMinimumSize(QSize(300, 0))
        self.frame_305.setFrameShape(QFrame.StyledPanel)
        self.frame_305.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_113 = QHBoxLayout(self.frame_305)
        self.horizontalLayout_113.setObjectName(u"horizontalLayout_113")
        self.horizontalLayout_113.setContentsMargins(-1, 0, -1, -1)
        self.frame_309 = QFrame(self.frame_305)
        self.frame_309.setObjectName(u"frame_309")
        self.frame_309.setMinimumSize(QSize(400, 0))
        self.frame_309.setFrameShape(QFrame.StyledPanel)
        self.frame_309.setFrameShadow(QFrame.Raised)
        self.verticalLayout_91 = QVBoxLayout(self.frame_309)
        self.verticalLayout_91.setObjectName(u"verticalLayout_91")
        self.verticalLayout_91.setContentsMargins(-1, 0, -1, -1)
        self.label_119 = QLabel(self.frame_309)
        self.label_119.setObjectName(u"label_119")

        self.verticalLayout_91.addWidget(self.label_119, 0, Qt.AlignTop)

        self.frame_312 = QFrame(self.frame_309)
        self.frame_312.setObjectName(u"frame_312")
        self.frame_312.setFrameShape(QFrame.StyledPanel)
        self.frame_312.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_112 = QHBoxLayout(self.frame_312)
        self.horizontalLayout_112.setObjectName(u"horizontalLayout_112")
        self.admin_status = QLabel(self.frame_312)
        self.admin_status.setObjectName(u"admin_status")

        self.horizontalLayout_112.addWidget(self.admin_status)

        self.admin_change_status = QPushButton(self.frame_312)
        self.admin_change_status.setObjectName(u"admin_change_status")
        self.admin_change_status.setFont(font4)
        self.admin_change_status.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_112.addWidget(self.admin_change_status)


        self.verticalLayout_91.addWidget(self.frame_312, 0, Qt.AlignTop)


        self.horizontalLayout_113.addWidget(self.frame_309, 0, Qt.AlignTop)

        self.frame_310 = QFrame(self.frame_305)
        self.frame_310.setObjectName(u"frame_310")
        self.frame_310.setFrameShape(QFrame.StyledPanel)
        self.frame_310.setFrameShadow(QFrame.Raised)
        self.verticalLayout_301 = QVBoxLayout(self.frame_310)
        self.verticalLayout_301.setObjectName(u"verticalLayout_301")
        self.verticalLayout_301.setContentsMargins(-1, 0, -1, 0)
        self.frame_343 = QFrame(self.frame_310)
        self.frame_343.setObjectName(u"frame_343")
        self.frame_343.setFrameShape(QFrame.StyledPanel)
        self.frame_343.setFrameShadow(QFrame.Raised)
        self.verticalLayout_302 = QVBoxLayout(self.frame_343)
        self.verticalLayout_302.setSpacing(8)
        self.verticalLayout_302.setObjectName(u"verticalLayout_302")
        self.verticalLayout_302.setContentsMargins(-1, 0, -1, 0)
        self.label_128 = QLabel(self.frame_343)
        self.label_128.setObjectName(u"label_128")

        self.verticalLayout_302.addWidget(self.label_128)

        self.label_129 = QLabel(self.frame_343)
        self.label_129.setObjectName(u"label_129")

        self.verticalLayout_302.addWidget(self.label_129)

        self.reset_password_perso = QLineEdit(self.frame_343)
        self.reset_password_perso.setObjectName(u"reset_password_perso")
        self.reset_password_perso.setFont(font2)
        self.reset_password_perso.setEchoMode(QLineEdit.Password)

        self.verticalLayout_302.addWidget(self.reset_password_perso)


        self.verticalLayout_301.addWidget(self.frame_343)

        self.frame_344 = QFrame(self.frame_310)
        self.frame_344.setObjectName(u"frame_344")
        self.frame_344.setFrameShape(QFrame.StyledPanel)
        self.frame_344.setFrameShadow(QFrame.Raised)
        self.verticalLayout_304 = QVBoxLayout(self.frame_344)
        self.verticalLayout_304.setSpacing(0)
        self.verticalLayout_304.setObjectName(u"verticalLayout_304")
        self.verticalLayout_304.setContentsMargins(-1, 0, -1, 0)
        self.label_130 = QLabel(self.frame_344)
        self.label_130.setObjectName(u"label_130")

        self.verticalLayout_304.addWidget(self.label_130)

        self.confirm_reset_password_perso = QLineEdit(self.frame_344)
        self.confirm_reset_password_perso.setObjectName(u"confirm_reset_password_perso")
        self.confirm_reset_password_perso.setFont(font2)
        self.confirm_reset_password_perso.setEchoMode(QLineEdit.Password)

        self.verticalLayout_304.addWidget(self.confirm_reset_password_perso)


        self.verticalLayout_301.addWidget(self.frame_344)

        self.frame_345 = QFrame(self.frame_310)
        self.frame_345.setObjectName(u"frame_345")
        self.frame_345.setFrameShape(QFrame.StyledPanel)
        self.frame_345.setFrameShadow(QFrame.Raised)
        self.verticalLayout_303 = QVBoxLayout(self.frame_345)
        self.verticalLayout_303.setObjectName(u"verticalLayout_303")
        self.reinitialiser_mot_de_passe = QPushButton(self.frame_345)
        self.reinitialiser_mot_de_passe.setObjectName(u"reinitialiser_mot_de_passe")
        self.reinitialiser_mot_de_passe.setFont(font4)

        self.verticalLayout_303.addWidget(self.reinitialiser_mot_de_passe)


        self.verticalLayout_301.addWidget(self.frame_345)


        self.horizontalLayout_113.addWidget(self.frame_310)

        self.frame_311 = QFrame(self.frame_305)
        self.frame_311.setObjectName(u"frame_311")
        self.frame_311.setFrameShape(QFrame.StyledPanel)
        self.frame_311.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_113.addWidget(self.frame_311)


        self.verticalLayout_269.addWidget(self.frame_305)

        self.scrollArea_5.setWidget(self.scrollAreaWidgetContents_8)

        self.verticalLayout_71.addWidget(self.scrollArea_5)

        self.admin_stacked.addWidget(self.add_admin)

        self.verticalLayout_16.addWidget(self.admin_stacked)

        self.stackedWidget.addWidget(self.admin_page)
        self.etudiant_page = QWidget()
        self.etudiant_page.setObjectName(u"etudiant_page")
        self.verticalLayout_19 = QVBoxLayout(self.etudiant_page)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.stackedStudent = QStackedWidget(self.etudiant_page)
        self.stackedStudent.setObjectName(u"stackedStudent")
        self.index_student = QWidget()
        self.index_student.setObjectName(u"index_student")
        self.verticalLayout_21 = QVBoxLayout(self.index_student)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(-1, -1, -1, 0)
        self.frame_9 = QFrame(self.index_student)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_22.setSpacing(15)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(-1, 0, -1, -1)
        self.add_student = QPushButton(self.frame_9)
        self.add_student.setObjectName(u"add_student")
        self.add_student.setMinimumSize(QSize(170, 33))
        self.add_student.setMaximumSize(QSize(16777215, 33))
        self.add_student.setFont(font4)
        self.add_student.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_22.addWidget(self.add_student)

        self.btn_importer_exel = QPushButton(self.frame_9)
        self.btn_importer_exel.setObjectName(u"btn_importer_exel")
        self.btn_importer_exel.setMinimumSize(QSize(110, 33))
        self.btn_importer_exel.setMaximumSize(QSize(16777215, 33))
        self.btn_importer_exel.setFont(font4)
        self.btn_importer_exel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_22.addWidget(self.btn_importer_exel)

        self.btn_diplome = QPushButton(self.frame_9)
        self.btn_diplome.setObjectName(u"btn_diplome")
        self.btn_diplome.setMinimumSize(QSize(110, 33))
        self.btn_diplome.setMaximumSize(QSize(16777215, 33))
        self.btn_diplome.setFont(font4)
        self.btn_diplome.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_22.addWidget(self.btn_diplome)

        self.btn_certificat = QPushButton(self.frame_9)
        self.btn_certificat.setObjectName(u"btn_certificat")
        self.btn_certificat.setMinimumSize(QSize(110, 33))
        self.btn_certificat.setMaximumSize(QSize(16777215, 33))
        self.btn_certificat.setFont(font4)
        self.btn_certificat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_22.addWidget(self.btn_certificat)

        self.btn_badge = QPushButton(self.frame_9)
        self.btn_badge.setObjectName(u"btn_badge")
        self.btn_badge.setMinimumSize(QSize(110, 33))
        self.btn_badge.setMaximumSize(QSize(16777215, 33))
        self.btn_badge.setFont(font4)
        self.btn_badge.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_22.addWidget(self.btn_badge)


        self.verticalLayout_21.addWidget(self.frame_9, 0, Qt.AlignLeft)

        self.frame_10 = QFrame(self.index_student)
        self.frame_10.setObjectName(u"frame_10")
        sizePolicy.setHeightForWidth(self.frame_10.sizePolicy().hasHeightForWidth())
        self.frame_10.setSizePolicy(sizePolicy)
        self.frame_10.setFrameShape(QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QFrame.Raised)
        self.verticalLayout_40 = QVBoxLayout(self.frame_10)
        self.verticalLayout_40.setObjectName(u"verticalLayout_40")
        self.verticalLayout_40.setContentsMargins(-1, 0, -1, 0)
        self.frame_50 = QFrame(self.frame_10)
        self.frame_50.setObjectName(u"frame_50")
        self.frame_50.setMinimumSize(QSize(400, 0))
        self.frame_50.setFrameShape(QFrame.StyledPanel)
        self.frame_50.setFrameShadow(QFrame.Raised)
        self.verticalLayout_65 = QVBoxLayout(self.frame_50)
        self.verticalLayout_65.setObjectName(u"verticalLayout_65")
        self.verticalLayout_65.setContentsMargins(-1, 0, -1, 0)
        self.sesrch_student = QLineEdit(self.frame_50)
        self.sesrch_student.setObjectName(u"sesrch_student")
        self.sesrch_student.setFont(font2)

        self.verticalLayout_65.addWidget(self.sesrch_student)


        self.verticalLayout_40.addWidget(self.frame_50, 0, Qt.AlignRight)

        self.student_table = QTableWidget(self.frame_10)
        self.student_table.setObjectName(u"student_table")
        self.student_table.setMinimumSize(QSize(800, 0))
        self.student_table.setLocale(QLocale(QLocale.French, QLocale.France))
        self.student_table.setFrameShape(QFrame.NoFrame)
        self.student_table.setFrameShadow(QFrame.Plain)
        self.student_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.student_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.student_table.setAlternatingRowColors(True)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.student_table.setSortingEnabled(True)
        self.student_table.setWordWrap(False)
        self.student_table.horizontalHeader().setCascadingSectionResizes(False)
        self.student_table.horizontalHeader().setMinimumSectionSize(100)
        self.student_table.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.student_table.horizontalHeader().setStretchLastSection(True)
        self.student_table.verticalHeader().setVisible(False)
        self.student_table.verticalHeader().setCascadingSectionResizes(False)
        self.student_table.verticalHeader().setDefaultSectionSize(40)
        self.student_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_40.addWidget(self.student_table)

        self.frame_51 = QFrame(self.frame_10)
        self.frame_51.setObjectName(u"frame_51")
        self.frame_51.setMinimumSize(QSize(0, 25))
        self.frame_51.setMaximumSize(QSize(16777215, 100))
        self.frame_51.setFrameShape(QFrame.StyledPanel)
        self.frame_51.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_32 = QHBoxLayout(self.frame_51)
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(-1, 0, -1, 0)
        self.frame_52 = QFrame(self.frame_51)
        self.frame_52.setObjectName(u"frame_52")
        self.frame_52.setFrameShape(QFrame.StyledPanel)
        self.frame_52.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_33 = QHBoxLayout(self.frame_52)
        self.horizontalLayout_33.setSpacing(25)
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.horizontalLayout_33.setContentsMargins(0, 0, 0, 0)
        self.prev_page_student = QPushButton(self.frame_52)
        self.prev_page_student.setObjectName(u"prev_page_student")
        self.prev_page_student.setMinimumSize(QSize(0, 30))
        self.prev_page_student.setFont(font)
        self.prev_page_student.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.prev_page_student.setFlat(True)

        self.horizontalLayout_33.addWidget(self.prev_page_student)

        self.next_page_student = QPushButton(self.frame_52)
        self.next_page_student.setObjectName(u"next_page_student")
        self.next_page_student.setMinimumSize(QSize(0, 30))
        self.next_page_student.setFont(font)
        self.next_page_student.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.next_page_student.setFlat(True)

        self.horizontalLayout_33.addWidget(self.next_page_student)


        self.horizontalLayout_32.addWidget(self.frame_52, 0, Qt.AlignRight)

        self.frame_54 = QFrame(self.frame_51)
        self.frame_54.setObjectName(u"frame_54")
        self.frame_54.setFrameShape(QFrame.StyledPanel)
        self.frame_54.setFrameShadow(QFrame.Raised)
        self.frame_54.setLineWidth(0)

        self.horizontalLayout_32.addWidget(self.frame_54)


        self.verticalLayout_40.addWidget(self.frame_51, 0, Qt.AlignRight)


        self.verticalLayout_21.addWidget(self.frame_10)

        self.stackedStudent.addWidget(self.index_student)
        self.add_student_page = QWidget()
        self.add_student_page.setObjectName(u"add_student_page")
        self.verticalLayout_22 = QVBoxLayout(self.add_student_page)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(-1, 0, -1, 0)
        self.tabWidget = QTabWidget(self.add_student_page)
        self.tabWidget.setObjectName(u"tabWidget")
        self.personnel_info = QWidget()
        self.personnel_info.setObjectName(u"personnel_info")
        self.personnel_info.setMinimumSize(QSize(700, 25))
        self.personnel_info.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.verticalLayout_26 = QVBoxLayout(self.personnel_info)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_10 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_26.addItem(self.verticalSpacer_10)

        self.widget = QWidget(self.personnel_info)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(800, 0))
        self.verticalLayout_23 = QVBoxLayout(self.widget)
        self.verticalLayout_23.setSpacing(12)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.frame_163 = QFrame(self.widget)
        self.frame_163.setObjectName(u"frame_163")
        self.frame_163.setFrameShape(QFrame.StyledPanel)
        self.frame_163.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_86 = QHBoxLayout(self.frame_163)
        self.horizontalLayout_86.setSpacing(15)
        self.horizontalLayout_86.setObjectName(u"horizontalLayout_86")
        self.horizontalLayout_86.setContentsMargins(0, 0, 0, 14)
        self.back_to_details = QPushButton(self.frame_163)
        self.back_to_details.setObjectName(u"back_to_details")
        self.back_to_details.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_to_details.setFlat(True)

        self.horizontalLayout_86.addWidget(self.back_to_details)

        self.label_67 = QLabel(self.frame_163)
        self.label_67.setObjectName(u"label_67")
        font6 = QFont()
        font6.setFamilies([u"Inter"])
        font6.setPointSize(17)
        font6.setBold(True)
        self.label_67.setFont(font6)

        self.horizontalLayout_86.addWidget(self.label_67)


        self.verticalLayout_23.addWidget(self.frame_163, 0, Qt.AlignLeft|Qt.AlignTop)

        self.widget_2 = QWidget(self.widget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMinimumSize(QSize(800, 0))
        self.verticalLayout_24 = QVBoxLayout(self.widget_2)
        self.verticalLayout_24.setSpacing(20)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.frame_38 = QFrame(self.widget_2)
        self.frame_38.setObjectName(u"frame_38")
        self.frame_38.setFrameShape(QFrame.StyledPanel)
        self.frame_38.setFrameShadow(QFrame.Raised)
        self.verticalLayout_48 = QVBoxLayout(self.frame_38)
        self.verticalLayout_48.setSpacing(0)
        self.verticalLayout_48.setObjectName(u"verticalLayout_48")
        self.verticalLayout_48.setContentsMargins(0, 0, 0, 0)
        self.frame_39 = QFrame(self.frame_38)
        self.frame_39.setObjectName(u"frame_39")
        self.frame_39.setFrameShape(QFrame.StyledPanel)
        self.frame_39.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_129 = QHBoxLayout(self.frame_39)
        self.horizontalLayout_129.setSpacing(30)
        self.horizontalLayout_129.setObjectName(u"horizontalLayout_129")
        self.horizontalLayout_129.setContentsMargins(0, 0, 0, 0)
        self.frame_354 = QFrame(self.frame_39)
        self.frame_354.setObjectName(u"frame_354")
        self.frame_354.setFrameShape(QFrame.StyledPanel)
        self.frame_354.setFrameShadow(QFrame.Raised)
        self.verticalLayout_312 = QVBoxLayout(self.frame_354)
        self.verticalLayout_312.setSpacing(0)
        self.verticalLayout_312.setObjectName(u"verticalLayout_312")
        self.verticalLayout_312.setContentsMargins(0, 0, 0, 0)
        self.label_27 = QLabel(self.frame_354)
        self.label_27.setObjectName(u"label_27")

        self.verticalLayout_312.addWidget(self.label_27)

        self.niveau_id = QComboBox(self.frame_354)
        self.niveau_id.setObjectName(u"niveau_id")
        self.niveau_id.setMinimumSize(QSize(300, 37))
        self.niveau_id.setFont(font2)
        self.niveau_id.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.niveau_id.setMouseTracking(True)
        self.niveau_id.setTabletTracking(True)
        self.niveau_id.setFocusPolicy(Qt.TabFocus)
        self.niveau_id.setContextMenuPolicy(Qt.PreventContextMenu)
        self.niveau_id.setAcceptDrops(False)
        self.niveau_id.setAutoFillBackground(False)
        self.niveau_id.setCurrentText(u"")

        self.verticalLayout_312.addWidget(self.niveau_id)


        self.horizontalLayout_129.addWidget(self.frame_354)

        self.frame_353 = QFrame(self.frame_39)
        self.frame_353.setObjectName(u"frame_353")
        self.frame_353.setFrameShape(QFrame.StyledPanel)
        self.frame_353.setFrameShadow(QFrame.Raised)
        self.verticalLayout_311 = QVBoxLayout(self.frame_353)
        self.verticalLayout_311.setSpacing(0)
        self.verticalLayout_311.setObjectName(u"verticalLayout_311")
        self.verticalLayout_311.setContentsMargins(0, 0, 0, 0)
        self.label_136 = QLabel(self.frame_353)
        self.label_136.setObjectName(u"label_136")

        self.verticalLayout_311.addWidget(self.label_136)

        self.dernier_etablissement = QLineEdit(self.frame_353)
        self.dernier_etablissement.setObjectName(u"dernier_etablissement")
        self.dernier_etablissement.setFont(font2)

        self.verticalLayout_311.addWidget(self.dernier_etablissement)


        self.horizontalLayout_129.addWidget(self.frame_353)

        self.frame_352 = QFrame(self.frame_39)
        self.frame_352.setObjectName(u"frame_352")
        self.frame_352.setFrameShape(QFrame.StyledPanel)
        self.frame_352.setFrameShadow(QFrame.Raised)
        self.verticalLayout_49 = QVBoxLayout(self.frame_352)
        self.verticalLayout_49.setSpacing(0)
        self.verticalLayout_49.setObjectName(u"verticalLayout_49")
        self.verticalLayout_49.setContentsMargins(0, 0, 0, 0)
        self.label_137 = QLabel(self.frame_352)
        self.label_137.setObjectName(u"label_137")

        self.verticalLayout_49.addWidget(self.label_137)

        self.nisu = QLineEdit(self.frame_352)
        self.nisu.setObjectName(u"nisu")
        self.nisu.setFont(font2)

        self.verticalLayout_49.addWidget(self.nisu)


        self.horizontalLayout_129.addWidget(self.frame_352)


        self.verticalLayout_48.addWidget(self.frame_39)


        self.verticalLayout_24.addWidget(self.frame_38)

        self.student_id = QLineEdit(self.widget_2)
        self.student_id.setObjectName(u"student_id")
        self.student_id.setReadOnly(True)

        self.verticalLayout_24.addWidget(self.student_id)

        self.frame_11 = QFrame(self.widget_2)
        self.frame_11.setObjectName(u"frame_11")
        sizePolicy1.setHeightForWidth(self.frame_11.sizePolicy().hasHeightForWidth())
        self.frame_11.setSizePolicy(sizePolicy1)
        self.frame_11.setMinimumSize(QSize(300, 0))
        self.frame_11.setFrameShape(QFrame.StyledPanel)
        self.frame_11.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_23 = QHBoxLayout(self.frame_11)
        self.horizontalLayout_23.setSpacing(25)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.frame_15 = QFrame(self.frame_11)
        self.frame_15.setObjectName(u"frame_15")
        self.frame_15.setMinimumSize(QSize(300, 0))
        self.frame_15.setFrameShape(QFrame.StyledPanel)
        self.frame_15.setFrameShadow(QFrame.Raised)
        self.verticalLayout_36 = QVBoxLayout(self.frame_15)
        self.verticalLayout_36.setSpacing(0)
        self.verticalLayout_36.setObjectName(u"verticalLayout_36")
        self.verticalLayout_36.setContentsMargins(0, 0, 0, 0)
        self.label_7 = QLabel(self.frame_15)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_36.addWidget(self.label_7)

        self.nom = QLineEdit(self.frame_15)
        self.nom.setObjectName(u"nom")
        self.nom.setMinimumSize(QSize(0, 37))
        self.nom.setFont(font2)

        self.verticalLayout_36.addWidget(self.nom)


        self.horizontalLayout_23.addWidget(self.frame_15)

        self.frame_16 = QFrame(self.frame_11)
        self.frame_16.setObjectName(u"frame_16")
        self.frame_16.setMinimumSize(QSize(300, 0))
        self.frame_16.setFrameShape(QFrame.StyledPanel)
        self.frame_16.setFrameShadow(QFrame.Raised)
        self.verticalLayout_34 = QVBoxLayout(self.frame_16)
        self.verticalLayout_34.setSpacing(0)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.verticalLayout_34.setContentsMargins(0, 0, 0, 0)
        self.label_10 = QLabel(self.frame_16)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_34.addWidget(self.label_10)

        self.prenom = QLineEdit(self.frame_16)
        self.prenom.setObjectName(u"prenom")
        self.prenom.setMinimumSize(QSize(0, 37))
        self.prenom.setFont(font2)

        self.verticalLayout_34.addWidget(self.prenom)


        self.horizontalLayout_23.addWidget(self.frame_16)

        self.frame_17 = QFrame(self.frame_11)
        self.frame_17.setObjectName(u"frame_17")
        self.frame_17.setMinimumSize(QSize(300, 25))
        self.frame_17.setFont(font4)
        self.frame_17.setFrameShape(QFrame.StyledPanel)
        self.frame_17.setFrameShadow(QFrame.Raised)
        self.verticalLayout_35 = QVBoxLayout(self.frame_17)
        self.verticalLayout_35.setSpacing(0)
        self.verticalLayout_35.setObjectName(u"verticalLayout_35")
        self.verticalLayout_35.setContentsMargins(0, 0, 0, 0)
        self.label_11 = QLabel(self.frame_17)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_35.addWidget(self.label_11)

        self.sexe = QComboBox(self.frame_17)
        self.sexe.setObjectName(u"sexe")
        self.sexe.setMinimumSize(QSize(0, 37))
        self.sexe.setFont(font2)
        self.sexe.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_35.addWidget(self.sexe)


        self.horizontalLayout_23.addWidget(self.frame_17)


        self.verticalLayout_24.addWidget(self.frame_11)

        self.frame_12 = QFrame(self.widget_2)
        self.frame_12.setObjectName(u"frame_12")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.frame_12.sizePolicy().hasHeightForWidth())
        self.frame_12.setSizePolicy(sizePolicy6)
        self.frame_12.setFrameShape(QFrame.StyledPanel)
        self.frame_12.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_24 = QHBoxLayout(self.frame_12)
        self.horizontalLayout_24.setSpacing(25)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.frame_18 = QFrame(self.frame_12)
        self.frame_18.setObjectName(u"frame_18")
        self.frame_18.setMinimumSize(QSize(300, 0))
        self.frame_18.setFrameShape(QFrame.StyledPanel)
        self.frame_18.setFrameShadow(QFrame.Raised)
        self.verticalLayout_32 = QVBoxLayout(self.frame_18)
        self.verticalLayout_32.setSpacing(0)
        self.verticalLayout_32.setObjectName(u"verticalLayout_32")
        self.verticalLayout_32.setContentsMargins(0, 0, 0, 0)
        self.label_28 = QLabel(self.frame_18)
        self.label_28.setObjectName(u"label_28")

        self.verticalLayout_32.addWidget(self.label_28)

        self.telephone = QLineEdit(self.frame_18)
        self.telephone.setObjectName(u"telephone")
        self.telephone.setMinimumSize(QSize(0, 37))
        self.telephone.setFont(font2)

        self.verticalLayout_32.addWidget(self.telephone)


        self.horizontalLayout_24.addWidget(self.frame_18)

        self.frame_19 = QFrame(self.frame_12)
        self.frame_19.setObjectName(u"frame_19")
        self.frame_19.setMinimumSize(QSize(300, 0))
        self.frame_19.setFrameShape(QFrame.StyledPanel)
        self.frame_19.setFrameShadow(QFrame.Raised)
        self.verticalLayout_33 = QVBoxLayout(self.frame_19)
        self.verticalLayout_33.setSpacing(0)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_33.setContentsMargins(0, 0, 0, 0)
        self.label_29 = QLabel(self.frame_19)
        self.label_29.setObjectName(u"label_29")

        self.verticalLayout_33.addWidget(self.label_29)

        self.adresse = QLineEdit(self.frame_19)
        self.adresse.setObjectName(u"adresse")
        self.adresse.setMinimumSize(QSize(0, 37))
        self.adresse.setFont(font2)

        self.verticalLayout_33.addWidget(self.adresse)


        self.horizontalLayout_24.addWidget(self.frame_19)

        self.frame_20 = QFrame(self.frame_12)
        self.frame_20.setObjectName(u"frame_20")
        self.frame_20.setMinimumSize(QSize(300, 0))
        self.frame_20.setFrameShape(QFrame.StyledPanel)
        self.frame_20.setFrameShadow(QFrame.Raised)
        self.verticalLayout_158 = QVBoxLayout(self.frame_20)
        self.verticalLayout_158.setSpacing(0)
        self.verticalLayout_158.setObjectName(u"verticalLayout_158")
        self.verticalLayout_158.setContentsMargins(0, 0, 0, 0)
        self.label_36 = QLabel(self.frame_20)
        self.label_36.setObjectName(u"label_36")

        self.verticalLayout_158.addWidget(self.label_36)

        self.email_3 = QLineEdit(self.frame_20)
        self.email_3.setObjectName(u"email_3")
        self.email_3.setMinimumSize(QSize(0, 37))
        self.email_3.setFont(font2)

        self.verticalLayout_158.addWidget(self.email_3)


        self.horizontalLayout_24.addWidget(self.frame_20)


        self.verticalLayout_24.addWidget(self.frame_12)

        self.frame_14 = QFrame(self.widget_2)
        self.frame_14.setObjectName(u"frame_14")
        self.frame_14.setFrameShape(QFrame.StyledPanel)
        self.frame_14.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_26 = QHBoxLayout(self.frame_14)
        self.horizontalLayout_26.setSpacing(25)
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.horizontalLayout_26.setContentsMargins(0, 0, 0, 0)
        self.frame_24 = QFrame(self.frame_14)
        self.frame_24.setObjectName(u"frame_24")
        self.frame_24.setMinimumSize(QSize(300, 0))
        self.frame_24.setFrameShape(QFrame.StyledPanel)
        self.frame_24.setFrameShadow(QFrame.Raised)
        self.verticalLayout_29 = QVBoxLayout(self.frame_24)
        self.verticalLayout_29.setSpacing(0)
        self.verticalLayout_29.setObjectName(u"verticalLayout_29")
        self.verticalLayout_29.setContentsMargins(0, 0, 0, 0)
        self.label_30 = QLabel(self.frame_24)
        self.label_30.setObjectName(u"label_30")

        self.verticalLayout_29.addWidget(self.label_30)

        self.date_de_naissance = QDateEdit(self.frame_24)
        self.date_de_naissance.setObjectName(u"date_de_naissance")
        self.date_de_naissance.setMinimumSize(QSize(0, 37))
        self.date_de_naissance.setFont(font2)
        self.date_de_naissance.setWrapping(True)
        self.date_de_naissance.setCalendarPopup(True)
        self.date_de_naissance.setCurrentSectionIndex(0)
        self.date_de_naissance.setTimeSpec(Qt.UTC)
        self.date_de_naissance.setDate(QDate(1989, 1, 19))

        self.verticalLayout_29.addWidget(self.date_de_naissance)


        self.horizontalLayout_26.addWidget(self.frame_24)

        self.frame_25 = QFrame(self.frame_14)
        self.frame_25.setObjectName(u"frame_25")
        self.frame_25.setMinimumSize(QSize(300, 25))
        self.frame_25.setFrameShape(QFrame.StyledPanel)
        self.frame_25.setFrameShadow(QFrame.Raised)
        self.verticalLayout_30 = QVBoxLayout(self.frame_25)
        self.verticalLayout_30.setSpacing(0)
        self.verticalLayout_30.setObjectName(u"verticalLayout_30")
        self.verticalLayout_30.setContentsMargins(0, 0, 0, 0)
        self.label_31 = QLabel(self.frame_25)
        self.label_31.setObjectName(u"label_31")

        self.verticalLayout_30.addWidget(self.label_31)

        self.lieu_de_naissance = QLineEdit(self.frame_25)
        self.lieu_de_naissance.setObjectName(u"lieu_de_naissance")
        self.lieu_de_naissance.setMinimumSize(QSize(0, 37))
        self.lieu_de_naissance.setFont(font2)

        self.verticalLayout_30.addWidget(self.lieu_de_naissance)


        self.horizontalLayout_26.addWidget(self.frame_25)

        self.frame_26 = QFrame(self.frame_14)
        self.frame_26.setObjectName(u"frame_26")
        self.frame_26.setMinimumSize(QSize(300, 0))
        self.frame_26.setFrameShape(QFrame.StyledPanel)
        self.frame_26.setFrameShadow(QFrame.Raised)
        self.verticalLayout_31 = QVBoxLayout(self.frame_26)
        self.verticalLayout_31.setSpacing(0)
        self.verticalLayout_31.setObjectName(u"verticalLayout_31")
        self.verticalLayout_31.setContentsMargins(0, 0, 0, 0)
        self.label_35 = QLabel(self.frame_26)
        self.label_35.setObjectName(u"label_35")

        self.verticalLayout_31.addWidget(self.label_35)

        self.religion = QLineEdit(self.frame_26)
        self.religion.setObjectName(u"religion")
        self.religion.setMinimumSize(QSize(0, 37))
        self.religion.setFont(font2)

        self.verticalLayout_31.addWidget(self.religion)


        self.horizontalLayout_26.addWidget(self.frame_26)


        self.verticalLayout_24.addWidget(self.frame_14)

        self.frame_13 = QFrame(self.widget_2)
        self.frame_13.setObjectName(u"frame_13")
        self.frame_13.setFrameShape(QFrame.StyledPanel)
        self.frame_13.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_25 = QHBoxLayout(self.frame_13)
        self.horizontalLayout_25.setSpacing(25)
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.horizontalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.frame_21 = QFrame(self.frame_13)
        self.frame_21.setObjectName(u"frame_21")
        self.frame_21.setMinimumSize(QSize(300, 0))
        self.frame_21.setFrameShape(QFrame.StyledPanel)
        self.frame_21.setFrameShadow(QFrame.Raised)
        self.verticalLayout_28 = QVBoxLayout(self.frame_21)
        self.verticalLayout_28.setSpacing(0)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.verticalLayout_28.setContentsMargins(0, 0, 0, 0)
        self.label_32 = QLabel(self.frame_21)
        self.label_32.setObjectName(u"label_32")

        self.verticalLayout_28.addWidget(self.label_32)

        self.annee_academique_id = QComboBox(self.frame_21)
        self.annee_academique_id.setObjectName(u"annee_academique_id")
        self.annee_academique_id.setMinimumSize(QSize(0, 37))
        self.annee_academique_id.setFont(font2)
        self.annee_academique_id.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_28.addWidget(self.annee_academique_id)


        self.horizontalLayout_25.addWidget(self.frame_21)

        self.frame_22 = QFrame(self.frame_13)
        self.frame_22.setObjectName(u"frame_22")
        self.frame_22.setMinimumSize(QSize(300, 0))
        self.frame_22.setFrameShape(QFrame.StyledPanel)
        self.frame_22.setFrameShadow(QFrame.Raised)
        self.verticalLayout_27 = QVBoxLayout(self.frame_22)
        self.verticalLayout_27.setSpacing(0)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.verticalLayout_27.setContentsMargins(0, 0, 0, 0)
        self.label_33 = QLabel(self.frame_22)
        self.label_33.setObjectName(u"label_33")

        self.verticalLayout_27.addWidget(self.label_33)

        self.classe_actuelle_id = QComboBox(self.frame_22)
        self.classe_actuelle_id.setObjectName(u"classe_actuelle_id")
        self.classe_actuelle_id.setMinimumSize(QSize(0, 37))
        self.classe_actuelle_id.setFont(font2)
        self.classe_actuelle_id.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_27.addWidget(self.classe_actuelle_id)


        self.horizontalLayout_25.addWidget(self.frame_22)

        self.frame_23 = QFrame(self.frame_13)
        self.frame_23.setObjectName(u"frame_23")
        self.frame_23.setMinimumSize(QSize(300, 25))
        self.frame_23.setFrameShape(QFrame.StyledPanel)
        self.frame_23.setFrameShadow(QFrame.Raised)
        self.verticalLayout_25 = QVBoxLayout(self.frame_23)
        self.verticalLayout_25.setSpacing(0)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(0, 0, 0, 0)
        self.label_34 = QLabel(self.frame_23)
        self.label_34.setObjectName(u"label_34")

        self.verticalLayout_25.addWidget(self.label_34)

        self.aide_financiere = QComboBox(self.frame_23)
        self.aide_financiere.setObjectName(u"aide_financiere")
        self.aide_financiere.setMinimumSize(QSize(0, 37))
        self.aide_financiere.setFont(font2)

        self.verticalLayout_25.addWidget(self.aide_financiere)


        self.horizontalLayout_25.addWidget(self.frame_23)


        self.verticalLayout_24.addWidget(self.frame_13)

        self.frame_371 = QFrame(self.widget_2)
        self.frame_371.setObjectName(u"frame_371")
        self.frame_371.setFrameShape(QFrame.StyledPanel)
        self.frame_371.setFrameShadow(QFrame.Raised)
        self.verticalLayout_325 = QVBoxLayout(self.frame_371)
        self.verticalLayout_325.setSpacing(0)
        self.verticalLayout_325.setObjectName(u"verticalLayout_325")
        self.verticalLayout_325.setContentsMargins(0, 0, 0, 0)
        self.label_146 = QLabel(self.frame_371)
        self.label_146.setObjectName(u"label_146")

        self.verticalLayout_325.addWidget(self.label_146)

        self.faculte_id = QComboBox(self.frame_371)
        self.faculte_id.setObjectName(u"faculte_id")
        self.faculte_id.setMinimumSize(QSize(300, 37))
        self.faculte_id.setFont(font2)
        self.faculte_id.setEditable(True)

        self.verticalLayout_325.addWidget(self.faculte_id)


        self.verticalLayout_24.addWidget(self.frame_371, 0, Qt.AlignLeft)


        self.verticalLayout_23.addWidget(self.widget_2, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.frame_28 = QFrame(self.widget)
        self.frame_28.setObjectName(u"frame_28")
        self.frame_28.setFrameShape(QFrame.StyledPanel)
        self.frame_28.setFrameShadow(QFrame.Raised)
        self.verticalLayout_39 = QVBoxLayout(self.frame_28)
        self.verticalLayout_39.setSpacing(0)
        self.verticalLayout_39.setObjectName(u"verticalLayout_39")
        self.verticalLayout_39.setContentsMargins(0, 0, 0, 0)
        self.suivant_1 = QPushButton(self.frame_28)
        self.suivant_1.setObjectName(u"suivant_1")
        self.suivant_1.setMinimumSize(QSize(140, 35))
        self.suivant_1.setFont(font)
        self.suivant_1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.suivant_1.setFlat(True)

        self.verticalLayout_39.addWidget(self.suivant_1)


        self.verticalLayout_23.addWidget(self.frame_28, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout_26.addWidget(self.widget, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.tabWidget.addTab(self.personnel_info, "")
        self.responsable_info = QWidget()
        self.responsable_info.setObjectName(u"responsable_info")
        self.verticalLayout_55 = QVBoxLayout(self.responsable_info)
        self.verticalLayout_55.setObjectName(u"verticalLayout_55")
        self.widget_4 = QWidget(self.responsable_info)
        self.widget_4.setObjectName(u"widget_4")
        self.widget_4.setMinimumSize(QSize(800, 0))
        self.verticalLayout_41 = QVBoxLayout(self.widget_4)
        self.verticalLayout_41.setObjectName(u"verticalLayout_41")
        self.frame_29 = QFrame(self.widget_4)
        self.frame_29.setObjectName(u"frame_29")
        self.frame_29.setFrameShape(QFrame.StyledPanel)
        self.frame_29.setFrameShadow(QFrame.Raised)
        self.verticalLayout_66 = QVBoxLayout(self.frame_29)
        self.verticalLayout_66.setObjectName(u"verticalLayout_66")
        self.label_15 = QLabel(self.frame_29)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setFont(font6)

        self.verticalLayout_66.addWidget(self.label_15)


        self.verticalLayout_41.addWidget(self.frame_29)

        self.widget_5 = QWidget(self.widget_4)
        self.widget_5.setObjectName(u"widget_5")
        self.widget_5.setMinimumSize(QSize(800, 0))
        self.verticalLayout_42 = QVBoxLayout(self.widget_5)
        self.verticalLayout_42.setSpacing(20)
        self.verticalLayout_42.setObjectName(u"verticalLayout_42")
        self.verticalLayout_42.setContentsMargins(-1, -1, 0, -1)
        self.frame_30 = QFrame(self.widget_5)
        self.frame_30.setObjectName(u"frame_30")
        self.frame_30.setMinimumSize(QSize(300, 0))
        self.frame_30.setFrameShape(QFrame.StyledPanel)
        self.frame_30.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_28 = QHBoxLayout(self.frame_30)
        self.horizontalLayout_28.setSpacing(20)
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.horizontalLayout_28.setContentsMargins(9, -1, 0, -1)
        self.frame_31 = QFrame(self.frame_30)
        self.frame_31.setObjectName(u"frame_31")
        self.frame_31.setMinimumSize(QSize(300, 0))
        self.frame_31.setFrameShape(QFrame.StyledPanel)
        self.frame_31.setFrameShadow(QFrame.Raised)
        self.verticalLayout_43 = QVBoxLayout(self.frame_31)
        self.verticalLayout_43.setObjectName(u"verticalLayout_43")
        self.verticalLayout_43.setContentsMargins(0, -1, 0, -1)
        self.label_37 = QLabel(self.frame_31)
        self.label_37.setObjectName(u"label_37")

        self.verticalLayout_43.addWidget(self.label_37)

        self.nom_responsable = QLineEdit(self.frame_31)
        self.nom_responsable.setObjectName(u"nom_responsable")
        self.nom_responsable.setMinimumSize(QSize(0, 37))
        self.nom_responsable.setFont(font2)

        self.verticalLayout_43.addWidget(self.nom_responsable)


        self.horizontalLayout_28.addWidget(self.frame_31)

        self.frame_32 = QFrame(self.frame_30)
        self.frame_32.setObjectName(u"frame_32")
        self.frame_32.setMinimumSize(QSize(300, 0))
        self.frame_32.setFrameShape(QFrame.StyledPanel)
        self.frame_32.setFrameShadow(QFrame.Raised)
        self.verticalLayout_44 = QVBoxLayout(self.frame_32)
        self.verticalLayout_44.setObjectName(u"verticalLayout_44")
        self.verticalLayout_44.setContentsMargins(0, -1, 0, -1)
        self.label_39 = QLabel(self.frame_32)
        self.label_39.setObjectName(u"label_39")

        self.verticalLayout_44.addWidget(self.label_39)

        self.prenom_responsable = QLineEdit(self.frame_32)
        self.prenom_responsable.setObjectName(u"prenom_responsable")
        self.prenom_responsable.setFont(font2)

        self.verticalLayout_44.addWidget(self.prenom_responsable)


        self.horizontalLayout_28.addWidget(self.frame_32)

        self.frame_33 = QFrame(self.frame_30)
        self.frame_33.setObjectName(u"frame_33")
        self.frame_33.setMinimumSize(QSize(300, 0))
        self.frame_33.setFrameShape(QFrame.StyledPanel)
        self.frame_33.setFrameShadow(QFrame.Raised)
        self.verticalLayout_45 = QVBoxLayout(self.frame_33)
        self.verticalLayout_45.setObjectName(u"verticalLayout_45")
        self.verticalLayout_45.setContentsMargins(0, -1, 0, -1)
        self.label_41 = QLabel(self.frame_33)
        self.label_41.setObjectName(u"label_41")

        self.verticalLayout_45.addWidget(self.label_41)

        self.email_responsable = QLineEdit(self.frame_33)
        self.email_responsable.setObjectName(u"email_responsable")
        self.email_responsable.setFont(font3)

        self.verticalLayout_45.addWidget(self.email_responsable)


        self.horizontalLayout_28.addWidget(self.frame_33)


        self.verticalLayout_42.addWidget(self.frame_30)

        self.frame_34 = QFrame(self.widget_5)
        self.frame_34.setObjectName(u"frame_34")
        self.frame_34.setFrameShape(QFrame.StyledPanel)
        self.frame_34.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_29 = QHBoxLayout(self.frame_34)
        self.horizontalLayout_29.setSpacing(25)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalLayout_29.setContentsMargins(0, -1, 0, -1)
        self.frame_35 = QFrame(self.frame_34)
        self.frame_35.setObjectName(u"frame_35")
        self.frame_35.setMinimumSize(QSize(300, 0))
        self.frame_35.setFrameShape(QFrame.StyledPanel)
        self.frame_35.setFrameShadow(QFrame.Raised)
        self.verticalLayout_46 = QVBoxLayout(self.frame_35)
        self.verticalLayout_46.setObjectName(u"verticalLayout_46")
        self.verticalLayout_46.setContentsMargins(0, -1, 0, -1)
        self.label_38 = QLabel(self.frame_35)
        self.label_38.setObjectName(u"label_38")

        self.verticalLayout_46.addWidget(self.label_38)

        self.adresse_responsable = QLineEdit(self.frame_35)
        self.adresse_responsable.setObjectName(u"adresse_responsable")
        self.adresse_responsable.setMinimumSize(QSize(0, 37))
        self.adresse_responsable.setMaximumSize(QSize(16777215, 37))
        self.adresse_responsable.setFont(font2)

        self.verticalLayout_46.addWidget(self.adresse_responsable)


        self.horizontalLayout_29.addWidget(self.frame_35)

        self.frame_36 = QFrame(self.frame_34)
        self.frame_36.setObjectName(u"frame_36")
        self.frame_36.setMinimumSize(QSize(300, 0))
        self.frame_36.setFrameShape(QFrame.StyledPanel)
        self.frame_36.setFrameShadow(QFrame.Raised)
        self.verticalLayout_47 = QVBoxLayout(self.frame_36)
        self.verticalLayout_47.setObjectName(u"verticalLayout_47")
        self.verticalLayout_47.setContentsMargins(0, -1, 0, -1)
        self.label_40 = QLabel(self.frame_36)
        self.label_40.setObjectName(u"label_40")

        self.verticalLayout_47.addWidget(self.label_40)

        self.telephone_responsable = QLineEdit(self.frame_36)
        self.telephone_responsable.setObjectName(u"telephone_responsable")
        self.telephone_responsable.setFont(font2)

        self.verticalLayout_47.addWidget(self.telephone_responsable)


        self.horizontalLayout_29.addWidget(self.frame_36)

        self.frame_37 = QFrame(self.frame_34)
        self.frame_37.setObjectName(u"frame_37")
        self.frame_37.setMinimumSize(QSize(300, 0))
        self.frame_37.setFrameShape(QFrame.StyledPanel)
        self.frame_37.setFrameShadow(QFrame.Raised)
        self.verticalLayout_159 = QVBoxLayout(self.frame_37)
        self.verticalLayout_159.setObjectName(u"verticalLayout_159")
        self.verticalLayout_159.setContentsMargins(0, -1, 0, -1)
        self.label_46 = QLabel(self.frame_37)
        self.label_46.setObjectName(u"label_46")

        self.verticalLayout_159.addWidget(self.label_46)

        self.sexe_responsable = QLineEdit(self.frame_37)
        self.sexe_responsable.setObjectName(u"sexe_responsable")
        self.sexe_responsable.setMinimumSize(QSize(200, 37))
        self.sexe_responsable.setFont(font3)

        self.verticalLayout_159.addWidget(self.sexe_responsable)


        self.horizontalLayout_29.addWidget(self.frame_37)


        self.verticalLayout_42.addWidget(self.frame_34)


        self.verticalLayout_41.addWidget(self.widget_5, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.frame_46 = QFrame(self.widget_4)
        self.frame_46.setObjectName(u"frame_46")
        self.frame_46.setFrameShape(QFrame.StyledPanel)
        self.frame_46.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_30 = QHBoxLayout(self.frame_46)
        self.horizontalLayout_30.setSpacing(15)
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.back_1 = QPushButton(self.frame_46)
        self.back_1.setObjectName(u"back_1")
        self.back_1.setMinimumSize(QSize(135, 0))
        self.back_1.setFont(font4)
        self.back_1.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_1.setFlat(True)

        self.horizontalLayout_30.addWidget(self.back_1)

        self.suivant_2 = QPushButton(self.frame_46)
        self.suivant_2.setObjectName(u"suivant_2")
        self.suivant_2.setMinimumSize(QSize(140, 35))
        self.suivant_2.setFont(font)
        self.suivant_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.suivant_2.setFlat(True)

        self.horizontalLayout_30.addWidget(self.suivant_2)


        self.verticalLayout_41.addWidget(self.frame_46, 0, Qt.AlignRight)


        self.verticalLayout_55.addWidget(self.widget_4, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.tabWidget.addTab(self.responsable_info, "")
        self.pieces = QWidget()
        self.pieces.setObjectName(u"pieces")
        self.verticalLayout_62 = QVBoxLayout(self.pieces)
        self.verticalLayout_62.setObjectName(u"verticalLayout_62")
        self.widget_piece = QWidget(self.pieces)
        self.widget_piece.setObjectName(u"widget_piece")
        self.verticalLayout_50 = QVBoxLayout(self.widget_piece)
        self.verticalLayout_50.setObjectName(u"verticalLayout_50")
        self.frame_47 = QFrame(self.widget_piece)
        self.frame_47.setObjectName(u"frame_47")
        self.frame_47.setFrameShape(QFrame.StyledPanel)
        self.frame_47.setFrameShadow(QFrame.Raised)
        self.verticalLayout_63 = QVBoxLayout(self.frame_47)
        self.verticalLayout_63.setObjectName(u"verticalLayout_63")
        self.label_13 = QLabel(self.frame_47)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setFont(font6)

        self.verticalLayout_63.addWidget(self.label_13)


        self.verticalLayout_50.addWidget(self.frame_47, 0, Qt.AlignLeft|Qt.AlignTop)

        self.widget_piece_inner = QWidget(self.widget_piece)
        self.widget_piece_inner.setObjectName(u"widget_piece_inner")
        self.verticalLayout_51 = QVBoxLayout(self.widget_piece_inner)
        self.verticalLayout_51.setSpacing(10)
        self.verticalLayout_51.setObjectName(u"verticalLayout_51")
        self.verticalLayout_51.setContentsMargins(0, -1, 0, -1)
        self.frame_48 = QFrame(self.widget_piece_inner)
        self.frame_48.setObjectName(u"frame_48")
        self.frame_48.setFrameShape(QFrame.StyledPanel)
        self.frame_48.setFrameShadow(QFrame.Raised)

        self.verticalLayout_51.addWidget(self.frame_48)

        self.frame_40 = QFrame(self.widget_piece_inner)
        self.frame_40.setObjectName(u"frame_40")
        self.frame_40.setMinimumSize(QSize(300, 0))
        self.frame_40.setFrameShape(QFrame.StyledPanel)
        self.frame_40.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_31 = QHBoxLayout(self.frame_40)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.supprimer = QPushButton(self.frame_40)
        self.supprimer.setObjectName(u"supprimer")
        self.supprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.supprimer.setFlat(True)

        self.horizontalLayout_31.addWidget(self.supprimer)

        self.frame_41 = QFrame(self.frame_40)
        self.frame_41.setObjectName(u"frame_41")
        self.frame_41.setMinimumSize(QSize(240, 0))
        self.frame_41.setFrameShape(QFrame.StyledPanel)
        self.frame_41.setFrameShadow(QFrame.Raised)
        self.verticalLayout_52 = QVBoxLayout(self.frame_41)
        self.verticalLayout_52.setObjectName(u"verticalLayout_52")
        self.type_de_document = QComboBox(self.frame_41)
        self.type_de_document.setObjectName(u"type_de_document")
        self.type_de_document.setMinimumSize(QSize(0, 37))
        self.type_de_document.setFont(font2)

        self.verticalLayout_52.addWidget(self.type_de_document)


        self.horizontalLayout_31.addWidget(self.frame_41)

        self.frame_43 = QFrame(self.frame_40)
        self.frame_43.setObjectName(u"frame_43")
        self.frame_43.setMinimumSize(QSize(200, 0))
        self.frame_43.setFrameShape(QFrame.StyledPanel)
        self.frame_43.setFrameShadow(QFrame.Raised)
        self.verticalLayout_56 = QVBoxLayout(self.frame_43)
        self.verticalLayout_56.setObjectName(u"verticalLayout_56")
        self.verticalLayout_56.setContentsMargins(-1, -1, 0, -1)
        self.document_date_dexpiration = QDateEdit(self.frame_43)
        self.document_date_dexpiration.setObjectName(u"document_date_dexpiration")
        self.document_date_dexpiration.setMinimumSize(QSize(0, 37))
        self.document_date_dexpiration.setFont(font2)
        self.document_date_dexpiration.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_56.addWidget(self.document_date_dexpiration)


        self.horizontalLayout_31.addWidget(self.frame_43)

        self.frame_42 = QFrame(self.frame_40)
        self.frame_42.setObjectName(u"frame_42")
        self.frame_42.setMinimumSize(QSize(200, 0))
        self.frame_42.setFrameShape(QFrame.StyledPanel)
        self.frame_42.setFrameShadow(QFrame.Raised)
        self.verticalLayout_53 = QVBoxLayout(self.frame_42)
        self.verticalLayout_53.setObjectName(u"verticalLayout_53")
        self.verticalLayout_53.setContentsMargins(0, -1, 0, -1)
        self.document_numero = QLineEdit(self.frame_42)
        self.document_numero.setObjectName(u"document_numero")
        self.document_numero.setMinimumSize(QSize(0, 37))
        self.document_numero.setFont(font2)

        self.verticalLayout_53.addWidget(self.document_numero)


        self.horizontalLayout_31.addWidget(self.frame_42)

        self.frame_44 = QFrame(self.frame_40)
        self.frame_44.setObjectName(u"frame_44")
        self.frame_44.setMinimumSize(QSize(240, 0))
        self.frame_44.setFrameShape(QFrame.StyledPanel)
        self.frame_44.setFrameShadow(QFrame.Raised)
        self.verticalLayout_57 = QVBoxLayout(self.frame_44)
        self.verticalLayout_57.setObjectName(u"verticalLayout_57")
        self.verticalLayout_57.setContentsMargins(0, 0, 0, 0)
        self.document_image = QLineEdit(self.frame_44)
        self.document_image.setObjectName(u"document_image")
        self.document_image.setMinimumSize(QSize(0, 37))
        self.document_image.setFont(font2)
        self.document_image.setInputMethodHints(Qt.ImhNone)
        self.document_image.setCursorPosition(0)

        self.verticalLayout_57.addWidget(self.document_image)

        self.chose_image = QPushButton(self.frame_44)
        self.chose_image.setObjectName(u"chose_image")
        self.chose_image.setFont(font4)
        self.chose_image.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chose_image.setFlat(True)

        self.verticalLayout_57.addWidget(self.chose_image)


        self.horizontalLayout_31.addWidget(self.frame_44)


        self.verticalLayout_51.addWidget(self.frame_40)


        self.verticalLayout_50.addWidget(self.widget_piece_inner, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.frame_45 = QFrame(self.widget_piece)
        self.frame_45.setObjectName(u"frame_45")
        self.frame_45.setFrameShape(QFrame.StyledPanel)
        self.frame_45.setFrameShadow(QFrame.Raised)
        self.verticalLayout_58 = QVBoxLayout(self.frame_45)
        self.verticalLayout_58.setObjectName(u"verticalLayout_58")
        self.ajouter_document = QPushButton(self.frame_45)
        self.ajouter_document.setObjectName(u"ajouter_document")
        self.ajouter_document.setFont(font)
        self.ajouter_document.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ajouter_document.setFlat(True)

        self.verticalLayout_58.addWidget(self.ajouter_document)


        self.verticalLayout_50.addWidget(self.frame_45, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_49 = QFrame(self.widget_piece)
        self.frame_49.setObjectName(u"frame_49")
        self.frame_49.setFont(font4)
        self.frame_49.setFrameShape(QFrame.StyledPanel)
        self.frame_49.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_27 = QHBoxLayout(self.frame_49)
        self.horizontalLayout_27.setSpacing(15)
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.back_2 = QPushButton(self.frame_49)
        self.back_2.setObjectName(u"back_2")
        self.back_2.setMinimumSize(QSize(135, 0))
        self.back_2.setFont(font4)
        self.back_2.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_2.setFlat(True)

        self.horizontalLayout_27.addWidget(self.back_2)

        self.enregistre = QPushButton(self.frame_49)
        self.enregistre.setObjectName(u"enregistre")
        self.enregistre.setMinimumSize(QSize(140, 35))
        self.enregistre.setFont(font)
        self.enregistre.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.enregistre.setFlat(True)

        self.horizontalLayout_27.addWidget(self.enregistre)


        self.verticalLayout_50.addWidget(self.frame_49, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_62.addWidget(self.widget_piece, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.tabWidget.addTab(self.pieces, "")
        self.details = QWidget()
        self.details.setObjectName(u"details")
        self.verticalLayout_166 = QVBoxLayout(self.details)
        self.verticalLayout_166.setSpacing(0)
        self.verticalLayout_166.setObjectName(u"verticalLayout_166")
        self.verticalLayout_166.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_12 = QSpacerItem(20, 23, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_166.addItem(self.verticalSpacer_12)

        self.scrollArea_4 = QScrollArea(self.details)
        self.scrollArea_4.setObjectName(u"scrollArea_4")
        self.scrollArea_4.setWidgetResizable(True)
        self.scrollAreaWidgetContents_7 = QWidget()
        self.scrollAreaWidgetContents_7.setObjectName(u"scrollAreaWidgetContents_7")
        self.scrollAreaWidgetContents_7.setGeometry(QRect(0, 0, 1022, 567))
        self.verticalLayout_167 = QVBoxLayout(self.scrollAreaWidgetContents_7)
        self.verticalLayout_167.setObjectName(u"verticalLayout_167")
        self.frame_224 = QFrame(self.scrollAreaWidgetContents_7)
        self.frame_224.setObjectName(u"frame_224")
        self.frame_224.setFrameShape(QFrame.StyledPanel)
        self.frame_224.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_88 = QHBoxLayout(self.frame_224)
        self.horizontalLayout_88.setSpacing(30)
        self.horizontalLayout_88.setObjectName(u"horizontalLayout_88")
        self.horizontalLayout_88.setContentsMargins(0, 0, 0, 12)
        self.frame_225 = QFrame(self.frame_224)
        self.frame_225.setObjectName(u"frame_225")
        self.frame_225.setFont(font4)
        self.frame_225.setFrameShape(QFrame.StyledPanel)
        self.frame_225.setFrameShadow(QFrame.Raised)
        self.verticalLayout_203 = QVBoxLayout(self.frame_225)
        self.verticalLayout_203.setSpacing(0)
        self.verticalLayout_203.setObjectName(u"verticalLayout_203")
        self.verticalLayout_203.setContentsMargins(-1, 0, 0, 0)
        self.search_student_for_detail = QLineEdit(self.frame_225)
        self.search_student_for_detail.setObjectName(u"search_student_for_detail")
        self.search_student_for_detail.setMinimumSize(QSize(450, 37))
        self.search_student_for_detail.setFont(font2)

        self.verticalLayout_203.addWidget(self.search_student_for_detail)


        self.horizontalLayout_88.addWidget(self.frame_225, 0, Qt.AlignLeft)

        self.frame_226 = QFrame(self.frame_224)
        self.frame_226.setObjectName(u"frame_226")
        self.frame_226.setFrameShape(QFrame.StyledPanel)
        self.frame_226.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_89 = QHBoxLayout(self.frame_226)
        self.horizontalLayout_89.setSpacing(15)
        self.horizontalLayout_89.setObjectName(u"horizontalLayout_89")
        self.horizontalLayout_89.setContentsMargins(0, 0, 0, 0)
        self.frame_334 = QFrame(self.frame_226)
        self.frame_334.setObjectName(u"frame_334")
        self.frame_334.setFrameShape(QFrame.StyledPanel)
        self.frame_334.setFrameShadow(QFrame.Raised)
        self.verticalLayout_296 = QVBoxLayout(self.frame_334)
        self.verticalLayout_296.setSpacing(0)
        self.verticalLayout_296.setObjectName(u"verticalLayout_296")
        self.verticalLayout_296.setContentsMargins(0, 0, 0, 0)
        self.recu_inscrit = QPushButton(self.frame_334)
        self.recu_inscrit.setObjectName(u"recu_inscrit")
        self.recu_inscrit.setMinimumSize(QSize(80, 0))
        self.recu_inscrit.setMaximumSize(QSize(16777215, 36))
        self.recu_inscrit.setFont(font4)
        self.recu_inscrit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_296.addWidget(self.recu_inscrit)


        self.horizontalLayout_89.addWidget(self.frame_334)

        self.imprimer_etudiant = QPushButton(self.frame_226)
        self.imprimer_etudiant.setObjectName(u"imprimer_etudiant")
        self.imprimer_etudiant.setMinimumSize(QSize(130, 0))
        self.imprimer_etudiant.setMaximumSize(QSize(16777215, 36))
        self.imprimer_etudiant.setFont(font4)
        self.imprimer_etudiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.imprimer_etudiant.setFlat(True)

        self.horizontalLayout_89.addWidget(self.imprimer_etudiant)

        self.modifier_etudiant = QPushButton(self.frame_226)
        self.modifier_etudiant.setObjectName(u"modifier_etudiant")
        self.modifier_etudiant.setMinimumSize(QSize(130, 0))
        self.modifier_etudiant.setMaximumSize(QSize(16777215, 36))
        self.modifier_etudiant.setFont(font4)
        self.modifier_etudiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.modifier_etudiant.setFlat(True)

        self.horizontalLayout_89.addWidget(self.modifier_etudiant)

        self.supprimer_etudiant = QPushButton(self.frame_226)
        self.supprimer_etudiant.setObjectName(u"supprimer_etudiant")
        self.supprimer_etudiant.setMinimumSize(QSize(130, 0))
        self.supprimer_etudiant.setMaximumSize(QSize(16777215, 36))
        self.supprimer_etudiant.setFont(font4)
        self.supprimer_etudiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_89.addWidget(self.supprimer_etudiant)


        self.horizontalLayout_88.addWidget(self.frame_226, 0, Qt.AlignRight)


        self.verticalLayout_167.addWidget(self.frame_224)

        self.informatios = QFrame(self.scrollAreaWidgetContents_7)
        self.informatios.setObjectName(u"informatios")
        sizePolicy.setHeightForWidth(self.informatios.sizePolicy().hasHeightForWidth())
        self.informatios.setSizePolicy(sizePolicy)
        self.informatios.setFrameShape(QFrame.StyledPanel)
        self.informatios.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_52 = QHBoxLayout(self.informatios)
        self.horizontalLayout_52.setSpacing(40)
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.horizontalLayout_52.setContentsMargins(0, 0, 0, 15)
        self.frame_164 = QFrame(self.informatios)
        self.frame_164.setObjectName(u"frame_164")
        sizePolicy1.setHeightForWidth(self.frame_164.sizePolicy().hasHeightForWidth())
        self.frame_164.setSizePolicy(sizePolicy1)
        self.frame_164.setMinimumSize(QSize(500, 0))
        self.frame_164.setFrameShape(QFrame.StyledPanel)
        self.frame_164.setFrameShadow(QFrame.Raised)
        self.verticalLayout_180 = QVBoxLayout(self.frame_164)
        self.verticalLayout_180.setSpacing(0)
        self.verticalLayout_180.setObjectName(u"verticalLayout_180")
        self.verticalLayout_180.setContentsMargins(-1, 0, -1, 0)
        self.widget_search_student = QWidget(self.frame_164)
        self.widget_search_student.setObjectName(u"widget_search_student")
        self.verticalLayout_164 = QVBoxLayout(self.widget_search_student)
        self.verticalLayout_164.setSpacing(0)
        self.verticalLayout_164.setObjectName(u"verticalLayout_164")
        self.verticalLayout_164.setContentsMargins(0, 0, 0, 0)
        self.tableWidget = QTableWidget(self.widget_search_student)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setFont(font4)

        self.verticalLayout_164.addWidget(self.tableWidget)


        self.verticalLayout_180.addWidget(self.widget_search_student)

        self.frame_171 = QFrame(self.frame_164)
        self.frame_171.setObjectName(u"frame_171")
        self.frame_171.setMaximumSize(QSize(16777215, 60))
        self.frame_171.setFrameShape(QFrame.NoFrame)
        self.frame_171.setFrameShadow(QFrame.Raised)
        self.frame_171.setLineWidth(1)
        self.frame_171.setMidLineWidth(1)
        self.verticalLayout_188 = QVBoxLayout(self.frame_171)
        self.verticalLayout_188.setSpacing(0)
        self.verticalLayout_188.setObjectName(u"verticalLayout_188")
        self.verticalLayout_188.setContentsMargins(0, 0, 0, 0)
        self.frame_172 = QFrame(self.frame_171)
        self.frame_172.setObjectName(u"frame_172")
        self.frame_172.setMaximumSize(QSize(16777215, 42))
        self.frame_172.setFrameShape(QFrame.NoFrame)
        self.frame_172.setFrameShadow(QFrame.Raised)
        self.frame_172.setMidLineWidth(1)
        self.verticalLayout_187 = QVBoxLayout(self.frame_172)
        self.verticalLayout_187.setSpacing(0)
        self.verticalLayout_187.setObjectName(u"verticalLayout_187")
        self.verticalLayout_187.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.frame_172)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font6)

        self.verticalLayout_187.addWidget(self.label_4, 0, Qt.AlignHCenter)


        self.verticalLayout_188.addWidget(self.frame_172)


        self.verticalLayout_180.addWidget(self.frame_171)

        self.frame_195 = QFrame(self.frame_164)
        self.frame_195.setObjectName(u"frame_195")
        font7 = QFont()
        font7.setFamilies([u"Times New Roman"])
        font7.setPointSize(14)
        font7.setBold(False)
        font7.setItalic(False)
        self.frame_195.setFont(font7)
        self.frame_195.setStyleSheet(u"font: 14pt \"Times New Roman\";")
        self.frame_195.setFrameShape(QFrame.StyledPanel)
        self.frame_195.setFrameShadow(QFrame.Raised)
        self.verticalLayout_197 = QVBoxLayout(self.frame_195)
        self.verticalLayout_197.setSpacing(4)
        self.verticalLayout_197.setObjectName(u"verticalLayout_197")
        self.verticalLayout_197.setContentsMargins(12, 0, 12, 0)
        self.frame_196 = QFrame(self.frame_195)
        self.frame_196.setObjectName(u"frame_196")
        self.frame_196.setFrameShape(QFrame.StyledPanel)
        self.frame_196.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_74 = QHBoxLayout(self.frame_196)
        self.horizontalLayout_74.setSpacing(0)
        self.horizontalLayout_74.setObjectName(u"horizontalLayout_74")
        self.horizontalLayout_74.setContentsMargins(0, 0, 0, 0)
        self.label_100 = QLabel(self.frame_196)
        self.label_100.setObjectName(u"label_100")

        self.horizontalLayout_74.addWidget(self.label_100)

        self.label_101 = QLabel(self.frame_196)
        self.label_101.setObjectName(u"label_101")
        self.label_101.setFont(font7)

        self.horizontalLayout_74.addWidget(self.label_101, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_196)

        self.frame_197 = QFrame(self.frame_195)
        self.frame_197.setObjectName(u"frame_197")
        self.frame_197.setFrameShape(QFrame.StyledPanel)
        self.frame_197.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_75 = QHBoxLayout(self.frame_197)
        self.horizontalLayout_75.setSpacing(0)
        self.horizontalLayout_75.setObjectName(u"horizontalLayout_75")
        self.horizontalLayout_75.setContentsMargins(0, 0, 0, 0)
        self.label_102 = QLabel(self.frame_197)
        self.label_102.setObjectName(u"label_102")

        self.horizontalLayout_75.addWidget(self.label_102)

        self.label_103 = QLabel(self.frame_197)
        self.label_103.setObjectName(u"label_103")
        self.label_103.setFont(font7)

        self.horizontalLayout_75.addWidget(self.label_103, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_197)

        self.frame_198 = QFrame(self.frame_195)
        self.frame_198.setObjectName(u"frame_198")
        self.frame_198.setFont(font7)
        self.frame_198.setFrameShape(QFrame.StyledPanel)
        self.frame_198.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_76 = QHBoxLayout(self.frame_198)
        self.horizontalLayout_76.setSpacing(0)
        self.horizontalLayout_76.setObjectName(u"horizontalLayout_76")
        self.horizontalLayout_76.setContentsMargins(0, 0, 0, 0)
        self.label_104 = QLabel(self.frame_198)
        self.label_104.setObjectName(u"label_104")

        self.horizontalLayout_76.addWidget(self.label_104)

        self.label_105 = QLabel(self.frame_198)
        self.label_105.setObjectName(u"label_105")
        self.label_105.setFont(font7)

        self.horizontalLayout_76.addWidget(self.label_105, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_198)

        self.frame_208 = QFrame(self.frame_195)
        self.frame_208.setObjectName(u"frame_208")
        self.frame_208.setFrameShape(QFrame.StyledPanel)
        self.frame_208.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_81 = QHBoxLayout(self.frame_208)
        self.horizontalLayout_81.setSpacing(0)
        self.horizontalLayout_81.setObjectName(u"horizontalLayout_81")
        self.horizontalLayout_81.setContentsMargins(0, 0, 0, 0)
        self.label_114 = QLabel(self.frame_208)
        self.label_114.setObjectName(u"label_114")

        self.horizontalLayout_81.addWidget(self.label_114)

        self.label_115 = QLabel(self.frame_208)
        self.label_115.setObjectName(u"label_115")
        self.label_115.setFont(font7)

        self.horizontalLayout_81.addWidget(self.label_115, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_208)

        self.frame_199 = QFrame(self.frame_195)
        self.frame_199.setObjectName(u"frame_199")
        self.frame_199.setFrameShape(QFrame.StyledPanel)
        self.frame_199.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_80 = QHBoxLayout(self.frame_199)
        self.horizontalLayout_80.setSpacing(0)
        self.horizontalLayout_80.setObjectName(u"horizontalLayout_80")
        self.horizontalLayout_80.setContentsMargins(0, 0, 0, 0)
        self.label_112 = QLabel(self.frame_199)
        self.label_112.setObjectName(u"label_112")

        self.horizontalLayout_80.addWidget(self.label_112)

        self.label_113 = QLabel(self.frame_199)
        self.label_113.setObjectName(u"label_113")
        self.label_113.setFont(font7)

        self.horizontalLayout_80.addWidget(self.label_113, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_199)

        self.frame_200 = QFrame(self.frame_195)
        self.frame_200.setObjectName(u"frame_200")
        self.frame_200.setFrameShape(QFrame.StyledPanel)
        self.frame_200.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_77 = QHBoxLayout(self.frame_200)
        self.horizontalLayout_77.setSpacing(0)
        self.horizontalLayout_77.setObjectName(u"horizontalLayout_77")
        self.horizontalLayout_77.setContentsMargins(0, 0, 0, 0)
        self.label_106 = QLabel(self.frame_200)
        self.label_106.setObjectName(u"label_106")

        self.horizontalLayout_77.addWidget(self.label_106)

        self.label_107 = QLabel(self.frame_200)
        self.label_107.setObjectName(u"label_107")
        self.label_107.setFont(font7)

        self.horizontalLayout_77.addWidget(self.label_107, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_200)

        self.frame_201 = QFrame(self.frame_195)
        self.frame_201.setObjectName(u"frame_201")
        self.frame_201.setFrameShape(QFrame.StyledPanel)
        self.frame_201.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_78 = QHBoxLayout(self.frame_201)
        self.horizontalLayout_78.setSpacing(0)
        self.horizontalLayout_78.setObjectName(u"horizontalLayout_78")
        self.horizontalLayout_78.setContentsMargins(0, 0, 0, 0)
        self.label_108 = QLabel(self.frame_201)
        self.label_108.setObjectName(u"label_108")

        self.horizontalLayout_78.addWidget(self.label_108)

        self.label_109 = QLabel(self.frame_201)
        self.label_109.setObjectName(u"label_109")
        self.label_109.setFont(font7)

        self.horizontalLayout_78.addWidget(self.label_109, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_201)

        self.frame_202 = QFrame(self.frame_195)
        self.frame_202.setObjectName(u"frame_202")
        self.frame_202.setFrameShape(QFrame.StyledPanel)
        self.frame_202.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_79 = QHBoxLayout(self.frame_202)
        self.horizontalLayout_79.setSpacing(0)
        self.horizontalLayout_79.setObjectName(u"horizontalLayout_79")
        self.horizontalLayout_79.setContentsMargins(0, 0, 0, 0)
        self.label_110 = QLabel(self.frame_202)
        self.label_110.setObjectName(u"label_110")

        self.horizontalLayout_79.addWidget(self.label_110)

        self.label_111 = QLabel(self.frame_202)
        self.label_111.setObjectName(u"label_111")
        self.label_111.setFont(font7)

        self.horizontalLayout_79.addWidget(self.label_111, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_202)

        self.frame_407 = QFrame(self.frame_195)
        self.frame_407.setObjectName(u"frame_407")
        self.frame_407.setFrameShape(QFrame.StyledPanel)
        self.frame_407.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_150 = QHBoxLayout(self.frame_407)
        self.horizontalLayout_150.setSpacing(0)
        self.horizontalLayout_150.setObjectName(u"horizontalLayout_150")
        self.horizontalLayout_150.setContentsMargins(0, 0, 0, 0)
        self.label_157 = QLabel(self.frame_407)
        self.label_157.setObjectName(u"label_157")

        self.horizontalLayout_150.addWidget(self.label_157)

        self.label_158 = QLabel(self.frame_407)
        self.label_158.setObjectName(u"label_158")

        self.horizontalLayout_150.addWidget(self.label_158, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_407)

        self.frame_209 = QFrame(self.frame_195)
        self.frame_209.setObjectName(u"frame_209")
        self.frame_209.setFrameShape(QFrame.StyledPanel)
        self.frame_209.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_82 = QHBoxLayout(self.frame_209)
        self.horizontalLayout_82.setSpacing(0)
        self.horizontalLayout_82.setObjectName(u"horizontalLayout_82")
        self.horizontalLayout_82.setContentsMargins(0, 0, 0, 0)
        self.label_116 = QLabel(self.frame_209)
        self.label_116.setObjectName(u"label_116")

        self.horizontalLayout_82.addWidget(self.label_116)

        self.label_117 = QLabel(self.frame_209)
        self.label_117.setObjectName(u"label_117")
        self.label_117.setFont(font7)

        self.horizontalLayout_82.addWidget(self.label_117, 0, Qt.AlignRight)


        self.verticalLayout_197.addWidget(self.frame_209)


        self.verticalLayout_180.addWidget(self.frame_195)


        self.horizontalLayout_52.addWidget(self.frame_164, 0, Qt.AlignHCenter)

        self.frame_166 = QFrame(self.informatios)
        self.frame_166.setObjectName(u"frame_166")
        self.frame_166.setFrameShape(QFrame.StyledPanel)
        self.frame_166.setFrameShadow(QFrame.Raised)
        self.verticalLayout_169 = QVBoxLayout(self.frame_166)
        self.verticalLayout_169.setSpacing(15)
        self.verticalLayout_169.setObjectName(u"verticalLayout_169")
        self.verticalLayout_169.setContentsMargins(-1, 0, 0, 0)
        self.frame_167 = QFrame(self.frame_166)
        self.frame_167.setObjectName(u"frame_167")
        self.frame_167.setFrameShape(QFrame.StyledPanel)
        self.frame_167.setFrameShadow(QFrame.Raised)
        self.verticalLayout_171 = QVBoxLayout(self.frame_167)
        self.verticalLayout_171.setSpacing(0)
        self.verticalLayout_171.setObjectName(u"verticalLayout_171")
        self.verticalLayout_171.setContentsMargins(-1, 0, 0, 0)
        self.frame_169 = QFrame(self.frame_167)
        self.frame_169.setObjectName(u"frame_169")
        self.frame_169.setFrameShape(QFrame.StyledPanel)
        self.frame_169.setFrameShadow(QFrame.Raised)
        self.verticalLayout_190 = QVBoxLayout(self.frame_169)
        self.verticalLayout_190.setSpacing(0)
        self.verticalLayout_190.setObjectName(u"verticalLayout_190")
        self.verticalLayout_190.setContentsMargins(0, 9, 0, 7)
        self.frame_173 = QFrame(self.frame_169)
        self.frame_173.setObjectName(u"frame_173")
        self.frame_173.setMinimumSize(QSize(0, 42))
        self.frame_173.setFrameShape(QFrame.NoFrame)
        self.frame_173.setFrameShadow(QFrame.Raised)
        self.frame_173.setMidLineWidth(1)
        self.verticalLayout_189 = QVBoxLayout(self.frame_173)
        self.verticalLayout_189.setSpacing(0)
        self.verticalLayout_189.setObjectName(u"verticalLayout_189")
        self.verticalLayout_189.setContentsMargins(0, 0, 0, 0)
        self.label_69 = QLabel(self.frame_173)
        self.label_69.setObjectName(u"label_69")
        self.label_69.setFont(font6)

        self.verticalLayout_189.addWidget(self.label_69, 0, Qt.AlignHCenter)


        self.verticalLayout_190.addWidget(self.frame_173)


        self.verticalLayout_171.addWidget(self.frame_169, 0, Qt.AlignTop)

        self.frame_194 = QFrame(self.frame_167)
        self.frame_194.setObjectName(u"frame_194")
        self.frame_194.setStyleSheet(u"font: 14pt \"Times New Roman\";")
        self.frame_194.setFrameShape(QFrame.StyledPanel)
        self.frame_194.setFrameShadow(QFrame.Raised)
        self.verticalLayout_195 = QVBoxLayout(self.frame_194)
        self.verticalLayout_195.setSpacing(4)
        self.verticalLayout_195.setObjectName(u"verticalLayout_195")
        self.verticalLayout_195.setContentsMargins(12, 0, 12, 0)
        self.frame_205 = QFrame(self.frame_194)
        self.frame_205.setObjectName(u"frame_205")
        self.frame_205.setFrameShape(QFrame.StyledPanel)
        self.frame_205.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_71 = QHBoxLayout(self.frame_205)
        self.horizontalLayout_71.setSpacing(0)
        self.horizontalLayout_71.setObjectName(u"horizontalLayout_71")
        self.horizontalLayout_71.setContentsMargins(0, 0, 0, 0)
        self.label_96 = QLabel(self.frame_205)
        self.label_96.setObjectName(u"label_96")

        self.horizontalLayout_71.addWidget(self.label_96)

        self.label_97 = QLabel(self.frame_205)
        self.label_97.setObjectName(u"label_97")
        self.label_97.setFont(font7)

        self.horizontalLayout_71.addWidget(self.label_97, 0, Qt.AlignRight)


        self.verticalLayout_195.addWidget(self.frame_205)

        self.frame_204 = QFrame(self.frame_194)
        self.frame_204.setObjectName(u"frame_204")
        self.frame_204.setFrameShape(QFrame.StyledPanel)
        self.frame_204.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_69 = QHBoxLayout(self.frame_204)
        self.horizontalLayout_69.setSpacing(0)
        self.horizontalLayout_69.setObjectName(u"horizontalLayout_69")
        self.horizontalLayout_69.setContentsMargins(0, 0, 0, 0)
        self.label_98 = QLabel(self.frame_204)
        self.label_98.setObjectName(u"label_98")

        self.horizontalLayout_69.addWidget(self.label_98)

        self.label_99 = QLabel(self.frame_204)
        self.label_99.setObjectName(u"label_99")
        self.label_99.setFont(font7)

        self.horizontalLayout_69.addWidget(self.label_99, 0, Qt.AlignRight)


        self.verticalLayout_195.addWidget(self.frame_204)

        self.frame_203 = QFrame(self.frame_194)
        self.frame_203.setObjectName(u"frame_203")
        self.frame_203.setFrameShape(QFrame.StyledPanel)
        self.frame_203.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_70 = QHBoxLayout(self.frame_203)
        self.horizontalLayout_70.setSpacing(0)
        self.horizontalLayout_70.setObjectName(u"horizontalLayout_70")
        self.horizontalLayout_70.setContentsMargins(0, 0, 0, 0)
        self.label_90 = QLabel(self.frame_203)
        self.label_90.setObjectName(u"label_90")

        self.horizontalLayout_70.addWidget(self.label_90)

        self.label_91 = QLabel(self.frame_203)
        self.label_91.setObjectName(u"label_91")
        self.label_91.setFont(font7)

        self.horizontalLayout_70.addWidget(self.label_91, 0, Qt.AlignRight)


        self.verticalLayout_195.addWidget(self.frame_203)

        self.frame_206 = QFrame(self.frame_194)
        self.frame_206.setObjectName(u"frame_206")
        self.frame_206.setFrameShape(QFrame.StyledPanel)
        self.frame_206.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_72 = QHBoxLayout(self.frame_206)
        self.horizontalLayout_72.setSpacing(0)
        self.horizontalLayout_72.setObjectName(u"horizontalLayout_72")
        self.horizontalLayout_72.setContentsMargins(0, 0, 0, 0)
        self.label_92 = QLabel(self.frame_206)
        self.label_92.setObjectName(u"label_92")

        self.horizontalLayout_72.addWidget(self.label_92)

        self.label_93 = QLabel(self.frame_206)
        self.label_93.setObjectName(u"label_93")
        self.label_93.setFont(font7)

        self.horizontalLayout_72.addWidget(self.label_93, 0, Qt.AlignRight)


        self.verticalLayout_195.addWidget(self.frame_206)

        self.frame_207 = QFrame(self.frame_194)
        self.frame_207.setObjectName(u"frame_207")
        self.frame_207.setFrameShape(QFrame.StyledPanel)
        self.frame_207.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_73 = QHBoxLayout(self.frame_207)
        self.horizontalLayout_73.setSpacing(0)
        self.horizontalLayout_73.setObjectName(u"horizontalLayout_73")
        self.horizontalLayout_73.setContentsMargins(0, 0, 0, 0)
        self.label_94 = QLabel(self.frame_207)
        self.label_94.setObjectName(u"label_94")

        self.horizontalLayout_73.addWidget(self.label_94)

        self.label_95 = QLabel(self.frame_207)
        self.label_95.setObjectName(u"label_95")
        self.label_95.setFont(font7)

        self.horizontalLayout_73.addWidget(self.label_95, 0, Qt.AlignRight)


        self.verticalLayout_195.addWidget(self.frame_207)


        self.verticalLayout_171.addWidget(self.frame_194)


        self.verticalLayout_169.addWidget(self.frame_167)

        self.frame_168 = QFrame(self.frame_166)
        self.frame_168.setObjectName(u"frame_168")
        self.frame_168.setFrameShape(QFrame.StyledPanel)
        self.frame_168.setFrameShadow(QFrame.Raised)
        self.verticalLayout_170 = QVBoxLayout(self.frame_168)
        self.verticalLayout_170.setObjectName(u"verticalLayout_170")
        self.frame_170 = QFrame(self.frame_168)
        self.frame_170.setObjectName(u"frame_170")
        self.frame_170.setMinimumSize(QSize(42, 0))
        self.frame_170.setMaximumSize(QSize(16777215, 42))
        self.frame_170.setFrameShape(QFrame.StyledPanel)
        self.frame_170.setFrameShadow(QFrame.Raised)
        self.verticalLayout_192 = QVBoxLayout(self.frame_170)
        self.verticalLayout_192.setObjectName(u"verticalLayout_192")
        self.frame_184 = QFrame(self.frame_170)
        self.frame_184.setObjectName(u"frame_184")
        self.frame_184.setFrameShape(QFrame.StyledPanel)
        self.frame_184.setFrameShadow(QFrame.Raised)
        self.verticalLayout_191 = QVBoxLayout(self.frame_184)
        self.verticalLayout_191.setSpacing(0)
        self.verticalLayout_191.setObjectName(u"verticalLayout_191")
        self.verticalLayout_191.setContentsMargins(0, 0, 0, 0)
        self.label_70 = QLabel(self.frame_184)
        self.label_70.setObjectName(u"label_70")
        self.label_70.setFont(font6)

        self.verticalLayout_191.addWidget(self.label_70, 0, Qt.AlignHCenter)


        self.verticalLayout_192.addWidget(self.frame_184)


        self.verticalLayout_170.addWidget(self.frame_170)

        self.scrollArea_6 = QScrollArea(self.frame_168)
        self.scrollArea_6.setObjectName(u"scrollArea_6")
        self.scrollArea_6.setMinimumSize(QSize(0, 150))
        self.scrollArea_6.setStyleSheet(u"font: 14pt \"Times New Roman\";")
        self.scrollArea_6.setWidgetResizable(True)
        self.scrollAreaWidgetContents_9 = QWidget()
        self.scrollAreaWidgetContents_9.setObjectName(u"scrollAreaWidgetContents_9")
        self.scrollAreaWidgetContents_9.setGeometry(QRect(0, 0, 437, 150))
        self.scrollAreaWidgetContents_9.setMinimumSize(QSize(0, 50))
        self.scrollArea_6.setWidget(self.scrollAreaWidgetContents_9)

        self.verticalLayout_170.addWidget(self.scrollArea_6)


        self.verticalLayout_169.addWidget(self.frame_168)


        self.horizontalLayout_52.addWidget(self.frame_166)


        self.verticalLayout_167.addWidget(self.informatios)

        self.frame_165 = QFrame(self.scrollAreaWidgetContents_7)
        self.frame_165.setObjectName(u"frame_165")
        self.frame_165.setMaximumSize(QSize(16777215, 42))
        self.frame_165.setFrameShape(QFrame.StyledPanel)
        self.frame_165.setFrameShadow(QFrame.Raised)
        self.verticalLayout_194 = QVBoxLayout(self.frame_165)
        self.verticalLayout_194.setObjectName(u"verticalLayout_194")
        self.verticalLayout_194.setContentsMargins(-1, 9, -1, -1)
        self.frame_193 = QFrame(self.frame_165)
        self.frame_193.setObjectName(u"frame_193")
        self.frame_193.setFrameShape(QFrame.StyledPanel)
        self.frame_193.setFrameShadow(QFrame.Raised)
        self.verticalLayout_193 = QVBoxLayout(self.frame_193)
        self.verticalLayout_193.setSpacing(0)
        self.verticalLayout_193.setObjectName(u"verticalLayout_193")
        self.verticalLayout_193.setContentsMargins(-1, 0, 0, 0)
        self.label_71 = QLabel(self.frame_193)
        self.label_71.setObjectName(u"label_71")
        self.label_71.setFont(font6)

        self.verticalLayout_193.addWidget(self.label_71, 0, Qt.AlignHCenter)


        self.verticalLayout_194.addWidget(self.frame_193)


        self.verticalLayout_167.addWidget(self.frame_165)

        self.widget_parcours = QWidget(self.scrollAreaWidgetContents_7)
        self.widget_parcours.setObjectName(u"widget_parcours")

        self.verticalLayout_167.addWidget(self.widget_parcours)

        self.scrollArea_4.setWidget(self.scrollAreaWidgetContents_7)

        self.verticalLayout_166.addWidget(self.scrollArea_4)

        self.tabWidget.addTab(self.details, "")

        self.verticalLayout_22.addWidget(self.tabWidget)

        self.stackedStudent.addWidget(self.add_student_page)
        self.diplome_page = QWidget()
        self.diplome_page.setObjectName(u"diplome_page")
        self.verticalLayout_344 = QVBoxLayout(self.diplome_page)
        self.verticalLayout_344.setObjectName(u"verticalLayout_344")
        self.frame_397 = QFrame(self.diplome_page)
        self.frame_397.setObjectName(u"frame_397")
        self.frame_397.setFrameShape(QFrame.StyledPanel)
        self.frame_397.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_147 = QHBoxLayout(self.frame_397)
        self.horizontalLayout_147.setObjectName(u"horizontalLayout_147")
        self.frame_398 = QFrame(self.frame_397)
        self.frame_398.setObjectName(u"frame_398")
        self.frame_398.setFrameShape(QFrame.StyledPanel)
        self.frame_398.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_147.addWidget(self.frame_398)

        self.frame_399 = QFrame(self.frame_397)
        self.frame_399.setObjectName(u"frame_399")
        self.frame_399.setFrameShape(QFrame.StyledPanel)
        self.frame_399.setFrameShadow(QFrame.Raised)
        self.verticalLayout_347 = QVBoxLayout(self.frame_399)
        self.verticalLayout_347.setObjectName(u"verticalLayout_347")
        self.frame_400 = QFrame(self.frame_399)
        self.frame_400.setObjectName(u"frame_400")
        self.frame_400.setFrameShape(QFrame.StyledPanel)
        self.frame_400.setFrameShadow(QFrame.Raised)
        self.verticalLayout_345 = QVBoxLayout(self.frame_400)
        self.verticalLayout_345.setObjectName(u"verticalLayout_345")
        self.search_for_deplome = QLineEdit(self.frame_400)
        self.search_for_deplome.setObjectName(u"search_for_deplome")
        self.search_for_deplome.setMinimumSize(QSize(400, 37))
        self.search_for_deplome.setFont(font2)

        self.verticalLayout_345.addWidget(self.search_for_deplome)

        self.diplome_table = QTableWidget(self.frame_400)
        self.diplome_table.setObjectName(u"diplome_table")

        self.verticalLayout_345.addWidget(self.diplome_table)


        self.verticalLayout_347.addWidget(self.frame_400)


        self.horizontalLayout_147.addWidget(self.frame_399, 0, Qt.AlignRight)


        self.verticalLayout_344.addWidget(self.frame_397)

        self.stackedStudent.addWidget(self.diplome_page)
        self.certificat_page = QWidget()
        self.certificat_page.setObjectName(u"certificat_page")
        self.verticalLayout_343 = QVBoxLayout(self.certificat_page)
        self.verticalLayout_343.setObjectName(u"verticalLayout_343")
        self.frame_396 = QFrame(self.certificat_page)
        self.frame_396.setObjectName(u"frame_396")
        self.frame_396.setFrameShape(QFrame.StyledPanel)
        self.frame_396.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_148 = QHBoxLayout(self.frame_396)
        self.horizontalLayout_148.setObjectName(u"horizontalLayout_148")
        self.frame_403 = QFrame(self.frame_396)
        self.frame_403.setObjectName(u"frame_403")
        self.frame_403.setFrameShape(QFrame.StyledPanel)
        self.frame_403.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_148.addWidget(self.frame_403)

        self.frame_401 = QFrame(self.frame_396)
        self.frame_401.setObjectName(u"frame_401")
        self.frame_401.setFrameShape(QFrame.StyledPanel)
        self.frame_401.setFrameShadow(QFrame.Raised)
        self.verticalLayout_348 = QVBoxLayout(self.frame_401)
        self.verticalLayout_348.setObjectName(u"verticalLayout_348")
        self.frame_402 = QFrame(self.frame_401)
        self.frame_402.setObjectName(u"frame_402")
        self.frame_402.setFrameShape(QFrame.StyledPanel)
        self.frame_402.setFrameShadow(QFrame.Raised)
        self.verticalLayout_346 = QVBoxLayout(self.frame_402)
        self.verticalLayout_346.setObjectName(u"verticalLayout_346")
        self.search_for_certificat = QLineEdit(self.frame_402)
        self.search_for_certificat.setObjectName(u"search_for_certificat")
        self.search_for_certificat.setMinimumSize(QSize(400, 37))
        self.search_for_certificat.setFont(font2)

        self.verticalLayout_346.addWidget(self.search_for_certificat)

        self.certificat_table = QTableWidget(self.frame_402)
        self.certificat_table.setObjectName(u"certificat_table")

        self.verticalLayout_346.addWidget(self.certificat_table)


        self.verticalLayout_348.addWidget(self.frame_402)


        self.horizontalLayout_148.addWidget(self.frame_401, 0, Qt.AlignRight)


        self.verticalLayout_343.addWidget(self.frame_396)

        self.stackedStudent.addWidget(self.certificat_page)

        self.verticalLayout_19.addWidget(self.stackedStudent)

        self.stackedWidget.addWidget(self.etudiant_page)
        self.promus_page = QWidget()
        self.promus_page.setObjectName(u"promus_page")
        self.verticalLayout_18 = QVBoxLayout(self.promus_page)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.frame_319 = QFrame(self.promus_page)
        self.frame_319.setObjectName(u"frame_319")
        self.frame_319.setFrameShape(QFrame.StyledPanel)
        self.frame_319.setFrameShadow(QFrame.Raised)
        self.verticalLayout_286 = QVBoxLayout(self.frame_319)
        self.verticalLayout_286.setObjectName(u"verticalLayout_286")
        self.frame_320 = QFrame(self.frame_319)
        self.frame_320.setObjectName(u"frame_320")
        self.frame_320.setFrameShape(QFrame.StyledPanel)
        self.frame_320.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_116 = QHBoxLayout(self.frame_320)
        self.horizontalLayout_116.setObjectName(u"horizontalLayout_116")
        self.horizontalLayout_116.setContentsMargins(0, 0, 0, 0)
        self.frame_323 = QFrame(self.frame_320)
        self.frame_323.setObjectName(u"frame_323")
        self.frame_323.setFrameShape(QFrame.StyledPanel)
        self.frame_323.setFrameShadow(QFrame.Raised)
        self.verticalLayout_287 = QVBoxLayout(self.frame_323)
        self.verticalLayout_287.setSpacing(0)
        self.verticalLayout_287.setObjectName(u"verticalLayout_287")
        self.verticalLayout_287.setContentsMargins(-1, 0, -1, 0)
        self.label_3 = QLabel(self.frame_323)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_287.addWidget(self.label_3)

        self.niveau_for_promus = QComboBox(self.frame_323)
        self.niveau_for_promus.setObjectName(u"niveau_for_promus")
        self.niveau_for_promus.setMaximumSize(QSize(16777215, 37))
        self.niveau_for_promus.setFont(font2)

        self.verticalLayout_287.addWidget(self.niveau_for_promus)


        self.horizontalLayout_116.addWidget(self.frame_323)

        self.frame_324 = QFrame(self.frame_320)
        self.frame_324.setObjectName(u"frame_324")
        self.frame_324.setFrameShape(QFrame.StyledPanel)
        self.frame_324.setFrameShadow(QFrame.Raised)
        self.verticalLayout_288 = QVBoxLayout(self.frame_324)
        self.verticalLayout_288.setSpacing(0)
        self.verticalLayout_288.setObjectName(u"verticalLayout_288")
        self.verticalLayout_288.setContentsMargins(-1, 0, -1, 0)
        self.label_120 = QLabel(self.frame_324)
        self.label_120.setObjectName(u"label_120")

        self.verticalLayout_288.addWidget(self.label_120)

        self.annee_for_promus = QComboBox(self.frame_324)
        self.annee_for_promus.setObjectName(u"annee_for_promus")
        self.annee_for_promus.setMaximumSize(QSize(16777215, 37))
        self.annee_for_promus.setFont(font2)

        self.verticalLayout_288.addWidget(self.annee_for_promus)


        self.horizontalLayout_116.addWidget(self.frame_324)

        self.frame_326 = QFrame(self.frame_320)
        self.frame_326.setObjectName(u"frame_326")
        self.frame_326.setFrameShape(QFrame.StyledPanel)
        self.frame_326.setFrameShadow(QFrame.Raised)
        self.verticalLayout_289 = QVBoxLayout(self.frame_326)
        self.verticalLayout_289.setSpacing(0)
        self.verticalLayout_289.setObjectName(u"verticalLayout_289")
        self.verticalLayout_289.setContentsMargins(-1, 0, -1, 0)
        self.label_121 = QLabel(self.frame_326)
        self.label_121.setObjectName(u"label_121")

        self.verticalLayout_289.addWidget(self.label_121)

        self.classe_for_promus = QComboBox(self.frame_326)
        self.classe_for_promus.setObjectName(u"classe_for_promus")
        self.classe_for_promus.setMinimumSize(QSize(0, 37))
        self.classe_for_promus.setMaximumSize(QSize(16777215, 37))
        self.classe_for_promus.setFont(font2)

        self.verticalLayout_289.addWidget(self.classe_for_promus)


        self.horizontalLayout_116.addWidget(self.frame_326)

        self.frame_325 = QFrame(self.frame_320)
        self.frame_325.setObjectName(u"frame_325")
        self.frame_325.setFrameShape(QFrame.StyledPanel)
        self.frame_325.setFrameShadow(QFrame.Raised)
        self.verticalLayout_290 = QVBoxLayout(self.frame_325)
        self.verticalLayout_290.setSpacing(0)
        self.verticalLayout_290.setObjectName(u"verticalLayout_290")
        self.verticalLayout_290.setContentsMargins(-1, 0, -1, 0)
        self.btn_for_promus = QPushButton(self.frame_325)
        self.btn_for_promus.setObjectName(u"btn_for_promus")
        self.btn_for_promus.setMinimumSize(QSize(35, 0))
        self.btn_for_promus.setMaximumSize(QSize(150, 16777215))
        self.btn_for_promus.setFont(font4)
        self.btn_for_promus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_290.addWidget(self.btn_for_promus)


        self.horizontalLayout_116.addWidget(self.frame_325, 0, Qt.AlignBottom)


        self.verticalLayout_286.addWidget(self.frame_320, 0, Qt.AlignTop)

        self.frame_321 = QFrame(self.frame_319)
        self.frame_321.setObjectName(u"frame_321")
        sizePolicy.setHeightForWidth(self.frame_321.sizePolicy().hasHeightForWidth())
        self.frame_321.setSizePolicy(sizePolicy)
        self.frame_321.setFrameShape(QFrame.StyledPanel)
        self.frame_321.setFrameShadow(QFrame.Raised)

        self.verticalLayout_286.addWidget(self.frame_321)

        self.frame_322 = QFrame(self.frame_319)
        self.frame_322.setObjectName(u"frame_322")
        self.frame_322.setFrameShape(QFrame.StyledPanel)
        self.frame_322.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_117 = QHBoxLayout(self.frame_322)
        self.horizontalLayout_117.setObjectName(u"horizontalLayout_117")
        self.horizontalLayout_117.setContentsMargins(0, 0, 0, 0)
        self.frame_327 = QFrame(self.frame_322)
        self.frame_327.setObjectName(u"frame_327")
        self.frame_327.setFrameShape(QFrame.StyledPanel)
        self.frame_327.setFrameShadow(QFrame.Raised)
        self.verticalLayout_291 = QVBoxLayout(self.frame_327)
        self.verticalLayout_291.setSpacing(0)
        self.verticalLayout_291.setObjectName(u"verticalLayout_291")
        self.verticalLayout_291.setContentsMargins(-1, 0, -1, 0)
        self.label_122 = QLabel(self.frame_327)
        self.label_122.setObjectName(u"label_122")

        self.verticalLayout_291.addWidget(self.label_122)

        self.niveau_promus = QComboBox(self.frame_327)
        self.niveau_promus.setObjectName(u"niveau_promus")
        self.niveau_promus.setMaximumSize(QSize(16777215, 37))
        self.niveau_promus.setFont(font2)

        self.verticalLayout_291.addWidget(self.niveau_promus)


        self.horizontalLayout_117.addWidget(self.frame_327)

        self.frame_328 = QFrame(self.frame_322)
        self.frame_328.setObjectName(u"frame_328")
        self.frame_328.setFrameShape(QFrame.StyledPanel)
        self.frame_328.setFrameShadow(QFrame.Raised)
        self.verticalLayout_294 = QVBoxLayout(self.frame_328)
        self.verticalLayout_294.setSpacing(0)
        self.verticalLayout_294.setObjectName(u"verticalLayout_294")
        self.verticalLayout_294.setContentsMargins(-1, 0, -1, 0)
        self.label_123 = QLabel(self.frame_328)
        self.label_123.setObjectName(u"label_123")

        self.verticalLayout_294.addWidget(self.label_123)

        self.annee_promus = QComboBox(self.frame_328)
        self.annee_promus.setObjectName(u"annee_promus")
        self.annee_promus.setMaximumSize(QSize(16777215, 37))
        self.annee_promus.setFont(font2)

        self.verticalLayout_294.addWidget(self.annee_promus)


        self.horizontalLayout_117.addWidget(self.frame_328)

        self.frame_329 = QFrame(self.frame_322)
        self.frame_329.setObjectName(u"frame_329")
        self.frame_329.setFrameShape(QFrame.StyledPanel)
        self.frame_329.setFrameShadow(QFrame.Raised)
        self.verticalLayout_292 = QVBoxLayout(self.frame_329)
        self.verticalLayout_292.setSpacing(0)
        self.verticalLayout_292.setObjectName(u"verticalLayout_292")
        self.verticalLayout_292.setContentsMargins(-1, 0, -1, 0)
        self.label_124 = QLabel(self.frame_329)
        self.label_124.setObjectName(u"label_124")

        self.verticalLayout_292.addWidget(self.label_124)

        self.classe_promus = QComboBox(self.frame_329)
        self.classe_promus.setObjectName(u"classe_promus")
        self.classe_promus.setMaximumSize(QSize(16777215, 37))
        self.classe_promus.setFont(font2)

        self.verticalLayout_292.addWidget(self.classe_promus)


        self.horizontalLayout_117.addWidget(self.frame_329)

        self.frame_330 = QFrame(self.frame_322)
        self.frame_330.setObjectName(u"frame_330")
        self.frame_330.setFrameShape(QFrame.StyledPanel)
        self.frame_330.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_118 = QHBoxLayout(self.frame_330)
        self.horizontalLayout_118.setSpacing(20)
        self.horizontalLayout_118.setObjectName(u"horizontalLayout_118")
        self.horizontalLayout_118.setContentsMargins(-1, 0, -1, 0)
        self.cancel_promus = QPushButton(self.frame_330)
        self.cancel_promus.setObjectName(u"cancel_promus")
        self.cancel_promus.setFont(font4)
        self.cancel_promus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_118.addWidget(self.cancel_promus)

        self.btn_promus = QPushButton(self.frame_330)
        self.btn_promus.setObjectName(u"btn_promus")
        self.btn_promus.setFont(font4)
        self.btn_promus.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_118.addWidget(self.btn_promus)


        self.horizontalLayout_117.addWidget(self.frame_330, 0, Qt.AlignBottom)


        self.verticalLayout_286.addWidget(self.frame_322, 0, Qt.AlignBottom)


        self.verticalLayout_18.addWidget(self.frame_319)

        self.stackedWidget.addWidget(self.promus_page)
        self.professeur_page = QWidget()
        self.professeur_page.setObjectName(u"professeur_page")
        self.verticalLayout_20 = QVBoxLayout(self.professeur_page)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(-1, 0, -1, 0)
        self.stacked_prof = QStackedWidget(self.professeur_page)
        self.stacked_prof.setObjectName(u"stacked_prof")
        self.index_prof = QWidget()
        self.index_prof.setObjectName(u"index_prof")
        self.verticalLayout_95 = QVBoxLayout(self.index_prof)
        self.verticalLayout_95.setObjectName(u"verticalLayout_95")
        self.verticalLayout_95.setContentsMargins(-1, 0, -1, -1)
        self.frame_84 = QFrame(self.index_prof)
        self.frame_84.setObjectName(u"frame_84")
        self.frame_84.setFrameShape(QFrame.StyledPanel)
        self.frame_84.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_39 = QHBoxLayout(self.frame_84)
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.horizontalLayout_39.setContentsMargins(-1, 0, -1, 0)
        self.add_prof_button = QPushButton(self.frame_84)
        self.add_prof_button.setObjectName(u"add_prof_button")
        self.add_prof_button.setMinimumSize(QSize(175, 32))
        self.add_prof_button.setFont(font4)
        self.add_prof_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_prof_button.setFlat(True)

        self.horizontalLayout_39.addWidget(self.add_prof_button)


        self.verticalLayout_95.addWidget(self.frame_84, 0, Qt.AlignLeft)

        self.frame_82 = QFrame(self.index_prof)
        self.frame_82.setObjectName(u"frame_82")
        self.frame_82.setMinimumSize(QSize(400, 0))
        self.frame_82.setFrameShape(QFrame.StyledPanel)
        self.frame_82.setFrameShadow(QFrame.Raised)
        self.verticalLayout_93 = QVBoxLayout(self.frame_82)
        self.verticalLayout_93.setSpacing(0)
        self.verticalLayout_93.setObjectName(u"verticalLayout_93")
        self.verticalLayout_93.setContentsMargins(0, 0, -1, 0)
        self.search_prof = QLineEdit(self.frame_82)
        self.search_prof.setObjectName(u"search_prof")

        self.verticalLayout_93.addWidget(self.search_prof)


        self.verticalLayout_95.addWidget(self.frame_82, 0, Qt.AlignRight)

        self.frame_85 = QFrame(self.index_prof)
        self.frame_85.setObjectName(u"frame_85")
        sizePolicy.setHeightForWidth(self.frame_85.sizePolicy().hasHeightForWidth())
        self.frame_85.setSizePolicy(sizePolicy)
        self.frame_85.setFrameShape(QFrame.StyledPanel)
        self.frame_85.setFrameShadow(QFrame.Raised)
        self.verticalLayout_94 = QVBoxLayout(self.frame_85)
        self.verticalLayout_94.setSpacing(0)
        self.verticalLayout_94.setObjectName(u"verticalLayout_94")
        self.verticalLayout_94.setContentsMargins(0, 0, 0, 0)
        self.prof_table = QTableWidget(self.frame_85)
        self.prof_table.setObjectName(u"prof_table")
        self.prof_table.setFont(font4)
        self.prof_table.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.PointingHandCursor))
        self.prof_table.setEditTriggers(QAbstractItemView.AnyKeyPressed)
        self.prof_table.setSortingEnabled(True)
        self.prof_table.setWordWrap(False)
        self.prof_table.horizontalHeader().setMinimumSectionSize(150)
        self.prof_table.horizontalHeader().setStretchLastSection(True)
        self.prof_table.verticalHeader().setVisible(False)
        self.prof_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_94.addWidget(self.prof_table)


        self.verticalLayout_95.addWidget(self.frame_85)

        self.frame_83 = QFrame(self.index_prof)
        self.frame_83.setObjectName(u"frame_83")
        self.frame_83.setMinimumSize(QSize(0, 15))
        self.frame_83.setFrameShape(QFrame.StyledPanel)
        self.frame_83.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_38 = QHBoxLayout(self.frame_83)
        self.horizontalLayout_38.setSpacing(15)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.prof_prev = QPushButton(self.frame_83)
        self.prof_prev.setObjectName(u"prof_prev")
        self.prof_prev.setFlat(True)

        self.horizontalLayout_38.addWidget(self.prof_prev)

        self.prof_label = QLabel(self.frame_83)
        self.prof_label.setObjectName(u"prof_label")

        self.horizontalLayout_38.addWidget(self.prof_label)

        self.prof_next = QPushButton(self.frame_83)
        self.prof_next.setObjectName(u"prof_next")
        self.prof_next.setFlat(True)

        self.horizontalLayout_38.addWidget(self.prof_next)


        self.verticalLayout_95.addWidget(self.frame_83, 0, Qt.AlignRight)

        self.stacked_prof.addWidget(self.index_prof)
        self.details_prof = QWidget()
        self.details_prof.setObjectName(u"details_prof")
        self.stacked_prof.addWidget(self.details_prof)
        self.add_prof = QWidget()
        self.add_prof.setObjectName(u"add_prof")
        self.verticalLayout_92 = QVBoxLayout(self.add_prof)
        self.verticalLayout_92.setObjectName(u"verticalLayout_92")
        self.verticalLayout_92.setContentsMargins(-1, 0, -1, -1)
        self.scrollArea_7 = QScrollArea(self.add_prof)
        self.scrollArea_7.setObjectName(u"scrollArea_7")
        self.scrollArea_7.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 770, 588))
        self.verticalLayout_310 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_310.setObjectName(u"verticalLayout_310")
        self.frame_71 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_71.setObjectName(u"frame_71")
        self.frame_71.setFrameShape(QFrame.StyledPanel)
        self.frame_71.setFrameShadow(QFrame.Raised)
        self.verticalLayout_82 = QVBoxLayout(self.frame_71)
        self.verticalLayout_82.setSpacing(0)
        self.verticalLayout_82.setObjectName(u"verticalLayout_82")
        self.verticalLayout_82.setContentsMargins(-1, 0, -1, 0)
        self.widget_6 = QWidget(self.frame_71)
        self.widget_6.setObjectName(u"widget_6")
        self.horizontalLayout_37 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_37.setSpacing(0)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalLayout_37.setContentsMargins(-1, 0, -1, 0)
        self.frame_72 = QFrame(self.widget_6)
        self.frame_72.setObjectName(u"frame_72")
        self.frame_72.setFrameShape(QFrame.StyledPanel)
        self.frame_72.setFrameShadow(QFrame.Raised)
        self.verticalLayout_83 = QVBoxLayout(self.frame_72)
        self.verticalLayout_83.setSpacing(0)
        self.verticalLayout_83.setObjectName(u"verticalLayout_83")
        self.verticalLayout_83.setContentsMargins(-1, 0, -1, 0)
        self.frame_73 = QFrame(self.frame_72)
        self.frame_73.setObjectName(u"frame_73")
        self.frame_73.setFrameShape(QFrame.StyledPanel)
        self.frame_73.setFrameShadow(QFrame.Raised)
        self.verticalLayout_84 = QVBoxLayout(self.frame_73)
        self.verticalLayout_84.setObjectName(u"verticalLayout_84")
        self.verticalLayout_84.setContentsMargins(-1, 0, -1, 0)
        self.label_5 = QLabel(self.frame_73)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_84.addWidget(self.label_5)

        self.nom_prof = QLineEdit(self.frame_73)
        self.nom_prof.setObjectName(u"nom_prof")
        self.nom_prof.setFont(font2)

        self.verticalLayout_84.addWidget(self.nom_prof)


        self.verticalLayout_83.addWidget(self.frame_73, 0, Qt.AlignTop)

        self.frame_74 = QFrame(self.frame_72)
        self.frame_74.setObjectName(u"frame_74")
        self.frame_74.setFrameShape(QFrame.StyledPanel)
        self.frame_74.setFrameShadow(QFrame.Raised)
        self.verticalLayout_85 = QVBoxLayout(self.frame_74)
        self.verticalLayout_85.setObjectName(u"verticalLayout_85")
        self.verticalLayout_85.setContentsMargins(-1, 0, -1, 0)
        self.label_19 = QLabel(self.frame_74)
        self.label_19.setObjectName(u"label_19")

        self.verticalLayout_85.addWidget(self.label_19)

        self.sexe_prof = QLineEdit(self.frame_74)
        self.sexe_prof.setObjectName(u"sexe_prof")
        self.sexe_prof.setFont(font2)

        self.verticalLayout_85.addWidget(self.sexe_prof)


        self.verticalLayout_83.addWidget(self.frame_74, 0, Qt.AlignTop)

        self.frame_75 = QFrame(self.frame_72)
        self.frame_75.setObjectName(u"frame_75")
        self.frame_75.setFrameShape(QFrame.StyledPanel)
        self.frame_75.setFrameShadow(QFrame.Raised)
        self.verticalLayout_86 = QVBoxLayout(self.frame_75)
        self.verticalLayout_86.setObjectName(u"verticalLayout_86")
        self.verticalLayout_86.setContentsMargins(-1, 0, -1, 0)
        self.label_20 = QLabel(self.frame_75)
        self.label_20.setObjectName(u"label_20")

        self.verticalLayout_86.addWidget(self.label_20)

        self.telephone_prof = QLineEdit(self.frame_75)
        self.telephone_prof.setObjectName(u"telephone_prof")
        self.telephone_prof.setFont(font2)

        self.verticalLayout_86.addWidget(self.telephone_prof)


        self.verticalLayout_83.addWidget(self.frame_75, 0, Qt.AlignTop)

        self.frame_86 = QFrame(self.frame_72)
        self.frame_86.setObjectName(u"frame_86")
        self.frame_86.setFrameShape(QFrame.StyledPanel)
        self.frame_86.setFrameShadow(QFrame.Raised)
        self.verticalLayout_96 = QVBoxLayout(self.frame_86)
        self.verticalLayout_96.setSpacing(0)
        self.verticalLayout_96.setObjectName(u"verticalLayout_96")
        self.verticalLayout_96.setContentsMargins(-1, 0, -1, 0)
        self.label_24 = QLabel(self.frame_86)
        self.label_24.setObjectName(u"label_24")

        self.verticalLayout_96.addWidget(self.label_24)

        self.matiere_enseignee = QLineEdit(self.frame_86)
        self.matiere_enseignee.setObjectName(u"matiere_enseignee")
        self.matiere_enseignee.setFont(font2)

        self.verticalLayout_96.addWidget(self.matiere_enseignee)


        self.verticalLayout_83.addWidget(self.frame_86)


        self.horizontalLayout_37.addWidget(self.frame_72)

        self.frame_76 = QFrame(self.widget_6)
        self.frame_76.setObjectName(u"frame_76")
        self.frame_76.setFrameShape(QFrame.StyledPanel)
        self.frame_76.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_37.addWidget(self.frame_76)

        self.frame_77 = QFrame(self.widget_6)
        self.frame_77.setObjectName(u"frame_77")
        self.frame_77.setFrameShape(QFrame.StyledPanel)
        self.frame_77.setFrameShadow(QFrame.Raised)
        self.verticalLayout_87 = QVBoxLayout(self.frame_77)
        self.verticalLayout_87.setSpacing(0)
        self.verticalLayout_87.setObjectName(u"verticalLayout_87")
        self.verticalLayout_87.setContentsMargins(9, 0, -1, 0)
        self.frame_78 = QFrame(self.frame_77)
        self.frame_78.setObjectName(u"frame_78")
        self.frame_78.setFrameShape(QFrame.StyledPanel)
        self.frame_78.setFrameShadow(QFrame.Raised)
        self.verticalLayout_88 = QVBoxLayout(self.frame_78)
        self.verticalLayout_88.setObjectName(u"verticalLayout_88")
        self.verticalLayout_88.setContentsMargins(-1, 0, -1, 0)
        self.label_21 = QLabel(self.frame_78)
        self.label_21.setObjectName(u"label_21")

        self.verticalLayout_88.addWidget(self.label_21)

        self.prenom_prof = QLineEdit(self.frame_78)
        self.prenom_prof.setObjectName(u"prenom_prof")
        self.prenom_prof.setFont(font2)

        self.verticalLayout_88.addWidget(self.prenom_prof)


        self.verticalLayout_87.addWidget(self.frame_78, 0, Qt.AlignTop)

        self.frame_79 = QFrame(self.frame_77)
        self.frame_79.setObjectName(u"frame_79")
        self.frame_79.setFrameShape(QFrame.StyledPanel)
        self.frame_79.setFrameShadow(QFrame.Raised)
        self.verticalLayout_89 = QVBoxLayout(self.frame_79)
        self.verticalLayout_89.setObjectName(u"verticalLayout_89")
        self.verticalLayout_89.setContentsMargins(-1, 0, -1, 0)
        self.label_22 = QLabel(self.frame_79)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_89.addWidget(self.label_22)

        self.email_prof = QLineEdit(self.frame_79)
        self.email_prof.setObjectName(u"email_prof")
        self.email_prof.setFont(font2)

        self.verticalLayout_89.addWidget(self.email_prof)


        self.verticalLayout_87.addWidget(self.frame_79, 0, Qt.AlignTop)

        self.frame_80 = QFrame(self.frame_77)
        self.frame_80.setObjectName(u"frame_80")
        self.frame_80.setFrameShape(QFrame.StyledPanel)
        self.frame_80.setFrameShadow(QFrame.Raised)
        self.verticalLayout_90 = QVBoxLayout(self.frame_80)
        self.verticalLayout_90.setObjectName(u"verticalLayout_90")
        self.verticalLayout_90.setContentsMargins(-1, 0, -1, 0)
        self.label_23 = QLabel(self.frame_80)
        self.label_23.setObjectName(u"label_23")

        self.verticalLayout_90.addWidget(self.label_23)

        self.adresse_prof = QLineEdit(self.frame_80)
        self.adresse_prof.setObjectName(u"adresse_prof")
        self.adresse_prof.setFont(font2)

        self.verticalLayout_90.addWidget(self.adresse_prof)


        self.verticalLayout_87.addWidget(self.frame_80, 0, Qt.AlignTop)

        self.frame_87 = QFrame(self.frame_77)
        self.frame_87.setObjectName(u"frame_87")
        self.frame_87.setFrameShape(QFrame.StyledPanel)
        self.frame_87.setFrameShadow(QFrame.Raised)
        self.verticalLayout_97 = QVBoxLayout(self.frame_87)
        self.verticalLayout_97.setObjectName(u"verticalLayout_97")
        self.frame_88 = QFrame(self.frame_87)
        self.frame_88.setObjectName(u"frame_88")
        self.frame_88.setFrameShape(QFrame.StyledPanel)
        self.frame_88.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_40 = QHBoxLayout(self.frame_88)
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.notif_prof = QCheckBox(self.frame_88)
        self.notif_prof.setObjectName(u"notif_prof")

        self.horizontalLayout_40.addWidget(self.notif_prof)

        self.label_25 = QLabel(self.frame_88)
        self.label_25.setObjectName(u"label_25")

        self.horizontalLayout_40.addWidget(self.label_25)


        self.verticalLayout_97.addWidget(self.frame_88)


        self.verticalLayout_87.addWidget(self.frame_87, 0, Qt.AlignRight|Qt.AlignBottom)


        self.horizontalLayout_37.addWidget(self.frame_77)


        self.verticalLayout_82.addWidget(self.widget_6)

        self.frame_81 = QFrame(self.frame_71)
        self.frame_81.setObjectName(u"frame_81")
        self.frame_81.setFrameShape(QFrame.StyledPanel)
        self.frame_81.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_109 = QHBoxLayout(self.frame_81)
        self.horizontalLayout_109.setObjectName(u"horizontalLayout_109")
        self.horizontalLayout_109.setContentsMargins(-1, 0, 40, 0)
        self.frame_302 = QFrame(self.frame_81)
        self.frame_302.setObjectName(u"frame_302")
        self.frame_302.setFrameShape(QFrame.StyledPanel)
        self.frame_302.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_108 = QHBoxLayout(self.frame_302)
        self.horizontalLayout_108.setObjectName(u"horizontalLayout_108")
        self.delete_prof = QPushButton(self.frame_302)
        self.delete_prof.setObjectName(u"delete_prof")
        self.delete_prof.setMinimumSize(QSize(120, 0))
        self.delete_prof.setMaximumSize(QSize(16777215, 35))
        self.delete_prof.setFont(font4)
        self.delete_prof.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_108.addWidget(self.delete_prof)


        self.horizontalLayout_109.addWidget(self.frame_302)

        self.enregistrer_prof = QPushButton(self.frame_81)
        self.enregistrer_prof.setObjectName(u"enregistrer_prof")
        self.enregistrer_prof.setMinimumSize(QSize(140, 32))
        self.enregistrer_prof.setMaximumSize(QSize(16777215, 35))
        self.enregistrer_prof.setFont(font4)
        self.enregistrer_prof.setFlat(True)

        self.horizontalLayout_109.addWidget(self.enregistrer_prof)


        self.verticalLayout_82.addWidget(self.frame_81, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout_310.addWidget(self.frame_71)

        self.frame_313 = QFrame(self.scrollAreaWidgetContents_2)
        self.frame_313.setObjectName(u"frame_313")
        self.frame_313.setFrameShape(QFrame.StyledPanel)
        self.frame_313.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_114 = QHBoxLayout(self.frame_313)
        self.horizontalLayout_114.setObjectName(u"horizontalLayout_114")
        self.frame_314 = QFrame(self.frame_313)
        self.frame_314.setObjectName(u"frame_314")
        self.frame_314.setMinimumSize(QSize(400, 0))
        self.frame_314.setFrameShape(QFrame.StyledPanel)
        self.frame_314.setFrameShadow(QFrame.Raised)
        self.verticalLayout_280 = QVBoxLayout(self.frame_314)
        self.verticalLayout_280.setObjectName(u"verticalLayout_280")
        self.label_118 = QLabel(self.frame_314)
        self.label_118.setObjectName(u"label_118")

        self.verticalLayout_280.addWidget(self.label_118)

        self.frame_317 = QFrame(self.frame_314)
        self.frame_317.setObjectName(u"frame_317")
        self.frame_317.setFrameShape(QFrame.StyledPanel)
        self.frame_317.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_115 = QHBoxLayout(self.frame_317)
        self.horizontalLayout_115.setObjectName(u"horizontalLayout_115")
        self.prof_status = QLabel(self.frame_317)
        self.prof_status.setObjectName(u"prof_status")

        self.horizontalLayout_115.addWidget(self.prof_status)

        self.status_prof_change = QPushButton(self.frame_317)
        self.status_prof_change.setObjectName(u"status_prof_change")
        self.status_prof_change.setFont(font4)
        self.status_prof_change.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_115.addWidget(self.status_prof_change)


        self.verticalLayout_280.addWidget(self.frame_317, 0, Qt.AlignTop)


        self.horizontalLayout_114.addWidget(self.frame_314, 0, Qt.AlignTop)

        self.frame_315 = QFrame(self.frame_313)
        self.frame_315.setObjectName(u"frame_315")
        self.frame_315.setFrameShape(QFrame.StyledPanel)
        self.frame_315.setFrameShadow(QFrame.Raised)
        self.verticalLayout_309 = QVBoxLayout(self.frame_315)
        self.verticalLayout_309.setObjectName(u"verticalLayout_309")
        self.frame_346 = QFrame(self.frame_315)
        self.frame_346.setObjectName(u"frame_346")
        self.frame_346.setFrameShape(QFrame.StyledPanel)
        self.frame_346.setFrameShadow(QFrame.Raised)
        self.verticalLayout_305 = QVBoxLayout(self.frame_346)
        self.verticalLayout_305.setSpacing(6)
        self.verticalLayout_305.setObjectName(u"verticalLayout_305")
        self.verticalLayout_305.setContentsMargins(-1, 0, -1, 0)
        self.frame_347 = QFrame(self.frame_346)
        self.frame_347.setObjectName(u"frame_347")
        self.frame_347.setFrameShape(QFrame.StyledPanel)
        self.frame_347.setFrameShadow(QFrame.Raised)
        self.verticalLayout_306 = QVBoxLayout(self.frame_347)
        self.verticalLayout_306.setSpacing(8)
        self.verticalLayout_306.setObjectName(u"verticalLayout_306")
        self.verticalLayout_306.setContentsMargins(-1, 0, -1, 0)
        self.label_131 = QLabel(self.frame_347)
        self.label_131.setObjectName(u"label_131")

        self.verticalLayout_306.addWidget(self.label_131)

        self.label_132 = QLabel(self.frame_347)
        self.label_132.setObjectName(u"label_132")

        self.verticalLayout_306.addWidget(self.label_132)

        self.reset_password_prof = QLineEdit(self.frame_347)
        self.reset_password_prof.setObjectName(u"reset_password_prof")
        self.reset_password_prof.setFont(font2)
        self.reset_password_prof.setEchoMode(QLineEdit.Password)

        self.verticalLayout_306.addWidget(self.reset_password_prof)


        self.verticalLayout_305.addWidget(self.frame_347)

        self.frame_348 = QFrame(self.frame_346)
        self.frame_348.setObjectName(u"frame_348")
        self.frame_348.setFrameShape(QFrame.StyledPanel)
        self.frame_348.setFrameShadow(QFrame.Raised)
        self.verticalLayout_307 = QVBoxLayout(self.frame_348)
        self.verticalLayout_307.setSpacing(0)
        self.verticalLayout_307.setObjectName(u"verticalLayout_307")
        self.verticalLayout_307.setContentsMargins(-1, 0, -1, 0)
        self.label_133 = QLabel(self.frame_348)
        self.label_133.setObjectName(u"label_133")

        self.verticalLayout_307.addWidget(self.label_133)

        self.confirm_reset_password_prof = QLineEdit(self.frame_348)
        self.confirm_reset_password_prof.setObjectName(u"confirm_reset_password_prof")
        self.confirm_reset_password_prof.setFont(font2)
        self.confirm_reset_password_prof.setEchoMode(QLineEdit.Password)

        self.verticalLayout_307.addWidget(self.confirm_reset_password_prof)


        self.verticalLayout_305.addWidget(self.frame_348)

        self.frame_349 = QFrame(self.frame_346)
        self.frame_349.setObjectName(u"frame_349")
        self.frame_349.setFrameShape(QFrame.StyledPanel)
        self.frame_349.setFrameShadow(QFrame.Raised)
        self.verticalLayout_308 = QVBoxLayout(self.frame_349)
        self.verticalLayout_308.setObjectName(u"verticalLayout_308")
        self.btn_reset_password_prof = QPushButton(self.frame_349)
        self.btn_reset_password_prof.setObjectName(u"btn_reset_password_prof")
        self.btn_reset_password_prof.setFont(font4)
        self.btn_reset_password_prof.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_308.addWidget(self.btn_reset_password_prof)


        self.verticalLayout_305.addWidget(self.frame_349)


        self.verticalLayout_309.addWidget(self.frame_346)


        self.horizontalLayout_114.addWidget(self.frame_315)

        self.frame_316 = QFrame(self.frame_313)
        self.frame_316.setObjectName(u"frame_316")
        self.frame_316.setFrameShape(QFrame.StyledPanel)
        self.frame_316.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_114.addWidget(self.frame_316)


        self.verticalLayout_310.addWidget(self.frame_313)

        self.scrollArea_7.setWidget(self.scrollAreaWidgetContents_2)

        self.verticalLayout_92.addWidget(self.scrollArea_7)

        self.stacked_prof.addWidget(self.add_prof)

        self.verticalLayout_20.addWidget(self.stacked_prof)

        self.stackedWidget.addWidget(self.professeur_page)
        self.cours_page = QWidget()
        self.cours_page.setObjectName(u"cours_page")
        self.verticalLayout_100 = QVBoxLayout(self.cours_page)
        self.verticalLayout_100.setObjectName(u"verticalLayout_100")
        self.verticalLayout_100.setContentsMargins(-1, 0, -1, -1)
        self.frame_91 = QFrame(self.cours_page)
        self.frame_91.setObjectName(u"frame_91")
        self.frame_91.setFrameShape(QFrame.StyledPanel)
        self.frame_91.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_41 = QHBoxLayout(self.frame_91)
        self.horizontalLayout_41.setSpacing(50)
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.horizontalLayout_41.setContentsMargins(-1, 0, -1, 0)
        self.cours_stack = QPushButton(self.frame_91)
        self.cours_stack.setObjectName(u"cours_stack")
        self.cours_stack.setMinimumSize(QSize(150, 33))
        self.cours_stack.setFont(font4)
        self.cours_stack.setCheckable(True)
        self.cours_stack.setChecked(True)
        self.cours_stack.setAutoExclusive(True)
        self.cours_stack.setFlat(True)

        self.horizontalLayout_41.addWidget(self.cours_stack)

        self.programme_stack = QPushButton(self.frame_91)
        self.programme_stack.setObjectName(u"programme_stack")
        self.programme_stack.setMinimumSize(QSize(150, 33))
        self.programme_stack.setFont(font4)
        self.programme_stack.setCheckable(True)
        self.programme_stack.setAutoExclusive(True)
        self.programme_stack.setFlat(True)

        self.horizontalLayout_41.addWidget(self.programme_stack)


        self.verticalLayout_100.addWidget(self.frame_91, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_92 = QFrame(self.cours_page)
        self.frame_92.setObjectName(u"frame_92")
        sizePolicy.setHeightForWidth(self.frame_92.sizePolicy().hasHeightForWidth())
        self.frame_92.setSizePolicy(sizePolicy)
        self.frame_92.setFrameShape(QFrame.StyledPanel)
        self.frame_92.setFrameShadow(QFrame.Raised)
        self.verticalLayout_101 = QVBoxLayout(self.frame_92)
        self.verticalLayout_101.setObjectName(u"verticalLayout_101")
        self.verticalLayout_101.setContentsMargins(-1, 0, -1, 0)
        self.coursStaked = QStackedWidget(self.frame_92)
        self.coursStaked.setObjectName(u"coursStaked")
        self.cours_staked_page = QWidget()
        self.cours_staked_page.setObjectName(u"cours_staked_page")
        self.verticalLayout_102 = QVBoxLayout(self.cours_staked_page)
        self.verticalLayout_102.setObjectName(u"verticalLayout_102")
        self.stackedWidgetCours = QStackedWidget(self.cours_staked_page)
        self.stackedWidgetCours.setObjectName(u"stackedWidgetCours")
        self.index_cours = QWidget()
        self.index_cours.setObjectName(u"index_cours")
        self.verticalLayout_103 = QVBoxLayout(self.index_cours)
        self.verticalLayout_103.setObjectName(u"verticalLayout_103")
        self.frame_93 = QFrame(self.index_cours)
        self.frame_93.setObjectName(u"frame_93")
        self.frame_93.setFrameShape(QFrame.StyledPanel)
        self.frame_93.setFrameShadow(QFrame.Raised)
        self.verticalLayout_104 = QVBoxLayout(self.frame_93)
        self.verticalLayout_104.setObjectName(u"verticalLayout_104")
        self.verticalLayout_104.setContentsMargins(-1, 0, -1, 0)
        self.addCours = QPushButton(self.frame_93)
        self.addCours.setObjectName(u"addCours")
        self.addCours.setMinimumSize(QSize(150, 0))
        self.addCours.setFont(font4)
        self.addCours.setFlat(True)

        self.verticalLayout_104.addWidget(self.addCours)


        self.verticalLayout_103.addWidget(self.frame_93, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_94 = QFrame(self.index_cours)
        self.frame_94.setObjectName(u"frame_94")
        self.frame_94.setFrameShape(QFrame.StyledPanel)
        self.frame_94.setFrameShadow(QFrame.Raised)
        self.verticalLayout_105 = QVBoxLayout(self.frame_94)
        self.verticalLayout_105.setObjectName(u"verticalLayout_105")
        self.verticalLayout_105.setContentsMargins(-1, 0, -1, 0)
        self.search_cours = QLineEdit(self.frame_94)
        self.search_cours.setObjectName(u"search_cours")
        self.search_cours.setMinimumSize(QSize(400, 37))
        self.search_cours.setFont(font2)

        self.verticalLayout_105.addWidget(self.search_cours)


        self.verticalLayout_103.addWidget(self.frame_94, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_95 = QFrame(self.index_cours)
        self.frame_95.setObjectName(u"frame_95")
        sizePolicy.setHeightForWidth(self.frame_95.sizePolicy().hasHeightForWidth())
        self.frame_95.setSizePolicy(sizePolicy)
        self.frame_95.setFrameShape(QFrame.StyledPanel)
        self.frame_95.setFrameShadow(QFrame.Raised)
        self.verticalLayout_106 = QVBoxLayout(self.frame_95)
        self.verticalLayout_106.setSpacing(0)
        self.verticalLayout_106.setObjectName(u"verticalLayout_106")
        self.verticalLayout_106.setContentsMargins(0, 0, 0, 0)
        self.cours_table = QTableWidget(self.frame_95)
        self.cours_table.setObjectName(u"cours_table")
        self.cours_table.setSortingEnabled(True)
        self.cours_table.horizontalHeader().setMinimumSectionSize(100)
        self.cours_table.horizontalHeader().setStretchLastSection(True)
        self.cours_table.verticalHeader().setVisible(False)
        self.cours_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_106.addWidget(self.cours_table)

        self.frame_332 = QFrame(self.frame_95)
        self.frame_332.setObjectName(u"frame_332")
        self.frame_332.setFrameShape(QFrame.StyledPanel)
        self.frame_332.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_120 = QHBoxLayout(self.frame_332)
        self.horizontalLayout_120.setSpacing(27)
        self.horizontalLayout_120.setObjectName(u"horizontalLayout_120")
        self.prev_cours = QPushButton(self.frame_332)
        self.prev_cours.setObjectName(u"prev_cours")
        self.prev_cours.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_120.addWidget(self.prev_cours)

        self.next_cours = QPushButton(self.frame_332)
        self.next_cours.setObjectName(u"next_cours")
        self.next_cours.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_120.addWidget(self.next_cours)


        self.verticalLayout_106.addWidget(self.frame_332, 0, Qt.AlignRight)


        self.verticalLayout_103.addWidget(self.frame_95)

        self.stackedWidgetCours.addWidget(self.index_cours)
        self.add_cours = QWidget()
        self.add_cours.setObjectName(u"add_cours")
        self.verticalLayout_107 = QVBoxLayout(self.add_cours)
        self.verticalLayout_107.setObjectName(u"verticalLayout_107")
        self.verticalLayout_107.setContentsMargins(-1, 0, -1, 0)
        self.frame_96 = QFrame(self.add_cours)
        self.frame_96.setObjectName(u"frame_96")
        self.frame_96.setFrameShape(QFrame.StyledPanel)
        self.frame_96.setFrameShadow(QFrame.Raised)
        self.verticalLayout_108 = QVBoxLayout(self.frame_96)
        self.verticalLayout_108.setObjectName(u"verticalLayout_108")
        self.verticalLayout_108.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.frame_96)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_10 = QWidget()
        self.scrollAreaWidgetContents_10.setObjectName(u"scrollAreaWidgetContents_10")
        self.scrollAreaWidgetContents_10.setGeometry(QRect(0, 0, 16, 16))
        self.verticalLayout_165 = QVBoxLayout(self.scrollAreaWidgetContents_10)
        self.verticalLayout_165.setSpacing(12)
        self.verticalLayout_165.setObjectName(u"verticalLayout_165")
        self.verticalLayout_165.setContentsMargins(0, 0, 0, 0)
        self.widget_10 = QWidget(self.scrollAreaWidgetContents_10)
        self.widget_10.setObjectName(u"widget_10")

        self.verticalLayout_165.addWidget(self.widget_10)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_10)

        self.verticalLayout_108.addWidget(self.scrollArea_2)

        self.frame_98 = QFrame(self.frame_96)
        self.frame_98.setObjectName(u"frame_98")
        self.frame_98.setFrameShape(QFrame.StyledPanel)
        self.frame_98.setFrameShadow(QFrame.Raised)
        self.verticalLayout_109 = QVBoxLayout(self.frame_98)
        self.verticalLayout_109.setObjectName(u"verticalLayout_109")
        self.verticalLayout_109.setContentsMargins(-1, 0, -1, 0)
        self.frame_100 = QFrame(self.frame_98)
        self.frame_100.setObjectName(u"frame_100")
        self.frame_100.setFrameShape(QFrame.StyledPanel)
        self.frame_100.setFrameShadow(QFrame.Raised)
        self.verticalLayout_110 = QVBoxLayout(self.frame_100)
        self.verticalLayout_110.setObjectName(u"verticalLayout_110")
        self.verticalLayout_110.setContentsMargins(-1, 0, -1, 0)
        self.add_course_line = QPushButton(self.frame_100)
        self.add_course_line.setObjectName(u"add_course_line")
        self.add_course_line.setMinimumSize(QSize(169, 33))
        self.add_course_line.setFont(font4)
        self.add_course_line.setFlat(True)

        self.verticalLayout_110.addWidget(self.add_course_line)


        self.verticalLayout_109.addWidget(self.frame_100, 0, Qt.AlignLeft|Qt.AlignBottom)

        self.frame_99 = QFrame(self.frame_98)
        self.frame_99.setObjectName(u"frame_99")
        self.frame_99.setFrameShape(QFrame.StyledPanel)
        self.frame_99.setFrameShadow(QFrame.Raised)
        self.verticalLayout_111 = QVBoxLayout(self.frame_99)
        self.verticalLayout_111.setObjectName(u"verticalLayout_111")
        self.verticalLayout_111.setContentsMargins(-1, 0, -1, 0)
        self.enregistrer_cours = QPushButton(self.frame_99)
        self.enregistrer_cours.setObjectName(u"enregistrer_cours")
        self.enregistrer_cours.setMinimumSize(QSize(150, 33))
        self.enregistrer_cours.setFont(font4)
        self.enregistrer_cours.setFlat(True)

        self.verticalLayout_111.addWidget(self.enregistrer_cours)


        self.verticalLayout_109.addWidget(self.frame_99, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_108.addWidget(self.frame_98, 0, Qt.AlignBottom)


        self.verticalLayout_107.addWidget(self.frame_96)

        self.stackedWidgetCours.addWidget(self.add_cours)

        self.verticalLayout_102.addWidget(self.stackedWidgetCours)

        self.coursStaked.addWidget(self.cours_staked_page)
        self.programme_staked_page = QWidget()
        self.programme_staked_page.setObjectName(u"programme_staked_page")
        self.verticalLayout_124 = QVBoxLayout(self.programme_staked_page)
        self.verticalLayout_124.setObjectName(u"verticalLayout_124")
        self.stackedWidgetProgramme = QStackedWidget(self.programme_staked_page)
        self.stackedWidgetProgramme.setObjectName(u"stackedWidgetProgramme")
        self.index_programme = QWidget()
        self.index_programme.setObjectName(u"index_programme")
        self.verticalLayout_114 = QVBoxLayout(self.index_programme)
        self.verticalLayout_114.setObjectName(u"verticalLayout_114")
        self.frame_97 = QFrame(self.index_programme)
        self.frame_97.setObjectName(u"frame_97")
        self.frame_97.setFrameShape(QFrame.StyledPanel)
        self.frame_97.setFrameShadow(QFrame.Raised)
        self.verticalLayout_115 = QVBoxLayout(self.frame_97)
        self.verticalLayout_115.setObjectName(u"verticalLayout_115")
        self.verticalLayout_115.setContentsMargins(-1, 0, -1, 0)
        self.addProgramme = QPushButton(self.frame_97)
        self.addProgramme.setObjectName(u"addProgramme")
        self.addProgramme.setMinimumSize(QSize(150, 0))
        self.addProgramme.setFont(font4)
        self.addProgramme.setFlat(True)

        self.verticalLayout_115.addWidget(self.addProgramme)


        self.verticalLayout_114.addWidget(self.frame_97, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_101 = QFrame(self.index_programme)
        self.frame_101.setObjectName(u"frame_101")
        self.frame_101.setFrameShape(QFrame.StyledPanel)
        self.frame_101.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_185 = QHBoxLayout(self.frame_101)
        self.horizontalLayout_185.setObjectName(u"horizontalLayout_185")
        self.horizontalLayout_185.setContentsMargins(-1, 0, -1, 0)
        self.frame_450 = QFrame(self.frame_101)
        self.frame_450.setObjectName(u"frame_450")
        self.frame_450.setFrameShape(QFrame.StyledPanel)
        self.frame_450.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_186 = QHBoxLayout(self.frame_450)
        self.horizontalLayout_186.setSpacing(17)
        self.horizontalLayout_186.setObjectName(u"horizontalLayout_186")
        self.class_id = QComboBox(self.frame_450)
        self.class_id.setObjectName(u"class_id")
        self.class_id.setMinimumSize(QSize(159, 37))
        self.class_id.setFont(font2)

        self.horizontalLayout_186.addWidget(self.class_id)

        self.anneeId = QComboBox(self.frame_450)
        self.anneeId.setObjectName(u"anneeId")
        self.anneeId.setMinimumSize(QSize(159, 37))
        self.anneeId.setFont(font2)

        self.horizontalLayout_186.addWidget(self.anneeId)

        self.niveauId = QComboBox(self.frame_450)
        self.niveauId.setObjectName(u"niveauId")
        self.niveauId.setMinimumSize(QSize(159, 37))
        self.niveauId.setFont(font2)

        self.horizontalLayout_186.addWidget(self.niveauId)


        self.horizontalLayout_185.addWidget(self.frame_450)

        self.search_programme = QLineEdit(self.frame_101)
        self.search_programme.setObjectName(u"search_programme")
        self.search_programme.setMinimumSize(QSize(350, 37))
        self.search_programme.setFont(font2)

        self.horizontalLayout_185.addWidget(self.search_programme, 0, Qt.AlignRight)


        self.verticalLayout_114.addWidget(self.frame_101, 0, Qt.AlignTop)

        self.frame_102 = QFrame(self.index_programme)
        self.frame_102.setObjectName(u"frame_102")
        sizePolicy.setHeightForWidth(self.frame_102.sizePolicy().hasHeightForWidth())
        self.frame_102.setSizePolicy(sizePolicy)
        self.frame_102.setFrameShape(QFrame.StyledPanel)
        self.frame_102.setFrameShadow(QFrame.Raised)
        self.verticalLayout_117 = QVBoxLayout(self.frame_102)
        self.verticalLayout_117.setSpacing(0)
        self.verticalLayout_117.setObjectName(u"verticalLayout_117")
        self.verticalLayout_117.setContentsMargins(0, 0, 0, 0)
        self.programme_table = QTableWidget(self.frame_102)
        self.programme_table.setObjectName(u"programme_table")
        self.programme_table.setSortingEnabled(True)
        self.programme_table.horizontalHeader().setMinimumSectionSize(100)
        self.programme_table.horizontalHeader().setStretchLastSection(True)
        self.programme_table.verticalHeader().setVisible(False)
        self.programme_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_117.addWidget(self.programme_table)

        self.frame_331 = QFrame(self.frame_102)
        self.frame_331.setObjectName(u"frame_331")
        self.frame_331.setFrameShape(QFrame.StyledPanel)
        self.frame_331.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_119 = QHBoxLayout(self.frame_331)
        self.horizontalLayout_119.setSpacing(25)
        self.horizontalLayout_119.setObjectName(u"horizontalLayout_119")
        self.horizontalLayout_119.setContentsMargins(0, 0, 0, 0)
        self.prev_programme = QPushButton(self.frame_331)
        self.prev_programme.setObjectName(u"prev_programme")
        self.prev_programme.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_119.addWidget(self.prev_programme)

        self.next_programme = QPushButton(self.frame_331)
        self.next_programme.setObjectName(u"next_programme")
        self.next_programme.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_119.addWidget(self.next_programme)


        self.verticalLayout_117.addWidget(self.frame_331, 0, Qt.AlignRight)


        self.verticalLayout_114.addWidget(self.frame_102)

        self.stackedWidgetProgramme.addWidget(self.index_programme)
        self.add_programme = QWidget()
        self.add_programme.setObjectName(u"add_programme")
        self.verticalLayout_118 = QVBoxLayout(self.add_programme)
        self.verticalLayout_118.setSpacing(0)
        self.verticalLayout_118.setObjectName(u"verticalLayout_118")
        self.verticalLayout_118.setContentsMargins(-1, 0, -1, 0)
        self.frame_103 = QFrame(self.add_programme)
        self.frame_103.setObjectName(u"frame_103")
        self.frame_103.setFrameShape(QFrame.StyledPanel)
        self.frame_103.setFrameShadow(QFrame.Raised)
        self.verticalLayout_119 = QVBoxLayout(self.frame_103)
        self.verticalLayout_119.setSpacing(0)
        self.verticalLayout_119.setObjectName(u"verticalLayout_119")
        self.verticalLayout_119.setContentsMargins(0, 0, 0, 0)
        self.widget_8 = QWidget(self.frame_103)
        self.widget_8.setObjectName(u"widget_8")
        sizePolicy.setHeightForWidth(self.widget_8.sizePolicy().hasHeightForWidth())
        self.widget_8.setSizePolicy(sizePolicy)
        self.verticalLayout_120 = QVBoxLayout(self.widget_8)
        self.verticalLayout_120.setSpacing(0)
        self.verticalLayout_120.setObjectName(u"verticalLayout_120")
        self.verticalLayout_120.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_cours = QScrollArea(self.widget_8)
        self.scrollArea_cours.setObjectName(u"scrollArea_cours")
        self.scrollArea_cours.setWidgetResizable(True)
        self.scrollAreaWidgetContents_4 = QWidget()
        self.scrollAreaWidgetContents_4.setObjectName(u"scrollAreaWidgetContents_4")
        self.scrollAreaWidgetContents_4.setGeometry(QRect(0, 0, 65, 16))
        self.verticalLayout_139 = QVBoxLayout(self.scrollAreaWidgetContents_4)
        self.verticalLayout_139.setSpacing(0)
        self.verticalLayout_139.setObjectName(u"verticalLayout_139")
        self.verticalLayout_139.setContentsMargins(0, 0, 0, 0)
        self.widget_9 = QWidget(self.scrollAreaWidgetContents_4)
        self.widget_9.setObjectName(u"widget_9")

        self.verticalLayout_139.addWidget(self.widget_9)

        self.scrollArea_cours.setWidget(self.scrollAreaWidgetContents_4)

        self.verticalLayout_120.addWidget(self.scrollArea_cours)


        self.verticalLayout_119.addWidget(self.widget_8)

        self.frame_104 = QFrame(self.frame_103)
        self.frame_104.setObjectName(u"frame_104")
        self.frame_104.setFrameShape(QFrame.StyledPanel)
        self.frame_104.setFrameShadow(QFrame.Raised)
        self.verticalLayout_121 = QVBoxLayout(self.frame_104)
        self.verticalLayout_121.setSpacing(0)
        self.verticalLayout_121.setObjectName(u"verticalLayout_121")
        self.verticalLayout_121.setContentsMargins(0, 0, 0, 0)
        self.frame_105 = QFrame(self.frame_104)
        self.frame_105.setObjectName(u"frame_105")
        self.frame_105.setFrameShape(QFrame.StyledPanel)
        self.frame_105.setFrameShadow(QFrame.Raised)
        self.verticalLayout_122 = QVBoxLayout(self.frame_105)
        self.verticalLayout_122.setObjectName(u"verticalLayout_122")
        self.verticalLayout_122.setContentsMargins(-1, 0, -1, 0)
        self.add_programme_line = QPushButton(self.frame_105)
        self.add_programme_line.setObjectName(u"add_programme_line")
        self.add_programme_line.setMinimumSize(QSize(169, 0))
        self.add_programme_line.setFont(font4)
        self.add_programme_line.setFlat(True)

        self.verticalLayout_122.addWidget(self.add_programme_line)


        self.verticalLayout_121.addWidget(self.frame_105, 0, Qt.AlignLeft|Qt.AlignBottom)

        self.frame_112 = QFrame(self.frame_104)
        self.frame_112.setObjectName(u"frame_112")
        self.frame_112.setFrameShape(QFrame.StyledPanel)
        self.frame_112.setFrameShadow(QFrame.Raised)
        self.verticalLayout_123 = QVBoxLayout(self.frame_112)
        self.verticalLayout_123.setObjectName(u"verticalLayout_123")
        self.verticalLayout_123.setContentsMargins(-1, 0, -1, 0)
        self.enregistrer_programme = QPushButton(self.frame_112)
        self.enregistrer_programme.setObjectName(u"enregistrer_programme")
        self.enregistrer_programme.setMinimumSize(QSize(130, 0))
        self.enregistrer_programme.setFont(font4)
        self.enregistrer_programme.setFlat(True)

        self.verticalLayout_123.addWidget(self.enregistrer_programme)


        self.verticalLayout_121.addWidget(self.frame_112, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_119.addWidget(self.frame_104, 0, Qt.AlignBottom)


        self.verticalLayout_118.addWidget(self.frame_103)

        self.stackedWidgetProgramme.addWidget(self.add_programme)

        self.verticalLayout_124.addWidget(self.stackedWidgetProgramme)

        self.coursStaked.addWidget(self.programme_staked_page)

        self.verticalLayout_101.addWidget(self.coursStaked)


        self.verticalLayout_100.addWidget(self.frame_92)

        self.stackedWidget.addWidget(self.cours_page)
        self.notes_page = QWidget()
        self.notes_page.setObjectName(u"notes_page")
        self.verticalLayout_99 = QVBoxLayout(self.notes_page)
        self.verticalLayout_99.setObjectName(u"verticalLayout_99")
        self.verticalLayout_99.setContentsMargins(-1, 0, -1, -1)
        self.stackedNotes = QStackedWidget(self.notes_page)
        self.stackedNotes.setObjectName(u"stackedNotes")
        self.index_notes = QWidget()
        self.index_notes.setObjectName(u"index_notes")
        self.verticalLayout_132 = QVBoxLayout(self.index_notes)
        self.verticalLayout_132.setObjectName(u"verticalLayout_132")
        self.verticalLayout_132.setContentsMargins(-1, 0, -1, -1)
        self.frame_126 = QFrame(self.index_notes)
        self.frame_126.setObjectName(u"frame_126")
        self.frame_126.setFrameShape(QFrame.StyledPanel)
        self.frame_126.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_105 = QHBoxLayout(self.frame_126)
        self.horizontalLayout_105.setSpacing(28)
        self.horizontalLayout_105.setObjectName(u"horizontalLayout_105")
        self.horizontalLayout_105.setContentsMargins(-1, 0, -1, 0)
        self.notes_dialog = QPushButton(self.frame_126)
        self.notes_dialog.setObjectName(u"notes_dialog")
        self.notes_dialog.setMinimumSize(QSize(220, 33))
        self.notes_dialog.setMaximumSize(QSize(16777215, 33))
        self.notes_dialog.setFont(font)
        self.notes_dialog.setCheckable(True)
        self.notes_dialog.setChecked(True)
        self.notes_dialog.setAutoExclusive(True)
        self.notes_dialog.setFlat(True)

        self.horizontalLayout_105.addWidget(self.notes_dialog)

        self.frame_296 = QFrame(self.frame_126)
        self.frame_296.setObjectName(u"frame_296")
        self.frame_296.setFrameShape(QFrame.StyledPanel)
        self.frame_296.setFrameShadow(QFrame.Raised)
        self.verticalLayout_277 = QVBoxLayout(self.frame_296)
        self.verticalLayout_277.setObjectName(u"verticalLayout_277")
        self.verticalLayout_277.setContentsMargins(-1, 0, -1, 0)
        self.bulletin_dialog = QPushButton(self.frame_296)
        self.bulletin_dialog.setObjectName(u"bulletin_dialog")
        self.bulletin_dialog.setMinimumSize(QSize(120, 33))
        self.bulletin_dialog.setMaximumSize(QSize(16777215, 33))
        self.bulletin_dialog.setFont(font4)
        self.bulletin_dialog.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.bulletin_dialog.setCheckable(True)
        self.bulletin_dialog.setAutoExclusive(True)

        self.verticalLayout_277.addWidget(self.bulletin_dialog)


        self.horizontalLayout_105.addWidget(self.frame_296)


        self.verticalLayout_132.addWidget(self.frame_126, 0, Qt.AlignLeft)

        self.frame_bulletin = QFrame(self.index_notes)
        self.frame_bulletin.setObjectName(u"frame_bulletin")
        self.frame_bulletin.setFrameShape(QFrame.StyledPanel)
        self.frame_bulletin.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_106 = QHBoxLayout(self.frame_bulletin)
        self.horizontalLayout_106.setSpacing(0)
        self.horizontalLayout_106.setObjectName(u"horizontalLayout_106")
        self.horizontalLayout_106.setContentsMargins(0, 0, 0, 0)
        self.frame_297 = QFrame(self.frame_bulletin)
        self.frame_297.setObjectName(u"frame_297")
        self.frame_297.setFrameShape(QFrame.StyledPanel)
        self.frame_297.setFrameShadow(QFrame.Raised)
        self.verticalLayout_133 = QVBoxLayout(self.frame_297)
        self.verticalLayout_133.setObjectName(u"verticalLayout_133")
        self.annee_for_bulletin = QComboBox(self.frame_297)
        self.annee_for_bulletin.setObjectName(u"annee_for_bulletin")
        self.annee_for_bulletin.setMinimumSize(QSize(200, 37))
        self.annee_for_bulletin.setMaximumSize(QSize(16777215, 37))
        self.annee_for_bulletin.setFont(font2)

        self.verticalLayout_133.addWidget(self.annee_for_bulletin)


        self.horizontalLayout_106.addWidget(self.frame_297)

        self.frame_298 = QFrame(self.frame_bulletin)
        self.frame_298.setObjectName(u"frame_298")
        self.frame_298.setFrameShape(QFrame.StyledPanel)
        self.frame_298.setFrameShadow(QFrame.Raised)
        self.verticalLayout_274 = QVBoxLayout(self.frame_298)
        self.verticalLayout_274.setObjectName(u"verticalLayout_274")
        self.mois_for_bulletin = QComboBox(self.frame_298)
        self.mois_for_bulletin.setObjectName(u"mois_for_bulletin")
        self.mois_for_bulletin.setMinimumSize(QSize(200, 37))
        self.mois_for_bulletin.setMaximumSize(QSize(16777215, 37))
        self.mois_for_bulletin.setFont(font2)

        self.verticalLayout_274.addWidget(self.mois_for_bulletin)


        self.horizontalLayout_106.addWidget(self.frame_298)

        self.frame_299 = QFrame(self.frame_bulletin)
        self.frame_299.setObjectName(u"frame_299")
        self.frame_299.setFrameShape(QFrame.StyledPanel)
        self.frame_299.setFrameShadow(QFrame.Raised)
        self.verticalLayout_275 = QVBoxLayout(self.frame_299)
        self.verticalLayout_275.setObjectName(u"verticalLayout_275")
        self.classe_for_bulletin = QComboBox(self.frame_299)
        self.classe_for_bulletin.setObjectName(u"classe_for_bulletin")
        self.classe_for_bulletin.setMinimumSize(QSize(200, 37))
        self.classe_for_bulletin.setMaximumSize(QSize(16777215, 37))
        self.classe_for_bulletin.setFont(font2)

        self.verticalLayout_275.addWidget(self.classe_for_bulletin)


        self.horizontalLayout_106.addWidget(self.frame_299)

        self.frame_300 = QFrame(self.frame_bulletin)
        self.frame_300.setObjectName(u"frame_300")
        self.frame_300.setFrameShape(QFrame.StyledPanel)
        self.frame_300.setFrameShadow(QFrame.Raised)
        self.verticalLayout_276 = QVBoxLayout(self.frame_300)
        self.verticalLayout_276.setObjectName(u"verticalLayout_276")
        self.imprimer_bulletin = QPushButton(self.frame_300)
        self.imprimer_bulletin.setObjectName(u"imprimer_bulletin")
        self.imprimer_bulletin.setMinimumSize(QSize(100, 0))
        self.imprimer_bulletin.setFont(font4)
        self.imprimer_bulletin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_276.addWidget(self.imprimer_bulletin)


        self.horizontalLayout_106.addWidget(self.frame_300)


        self.verticalLayout_132.addWidget(self.frame_bulletin, 0, Qt.AlignHCenter)

        self.frame_127 = QFrame(self.index_notes)
        self.frame_127.setObjectName(u"frame_127")
        self.frame_127.setMinimumSize(QSize(400, 0))
        self.frame_127.setFrameShape(QFrame.StyledPanel)
        self.frame_127.setFrameShadow(QFrame.Raised)
        self.verticalLayout_134 = QVBoxLayout(self.frame_127)
        self.verticalLayout_134.setObjectName(u"verticalLayout_134")
        self.verticalLayout_134.setContentsMargins(-1, 0, -1, 0)
        self.search_notes = QLineEdit(self.frame_127)
        self.search_notes.setObjectName(u"search_notes")

        self.verticalLayout_134.addWidget(self.search_notes)


        self.verticalLayout_132.addWidget(self.frame_127, 0, Qt.AlignRight)

        self.frame_128 = QFrame(self.index_notes)
        self.frame_128.setObjectName(u"frame_128")
        sizePolicy.setHeightForWidth(self.frame_128.sizePolicy().hasHeightForWidth())
        self.frame_128.setSizePolicy(sizePolicy)
        self.frame_128.setFrameShape(QFrame.StyledPanel)
        self.frame_128.setFrameShadow(QFrame.Raised)
        self.verticalLayout_135 = QVBoxLayout(self.frame_128)
        self.verticalLayout_135.setObjectName(u"verticalLayout_135")
        self.verticalLayout_135.setContentsMargins(-1, 0, -1, 0)
        self.notes_table = QTableWidget(self.frame_128)
        self.notes_table.setObjectName(u"notes_table")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(1)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.notes_table.sizePolicy().hasHeightForWidth())
        self.notes_table.setSizePolicy(sizePolicy7)
        self.notes_table.setFont(font4)
        self.notes_table.setTabletTracking(True)
        self.notes_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.notes_table.setTabKeyNavigation(False)
        self.notes_table.setProperty(u"showDropIndicator", False)
        self.notes_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.notes_table.setSortingEnabled(True)
        self.notes_table.setWordWrap(True)
        self.notes_table.setCornerButtonEnabled(False)
        self.notes_table.horizontalHeader().setCascadingSectionResizes(False)
        self.notes_table.horizontalHeader().setMinimumSectionSize(100)
        self.notes_table.horizontalHeader().setHighlightSections(False)
        self.notes_table.horizontalHeader().setStretchLastSection(True)
        self.notes_table.verticalHeader().setVisible(False)
        self.notes_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_135.addWidget(self.notes_table)


        self.verticalLayout_132.addWidget(self.frame_128)

        self.frame_135 = QFrame(self.index_notes)
        self.frame_135.setObjectName(u"frame_135")
        self.frame_135.setFrameShape(QFrame.StyledPanel)
        self.frame_135.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_45 = QHBoxLayout(self.frame_135)
        self.horizontalLayout_45.setSpacing(20)
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.horizontalLayout_45.setContentsMargins(-1, 0, -1, 0)
        self.prev_notes = QPushButton(self.frame_135)
        self.prev_notes.setObjectName(u"prev_notes")
        self.prev_notes.setFlat(True)

        self.horizontalLayout_45.addWidget(self.prev_notes)

        self.label_notes = QLabel(self.frame_135)
        self.label_notes.setObjectName(u"label_notes")

        self.horizontalLayout_45.addWidget(self.label_notes)

        self.next_notes = QPushButton(self.frame_135)
        self.next_notes.setObjectName(u"next_notes")
        self.next_notes.setFlat(True)

        self.horizontalLayout_45.addWidget(self.next_notes)


        self.verticalLayout_132.addWidget(self.frame_135, 0, Qt.AlignRight)

        self.stackedNotes.addWidget(self.index_notes)
        self.add_notes = QWidget()
        self.add_notes.setObjectName(u"add_notes")
        self.horizontalLayout_46 = QHBoxLayout(self.add_notes)
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.horizontalLayout_46.setContentsMargins(-1, 0, -1, -1)
        self.frame_141 = QFrame(self.add_notes)
        self.frame_141.setObjectName(u"frame_141")
        self.frame_141.setFrameShape(QFrame.StyledPanel)
        self.frame_141.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_141)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(-1, 0, -1, -1)
        self.frame_137 = QFrame(self.frame_141)
        self.frame_137.setObjectName(u"frame_137")
        self.frame_137.setFrameShape(QFrame.StyledPanel)
        self.frame_137.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_137)
        self.horizontalLayout_8.setSpacing(17)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(9, 0, 9, 0)
        self.frame_138 = QFrame(self.frame_137)
        self.frame_138.setObjectName(u"frame_138")
        self.frame_138.setMinimumSize(QSize(0, 30))
        self.frame_138.setFrameShape(QFrame.StyledPanel)
        self.frame_138.setFrameShadow(QFrame.Raised)
        self.verticalLayout_293 = QVBoxLayout(self.frame_138)
        self.verticalLayout_293.setSpacing(0)
        self.verticalLayout_293.setObjectName(u"verticalLayout_293")
        self.verticalLayout_293.setContentsMargins(0, 0, 0, 0)
        self.frame_333 = QFrame(self.frame_138)
        self.frame_333.setObjectName(u"frame_333")
        self.frame_333.setFrameShape(QFrame.StyledPanel)
        self.frame_333.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_121 = QHBoxLayout(self.frame_333)
        self.horizontalLayout_121.setObjectName(u"horizontalLayout_121")
        self.horizontalLayout_121.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.frame_333)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font1)

        self.horizontalLayout_121.addWidget(self.label_6)

        self.affiche_cours = QLabel(self.frame_333)
        self.affiche_cours.setObjectName(u"affiche_cours")

        self.horizontalLayout_121.addWidget(self.affiche_cours)


        self.verticalLayout_293.addWidget(self.frame_333, 0, Qt.AlignTop)

        self.frame_336 = QFrame(self.frame_138)
        self.frame_336.setObjectName(u"frame_336")
        self.frame_336.setFrameShape(QFrame.StyledPanel)
        self.frame_336.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_124 = QHBoxLayout(self.frame_336)
        self.horizontalLayout_124.setObjectName(u"horizontalLayout_124")
        self.horizontalLayout_124.setContentsMargins(0, 0, 0, 0)
        self.label_127 = QLabel(self.frame_336)
        self.label_127.setObjectName(u"label_127")
        self.label_127.setFont(font1)

        self.horizontalLayout_124.addWidget(self.label_127)

        self.affiche_classe = QLabel(self.frame_336)
        self.affiche_classe.setObjectName(u"affiche_classe")

        self.horizontalLayout_124.addWidget(self.affiche_classe)


        self.verticalLayout_293.addWidget(self.frame_336, 0, Qt.AlignTop)


        self.horizontalLayout_8.addWidget(self.frame_138, 0, Qt.AlignTop)

        self.frame_139 = QFrame(self.frame_137)
        self.frame_139.setObjectName(u"frame_139")
        self.frame_139.setFrameShape(QFrame.StyledPanel)
        self.frame_139.setFrameShadow(QFrame.Raised)
        self.verticalLayout_313 = QVBoxLayout(self.frame_139)
        self.verticalLayout_313.setSpacing(0)
        self.verticalLayout_313.setObjectName(u"verticalLayout_313")
        self.verticalLayout_313.setContentsMargins(-1, 0, -1, 0)
        self.frame_356 = QFrame(self.frame_139)
        self.frame_356.setObjectName(u"frame_356")
        self.frame_356.setFont(font4)
        self.frame_356.setFrameShape(QFrame.StyledPanel)
        self.frame_356.setFrameShadow(QFrame.Raised)
        self.verticalLayout_314 = QVBoxLayout(self.frame_356)
        self.verticalLayout_314.setSpacing(0)
        self.verticalLayout_314.setObjectName(u"verticalLayout_314")
        self.verticalLayout_314.setContentsMargins(0, 0, 0, 0)
        self.label_138 = QLabel(self.frame_356)
        self.label_138.setObjectName(u"label_138")

        self.verticalLayout_314.addWidget(self.label_138)

        self.change_cours = QComboBox(self.frame_356)
        self.change_cours.setObjectName(u"change_cours")
        self.change_cours.setMinimumSize(QSize(0, 37))
        self.change_cours.setMaximumSize(QSize(16777215, 37))
        self.change_cours.setFont(font2)

        self.verticalLayout_314.addWidget(self.change_cours)


        self.verticalLayout_313.addWidget(self.frame_356, 0, Qt.AlignTop)


        self.horizontalLayout_8.addWidget(self.frame_139, 0, Qt.AlignTop)

        self.frame_140 = QFrame(self.frame_137)
        self.frame_140.setObjectName(u"frame_140")
        self.frame_140.setFrameShape(QFrame.StyledPanel)
        self.frame_140.setFrameShadow(QFrame.Raised)
        self.verticalLayout_136 = QVBoxLayout(self.frame_140)
        self.verticalLayout_136.setSpacing(0)
        self.verticalLayout_136.setObjectName(u"verticalLayout_136")
        self.verticalLayout_136.setContentsMargins(0, 0, 0, 0)
        self.label_8 = QLabel(self.frame_140)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_136.addWidget(self.label_8)

        self.combo_evaluation = QComboBox(self.frame_140)
        self.combo_evaluation.setObjectName(u"combo_evaluation")
        self.combo_evaluation.setFont(font2)

        self.verticalLayout_136.addWidget(self.combo_evaluation)

        self.frame_355 = QFrame(self.frame_140)
        self.frame_355.setObjectName(u"frame_355")
        self.frame_355.setFrameShape(QFrame.StyledPanel)
        self.frame_355.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_355)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.intra_button = QRadioButton(self.frame_355)
        self.intra_button.setObjectName(u"intra_button")
        self.intra_button.setFont(font4)
        self.intra_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_10.addWidget(self.intra_button)

        self.finale_button = QRadioButton(self.frame_355)
        self.finale_button.setObjectName(u"finale_button")
        self.finale_button.setFont(font4)
        self.finale_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_10.addWidget(self.finale_button)


        self.verticalLayout_136.addWidget(self.frame_355, 0, Qt.AlignTop)


        self.horizontalLayout_8.addWidget(self.frame_140, 0, Qt.AlignTop)


        self.verticalLayout_13.addWidget(self.frame_137, 0, Qt.AlignTop)

        self.widget_notes = QWidget(self.frame_141)
        self.widget_notes.setObjectName(u"widget_notes")
        sizePolicy.setHeightForWidth(self.widget_notes.sizePolicy().hasHeightForWidth())
        self.widget_notes.setSizePolicy(sizePolicy)

        self.verticalLayout_13.addWidget(self.widget_notes)


        self.horizontalLayout_46.addWidget(self.frame_141)

        self.stackedNotes.addWidget(self.add_notes)
        self.show_note = QWidget()
        self.show_note.setObjectName(u"show_note")
        self.verticalLayout_38 = QVBoxLayout(self.show_note)
        self.verticalLayout_38.setObjectName(u"verticalLayout_38")
        self.verticalLayout_38.setContentsMargins(-1, 0, -1, -1)
        self.scrollArea_3 = QScrollArea(self.show_note)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_5 = QWidget()
        self.scrollAreaWidgetContents_5.setObjectName(u"scrollAreaWidgetContents_5")
        self.scrollAreaWidgetContents_5.setGeometry(QRect(0, 0, 82, 21))
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_5)

        self.verticalLayout_38.addWidget(self.scrollArea_3)

        self.stackedNotes.addWidget(self.show_note)

        self.verticalLayout_99.addWidget(self.stackedNotes)

        self.stackedWidget.addWidget(self.notes_page)
        self.paiement_page = QWidget()
        self.paiement_page.setObjectName(u"paiement_page")
        self.verticalLayout_113 = QVBoxLayout(self.paiement_page)
        self.verticalLayout_113.setObjectName(u"verticalLayout_113")
        self.verticalLayout_113.setContentsMargins(-1, 0, -1, -1)
        self.stackedPaiement = QStackedWidget(self.paiement_page)
        self.stackedPaiement.setObjectName(u"stackedPaiement")
        self.index_paiement = QWidget()
        self.index_paiement.setObjectName(u"index_paiement")
        self.verticalLayout_125 = QVBoxLayout(self.index_paiement)
        self.verticalLayout_125.setObjectName(u"verticalLayout_125")
        self.verticalLayout_125.setContentsMargins(-1, 0, -1, -1)
        self.frame_117 = QFrame(self.index_paiement)
        self.frame_117.setObjectName(u"frame_117")
        self.frame_117.setFrameShape(QFrame.StyledPanel)
        self.frame_117.setFrameShadow(QFrame.Raised)
        self.verticalLayout_126 = QVBoxLayout(self.frame_117)
        self.verticalLayout_126.setObjectName(u"verticalLayout_126")
        self.verticalLayout_126.setContentsMargins(-1, 0, -1, 0)
        self.paiement_dialog = QPushButton(self.frame_117)
        self.paiement_dialog.setObjectName(u"paiement_dialog")
        self.paiement_dialog.setMinimumSize(QSize(140, 0))
        self.paiement_dialog.setFont(font)
        self.paiement_dialog.setFlat(True)

        self.verticalLayout_126.addWidget(self.paiement_dialog)


        self.verticalLayout_125.addWidget(self.frame_117, 0, Qt.AlignLeft)

        self.frame_118 = QFrame(self.index_paiement)
        self.frame_118.setObjectName(u"frame_118")
        self.frame_118.setMinimumSize(QSize(400, 0))
        self.frame_118.setFrameShape(QFrame.StyledPanel)
        self.frame_118.setFrameShadow(QFrame.Raised)
        self.verticalLayout_127 = QVBoxLayout(self.frame_118)
        self.verticalLayout_127.setObjectName(u"verticalLayout_127")
        self.verticalLayout_127.setContentsMargins(-1, 0, -1, 0)
        self.search_paiement = QLineEdit(self.frame_118)
        self.search_paiement.setObjectName(u"search_paiement")

        self.verticalLayout_127.addWidget(self.search_paiement)


        self.verticalLayout_125.addWidget(self.frame_118, 0, Qt.AlignRight)

        self.frame_119 = QFrame(self.index_paiement)
        self.frame_119.setObjectName(u"frame_119")
        sizePolicy.setHeightForWidth(self.frame_119.sizePolicy().hasHeightForWidth())
        self.frame_119.setSizePolicy(sizePolicy)
        self.frame_119.setFrameShape(QFrame.StyledPanel)
        self.frame_119.setFrameShadow(QFrame.Raised)
        self.verticalLayout_128 = QVBoxLayout(self.frame_119)
        self.verticalLayout_128.setObjectName(u"verticalLayout_128")
        self.verticalLayout_128.setContentsMargins(-1, 0, -1, 0)
        self.paiement_table = QTableWidget(self.frame_119)
        self.paiement_table.setObjectName(u"paiement_table")
        sizePolicy7.setHeightForWidth(self.paiement_table.sizePolicy().hasHeightForWidth())
        self.paiement_table.setSizePolicy(sizePolicy7)
        self.paiement_table.setFont(font4)
        self.paiement_table.setTabletTracking(True)
        self.paiement_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.paiement_table.setTabKeyNavigation(False)
        self.paiement_table.setProperty(u"showDropIndicator", False)
        self.paiement_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.paiement_table.setSortingEnabled(True)
        self.paiement_table.setWordWrap(False)
        self.paiement_table.setCornerButtonEnabled(False)
        self.paiement_table.horizontalHeader().setCascadingSectionResizes(False)
        self.paiement_table.horizontalHeader().setMinimumSectionSize(100)
        self.paiement_table.horizontalHeader().setHighlightSections(False)
        self.paiement_table.horizontalHeader().setStretchLastSection(True)
        self.paiement_table.verticalHeader().setVisible(False)
        self.paiement_table.verticalHeader().setHighlightSections(False)

        self.verticalLayout_128.addWidget(self.paiement_table)


        self.verticalLayout_125.addWidget(self.frame_119)

        self.frame_120 = QFrame(self.index_paiement)
        self.frame_120.setObjectName(u"frame_120")
        self.frame_120.setFrameShape(QFrame.StyledPanel)
        self.frame_120.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_42 = QHBoxLayout(self.frame_120)
        self.horizontalLayout_42.setSpacing(20)
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.horizontalLayout_42.setContentsMargins(-1, 0, -1, 0)
        self.prev_paiement = QPushButton(self.frame_120)
        self.prev_paiement.setObjectName(u"prev_paiement")
        self.prev_paiement.setFlat(True)

        self.horizontalLayout_42.addWidget(self.prev_paiement)

        self.label_paiement = QLabel(self.frame_120)
        self.label_paiement.setObjectName(u"label_paiement")

        self.horizontalLayout_42.addWidget(self.label_paiement)

        self.next_paiement = QPushButton(self.frame_120)
        self.next_paiement.setObjectName(u"next_paiement")
        self.next_paiement.setFlat(True)

        self.horizontalLayout_42.addWidget(self.next_paiement)


        self.verticalLayout_125.addWidget(self.frame_120, 0, Qt.AlignRight)

        self.stackedPaiement.addWidget(self.index_paiement)
        self.add_paiement = QWidget()
        self.add_paiement.setObjectName(u"add_paiement")
        self.horizontalLayout_43 = QHBoxLayout(self.add_paiement)
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.horizontalLayout_43.setContentsMargins(-1, 0, -1, -1)
        self.frame_121 = QFrame(self.add_paiement)
        self.frame_121.setObjectName(u"frame_121")
        self.frame_121.setMinimumSize(QSize(400, 0))
        self.frame_121.setFrameShape(QFrame.StyledPanel)
        self.frame_121.setFrameShadow(QFrame.Raised)
        self.verticalLayout_130 = QVBoxLayout(self.frame_121)
        self.verticalLayout_130.setSpacing(0)
        self.verticalLayout_130.setObjectName(u"verticalLayout_130")
        self.frame_123 = QFrame(self.frame_121)
        self.frame_123.setObjectName(u"frame_123")
        self.frame_123.setMaximumSize(QSize(202, 16777215))
        self.frame_123.setFrameShape(QFrame.StyledPanel)
        self.frame_123.setFrameShadow(QFrame.Raised)
        self.verticalLayout_129 = QVBoxLayout(self.frame_123)
        self.verticalLayout_129.setSpacing(0)
        self.verticalLayout_129.setObjectName(u"verticalLayout_129")
        self.verticalLayout_129.setContentsMargins(0, 0, 0, 0)
        self.imag_ilustrative = QLabel(self.frame_123)
        self.imag_ilustrative.setObjectName(u"imag_ilustrative")
        self.imag_ilustrative.setMinimumSize(QSize(200, 200))
        self.imag_ilustrative.setMaximumSize(QSize(200, 200))

        self.verticalLayout_129.addWidget(self.imag_ilustrative, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_130.addWidget(self.frame_123, 0, Qt.AlignHCenter|Qt.AlignVCenter)

        self.frame_124 = QFrame(self.frame_121)
        self.frame_124.setObjectName(u"frame_124")
        sizePolicy.setHeightForWidth(self.frame_124.sizePolicy().hasHeightForWidth())
        self.frame_124.setSizePolicy(sizePolicy)
        self.frame_124.setFrameShape(QFrame.StyledPanel)
        self.frame_124.setFrameShadow(QFrame.Raised)
        self.verticalLayout_131 = QVBoxLayout(self.frame_124)
        self.verticalLayout_131.setObjectName(u"verticalLayout_131")
        self.verticalLayout_131.setContentsMargins(0, 0, 0, 0)
        self.identifiant = QLabel(self.frame_124)
        self.identifiant.setObjectName(u"identifiant")

        self.verticalLayout_131.addWidget(self.identifiant, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.frame_125 = QFrame(self.frame_124)
        self.frame_125.setObjectName(u"frame_125")
        self.frame_125.setFrameShape(QFrame.StyledPanel)
        self.frame_125.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_44 = QHBoxLayout(self.frame_125)
        self.horizontalLayout_44.setSpacing(10)
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.horizontalLayout_44.setContentsMargins(0, 0, 0, 0)
        self.fname = QLabel(self.frame_125)
        self.fname.setObjectName(u"fname")

        self.horizontalLayout_44.addWidget(self.fname)

        self.lname = QLabel(self.frame_125)
        self.lname.setObjectName(u"lname")

        self.horizontalLayout_44.addWidget(self.lname)


        self.verticalLayout_131.addWidget(self.frame_125, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.classe_actuelle = QLabel(self.frame_124)
        self.classe_actuelle.setObjectName(u"classe_actuelle")

        self.verticalLayout_131.addWidget(self.classe_actuelle, 0, Qt.AlignHCenter|Qt.AlignTop)


        self.verticalLayout_130.addWidget(self.frame_124, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.frame_124.raise_()
        self.frame_123.raise_()

        self.horizontalLayout_43.addWidget(self.frame_121, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_122 = QFrame(self.add_paiement)
        self.frame_122.setObjectName(u"frame_122")
        self.frame_122.setFrameShape(QFrame.StyledPanel)
        self.frame_122.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.frame_122)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.scroll_pay = QScrollArea(self.frame_122)
        self.scroll_pay.setObjectName(u"scroll_pay")
        self.scroll_pay.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_pay.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 16, 16))
        self.scroll_pay.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_10.addWidget(self.scroll_pay)


        self.horizontalLayout_43.addWidget(self.frame_122)

        self.stackedPaiement.addWidget(self.add_paiement)
        self.show_paiement = QWidget()
        self.show_paiement.setObjectName(u"show_paiement")
        self.verticalLayout_112 = QVBoxLayout(self.show_paiement)
        self.verticalLayout_112.setObjectName(u"verticalLayout_112")
        self.scrollArea_show_paiement = QScrollArea(self.show_paiement)
        self.scrollArea_show_paiement.setObjectName(u"scrollArea_show_paiement")
        self.scrollArea_show_paiement.setWidgetResizable(True)
        self.scrollAreaWidgetContents_6 = QWidget()
        self.scrollAreaWidgetContents_6.setObjectName(u"scrollAreaWidgetContents_6")
        self.scrollAreaWidgetContents_6.setGeometry(QRect(0, 0, 65, 16))
        self.widget_7 = QWidget(self.scrollAreaWidgetContents_6)
        self.widget_7.setObjectName(u"widget_7")
        self.widget_7.setGeometry(QRect(540, 150, 120, 80))
        self.scrollArea_show_paiement.setWidget(self.scrollAreaWidgetContents_6)

        self.verticalLayout_112.addWidget(self.scrollArea_show_paiement)

        self.stackedPaiement.addWidget(self.show_paiement)

        self.verticalLayout_113.addWidget(self.stackedPaiement)

        self.stackedWidget.addWidget(self.paiement_page)
        self.vente_page = QWidget()
        self.vente_page.setObjectName(u"vente_page")
        self.vente_page.setStyleSheet(u"")
        self.verticalLayout_254 = QVBoxLayout(self.vente_page)
        self.verticalLayout_254.setSpacing(0)
        self.verticalLayout_254.setObjectName(u"verticalLayout_254")
        self.verticalLayout_254.setContentsMargins(-1, 0, -1, -1)
        self.frame_272 = QFrame(self.vente_page)
        self.frame_272.setObjectName(u"frame_272")
        self.frame_272.setFrameShape(QFrame.StyledPanel)
        self.frame_272.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_97 = QHBoxLayout(self.frame_272)
        self.horizontalLayout_97.setSpacing(25)
        self.horizontalLayout_97.setObjectName(u"horizontalLayout_97")
        self.horizontalLayout_97.setContentsMargins(-1, 9, -1, 15)
        self.btn_vente_back = QPushButton(self.frame_272)
        self.btn_vente_back.setObjectName(u"btn_vente_back")
        self.btn_vente_back.setMinimumSize(QSize(110, 33))
        self.btn_vente_back.setMaximumSize(QSize(16777215, 33))
        self.btn_vente_back.setFont(font4)
        self.btn_vente_back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_vente_back.setCheckable(True)
        self.btn_vente_back.setAutoExclusive(True)

        self.horizontalLayout_97.addWidget(self.btn_vente_back)

        self.btn_vente_page = QPushButton(self.frame_272)
        self.btn_vente_page.setObjectName(u"btn_vente_page")
        self.btn_vente_page.setMinimumSize(QSize(110, 33))
        self.btn_vente_page.setMaximumSize(QSize(16777215, 33))
        self.btn_vente_page.setFont(font4)
        self.btn_vente_page.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_vente_page.setCheckable(True)
        self.btn_vente_page.setAutoExclusive(True)

        self.horizontalLayout_97.addWidget(self.btn_vente_page)

        self.frame_335 = QFrame(self.frame_272)
        self.frame_335.setObjectName(u"frame_335")
        self.frame_335.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.frame_335.setFrameShape(QFrame.StyledPanel)
        self.frame_335.setFrameShadow(QFrame.Raised)
        self.verticalLayout_297 = QVBoxLayout(self.frame_335)
        self.verticalLayout_297.setObjectName(u"verticalLayout_297")
        self.verticalLayout_297.setContentsMargins(0, 0, 0, 0)
        self.depense_btn = QPushButton(self.frame_335)
        self.depense_btn.setObjectName(u"depense_btn")
        self.depense_btn.setMinimumSize(QSize(110, 33))
        self.depense_btn.setMaximumSize(QSize(16777215, 33))
        self.depense_btn.setFont(font4)

        self.verticalLayout_297.addWidget(self.depense_btn)


        self.horizontalLayout_97.addWidget(self.frame_335)

        self.frame_411 = QFrame(self.frame_272)
        self.frame_411.setObjectName(u"frame_411")
        self.frame_411.setFrameShape(QFrame.StyledPanel)
        self.frame_411.setFrameShadow(QFrame.Raised)
        self.verticalLayout_354 = QVBoxLayout(self.frame_411)
        self.verticalLayout_354.setSpacing(0)
        self.verticalLayout_354.setObjectName(u"verticalLayout_354")
        self.verticalLayout_354.setContentsMargins(0, 0, 0, 0)
        self.loans = QPushButton(self.frame_411)
        self.loans.setObjectName(u"loans")
        self.loans.setMinimumSize(QSize(110, 33))
        self.loans.setMaximumSize(QSize(16777215, 33))
        self.loans.setFont(font4)
        self.loans.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_354.addWidget(self.loans)


        self.horizontalLayout_97.addWidget(self.frame_411)

        self.frame_452 = QFrame(self.frame_272)
        self.frame_452.setObjectName(u"frame_452")
        self.frame_452.setFrameShape(QFrame.StyledPanel)
        self.frame_452.setFrameShadow(QFrame.Raised)
        self.verticalLayout_386 = QVBoxLayout(self.frame_452)
        self.verticalLayout_386.setSpacing(0)
        self.verticalLayout_386.setObjectName(u"verticalLayout_386")
        self.verticalLayout_386.setContentsMargins(0, 0, 0, 0)
        self.autre_transaction = QPushButton(self.frame_452)
        self.autre_transaction.setObjectName(u"autre_transaction")
        self.autre_transaction.setMinimumSize(QSize(160, 33))
        self.autre_transaction.setMaximumSize(QSize(16777215, 33))
        self.autre_transaction.setFont(font4)
        self.autre_transaction.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_386.addWidget(self.autre_transaction)


        self.horizontalLayout_97.addWidget(self.frame_452)


        self.verticalLayout_254.addWidget(self.frame_272, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_273 = QFrame(self.vente_page)
        self.frame_273.setObjectName(u"frame_273")
        sizePolicy.setHeightForWidth(self.frame_273.sizePolicy().hasHeightForWidth())
        self.frame_273.setSizePolicy(sizePolicy)
        self.frame_273.setFrameShape(QFrame.StyledPanel)
        self.frame_273.setFrameShadow(QFrame.Raised)
        self.verticalLayout_255 = QVBoxLayout(self.frame_273)
        self.verticalLayout_255.setObjectName(u"verticalLayout_255")
        self.verticalLayout_255.setContentsMargins(-1, 0, -1, 9)
        self.tabWidget_2 = QTabWidget(self.frame_273)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        self.vente_index = QWidget()
        self.vente_index.setObjectName(u"vente_index")
        self.verticalLayout_256 = QVBoxLayout(self.vente_index)
        self.verticalLayout_256.setObjectName(u"verticalLayout_256")
        self.search_vente_frame = QFrame(self.vente_index)
        self.search_vente_frame.setObjectName(u"search_vente_frame")
        self.search_vente_frame.setFrameShape(QFrame.StyledPanel)
        self.search_vente_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_257 = QVBoxLayout(self.search_vente_frame)
        self.verticalLayout_257.setObjectName(u"verticalLayout_257")
        self.verticalLayout_257.setContentsMargins(-1, 9, -1, -1)
        self.search_vente = QLineEdit(self.search_vente_frame)
        self.search_vente.setObjectName(u"search_vente")
        self.search_vente.setMinimumSize(QSize(450, 37))
        self.search_vente.setMaximumSize(QSize(16777215, 37))
        self.search_vente.setFont(font2)

        self.verticalLayout_257.addWidget(self.search_vente)


        self.verticalLayout_256.addWidget(self.search_vente_frame, 0, Qt.AlignRight)

        self.frame_275 = QFrame(self.vente_index)
        self.frame_275.setObjectName(u"frame_275")
        self.frame_275.setFrameShape(QFrame.StyledPanel)
        self.frame_275.setFrameShadow(QFrame.Raised)
        self.verticalLayout_273 = QVBoxLayout(self.frame_275)
        self.verticalLayout_273.setObjectName(u"verticalLayout_273")
        self.table_vente = QTableWidget(self.frame_275)
        self.table_vente.setObjectName(u"table_vente")
        self.table_vente.setFont(font4)
        self.table_vente.viewport().setProperty(u"cursor", QCursor(Qt.CursorShape.PointingHandCursor))
        self.table_vente.setEditTriggers(QAbstractItemView.AnyKeyPressed)
        self.table_vente.setSortingEnabled(True)
        self.table_vente.setWordWrap(False)
        self.table_vente.horizontalHeader().setMinimumSectionSize(150)
        self.table_vente.horizontalHeader().setStretchLastSection(True)
        self.table_vente.verticalHeader().setVisible(False)
        self.table_vente.verticalHeader().setHighlightSections(False)

        self.verticalLayout_273.addWidget(self.table_vente)


        self.verticalLayout_256.addWidget(self.frame_275)

        self.frame_373 = QFrame(self.vente_index)
        self.frame_373.setObjectName(u"frame_373")
        self.frame_373.setFrameShape(QFrame.StyledPanel)
        self.frame_373.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_138 = QHBoxLayout(self.frame_373)
        self.horizontalLayout_138.setSpacing(30)
        self.horizontalLayout_138.setObjectName(u"horizontalLayout_138")
        self.prev_vente = QPushButton(self.frame_373)
        self.prev_vente.setObjectName(u"prev_vente")
        self.prev_vente.setFont(font4)
        self.prev_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_138.addWidget(self.prev_vente)

        self.next_vente = QPushButton(self.frame_373)
        self.next_vente.setObjectName(u"next_vente")
        self.next_vente.setFont(font4)
        self.next_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_138.addWidget(self.next_vente)


        self.verticalLayout_256.addWidget(self.frame_373, 0, Qt.AlignRight)

        self.tabWidget_2.addTab(self.vente_index, "")
        self.add_vente = QWidget()
        self.add_vente.setObjectName(u"add_vente")
        self.add_vente.setStyleSheet(u"")
        self.horizontalLayout_98 = QHBoxLayout(self.add_vente)
        self.horizontalLayout_98.setObjectName(u"horizontalLayout_98")
        self.frame_274 = QFrame(self.add_vente)
        self.frame_274.setObjectName(u"frame_274")
        self.frame_274.setFrameShape(QFrame.StyledPanel)
        self.frame_274.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_99 = QHBoxLayout(self.frame_274)
        self.horizontalLayout_99.setSpacing(18)
        self.horizontalLayout_99.setObjectName(u"horizontalLayout_99")
        self.horizontalLayout_99.setContentsMargins(0, 0, 0, 0)
        self.frame_276 = QFrame(self.frame_274)
        self.frame_276.setObjectName(u"frame_276")
        self.frame_276.setFrameShape(QFrame.StyledPanel)
        self.frame_276.setFrameShadow(QFrame.Raised)
        self.verticalLayout_259 = QVBoxLayout(self.frame_276)
        self.verticalLayout_259.setSpacing(10)
        self.verticalLayout_259.setObjectName(u"verticalLayout_259")
        self.verticalLayout_259.setContentsMargins(9, 9, 9, 0)
        self.frame_386 = QFrame(self.frame_276)
        self.frame_386.setObjectName(u"frame_386")
        self.frame_386.setFrameShape(QFrame.StyledPanel)
        self.frame_386.setFrameShadow(QFrame.Raised)
        self.verticalLayout_336 = QVBoxLayout(self.frame_386)
        self.verticalLayout_336.setSpacing(0)
        self.verticalLayout_336.setObjectName(u"verticalLayout_336")
        self.verticalLayout_336.setContentsMargins(0, 0, 0, 0)
        self.search_student_for_sell = QLineEdit(self.frame_386)
        self.search_student_for_sell.setObjectName(u"search_student_for_sell")
        self.search_student_for_sell.setFont(font2)

        self.verticalLayout_336.addWidget(self.search_student_for_sell)


        self.verticalLayout_259.addWidget(self.frame_386)

        self.frame_278 = QFrame(self.frame_276)
        self.frame_278.setObjectName(u"frame_278")
        self.frame_278.setMinimumSize(QSize(400, 0))
        self.frame_278.setFrameShape(QFrame.StyledPanel)
        self.frame_278.setFrameShadow(QFrame.Raised)
        self.verticalLayout_260 = QVBoxLayout(self.frame_278)
        self.verticalLayout_260.setSpacing(0)
        self.verticalLayout_260.setObjectName(u"verticalLayout_260")
        self.verticalLayout_260.setContentsMargins(0, 0, 0, 0)
        self.frame_295 = QFrame(self.frame_278)
        self.frame_295.setObjectName(u"frame_295")
        self.frame_295.setFrameShape(QFrame.StyledPanel)
        self.frame_295.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_104 = QHBoxLayout(self.frame_295)
        self.horizontalLayout_104.setSpacing(0)
        self.horizontalLayout_104.setObjectName(u"horizontalLayout_104")
        self.horizontalLayout_104.setContentsMargins(0, 0, 0, 0)
        self.student_vente_id = QLineEdit(self.frame_295)
        self.student_vente_id.setObjectName(u"student_vente_id")

        self.horizontalLayout_104.addWidget(self.student_vente_id)

        self.vente_edit_id = QLineEdit(self.frame_295)
        self.vente_edit_id.setObjectName(u"vente_edit_id")

        self.horizontalLayout_104.addWidget(self.vente_edit_id)


        self.verticalLayout_260.addWidget(self.frame_295)


        self.verticalLayout_259.addWidget(self.frame_278, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_279 = QFrame(self.frame_276)
        self.frame_279.setObjectName(u"frame_279")
        self.frame_279.setFrameShape(QFrame.StyledPanel)
        self.frame_279.setFrameShadow(QFrame.Raised)
        self.verticalLayout_258 = QVBoxLayout(self.frame_279)
        self.verticalLayout_258.setSpacing(20)
        self.verticalLayout_258.setObjectName(u"verticalLayout_258")
        self.verticalLayout_258.setContentsMargins(0, 0, 0, 0)
        self.frame_284 = QFrame(self.frame_279)
        self.frame_284.setObjectName(u"frame_284")
        self.frame_284.setFrameShape(QFrame.StyledPanel)
        self.frame_284.setFrameShadow(QFrame.Raised)
        self.verticalLayout_261 = QVBoxLayout(self.frame_284)
        self.verticalLayout_261.setSpacing(0)
        self.verticalLayout_261.setObjectName(u"verticalLayout_261")
        self.verticalLayout_261.setContentsMargins(0, 0, 0, 0)
        self.label_9 = QLabel(self.frame_284)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_261.addWidget(self.label_9)

        self.materiel_name = QLineEdit(self.frame_284)
        self.materiel_name.setObjectName(u"materiel_name")
        self.materiel_name.setMaximumSize(QSize(500, 37))
        self.materiel_name.setFont(font2)

        self.verticalLayout_261.addWidget(self.materiel_name)


        self.verticalLayout_258.addWidget(self.frame_284, 0, Qt.AlignTop)

        self.frame_283 = QFrame(self.frame_279)
        self.frame_283.setObjectName(u"frame_283")
        self.frame_283.setFrameShape(QFrame.StyledPanel)
        self.frame_283.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_100 = QHBoxLayout(self.frame_283)
        self.horizontalLayout_100.setSpacing(12)
        self.horizontalLayout_100.setObjectName(u"horizontalLayout_100")
        self.horizontalLayout_100.setContentsMargins(0, 0, 0, 0)
        self.frame_285 = QFrame(self.frame_283)
        self.frame_285.setObjectName(u"frame_285")
        self.frame_285.setMinimumSize(QSize(250, 0))
        self.frame_285.setMaximumSize(QSize(250, 16777215))
        self.frame_285.setFrameShape(QFrame.StyledPanel)
        self.frame_285.setFrameShadow(QFrame.Raised)
        self.verticalLayout_263 = QVBoxLayout(self.frame_285)
        self.verticalLayout_263.setSpacing(0)
        self.verticalLayout_263.setObjectName(u"verticalLayout_263")
        self.verticalLayout_263.setContentsMargins(0, 0, 0, -1)
        self.label_52 = QLabel(self.frame_285)
        self.label_52.setObjectName(u"label_52")

        self.verticalLayout_263.addWidget(self.label_52)

        self.category = QComboBox(self.frame_285)
        self.category.setObjectName(u"category")
        self.category.setMaximumSize(QSize(250, 37))
        self.category.setFont(font2)

        self.verticalLayout_263.addWidget(self.category)


        self.horizontalLayout_100.addWidget(self.frame_285)

        self.frame_286 = QFrame(self.frame_283)
        self.frame_286.setObjectName(u"frame_286")
        self.frame_286.setFrameShape(QFrame.StyledPanel)
        self.frame_286.setFrameShadow(QFrame.Raised)
        self.verticalLayout_264 = QVBoxLayout(self.frame_286)
        self.verticalLayout_264.setSpacing(0)
        self.verticalLayout_264.setObjectName(u"verticalLayout_264")
        self.verticalLayout_264.setContentsMargins(0, 0, 0, -1)
        self.label_62 = QLabel(self.frame_286)
        self.label_62.setObjectName(u"label_62")

        self.verticalLayout_264.addWidget(self.label_62)

        self.quantity = QLineEdit(self.frame_286)
        self.quantity.setObjectName(u"quantity")
        self.quantity.setMaximumSize(QSize(250, 37))
        self.quantity.setFont(font2)

        self.verticalLayout_264.addWidget(self.quantity)


        self.horizontalLayout_100.addWidget(self.frame_286)


        self.verticalLayout_258.addWidget(self.frame_283, 0, Qt.AlignTop)

        self.frame_282 = QFrame(self.frame_279)
        self.frame_282.setObjectName(u"frame_282")
        self.frame_282.setFrameShape(QFrame.StyledPanel)
        self.frame_282.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_101 = QHBoxLayout(self.frame_282)
        self.horizontalLayout_101.setSpacing(15)
        self.horizontalLayout_101.setObjectName(u"horizontalLayout_101")
        self.horizontalLayout_101.setContentsMargins(0, 0, 0, 0)
        self.frame_287 = QFrame(self.frame_282)
        self.frame_287.setObjectName(u"frame_287")
        self.frame_287.setMaximumSize(QSize(250, 16777215))
        self.frame_287.setFrameShape(QFrame.StyledPanel)
        self.frame_287.setFrameShadow(QFrame.Raised)
        self.verticalLayout_262 = QVBoxLayout(self.frame_287)
        self.verticalLayout_262.setSpacing(0)
        self.verticalLayout_262.setObjectName(u"verticalLayout_262")
        self.verticalLayout_262.setContentsMargins(0, 0, 0, 0)
        self.label_50 = QLabel(self.frame_287)
        self.label_50.setObjectName(u"label_50")

        self.verticalLayout_262.addWidget(self.label_50)

        self.unit_prise = QLineEdit(self.frame_287)
        self.unit_prise.setObjectName(u"unit_prise")
        self.unit_prise.setMaximumSize(QSize(250, 37))
        self.unit_prise.setFont(font2)

        self.verticalLayout_262.addWidget(self.unit_prise)


        self.horizontalLayout_101.addWidget(self.frame_287)

        self.frame_288 = QFrame(self.frame_282)
        self.frame_288.setObjectName(u"frame_288")
        self.frame_288.setFrameShape(QFrame.StyledPanel)
        self.frame_288.setFrameShadow(QFrame.Raised)
        self.verticalLayout_265 = QVBoxLayout(self.frame_288)
        self.verticalLayout_265.setSpacing(0)
        self.verticalLayout_265.setObjectName(u"verticalLayout_265")
        self.verticalLayout_265.setContentsMargins(0, 0, 0, 0)
        self.label_51 = QLabel(self.frame_288)
        self.label_51.setObjectName(u"label_51")

        self.verticalLayout_265.addWidget(self.label_51)

        self.total_prise = QLineEdit(self.frame_288)
        self.total_prise.setObjectName(u"total_prise")
        self.total_prise.setMaximumSize(QSize(250, 37))
        self.total_prise.setFont(font2)

        self.verticalLayout_265.addWidget(self.total_prise)


        self.horizontalLayout_101.addWidget(self.frame_288)


        self.verticalLayout_258.addWidget(self.frame_282, 0, Qt.AlignTop)

        self.vente_status = QComboBox(self.frame_279)
        self.vente_status.setObjectName(u"vente_status")
        self.vente_status.setFont(font2)

        self.verticalLayout_258.addWidget(self.vente_status)

        self.frame_281 = QFrame(self.frame_279)
        self.frame_281.setObjectName(u"frame_281")
        self.frame_281.setFrameShape(QFrame.StyledPanel)
        self.frame_281.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_107 = QHBoxLayout(self.frame_281)
        self.horizontalLayout_107.setObjectName(u"horizontalLayout_107")
        self.horizontalLayout_107.setContentsMargins(-1, 0, -1, 0)
        self.frame_301 = QFrame(self.frame_281)
        self.frame_301.setObjectName(u"frame_301")
        self.frame_301.setFrameShape(QFrame.StyledPanel)
        self.frame_301.setFrameShadow(QFrame.Raised)
        self.verticalLayout_266 = QVBoxLayout(self.frame_301)
        self.verticalLayout_266.setObjectName(u"verticalLayout_266")
        self.delete_vente = QPushButton(self.frame_301)
        self.delete_vente.setObjectName(u"delete_vente")
        self.delete_vente.setFont(font4)
        self.delete_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.delete_vente.setAutoExclusive(True)

        self.verticalLayout_266.addWidget(self.delete_vente)


        self.horizontalLayout_107.addWidget(self.frame_301, 0, Qt.AlignHCenter)

        self.ajouter_vente = QPushButton(self.frame_281)
        self.ajouter_vente.setObjectName(u"ajouter_vente")
        self.ajouter_vente.setMinimumSize(QSize(100, 0))
        self.ajouter_vente.setFont(font4)
        self.ajouter_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_107.addWidget(self.ajouter_vente)


        self.verticalLayout_258.addWidget(self.frame_281, 0, Qt.AlignRight|Qt.AlignTop)


        self.verticalLayout_259.addWidget(self.frame_279, 0, Qt.AlignTop)

        self.frame_280 = QFrame(self.frame_276)
        self.frame_280.setObjectName(u"frame_280")
        self.frame_280.setFrameShape(QFrame.StyledPanel)
        self.frame_280.setFrameShadow(QFrame.Raised)
        self.verticalLayout_268 = QVBoxLayout(self.frame_280)
        self.verticalLayout_268.setSpacing(0)
        self.verticalLayout_268.setObjectName(u"verticalLayout_268")
        self.verticalLayout_268.setContentsMargins(0, 0, 0, 0)
        self.table_search_student_vente = QTableWidget(self.frame_280)
        self.table_search_student_vente.setObjectName(u"table_search_student_vente")
        self.table_search_student_vente.setSortingEnabled(True)
        self.table_search_student_vente.horizontalHeader().setHighlightSections(False)
        self.table_search_student_vente.verticalHeader().setVisible(False)
        self.table_search_student_vente.verticalHeader().setHighlightSections(False)

        self.verticalLayout_268.addWidget(self.table_search_student_vente, 0, Qt.AlignTop)


        self.verticalLayout_259.addWidget(self.frame_280, 0, Qt.AlignTop)


        self.horizontalLayout_99.addWidget(self.frame_276, 0, Qt.AlignTop)

        self.frame_277 = QFrame(self.frame_274)
        self.frame_277.setObjectName(u"frame_277")
        self.frame_277.setMinimumSize(QSize(500, 0))
        self.frame_277.setFrameShape(QFrame.StyledPanel)
        self.frame_277.setFrameShadow(QFrame.Raised)
        self.verticalLayout_267 = QVBoxLayout(self.frame_277)
        self.verticalLayout_267.setSpacing(6)
        self.verticalLayout_267.setObjectName(u"verticalLayout_267")
        self.verticalLayout_267.setContentsMargins(0, 0, 0, 0)
        self.frame_289 = QFrame(self.frame_277)
        self.frame_289.setObjectName(u"frame_289")
        self.frame_289.setFrameShape(QFrame.StyledPanel)
        self.frame_289.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_126 = QHBoxLayout(self.frame_289)
        self.horizontalLayout_126.setSpacing(20)
        self.horizontalLayout_126.setObjectName(u"horizontalLayout_126")
        self.imprimer_vente = QPushButton(self.frame_289)
        self.imprimer_vente.setObjectName(u"imprimer_vente")
        self.imprimer_vente.setFont(font4)
        self.imprimer_vente.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_126.addWidget(self.imprimer_vente)

        self.frame_292 = QFrame(self.frame_289)
        self.frame_292.setObjectName(u"frame_292")
        self.frame_292.setFrameShape(QFrame.StyledPanel)
        self.frame_292.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_102 = QHBoxLayout(self.frame_292)
        self.horizontalLayout_102.setSpacing(10)
        self.horizontalLayout_102.setObjectName(u"horizontalLayout_102")
        self.horizontalLayout_102.setContentsMargins(0, 0, 0, 0)
        self.label_63 = QLabel(self.frame_292)
        self.label_63.setObjectName(u"label_63")

        self.horizontalLayout_102.addWidget(self.label_63)

        self.label_commande_number = QLabel(self.frame_292)
        self.label_commande_number.setObjectName(u"label_commande_number")
        self.label_commande_number.setMinimumSize(QSize(20, 0))

        self.horizontalLayout_102.addWidget(self.label_commande_number)


        self.horizontalLayout_126.addWidget(self.frame_292)


        self.verticalLayout_267.addWidget(self.frame_289, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_290 = QFrame(self.frame_277)
        self.frame_290.setObjectName(u"frame_290")
        sizePolicy.setHeightForWidth(self.frame_290.sizePolicy().hasHeightForWidth())
        self.frame_290.setSizePolicy(sizePolicy)
        self.frame_290.setFrameShape(QFrame.StyledPanel)
        self.frame_290.setFrameShadow(QFrame.Raised)
        self.verticalLayout_270 = QVBoxLayout(self.frame_290)
        self.verticalLayout_270.setObjectName(u"verticalLayout_270")
        self.table_show_order = QTableWidget(self.frame_290)
        self.table_show_order.setObjectName(u"table_show_order")
        self.table_show_order.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_show_order.setSortingEnabled(True)
        self.table_show_order.horizontalHeader().setVisible(True)
        self.table_show_order.horizontalHeader().setCascadingSectionResizes(True)
        self.table_show_order.horizontalHeader().setProperty(u"showSortIndicator", True)
        self.table_show_order.horizontalHeader().setStretchLastSection(True)
        self.table_show_order.verticalHeader().setVisible(False)
        self.table_show_order.verticalHeader().setHighlightSections(False)

        self.verticalLayout_270.addWidget(self.table_show_order)


        self.verticalLayout_267.addWidget(self.frame_290)

        self.frame_291 = QFrame(self.frame_277)
        self.frame_291.setObjectName(u"frame_291")
        self.frame_291.setFrameShape(QFrame.StyledPanel)
        self.frame_291.setFrameShadow(QFrame.Raised)
        self.verticalLayout_271 = QVBoxLayout(self.frame_291)
        self.verticalLayout_271.setObjectName(u"verticalLayout_271")
        self.verticalLayout_271.setContentsMargins(-1, 0, -1, 0)
        self.frame_293 = QFrame(self.frame_291)
        self.frame_293.setObjectName(u"frame_293")
        self.frame_293.setFrameShape(QFrame.StyledPanel)
        self.frame_293.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_103 = QHBoxLayout(self.frame_293)
        self.horizontalLayout_103.setObjectName(u"horizontalLayout_103")
        self.label_88 = QLabel(self.frame_293)
        self.label_88.setObjectName(u"label_88")
        self.label_88.setFont(font1)

        self.horizontalLayout_103.addWidget(self.label_88)

        self.label_total_commande = QLabel(self.frame_293)
        self.label_total_commande.setObjectName(u"label_total_commande")
        self.label_total_commande.setFont(font1)

        self.horizontalLayout_103.addWidget(self.label_total_commande, 0, Qt.AlignRight)


        self.verticalLayout_271.addWidget(self.frame_293)

        self.frame_294 = QFrame(self.frame_291)
        self.frame_294.setObjectName(u"frame_294")
        self.frame_294.setFrameShape(QFrame.StyledPanel)
        self.frame_294.setFrameShadow(QFrame.Raised)
        self.verticalLayout_272 = QVBoxLayout(self.frame_294)
        self.verticalLayout_272.setObjectName(u"verticalLayout_272")
        self.verticalLayout_272.setContentsMargins(-1, 0, -1, 0)
        self.passer_la_commande = QPushButton(self.frame_294)
        self.passer_la_commande.setObjectName(u"passer_la_commande")
        self.passer_la_commande.setMinimumSize(QSize(190, 0))
        self.passer_la_commande.setFont(font)
        self.passer_la_commande.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_272.addWidget(self.passer_la_commande)


        self.verticalLayout_271.addWidget(self.frame_294, 0, Qt.AlignRight)


        self.verticalLayout_267.addWidget(self.frame_291)


        self.horizontalLayout_99.addWidget(self.frame_277)


        self.horizontalLayout_98.addWidget(self.frame_274, 0, Qt.AlignTop)

        self.tabWidget_2.addTab(self.add_vente, "")
        self.loans_widget = QWidget()
        self.loans_widget.setObjectName(u"loans_widget")
        self.verticalLayout_355 = QVBoxLayout(self.loans_widget)
        self.verticalLayout_355.setObjectName(u"verticalLayout_355")
        self.frame_414 = QFrame(self.loans_widget)
        self.frame_414.setObjectName(u"frame_414")
        self.frame_414.setMaximumSize(QSize(500, 16777215))
        self.frame_414.setFrameShape(QFrame.StyledPanel)
        self.frame_414.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_174 = QHBoxLayout(self.frame_414)
        self.horizontalLayout_174.setSpacing(0)
        self.horizontalLayout_174.setObjectName(u"horizontalLayout_174")
        self.horizontalLayout_174.setContentsMargins(0, 9, 0, 0)
        self.frame_418 = QFrame(self.frame_414)
        self.frame_418.setObjectName(u"frame_418")
        self.frame_418.setMaximumSize(QSize(300, 16777215))
        self.frame_418.setFrameShape(QFrame.StyledPanel)
        self.frame_418.setFrameShadow(QFrame.Raised)
        self.verticalLayout_357 = QVBoxLayout(self.frame_418)
        self.verticalLayout_357.setSpacing(0)
        self.verticalLayout_357.setObjectName(u"verticalLayout_357")
        self.verticalLayout_357.setContentsMargins(0, 0, 0, 0)
        self.accorder_un_pret = QPushButton(self.frame_418)
        self.accorder_un_pret.setObjectName(u"accorder_un_pret")
        self.accorder_un_pret.setMinimumSize(QSize(200, 0))
        self.accorder_un_pret.setFont(font4)
        self.accorder_un_pret.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.accorder_un_pret.setCheckable(True)

        self.verticalLayout_357.addWidget(self.accorder_un_pret)


        self.horizontalLayout_174.addWidget(self.frame_418, 0, Qt.AlignLeft|Qt.AlignTop)

        self.frame_417 = QFrame(self.frame_414)
        self.frame_417.setObjectName(u"frame_417")
        self.frame_417.setMaximumSize(QSize(300, 16777215))
        self.frame_417.setFrameShape(QFrame.StyledPanel)
        self.frame_417.setFrameShadow(QFrame.Raised)
        self.verticalLayout_356 = QVBoxLayout(self.frame_417)
        self.verticalLayout_356.setSpacing(0)
        self.verticalLayout_356.setObjectName(u"verticalLayout_356")
        self.verticalLayout_356.setContentsMargins(0, 0, 0, 0)
        self.faire_un_remboursement3 = QPushButton(self.frame_417)
        self.faire_un_remboursement3.setObjectName(u"faire_un_remboursement3")
        self.faire_un_remboursement3.setMinimumSize(QSize(250, 0))
        self.faire_un_remboursement3.setFont(font4)
        self.faire_un_remboursement3.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_356.addWidget(self.faire_un_remboursement3, 0, Qt.AlignLeft)


        self.horizontalLayout_174.addWidget(self.frame_417, 0, Qt.AlignLeft|Qt.AlignTop)


        self.verticalLayout_355.addWidget(self.frame_414)

        self.frame_416 = QFrame(self.loans_widget)
        self.frame_416.setObjectName(u"frame_416")
        self.frame_416.setFrameShape(QFrame.StyledPanel)
        self.frame_416.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_175 = QHBoxLayout(self.frame_416)
        self.horizontalLayout_175.setObjectName(u"horizontalLayout_175")
        self.tabWidget_4 = QTabWidget(self.frame_416)
        self.tabWidget_4.setObjectName(u"tabWidget_4")
        self.tab_loans = QWidget()
        self.tab_loans.setObjectName(u"tab_loans")
        self.verticalLayout_358 = QVBoxLayout(self.tab_loans)
        self.verticalLayout_358.setObjectName(u"verticalLayout_358")
        self.frame_415 = QFrame(self.tab_loans)
        self.frame_415.setObjectName(u"frame_415")
        self.frame_415.setFrameShape(QFrame.StyledPanel)
        self.frame_415.setFrameShadow(QFrame.Raised)
        self.verticalLayout_359 = QVBoxLayout(self.frame_415)
        self.verticalLayout_359.setObjectName(u"verticalLayout_359")
        self.verticalLayout_359.setContentsMargins(0, 9, 0, 0)
        self.loans_search = QLineEdit(self.frame_415)
        self.loans_search.setObjectName(u"loans_search")
        self.loans_search.setMinimumSize(QSize(400, 37))

        self.verticalLayout_359.addWidget(self.loans_search)


        self.verticalLayout_358.addWidget(self.frame_415, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_419 = QFrame(self.tab_loans)
        self.frame_419.setObjectName(u"frame_419")
        self.frame_419.setFrameShape(QFrame.StyledPanel)
        self.frame_419.setFrameShadow(QFrame.Raised)
        self.verticalLayout_360 = QVBoxLayout(self.frame_419)
        self.verticalLayout_360.setObjectName(u"verticalLayout_360")
        self.verticalLayout_360.setContentsMargins(0, 0, 0, 0)
        self.loans_table = QTableWidget(self.frame_419)
        self.loans_table.setObjectName(u"loans_table")

        self.verticalLayout_360.addWidget(self.loans_table)

        self.frame_422 = QFrame(self.frame_419)
        self.frame_422.setObjectName(u"frame_422")
        self.frame_422.setFrameShape(QFrame.StyledPanel)
        self.frame_422.setFrameShadow(QFrame.Raised)
        self.verticalLayout_364 = QVBoxLayout(self.frame_422)
        self.verticalLayout_364.setObjectName(u"verticalLayout_364")
        self.verticalLayout_364.setContentsMargins(0, 0, 0, 0)
        self.frame_423 = QFrame(self.frame_422)
        self.frame_423.setObjectName(u"frame_423")
        self.frame_423.setFrameShape(QFrame.StyledPanel)
        self.frame_423.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_178 = QHBoxLayout(self.frame_423)
        self.horizontalLayout_178.setSpacing(50)
        self.horizontalLayout_178.setObjectName(u"horizontalLayout_178")
        self.horizontalLayout_178.setContentsMargins(0, 0, 0, 0)
        self.prev_loans = QPushButton(self.frame_423)
        self.prev_loans.setObjectName(u"prev_loans")
        self.prev_loans.setMinimumSize(QSize(50, 0))
        self.prev_loans.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_178.addWidget(self.prev_loans)

        self.next_loans = QPushButton(self.frame_423)
        self.next_loans.setObjectName(u"next_loans")
        self.next_loans.setMinimumSize(QSize(50, 0))

        self.horizontalLayout_178.addWidget(self.next_loans)


        self.verticalLayout_364.addWidget(self.frame_423)


        self.verticalLayout_360.addWidget(self.frame_422, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_358.addWidget(self.frame_419)

        self.tabWidget_4.addTab(self.tab_loans, "")
        self.tab_loans_form = QWidget()
        self.tab_loans_form.setObjectName(u"tab_loans_form")
        self.verticalLayout_365 = QVBoxLayout(self.tab_loans_form)
        self.verticalLayout_365.setObjectName(u"verticalLayout_365")
        self.frame_424 = QFrame(self.tab_loans_form)
        self.frame_424.setObjectName(u"frame_424")
        self.frame_424.setFrameShape(QFrame.StyledPanel)
        self.frame_424.setFrameShadow(QFrame.Raised)
        self.verticalLayout_366 = QVBoxLayout(self.frame_424)
        self.verticalLayout_366.setSpacing(0)
        self.verticalLayout_366.setObjectName(u"verticalLayout_366")
        self.verticalLayout_366.setContentsMargins(0, 0, 0, 0)
        self.frame_425 = QFrame(self.frame_424)
        self.frame_425.setObjectName(u"frame_425")
        self.frame_425.setFrameShape(QFrame.StyledPanel)
        self.frame_425.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_180 = QHBoxLayout(self.frame_425)
        self.horizontalLayout_180.setSpacing(17)
        self.horizontalLayout_180.setObjectName(u"horizontalLayout_180")
        self.horizontalLayout_180.setContentsMargins(0, 0, 0, 0)
        self.frame_429 = QFrame(self.frame_425)
        self.frame_429.setObjectName(u"frame_429")
        self.frame_429.setFrameShape(QFrame.StyledPanel)
        self.frame_429.setFrameShadow(QFrame.Raised)
        self.verticalLayout_374 = QVBoxLayout(self.frame_429)
        self.verticalLayout_374.setObjectName(u"verticalLayout_374")
        self.label_161 = QLabel(self.frame_429)
        self.label_161.setObjectName(u"label_161")

        self.verticalLayout_374.addWidget(self.label_161)

        self.identifiant_user = QComboBox(self.frame_429)
        self.identifiant_user.setObjectName(u"identifiant_user")
        self.identifiant_user.setMinimumSize(QSize(300, 37))
        self.identifiant_user.setFont(font2)
        self.identifiant_user.setEditable(True)

        self.verticalLayout_374.addWidget(self.identifiant_user)


        self.horizontalLayout_180.addWidget(self.frame_429)

        self.frame_430 = QFrame(self.frame_425)
        self.frame_430.setObjectName(u"frame_430")
        self.frame_430.setFrameShape(QFrame.StyledPanel)
        self.frame_430.setFrameShadow(QFrame.Raised)
        self.verticalLayout_373 = QVBoxLayout(self.frame_430)
        self.verticalLayout_373.setObjectName(u"verticalLayout_373")
        self.label_162 = QLabel(self.frame_430)
        self.label_162.setObjectName(u"label_162")

        self.verticalLayout_373.addWidget(self.label_162)

        self.amount = QLineEdit(self.frame_430)
        self.amount.setObjectName(u"amount")
        self.amount.setFont(font2)
        self.amount.setClearButtonEnabled(True)

        self.verticalLayout_373.addWidget(self.amount)


        self.horizontalLayout_180.addWidget(self.frame_430)

        self.frame_431 = QFrame(self.frame_425)
        self.frame_431.setObjectName(u"frame_431")
        self.frame_431.setFrameShape(QFrame.StyledPanel)
        self.frame_431.setFrameShadow(QFrame.Raised)
        self.verticalLayout_368 = QVBoxLayout(self.frame_431)
        self.verticalLayout_368.setObjectName(u"verticalLayout_368")
        self.label_163 = QLabel(self.frame_431)
        self.label_163.setObjectName(u"label_163")

        self.verticalLayout_368.addWidget(self.label_163)

        self.term_months = QLineEdit(self.frame_431)
        self.term_months.setObjectName(u"term_months")
        self.term_months.setFont(font2)

        self.verticalLayout_368.addWidget(self.term_months)


        self.horizontalLayout_180.addWidget(self.frame_431)


        self.verticalLayout_366.addWidget(self.frame_425)

        self.frame_426 = QFrame(self.frame_424)
        self.frame_426.setObjectName(u"frame_426")
        self.frame_426.setFrameShape(QFrame.StyledPanel)
        self.frame_426.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_179 = QHBoxLayout(self.frame_426)
        self.horizontalLayout_179.setSpacing(17)
        self.horizontalLayout_179.setObjectName(u"horizontalLayout_179")
        self.horizontalLayout_179.setContentsMargins(0, 0, 0, 0)
        self.frame_432 = QFrame(self.frame_426)
        self.frame_432.setObjectName(u"frame_432")
        self.frame_432.setFrameShape(QFrame.StyledPanel)
        self.frame_432.setFrameShadow(QFrame.Raised)
        self.verticalLayout_379 = QVBoxLayout(self.frame_432)
        self.verticalLayout_379.setObjectName(u"verticalLayout_379")
        self.label_164 = QLabel(self.frame_432)
        self.label_164.setObjectName(u"label_164")

        self.verticalLayout_379.addWidget(self.label_164)

        self.interest_rate = QLineEdit(self.frame_432)
        self.interest_rate.setObjectName(u"interest_rate")
        self.interest_rate.setFont(font2)
        self.interest_rate.setReadOnly(True)

        self.verticalLayout_379.addWidget(self.interest_rate)


        self.horizontalLayout_179.addWidget(self.frame_432)

        self.frame_433 = QFrame(self.frame_426)
        self.frame_433.setObjectName(u"frame_433")
        self.frame_433.setFrameShape(QFrame.StyledPanel)
        self.frame_433.setFrameShadow(QFrame.Raised)
        self.verticalLayout_369 = QVBoxLayout(self.frame_433)
        self.verticalLayout_369.setObjectName(u"verticalLayout_369")
        self.label_165 = QLabel(self.frame_433)
        self.label_165.setObjectName(u"label_165")

        self.verticalLayout_369.addWidget(self.label_165)

        self.monthly_payment = QLineEdit(self.frame_433)
        self.monthly_payment.setObjectName(u"monthly_payment")
        self.monthly_payment.setFont(font2)
        self.monthly_payment.setReadOnly(False)

        self.verticalLayout_369.addWidget(self.monthly_payment)


        self.horizontalLayout_179.addWidget(self.frame_433)

        self.frame_434 = QFrame(self.frame_426)
        self.frame_434.setObjectName(u"frame_434")
        self.frame_434.setFrameShape(QFrame.StyledPanel)
        self.frame_434.setFrameShadow(QFrame.Raised)
        self.verticalLayout_377 = QVBoxLayout(self.frame_434)
        self.verticalLayout_377.setObjectName(u"verticalLayout_377")
        self.label_166 = QLabel(self.frame_434)
        self.label_166.setObjectName(u"label_166")

        self.verticalLayout_377.addWidget(self.label_166)

        self.loans_status = QComboBox(self.frame_434)
        self.loans_status.setObjectName(u"loans_status")
        self.loans_status.setMinimumSize(QSize(250, 37))
        self.loans_status.setFont(font2)

        self.verticalLayout_377.addWidget(self.loans_status)


        self.horizontalLayout_179.addWidget(self.frame_434)


        self.verticalLayout_366.addWidget(self.frame_426)

        self.frame_428 = QFrame(self.frame_424)
        self.frame_428.setObjectName(u"frame_428")
        self.frame_428.setFrameShape(QFrame.StyledPanel)
        self.frame_428.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_181 = QHBoxLayout(self.frame_428)
        self.horizontalLayout_181.setSpacing(17)
        self.horizontalLayout_181.setObjectName(u"horizontalLayout_181")
        self.horizontalLayout_181.setContentsMargins(0, 0, 0, 0)
        self.frame_435 = QFrame(self.frame_428)
        self.frame_435.setObjectName(u"frame_435")
        self.frame_435.setFrameShape(QFrame.StyledPanel)
        self.frame_435.setFrameShadow(QFrame.Raised)
        self.verticalLayout_375 = QVBoxLayout(self.frame_435)
        self.verticalLayout_375.setObjectName(u"verticalLayout_375")
        self.label_169 = QLabel(self.frame_435)
        self.label_169.setObjectName(u"label_169")

        self.verticalLayout_375.addWidget(self.label_169)

        self.approved_by = QLineEdit(self.frame_435)
        self.approved_by.setObjectName(u"approved_by")
        self.approved_by.setFont(font2)
        self.approved_by.setReadOnly(True)

        self.verticalLayout_375.addWidget(self.approved_by)


        self.horizontalLayout_181.addWidget(self.frame_435)

        self.frame_436 = QFrame(self.frame_428)
        self.frame_436.setObjectName(u"frame_436")
        self.frame_436.setFrameShape(QFrame.StyledPanel)
        self.frame_436.setFrameShadow(QFrame.Raised)
        self.verticalLayout_371 = QVBoxLayout(self.frame_436)
        self.verticalLayout_371.setObjectName(u"verticalLayout_371")
        self.label_168 = QLabel(self.frame_436)
        self.label_168.setObjectName(u"label_168")

        self.verticalLayout_371.addWidget(self.label_168)

        self.approved_at = QLineEdit(self.frame_436)
        self.approved_at.setObjectName(u"approved_at")
        self.approved_at.setFont(font2)
        self.approved_at.setReadOnly(True)

        self.verticalLayout_371.addWidget(self.approved_at)


        self.horizontalLayout_181.addWidget(self.frame_436)

        self.frame_437 = QFrame(self.frame_428)
        self.frame_437.setObjectName(u"frame_437")
        self.frame_437.setFrameShape(QFrame.StyledPanel)
        self.frame_437.setFrameShadow(QFrame.Raised)
        self.verticalLayout_370 = QVBoxLayout(self.frame_437)
        self.verticalLayout_370.setObjectName(u"verticalLayout_370")
        self.label_167 = QLabel(self.frame_437)
        self.label_167.setObjectName(u"label_167")

        self.verticalLayout_370.addWidget(self.label_167)

        self.disbursed_at = QLineEdit(self.frame_437)
        self.disbursed_at.setObjectName(u"disbursed_at")
        self.disbursed_at.setFont(font2)
        self.disbursed_at.setReadOnly(True)

        self.verticalLayout_370.addWidget(self.disbursed_at)


        self.horizontalLayout_181.addWidget(self.frame_437)


        self.verticalLayout_366.addWidget(self.frame_428)

        self.frame_427 = QFrame(self.frame_424)
        self.frame_427.setObjectName(u"frame_427")
        self.frame_427.setFrameShape(QFrame.StyledPanel)
        self.frame_427.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_182 = QHBoxLayout(self.frame_427)
        self.horizontalLayout_182.setSpacing(17)
        self.horizontalLayout_182.setObjectName(u"horizontalLayout_182")
        self.horizontalLayout_182.setContentsMargins(0, 0, 0, 0)
        self.frame_438 = QFrame(self.frame_427)
        self.frame_438.setObjectName(u"frame_438")
        self.frame_438.setFrameShape(QFrame.StyledPanel)
        self.frame_438.setFrameShadow(QFrame.Raised)
        self.verticalLayout_378 = QVBoxLayout(self.frame_438)
        self.verticalLayout_378.setObjectName(u"verticalLayout_378")
        self.label_170 = QLabel(self.frame_438)
        self.label_170.setObjectName(u"label_170")

        self.verticalLayout_378.addWidget(self.label_170)

        self.remaining_balance = QLineEdit(self.frame_438)
        self.remaining_balance.setObjectName(u"remaining_balance")
        self.remaining_balance.setFont(font2)
        self.remaining_balance.setReadOnly(True)

        self.verticalLayout_378.addWidget(self.remaining_balance)


        self.horizontalLayout_182.addWidget(self.frame_438)

        self.frame_439 = QFrame(self.frame_427)
        self.frame_439.setObjectName(u"frame_439")
        self.frame_439.setFrameShape(QFrame.StyledPanel)
        self.frame_439.setFrameShadow(QFrame.Raised)
        self.verticalLayout_376 = QVBoxLayout(self.frame_439)
        self.verticalLayout_376.setObjectName(u"verticalLayout_376")
        self.label_171 = QLabel(self.frame_439)
        self.label_171.setObjectName(u"label_171")

        self.verticalLayout_376.addWidget(self.label_171)

        self.created_at = QLineEdit(self.frame_439)
        self.created_at.setObjectName(u"created_at")
        self.created_at.setFont(font2)
        self.created_at.setReadOnly(True)

        self.verticalLayout_376.addWidget(self.created_at)


        self.horizontalLayout_182.addWidget(self.frame_439)

        self.frame_440 = QFrame(self.frame_427)
        self.frame_440.setObjectName(u"frame_440")
        self.frame_440.setFrameShape(QFrame.StyledPanel)
        self.frame_440.setFrameShadow(QFrame.Raised)
        self.verticalLayout_372 = QVBoxLayout(self.frame_440)
        self.verticalLayout_372.setObjectName(u"verticalLayout_372")
        self.label_172 = QLabel(self.frame_440)
        self.label_172.setObjectName(u"label_172")

        self.verticalLayout_372.addWidget(self.label_172)

        self.updated_at = QLineEdit(self.frame_440)
        self.updated_at.setObjectName(u"updated_at")
        self.updated_at.setFont(font2)
        self.updated_at.setReadOnly(True)

        self.verticalLayout_372.addWidget(self.updated_at)


        self.horizontalLayout_182.addWidget(self.frame_440)


        self.verticalLayout_366.addWidget(self.frame_427)

        self.frame_441 = QFrame(self.frame_424)
        self.frame_441.setObjectName(u"frame_441")
        self.frame_441.setFont(font4)
        self.frame_441.setFrameShape(QFrame.StyledPanel)
        self.frame_441.setFrameShadow(QFrame.Raised)
        self.verticalLayout_367 = QVBoxLayout(self.frame_441)
        self.verticalLayout_367.setObjectName(u"verticalLayout_367")
        self.verticalLayout_367.setContentsMargins(0, -1, -1, 0)
        self.valider_loans = QPushButton(self.frame_441)
        self.valider_loans.setObjectName(u"valider_loans")
        self.valider_loans.setMinimumSize(QSize(200, 0))
        self.valider_loans.setFont(font4)
        self.valider_loans.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_367.addWidget(self.valider_loans, 0, Qt.AlignBottom)


        self.verticalLayout_366.addWidget(self.frame_441, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_365.addWidget(self.frame_424)

        self.tabWidget_4.addTab(self.tab_loans_form, "")
        self.tab_rembousement = QWidget()
        self.tab_rembousement.setObjectName(u"tab_rembousement")
        self.horizontalLayout_183 = QHBoxLayout(self.tab_rembousement)
        self.horizontalLayout_183.setObjectName(u"horizontalLayout_183")
        self.horizontalLayout_183.setContentsMargins(-1, 0, -1, 0)
        self.frame_447 = QFrame(self.tab_rembousement)
        self.frame_447.setObjectName(u"frame_447")
        self.frame_447.setFrameShape(QFrame.StyledPanel)
        self.frame_447.setFrameShadow(QFrame.Raised)
        self.verticalLayout_384 = QVBoxLayout(self.frame_447)
        self.verticalLayout_384.setSpacing(0)
        self.verticalLayout_384.setObjectName(u"verticalLayout_384")
        self.verticalLayout_384.setContentsMargins(-1, 0, -1, 0)
        self.frame_449 = QFrame(self.frame_447)
        self.frame_449.setObjectName(u"frame_449")
        self.frame_449.setFrameShape(QFrame.StyledPanel)
        self.frame_449.setFrameShadow(QFrame.Raised)
        self.verticalLayout_385 = QVBoxLayout(self.frame_449)
        self.verticalLayout_385.setSpacing(0)
        self.verticalLayout_385.setObjectName(u"verticalLayout_385")
        self.verticalLayout_385.setContentsMargins(-1, 9, 0, 0)
        self.label_179 = QLabel(self.frame_449)
        self.label_179.setObjectName(u"label_179")

        self.verticalLayout_385.addWidget(self.label_179)


        self.verticalLayout_384.addWidget(self.frame_449, 0, Qt.AlignHCenter)

        self.scrollArea_10 = QScrollArea(self.frame_447)
        self.scrollArea_10.setObjectName(u"scrollArea_10")
        self.scrollArea_10.setWidgetResizable(True)
        self.scrollAreaWidgetContents_14 = QWidget()
        self.scrollAreaWidgetContents_14.setObjectName(u"scrollAreaWidgetContents_14")
        self.scrollAreaWidgetContents_14.setGeometry(QRect(0, 0, 16, 16))
        self.frame_448 = QFrame(self.scrollAreaWidgetContents_14)
        self.frame_448.setObjectName(u"frame_448")
        self.frame_448.setGeometry(QRect(0, 30, 120, 80))
        self.frame_448.setFrameShape(QFrame.StyledPanel)
        self.frame_448.setFrameShadow(QFrame.Raised)
        self.scrollArea_10.setWidget(self.scrollAreaWidgetContents_14)

        self.verticalLayout_384.addWidget(self.scrollArea_10)


        self.horizontalLayout_183.addWidget(self.frame_447)

        self.widget_20 = QWidget(self.tab_rembousement)
        self.widget_20.setObjectName(u"widget_20")
        self.verticalLayout_361 = QVBoxLayout(self.widget_20)
        self.verticalLayout_361.setObjectName(u"verticalLayout_361")
        self.verticalLayout_361.setContentsMargins(-1, 0, -1, 0)
        self.label_173 = QLabel(self.widget_20)
        self.label_173.setObjectName(u"label_173")
        self.label_173.setFont(font2)

        self.verticalLayout_361.addWidget(self.label_173)

        self.frame_420 = QFrame(self.widget_20)
        self.frame_420.setObjectName(u"frame_420")
        self.frame_420.setFrameShape(QFrame.StyledPanel)
        self.frame_420.setFrameShadow(QFrame.Raised)
        self.verticalLayout_362 = QVBoxLayout(self.frame_420)
        self.verticalLayout_362.setSpacing(0)
        self.verticalLayout_362.setObjectName(u"verticalLayout_362")
        self.verticalLayout_362.setContentsMargins(-1, 0, -1, 0)
        self.label_174 = QLabel(self.frame_420)
        self.label_174.setObjectName(u"label_174")

        self.verticalLayout_362.addWidget(self.label_174)

        self.month_ter = QLineEdit(self.frame_420)
        self.month_ter.setObjectName(u"month_ter")
        self.month_ter.setFont(font2)
        self.month_ter.setReadOnly(True)

        self.verticalLayout_362.addWidget(self.month_ter)


        self.verticalLayout_361.addWidget(self.frame_420)

        self.loans_id = QLineEdit(self.widget_20)
        self.loans_id.setObjectName(u"loans_id")

        self.verticalLayout_361.addWidget(self.loans_id)

        self.frame_421 = QFrame(self.widget_20)
        self.frame_421.setObjectName(u"frame_421")
        self.frame_421.setFrameShape(QFrame.StyledPanel)
        self.frame_421.setFrameShadow(QFrame.Raised)
        self.verticalLayout_363 = QVBoxLayout(self.frame_421)
        self.verticalLayout_363.setSpacing(0)
        self.verticalLayout_363.setObjectName(u"verticalLayout_363")
        self.verticalLayout_363.setContentsMargins(-1, 0, -1, 0)
        self.label_176 = QLabel(self.frame_421)
        self.label_176.setObjectName(u"label_176")

        self.verticalLayout_363.addWidget(self.label_176)

        self.inter_rate = QLineEdit(self.frame_421)
        self.inter_rate.setObjectName(u"inter_rate")
        self.inter_rate.setFont(font2)
        self.inter_rate.setReadOnly(True)

        self.verticalLayout_363.addWidget(self.inter_rate)


        self.verticalLayout_361.addWidget(self.frame_421)

        self.frame_446 = QFrame(self.widget_20)
        self.frame_446.setObjectName(u"frame_446")
        self.frame_446.setFrameShape(QFrame.StyledPanel)
        self.frame_446.setFrameShadow(QFrame.Raised)
        self.verticalLayout_323 = QVBoxLayout(self.frame_446)
        self.verticalLayout_323.setSpacing(0)
        self.verticalLayout_323.setObjectName(u"verticalLayout_323")
        self.verticalLayout_323.setContentsMargins(-1, 0, -1, 0)
        self.label_178 = QLabel(self.frame_446)
        self.label_178.setObjectName(u"label_178")

        self.verticalLayout_323.addWidget(self.label_178)

        self.payment_methode = QLineEdit(self.frame_446)
        self.payment_methode.setObjectName(u"payment_methode")
        self.payment_methode.setReadOnly(True)

        self.verticalLayout_323.addWidget(self.payment_methode)


        self.verticalLayout_361.addWidget(self.frame_446)

        self.frame_442 = QFrame(self.widget_20)
        self.frame_442.setObjectName(u"frame_442")
        self.frame_442.setFrameShape(QFrame.StyledPanel)
        self.frame_442.setFrameShadow(QFrame.Raised)
        self.verticalLayout_380 = QVBoxLayout(self.frame_442)
        self.verticalLayout_380.setSpacing(0)
        self.verticalLayout_380.setObjectName(u"verticalLayout_380")
        self.verticalLayout_380.setContentsMargins(-1, 0, -1, 0)
        self.label_175 = QLabel(self.frame_442)
        self.label_175.setObjectName(u"label_175")

        self.verticalLayout_380.addWidget(self.label_175)

        self.amount_to_pay = QLineEdit(self.frame_442)
        self.amount_to_pay.setObjectName(u"amount_to_pay")
        self.amount_to_pay.setFont(font2)

        self.verticalLayout_380.addWidget(self.amount_to_pay)


        self.verticalLayout_361.addWidget(self.frame_442)

        self.frame_443 = QFrame(self.widget_20)
        self.frame_443.setObjectName(u"frame_443")
        self.frame_443.setFrameShape(QFrame.StyledPanel)
        self.frame_443.setFrameShadow(QFrame.Raised)
        self.verticalLayout_381 = QVBoxLayout(self.frame_443)
        self.verticalLayout_381.setObjectName(u"verticalLayout_381")
        self.faire_un_remboursement = QPushButton(self.frame_443)
        self.faire_un_remboursement.setObjectName(u"faire_un_remboursement")
        self.faire_un_remboursement.setFont(font4)
        self.faire_un_remboursement.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_381.addWidget(self.faire_un_remboursement)


        self.verticalLayout_361.addWidget(self.frame_443)


        self.horizontalLayout_183.addWidget(self.widget_20)

        self.tabWidget_4.addTab(self.tab_rembousement, "")

        self.horizontalLayout_175.addWidget(self.tabWidget_4)


        self.verticalLayout_355.addWidget(self.frame_416)

        self.tabWidget_2.addTab(self.loans_widget, "")
        self.transaction_page = QWidget()
        self.transaction_page.setObjectName(u"transaction_page")
        self.verticalLayout_387 = QVBoxLayout(self.transaction_page)
        self.verticalLayout_387.setObjectName(u"verticalLayout_387")
        self.verticalLayout_387.setContentsMargins(-1, 9, -1, 0)
        self.frame_453 = QFrame(self.transaction_page)
        self.frame_453.setObjectName(u"frame_453")
        self.frame_453.setFrameShape(QFrame.StyledPanel)
        self.frame_453.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_187 = QHBoxLayout(self.frame_453)
        self.horizontalLayout_187.setSpacing(24)
        self.horizontalLayout_187.setObjectName(u"horizontalLayout_187")
        self.horizontalLayout_187.setContentsMargins(0, 0, 0, 0)
        self.frame_465 = QFrame(self.frame_453)
        self.frame_465.setObjectName(u"frame_465")
        self.frame_465.setFrameShape(QFrame.StyledPanel)
        self.frame_465.setFrameShadow(QFrame.Raised)
        self.verticalLayout_397 = QVBoxLayout(self.frame_465)
        self.verticalLayout_397.setSpacing(0)
        self.verticalLayout_397.setObjectName(u"verticalLayout_397")
        self.verticalLayout_397.setContentsMargins(0, 0, 0, 0)
        self.label_185 = QLabel(self.frame_465)
        self.label_185.setObjectName(u"label_185")

        self.verticalLayout_397.addWidget(self.label_185)

        self.combo_transact_identifiant = QComboBox(self.frame_465)
        self.combo_transact_identifiant.setObjectName(u"combo_transact_identifiant")
        self.combo_transact_identifiant.setMinimumSize(QSize(200, 37))
        self.combo_transact_identifiant.setEditable(True)
        self.combo_transact_identifiant.setInsertPolicy(QComboBox.NoInsert)

        self.verticalLayout_397.addWidget(self.combo_transact_identifiant)


        self.horizontalLayout_187.addWidget(self.frame_465)

        self.frame_471 = QFrame(self.frame_453)
        self.frame_471.setObjectName(u"frame_471")
        self.frame_471.setFrameShape(QFrame.StyledPanel)
        self.frame_471.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_192 = QHBoxLayout(self.frame_471)
        self.horizontalLayout_192.setObjectName(u"horizontalLayout_192")
        self.modal_identifiant = QPushButton(self.frame_471)
        self.modal_identifiant.setObjectName(u"modal_identifiant")
        self.modal_identifiant.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_192.addWidget(self.modal_identifiant)


        self.horizontalLayout_187.addWidget(self.frame_471)

        self.frame_464 = QFrame(self.frame_453)
        self.frame_464.setObjectName(u"frame_464")
        self.frame_464.setFrameShape(QFrame.StyledPanel)
        self.frame_464.setFrameShadow(QFrame.Raised)
        self.verticalLayout_398 = QVBoxLayout(self.frame_464)
        self.verticalLayout_398.setSpacing(0)
        self.verticalLayout_398.setObjectName(u"verticalLayout_398")
        self.verticalLayout_398.setContentsMargins(0, 0, 0, 0)
        self.label_186 = QLabel(self.frame_464)
        self.label_186.setObjectName(u"label_186")

        self.verticalLayout_398.addWidget(self.label_186)

        self.combo_transact_description = QComboBox(self.frame_464)
        self.combo_transact_description.setObjectName(u"combo_transact_description")
        self.combo_transact_description.setMinimumSize(QSize(200, 37))

        self.verticalLayout_398.addWidget(self.combo_transact_description)


        self.horizontalLayout_187.addWidget(self.frame_464)

        self.frame_457 = QFrame(self.frame_453)
        self.frame_457.setObjectName(u"frame_457")
        self.frame_457.setFrameShape(QFrame.StyledPanel)
        self.frame_457.setFrameShadow(QFrame.Raised)
        self.verticalLayout_390 = QVBoxLayout(self.frame_457)
        self.verticalLayout_390.setSpacing(0)
        self.verticalLayout_390.setObjectName(u"verticalLayout_390")
        self.verticalLayout_390.setContentsMargins(0, 0, 0, 0)
        self.label_181 = QLabel(self.frame_457)
        self.label_181.setObjectName(u"label_181")

        self.verticalLayout_390.addWidget(self.label_181)

        self.transac_descript = QLineEdit(self.frame_457)
        self.transac_descript.setObjectName(u"transac_descript")

        self.verticalLayout_390.addWidget(self.transac_descript)


        self.horizontalLayout_187.addWidget(self.frame_457)

        self.frame_458 = QFrame(self.frame_453)
        self.frame_458.setObjectName(u"frame_458")
        self.frame_458.setFrameShape(QFrame.StyledPanel)
        self.frame_458.setFrameShadow(QFrame.Raised)
        self.verticalLayout_389 = QVBoxLayout(self.frame_458)
        self.verticalLayout_389.setSpacing(0)
        self.verticalLayout_389.setObjectName(u"verticalLayout_389")
        self.verticalLayout_389.setContentsMargins(0, 0, 0, 0)
        self.label_182 = QLabel(self.frame_458)
        self.label_182.setObjectName(u"label_182")

        self.verticalLayout_389.addWidget(self.label_182)

        self.transac_amount = QLineEdit(self.frame_458)
        self.transac_amount.setObjectName(u"transac_amount")

        self.verticalLayout_389.addWidget(self.transac_amount)


        self.horizontalLayout_187.addWidget(self.frame_458)

        self.transac_id = QLineEdit(self.frame_453)
        self.transac_id.setObjectName(u"transac_id")

        self.horizontalLayout_187.addWidget(self.transac_id)


        self.verticalLayout_387.addWidget(self.frame_453, 0, Qt.AlignTop)

        self.frame_466 = QFrame(self.transaction_page)
        self.frame_466.setObjectName(u"frame_466")
        self.frame_466.setFrameShape(QFrame.StyledPanel)
        self.frame_466.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_190 = QHBoxLayout(self.frame_466)
        self.horizontalLayout_190.setSpacing(40)
        self.horizontalLayout_190.setObjectName(u"horizontalLayout_190")
        self.edit_transact = QPushButton(self.frame_466)
        self.edit_transact.setObjectName(u"edit_transact")
        self.edit_transact.setMinimumSize(QSize(120, 0))
        self.edit_transact.setMaximumSize(QSize(16777215, 33))
        self.edit_transact.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_190.addWidget(self.edit_transact)

        self.delete_transact = QPushButton(self.frame_466)
        self.delete_transact.setObjectName(u"delete_transact")
        self.delete_transact.setMinimumSize(QSize(120, 0))
        self.delete_transact.setMaximumSize(QSize(16777215, 33))
        self.delete_transact.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_190.addWidget(self.delete_transact)

        self.frame_459 = QFrame(self.frame_466)
        self.frame_459.setObjectName(u"frame_459")
        self.frame_459.setFrameShape(QFrame.StyledPanel)
        self.frame_459.setFrameShadow(QFrame.Raised)
        self.verticalLayout_388 = QVBoxLayout(self.frame_459)
        self.verticalLayout_388.setSpacing(0)
        self.verticalLayout_388.setObjectName(u"verticalLayout_388")
        self.verticalLayout_388.setContentsMargins(0, 0, 0, 0)
        self.save_transac = QPushButton(self.frame_459)
        self.save_transac.setObjectName(u"save_transac")
        self.save_transac.setMinimumSize(QSize(120, 0))
        self.save_transac.setMaximumSize(QSize(16777215, 33))
        self.save_transac.setFont(font4)
        self.save_transac.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_388.addWidget(self.save_transac, 0, Qt.AlignBottom)


        self.horizontalLayout_190.addWidget(self.frame_459)


        self.verticalLayout_387.addWidget(self.frame_466, 0, Qt.AlignRight)

        self.frame_456 = QFrame(self.transaction_page)
        self.frame_456.setObjectName(u"frame_456")
        self.frame_456.setMinimumSize(QSize(200, 0))
        self.frame_456.setFrameShape(QFrame.StyledPanel)
        self.frame_456.setFrameShadow(QFrame.Raised)
        self.verticalLayout_391 = QVBoxLayout(self.frame_456)
        self.verticalLayout_391.setSpacing(0)
        self.verticalLayout_391.setObjectName(u"verticalLayout_391")
        self.verticalLayout_391.setContentsMargins(0, 0, 0, 0)
        self.search_transac = QLineEdit(self.frame_456)
        self.search_transac.setObjectName(u"search_transac")
        self.search_transac.setMinimumSize(QSize(300, 37))

        self.verticalLayout_391.addWidget(self.search_transac)


        self.verticalLayout_387.addWidget(self.frame_456, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_454 = QFrame(self.transaction_page)
        self.frame_454.setObjectName(u"frame_454")
        self.frame_454.setFrameShape(QFrame.StyledPanel)
        self.frame_454.setFrameShadow(QFrame.Raised)
        self.verticalLayout_392 = QVBoxLayout(self.frame_454)
        self.verticalLayout_392.setSpacing(0)
        self.verticalLayout_392.setObjectName(u"verticalLayout_392")
        self.verticalLayout_392.setContentsMargins(0, 0, 0, 0)
        self.table_transac = QTableWidget(self.frame_454)
        self.table_transac.setObjectName(u"table_transac")

        self.verticalLayout_392.addWidget(self.table_transac)


        self.verticalLayout_387.addWidget(self.frame_454)

        self.frame_455 = QFrame(self.transaction_page)
        self.frame_455.setObjectName(u"frame_455")
        self.frame_455.setFrameShape(QFrame.StyledPanel)
        self.frame_455.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_188 = QHBoxLayout(self.frame_455)
        self.horizontalLayout_188.setSpacing(56)
        self.horizontalLayout_188.setObjectName(u"horizontalLayout_188")
        self.horizontalLayout_188.setContentsMargins(0, 0, 0, 0)
        self.prev_transac = QPushButton(self.frame_455)
        self.prev_transac.setObjectName(u"prev_transac")
        self.prev_transac.setFont(font4)
        self.prev_transac.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_188.addWidget(self.prev_transac)

        self.next_transac = QPushButton(self.frame_455)
        self.next_transac.setObjectName(u"next_transac")
        self.next_transac.setFont(font4)
        self.next_transac.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_188.addWidget(self.next_transac)


        self.verticalLayout_387.addWidget(self.frame_455, 0, Qt.AlignRight|Qt.AlignBottom)

        self.tabWidget_2.addTab(self.transaction_page, "")
        self.depense = QWidget()
        self.depense.setObjectName(u"depense")
        self.verticalLayout_172 = QVBoxLayout(self.depense)
        self.verticalLayout_172.setObjectName(u"verticalLayout_172")
        self.verticalLayout_172.setContentsMargins(-1, 0, -1, 0)
        self.frame_337 = QFrame(self.depense)
        self.frame_337.setObjectName(u"frame_337")
        self.frame_337.setFrameShape(QFrame.StyledPanel)
        self.frame_337.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_123 = QHBoxLayout(self.frame_337)
        self.horizontalLayout_123.setObjectName(u"horizontalLayout_123")
        self.horizontalLayout_123.setContentsMargins(-1, 9, -1, 0)
        self.frame_339 = QFrame(self.frame_337)
        self.frame_339.setObjectName(u"frame_339")
        self.frame_339.setFrameShape(QFrame.StyledPanel)
        self.frame_339.setFrameShadow(QFrame.Raised)
        self.verticalLayout_173 = QVBoxLayout(self.frame_339)
        self.verticalLayout_173.setSpacing(0)
        self.verticalLayout_173.setObjectName(u"verticalLayout_173")
        self.verticalLayout_173.setContentsMargins(-1, 0, -1, -1)
        self.label_125 = QLabel(self.frame_339)
        self.label_125.setObjectName(u"label_125")

        self.verticalLayout_173.addWidget(self.label_125)

        self.id_depense = QLineEdit(self.frame_339)
        self.id_depense.setObjectName(u"id_depense")
        self.id_depense.setMaximumSize(QSize(16777215, 37))

        self.verticalLayout_173.addWidget(self.id_depense)

        self.description_depense = QLineEdit(self.frame_339)
        self.description_depense.setObjectName(u"description_depense")
        self.description_depense.setMaximumSize(QSize(16777215, 37))

        self.verticalLayout_173.addWidget(self.description_depense)


        self.horizontalLayout_123.addWidget(self.frame_339)

        self.frame_340 = QFrame(self.frame_337)
        self.frame_340.setObjectName(u"frame_340")
        self.frame_340.setFrameShape(QFrame.StyledPanel)
        self.frame_340.setFrameShadow(QFrame.Raised)
        self.verticalLayout_298 = QVBoxLayout(self.frame_340)
        self.verticalLayout_298.setSpacing(0)
        self.verticalLayout_298.setObjectName(u"verticalLayout_298")
        self.verticalLayout_298.setContentsMargins(-1, 0, -1, -1)
        self.label_126 = QLabel(self.frame_340)
        self.label_126.setObjectName(u"label_126")

        self.verticalLayout_298.addWidget(self.label_126)

        self.prix_depense = QLineEdit(self.frame_340)
        self.prix_depense.setObjectName(u"prix_depense")
        self.prix_depense.setMaximumSize(QSize(16777215, 37))

        self.verticalLayout_298.addWidget(self.prix_depense)


        self.horizontalLayout_123.addWidget(self.frame_340)

        self.frame_341 = QFrame(self.frame_337)
        self.frame_341.setObjectName(u"frame_341")
        self.frame_341.setFrameShape(QFrame.StyledPanel)
        self.frame_341.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_132 = QHBoxLayout(self.frame_341)
        self.horizontalLayout_132.setSpacing(15)
        self.horizontalLayout_132.setObjectName(u"horizontalLayout_132")
        self.horizontalLayout_132.setContentsMargins(-1, 0, -1, -1)
        self.enregistrer_depense = QPushButton(self.frame_341)
        self.enregistrer_depense.setObjectName(u"enregistrer_depense")
        self.enregistrer_depense.setMinimumSize(QSize(130, 0))
        self.enregistrer_depense.setFont(font4)
        self.enregistrer_depense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_132.addWidget(self.enregistrer_depense)

        self.delete_depense = QPushButton(self.frame_341)
        self.delete_depense.setObjectName(u"delete_depense")
        self.delete_depense.setMinimumSize(QSize(100, 33))
        self.delete_depense.setMaximumSize(QSize(16777215, 33))
        self.delete_depense.setFont(font4)
        self.delete_depense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_132.addWidget(self.delete_depense)


        self.horizontalLayout_123.addWidget(self.frame_341, 0, Qt.AlignBottom)


        self.verticalLayout_172.addWidget(self.frame_337, 0, Qt.AlignTop)

        self.frame_338 = QFrame(self.depense)
        self.frame_338.setObjectName(u"frame_338")
        self.frame_338.setFrameShape(QFrame.StyledPanel)
        self.frame_338.setFrameShadow(QFrame.Raised)
        self.verticalLayout_300 = QVBoxLayout(self.frame_338)
        self.verticalLayout_300.setObjectName(u"verticalLayout_300")
        self.verticalLayout_300.setContentsMargins(-1, 0, -1, 0)
        self.frame_372 = QFrame(self.frame_338)
        self.frame_372.setObjectName(u"frame_372")
        self.frame_372.setFrameShape(QFrame.StyledPanel)
        self.frame_372.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_137 = QHBoxLayout(self.frame_372)
        self.horizontalLayout_137.setSpacing(0)
        self.horizontalLayout_137.setObjectName(u"horizontalLayout_137")
        self.horizontalLayout_137.setContentsMargins(0, 0, -1, 0)
        self.search_depense = QLineEdit(self.frame_372)
        self.search_depense.setObjectName(u"search_depense")
        self.search_depense.setMinimumSize(QSize(350, 37))
        self.search_depense.setMaximumSize(QSize(300, 37))
        self.search_depense.setFont(font2)

        self.horizontalLayout_137.addWidget(self.search_depense)


        self.verticalLayout_300.addWidget(self.frame_372, 0, Qt.AlignRight)

        self.table_depense = QTableWidget(self.frame_338)
        self.table_depense.setObjectName(u"table_depense")
        self.table_depense.setSortingEnabled(True)

        self.verticalLayout_300.addWidget(self.table_depense)

        self.frame_342 = QFrame(self.frame_338)
        self.frame_342.setObjectName(u"frame_342")
        self.frame_342.setFrameShape(QFrame.StyledPanel)
        self.frame_342.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_125 = QHBoxLayout(self.frame_342)
        self.horizontalLayout_125.setSpacing(25)
        self.horizontalLayout_125.setObjectName(u"horizontalLayout_125")
        self.horizontalLayout_125.setContentsMargins(-1, 0, -1, 0)
        self.prev_depense = QPushButton(self.frame_342)
        self.prev_depense.setObjectName(u"prev_depense")
        self.prev_depense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_125.addWidget(self.prev_depense)

        self.next_depense = QPushButton(self.frame_342)
        self.next_depense.setObjectName(u"next_depense")
        self.next_depense.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_125.addWidget(self.next_depense)


        self.verticalLayout_300.addWidget(self.frame_342, 0, Qt.AlignRight)


        self.verticalLayout_172.addWidget(self.frame_338)

        self.tabWidget_2.addTab(self.depense, "")

        self.verticalLayout_255.addWidget(self.tabWidget_2)


        self.verticalLayout_254.addWidget(self.frame_273)

        self.stackedWidget.addWidget(self.vente_page)
        self.profile = QWidget()
        self.profile.setObjectName(u"profile")
        self.profile.setMinimumSize(QSize(521, 279))
        self.profile.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_60 = QVBoxLayout(self.profile)
        self.verticalLayout_60.setObjectName(u"verticalLayout_60")
        self.verticalLayout_60.setContentsMargins(-1, 0, -1, 0)
        self.frame_90 = QFrame(self.profile)
        self.frame_90.setObjectName(u"frame_90")
        self.frame_90.setFrameShape(QFrame.StyledPanel)
        self.frame_90.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame_90)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, -1, 0)
        self.frame_106 = QFrame(self.frame_90)
        self.frame_106.setObjectName(u"frame_106")
        self.frame_106.setFrameShape(QFrame.StyledPanel)
        self.frame_106.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_106)
        self.horizontalLayout_2.setSpacing(30)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.btn_permission_page = QPushButton(self.frame_106)
        self.btn_permission_page.setObjectName(u"btn_permission_page")
        self.btn_permission_page.setFont(font4)
        self.btn_permission_page.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_permission_page.setCheckable(True)
        self.btn_permission_page.setAutoExclusive(True)

        self.horizontalLayout_2.addWidget(self.btn_permission_page)

        self.btn_role_page = QPushButton(self.frame_106)
        self.btn_role_page.setObjectName(u"btn_role_page")
        self.btn_role_page.setFont(font4)
        self.btn_role_page.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_role_page.setCheckable(True)
        self.btn_role_page.setAutoExclusive(True)

        self.horizontalLayout_2.addWidget(self.btn_role_page)


        self.verticalLayout_5.addWidget(self.frame_106, 0, Qt.AlignLeft|Qt.AlignTop)


        self.verticalLayout_60.addWidget(self.frame_90, 0, Qt.AlignTop)

        self.frame_235 = QFrame(self.profile)
        self.frame_235.setObjectName(u"frame_235")
        self.frame_235.setFrameShape(QFrame.StyledPanel)
        self.frame_235.setFrameShadow(QFrame.Raised)
        self.verticalLayout_211 = QVBoxLayout(self.frame_235)
        self.verticalLayout_211.setSpacing(0)
        self.verticalLayout_211.setObjectName(u"verticalLayout_211")
        self.verticalLayout_211.setContentsMargins(0, 0, 0, 0)
        self.widget_13 = QWidget(self.frame_235)
        self.widget_13.setObjectName(u"widget_13")
        self.verticalLayout_221 = QVBoxLayout(self.widget_13)
        self.verticalLayout_221.setSpacing(0)
        self.verticalLayout_221.setObjectName(u"verticalLayout_221")
        self.verticalLayout_221.setContentsMargins(0, 9, 0, 9)
        self.frame_239 = QFrame(self.widget_13)
        self.frame_239.setObjectName(u"frame_239")
        self.frame_239.setFrameShape(QFrame.StyledPanel)
        self.frame_239.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_91 = QHBoxLayout(self.frame_239)
        self.horizontalLayout_91.setSpacing(6)
        self.horizontalLayout_91.setObjectName(u"horizontalLayout_91")
        self.horizontalLayout_91.setContentsMargins(-1, -1, -1, 0)
        self.frame_246 = QFrame(self.frame_239)
        self.frame_246.setObjectName(u"frame_246")
        self.frame_246.setFrameShape(QFrame.StyledPanel)
        self.frame_246.setFrameShadow(QFrame.Raised)
        self.verticalLayout_228 = QVBoxLayout(self.frame_246)
        self.verticalLayout_228.setObjectName(u"verticalLayout_228")
        self.label_77 = QLabel(self.frame_246)
        self.label_77.setObjectName(u"label_77")

        self.verticalLayout_228.addWidget(self.label_77)

        self.input_nom = QLineEdit(self.frame_246)
        self.input_nom.setObjectName(u"input_nom")
        self.input_nom.setMinimumSize(QSize(0, 37))
        self.input_nom.setMaximumSize(QSize(16777215, 37))
        self.input_nom.setFont(font2)

        self.verticalLayout_228.addWidget(self.input_nom)


        self.horizontalLayout_91.addWidget(self.frame_246)

        self.frame_247 = QFrame(self.frame_239)
        self.frame_247.setObjectName(u"frame_247")
        self.frame_247.setFrameShape(QFrame.StyledPanel)
        self.frame_247.setFrameShadow(QFrame.Raised)
        self.verticalLayout_227 = QVBoxLayout(self.frame_247)
        self.verticalLayout_227.setObjectName(u"verticalLayout_227")
        self.label_78 = QLabel(self.frame_247)
        self.label_78.setObjectName(u"label_78")

        self.verticalLayout_227.addWidget(self.label_78)

        self.input_email = QLineEdit(self.frame_247)
        self.input_email.setObjectName(u"input_email")
        self.input_email.setMinimumSize(QSize(0, 37))
        self.input_email.setMaximumSize(QSize(16777215, 37))
        self.input_email.setFont(font2)

        self.verticalLayout_227.addWidget(self.input_email)


        self.horizontalLayout_91.addWidget(self.frame_247)

        self.frame_248 = QFrame(self.frame_239)
        self.frame_248.setObjectName(u"frame_248")
        self.frame_248.setFrameShape(QFrame.StyledPanel)
        self.frame_248.setFrameShadow(QFrame.Raised)
        self.verticalLayout_226 = QVBoxLayout(self.frame_248)
        self.verticalLayout_226.setObjectName(u"verticalLayout_226")
        self.label_79 = QLabel(self.frame_248)
        self.label_79.setObjectName(u"label_79")

        self.verticalLayout_226.addWidget(self.label_79)

        self.input_adresse = QLineEdit(self.frame_248)
        self.input_adresse.setObjectName(u"input_adresse")
        self.input_adresse.setMinimumSize(QSize(0, 37))
        self.input_adresse.setMaximumSize(QSize(16777215, 37))
        self.input_adresse.setFont(font2)

        self.verticalLayout_226.addWidget(self.input_adresse)


        self.horizontalLayout_91.addWidget(self.frame_248)


        self.verticalLayout_221.addWidget(self.frame_239)

        self.frame_244 = QFrame(self.widget_13)
        self.frame_244.setObjectName(u"frame_244")
        self.frame_244.setFrameShape(QFrame.StyledPanel)
        self.frame_244.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_92 = QHBoxLayout(self.frame_244)
        self.horizontalLayout_92.setObjectName(u"horizontalLayout_92")
        self.horizontalLayout_92.setContentsMargins(-1, 0, -1, 0)
        self.frame_249 = QFrame(self.frame_244)
        self.frame_249.setObjectName(u"frame_249")
        self.frame_249.setFrameShape(QFrame.StyledPanel)
        self.frame_249.setFrameShadow(QFrame.Raised)
        self.verticalLayout_223 = QVBoxLayout(self.frame_249)
        self.verticalLayout_223.setObjectName(u"verticalLayout_223")
        self.verticalLayout_223.setContentsMargins(-1, 0, -1, 9)
        self.label_80 = QLabel(self.frame_249)
        self.label_80.setObjectName(u"label_80")

        self.verticalLayout_223.addWidget(self.label_80)

        self.input_ligne1 = QLineEdit(self.frame_249)
        self.input_ligne1.setObjectName(u"input_ligne1")
        self.input_ligne1.setMinimumSize(QSize(0, 37))
        self.input_ligne1.setMaximumSize(QSize(16777215, 37))
        self.input_ligne1.setFont(font2)

        self.verticalLayout_223.addWidget(self.input_ligne1)


        self.horizontalLayout_92.addWidget(self.frame_249)

        self.frame_250 = QFrame(self.frame_244)
        self.frame_250.setObjectName(u"frame_250")
        self.frame_250.setFrameShape(QFrame.StyledPanel)
        self.frame_250.setFrameShadow(QFrame.Raised)
        self.verticalLayout_224 = QVBoxLayout(self.frame_250)
        self.verticalLayout_224.setSpacing(0)
        self.verticalLayout_224.setObjectName(u"verticalLayout_224")
        self.verticalLayout_224.setContentsMargins(-1, 0, -1, -1)
        self.label_81 = QLabel(self.frame_250)
        self.label_81.setObjectName(u"label_81")

        self.verticalLayout_224.addWidget(self.label_81)

        self.input_ligne2 = QLineEdit(self.frame_250)
        self.input_ligne2.setObjectName(u"input_ligne2")
        self.input_ligne2.setMinimumSize(QSize(0, 37))
        self.input_ligne2.setMaximumSize(QSize(16777215, 37))
        self.input_ligne2.setFont(font2)

        self.verticalLayout_224.addWidget(self.input_ligne2)


        self.horizontalLayout_92.addWidget(self.frame_250)

        self.frame_251 = QFrame(self.frame_244)
        self.frame_251.setObjectName(u"frame_251")
        self.frame_251.setFrameShape(QFrame.StyledPanel)
        self.frame_251.setFrameShadow(QFrame.Raised)
        self.verticalLayout_225 = QVBoxLayout(self.frame_251)
        self.verticalLayout_225.setSpacing(0)
        self.verticalLayout_225.setObjectName(u"verticalLayout_225")
        self.verticalLayout_225.setContentsMargins(-1, 0, -1, -1)
        self.label_82 = QLabel(self.frame_251)
        self.label_82.setObjectName(u"label_82")

        self.verticalLayout_225.addWidget(self.label_82)

        self.frame_252 = QFrame(self.frame_251)
        self.frame_252.setObjectName(u"frame_252")
        self.frame_252.setFrameShape(QFrame.StyledPanel)
        self.frame_252.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_93 = QHBoxLayout(self.frame_252)
        self.horizontalLayout_93.setObjectName(u"horizontalLayout_93")
        self.horizontalLayout_93.setContentsMargins(0, 0, 0, 0)
        self.show_image = QLabel(self.frame_252)
        self.show_image.setObjectName(u"show_image")

        self.horizontalLayout_93.addWidget(self.show_image)

        self.choise_profile_image = QPushButton(self.frame_252)
        self.choise_profile_image.setObjectName(u"choise_profile_image")
        self.choise_profile_image.setFont(font4)
        self.choise_profile_image.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.choise_profile_image.setCheckable(True)
        self.choise_profile_image.setAutoExclusive(True)

        self.horizontalLayout_93.addWidget(self.choise_profile_image)


        self.verticalLayout_225.addWidget(self.frame_252)

        self.input_image = QLineEdit(self.frame_251)
        self.input_image.setObjectName(u"input_image")
        self.input_image.setMinimumSize(QSize(0, 37))
        self.input_image.setMaximumSize(QSize(16777215, 37))
        self.input_image.setFont(font2)

        self.verticalLayout_225.addWidget(self.input_image)


        self.horizontalLayout_92.addWidget(self.frame_251)


        self.verticalLayout_221.addWidget(self.frame_244)

        self.frame_245 = QFrame(self.widget_13)
        self.frame_245.setObjectName(u"frame_245")
        self.frame_245.setFrameShape(QFrame.StyledPanel)
        self.frame_245.setFrameShadow(QFrame.Raised)
        self.verticalLayout_222 = QVBoxLayout(self.frame_245)
        self.verticalLayout_222.setSpacing(0)
        self.verticalLayout_222.setObjectName(u"verticalLayout_222")
        self.verticalLayout_222.setContentsMargins(0, 0, 25, 0)
        self.valider_profile = QPushButton(self.frame_245)
        self.valider_profile.setObjectName(u"valider_profile")
        self.valider_profile.setMinimumSize(QSize(120, 0))
        self.valider_profile.setFont(font4)
        self.valider_profile.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_222.addWidget(self.valider_profile)


        self.verticalLayout_221.addWidget(self.frame_245, 0, Qt.AlignRight)


        self.verticalLayout_211.addWidget(self.widget_13)


        self.verticalLayout_60.addWidget(self.frame_235, 0, Qt.AlignTop)

        self.scrollArea_9 = QScrollArea(self.profile)
        self.scrollArea_9.setObjectName(u"scrollArea_9")
        self.scrollArea_9.setWidgetResizable(True)
        self.scrollAreaWidgetContents_12 = QWidget()
        self.scrollAreaWidgetContents_12.setObjectName(u"scrollAreaWidgetContents_12")
        self.scrollAreaWidgetContents_12.setGeometry(QRect(0, 0, 720, 730))
        self.verticalLayout_349 = QVBoxLayout(self.scrollAreaWidgetContents_12)
        self.verticalLayout_349.setObjectName(u"verticalLayout_349")
        self.frame_394 = QFrame(self.scrollAreaWidgetContents_12)
        self.frame_394.setObjectName(u"frame_394")
        self.frame_394.setMaximumSize(QSize(16777215, 16777215))
        self.frame_394.setFrameShape(QFrame.StyledPanel)
        self.frame_394.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_146 = QHBoxLayout(self.frame_394)
        self.horizontalLayout_146.setSpacing(20)
        self.horizontalLayout_146.setObjectName(u"horizontalLayout_146")
        self.horizontalLayout_146.setContentsMargins(-1, -1, -1, 20)
        self.frame_395 = QFrame(self.frame_394)
        self.frame_395.setObjectName(u"frame_395")
        self.frame_395.setMinimumSize(QSize(321, 290))
        self.frame_395.setFrameShape(QFrame.StyledPanel)
        self.frame_395.setFrameShadow(QFrame.Raised)
        self.verticalLayout_340 = QVBoxLayout(self.frame_395)
        self.verticalLayout_340.setObjectName(u"verticalLayout_340")
        self.template_badge_1 = QPushButton(self.frame_395)
        self.template_badge_1.setObjectName(u"template_badge_1")
        self.template_badge_1.setMinimumSize(QSize(150, 0))
        self.template_badge_1.setFont(font4)

        self.verticalLayout_340.addWidget(self.template_badge_1, 0, Qt.AlignRight)

        self.input_image_temlate_1 = QLineEdit(self.frame_395)
        self.input_image_temlate_1.setObjectName(u"input_image_temlate_1")

        self.verticalLayout_340.addWidget(self.input_image_temlate_1)

        self.label_153 = QLabel(self.frame_395)
        self.label_153.setObjectName(u"label_153")
        self.label_153.setMinimumSize(QSize(435, 279))
        self.label_153.setMaximumSize(QSize(16777215, 16777215))
        self.label_153.setScaledContents(True)

        self.verticalLayout_340.addWidget(self.label_153)


        self.horizontalLayout_146.addWidget(self.frame_395, 0, Qt.AlignLeft)

        self.frame_404 = QFrame(self.frame_394)
        self.frame_404.setObjectName(u"frame_404")
        self.frame_404.setMinimumSize(QSize(321, 290))
        self.frame_404.setFrameShape(QFrame.StyledPanel)
        self.frame_404.setFrameShadow(QFrame.Raised)
        self.verticalLayout_342 = QVBoxLayout(self.frame_404)
        self.verticalLayout_342.setObjectName(u"verticalLayout_342")
        self.template_badge_2 = QPushButton(self.frame_404)
        self.template_badge_2.setObjectName(u"template_badge_2")
        self.template_badge_2.setMinimumSize(QSize(150, 0))
        self.template_badge_2.setFont(font4)

        self.verticalLayout_342.addWidget(self.template_badge_2, 0, Qt.AlignRight)

        self.input_image_temlate_2 = QLineEdit(self.frame_404)
        self.input_image_temlate_2.setObjectName(u"input_image_temlate_2")

        self.verticalLayout_342.addWidget(self.input_image_temlate_2)

        self.label_154 = QLabel(self.frame_404)
        self.label_154.setObjectName(u"label_154")
        self.label_154.setMinimumSize(QSize(435, 279))
        self.label_154.setScaledContents(True)

        self.verticalLayout_342.addWidget(self.label_154)


        self.horizontalLayout_146.addWidget(self.frame_404, 0, Qt.AlignRight)


        self.verticalLayout_349.addWidget(self.frame_394)

        self.frame_393 = QFrame(self.scrollAreaWidgetContents_12)
        self.frame_393.setObjectName(u"frame_393")
        self.frame_393.setFrameShape(QFrame.StyledPanel)
        self.frame_393.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_149 = QHBoxLayout(self.frame_393)
        self.horizontalLayout_149.setObjectName(u"horizontalLayout_149")
        self.frame_405 = QFrame(self.frame_393)
        self.frame_405.setObjectName(u"frame_405")
        self.frame_405.setFrameShape(QFrame.StyledPanel)
        self.frame_405.setFrameShadow(QFrame.Raised)
        self.verticalLayout_351 = QVBoxLayout(self.frame_405)
        self.verticalLayout_351.setObjectName(u"verticalLayout_351")
        self.template_certificat = QPushButton(self.frame_405)
        self.template_certificat.setObjectName(u"template_certificat")
        self.template_certificat.setMinimumSize(QSize(150, 0))
        self.template_certificat.setFont(font4)

        self.verticalLayout_351.addWidget(self.template_certificat, 0, Qt.AlignRight)

        self.input_image_template_certificat = QLineEdit(self.frame_405)
        self.input_image_template_certificat.setObjectName(u"input_image_template_certificat")

        self.verticalLayout_351.addWidget(self.input_image_template_certificat)

        self.label_155 = QLabel(self.frame_405)
        self.label_155.setObjectName(u"label_155")
        self.label_155.setMinimumSize(QSize(321, 279))
        self.label_155.setMaximumSize(QSize(16777215, 16777215))
        self.label_155.setScaledContents(True)

        self.verticalLayout_351.addWidget(self.label_155)


        self.horizontalLayout_149.addWidget(self.frame_405)

        self.frame_406 = QFrame(self.frame_393)
        self.frame_406.setObjectName(u"frame_406")
        self.frame_406.setFrameShape(QFrame.StyledPanel)
        self.frame_406.setFrameShadow(QFrame.Raised)
        self.verticalLayout_350 = QVBoxLayout(self.frame_406)
        self.verticalLayout_350.setObjectName(u"verticalLayout_350")
        self.template_diplome = QPushButton(self.frame_406)
        self.template_diplome.setObjectName(u"template_diplome")
        self.template_diplome.setMinimumSize(QSize(150, 0))
        self.template_diplome.setFont(font4)

        self.verticalLayout_350.addWidget(self.template_diplome, 0, Qt.AlignRight)

        self.input_image_temlate_diplome = QLineEdit(self.frame_406)
        self.input_image_temlate_diplome.setObjectName(u"input_image_temlate_diplome")

        self.verticalLayout_350.addWidget(self.input_image_temlate_diplome)

        self.label_156 = QLabel(self.frame_406)
        self.label_156.setObjectName(u"label_156")
        self.label_156.setMinimumSize(QSize(321, 279))
        self.label_156.setMaximumSize(QSize(16777215, 16777215))
        self.label_156.setScaledContents(True)

        self.verticalLayout_350.addWidget(self.label_156)


        self.horizontalLayout_149.addWidget(self.frame_406)


        self.verticalLayout_349.addWidget(self.frame_393)

        self.scrollArea_9.setWidget(self.scrollAreaWidgetContents_12)

        self.verticalLayout_60.addWidget(self.scrollArea_9)

        self.stackedWidget.addWidget(self.profile)
        self.permission_page = QWidget()
        self.permission_page.setObjectName(u"permission_page")
        self.verticalLayout_59 = QVBoxLayout(self.permission_page)
        self.verticalLayout_59.setObjectName(u"verticalLayout_59")
        self.verticalLayout_59.setContentsMargins(-1, 0, -1, -1)
        self.frame_237 = QFrame(self.permission_page)
        self.frame_237.setObjectName(u"frame_237")
        self.frame_237.setFrameShape(QFrame.Box)
        self.frame_237.setFrameShadow(QFrame.Sunken)
        self.verticalLayout_213 = QVBoxLayout(self.frame_237)
        self.verticalLayout_213.setObjectName(u"verticalLayout_213")
        self.verticalLayout_213.setContentsMargins(0, 0, 0, -1)
        self.frame_261 = QFrame(self.frame_237)
        self.frame_261.setObjectName(u"frame_261")
        self.frame_261.setFrameShape(QFrame.StyledPanel)
        self.frame_261.setFrameShadow(QFrame.Raised)
        self.verticalLayout_235 = QVBoxLayout(self.frame_261)
        self.verticalLayout_235.setObjectName(u"verticalLayout_235")
        self.verticalLayout_235.setContentsMargins(9, 0, -1, 0)
        self.label_86 = QLabel(self.frame_261)
        self.label_86.setObjectName(u"label_86")

        self.verticalLayout_235.addWidget(self.label_86)


        self.verticalLayout_213.addWidget(self.frame_261)

        self.frame_253 = QFrame(self.frame_237)
        self.frame_253.setObjectName(u"frame_253")
        self.frame_253.setFrameShape(QFrame.StyledPanel)
        self.frame_253.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_94 = QHBoxLayout(self.frame_253)
        self.horizontalLayout_94.setSpacing(10)
        self.horizontalLayout_94.setObjectName(u"horizontalLayout_94")
        self.horizontalLayout_94.setContentsMargins(-1, 0, -1, -1)
        self.input_id_user_for_permission = QLineEdit(self.frame_253)
        self.input_id_user_for_permission.setObjectName(u"input_id_user_for_permission")

        self.horizontalLayout_94.addWidget(self.input_id_user_for_permission)

        self.frame_255 = QFrame(self.frame_253)
        self.frame_255.setObjectName(u"frame_255")
        self.frame_255.setFrameShape(QFrame.StyledPanel)
        self.frame_255.setFrameShadow(QFrame.Raised)
        self.verticalLayout_229 = QVBoxLayout(self.frame_255)
        self.verticalLayout_229.setSpacing(0)
        self.verticalLayout_229.setObjectName(u"verticalLayout_229")
        self.verticalLayout_229.setContentsMargins(-1, 0, -1, 0)
        self.label_83 = QLabel(self.frame_255)
        self.label_83.setObjectName(u"label_83")

        self.verticalLayout_229.addWidget(self.label_83)

        self.combo_roles = QComboBox(self.frame_255)
        self.combo_roles.setObjectName(u"combo_roles")
        self.combo_roles.setMinimumSize(QSize(400, 37))
        self.combo_roles.setMaximumSize(QSize(16777215, 37))
        self.combo_roles.setFont(font2)

        self.verticalLayout_229.addWidget(self.combo_roles)


        self.horizontalLayout_94.addWidget(self.frame_255)

        self.frame_270 = QFrame(self.frame_253)
        self.frame_270.setObjectName(u"frame_270")
        self.frame_270.setFrameShape(QFrame.StyledPanel)
        self.frame_270.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_96 = QHBoxLayout(self.frame_270)
        self.horizontalLayout_96.setSpacing(10)
        self.horizontalLayout_96.setObjectName(u"horizontalLayout_96")
        self.horizontalLayout_96.setContentsMargins(0, 0, 0, 0)
        self.frame_256 = QFrame(self.frame_270)
        self.frame_256.setObjectName(u"frame_256")
        self.frame_256.setFont(font4)
        self.frame_256.setFrameShape(QFrame.StyledPanel)
        self.frame_256.setFrameShadow(QFrame.Raised)
        self.verticalLayout_230 = QVBoxLayout(self.frame_256)
        self.verticalLayout_230.setObjectName(u"verticalLayout_230")
        self.verticalLayout_230.setContentsMargins(-1, 0, 0, 0)
        self.label_84 = QLabel(self.frame_256)
        self.label_84.setObjectName(u"label_84")

        self.verticalLayout_230.addWidget(self.label_84)

        self.recherche_un_user = QLineEdit(self.frame_256)
        self.recherche_un_user.setObjectName(u"recherche_un_user")
        self.recherche_un_user.setMinimumSize(QSize(300, 37))
        self.recherche_un_user.setMaximumSize(QSize(400, 37))
        self.recherche_un_user.setFont(font2)

        self.verticalLayout_230.addWidget(self.recherche_un_user)


        self.horizontalLayout_96.addWidget(self.frame_256)

        self.frame_269 = QFrame(self.frame_270)
        self.frame_269.setObjectName(u"frame_269")
        self.frame_269.setFont(font4)
        self.frame_269.setFrameShape(QFrame.StyledPanel)
        self.frame_269.setFrameShadow(QFrame.Raised)
        self.verticalLayout_252 = QVBoxLayout(self.frame_269)
        self.verticalLayout_252.setObjectName(u"verticalLayout_252")
        self.recherche_user_permission = QPushButton(self.frame_269)
        self.recherche_user_permission.setObjectName(u"recherche_user_permission")
        self.recherche_user_permission.setFont(font4)

        self.verticalLayout_252.addWidget(self.recherche_user_permission)


        self.horizontalLayout_96.addWidget(self.frame_269, 0, Qt.AlignBottom)


        self.horizontalLayout_94.addWidget(self.frame_270, 0, Qt.AlignRight)


        self.verticalLayout_213.addWidget(self.frame_253, 0, Qt.AlignHCenter|Qt.AlignTop)

        self.table_permission = QTableWidget(self.frame_237)
        self.table_permission.setObjectName(u"table_permission")
        self.table_permission.setMinimumSize(QSize(500, 0))

        self.verticalLayout_213.addWidget(self.table_permission, 0, Qt.AlignHCenter)

        self.widget_15 = QWidget(self.frame_237)
        self.widget_15.setObjectName(u"widget_15")
        self.widget_15.setFont(font4)

        self.verticalLayout_213.addWidget(self.widget_15)

        self.frame_254 = QFrame(self.frame_237)
        self.frame_254.setObjectName(u"frame_254")
        self.frame_254.setFrameShape(QFrame.StyledPanel)
        self.frame_254.setFrameShadow(QFrame.Raised)
        self.verticalLayout_231 = QVBoxLayout(self.frame_254)
        self.verticalLayout_231.setObjectName(u"verticalLayout_231")
        self.btn_modifier_permission = QPushButton(self.frame_254)
        self.btn_modifier_permission.setObjectName(u"btn_modifier_permission")
        self.btn_modifier_permission.setMinimumSize(QSize(150, 33))
        self.btn_modifier_permission.setFont(font4)
        self.btn_modifier_permission.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_231.addWidget(self.btn_modifier_permission)


        self.verticalLayout_213.addWidget(self.frame_254, 0, Qt.AlignRight)


        self.verticalLayout_59.addWidget(self.frame_237, 0, Qt.AlignTop)

        self.stackedWidget.addWidget(self.permission_page)
        self.role_page = QWidget()
        self.role_page.setObjectName(u"role_page")
        self.verticalLayout_6 = QVBoxLayout(self.role_page)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(-1, 0, -1, -1)
        self.frame_236 = QFrame(self.role_page)
        self.frame_236.setObjectName(u"frame_236")
        self.frame_236.setFrameShape(QFrame.NoFrame)
        self.frame_236.setFrameShadow(QFrame.Plain)
        self.verticalLayout_212 = QVBoxLayout(self.frame_236)
        self.verticalLayout_212.setObjectName(u"verticalLayout_212")
        self.verticalLayout_212.setContentsMargins(0, -1, 0, -1)
        self.frame_260 = QFrame(self.frame_236)
        self.frame_260.setObjectName(u"frame_260")
        self.frame_260.setFrameShape(QFrame.StyledPanel)
        self.frame_260.setFrameShadow(QFrame.Raised)
        self.verticalLayout_234 = QVBoxLayout(self.frame_260)
        self.verticalLayout_234.setObjectName(u"verticalLayout_234")
        self.verticalLayout_234.setContentsMargins(9, 0, 0, 0)
        self.label_85 = QLabel(self.frame_260)
        self.label_85.setObjectName(u"label_85")
        self.label_85.setFont(font2)

        self.verticalLayout_234.addWidget(self.label_85)


        self.verticalLayout_212.addWidget(self.frame_260)

        self.frame_257 = QFrame(self.frame_236)
        self.frame_257.setObjectName(u"frame_257")
        self.frame_257.setFrameShape(QFrame.StyledPanel)
        self.frame_257.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_95 = QHBoxLayout(self.frame_257)
        self.horizontalLayout_95.setObjectName(u"horizontalLayout_95")
        self.horizontalLayout_95.setContentsMargins(-1, 0, -1, 0)
        self.input_id_user_for_role = QLineEdit(self.frame_257)
        self.input_id_user_for_role.setObjectName(u"input_id_user_for_role")
        self.input_id_user_for_role.setMinimumSize(QSize(0, 37))
        self.input_id_user_for_role.setMaximumSize(QSize(16777215, 37))

        self.horizontalLayout_95.addWidget(self.input_id_user_for_role)

        self.frame_259 = QFrame(self.frame_257)
        self.frame_259.setObjectName(u"frame_259")
        self.frame_259.setFrameShape(QFrame.StyledPanel)
        self.frame_259.setFrameShadow(QFrame.Raised)
        self.verticalLayout_232 = QVBoxLayout(self.frame_259)
        self.verticalLayout_232.setObjectName(u"verticalLayout_232")
        self.verticalLayout_232.setContentsMargins(-1, 0, -1, -1)
        self.label_87 = QLabel(self.frame_259)
        self.label_87.setObjectName(u"label_87")

        self.verticalLayout_232.addWidget(self.label_87)

        self.rechercher_pour_role = QLineEdit(self.frame_259)
        self.rechercher_pour_role.setObjectName(u"rechercher_pour_role")
        self.rechercher_pour_role.setMinimumSize(QSize(450, 37))
        self.rechercher_pour_role.setMaximumSize(QSize(16777215, 37))
        self.rechercher_pour_role.setFont(font2)

        self.verticalLayout_232.addWidget(self.rechercher_pour_role)


        self.horizontalLayout_95.addWidget(self.frame_259)

        self.frame_268 = QFrame(self.frame_257)
        self.frame_268.setObjectName(u"frame_268")
        self.frame_268.setFrameShape(QFrame.StyledPanel)
        self.frame_268.setFrameShadow(QFrame.Raised)
        self.verticalLayout_251 = QVBoxLayout(self.frame_268)
        self.verticalLayout_251.setObjectName(u"verticalLayout_251")
        self.recherche_user_role = QPushButton(self.frame_268)
        self.recherche_user_role.setObjectName(u"recherche_user_role")
        self.recherche_user_role.setFont(font4)
        self.recherche_user_role.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_251.addWidget(self.recherche_user_role)


        self.horizontalLayout_95.addWidget(self.frame_268, 0, Qt.AlignBottom)


        self.verticalLayout_212.addWidget(self.frame_257, 0, Qt.AlignLeft)

        self.table_roles = QTableWidget(self.frame_236)
        self.table_roles.setObjectName(u"table_roles")
        self.table_roles.setMinimumSize(QSize(500, 0))
        self.table_roles.setSortingEnabled(True)

        self.verticalLayout_212.addWidget(self.table_roles, 0, Qt.AlignHCenter)

        self.widget_14 = QWidget(self.frame_236)
        self.widget_14.setObjectName(u"widget_14")
        self.widget_14.setFont(font4)
        self.scrollArea_11 = QScrollArea(self.widget_14)
        self.scrollArea_11.setObjectName(u"scrollArea_11")
        self.scrollArea_11.setGeometry(QRect(390, 0, 120, 80))
        self.scrollArea_11.setWidgetResizable(True)
        self.scrollAreaWidgetContents_16 = QWidget()
        self.scrollAreaWidgetContents_16.setObjectName(u"scrollAreaWidgetContents_16")
        self.scrollAreaWidgetContents_16.setGeometry(QRect(0, 0, 120, 80))
        self.scrollArea_11.setWidget(self.scrollAreaWidgetContents_16)

        self.verticalLayout_212.addWidget(self.widget_14)

        self.frame_258 = QFrame(self.frame_236)
        self.frame_258.setObjectName(u"frame_258")
        self.frame_258.setFrameShape(QFrame.StyledPanel)
        self.frame_258.setFrameShadow(QFrame.Raised)
        self.verticalLayout_233 = QVBoxLayout(self.frame_258)
        self.verticalLayout_233.setObjectName(u"verticalLayout_233")
        self.btn_modifier_roles = QPushButton(self.frame_258)
        self.btn_modifier_roles.setObjectName(u"btn_modifier_roles")
        self.btn_modifier_roles.setMinimumSize(QSize(120, 0))
        self.btn_modifier_roles.setFont(font4)
        self.btn_modifier_roles.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_233.addWidget(self.btn_modifier_roles)


        self.verticalLayout_212.addWidget(self.frame_258, 0, Qt.AlignRight)


        self.verticalLayout_6.addWidget(self.frame_236, 0, Qt.AlignTop)

        self.stackedWidget.addWidget(self.role_page)
        self.rapport_page = QWidget()
        self.rapport_page.setObjectName(u"rapport_page")
        self.horizontalLayout_50 = QHBoxLayout(self.rapport_page)
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.horizontalLayout_50.setContentsMargins(-1, 0, -1, -1)
        self.scrollArea = QScrollArea(self.rapport_page)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 753, 848))
        self.horizontalLayout_59 = QHBoxLayout(self.scrollAreaWidgetContents_3)
        self.horizontalLayout_59.setObjectName(u"horizontalLayout_59")
        self.horizontalLayout_59.setContentsMargins(-1, 0, -1, -1)
        self.widget_16 = QWidget(self.scrollAreaWidgetContents_3)
        self.widget_16.setObjectName(u"widget_16")
        self.verticalLayout_61 = QVBoxLayout(self.widget_16)
        self.verticalLayout_61.setSpacing(25)
        self.verticalLayout_61.setObjectName(u"verticalLayout_61")
        self.verticalLayout_61.setContentsMargins(-1, 0, -1, -1)
        self.widget_global = QWidget(self.widget_16)
        self.widget_global.setObjectName(u"widget_global")
        self.verticalLayout_181 = QVBoxLayout(self.widget_global)
        self.verticalLayout_181.setObjectName(u"verticalLayout_181")
        self.frame_186 = QFrame(self.widget_global)
        self.frame_186.setObjectName(u"frame_186")
        self.frame_186.setFrameShape(QFrame.StyledPanel)
        self.frame_186.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_60 = QHBoxLayout(self.frame_186)
        self.horizontalLayout_60.setObjectName(u"horizontalLayout_60")
        self.horizontalLayout_60.setContentsMargins(0, 0, 0, 0)
        self.frame_357 = QFrame(self.frame_186)
        self.frame_357.setObjectName(u"frame_357")
        self.frame_357.setFrameShape(QFrame.StyledPanel)
        self.frame_357.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_130 = QHBoxLayout(self.frame_357)
        self.horizontalLayout_130.setObjectName(u"horizontalLayout_130")
        self.label_42 = QLabel(self.frame_357)
        self.label_42.setObjectName(u"label_42")

        self.horizontalLayout_130.addWidget(self.label_42)

        self.label_repport_type = QLabel(self.frame_357)
        self.label_repport_type.setObjectName(u"label_repport_type")

        self.horizontalLayout_130.addWidget(self.label_repport_type)


        self.horizontalLayout_60.addWidget(self.frame_357)

        self.frame_358 = QFrame(self.frame_186)
        self.frame_358.setObjectName(u"frame_358")
        self.frame_358.setFrameShape(QFrame.StyledPanel)
        self.frame_358.setFrameShadow(QFrame.Raised)
        self.verticalLayout_315 = QVBoxLayout(self.frame_358)
        self.verticalLayout_315.setSpacing(0)
        self.verticalLayout_315.setObjectName(u"verticalLayout_315")
        self.verticalLayout_315.setContentsMargins(-1, 0, -1, 0)
        self.label_139 = QLabel(self.frame_358)
        self.label_139.setObjectName(u"label_139")
        self.label_139.setFont(font2)

        self.verticalLayout_315.addWidget(self.label_139)

        self.repport_type = QComboBox(self.frame_358)
        self.repport_type.setObjectName(u"repport_type")
        self.repport_type.setMinimumSize(QSize(0, 37))
        self.repport_type.setMaximumSize(QSize(16777215, 37))
        self.repport_type.setFont(font2)

        self.verticalLayout_315.addWidget(self.repport_type)


        self.horizontalLayout_60.addWidget(self.frame_358)


        self.verticalLayout_181.addWidget(self.frame_186)

        self.frame_187 = QFrame(self.widget_global)
        self.frame_187.setObjectName(u"frame_187")
        self.frame_187.setFrameShape(QFrame.StyledPanel)
        self.frame_187.setFrameShadow(QFrame.Raised)
        self.verticalLayout_182 = QVBoxLayout(self.frame_187)
        self.verticalLayout_182.setSpacing(0)
        self.verticalLayout_182.setObjectName(u"verticalLayout_182")
        self.verticalLayout_182.setContentsMargins(12, -1, -1, 4)
        self.label_43 = QLabel(self.frame_187)
        self.label_43.setObjectName(u"label_43")

        self.verticalLayout_182.addWidget(self.label_43)

        self.global_date_debut = QDateEdit(self.frame_187)
        self.global_date_debut.setObjectName(u"global_date_debut")
        self.global_date_debut.setFont(font2)
        self.global_date_debut.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.global_date_debut.setTabletTracking(True)
        self.global_date_debut.setAutoFillBackground(True)
        self.global_date_debut.setMinimumDateTime(QDateTime(QDate(2024, 8, 14), QTime(0, 0, 0)))
        self.global_date_debut.setMinimumDate(QDate(2024, 8, 14))
        self.global_date_debut.setCalendarPopup(True)

        self.verticalLayout_182.addWidget(self.global_date_debut)


        self.verticalLayout_181.addWidget(self.frame_187)

        self.frame_188 = QFrame(self.widget_global)
        self.frame_188.setObjectName(u"frame_188")
        self.frame_188.setFrameShape(QFrame.StyledPanel)
        self.frame_188.setFrameShadow(QFrame.Raised)
        self.verticalLayout_183 = QVBoxLayout(self.frame_188)
        self.verticalLayout_183.setSpacing(0)
        self.verticalLayout_183.setObjectName(u"verticalLayout_183")
        self.verticalLayout_183.setContentsMargins(12, 0, -1, -1)
        self.label_44 = QLabel(self.frame_188)
        self.label_44.setObjectName(u"label_44")

        self.verticalLayout_183.addWidget(self.label_44)

        self.global_date_fin = QDateEdit(self.frame_188)
        self.global_date_fin.setObjectName(u"global_date_fin")
        self.global_date_fin.setFont(font2)
        self.global_date_fin.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.global_date_fin.setCorrectionMode(QAbstractSpinBox.CorrectToNearestValue)
        self.global_date_fin.setProperty(u"showGroupSeparator", True)
        self.global_date_fin.setMinimumDate(QDate(2024, 7, 15))
        self.global_date_fin.setCurrentSection(QDateTimeEdit.DaySection)
        self.global_date_fin.setCalendarPopup(True)
        self.global_date_fin.setCurrentSectionIndex(0)
        self.global_date_fin.setTimeSpec(Qt.TimeZone)

        self.verticalLayout_183.addWidget(self.global_date_fin)


        self.verticalLayout_181.addWidget(self.frame_188)

        self.frame_189 = QFrame(self.widget_global)
        self.frame_189.setObjectName(u"frame_189")
        self.frame_189.setFrameShape(QFrame.StyledPanel)
        self.frame_189.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_61 = QHBoxLayout(self.frame_189)
        self.horizontalLayout_61.setSpacing(0)
        self.horizontalLayout_61.setObjectName(u"horizontalLayout_61")
        self.horizontalLayout_61.setContentsMargins(0, 0, 9, 9)
        self.global_rapport_imprimer = QPushButton(self.frame_189)
        self.global_rapport_imprimer.setObjectName(u"global_rapport_imprimer")
        self.global_rapport_imprimer.setMinimumSize(QSize(130, 33))
        self.global_rapport_imprimer.setFont(font4)
        self.global_rapport_imprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.global_rapport_imprimer.setFlat(True)

        self.horizontalLayout_61.addWidget(self.global_rapport_imprimer)


        self.verticalLayout_181.addWidget(self.frame_189, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_61.addWidget(self.widget_global)

        self.widget_administratif = QWidget(self.widget_16)
        self.widget_administratif.setObjectName(u"widget_administratif")
        self.verticalLayout_54 = QVBoxLayout(self.widget_administratif)
        self.verticalLayout_54.setObjectName(u"verticalLayout_54")
        self.frame_174 = QFrame(self.widget_administratif)
        self.frame_174.setObjectName(u"frame_174")
        self.frame_174.setFrameShape(QFrame.StyledPanel)
        self.frame_174.setFrameShadow(QFrame.Raised)
        self.verticalLayout_178 = QVBoxLayout(self.frame_174)
        self.verticalLayout_178.setObjectName(u"verticalLayout_178")
        self.label_47 = QLabel(self.frame_174)
        self.label_47.setObjectName(u"label_47")
        self.label_47.setFont(font2)

        self.verticalLayout_178.addWidget(self.label_47)


        self.verticalLayout_54.addWidget(self.frame_174)

        self.frame_176 = QFrame(self.widget_administratif)
        self.frame_176.setObjectName(u"frame_176")
        self.frame_176.setFrameShape(QFrame.StyledPanel)
        self.frame_176.setFrameShadow(QFrame.Raised)
        self.verticalLayout_175 = QVBoxLayout(self.frame_176)
        self.verticalLayout_175.setObjectName(u"verticalLayout_175")
        self.verticalLayout_175.setContentsMargins(0, 0, -1, 0)
        self.label_55 = QLabel(self.frame_176)
        self.label_55.setObjectName(u"label_55")

        self.verticalLayout_175.addWidget(self.label_55)


        self.verticalLayout_54.addWidget(self.frame_176)

        self.frame_175 = QFrame(self.widget_administratif)
        self.frame_175.setObjectName(u"frame_175")
        self.frame_175.setFrameShape(QFrame.StyledPanel)
        self.frame_175.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_54 = QHBoxLayout(self.frame_175)
        self.horizontalLayout_54.setSpacing(7)
        self.horizontalLayout_54.setObjectName(u"horizontalLayout_54")
        self.frame_180 = QFrame(self.frame_175)
        self.frame_180.setObjectName(u"frame_180")
        self.frame_180.setFrameShape(QFrame.StyledPanel)
        self.frame_180.setFrameShadow(QFrame.Raised)
        self.verticalLayout_177 = QVBoxLayout(self.frame_180)
        self.verticalLayout_177.setSpacing(0)
        self.verticalLayout_177.setObjectName(u"verticalLayout_177")
        self.verticalLayout_177.setContentsMargins(0, 0, 0, 0)
        self.label_48 = QLabel(self.frame_180)
        self.label_48.setObjectName(u"label_48")

        self.verticalLayout_177.addWidget(self.label_48)

        self.combo_administratif_niveau = QComboBox(self.frame_180)
        self.combo_administratif_niveau.setObjectName(u"combo_administratif_niveau")
        self.combo_administratif_niveau.setFont(font2)

        self.verticalLayout_177.addWidget(self.combo_administratif_niveau)


        self.horizontalLayout_54.addWidget(self.frame_180)

        self.frame_181 = QFrame(self.frame_175)
        self.frame_181.setObjectName(u"frame_181")
        self.frame_181.setFrameShape(QFrame.StyledPanel)
        self.frame_181.setFrameShadow(QFrame.Raised)
        self.verticalLayout_176 = QVBoxLayout(self.frame_181)
        self.verticalLayout_176.setSpacing(0)
        self.verticalLayout_176.setObjectName(u"verticalLayout_176")
        self.verticalLayout_176.setContentsMargins(0, 0, 0, 0)
        self.label_53 = QLabel(self.frame_181)
        self.label_53.setObjectName(u"label_53")

        self.verticalLayout_176.addWidget(self.label_53)

        self.combo_administratif_classe = QComboBox(self.frame_181)
        self.combo_administratif_classe.setObjectName(u"combo_administratif_classe")
        self.combo_administratif_classe.setFont(font2)

        self.verticalLayout_176.addWidget(self.combo_administratif_classe)


        self.horizontalLayout_54.addWidget(self.frame_181)


        self.verticalLayout_54.addWidget(self.frame_175)

        self.frame_177 = QFrame(self.widget_administratif)
        self.frame_177.setObjectName(u"frame_177")
        self.frame_177.setFrameShape(QFrame.StyledPanel)
        self.frame_177.setFrameShadow(QFrame.Raised)
        self.verticalLayout_174 = QVBoxLayout(self.frame_177)
        self.verticalLayout_174.setSpacing(0)
        self.verticalLayout_174.setObjectName(u"verticalLayout_174")
        self.verticalLayout_174.setContentsMargins(-1, 0, -1, 0)
        self.label_54 = QLabel(self.frame_177)
        self.label_54.setObjectName(u"label_54")

        self.verticalLayout_174.addWidget(self.label_54)

        self.combo_administratif_annee = QComboBox(self.frame_177)
        self.combo_administratif_annee.setObjectName(u"combo_administratif_annee")
        self.combo_administratif_annee.setFont(font2)

        self.verticalLayout_174.addWidget(self.combo_administratif_annee)


        self.verticalLayout_54.addWidget(self.frame_177)

        self.frame_179 = QFrame(self.widget_administratif)
        self.frame_179.setObjectName(u"frame_179")
        self.frame_179.setFrameShape(QFrame.StyledPanel)
        self.frame_179.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_56 = QHBoxLayout(self.frame_179)
        self.horizontalLayout_56.setObjectName(u"horizontalLayout_56")
        self.horizontalLayout_56.setContentsMargins(-1, 5, -1, 0)
        self.label_56 = QLabel(self.frame_179)
        self.label_56.setObjectName(u"label_56")

        self.horizontalLayout_56.addWidget(self.label_56)

        self.administrafif_identifiant = QCheckBox(self.frame_179)
        self.administrafif_identifiant.setObjectName(u"administrafif_identifiant")

        self.horizontalLayout_56.addWidget(self.administrafif_identifiant)


        self.verticalLayout_54.addWidget(self.frame_179, 0, Qt.AlignRight)

        self.frame_178 = QFrame(self.widget_administratif)
        self.frame_178.setObjectName(u"frame_178")
        self.frame_178.setFrameShape(QFrame.StyledPanel)
        self.frame_178.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_122 = QHBoxLayout(self.frame_178)
        self.horizontalLayout_122.setObjectName(u"horizontalLayout_122")
        self.horizontalLayout_122.setContentsMargins(-1, 5, -1, 9)
        self.administratif_imprimer = QPushButton(self.frame_178)
        self.administratif_imprimer.setObjectName(u"administratif_imprimer")
        self.administratif_imprimer.setMinimumSize(QSize(130, 33))
        self.administratif_imprimer.setFont(font4)
        self.administratif_imprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.administratif_imprimer.setFlat(True)

        self.horizontalLayout_122.addWidget(self.administratif_imprimer)

        self.format_excel_administratif = QPushButton(self.frame_178)
        self.format_excel_administratif.setObjectName(u"format_excel_administratif")
        self.format_excel_administratif.setMinimumSize(QSize(130, 33))
        self.format_excel_administratif.setFont(font4)
        self.format_excel_administratif.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_122.addWidget(self.format_excel_administratif)


        self.verticalLayout_54.addWidget(self.frame_178, 0, Qt.AlignRight)


        self.verticalLayout_61.addWidget(self.widget_administratif)


        self.horizontalLayout_59.addWidget(self.widget_16)

        self.widget_17 = QWidget(self.scrollAreaWidgetContents_3)
        self.widget_17.setObjectName(u"widget_17")
        self.widget_17.setFont(font4)
        self.verticalLayout_161 = QVBoxLayout(self.widget_17)
        self.verticalLayout_161.setSpacing(19)
        self.verticalLayout_161.setObjectName(u"verticalLayout_161")
        self.verticalLayout_161.setContentsMargins(-1, 0, -1, -1)
        self.widget_financier = QWidget(self.widget_17)
        self.widget_financier.setObjectName(u"widget_financier")
        self.verticalLayout_160 = QVBoxLayout(self.widget_financier)
        self.verticalLayout_160.setSpacing(0)
        self.verticalLayout_160.setObjectName(u"verticalLayout_160")
        self.verticalLayout_160.setContentsMargins(-1, 0, 0, 0)
        self.frame_182 = QFrame(self.widget_financier)
        self.frame_182.setObjectName(u"frame_182")
        self.frame_182.setFrameShape(QFrame.StyledPanel)
        self.frame_182.setFrameShadow(QFrame.Raised)
        self.verticalLayout_179 = QVBoxLayout(self.frame_182)
        self.verticalLayout_179.setObjectName(u"verticalLayout_179")
        self.label_57 = QLabel(self.frame_182)
        self.label_57.setObjectName(u"label_57")
        self.label_57.setFont(font2)

        self.verticalLayout_179.addWidget(self.label_57)


        self.verticalLayout_160.addWidget(self.frame_182)

        self.frame_192 = QFrame(self.widget_financier)
        self.frame_192.setObjectName(u"frame_192")
        self.frame_192.setFrameShape(QFrame.StyledPanel)
        self.frame_192.setFrameShadow(QFrame.Raised)
        self.verticalLayout_186 = QVBoxLayout(self.frame_192)
        self.verticalLayout_186.setObjectName(u"verticalLayout_186")
        self.verticalLayout_186.setContentsMargins(0, 0, -1, 0)
        self.label_66 = QLabel(self.frame_192)
        self.label_66.setObjectName(u"label_66")

        self.verticalLayout_186.addWidget(self.label_66)


        self.verticalLayout_160.addWidget(self.frame_192)

        self.frame_183 = QFrame(self.widget_financier)
        self.frame_183.setObjectName(u"frame_183")
        self.frame_183.setFrameShape(QFrame.StyledPanel)
        self.frame_183.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_55 = QHBoxLayout(self.frame_183)
        self.horizontalLayout_55.setSpacing(7)
        self.horizontalLayout_55.setObjectName(u"horizontalLayout_55")
        self.frame_185 = QFrame(self.frame_183)
        self.frame_185.setObjectName(u"frame_185")
        self.frame_185.setFrameShape(QFrame.StyledPanel)
        self.frame_185.setFrameShadow(QFrame.Raised)
        self.verticalLayout_184 = QVBoxLayout(self.frame_185)
        self.verticalLayout_184.setSpacing(0)
        self.verticalLayout_184.setObjectName(u"verticalLayout_184")
        self.verticalLayout_184.setContentsMargins(0, 0, 0, 0)
        self.label_64 = QLabel(self.frame_185)
        self.label_64.setObjectName(u"label_64")

        self.verticalLayout_184.addWidget(self.label_64)

        self.combo_financier_classe = QComboBox(self.frame_185)
        self.combo_financier_classe.setObjectName(u"combo_financier_classe")
        self.combo_financier_classe.setFont(font2)

        self.verticalLayout_184.addWidget(self.combo_financier_classe)


        self.horizontalLayout_55.addWidget(self.frame_185)


        self.verticalLayout_160.addWidget(self.frame_183)

        self.frame_451 = QFrame(self.widget_financier)
        self.frame_451.setObjectName(u"frame_451")
        self.frame_451.setFrameShape(QFrame.StyledPanel)
        self.frame_451.setFrameShadow(QFrame.Raised)
        self.verticalLayout_116 = QVBoxLayout(self.frame_451)
        self.verticalLayout_116.setSpacing(0)
        self.verticalLayout_116.setObjectName(u"verticalLayout_116")
        self.verticalLayout_116.setContentsMargins(9, 0, 9, 0)
        self.label_180 = QLabel(self.frame_451)
        self.label_180.setObjectName(u"label_180")

        self.verticalLayout_116.addWidget(self.label_180)

        self.financier_annee_academique = QComboBox(self.frame_451)
        self.financier_annee_academique.setObjectName(u"financier_annee_academique")
        self.financier_annee_academique.setFont(font2)

        self.verticalLayout_116.addWidget(self.financier_annee_academique)


        self.verticalLayout_160.addWidget(self.frame_451)

        self.frame_160 = QFrame(self.widget_financier)
        self.frame_160.setObjectName(u"frame_160")
        self.frame_160.setFrameShape(QFrame.StyledPanel)
        self.frame_160.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_51 = QHBoxLayout(self.frame_160)
        self.horizontalLayout_51.setSpacing(0)
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.horizontalLayout_51.setContentsMargins(0, 0, 0, 0)
        self.frame_161 = QFrame(self.frame_160)
        self.frame_161.setObjectName(u"frame_161")
        self.frame_161.setFrameShape(QFrame.StyledPanel)
        self.frame_161.setFrameShadow(QFrame.Raised)
        self.verticalLayout_163 = QVBoxLayout(self.frame_161)
        self.verticalLayout_163.setSpacing(0)
        self.verticalLayout_163.setObjectName(u"verticalLayout_163")
        self.verticalLayout_163.setContentsMargins(-1, 0, 0, 0)
        self.label_58 = QLabel(self.frame_161)
        self.label_58.setObjectName(u"label_58")

        self.verticalLayout_163.addWidget(self.label_58)

        self.date_debut_financier = QDateEdit(self.frame_161)
        self.date_debut_financier.setObjectName(u"date_debut_financier")
        self.date_debut_financier.setFont(font2)
        self.date_debut_financier.setDateTime(QDateTime(QDate(2024, 9, 14), QTime(0, 0, 0)))
        self.date_debut_financier.setMinimumDateTime(QDateTime(QDate(2024, 9, 14), QTime(0, 0, 0)))
        self.date_debut_financier.setCalendarPopup(True)

        self.verticalLayout_163.addWidget(self.date_debut_financier)


        self.horizontalLayout_51.addWidget(self.frame_161)

        self.frame_162 = QFrame(self.frame_160)
        self.frame_162.setObjectName(u"frame_162")
        self.frame_162.setFrameShape(QFrame.StyledPanel)
        self.frame_162.setFrameShadow(QFrame.Raised)
        self.verticalLayout_162 = QVBoxLayout(self.frame_162)
        self.verticalLayout_162.setSpacing(0)
        self.verticalLayout_162.setObjectName(u"verticalLayout_162")
        self.verticalLayout_162.setContentsMargins(-1, 0, 9, 0)
        self.label_68 = QLabel(self.frame_162)
        self.label_68.setObjectName(u"label_68")

        self.verticalLayout_162.addWidget(self.label_68)

        self.date_fin_financier = QDateEdit(self.frame_162)
        self.date_fin_financier.setObjectName(u"date_fin_financier")
        self.date_fin_financier.setFont(font2)
        self.date_fin_financier.setMinimumDateTime(QDateTime(QDate(2024, 9, 14), QTime(0, 0, 0)))
        self.date_fin_financier.setCalendarPopup(True)

        self.verticalLayout_162.addWidget(self.date_fin_financier)


        self.horizontalLayout_51.addWidget(self.frame_162)


        self.verticalLayout_160.addWidget(self.frame_160)

        self.frame_191 = QFrame(self.widget_financier)
        self.frame_191.setObjectName(u"frame_191")
        self.frame_191.setFrameShape(QFrame.StyledPanel)
        self.frame_191.setFrameShadow(QFrame.Raised)
        self.verticalLayout_185 = QVBoxLayout(self.frame_191)
        self.verticalLayout_185.setSpacing(0)
        self.verticalLayout_185.setObjectName(u"verticalLayout_185")
        self.verticalLayout_185.setContentsMargins(-1, 7, -1, 0)
        self.label_65 = QLabel(self.frame_191)
        self.label_65.setObjectName(u"label_65")

        self.verticalLayout_185.addWidget(self.label_65)

        self.combo_financier_annee = QComboBox(self.frame_191)
        self.combo_financier_annee.setObjectName(u"combo_financier_annee")
        self.combo_financier_annee.setFont(font2)

        self.verticalLayout_185.addWidget(self.combo_financier_annee)


        self.verticalLayout_160.addWidget(self.frame_191)

        self.frame_190 = QFrame(self.widget_financier)
        self.frame_190.setObjectName(u"frame_190")
        self.frame_190.setFrameShape(QFrame.StyledPanel)
        self.frame_190.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.frame_190)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(-1, 12, -1, 8)
        self.financier_imprimer = QPushButton(self.frame_190)
        self.financier_imprimer.setObjectName(u"financier_imprimer")
        self.financier_imprimer.setMinimumSize(QSize(130, 33))
        self.financier_imprimer.setFont(font4)
        self.financier_imprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.financier_imprimer.setFlat(True)

        self.horizontalLayout_11.addWidget(self.financier_imprimer)

        self.format_excel_financier = QPushButton(self.frame_190)
        self.format_excel_financier.setObjectName(u"format_excel_financier")
        self.format_excel_financier.setMinimumSize(QSize(130, 33))
        self.format_excel_financier.setFont(font4)
        self.format_excel_financier.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_11.addWidget(self.format_excel_financier)


        self.verticalLayout_160.addWidget(self.frame_190, 0, Qt.AlignRight)


        self.verticalLayout_161.addWidget(self.widget_financier)

        self.widget_11 = QWidget(self.widget_17)
        self.widget_11.setObjectName(u"widget_11")
        self.verticalLayout_324 = QVBoxLayout(self.widget_11)
        self.verticalLayout_324.setObjectName(u"verticalLayout_324")
        self.frame_368 = QFrame(self.widget_11)
        self.frame_368.setObjectName(u"frame_368")
        self.frame_368.setFrameShape(QFrame.StyledPanel)
        self.frame_368.setFrameShadow(QFrame.Raised)
        self.verticalLayout_322 = QVBoxLayout(self.frame_368)
        self.verticalLayout_322.setObjectName(u"verticalLayout_322")
        self.label_143 = QLabel(self.frame_368)
        self.label_143.setObjectName(u"label_143")
        self.label_143.setFont(font2)

        self.verticalLayout_322.addWidget(self.label_143)


        self.verticalLayout_324.addWidget(self.frame_368)

        self.frame_363 = QFrame(self.widget_11)
        self.frame_363.setObjectName(u"frame_363")
        self.frame_363.setFrameShape(QFrame.StyledPanel)
        self.frame_363.setFrameShadow(QFrame.Raised)
        self.verticalLayout_299 = QVBoxLayout(self.frame_363)
        self.verticalLayout_299.setObjectName(u"verticalLayout_299")
        self.verticalLayout_299.setContentsMargins(0, 0, -1, 0)
        self.label_140 = QLabel(self.frame_363)
        self.label_140.setObjectName(u"label_140")

        self.verticalLayout_299.addWidget(self.label_140)


        self.verticalLayout_324.addWidget(self.frame_363)

        self.frame_364 = QFrame(self.widget_11)
        self.frame_364.setObjectName(u"frame_364")
        self.frame_364.setFrameShape(QFrame.StyledPanel)
        self.frame_364.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_134 = QHBoxLayout(self.frame_364)
        self.horizontalLayout_134.setSpacing(10)
        self.horizontalLayout_134.setObjectName(u"horizontalLayout_134")
        self.frame_365 = QFrame(self.frame_364)
        self.frame_365.setObjectName(u"frame_365")
        self.frame_365.setFrameShape(QFrame.StyledPanel)
        self.frame_365.setFrameShadow(QFrame.Raised)
        self.verticalLayout_320 = QVBoxLayout(self.frame_365)
        self.verticalLayout_320.setSpacing(0)
        self.verticalLayout_320.setObjectName(u"verticalLayout_320")
        self.verticalLayout_320.setContentsMargins(0, 0, 0, 0)
        self.label_141 = QLabel(self.frame_365)
        self.label_141.setObjectName(u"label_141")

        self.verticalLayout_320.addWidget(self.label_141)

        self.combo_pedagogique_niveau = QComboBox(self.frame_365)
        self.combo_pedagogique_niveau.setObjectName(u"combo_pedagogique_niveau")
        self.combo_pedagogique_niveau.setFont(font2)

        self.verticalLayout_320.addWidget(self.combo_pedagogique_niveau)


        self.horizontalLayout_134.addWidget(self.frame_365)

        self.frame_366 = QFrame(self.frame_364)
        self.frame_366.setObjectName(u"frame_366")
        self.frame_366.setFrameShape(QFrame.StyledPanel)
        self.frame_366.setFrameShadow(QFrame.Raised)
        self.verticalLayout_321 = QVBoxLayout(self.frame_366)
        self.verticalLayout_321.setSpacing(0)
        self.verticalLayout_321.setObjectName(u"verticalLayout_321")
        self.verticalLayout_321.setContentsMargins(0, 0, 0, 0)
        self.label_142 = QLabel(self.frame_366)
        self.label_142.setObjectName(u"label_142")

        self.verticalLayout_321.addWidget(self.label_142)

        self.combo_pedagogique_classe = QComboBox(self.frame_366)
        self.combo_pedagogique_classe.setObjectName(u"combo_pedagogique_classe")
        self.combo_pedagogique_classe.setFont(font2)

        self.verticalLayout_321.addWidget(self.combo_pedagogique_classe)


        self.horizontalLayout_134.addWidget(self.frame_366)


        self.verticalLayout_324.addWidget(self.frame_364)

        self.frame_369 = QFrame(self.widget_11)
        self.frame_369.setObjectName(u"frame_369")
        self.frame_369.setFrameShape(QFrame.StyledPanel)
        self.frame_369.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_184 = QHBoxLayout(self.frame_369)
        self.horizontalLayout_184.setSpacing(0)
        self.horizontalLayout_184.setObjectName(u"horizontalLayout_184")
        self.horizontalLayout_184.setContentsMargins(-1, 0, -1, 0)
        self.frame_445 = QFrame(self.frame_369)
        self.frame_445.setObjectName(u"frame_445")
        self.frame_445.setFrameShape(QFrame.StyledPanel)
        self.frame_445.setFrameShadow(QFrame.Raised)
        self.verticalLayout_383 = QVBoxLayout(self.frame_445)
        self.verticalLayout_383.setSpacing(0)
        self.verticalLayout_383.setObjectName(u"verticalLayout_383")
        self.verticalLayout_383.setContentsMargins(0, 0, -1, 0)
        self.label_177 = QLabel(self.frame_445)
        self.label_177.setObjectName(u"label_177")

        self.verticalLayout_383.addWidget(self.label_177)

        self.combo_pedagogique_mois = QComboBox(self.frame_445)
        self.combo_pedagogique_mois.setObjectName(u"combo_pedagogique_mois")
        self.combo_pedagogique_mois.setFont(font2)

        self.verticalLayout_383.addWidget(self.combo_pedagogique_mois)


        self.horizontalLayout_184.addWidget(self.frame_445)

        self.frame_444 = QFrame(self.frame_369)
        self.frame_444.setObjectName(u"frame_444")
        self.frame_444.setFrameShape(QFrame.StyledPanel)
        self.frame_444.setFrameShadow(QFrame.Raised)
        self.verticalLayout_382 = QVBoxLayout(self.frame_444)
        self.verticalLayout_382.setSpacing(0)
        self.verticalLayout_382.setObjectName(u"verticalLayout_382")
        self.verticalLayout_382.setContentsMargins(-1, 0, 0, 0)
        self.label_144 = QLabel(self.frame_444)
        self.label_144.setObjectName(u"label_144")

        self.verticalLayout_382.addWidget(self.label_144)

        self.combo_pedagogique_annee = QComboBox(self.frame_444)
        self.combo_pedagogique_annee.setObjectName(u"combo_pedagogique_annee")
        self.combo_pedagogique_annee.setFont(font2)

        self.verticalLayout_382.addWidget(self.combo_pedagogique_annee)


        self.horizontalLayout_184.addWidget(self.frame_444)


        self.verticalLayout_324.addWidget(self.frame_369)

        self.frame_370 = QFrame(self.widget_11)
        self.frame_370.setObjectName(u"frame_370")
        self.frame_370.setFrameShape(QFrame.StyledPanel)
        self.frame_370.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_136 = QHBoxLayout(self.frame_370)
        self.horizontalLayout_136.setObjectName(u"horizontalLayout_136")
        self.horizontalLayout_136.setContentsMargins(-1, 5, -1, 0)
        self.label_145 = QLabel(self.frame_370)
        self.label_145.setObjectName(u"label_145")

        self.horizontalLayout_136.addWidget(self.label_145)

        self.pedagogique_identifiant = QCheckBox(self.frame_370)
        self.pedagogique_identifiant.setObjectName(u"pedagogique_identifiant")

        self.horizontalLayout_136.addWidget(self.pedagogique_identifiant)


        self.verticalLayout_324.addWidget(self.frame_370)

        self.frame_367 = QFrame(self.widget_11)
        self.frame_367.setObjectName(u"frame_367")
        self.frame_367.setFrameShape(QFrame.StyledPanel)
        self.frame_367.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_135 = QHBoxLayout(self.frame_367)
        self.horizontalLayout_135.setObjectName(u"horizontalLayout_135")
        self.horizontalLayout_135.setContentsMargins(-1, 5, -1, 9)
        self.pedagogique_imprimer = QPushButton(self.frame_367)
        self.pedagogique_imprimer.setObjectName(u"pedagogique_imprimer")
        self.pedagogique_imprimer.setMinimumSize(QSize(130, 33))
        self.pedagogique_imprimer.setFont(font4)
        self.pedagogique_imprimer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pedagogique_imprimer.setFlat(True)

        self.horizontalLayout_135.addWidget(self.pedagogique_imprimer)

        self.format_excel_pedagogique = QPushButton(self.frame_367)
        self.format_excel_pedagogique.setObjectName(u"format_excel_pedagogique")
        self.format_excel_pedagogique.setMinimumSize(QSize(130, 33))
        self.format_excel_pedagogique.setFont(font4)
        self.format_excel_pedagogique.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_135.addWidget(self.format_excel_pedagogique)


        self.verticalLayout_324.addWidget(self.frame_367, 0, Qt.AlignRight)

        self.frame_468 = QFrame(self.widget_11)
        self.frame_468.setObjectName(u"frame_468")
        self.frame_468.setFrameShape(QFrame.StyledPanel)
        self.frame_468.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_191 = QHBoxLayout(self.frame_468)
        self.horizontalLayout_191.setSpacing(0)
        self.horizontalLayout_191.setObjectName(u"horizontalLayout_191")
        self.horizontalLayout_191.setContentsMargins(0, 0, 0, 0)
        self.frame_469 = QFrame(self.frame_468)
        self.frame_469.setObjectName(u"frame_469")
        self.frame_469.setFrameShape(QFrame.StyledPanel)
        self.frame_469.setFrameShadow(QFrame.Raised)
        self.verticalLayout_399 = QVBoxLayout(self.frame_469)
        self.verticalLayout_399.setObjectName(u"verticalLayout_399")
        self.desicion_finale_exel = QPushButton(self.frame_469)
        self.desicion_finale_exel.setObjectName(u"desicion_finale_exel")
        self.desicion_finale_exel.setMinimumSize(QSize(130, 33))
        self.desicion_finale_exel.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_399.addWidget(self.desicion_finale_exel)


        self.horizontalLayout_191.addWidget(self.frame_469)

        self.frame_470 = QFrame(self.frame_468)
        self.frame_470.setObjectName(u"frame_470")
        self.frame_470.setFrameShape(QFrame.StyledPanel)
        self.frame_470.setFrameShadow(QFrame.Raised)
        self.verticalLayout_400 = QVBoxLayout(self.frame_470)
        self.verticalLayout_400.setObjectName(u"verticalLayout_400")
        self.desicion_finale = QPushButton(self.frame_470)
        self.desicion_finale.setObjectName(u"desicion_finale")
        self.desicion_finale.setMinimumSize(QSize(130, 33))
        self.desicion_finale.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.verticalLayout_400.addWidget(self.desicion_finale)


        self.horizontalLayout_191.addWidget(self.frame_470)


        self.verticalLayout_324.addWidget(self.frame_468)


        self.verticalLayout_161.addWidget(self.widget_11)

        self.frame_467 = QFrame(self.widget_17)
        self.frame_467.setObjectName(u"frame_467")
        self.frame_467.setFrameShape(QFrame.StyledPanel)
        self.frame_467.setFrameShadow(QFrame.Raised)

        self.verticalLayout_161.addWidget(self.frame_467)

        self.widget_12 = QWidget(self.widget_17)
        self.widget_12.setObjectName(u"widget_12")

        self.verticalLayout_161.addWidget(self.widget_12)


        self.horizontalLayout_59.addWidget(self.widget_17)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_3)

        self.horizontalLayout_50.addWidget(self.scrollArea)

        self.stackedWidget.addWidget(self.rapport_page)
        self.param_page = QWidget()
        self.param_page.setObjectName(u"param_page")
        self.verticalLayout_137 = QVBoxLayout(self.param_page)
        self.verticalLayout_137.setObjectName(u"verticalLayout_137")
        self.verticalLayout_137.setContentsMargins(0, 0, 0, -1)
        self.frame_107 = QFrame(self.param_page)
        self.frame_107.setObjectName(u"frame_107")
        self.frame_107.setFrameShape(QFrame.StyledPanel)
        self.frame_107.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_107)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_8 = QScrollArea(self.frame_107)
        self.scrollArea_8.setObjectName(u"scrollArea_8")
        self.scrollArea_8.setMaximumSize(QSize(16777215, 60))
        self.scrollArea_8.setWidgetResizable(True)
        self.scrollArea_8.setAlignment(Qt.AlignHCenter|Qt.AlignTop)
        self.scrollAreaWidgetContents_11 = QWidget()
        self.scrollAreaWidgetContents_11.setObjectName(u"scrollAreaWidgetContents_11")
        self.scrollAreaWidgetContents_11.setGeometry(QRect(0, 0, 83, 16))
        self.frame_362 = QFrame(self.scrollAreaWidgetContents_11)
        self.frame_362.setObjectName(u"frame_362")
        self.frame_362.setGeometry(QRect(20, 20, 948, 40))
        self.frame_362.setFrameShape(QFrame.StyledPanel)
        self.frame_362.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_133 = QHBoxLayout(self.frame_362)
        self.horizontalLayout_133.setSpacing(5)
        self.horizontalLayout_133.setObjectName(u"horizontalLayout_133")
        self.horizontalLayout_133.setContentsMargins(0, 0, 0, 0)
        self.btn_param_paiement = QPushButton(self.frame_362)
        self.btn_param_paiement.setObjectName(u"btn_param_paiement")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.btn_param_paiement.sizePolicy().hasHeightForWidth())
        self.btn_param_paiement.setSizePolicy(sizePolicy8)
        self.btn_param_paiement.setMinimumSize(QSize(185, 0))
        self.btn_param_paiement.setFont(font4)
        self.btn_param_paiement.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_param_paiement.setCheckable(True)
        self.btn_param_paiement.setChecked(True)
        self.btn_param_paiement.setAutoExclusive(True)

        self.horizontalLayout_133.addWidget(self.btn_param_paiement)

        self.btn_param_exam = QPushButton(self.frame_362)
        self.btn_param_exam.setObjectName(u"btn_param_exam")
        self.btn_param_exam.setMinimumSize(QSize(180, 0))
        self.btn_param_exam.setFont(font4)
        self.btn_param_exam.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_param_exam.setCheckable(True)
        self.btn_param_exam.setAutoExclusive(True)

        self.horizontalLayout_133.addWidget(self.btn_param_exam)

        self.btn_classe = QPushButton(self.frame_362)
        self.btn_classe.setObjectName(u"btn_classe")
        self.btn_classe.setMinimumSize(QSize(0, 0))
        self.btn_classe.setFont(font4)
        self.btn_classe.setCheckable(True)
        self.btn_classe.setAutoExclusive(True)

        self.horizontalLayout_133.addWidget(self.btn_classe)

        self.btn_annee = QPushButton(self.frame_362)
        self.btn_annee.setObjectName(u"btn_annee")
        self.btn_annee.setMinimumSize(QSize(160, 0))
        self.btn_annee.setFont(font4)
        self.btn_annee.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_annee.setCheckable(True)
        self.btn_annee.setAutoExclusive(True)

        self.horizontalLayout_133.addWidget(self.btn_annee)

        self.btn_frais = QPushButton(self.frame_362)
        self.btn_frais.setObjectName(u"btn_frais")
        self.btn_frais.setMinimumSize(QSize(30, 0))
        self.btn_frais.setFont(font4)
        self.btn_frais.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_frais.setCheckable(True)
        self.btn_frais.setAutoExclusive(True)

        self.horizontalLayout_133.addWidget(self.btn_frais)

        self.btn_param_faculte = QPushButton(self.frame_362)
        self.btn_param_faculte.setObjectName(u"btn_param_faculte")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.btn_param_faculte.sizePolicy().hasHeightForWidth())
        self.btn_param_faculte.setSizePolicy(sizePolicy9)
        self.btn_param_faculte.setMinimumSize(QSize(0, 0))
        self.btn_param_faculte.setFont(font4)
        self.btn_param_faculte.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_133.addWidget(self.btn_param_faculte)

        self.btn_frais_divers = QPushButton(self.frame_362)
        self.btn_frais_divers.setObjectName(u"btn_frais_divers")
        self.btn_frais_divers.setMinimumSize(QSize(0, 0))
        self.btn_frais_divers.setFont(font4)

        self.horizontalLayout_133.addWidget(self.btn_frais_divers)

        self.scrollArea_8.setWidget(self.scrollAreaWidgetContents_11)

        self.horizontalLayout_3.addWidget(self.scrollArea_8)


        self.verticalLayout_137.addWidget(self.frame_107)

        self.tabWidget_params = QTabWidget(self.param_page)
        self.tabWidget_params.setObjectName(u"tabWidget_params")
        self.ezam_params = QWidget()
        self.ezam_params.setObjectName(u"ezam_params")
        self.verticalLayout_214 = QVBoxLayout(self.ezam_params)
        self.verticalLayout_214.setObjectName(u"verticalLayout_214")
        self.widget_param_exam = QWidget(self.ezam_params)
        self.widget_param_exam.setObjectName(u"widget_param_exam")
        self.verticalLayout_156 = QVBoxLayout(self.widget_param_exam)
        self.verticalLayout_156.setObjectName(u"verticalLayout_156")
        self.verticalLayout_156.setContentsMargins(0, 0, 0, 0)
        self.frame_151 = QFrame(self.widget_param_exam)
        self.frame_151.setObjectName(u"frame_151")
        self.frame_151.setFrameShape(QFrame.StyledPanel)
        self.frame_151.setFrameShadow(QFrame.Raised)
        self.verticalLayout_148 = QVBoxLayout(self.frame_151)
        self.verticalLayout_148.setObjectName(u"verticalLayout_148")
        self.verticalLayout_148.setContentsMargins(-1, 0, -1, 0)
        self.add_param_exam = QPushButton(self.frame_151)
        self.add_param_exam.setObjectName(u"add_param_exam")
        self.add_param_exam.setMinimumSize(QSize(240, 33))
        self.add_param_exam.setFont(font4)

        self.verticalLayout_148.addWidget(self.add_param_exam)


        self.verticalLayout_156.addWidget(self.frame_151, 0, Qt.AlignRight)

        self.frame_153 = QFrame(self.widget_param_exam)
        self.frame_153.setObjectName(u"frame_153")
        self.frame_153.setFrameShape(QFrame.StyledPanel)
        self.frame_153.setFrameShadow(QFrame.Raised)
        self.verticalLayout_149 = QVBoxLayout(self.frame_153)
        self.verticalLayout_149.setSpacing(0)
        self.verticalLayout_149.setObjectName(u"verticalLayout_149")
        self.verticalLayout_149.setContentsMargins(0, 0, 0, 0)
        self.table_param_exam = QTableWidget(self.frame_153)
        self.table_param_exam.setObjectName(u"table_param_exam")
        self.table_param_exam.setMinimumSize(QSize(0, 450))
        self.table_param_exam.setSortingEnabled(True)

        self.verticalLayout_149.addWidget(self.table_param_exam)


        self.verticalLayout_156.addWidget(self.frame_153)

        self.frame_152 = QFrame(self.widget_param_exam)
        self.frame_152.setObjectName(u"frame_152")
        self.frame_152.setFrameShape(QFrame.StyledPanel)
        self.frame_152.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_47 = QHBoxLayout(self.frame_152)
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.horizontalLayout_47.setContentsMargins(-1, 0, -1, 0)
        self.prev_param_exam = QPushButton(self.frame_152)
        self.prev_param_exam.setObjectName(u"prev_param_exam")
        self.prev_param_exam.setFlat(True)

        self.horizontalLayout_47.addWidget(self.prev_param_exam)

        self.next_param_exam = QPushButton(self.frame_152)
        self.next_param_exam.setObjectName(u"next_param_exam")
        self.next_param_exam.setFlat(True)

        self.horizontalLayout_47.addWidget(self.next_param_exam)


        self.verticalLayout_156.addWidget(self.frame_152, 0, Qt.AlignRight)


        self.verticalLayout_214.addWidget(self.widget_param_exam, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.ezam_params, "")
        self.paiement_params = QWidget()
        self.paiement_params.setObjectName(u"paiement_params")
        self.verticalLayout_210 = QVBoxLayout(self.paiement_params)
        self.verticalLayout_210.setSpacing(6)
        self.verticalLayout_210.setObjectName(u"verticalLayout_210")
        self.verticalLayout_210.setContentsMargins(9, 9, 9, 9)
        self.widget_parametre_paiement = QWidget(self.paiement_params)
        self.widget_parametre_paiement.setObjectName(u"widget_parametre_paiement")
        self.widget_parametre_paiement.setMinimumSize(QSize(0, 300))
        self.verticalLayout_145 = QVBoxLayout(self.widget_parametre_paiement)
        self.verticalLayout_145.setObjectName(u"verticalLayout_145")
        self.verticalLayout_145.setContentsMargins(0, 0, 0, 0)
        self.frame_145 = QFrame(self.widget_parametre_paiement)
        self.frame_145.setObjectName(u"frame_145")
        self.frame_145.setFrameShape(QFrame.StyledPanel)
        self.frame_145.setFrameShadow(QFrame.Raised)
        self.verticalLayout_143 = QVBoxLayout(self.frame_145)
        self.verticalLayout_143.setObjectName(u"verticalLayout_143")
        self.verticalLayout_143.setContentsMargins(-1, 0, -1, 0)
        self.add_paiement_params = QPushButton(self.frame_145)
        self.add_paiement_params.setObjectName(u"add_paiement_params")
        self.add_paiement_params.setMinimumSize(QSize(250, 33))
        self.add_paiement_params.setFont(font4)

        self.verticalLayout_143.addWidget(self.add_paiement_params)


        self.verticalLayout_145.addWidget(self.frame_145, 0, Qt.AlignRight)

        self.frame_147 = QFrame(self.widget_parametre_paiement)
        self.frame_147.setObjectName(u"frame_147")
        self.frame_147.setFrameShape(QFrame.StyledPanel)
        self.frame_147.setFrameShadow(QFrame.Raised)
        self.verticalLayout_144 = QVBoxLayout(self.frame_147)
        self.verticalLayout_144.setObjectName(u"verticalLayout_144")
        self.verticalLayout_144.setContentsMargins(0, 0, 0, 0)
        self.table_paiement_params = QTableWidget(self.frame_147)
        self.table_paiement_params.setObjectName(u"table_paiement_params")
        self.table_paiement_params.setMinimumSize(QSize(0, 450))
        self.table_paiement_params.setSortingEnabled(True)

        self.verticalLayout_144.addWidget(self.table_paiement_params)


        self.verticalLayout_145.addWidget(self.frame_147)

        self.frame_146 = QFrame(self.widget_parametre_paiement)
        self.frame_146.setObjectName(u"frame_146")
        self.frame_146.setFrameShape(QFrame.StyledPanel)
        self.frame_146.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_16 = QHBoxLayout(self.frame_146)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(-1, 0, -1, 0)
        self.prev_paiement_params = QPushButton(self.frame_146)
        self.prev_paiement_params.setObjectName(u"prev_paiement_params")
        self.prev_paiement_params.setFlat(True)

        self.horizontalLayout_16.addWidget(self.prev_paiement_params)

        self.next_paiement_params = QPushButton(self.frame_146)
        self.next_paiement_params.setObjectName(u"next_paiement_params")
        self.next_paiement_params.setFlat(True)

        self.horizontalLayout_16.addWidget(self.next_paiement_params)


        self.verticalLayout_145.addWidget(self.frame_146, 0, Qt.AlignRight)


        self.verticalLayout_210.addWidget(self.widget_parametre_paiement, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.paiement_params, "")
        self.tab_annee = QWidget()
        self.tab_annee.setObjectName(u"tab_annee")
        self.verticalLayout_236 = QVBoxLayout(self.tab_annee)
        self.verticalLayout_236.setSpacing(6)
        self.verticalLayout_236.setObjectName(u"verticalLayout_236")
        self.verticalLayout_236.setContentsMargins(9, 9, 9, 9)
        self.widget_annee_academique = QWidget(self.tab_annee)
        self.widget_annee_academique.setObjectName(u"widget_annee_academique")
        self.widget_annee_academique.setMinimumSize(QSize(0, 300))
        self.verticalLayout_140 = QVBoxLayout(self.widget_annee_academique)
        self.verticalLayout_140.setSpacing(9)
        self.verticalLayout_140.setObjectName(u"verticalLayout_140")
        self.verticalLayout_140.setContentsMargins(0, 0, 0, 0)
        self.frame_142 = QFrame(self.widget_annee_academique)
        self.frame_142.setObjectName(u"frame_142")
        self.frame_142.setFrameShape(QFrame.StyledPanel)
        self.frame_142.setFrameShadow(QFrame.Raised)
        self.verticalLayout_141 = QVBoxLayout(self.frame_142)
        self.verticalLayout_141.setObjectName(u"verticalLayout_141")
        self.verticalLayout_141.setContentsMargins(-1, 0, -1, 0)
        self.add_year = QPushButton(self.frame_142)
        self.add_year.setObjectName(u"add_year")
        self.add_year.setMinimumSize(QSize(190, 33))
        self.add_year.setFont(font4)

        self.verticalLayout_141.addWidget(self.add_year)


        self.verticalLayout_140.addWidget(self.frame_142, 0, Qt.AlignRight)

        self.frame_143 = QFrame(self.widget_annee_academique)
        self.frame_143.setObjectName(u"frame_143")
        self.frame_143.setFrameShape(QFrame.StyledPanel)
        self.frame_143.setFrameShadow(QFrame.Raised)
        self.verticalLayout_142 = QVBoxLayout(self.frame_143)
        self.verticalLayout_142.setSpacing(0)
        self.verticalLayout_142.setObjectName(u"verticalLayout_142")
        self.verticalLayout_142.setContentsMargins(0, 0, 0, 0)
        self.table_annee = QTableWidget(self.frame_143)
        self.table_annee.setObjectName(u"table_annee")
        self.table_annee.setMinimumSize(QSize(0, 450))
        self.table_annee.setSortingEnabled(True)

        self.verticalLayout_142.addWidget(self.table_annee)


        self.verticalLayout_140.addWidget(self.frame_143, 0, Qt.AlignTop)

        self.frame_144 = QFrame(self.widget_annee_academique)
        self.frame_144.setObjectName(u"frame_144")
        self.frame_144.setFrameShape(QFrame.StyledPanel)
        self.frame_144.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.frame_144)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(-1, 0, -1, 0)
        self.prev_annee = QPushButton(self.frame_144)
        self.prev_annee.setObjectName(u"prev_annee")
        self.prev_annee.setFlat(True)

        self.horizontalLayout_15.addWidget(self.prev_annee)

        self.next_annee = QPushButton(self.frame_144)
        self.next_annee.setObjectName(u"next_annee")
        self.next_annee.setFlat(True)

        self.horizontalLayout_15.addWidget(self.next_annee)


        self.verticalLayout_140.addWidget(self.frame_144, 0, Qt.AlignRight)


        self.verticalLayout_236.addWidget(self.widget_annee_academique, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.tab_annee, "")
        self.tab_classe = QWidget()
        self.tab_classe.setObjectName(u"tab_classe")
        self.verticalLayout_238 = QVBoxLayout(self.tab_classe)
        self.verticalLayout_238.setObjectName(u"verticalLayout_238")
        self.widget_classe = QWidget(self.tab_classe)
        self.widget_classe.setObjectName(u"widget_classe")
        self.verticalLayout_155 = QVBoxLayout(self.widget_classe)
        self.verticalLayout_155.setObjectName(u"verticalLayout_155")
        self.verticalLayout_155.setContentsMargins(0, 0, 0, 0)
        self.frame_154 = QFrame(self.widget_classe)
        self.frame_154.setObjectName(u"frame_154")
        self.frame_154.setFrameShape(QFrame.StyledPanel)
        self.frame_154.setFrameShadow(QFrame.Raised)
        self.verticalLayout_150 = QVBoxLayout(self.frame_154)
        self.verticalLayout_150.setObjectName(u"verticalLayout_150")
        self.verticalLayout_150.setContentsMargins(-1, 0, -1, 0)
        self.add_class = QPushButton(self.frame_154)
        self.add_class.setObjectName(u"add_class")
        self.add_class.setMinimumSize(QSize(150, 33))
        self.add_class.setFont(font5)

        self.verticalLayout_150.addWidget(self.add_class)


        self.verticalLayout_155.addWidget(self.frame_154, 0, Qt.AlignRight)

        self.frame_156 = QFrame(self.widget_classe)
        self.frame_156.setObjectName(u"frame_156")
        self.frame_156.setFrameShape(QFrame.StyledPanel)
        self.frame_156.setFrameShadow(QFrame.Raised)
        self.verticalLayout_151 = QVBoxLayout(self.frame_156)
        self.verticalLayout_151.setObjectName(u"verticalLayout_151")
        self.verticalLayout_151.setContentsMargins(0, 0, -1, 0)
        self.table_class = QTableWidget(self.frame_156)
        self.table_class.setObjectName(u"table_class")
        self.table_class.setMinimumSize(QSize(0, 450))
        self.table_class.setSortingEnabled(True)

        self.verticalLayout_151.addWidget(self.table_class)


        self.verticalLayout_155.addWidget(self.frame_156)

        self.frame_155 = QFrame(self.widget_classe)
        self.frame_155.setObjectName(u"frame_155")
        self.frame_155.setFrameShape(QFrame.StyledPanel)
        self.frame_155.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_48 = QHBoxLayout(self.frame_155)
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.horizontalLayout_48.setContentsMargins(-1, 0, -1, 0)
        self.prev_class = QPushButton(self.frame_155)
        self.prev_class.setObjectName(u"prev_class")
        self.prev_class.setFlat(True)

        self.horizontalLayout_48.addWidget(self.prev_class)

        self.next_class = QPushButton(self.frame_155)
        self.next_class.setObjectName(u"next_class")
        self.next_class.setFlat(True)

        self.horizontalLayout_48.addWidget(self.next_class)


        self.verticalLayout_155.addWidget(self.frame_155, 0, Qt.AlignRight)


        self.verticalLayout_238.addWidget(self.widget_classe, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.tab_classe, "")
        self.tab_faculte = QWidget()
        self.tab_faculte.setObjectName(u"tab_faculte")
        self.verticalLayout_138 = QVBoxLayout(self.tab_faculte)
        self.verticalLayout_138.setObjectName(u"verticalLayout_138")
        self.param_exam_and_fac = QWidget(self.tab_faculte)
        self.param_exam_and_fac.setObjectName(u"param_exam_and_fac")
        self.param_exam_and_fac.setMinimumSize(QSize(0, 300))
        self.horizontalLayout_13 = QHBoxLayout(self.param_exam_and_fac)
        self.horizontalLayout_13.setSpacing(20)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.widget_faculte = QWidget(self.param_exam_and_fac)
        self.widget_faculte.setObjectName(u"widget_faculte")
        self.verticalLayout_157 = QVBoxLayout(self.widget_faculte)
        self.verticalLayout_157.setObjectName(u"verticalLayout_157")
        self.verticalLayout_157.setContentsMargins(0, 0, 0, 0)
        self.frame_148 = QFrame(self.widget_faculte)
        self.frame_148.setObjectName(u"frame_148")
        self.frame_148.setFrameShape(QFrame.StyledPanel)
        self.frame_148.setFrameShadow(QFrame.Raised)
        self.verticalLayout_146 = QVBoxLayout(self.frame_148)
        self.verticalLayout_146.setObjectName(u"verticalLayout_146")
        self.verticalLayout_146.setContentsMargins(-1, 0, -1, 0)
        self.add_faculte = QPushButton(self.frame_148)
        self.add_faculte.setObjectName(u"add_faculte")
        self.add_faculte.setMinimumSize(QSize(200, 33))
        self.add_faculte.setFont(font4)

        self.verticalLayout_146.addWidget(self.add_faculte)


        self.verticalLayout_157.addWidget(self.frame_148, 0, Qt.AlignRight)

        self.frame_150 = QFrame(self.widget_faculte)
        self.frame_150.setObjectName(u"frame_150")
        self.frame_150.setFrameShape(QFrame.StyledPanel)
        self.frame_150.setFrameShadow(QFrame.Raised)
        self.verticalLayout_147 = QVBoxLayout(self.frame_150)
        self.verticalLayout_147.setSpacing(0)
        self.verticalLayout_147.setObjectName(u"verticalLayout_147")
        self.verticalLayout_147.setContentsMargins(0, 0, 0, 0)
        self.table_faculte = QTableWidget(self.frame_150)
        self.table_faculte.setObjectName(u"table_faculte")
        self.table_faculte.setMinimumSize(QSize(0, 450))
        self.table_faculte.setSortingEnabled(True)

        self.verticalLayout_147.addWidget(self.table_faculte)


        self.verticalLayout_157.addWidget(self.frame_150)

        self.frame_149 = QFrame(self.widget_faculte)
        self.frame_149.setObjectName(u"frame_149")
        self.frame_149.setFrameShape(QFrame.StyledPanel)
        self.frame_149.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.frame_149)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(-1, 0, -1, 0)
        self.prev_faculte = QPushButton(self.frame_149)
        self.prev_faculte.setObjectName(u"prev_faculte")
        self.prev_faculte.setFlat(True)

        self.horizontalLayout_17.addWidget(self.prev_faculte)

        self.next_faculte = QPushButton(self.frame_149)
        self.next_faculte.setObjectName(u"next_faculte")
        self.next_faculte.setFlat(True)

        self.horizontalLayout_17.addWidget(self.next_faculte)


        self.verticalLayout_157.addWidget(self.frame_149, 0, Qt.AlignRight)


        self.horizontalLayout_13.addWidget(self.widget_faculte)


        self.verticalLayout_138.addWidget(self.param_exam_and_fac, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.tab_faculte, "")
        self.tab_frais = QWidget()
        self.tab_frais.setObjectName(u"tab_frais")
        self.verticalLayout_237 = QVBoxLayout(self.tab_frais)
        self.verticalLayout_237.setObjectName(u"verticalLayout_237")
        self.widget_frais = QWidget(self.tab_frais)
        self.widget_frais.setObjectName(u"widget_frais")
        self.verticalLayout_154 = QVBoxLayout(self.widget_frais)
        self.verticalLayout_154.setObjectName(u"verticalLayout_154")
        self.verticalLayout_154.setContentsMargins(0, 0, 0, 0)
        self.frame_157 = QFrame(self.widget_frais)
        self.frame_157.setObjectName(u"frame_157")
        self.frame_157.setFrameShape(QFrame.StyledPanel)
        self.frame_157.setFrameShadow(QFrame.Raised)
        self.verticalLayout_152 = QVBoxLayout(self.frame_157)
        self.verticalLayout_152.setObjectName(u"verticalLayout_152")
        self.verticalLayout_152.setContentsMargins(-1, 0, -1, 0)
        self.add_frais = QPushButton(self.frame_157)
        self.add_frais.setObjectName(u"add_frais")
        self.add_frais.setMinimumSize(QSize(180, 33))
        self.add_frais.setFont(font4)

        self.verticalLayout_152.addWidget(self.add_frais)


        self.verticalLayout_154.addWidget(self.frame_157, 0, Qt.AlignRight)

        self.frame_159 = QFrame(self.widget_frais)
        self.frame_159.setObjectName(u"frame_159")
        self.frame_159.setFrameShape(QFrame.StyledPanel)
        self.frame_159.setFrameShadow(QFrame.Raised)
        self.verticalLayout_153 = QVBoxLayout(self.frame_159)
        self.verticalLayout_153.setObjectName(u"verticalLayout_153")
        self.verticalLayout_153.setContentsMargins(-1, 0, -1, 0)
        self.table_frais = QTableWidget(self.frame_159)
        self.table_frais.setObjectName(u"table_frais")
        self.table_frais.setMinimumSize(QSize(0, 450))
        self.table_frais.setSortingEnabled(True)

        self.verticalLayout_153.addWidget(self.table_frais)


        self.verticalLayout_154.addWidget(self.frame_159)

        self.frame_158 = QFrame(self.widget_frais)
        self.frame_158.setObjectName(u"frame_158")
        self.frame_158.setFrameShape(QFrame.StyledPanel)
        self.frame_158.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_49 = QHBoxLayout(self.frame_158)
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.horizontalLayout_49.setContentsMargins(-1, 0, -1, 0)
        self.prev_frais = QPushButton(self.frame_158)
        self.prev_frais.setObjectName(u"prev_frais")
        self.prev_frais.setFlat(True)

        self.horizontalLayout_49.addWidget(self.prev_frais)

        self.next_frais = QPushButton(self.frame_158)
        self.next_frais.setObjectName(u"next_frais")
        self.next_frais.setFlat(True)

        self.horizontalLayout_49.addWidget(self.next_frais)


        self.verticalLayout_154.addWidget(self.frame_158, 0, Qt.AlignRight)


        self.verticalLayout_237.addWidget(self.widget_frais, 0, Qt.AlignTop)

        self.tabWidget_params.addTab(self.tab_frais, "")
        self.tab_frais_divers = QWidget()
        self.tab_frais_divers.setObjectName(u"tab_frais_divers")
        self.verticalLayout_319 = QVBoxLayout(self.tab_frais_divers)
        self.verticalLayout_319.setObjectName(u"verticalLayout_319")
        self.widget_frais_divers = QWidget(self.tab_frais_divers)
        self.widget_frais_divers.setObjectName(u"widget_frais_divers")
        self.verticalLayout_318 = QVBoxLayout(self.widget_frais_divers)
        self.verticalLayout_318.setObjectName(u"verticalLayout_318")
        self.frame_360 = QFrame(self.widget_frais_divers)
        self.frame_360.setObjectName(u"frame_360")
        self.frame_360.setFrameShape(QFrame.StyledPanel)
        self.frame_360.setFrameShadow(QFrame.Raised)
        self.verticalLayout_316 = QVBoxLayout(self.frame_360)
        self.verticalLayout_316.setObjectName(u"verticalLayout_316")
        self.verticalLayout_316.setContentsMargins(-1, 0, -1, 0)
        self.add_frais_divers = QPushButton(self.frame_360)
        self.add_frais_divers.setObjectName(u"add_frais_divers")
        self.add_frais_divers.setMinimumSize(QSize(180, 33))
        self.add_frais_divers.setFont(font4)

        self.verticalLayout_316.addWidget(self.add_frais_divers)


        self.verticalLayout_318.addWidget(self.frame_360, 0, Qt.AlignRight)

        self.frame_361 = QFrame(self.widget_frais_divers)
        self.frame_361.setObjectName(u"frame_361")
        self.frame_361.setFrameShape(QFrame.StyledPanel)
        self.frame_361.setFrameShadow(QFrame.Raised)
        self.verticalLayout_317 = QVBoxLayout(self.frame_361)
        self.verticalLayout_317.setObjectName(u"verticalLayout_317")
        self.verticalLayout_317.setContentsMargins(-1, 0, -1, 0)
        self.table_frais_divers = QTableWidget(self.frame_361)
        self.table_frais_divers.setObjectName(u"table_frais_divers")
        self.table_frais_divers.setMinimumSize(QSize(0, 450))
        self.table_frais_divers.setSortingEnabled(True)

        self.verticalLayout_317.addWidget(self.table_frais_divers)


        self.verticalLayout_318.addWidget(self.frame_361)

        self.frame_359 = QFrame(self.widget_frais_divers)
        self.frame_359.setObjectName(u"frame_359")
        self.frame_359.setFrameShape(QFrame.StyledPanel)
        self.frame_359.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_131 = QHBoxLayout(self.frame_359)
        self.horizontalLayout_131.setObjectName(u"horizontalLayout_131")
        self.horizontalLayout_131.setContentsMargins(-1, 0, -1, 0)
        self.prev_frais_divers = QPushButton(self.frame_359)
        self.prev_frais_divers.setObjectName(u"prev_frais_divers")
        self.prev_frais_divers.setFlat(True)

        self.horizontalLayout_131.addWidget(self.prev_frais_divers)

        self.next_frais_divers = QPushButton(self.frame_359)
        self.next_frais_divers.setObjectName(u"next_frais_divers")
        self.next_frais_divers.setFlat(True)

        self.horizontalLayout_131.addWidget(self.next_frais_divers)


        self.verticalLayout_318.addWidget(self.frame_359)


        self.verticalLayout_319.addWidget(self.widget_frais_divers)

        self.tabWidget_params.addTab(self.tab_frais_divers, "")

        self.verticalLayout_137.addWidget(self.tabWidget_params)

        self.stackedWidget.addWidget(self.param_page)
        self.log_page = QWidget()
        self.log_page.setObjectName(u"log_page")
        self.verticalLayout_326 = QVBoxLayout(self.log_page)
        self.verticalLayout_326.setObjectName(u"verticalLayout_326")
        self.tabWidget_3 = QTabWidget(self.log_page)
        self.tabWidget_3.setObjectName(u"tabWidget_3")
        self.grafic_log = QWidget()
        self.grafic_log.setObjectName(u"grafic_log")
        self.verticalLayout_327 = QVBoxLayout(self.grafic_log)
        self.verticalLayout_327.setObjectName(u"verticalLayout_327")
        self.frame_374 = QFrame(self.grafic_log)
        self.frame_374.setObjectName(u"frame_374")
        self.frame_374.setFrameShape(QFrame.StyledPanel)
        self.frame_374.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_139 = QHBoxLayout(self.frame_374)
        self.horizontalLayout_139.setSpacing(25)
        self.horizontalLayout_139.setObjectName(u"horizontalLayout_139")
        self.horizontalLayout_139.setContentsMargins(-1, 0, 0, 0)
        self.frame_378 = QFrame(self.frame_374)
        self.frame_378.setObjectName(u"frame_378")
        self.frame_378.setFrameShape(QFrame.StyledPanel)
        self.frame_378.setFrameShadow(QFrame.Raised)
        self.verticalLayout_328 = QVBoxLayout(self.frame_378)
        self.verticalLayout_328.setSpacing(0)
        self.verticalLayout_328.setObjectName(u"verticalLayout_328")
        self.verticalLayout_328.setContentsMargins(0, 0, 0, 0)
        self.label_147 = QLabel(self.frame_378)
        self.label_147.setObjectName(u"label_147")

        self.verticalLayout_328.addWidget(self.label_147)

        self.model_log = QComboBox(self.frame_378)
        self.model_log.setObjectName(u"model_log")
        self.model_log.setMinimumSize(QSize(0, 37))
        self.model_log.setMaximumSize(QSize(16777215, 37))
        self.model_log.setFont(font2)

        self.verticalLayout_328.addWidget(self.model_log)


        self.horizontalLayout_139.addWidget(self.frame_378, 0, Qt.AlignTop)

        self.frame_379 = QFrame(self.frame_374)
        self.frame_379.setObjectName(u"frame_379")
        self.frame_379.setFrameShape(QFrame.StyledPanel)
        self.frame_379.setFrameShadow(QFrame.Raised)
        self.verticalLayout_329 = QVBoxLayout(self.frame_379)
        self.verticalLayout_329.setSpacing(0)
        self.verticalLayout_329.setObjectName(u"verticalLayout_329")
        self.verticalLayout_329.setContentsMargins(0, 0, 0, 0)
        self.label_148 = QLabel(self.frame_379)
        self.label_148.setObjectName(u"label_148")

        self.verticalLayout_329.addWidget(self.label_148)

        self.action_log = QComboBox(self.frame_379)
        self.action_log.setObjectName(u"action_log")
        self.action_log.setMinimumSize(QSize(0, 37))
        self.action_log.setMaximumSize(QSize(16777215, 37))
        self.action_log.setFont(font2)

        self.verticalLayout_329.addWidget(self.action_log)


        self.horizontalLayout_139.addWidget(self.frame_379, 0, Qt.AlignTop)

        self.frame_380 = QFrame(self.frame_374)
        self.frame_380.setObjectName(u"frame_380")
        self.frame_380.setFrameShape(QFrame.StyledPanel)
        self.frame_380.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_141 = QHBoxLayout(self.frame_380)
        self.horizontalLayout_141.setObjectName(u"horizontalLayout_141")
        self.live_log = QPushButton(self.frame_380)
        self.live_log.setObjectName(u"live_log")
        self.live_log.setMinimumSize(QSize(100, 33))
        self.live_log.setFont(font4)
        self.live_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_141.addWidget(self.live_log)


        self.horizontalLayout_139.addWidget(self.frame_380, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_327.addWidget(self.frame_374, 0, Qt.AlignTop)

        self.frame_375 = QFrame(self.grafic_log)
        self.frame_375.setObjectName(u"frame_375")
        self.frame_375.setFrameShape(QFrame.StyledPanel)
        self.frame_375.setFrameShadow(QFrame.Raised)
        self.verticalLayout_330 = QVBoxLayout(self.frame_375)
        self.verticalLayout_330.setSpacing(0)
        self.verticalLayout_330.setObjectName(u"verticalLayout_330")
        self.verticalLayout_330.setContentsMargins(-1, 0, 0, 0)
        self.search_log = QLineEdit(self.frame_375)
        self.search_log.setObjectName(u"search_log")
        self.search_log.setMinimumSize(QSize(350, 37))

        self.verticalLayout_330.addWidget(self.search_log)


        self.verticalLayout_327.addWidget(self.frame_375, 0, Qt.AlignRight|Qt.AlignTop)

        self.frame_377 = QFrame(self.grafic_log)
        self.frame_377.setObjectName(u"frame_377")
        self.frame_377.setFrameShape(QFrame.StyledPanel)
        self.frame_377.setFrameShadow(QFrame.Raised)
        self.verticalLayout_331 = QVBoxLayout(self.frame_377)
        self.verticalLayout_331.setObjectName(u"verticalLayout_331")
        self.log_table = QTableWidget(self.frame_377)
        self.log_table.setObjectName(u"log_table")
        self.log_table.setSortingEnabled(True)
        self.log_table.setWordWrap(False)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.verticalHeader().setHighlightSections(True)

        self.verticalLayout_331.addWidget(self.log_table)


        self.verticalLayout_327.addWidget(self.frame_377)

        self.frame_376 = QFrame(self.grafic_log)
        self.frame_376.setObjectName(u"frame_376")
        self.frame_376.setFrameShape(QFrame.StyledPanel)
        self.frame_376.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_140 = QHBoxLayout(self.frame_376)
        self.horizontalLayout_140.setSpacing(50)
        self.horizontalLayout_140.setObjectName(u"horizontalLayout_140")
        self.horizontalLayout_140.setContentsMargins(0, 0, 0, 0)
        self.prev_log = QPushButton(self.frame_376)
        self.prev_log.setObjectName(u"prev_log")
        self.prev_log.setFont(font4)
        self.prev_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_140.addWidget(self.prev_log)

        self.next_log = QPushButton(self.frame_376)
        self.next_log.setObjectName(u"next_log")
        self.next_log.setFont(font4)
        self.next_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_140.addWidget(self.next_log)


        self.verticalLayout_327.addWidget(self.frame_376, 0, Qt.AlignRight)

        self.tabWidget_3.addTab(self.grafic_log, "")
        self.console_log = QWidget()
        self.console_log.setObjectName(u"console_log")
        self.verticalLayout_334 = QVBoxLayout(self.console_log)
        self.verticalLayout_334.setObjectName(u"verticalLayout_334")
        self.frame_381 = QFrame(self.console_log)
        self.frame_381.setObjectName(u"frame_381")
        self.frame_381.setFrameShape(QFrame.StyledPanel)
        self.frame_381.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_142 = QHBoxLayout(self.frame_381)
        self.horizontalLayout_142.setSpacing(25)
        self.horizontalLayout_142.setObjectName(u"horizontalLayout_142")
        self.horizontalLayout_142.setContentsMargins(-1, 0, 0, 0)
        self.frame_382 = QFrame(self.frame_381)
        self.frame_382.setObjectName(u"frame_382")
        self.frame_382.setFrameShape(QFrame.StyledPanel)
        self.frame_382.setFrameShadow(QFrame.Raised)
        self.verticalLayout_332 = QVBoxLayout(self.frame_382)
        self.verticalLayout_332.setSpacing(0)
        self.verticalLayout_332.setObjectName(u"verticalLayout_332")
        self.verticalLayout_332.setContentsMargins(0, 0, 0, 0)
        self.label_149 = QLabel(self.frame_382)
        self.label_149.setObjectName(u"label_149")

        self.verticalLayout_332.addWidget(self.label_149)

        self.model_log_console = QComboBox(self.frame_382)
        self.model_log_console.setObjectName(u"model_log_console")
        self.model_log_console.setMinimumSize(QSize(0, 37))
        self.model_log_console.setMaximumSize(QSize(16777215, 37))
        self.model_log_console.setFont(font2)

        self.verticalLayout_332.addWidget(self.model_log_console)


        self.horizontalLayout_142.addWidget(self.frame_382, 0, Qt.AlignTop)

        self.frame_383 = QFrame(self.frame_381)
        self.frame_383.setObjectName(u"frame_383")
        self.frame_383.setFrameShape(QFrame.StyledPanel)
        self.frame_383.setFrameShadow(QFrame.Raised)
        self.verticalLayout_333 = QVBoxLayout(self.frame_383)
        self.verticalLayout_333.setSpacing(0)
        self.verticalLayout_333.setObjectName(u"verticalLayout_333")
        self.verticalLayout_333.setContentsMargins(0, 0, 0, 0)
        self.label_150 = QLabel(self.frame_383)
        self.label_150.setObjectName(u"label_150")

        self.verticalLayout_333.addWidget(self.label_150)

        self.action_log_console = QComboBox(self.frame_383)
        self.action_log_console.setObjectName(u"action_log_console")
        self.action_log_console.setMinimumSize(QSize(0, 37))
        self.action_log_console.setMaximumSize(QSize(16777215, 37))
        self.action_log_console.setFont(font2)

        self.verticalLayout_333.addWidget(self.action_log_console)


        self.horizontalLayout_142.addWidget(self.frame_383, 0, Qt.AlignTop)

        self.frame_384 = QFrame(self.frame_381)
        self.frame_384.setObjectName(u"frame_384")
        self.frame_384.setFrameShape(QFrame.StyledPanel)
        self.frame_384.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_143 = QHBoxLayout(self.frame_384)
        self.horizontalLayout_143.setObjectName(u"horizontalLayout_143")
        self.log_grafic = QPushButton(self.frame_384)
        self.log_grafic.setObjectName(u"log_grafic")
        self.log_grafic.setMinimumSize(QSize(100, 0))
        self.log_grafic.setFont(font4)
        self.log_grafic.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayout_143.addWidget(self.log_grafic)


        self.horizontalLayout_142.addWidget(self.frame_384, 0, Qt.AlignRight|Qt.AlignBottom)


        self.verticalLayout_334.addWidget(self.frame_381)

        self.frame_385 = QFrame(self.console_log)
        self.frame_385.setObjectName(u"frame_385")
        self.frame_385.setFrameShape(QFrame.StyledPanel)
        self.frame_385.setFrameShadow(QFrame.Raised)
        self.verticalLayout_335 = QVBoxLayout(self.frame_385)
        self.verticalLayout_335.setObjectName(u"verticalLayout_335")
        self.console_log_table = QTableWidget(self.frame_385)
        self.console_log_table.setObjectName(u"console_log_table")
        self.console_log_table.setSortingEnabled(True)

        self.verticalLayout_335.addWidget(self.console_log_table)


        self.verticalLayout_334.addWidget(self.frame_385)

        self.tabWidget_3.addTab(self.console_log, "")

        self.verticalLayout_326.addWidget(self.tabWidget_3)

        self.stackedWidget.addWidget(self.log_page)
        self.about_page = QWidget()
        self.about_page.setObjectName(u"about_page")
        self.stackedWidget.addWidget(self.about_page)

        self.verticalLayout_8.addWidget(self.stackedWidget)

        self.footer = QFrame(self.main)
        self.footer.setObjectName(u"footer")
        self.footer.setMinimumSize(QSize(0, 30))
        self.footer.setFrameShape(QFrame.StyledPanel)
        self.footer.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_162 = QHBoxLayout(self.footer)
        self.horizontalLayout_162.setSpacing(0)
        self.horizontalLayout_162.setObjectName(u"horizontalLayout_162")
        self.horizontalLayout_162.setContentsMargins(0, 0, 0, 0)
        self.frame_136 = QFrame(self.footer)
        self.frame_136.setObjectName(u"frame_136")
        self.frame_136.setFrameShape(QFrame.StyledPanel)
        self.frame_136.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_189 = QHBoxLayout(self.frame_136)
        self.horizontalLayout_189.setSpacing(0)
        self.horizontalLayout_189.setObjectName(u"horizontalLayout_189")
        self.horizontalLayout_189.setContentsMargins(20, 0, 20, 0)
        self.frame_461 = QFrame(self.frame_136)
        self.frame_461.setObjectName(u"frame_461")
        self.frame_461.setFrameShape(QFrame.StyledPanel)
        self.frame_461.setFrameShadow(QFrame.Raised)
        self.verticalLayout_394 = QVBoxLayout(self.frame_461)
        self.verticalLayout_394.setSpacing(0)
        self.verticalLayout_394.setObjectName(u"verticalLayout_394")
        self.verticalLayout_394.setContentsMargins(0, 0, 0, 0)
        self.label_184 = QLabel(self.frame_461)
        self.label_184.setObjectName(u"label_184")

        self.verticalLayout_394.addWidget(self.label_184)


        self.horizontalLayout_189.addWidget(self.frame_461)

        self.frame_462 = QFrame(self.frame_136)
        self.frame_462.setObjectName(u"frame_462")
        self.frame_462.setFrameShape(QFrame.StyledPanel)
        self.frame_462.setFrameShadow(QFrame.Raised)
        self.verticalLayout_396 = QVBoxLayout(self.frame_462)
        self.verticalLayout_396.setSpacing(0)
        self.verticalLayout_396.setObjectName(u"verticalLayout_396")
        self.verticalLayout_396.setContentsMargins(0, 0, 0, 0)
        self.label_183 = QLabel(self.frame_462)
        self.label_183.setObjectName(u"label_183")
        self.label_183.setStyleSheet(u"font: 13pt \"Sitka\";")

        self.verticalLayout_396.addWidget(self.label_183)


        self.horizontalLayout_189.addWidget(self.frame_462, 0, Qt.AlignHCenter)

        self.frame_463 = QFrame(self.frame_136)
        self.frame_463.setObjectName(u"frame_463")
        self.frame_463.setFrameShape(QFrame.StyledPanel)
        self.frame_463.setFrameShadow(QFrame.Raised)
        self.verticalLayout_395 = QVBoxLayout(self.frame_463)
        self.verticalLayout_395.setSpacing(0)
        self.verticalLayout_395.setObjectName(u"verticalLayout_395")
        self.verticalLayout_395.setContentsMargins(0, 0, 0, 0)
        self.label_expiration_date = QLabel(self.frame_463)
        self.label_expiration_date.setObjectName(u"label_expiration_date")

        self.verticalLayout_395.addWidget(self.label_expiration_date)


        self.horizontalLayout_189.addWidget(self.frame_463, 0, Qt.AlignRight)


        self.horizontalLayout_162.addWidget(self.frame_136)


        self.verticalLayout_8.addWidget(self.footer)


        self.horizontalLayout_4.addWidget(self.main)

        self.main_with_shadow.addWidget(self.shadow_windowPage1)

        self.verticalLayout.addWidget(self.main_with_shadow)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.confirm_password.returnPressed.connect(self.btn_reset_password.click)
        self.confirm_reset_password_perso.returnPressed.connect(self.reinitialiser_mot_de_passe.click)
        self.confirm_reset_password_prof.returnPressed.connect(self.btn_reset_password_prof.click)
        self.rechercher_pour_role.returnPressed.connect(self.recherche_user_role.click)
        self.prix_depense.returnPressed.connect(self.enregistrer_depense.click)
        self.transac_amount.returnPressed.connect(self.save_transac.click)
        self.monthly_payment.returnPressed.connect(self.valider_loans.click)
        self.amount_to_pay.returnPressed.connect(self.faire_un_remboursement.click)
        self.recherche_un_user.returnPressed.connect(self.recherche_user_permission.click)
        self.description_depense.returnPressed.connect(self.prix_depense.setFocus)
        self.input_change_ip.returnPressed.connect(self.change_ip.click)
        self.materiel_name.returnPressed.connect(self.category.setFocus)
        self.quantity.returnPressed.connect(self.unit_prise.setFocus)
        self.unit_prise.returnPressed.connect(self.ajouter_vente.click)
        self.identifiant_user.currentIndexChanged.connect(self.amount.setFocus)
        self.amount.returnPressed.connect(self.term_months.setFocus)
        self.term_months.returnPressed.connect(self.monthly_payment.setFocus)
        self.monthly_payment.returnPressed.connect(self.valider_loans.click)
        self.transac_descript.returnPressed.connect(self.transac_amount.setFocus)
        self.admin_nom.returnPressed.connect(self.admin_prenom.setFocus)
        self.admin_prenom.returnPressed.connect(self.admin_sexe.setFocus)
        self.admin_sexe.returnPressed.connect(self.admin_email.setFocus)
        self.admin_email.returnPressed.connect(self.admin_telephone.setFocus)
        self.admin_telephone.returnPressed.connect(self.admin_adresse.setFocus)
        self.admin_adresse.returnPressed.connect(self.admin_role.setFocus)
        self.niveau_id.currentIndexChanged.connect(self.dernier_etablissement.setFocus)
        self.dernier_etablissement.returnPressed.connect(self.nisu.setFocus)
        self.nisu.returnPressed.connect(self.nom.setFocus)
        self.nom.returnPressed.connect(self.prenom.setFocus)
        self.prenom.returnPressed.connect(self.sexe.setFocus)
        self.telephone.returnPressed.connect(self.adresse.setFocus)
        self.adresse.returnPressed.connect(self.email_3.setFocus)
        self.email_3.returnPressed.connect(self.date_de_naissance.setFocus)
        self.lieu_de_naissance.returnPressed.connect(self.religion.setFocus)
        self.religion.returnPressed.connect(self.annee_academique_id.setFocus)
        self.annee_academique_id.currentIndexChanged.connect(self.classe_actuelle_id.setFocus)
        self.nom_responsable.returnPressed.connect(self.prenom_responsable.setFocus)
        self.prenom_responsable.returnPressed.connect(self.email_responsable.setFocus)
        self.email_responsable.returnPressed.connect(self.adresse_responsable.setFocus)
        self.adresse_responsable.returnPressed.connect(self.telephone_responsable.setFocus)
        self.telephone_responsable.returnPressed.connect(self.sexe_responsable.setFocus)
        self.sexe_responsable.returnPressed.connect(self.suivant_2.click)
        self.input_nom.returnPressed.connect(self.input_email.setFocus)
        self.input_email.returnPressed.connect(self.input_adresse.setFocus)
        self.input_adresse.returnPressed.connect(self.input_ligne1.setFocus)
        self.input_ligne1.returnPressed.connect(self.input_ligne2.setFocus)
        self.input_ligne2.returnPressed.connect(self.choise_profile_image.click)
        self.nom_prof.returnPressed.connect(self.prenom_prof.setFocus)
        self.prenom_prof.returnPressed.connect(self.sexe_prof.setFocus)
        self.sexe_prof.returnPressed.connect(self.email_prof.setFocus)
        self.email_prof.returnPressed.connect(self.telephone_prof.setFocus)
        self.telephone_prof.returnPressed.connect(self.adresse_prof.setFocus)
        self.adresse_prof.returnPressed.connect(self.matiere_enseignee.setFocus)
        self.matiere_enseignee.returnPressed.connect(self.notif_prof.setFocus)
        self.annee_for_bulletin.currentIndexChanged.connect(self.mois_for_bulletin.setCurrentIndex)
        self.mois_for_bulletin.currentIndexChanged.connect(self.classe_for_bulletin.setCurrentIndex)
        self.confirm_password.returnPressed.connect(self.btn_reset_password.animateClick)
        self.input_change_ip.returnPressed.connect(self.change_ip.animateClick)

        self.main_with_shadow.setCurrentIndex(4)
        self.btn_left_home.setDefault(False)
        self.btn_left_admin.setDefault(False)
        self.stackedWidget.setCurrentIndex(12)
        self.admin_stacked.setCurrentIndex(1)
        self.stackedStudent.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        self.stacked_prof.setCurrentIndex(2)
        self.coursStaked.setCurrentIndex(0)
        self.stackedWidgetCours.setCurrentIndex(1)
        self.stackedWidgetProgramme.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(3)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_72.setText("")
        self.label_73.setText("")
        self.label_connect_4.setText(QCoreApplication.translate("MainWindow", u"Application de gestion des \u00e9coles", None))
        self.label_74.setText("")
        self.min_error.setText("")
        self.close_error.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"Adresse ip du server", None))
        self.valider_id_server.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.gif_animate.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_75.setText(QCoreApplication.translate("MainWindow", u"Le service est temporairement indisponible. Veuillez r\u00e9essayer ult\u00e9rieurement. Si le probl\u00e8me persiste, contactez notre support technique.", None))
        self.label_89.setText(QCoreApplication.translate("MainWindow", u"R\u00e9initialiser Votre mot de passe", None))
        self.error_message_2.setText("")
        self.password_for_reset.setText("")
        self.password_for_reset.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Mot de passe", None))
        self.confirm_password.setText("")
        self.confirm_password.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Confirmer le mot de passe", None))
        self.btn_reset_password.setText(QCoreApplication.translate("MainWindow", u"R\u00e9initialiser", None))
        self.label_59.setText("")
        self.label_60.setText("")
        self.label_connect_3.setText(QCoreApplication.translate("MainWindow", u"Application de gestion des \u00e9coles", None))
        self.label_61.setText("")
        self.min_4.setText("")
        self.full_4.setText("")
        self.close_4.setText("")
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"Connexion", None))
        self.logo.setText("")
        self.error_message.setText("")
        self.email_2.setText("")
        self.email_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Email", None))
        self.password_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Password", None))
        self.show_frame_ip.setText(QCoreApplication.translate("MainWindow", u"show ip", None))
        self.label_76.setText(QCoreApplication.translate("MainWindow", u"Modifier l'ip", None))
        self.change_ip.setText(QCoreApplication.translate("MainWindow", u"Modifier", None))
        self.btn_connexion.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.logo_2.setText("")
        self.btn_left_home.setText(QCoreApplication.translate("MainWindow", u"Dashbord", None))
        self.btn_left_admin.setText(QCoreApplication.translate("MainWindow", u"Administration", None))
        self.btn_left_etudiant.setText(QCoreApplication.translate("MainWindow", u"Etudiant", None))
        self.btn_left_promus.setText(QCoreApplication.translate("MainWindow", u"Promus", None))
        self.btn_left_prof.setText(QCoreApplication.translate("MainWindow", u"Professeur", None))
        self.btn_left_notes.setText(QCoreApplication.translate("MainWindow", u"Notes", None))
        self.btn_left_paiement.setText(QCoreApplication.translate("MainWindow", u"Paiement ", None))
        self.btn_left_vente.setText(QCoreApplication.translate("MainWindow", u"Finances", None))
        self.btn_left_rapport.setText(QCoreApplication.translate("MainWindow", u"Rapport", None))
        self.btn_left_profile.setText(QCoreApplication.translate("MainWindow", u"Profile", None))
        self.btn_left_deconnexion.setText(QCoreApplication.translate("MainWindow", u"Deconnexion", None))
        self.btn_settings.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres", None))
        self.btn_log.setText(QCoreApplication.translate("MainWindow", u"Log", None))
        self.btn_actualiser.setText(QCoreApplication.translate("MainWindow", u"Actualiser", None))
        self.btn_a_propos.setText(QCoreApplication.translate("MainWindow", u"   A Propos  ", None))
        self.label_159.setText(QCoreApplication.translate("MainWindow", u"Direct_Request", None))
        self.direct_request.setText("")
        self.label_160.setText(QCoreApplication.translate("MainWindow", u"On (Domain)  Off (IP)", None))
        self.domain_or_ip.setText("")
        self.label_134.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e:", None))
        self.user_email.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_etudiant_dash.setText(QCoreApplication.translate("MainWindow", u"\u00c9tudiant", None))
        self.btn_plus_eudiant.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_etudiant_dash.setText("")
        self.label_number_etudiant.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_professeur.setText(QCoreApplication.translate("MainWindow", u"Professeur", None))
        self.btn_plus_professeur.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_professeur.setText("")
        self.label_number_professeur.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_personnel_dash.setText(QCoreApplication.translate("MainWindow", u"Personnel", None))
        self.btn_plus_personnel.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_personnel.setText("")
        self.label_number_personnel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_classe_dash.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.btn_plus_classe.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_classe_dash.setText("")
        self.label_number_classe_dash.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_notes_2.setText(QCoreApplication.translate("MainWindow", u"Notes", None))
        self.btn_plus_notes.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_notes.setText("")
        self.label_number_notes.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_paiement_2.setText(QCoreApplication.translate("MainWindow", u"Paiement", None))
        self.btn_plus_paiement.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_paiement.setText("")
        self.label_number_paiement.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_cours.setText(QCoreApplication.translate("MainWindow", u"Cours", None))
        self.btn_plus_cours.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.label_icon_cours.setText("")
        self.label_number_cours.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.image_path.setText(QCoreApplication.translate("MainWindow", u"Photo", None))
        self.student_identifiant.setText(QCoreApplication.translate("MainWindow", u"Id Card", None))
        self.label_45.setText("")
        self.full_name.setText(QCoreApplication.translate("MainWindow", u"Full Name", None))
        self.classe.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.date_dexp.setText("")
        self.signature.setText("")
        self.shool_adress.setText("")
        self.search_for_card.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Identifiant de l'etudiant", None))
        self.view_image.setText(QCoreApplication.translate("MainWindow", u"view image", None))
        self.line_camera_ip_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Entrer l'adresse ip du t\u00e9l\u00e9phone", None))
        self.camera_ip_2.setText(QCoreApplication.translate("MainWindow", u"Ip desactive", None))
        self.label_151.setText(QCoreApplication.translate("MainWindow", u"Template", None))
        self.label_135.setText(QCoreApplication.translate("MainWindow", u"Salle", None))
        self.label_152.setText(QCoreApplication.translate("MainWindow", u"Choisir La camera", None))
        self.stop_search_cam.setText(QCoreApplication.translate("MainWindow", u"Stop search ", None))
        self.capture_btn.setText(QCoreApplication.translate("MainWindow", u"Prendre Photo", None))
        self.load_btn.setText(QCoreApplication.translate("MainWindow", u"Charger Photo", None))
        self.generate_btn.setText(QCoreApplication.translate("MainWindow", u"G\u00e9n\u00e9rer le Badge", None))
        self.save_badge.setText(QCoreApplication.translate("MainWindow", u"G\u00e9n\u00e9rer le Badge et enregistrer la photo", None))
        self.add_personnel.setText(QCoreApplication.translate("MainWindow", u"Ajouter personnel", None))
        self.admin_prev.setText("")
        self.admin_label.setText("")
        self.admin_next.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"R\u00f4les", None))
        self.delete_admin.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.enregistrer_admin.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.label_119.setText(QCoreApplication.translate("MainWindow", u"Compte", None))
        self.admin_status.setText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.admin_change_status.setText(QCoreApplication.translate("MainWindow", u"Activate", None))
        self.label_128.setText(QCoreApplication.translate("MainWindow", u"R\u00e9inialisation du mot de passe", None))
        self.label_129.setText(QCoreApplication.translate("MainWindow", u"Mot de passe", None))
        self.label_130.setText(QCoreApplication.translate("MainWindow", u"Confirmer le mot de passe", None))
        self.reinitialiser_mot_de_passe.setText(QCoreApplication.translate("MainWindow", u"R\u00e9initialiser", None))
        self.add_student.setText(QCoreApplication.translate("MainWindow", u"Ajouter Etudiant", None))
        self.btn_importer_exel.setText(QCoreApplication.translate("MainWindow", u"Importer", None))
        self.btn_diplome.setText(QCoreApplication.translate("MainWindow", u"Diplome", None))
        self.btn_certificat.setText(QCoreApplication.translate("MainWindow", u"Certificat", None))
        self.btn_badge.setText(QCoreApplication.translate("MainWindow", u"Badge", None))
        self.sesrch_student.setPlaceholderText(QCoreApplication.translate("MainWindow", u"    Rechercher ...", None))
        self.prev_page_student.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9cedent", None))
        self.next_page_student.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.back_to_details.setText("")
        self.label_67.setText(QCoreApplication.translate("MainWindow", u"Inscription / Parcours", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Niveau / Cycle / Section", None))
        self.niveau_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Niveau", None))
        self.label_136.setText(QCoreApplication.translate("MainWindow", u"Dernier \u00e9tablissement fr\u00e9quent\u00e9", None))
        self.label_137.setText(QCoreApplication.translate("MainWindow", u"NISU", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.nom.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.prenom.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.sexe.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.telephone.setPlaceholderText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.adresse.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.email_3.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Date de naissance", None))
        self.date_de_naissance.setDisplayFormat(QCoreApplication.translate("MainWindow", u"d/M/yyyy", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Lieu de naissance", None))
        self.lieu_de_naissance.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Lieu de Naissance", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"Religion", None))
        self.religion.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Religion", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acad\u00e9mique", None))
        self.annee_academique_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acad\u00e9mique", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.classe_actuelle_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Aide financi\u00e8re", None))
        self.label_146.setText(QCoreApplication.translate("MainWindow", u"Facult\u00e9", None))
        self.faculte_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Faculte", None))
        self.suivant_1.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.personnel_info), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Personnes Responsable", None))
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.nom_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.prenom_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.email_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Couriel", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.adresse_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.telephone_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.label_46.setText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.sexe_responsable.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.back_1.setText(QCoreApplication.translate("MainWindow", u"Retourner", None))
        self.suivant_2.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.responsable_info), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Pieces Soumises", None))
        self.supprimer.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.type_de_document.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type de document", None))
        self.document_numero.setPlaceholderText(QCoreApplication.translate("MainWindow", u"num\u00e9ro du document", None))
        self.document_image.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Photo du document", None))
        self.chose_image.setText(QCoreApplication.translate("MainWindow", u"Choisir une Image", None))
        self.ajouter_document.setText(QCoreApplication.translate("MainWindow", u"Ajouter un document", None))
        self.back_2.setText(QCoreApplication.translate("MainWindow", u"Retourner", None))
        self.enregistre.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.pieces), QCoreApplication.translate("MainWindow", u"Page", None))
        self.search_student_for_detail.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rechercher un \u00e9tudiant", None))
        self.recu_inscrit.setText(QCoreApplication.translate("MainWindow", u"Re\u00e7u", None))
        self.imprimer_etudiant.setText(QCoreApplication.translate("MainWindow", u"Imprimer", None))
        self.modifier_etudiant.setText(QCoreApplication.translate("MainWindow", u"Modifier", None))
        self.supprimer_etudiant.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"    Informations personnels", None))
        self.label_100.setText(QCoreApplication.translate("MainWindow", u"Identifiant", None))
        self.label_101.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_102.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_103.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_104.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_105.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_114.setText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.label_115.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_112.setText(QCoreApplication.translate("MainWindow", u"Date de naissance: ", None))
        self.label_113.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_106.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_107.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_108.setText(QCoreApplication.translate("MainWindow", u"Courriel: ", None))
        self.label_109.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_110.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone:", None))
        self.label_111.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_157.setText(QCoreApplication.translate("MainWindow", u"Classe actuelle", None))
        self.label_158.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_116.setText(QCoreApplication.translate("MainWindow", u"Lieu de naissance: ", None))
        self.label_117.setText(QCoreApplication.translate("MainWindow", u"----", None))
        self.label_69.setText(QCoreApplication.translate("MainWindow", u"Informations sur le responsable", None))
        self.label_96.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_97.setText(QCoreApplication.translate("MainWindow", u"---", None))
        self.label_98.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_99.setText(QCoreApplication.translate("MainWindow", u"---", None))
        self.label_90.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_91.setText(QCoreApplication.translate("MainWindow", u"---", None))
        self.label_92.setText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.label_93.setText(QCoreApplication.translate("MainWindow", u"---", None))
        self.label_94.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.label_95.setText(QCoreApplication.translate("MainWindow", u"---", None))
        self.label_70.setText(QCoreApplication.translate("MainWindow", u"Pieces Soumises ", None))
        self.label_71.setText(QCoreApplication.translate("MainWindow", u"Parcours ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.details), QCoreApplication.translate("MainWindow", u"Page", None))
        self.search_for_deplome.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rechercher par Identifiant, nom ou pr\u00e9nom", None))
        self.search_for_certificat.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rechercher par Identifiant, nom ou pr\u00e9nom", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Niveau / Cycle / Section", None))
        self.niveau_for_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Niveau / Cycle / Section", None))
        self.label_120.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acd\u00e9mique", None))
        self.annee_for_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acd\u00e9mique", None))
        self.label_121.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.classe_for_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"classe", None))
        self.btn_for_promus.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.label_122.setText(QCoreApplication.translate("MainWindow", u"Niveau / Cycle / Section", None))
        self.niveau_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Niveau / Cycle / Section", None))
        self.label_123.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acd\u00e9mique", None))
        self.annee_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acd\u00e9mique", None))
        self.label_124.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.classe_promus.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.cancel_promus.setText(QCoreApplication.translate("MainWindow", u"Annuler", None))
        self.btn_promus.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.add_prof_button.setText(QCoreApplication.translate("MainWindow", u"Ajouter professeur", None))
        self.prof_prev.setText("")
        self.prof_label.setText("")
        self.prof_next.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Sexe", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"T\u00e9l\u00e9phone", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Mati\u00e8re enseign\u00e9e", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9nom", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Courriel", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.notif_prof.setText("")
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Notifier le prof", None))
        self.delete_prof.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.enregistrer_prof.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.label_118.setText(QCoreApplication.translate("MainWindow", u"Compte", None))
        self.prof_status.setText(QCoreApplication.translate("MainWindow", u"status", None))
        self.status_prof_change.setText(QCoreApplication.translate("MainWindow", u"Active", None))
        self.label_131.setText(QCoreApplication.translate("MainWindow", u"R\u00e9inialisation du mot de passe", None))
        self.label_132.setText(QCoreApplication.translate("MainWindow", u"Mot de passe", None))
        self.label_133.setText(QCoreApplication.translate("MainWindow", u"Confirmer le mot de passe", None))
        self.btn_reset_password_prof.setText(QCoreApplication.translate("MainWindow", u"R\u00e9initialiser", None))
        self.cours_stack.setText(QCoreApplication.translate("MainWindow", u"Cours", None))
        self.programme_stack.setText(QCoreApplication.translate("MainWindow", u"Programme", None))
        self.addCours.setText(QCoreApplication.translate("MainWindow", u"Ajouter Cours", None))
        self.prev_cours.setText(QCoreApplication.translate("MainWindow", u"Prev", None))
        self.next_cours.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.add_course_line.setText(QCoreApplication.translate("MainWindow", u"Ajouter une ligne", None))
        self.enregistrer_cours.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.addProgramme.setText(QCoreApplication.translate("MainWindow", u"Ajouter Programme", None))
        self.class_id.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.anneeId.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e", None))
        self.niveauId.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Cycle / S\u00e9ction", None))
        self.prev_programme.setText(QCoreApplication.translate("MainWindow", u"prev", None))
        self.next_programme.setText(QCoreApplication.translate("MainWindow", u"next", None))
        self.add_programme_line.setText(QCoreApplication.translate("MainWindow", u"Ajouter une ligne", None))
        self.enregistrer_programme.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.notes_dialog.setText(QCoreApplication.translate("MainWindow", u"Ajouter / Modifier note", None))
        self.bulletin_dialog.setText(QCoreApplication.translate("MainWindow", u"Bulletin", None))
        self.annee_for_bulletin.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acad\u00e9mique", None))
        self.mois_for_bulletin.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Mois", None))
        self.classe_for_bulletin.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.imprimer_bulletin.setText(QCoreApplication.translate("MainWindow", u"Imprimer", None))
        self.prev_notes.setText("")
        self.label_notes.setText("")
        self.next_notes.setText("")
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Cours / Mati\u00e8re:", None))
        self.affiche_cours.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_127.setText(QCoreApplication.translate("MainWindow", u"Classe - Ann\u00e9e", None))
        self.affiche_classe.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.label_138.setText(QCoreApplication.translate("MainWindow", u"Mati\u00e8re / Cours", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Evaluation / Examen", None))
        self.intra_button.setText(QCoreApplication.translate("MainWindow", u"Intra", None))
        self.finale_button.setText(QCoreApplication.translate("MainWindow", u"finale", None))
        self.paiement_dialog.setText(QCoreApplication.translate("MainWindow", u"Paiement", None))
        self.prev_paiement.setText("")
        self.label_paiement.setText("")
        self.next_paiement.setText("")
        self.imag_ilustrative.setText("")
        self.identifiant.setText("")
        self.fname.setText("")
        self.lname.setText("")
        self.classe_actuelle.setText("")
        self.btn_vente_back.setText(QCoreApplication.translate("MainWindow", u"Retourner", None))
        self.btn_vente_page.setText(QCoreApplication.translate("MainWindow", u"Vente", None))
        self.depense_btn.setText(QCoreApplication.translate("MainWindow", u"D\u00e9pense", None))
        self.loans.setText(QCoreApplication.translate("MainWindow", u"Pr\u00eats", None))
        self.autre_transaction.setText(QCoreApplication.translate("MainWindow", u"Autre transaction", None))
        self.prev_vente.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9c\u00e9dent", None))
        self.next_vente.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.vente_index), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.search_student_for_sell.setPlaceholderText(QCoreApplication.translate("MainWindow", u"rechercher un el\u00e8ve", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Nom du mat\u00e9riel", None))
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Cat\u00e9gorie", None))
        self.label_62.setText(QCoreApplication.translate("MainWindow", u"Quantit\u00e9", None))
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"Prit Unitaire", None))
        self.label_51.setText(QCoreApplication.translate("MainWindow", u"Prix Total", None))
        self.vente_status.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Status", None))
        self.delete_vente.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.ajouter_vente.setText(QCoreApplication.translate("MainWindow", u"Ajouter", None))
        self.imprimer_vente.setText(QCoreApplication.translate("MainWindow", u"Imprimer", None))
        self.label_63.setText(QCoreApplication.translate("MainWindow", u"Commande", None))
        self.label_commande_number.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_88.setText(QCoreApplication.translate("MainWindow", u"Total", None))
        self.label_total_commande.setText(QCoreApplication.translate("MainWindow", u"0 GDES", None))
        self.passer_la_commande.setText(QCoreApplication.translate("MainWindow", u"Passer La Commande", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.add_vente), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.accorder_un_pret.setText(QCoreApplication.translate("MainWindow", u"Accorder un pr\u00eat", None))
        self.faire_un_remboursement3.setText(QCoreApplication.translate("MainWindow", u"Retourner", None))
        self.prev_loans.setText(QCoreApplication.translate("MainWindow", u"Prev", None))
        self.next_loans.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_loans), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.label_161.setText(QCoreApplication.translate("MainWindow", u"Identifiant utilisateur / nom", None))
        self.label_162.setText(QCoreApplication.translate("MainWindow", u"Montant", None))
        self.label_163.setText(QCoreApplication.translate("MainWindow", u"Dur\u00e9e (en mois) ", None))
        self.label_164.setText(QCoreApplication.translate("MainWindow", u"Taux d\u2019int\u00e9r\u00eat", None))
        self.label_165.setText(QCoreApplication.translate("MainWindow", u"Paiement mensuel", None))
        self.label_166.setText(QCoreApplication.translate("MainWindow", u"Statut", None))
        self.label_169.setText(QCoreApplication.translate("MainWindow", u"Approuv\u00e9 par", None))
        self.label_168.setText(QCoreApplication.translate("MainWindow", u"Date d\u2019approbation", None))
        self.label_167.setText(QCoreApplication.translate("MainWindow", u"Date de d\u00e9blocage", None))
        self.label_170.setText(QCoreApplication.translate("MainWindow", u"Solde restant", None))
        self.label_171.setText(QCoreApplication.translate("MainWindow", u"Date de cr\u00e9ation", None))
        self.label_172.setText(QCoreApplication.translate("MainWindow", u"Derni\u00e8re mise \u00e0 jour", None))
        self.valider_loans.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_loans_form), QCoreApplication.translate("MainWindow", u"Page", None))
        self.label_179.setText(QCoreApplication.translate("MainWindow", u"Historique des paiements", None))
        self.label_173.setText(QCoreApplication.translate("MainWindow", u"Faire un remboursement", None))
        self.label_174.setText(QCoreApplication.translate("MainWindow", u"Paiement mensuel", None))
        self.label_176.setText(QCoreApplication.translate("MainWindow", u"Taux d\u2019int\u00e9r\u00eat", None))
        self.label_178.setText(QCoreApplication.translate("MainWindow", u"Methode de paiement", None))
        self.label_175.setText(QCoreApplication.translate("MainWindow", u"Montant \u00e0 payer", None))
        self.faire_un_remboursement.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
        self.tabWidget_4.setTabText(self.tabWidget_4.indexOf(self.tab_rembousement), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.loans_widget), QCoreApplication.translate("MainWindow", u"Page", None))
        self.label_185.setText(QCoreApplication.translate("MainWindow", u"Identitfiant", None))
        self.modal_identifiant.setText(QCoreApplication.translate("MainWindow", u"search", None))
        self.label_186.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.label_181.setText(QCoreApplication.translate("MainWindow", u"description suppl\u00e9mentaire", None))
        self.label_182.setText(QCoreApplication.translate("MainWindow", u"Montant", None))
        self.edit_transact.setText(QCoreApplication.translate("MainWindow", u"Modifier", None))
        self.delete_transact.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.save_transac.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.prev_transac.setText(QCoreApplication.translate("MainWindow", u"Prev", None))
        self.next_transac.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.transaction_page), QCoreApplication.translate("MainWindow", u"Page", None))
        self.label_125.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.label_126.setText(QCoreApplication.translate("MainWindow", u"Prix", None))
        self.enregistrer_depense.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.delete_depense.setText(QCoreApplication.translate("MainWindow", u"Supprimer", None))
        self.search_depense.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rechercher", None))
        self.prev_depense.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9c\u00e9dent", None))
        self.next_depense.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.depense), QCoreApplication.translate("MainWindow", u"Page", None))
        self.btn_permission_page.setText(QCoreApplication.translate("MainWindow", u"Permission", None))
        self.btn_role_page.setText(QCoreApplication.translate("MainWindow", u"Role", None))
        self.label_77.setText(QCoreApplication.translate("MainWindow", u"Nom", None))
        self.label_78.setText(QCoreApplication.translate("MainWindow", u"Email", None))
        self.label_79.setText(QCoreApplication.translate("MainWindow", u"Adresse", None))
        self.label_80.setText(QCoreApplication.translate("MainWindow", u"Telephone 1", None))
        self.label_81.setText(QCoreApplication.translate("MainWindow", u"Telephone 2", None))
        self.label_82.setText(QCoreApplication.translate("MainWindow", u"Logo", None))
        self.show_image.setText("")
        self.choise_profile_image.setText(QCoreApplication.translate("MainWindow", u"Choisir une image", None))
        self.valider_profile.setText(QCoreApplication.translate("MainWindow", u"Enregistrer", None))
        self.template_badge_1.setText(QCoreApplication.translate("MainWindow", u"Template badge 1", None))
        self.label_153.setText("")
        self.template_badge_2.setText(QCoreApplication.translate("MainWindow", u"Template badge 2", None))
        self.label_154.setText("")
        self.template_certificat.setText(QCoreApplication.translate("MainWindow", u"Template certificat", None))
        self.label_155.setText("")
        self.template_diplome.setText(QCoreApplication.translate("MainWindow", u"Template diplome", None))
        self.label_156.setText("")
        self.label_86.setText(QCoreApplication.translate("MainWindow", u"Permission", None))
        self.label_83.setText(QCoreApplication.translate("MainWindow", u"Roles", None))
        self.combo_roles.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Selectioner un role", None))
        self.label_84.setText(QCoreApplication.translate("MainWindow", u"Rechercher un utilisateur", None))
        self.recherche_user_permission.setText(QCoreApplication.translate("MainWindow", u"Rechercher", None))
        self.btn_modifier_permission.setText(QCoreApplication.translate("MainWindow", u"Modifier la permission", None))
        self.label_85.setText(QCoreApplication.translate("MainWindow", u"Role", None))
        self.label_87.setText(QCoreApplication.translate("MainWindow", u"Rechercher un utilisateur", None))
        self.recherche_user_role.setText(QCoreApplication.translate("MainWindow", u"Rechercher", None))
        self.btn_modifier_roles.setText(QCoreApplication.translate("MainWindow", u"Modifier le role", None))
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"- Rapport ", None))
        self.label_repport_type.setText(QCoreApplication.translate("MainWindow", u"Global", None))
        self.label_139.setText(QCoreApplication.translate("MainWindow", u"Choisir un type", None))
        self.label_43.setText(QCoreApplication.translate("MainWindow", u"D\u00e9but", None))
        self.global_date_debut.setDisplayFormat(QCoreApplication.translate("MainWindow", u"d/M/yyyy", None))
        self.label_44.setText(QCoreApplication.translate("MainWindow", u"Fin", None))
        self.global_date_fin.setDisplayFormat(QCoreApplication.translate("MainWindow", u"d/M/yyyy", None))
        self.global_rapport_imprimer.setText(QCoreApplication.translate("MainWindow", u"Imprimer", None))
        self.label_47.setText(QCoreApplication.translate("MainWindow", u"Rapports Administratifs ", None))
        self.label_55.setText(QCoreApplication.translate("MainWindow", u"- Rapport d'inscription des \u00e9l\u00e8ves", None))
        self.label_48.setText(QCoreApplication.translate("MainWindow", u"Cycle / Section / Niveau", None))
        self.label_53.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.label_54.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Ac.", None))
        self.label_56.setText(QCoreApplication.translate("MainWindow", u"Avec Identifiant", None))
        self.administrafif_identifiant.setText("")
        self.administratif_imprimer.setText(QCoreApplication.translate("MainWindow", u"Format PDF", None))
        self.format_excel_administratif.setText(QCoreApplication.translate("MainWindow", u"Format Excel", None))
        self.label_57.setText(QCoreApplication.translate("MainWindow", u"Rapports Financiers ", None))
        self.label_66.setText(QCoreApplication.translate("MainWindow", u"- Rapport des paiements des \u00e9l\u00e8ves", None))
        self.label_64.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.label_180.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e acad\u00e9mique", None))
        self.financier_annee_academique.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e acad\u00e9mique", None))
        self.label_58.setText(QCoreApplication.translate("MainWindow", u"D\u00e9but", None))
        self.date_debut_financier.setDisplayFormat(QCoreApplication.translate("MainWindow", u"d/M/yyyy", None))
        self.label_68.setText(QCoreApplication.translate("MainWindow", u"Fin", None))
        self.date_fin_financier.setDisplayFormat(QCoreApplication.translate("MainWindow", u"d/M/yyyy", None))
        self.label_65.setText(QCoreApplication.translate("MainWindow", u"Versement", None))
        self.financier_imprimer.setText(QCoreApplication.translate("MainWindow", u"Format PDF", None))
        self.format_excel_financier.setText(QCoreApplication.translate("MainWindow", u"Format Excel", None))
        self.label_143.setText(QCoreApplication.translate("MainWindow", u"Rapports p\u00e9dagogiques", None))
        self.label_140.setText(QCoreApplication.translate("MainWindow", u"- Rapport d\u2019\u00e9valuation Mensuel / Annuel", None))
        self.label_141.setText(QCoreApplication.translate("MainWindow", u"Cycle / Section / Niveau", None))
        self.label_142.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.label_177.setText(QCoreApplication.translate("MainWindow", u"Mois", None))
        self.label_144.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acad\u00e9mique", None))
        self.label_145.setText(QCoreApplication.translate("MainWindow", u"Avec Identifiant", None))
        self.pedagogique_identifiant.setText("")
        self.pedagogique_imprimer.setText(QCoreApplication.translate("MainWindow", u"Format PDF", None))
        self.format_excel_pedagogique.setText(QCoreApplication.translate("MainWindow", u"Format Excel", None))
        self.desicion_finale_exel.setText(QCoreApplication.translate("MainWindow", u"D. de fin d'ann\u00e9e (Excel)", None))
        self.desicion_finale.setText(QCoreApplication.translate("MainWindow", u"D. de fin d'ann\u00e9e ( PDF)", None))
        self.btn_param_paiement.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres paiement", None))
        self.btn_param_exam.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres d'Examen", None))
        self.btn_classe.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.btn_annee.setText(QCoreApplication.translate("MainWindow", u"Annee Acad\u00e9mique", None))
        self.btn_frais.setText(QCoreApplication.translate("MainWindow", u"Frais", None))
        self.btn_param_faculte.setText(QCoreApplication.translate("MainWindow", u"Facult\u00e9", None))
        self.btn_frais_divers.setText(QCoreApplication.translate("MainWindow", u"Frais divers", None))
        self.add_param_exam.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres des Examens", None))
        self.prev_param_exam.setText("")
        self.next_param_exam.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.ezam_params), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.add_paiement_params.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres des paiements", None))
        self.prev_paiement_params.setText("")
        self.next_paiement_params.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.paiement_params), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.add_year.setText(QCoreApplication.translate("MainWindow", u"Ann\u00e9e Acad\u00e9mique", None))
        self.prev_annee.setText("")
        self.next_annee.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.tab_annee), QCoreApplication.translate("MainWindow", u"Page", None))
        self.add_class.setText(QCoreApplication.translate("MainWindow", u"Classe", None))
        self.prev_class.setText("")
        self.next_class.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.tab_classe), QCoreApplication.translate("MainWindow", u"Page", None))
        self.add_faculte.setText(QCoreApplication.translate("MainWindow", u"Facult\u00e9 / Profession", None))
        self.prev_faculte.setText("")
        self.next_faculte.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.tab_faculte), QCoreApplication.translate("MainWindow", u"Page", None))
        self.add_frais.setText(QCoreApplication.translate("MainWindow", u"Frais d'inscription", None))
        self.prev_frais.setText("")
        self.next_frais.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.tab_frais), QCoreApplication.translate("MainWindow", u"Page", None))
        self.add_frais_divers.setText(QCoreApplication.translate("MainWindow", u"Frais divers", None))
        self.prev_frais_divers.setText("")
        self.next_frais_divers.setText("")
        self.tabWidget_params.setTabText(self.tabWidget_params.indexOf(self.tab_frais_divers), QCoreApplication.translate("MainWindow", u"Page", None))
        self.label_147.setText(QCoreApplication.translate("MainWindow", u"Model / Table", None))
        self.model_log.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Model / Table", None))
        self.label_148.setText(QCoreApplication.translate("MainWindow", u"Action", None))
        self.action_log.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Action", None))
        self.live_log.setText(QCoreApplication.translate("MainWindow", u"Console", None))
        self.prev_log.setText(QCoreApplication.translate("MainWindow", u"Pr\u00e9c\u00e9dent", None))
        self.next_log.setText(QCoreApplication.translate("MainWindow", u"Suivant", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.grafic_log), QCoreApplication.translate("MainWindow", u"Tab 1", None))
        self.label_149.setText(QCoreApplication.translate("MainWindow", u"Model / Table", None))
        self.model_log_console.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Model /Table", None))
        self.label_150.setText(QCoreApplication.translate("MainWindow", u"Action", None))
        self.action_log_console.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Action", None))
        self.log_grafic.setText(QCoreApplication.translate("MainWindow", u"Graphique", None))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.console_log), QCoreApplication.translate("MainWindow", u"Tab 2", None))
        self.label_184.setText("")
        self.label_183.setText(QCoreApplication.translate("MainWindow", u"Version 1.0.1", None))
        self.label_expiration_date.setText("")
    # retranslateUi

