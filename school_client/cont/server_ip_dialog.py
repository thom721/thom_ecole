# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'server_ip_dialog.ui'
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
"\n"
"#valider_id_server:hover {\n"
"    border: 1px solid #1266f1;\n"
"    background-color: #1266f1;\n"
"    padding: 4px;"
                        "\n"
"    border-radius: 5px;\n"
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
"       "
                        "     QComboBox:disabled {\n"
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
        self.verticalLayout_2.setSpacing(19)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.header_connexion_error = QWidget(self.widget)
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

        self.frame_27 = QFrame(self.widget)
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
        self.verticalLayout_204.setContentsMargins(9, 9, -1, -1)
        self.frame_232 = QFrame(self.frame_27)
        self.frame_232.setObjectName(u"frame_232")
        self.frame_232.setFrameShape(QFrame.StyledPanel)
        self.frame_232.setFrameShadow(QFrame.Raised)
        self.verticalLayout_207 = QVBoxLayout(self.frame_232)
        self.verticalLayout_207.setSpacing(15)
        self.verticalLayout_207.setObjectName(u"verticalLayout_207")
        self.verticalLayout_207.setContentsMargins(0, 0, 0, 0)
        self.frame_233 = QFrame(self.frame_232)
        self.frame_233.setObjectName(u"frame_233")
        self.frame_233.setFrameShape(QFrame.StyledPanel)
        self.frame_233.setFrameShadow(QFrame.Raised)
        self.verticalLayout_208 = QVBoxLayout(self.frame_233)
        self.verticalLayout_208.setObjectName(u"verticalLayout_208")
        self.verticalLayout_208.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.frame_233)
        self.label.setObjectName(u"label")

        self.verticalLayout_208.addWidget(self.label)

        self.server_ip = QLineEdit(self.frame_233)
        self.server_ip.setObjectName(u"server_ip")
        self.server_ip.setMinimumSize(QSize(500, 37))
        font1 = QFont()
        font1.setPointSize(13)
        self.server_ip.setFont(font1)

        self.verticalLayout_208.addWidget(self.server_ip)


        self.verticalLayout_207.addWidget(self.frame_233)

        self.frame_234 = QFrame(self.frame_232)
        self.frame_234.setObjectName(u"frame_234")
        self.frame_234.setFrameShape(QFrame.StyledPanel)
        self.frame_234.setFrameShadow(QFrame.Raised)
        self.verticalLayout_209 = QVBoxLayout(self.frame_234)
        self.verticalLayout_209.setSpacing(0)
        self.verticalLayout_209.setObjectName(u"verticalLayout_209")
        self.verticalLayout_209.setContentsMargins(0, 0, 0, 0)
        self.valider_id_server = QPushButton(self.frame_234)
        self.valider_id_server.setObjectName(u"valider_id_server")
        self.valider_id_server.setMinimumSize(QSize(110, 0))
        font2 = QFont()
        font2.setPointSize(14)
        font2.setBold(True)
        self.valider_id_server.setFont(font2)
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
        font3 = QFont()
        font3.setPointSize(14)
        self.label_75.setFont(font3)
        self.label_75.setWordWrap(True)

        self.verticalLayout_206.addWidget(self.label_75)


        self.verticalLayout_205.addWidget(self.frame_231)


        self.verticalLayout_204.addWidget(self.frame_229, 0, Qt.AlignHCenter|Qt.AlignVCenter)


        self.verticalLayout_2.addWidget(self.frame_27)


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
        self.label.setText(QCoreApplication.translate("Dialog", u"Adresse ip du server", None))
        self.valider_id_server.setText(QCoreApplication.translate("Dialog", u"Valider", None))
        self.gif_animate.setText(QCoreApplication.translate("Dialog", u"TextLabel", None))
        self.label_75.setText(QCoreApplication.translate("Dialog", u"Le service est temporairement indisponible. Veuillez r\u00e9essayer ult\u00e9rieurement. Si le probl\u00e8me persiste, contactez notre support technique.", None))
    # retranslateUi

