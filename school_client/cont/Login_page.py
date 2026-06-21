# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login_page.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(640, 594)
        Dialog.setStyleSheet(u"QDialog{background: transparent}\n"
"#Dialog{background: transparent}\n"
"#widget{background: #444}\n"
"\n"
"QWidget,QFrame, #frame,frame{\n"
"background: transparent;\n"
"}\n"
"#label_connect_4{color:#c1c1c1;font-size:13pt}\n"
"\n"
"\n"
"#label_75{\n"
"font-size:14pt;\n"
"color:#eb983f\n"
"}\n"
"\n"
"QLabel{\n"
"font-size:14pt;\n"
"color:#4b5563\n"
"}\n"
" \n"
"#show_frame_ip{color:#4b5563}\n"
"#show_frame_ip:hover{color:#228BE6}\n"
"#show_frame_ip:checked{color:red}\n"
"\n"
"\n"
"#header_connexion_error{\n"
"    border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"border-bottom:1px solid #c1c1c1;\n"
"background-color:#222\n"
"}\n"
"\n"
"\n"
"\n"
"QLineEdit,\n"
"QComboBox,\n"
"QDateEdit {\n"
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
"\n"
"#valider_id_server {\n"
"    border: 1px sol"
                        "id #1266f1;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #1266f1;\n"
"    width: 50px\n"
"}\n"
"\n"
"#btn_connexion:hover {\n"
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
"    background-color: #f74a4a;\n"
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
"#btn_connexion,\n"
"#valider_prog,\n"
"#modifier_prog {\n"
"    border: 1px solid #1266f1;\n"
"    padding: 4px;\n"
"    border-radius: 5px;\n"
"    color: #1266f1;\n"
"    width: 50px\n"
"}\n"
"\n"
"\n"
"#valider_id_server:hover {\n"
"    border: 1px solid #1266f1;\n"
"    background-color: #1266f1;\n"
"    padding: 4px;\n"
"    borde"
                        "r-radius: 5px;\n"
"    color: #fff;\n"
"    width: 50px\n"
"}\n"
"\n"
"\n"
"#label_57 {\n"
"    color: #951d32;\n"
"}\n"
"\n"
"\n"
"QComboBox,QLineEdit,QDateEdit {\n"
"                background-color: white;\n"
"                color: black;\n"
"                border: 1px solid #ccc;\n"
"                border-radius:5px;\n"
"                padding: 5px;\n"
"min-height:25px;\n"
"max-height:25px; \n"
"            }\n"
"QCheckBox{\n"
"  background-color: white;\n"
"                color: black;\n"
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
"            QComboBox"
                        ":disabled {\n"
"                background-color: #afafaf;  /* Gris clair */\n"
"                color: #f0f0f0;  /* Texte gris\u00e9 */\n"
"                border: 1px solid #dcdcdc;\n"
"            }\n"
"\n"
"")
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.header_connexion_error = QWidget(self.widget)
        self.header_connexion_error.setObjectName(u"header_connexion_error")
        self.header_connexion_error.setMaximumSize(QSize(16777215, 42))
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
        self.horizontalLayout_163.setContentsMargins(9, 0, 0, 0)
        self.frame_223 = QFrame(self.frame_222)
        self.frame_223.setObjectName(u"frame_223")
        self.frame_223.setFrameShape(QFrame.StyledPanel)
        self.frame_223.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_164 = QHBoxLayout(self.frame_223)
        self.horizontalLayout_164.setObjectName(u"horizontalLayout_164")
        self.horizontalLayout_164.setContentsMargins(0, 0, 0, -1)

        self.horizontalLayout_163.addWidget(self.frame_223)

        self.frame_227 = QFrame(self.frame_222)
        self.frame_227.setObjectName(u"frame_227")
        self.frame_227.setMinimumSize(QSize(430, 0))
        self.frame_227.setFrameShape(QFrame.StyledPanel)
        self.frame_227.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_165 = QHBoxLayout(self.frame_227)
        self.horizontalLayout_165.setObjectName(u"horizontalLayout_165")
        self.horizontalLayout_165.setContentsMargins(0, 0, 0, 0)
        self.label_connect_4 = QLabel(self.frame_227)
        self.label_connect_4.setObjectName(u"label_connect_4")
        font = QFont()
        font.setPointSize(13)
        font.setBold(False)
        self.label_connect_4.setFont(font)

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


        self.horizontalLayout_87.addWidget(self.frame_222, 0, Qt.AlignHCenter)


        self.verticalLayout_2.addWidget(self.header_connexion_error)

        self.body_connect = QWidget(self.widget)
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
        font1 = QFont()
        font1.setPointSize(14)
        font1.setBold(True)
        self.label_49.setFont(font1)

        self.horizontalLayout_152.addWidget(self.label_49, 0, Qt.AlignHCenter)


        self.verticalLayout_68.addWidget(self.title_3)

        self.frame_130 = QFrame(self.frame_129)
        self.frame_130.setObjectName(u"frame_130")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_130.sizePolicy().hasHeightForWidth())
        self.frame_130.setSizePolicy(sizePolicy)
        self.frame_130.setMinimumSize(QSize(500, 0))
        self.frame_130.setMaximumSize(QSize(700, 16777215))
        self.frame_130.setFrameShape(QFrame.StyledPanel)
        self.frame_130.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_153 = QHBoxLayout(self.frame_130)
        self.horizontalLayout_153.setSpacing(20)
        self.horizontalLayout_153.setObjectName(u"horizontalLayout_153")
        self.horizontalLayout_153.setContentsMargins(0, 0, 0, 0)
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
        palette = QPalette()
        brush = QBrush(QColor(75, 85, 99, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush1)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush)
#endif
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush)
#endif
        self.error_message.setPalette(palette)
        self.error_message.setFont(font1)

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
        font2 = QFont()
        font2.setPointSize(14)
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
        font3 = QFont()
        font3.setPointSize(13)
        self.show_frame_ip.setFont(font3)
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
        self.input_change_ip.setFont(font3)

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
        self.change_ip.setFont(font3)
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
        self.btn_connexion = QPushButton(self.frame_button_3)
        self.btn_connexion.setObjectName(u"btn_connexion")
        self.btn_connexion.setEnabled(True)
        font4 = QFont()
        font4.setPointSize(13)
        font4.setBold(True)
        self.btn_connexion.setFont(font4)
        self.btn_connexion.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_connexion.setFlat(True)

        self.horizontalLayout_157.addWidget(self.btn_connexion)


        self.verticalLayout_69.addWidget(self.frame_button_3)


        self.horizontalLayout_153.addWidget(self.form_3)


        self.verticalLayout_68.addWidget(self.frame_130)


        self.horizontalLayout_151.addWidget(self.frame_129)


        self.verticalLayout_3.addWidget(self.connexion_3, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_2.addWidget(self.body_connect)


        self.verticalLayout.addWidget(self.widget)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_connect_4.setText(QCoreApplication.translate("Dialog", u"Application de gestion des \u00e9coles", None))
        self.label_74.setText("")
        self.min_error.setText("")
        self.close_error.setText("")
        self.label_49.setText(QCoreApplication.translate("Dialog", u"Connexion", None))
        self.error_message.setText("")
        self.email_2.setText("")
        self.email_2.setPlaceholderText(QCoreApplication.translate("Dialog", u"Email", None))
        self.password_2.setPlaceholderText(QCoreApplication.translate("Dialog", u"Password", None))
        self.show_frame_ip.setText(QCoreApplication.translate("Dialog", u"show ip", None))
        self.label_76.setText(QCoreApplication.translate("Dialog", u"Modifier l'ip", None))
        self.change_ip.setText(QCoreApplication.translate("Dialog", u"Modifier", None))
        self.btn_connexion.setText(QCoreApplication.translate("Dialog", u"Valider", None))
    # retranslateUi

