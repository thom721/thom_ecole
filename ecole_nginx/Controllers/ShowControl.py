import sys
import os
import requests
import subprocess
from functools import partial
from PySide6.QtGui import QColor,QIcon,QCursor
# from PySide6.QtGui import 

from PySide6.QtCore import Qt,QTimer
from datetime import datetime, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,QGraphicsDropShadowEffect,QFrame,QGroupBox,QCheckBox,QScrollArea, QSystemTrayIcon, QMenu,QApplication,QLineEdit,QDialog
from PySide6.QtCore import QSettings
from PySide6.QtGui import QPixmap
from Helper.Ip_manager import Ip_manager
from Helper.Ip_manager import Ip_manager
from Helper.server_key_generate import get_mac_address,verify_activation_key_graphic,is_license_valid
from PySide6.QtGui import QAction

class ServiceControlWindow(QWidget):
    def __init__(self, base__url = None):
        super().__init__()
        self.setWindowTitle("Gestion des Services")
        self.setGeometry(100, 100, 600, 640)

        self.setWindowFlags(Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground,False) 
        # self.setWindowOpacity(1)
        self.token_access = None
        # self.setStyleSheet("background-color: #2E2E2E; color: white; border-radius: 0px;") 
        self.base__url= base__url
        self.setStyleSheet("""

                          QWidget{background-color: #2E2E2E; color: white; border-radius: 10px;}
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

    """)
     
 
        self.old_pos = None  
        self.services = ["MySQLEcole", "ApacheEcole"]  
        self.service_buttons = {}
        self.title_bar = QWidget()
        self.widget = QWidget()
        
 

        shadow = QGraphicsDropShadowEffect()
        shadow.setOffset(15, 15)  
        shadow.setBlurRadius(30)  
        shadow.setColor(QColor(2, 6, 0, 150))  
        self.widget.setGraphicsEffect(shadow)

        # self.ajouter_au_demarrage("école-server")


# ================================================MINIMIZE=========================================
        self.icon_path_logo = self.get_resource_path(os.path.join('Controllers', 'favicon.ico'))
 
        self.tray_icon = QSystemTrayIcon(QIcon(self.icon_path_logo), parent=self)
        self.tray_icon.setToolTip("Server Gestion d'école")

        # Menu contextuel de l'icône (clic droit)
        self.tray_menu = QMenu(self)

        show_action = QAction("Afficher", self)
        quit_action = QAction("Quitter", self)

        show_action.triggered.connect(self.show_window)
        quit_action.triggered.connect(self.shutDownAll)

        self.tray_menu.addAction(show_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(self.tray_menu)
        # menu.exec_(table_widget.mapToGlobal(pos))
        

        # Clic sur l'icône (clic gauche)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Affiche l'icône
        self.tray_icon.show()
    
    def shutDownAll(self):
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment fermer toutes les services en cours?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes: 
            for service in self.services:
                print(f"service   {service}")
                # self.get_service_status(service)
                subprocess.run(["net", "stop", service], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
            QApplication.quit

    def show_window(self):
        # self.hide()
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        """Lorsqu'on ferme la fenêtre, on la cache et on affiche un message."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application réduite",
            "L'application continue de s'exécuter en arrière-plan.",
            QSystemTrayIcon.Information,
            3000
        )


    def on_tray_icon_activated(self, reason):
        """Gère les interactions avec l'icône de la barre système"""
        if reason == QSystemTrayIcon.Trigger:  # Clic gauche
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
        elif reason == QSystemTrayIcon.DoubleClick:  # Double-clic
            self.show_window()
        elif reason == QSystemTrayIcon.Context:  # Clic droit
            # Le menu contextuel s'affichera automatiquement grâce à setContextMenu
            pass

 #=================================================================================================

     #    self.init_ui()
    def get_resource_path(self, relative_path: str) -> str:
        """Retourne le chemin absolu d'une ressource, adapté à PyInstaller."""
        if getattr(sys, 'frozen', False):
            # Chemin dans le contexte temporaire de PyInstaller
            base_path = sys._MEIPASS
        else:
            # Chemin normal (lors de l'exécution en script)
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    

    def ajouter_au_demarrage(self, nom_app: str = "école-server"):
        startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")

        chemin_script = sys.argv[0]
        
        # Si tu utilises un .exe compilé (via PyInstaller), prends ce chemin-là
        if getattr(sys, 'frozen', False):
            chemin_executable = sys.executable
        else:
            # Sinon, on utilise le script Python directement
            chemin_executable = chemin_script

        raccourci_path = os.path.join(startup_dir, f"{nom_app}.bat")

        with open(raccourci_path, "w") as f:
            f.write(f'start "" "{chemin_executable}"')
 

    
    def init_ui(self, services,url,client_data = None, base_url =None):
        """Initialisation de l'interface."""
        layout = QVBoxLayout(self.widget)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 0, 10, 20)        

        
        
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #1C1C1C;")  
        self.title_bar.move(0, 0)

        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(10, 0, 10, 0)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel("Gestion des Services")
        title_label.setStyleSheet("color: white; font-size: 14pt; font-weight: bold;")
        title_layout.addWidget(title_label)

        #
        minimize_button = QPushButton()

        minimize_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 13pt;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: yellow;
            }
        """)
        minimize_button.setFixedSize(35, 35)
        min_icon = os.path.join(self.get_resource_path('Controllers'), 'min_w.png')
        icon = QIcon(min_icon)  
        minimize_button.setIcon(icon)
        minimize_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_button)
 
       
        close_button = QPushButton()
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 12pt;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                color: red;
                                   
            }
        """)
        close_button.setFixedSize(35, 35)

        close_icon = os.path.join(self.get_resource_path('Controllers'), 'close_w.png')
        icon = QIcon(close_icon)  
        close_button.setIcon(icon)

        close_button.clicked.connect(self.confirm_close)
        title_layout.addWidget(close_button)

        self.title_bar.setLayout(title_layout)
        layout.addWidget(self.title_bar)

        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(6, 9, 6, 9)
        body_layout.setSpacing(10)
        body_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.authorization(body_layout,client_data,url)

        groupe_box = QGroupBox("Services")

        groupe_box.setStyleSheet("""
                                 QLabel{font-size:12pt}
            QGroupBox {
                font-size: 12pt;
                color: #333;
                border: 1px solid #777;
                border-radius: 5px;
                margin-top: 15px;
                padding: 5px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0px;
                color: #0078D7;
            }
        """)

        main_layout = QVBoxLayout(groupe_box)
        main_layout.setSpacing(0)
        self.attach_php(main_layout)

        body_layout.addWidget(groupe_box)

        # Liste des services avec leurs boutons ON/OFF
        v_layout_service = QVBoxLayout()
        v_layout_service.setSpacing(0)
        v_layout_service.setContentsMargins(0, 0, 0, 0)
        for service in services:
            service_layout = QHBoxLayout()
            service_layout.setContentsMargins(2, 0, 2, 0)
            service_label = QLabel("Service MySQL" if service == "MySQLEcole" else "Service Apache")
            service_label.setStyleSheet("font-size: 14pt; padding: 7px;")  # 🔹 Texte blanc, sans fond
            service_layout.addWidget(service_label)

            # Vérifier l'état du service
            status = self.get_service_status(service)
            toggle_button = QPushButton("ON" if status else "OFF")
            toggle_button.setCheckable(True)
            toggle_button.setChecked(status)
            toggle_button.setStyleSheet(self.get_button_style(status))
            toggle_button.clicked.connect(lambda checked, s=service, b=toggle_button: self.toggle_service(s, b, checked))

            self.service_buttons[service] = toggle_button
            service_layout.addWidget(toggle_button)
            v_layout_service.addLayout(service_layout)


        self.fram_activate =  QFrame()
        self.layout_ = QVBoxLayout(self.fram_activate)
        self.label = QLabel("Entrez votre clé d'activation :")
        self.key_input = QLineEdit()
        self.btn_verify = QPushButton("Vérifier la clé")
        self.btn_verify.setCursor(Qt.PointingHandCursor)

        self.btn_verify.setStyleSheet("""
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
        
        # self.btn_verify.clicked.connect(lambda url=base_url: self.verifier_cle(url)) 
        url_copy = base_url  # pour geler la valeur
        self.btn_verify.clicked.connect(lambda: self.verifier_cle(url_copy))
         

        self.layout_.addWidget(self.label)
        self.layout_.addWidget(self.key_input)
        self.layout_.addWidget(self.btn_verify)

        main_layout.addLayout(v_layout_service)
        layout.addLayout(body_layout)
        if not is_license_valid():
            layout.addWidget(self.fram_activate)
        self.setLayout(layout)

    def verifier_cle(self, url):
        user_input_key = self.key_input.text().strip()
        mac = get_mac_address()  # Exemple: "4CCC6A3FA142"  '84:a6:c8:f3:d5:bc'#
        expiration_date = 30
        # user_input_key = "ABCD-EFGH-IJKL-MNOP"
        if verify_activation_key_graphic(provided_key=user_input_key, mac_address=mac, days=expiration_date, url=url):
            expiration_date_ =(datetime.utcnow() + timedelta(days=expiration_date)).strftime("%Y-%m-%d") #datetime.utcnow() + timedelta(days=expiration_date).strftime("%Y-%m-%d")
            # self.fram_activate.setHidden(True)
            QMessageBox.information(self, "Succès", f"Clé valide. Expire le {expiration_date_}")
            print(f"✅ Clé valide. mac {mac}")
        else:
            QMessageBox.critical(self, "Erreur", "Clé invalide ou expirée.")
            print(f"❌ Clé invalide. mac {mac}") 

    def get_service_status(self, service_name):
        """Vérifie si un service est en cours d'exécution."""
        try:
            result = subprocess.run(["sc", "query", service_name], capture_output=True, text=True)
          #   print(result)
            return "RUNNING" in result.stdout
        except Exception:
            return False  # Si erreur, considérer comme arrêté

    def toggle_service(self, service_name, button, checked):
        """Démarre ou arrête un service."""
        if checked:
            subprocess.run(["net", "start", service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            button.setText("ON")
        else:
            subprocess.run(["net", "stop", service_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            button.setText("OFF")

        # Mettre à jour le style du bouton
        button.setStyleSheet(self.get_button_style(checked))

    def get_button_style(self, active):
        """Retourne le style du bouton ON/OFF sans transition."""
        return """
            QPushButton {
                border-radius: 8px;
                padding: 5px;
                font-size: 13pt;
                color: %s;
            }
            QPushButton:checked {
               color: %s;
               font-weight: bold;
            }
        """ % ("#ff4d4d" if not active else "#4CAF50", "#4CAF50" if active else "#ff4d4d")
          
    def confirm_close(self):
        """Affiche une boîte de dialogue pour confirmer la fermeture."""
        reply = QMessageBox.question(self, "Confirmation", "Voulez-vous vraiment fermer l'application ?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    # Permettre le déplacement de la fenêtre en cliquant sur la barre de titre
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 40:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def attach_php(self, layouts):
        """Initialisation de l'interface."""

        self.server_label = QLabel()

        layouts.addWidget(self.server_label)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.start_button = QPushButton("Démarrer")
        self.stop_button = QPushButton("Arrêter")
        if not self.is_php_running():
            self.buttons_layout.setContentsMargins(9,0,9,0)
            self.start_button.setStyleSheet("color: #4CAF50; font-size: 13pt; padding: 5px; border-radius: 5px;")
            self.stop_button.setHidden(True)
            self.start_button.clicked.connect(self.start_php)
            self.buttons_layout.addWidget(self.start_button)
        else:
            self.stop_button.setStyleSheet("color: #FF4D4D; font-size: 13pt; padding: 5px; border-radius: 5px;")
            self.start_button.setHidden(True)
            self.stop_button.clicked.connect(self.stop_php)
            self.buttons_layout.addWidget(self.stop_button)

        layouts.addLayout(self.buttons_layout)

        self.update_php_status()

    def is_php_running(self, port=8080):
        """Vérifie si PHP fonctionne sur le port donné."""
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            return f":{port}" in result.stdout
        except Exception:
            return False

    def update_php_status(self):
        """Mise à jour du texte et de la couleur du label selon l'état du serveur PHP."""
        if self.is_php_running():
            self.server_label.setText("Le server est en cours d'exécution")
            self.server_label.setStyleSheet("color: #4CAF50; font-size: 14pt; ")
            self.start_button.setEnabled(False)  # Désactive le bouton Démarrer
            self.stop_button.setEnabled(True)  # Active le bouton Arrêter
        else:
            self.server_label.setText("Le server est arrêté")
            self.server_label.setStyleSheet("color: #FF4D4D; font-size: 13pt;")
            self.start_button.setEnabled(True)  # Active le bouton Démarrer
            self.stop_button.setEnabled(False)  # Désactive le bouton Arrêter

    def start_php(self):
        """Démarre le serveur PHP."""
        try:
            cwds=os.path.join(os.getcwd(), 'nginx','html','api')
            process = subprocess.Popen(
                    ["php", "artisan", "serve", "--host", Ip_manager().get_server_ip(), "--port", "8080"],
                    cwd=cwds, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
                )
                    # Écrit le PID dans un fichier
            with open("php_server.pid", "w") as pid_file:
                pid_file.write(str(process.pid))
                self.update_php_status()  # Met à jour l'état après le démarrage
        except Exception as e:
            print(f"Erreur lors du démarrage de PHP: {e}")

    def stop_php(self):
        """Arrête le serveur PHP."""
        try:
            if os.path.exists("php_server.pid"):
                with open("php_server.pid", "r") as pid_file:
                    pid = pid_file.read().strip()

                subprocess.run(["taskkill", "/PID", pid, "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove("php_server.pid")
                self.update_php_status()
            else:
                print("Aucun fichier PID trouvé. Le serveur n'a peut-être pas été lancé depuis cette app.")
        except Exception as e:
            print(f"Erreur lors de l'arrêt du serveur PHP artisan: {e}")



    def authorization(self, layout, client_data, url):
        groupe_box = QGroupBox("Client Authorization")
        groupe_box.setStyleSheet("""
                                  QLabel{font-size:12pt}
            QGroupBox {
                font-size: 12pt;
                color: #333;
                border: 1px solid #777;
                border-radius: 5px;
                margin-top: 15px;
                padding: 4px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 0px;
                color: #0078D7;
            }
        """)

        main_layout = QVBoxLayout(groupe_box)
        main_layout.setContentsMargins(2, 0, 2, 0)
        self.status_label = QLabel("")
        # main_layout.addWidget(self.status_label)
        
        # Section de contrôle refresh
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        # Bouton refresh manuel
        self.btn_manual_refresh = QPushButton("Manual Refresh")
        self.btn_manual_refresh.setStyleSheet("font-size: 12pt; padding: 4px;")
        self.btn_manual_refresh.clicked.connect(lambda: self.refresh_client_data(url))
        
        # Contrôle auto-refresh
        self.auto_refresh_toggle = QCheckBox("Auto Refresh (30s)")
        self.auto_refresh_toggle.setStyleSheet("font-size: 12pt;")
        self.auto_refresh_toggle.stateChanged.connect(self.toggle_auto_refresh)

        self.auto_refresh_toggle.setStyleSheet("""
            QCheckBox {
                font-size: 12pt;
                color: #999;
            }
            QCheckBox::indicator:checked {
                background-color: #0078D7;
                border: 1px solid #fff;
            }
                                               
            QCheckBox::indicator:unchecked {
                background-color: #fff;
                border: 1px solid #777;
            }
        """)

        self.btn_manual_refresh.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
                padding: 6px 12px;
                font-size: 12pt;
                width:150px
            }
                                              
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)

        
        control_layout.addWidget(self.btn_manual_refresh)
        control_layout.addStretch()
        control_layout.addWidget(self.status_label)
        control_layout.addStretch()
        control_layout.addWidget(self.auto_refresh_toggle)
        
        # Zone des clients
        self.client_scroll = QScrollArea()
        self.client_widget = QWidget()
        self.client_layout = QVBoxLayout(self.client_widget)
        self.client_layout.setContentsMargins(10,0,0,10)
        self.client_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.client_layout.setSpacing(2)
        # self.client_widget.setStyleSheet("""background:#444;border-bottom:1px solid #555""")
        
        self.client_scroll.setWidgetResizable(True)
        self.client_scroll.setWidget(self.client_widget)
        
        main_layout.addWidget(control_frame)
        main_layout.addWidget(self.client_scroll)
        
        # Timer pour auto-refresh
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.setInterval(30000)  # 30 secondes
        self.auto_refresh_timer.timeout.connect(lambda: self.refresh_client_data(url))
        
        self.populate_clients(client_data, url)
        
        layout.addWidget(groupe_box)


    def populate_clients(self, client_data, url):
        # Nettoyer l'ancien contenu
        for i in reversed(range(self.client_layout.count())): 
            self.client_layout.itemAt(i).widget().setParent(None)
        
        if client_data:
            for client in client_data:
                client_frame = QFrame()
                # client_frame.setFixedHeight(60)
                # client_frame.setStyleSheet("background:#555;border-radius:7px")
                frame_layout = QHBoxLayout(client_frame)
                frame_layout.setContentsMargins(0,0,0,3)
                frame_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

                # Info client
                info_layout = QVBoxLayout()
                info_layout.setContentsMargins(0,0,0,0)
                info_layout.setSpacing(0)
                label_name = QLabel(client.get("client_name", "Unknown Device"))
                label_mac = QLabel(client.get("client_mac", "00:00:00:00:00:00"))
                
                label_name.setStyleSheet("font-size: 13pt; font-weight: bold;")
                label_mac.setStyleSheet("font-size: 12pt; color: #999;height:20px")
                
                info_layout.addWidget(label_name)
                info_layout.addWidget(label_mac)
                
                # Bouton d'autorisation
                btn_auth = QPushButton()
                btn_auth.setCheckable(True)
                btn_auth.setChecked(client.get('authorisation', 0) == 1)
                self.update_auth_button_style(btn_auth)
                
                btn_auth.clicked.connect(partial(
                    self.toggle_authorization,
                    client.get("id"),
                    url,
                    btn_auth
                ))
                
                frame_layout.addLayout(info_layout)
                frame_layout.addWidget(btn_auth)
                
                self.client_layout.addWidget(client_frame)

    def toggle_authorization___(self, client_id, url, button):
        new_state = int(button.isChecked())
        
        # Appel API pour modifier l'état
        try:
            response = requests.post(
                url,
                json={"client_id": client_id, "state": new_state},
                timeout=5
            )
            
            if response.status_code == 200:
                self.update_auth_button_style(button)
            else:
                button.setChecked(not new_state)
                self.show_error_message("Update failed")
                
        except Exception as e:
            print(f"API Error: {str(e)}")
            button.setChecked(not new_state)

    def update_auth_button_style(self, button):
        state = "Authorized" if button.isChecked() else "Blocked"
        color = "#4CAF50" if button.isChecked() else "#F44336"
        
        button.setText(state)
        button.setStyleSheet(f"""
            QPushButton {{
                font-size: 12pt;
                min-width: 80px;
                padding: 6px;
                color: white;
                background-color: {color};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {color}AA;
            }}
        """)


    def toggle_auto_refresh(self, state):
        if self.auto_refresh_toggle.isChecked():
            self.auto_refresh_timer.start()
            self.btn_manual_refresh.setEnabled(False)
            self.status_label.setText("🔄 Auto-refresh activé")
        else:
            self.auto_refresh_timer.stop()
            self.btn_manual_refresh.setEnabled(True)
            self.status_label.setText("⏸️ Auto-refresh désactivé")

        #QTimer.singleShot(113000, lambda: self.status_label.setText(""))  # Efface le message après 3s


    def refresh_client_data(self, url):
        try:
            data = requests.get(url, timeout=15)
            response_data = data.json()
            if data.status_code == 200:
                print(data.json())
                client_data = response_data['data_client']
                self.populate_clients(client_data, url)
            else:
                self.show_error_message("Refresh failed")
        except Exception as e:
            print(f"Refresh error: {str(e)}")
            self.show_error_message("Connection error")

    def show_error_message(self, text):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(text)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()


    def toggle_authorization(self, client_id, url, button):
        payload = {"id": client_id}
        if self.token_access:
            headers['X-Admin-Token'] = self.token_access
            print(f"token_access   {self.token_access}")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response_data = response.json()

            if response.status_code == 200:
                # Nouvelle autorisation renvoyée par l'API
                new_status = response_data.get('authorisation', 0)
                if new_status == 1:
                    self.update_auth_button_style(button)
                else:
                    button.setText("Not Authorized")
                    button.setStyleSheet("""
                        QPushButton {
                            font-size: 12pt;
                            color: white;
                            background-color: red;
                            border: none;
                            padding: 6px 12px;
                            border-radius: 5px;
                        }
                    """)
                return response_data
            if response.status_code == 422:
                if response_data and "Authorization" in response_data and response_data["Authorization"] == False:
                    self.request_access_for_delete()
            else: 
                # button.setChecked(not new_state)
                self.show_error_message("Update failed")
                print("Erreur:", response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")


    def request_access_for_delete(self):
        self.dialog_delete = QDialog()
        self.dialog_delete.setModal(True) 
        self.dialog_delete.setWindowTitle("Confirmation requise")
        self.dialog_delete.setStyleSheet("""
  QDialog {
            background: #fff;
        }
                                                  QComboBox, QLineEdit, QDateEdit{ width: 350px; min-height: 33px; max-height: 33px;border: 1px solid #999; border-radius:5px;padding-left:7px}
                                                QComboBox:hover,QComboBox:focus, QLineEdit:hover, QDateEdit:hover, QLineEdit:focus, QDateEdit:focus {
                    
                    border: 1px solid #007bff;
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
        try:
            vh_layout_confirm = QVBoxLayout()

            self.frame_image = QFrame()
            self.layout_image = QVBoxLayout(self.frame_image)

            self.icon_path_lock = self.get_path(os.path.join('assets', 'icons', 'lock.png'))
            pixmap = QPixmap(self.icon_path_lock)

            label = QLabel()
            # Fixer une taille spécifique si nécessaire, sinon le pixmap peut être vide
            label.setFixedSize(80, 80)  # exemple de taille
            pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.layout_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setPixmap(pixmap)
            self.layout_image.setContentsMargins(0,0,0,0)
            label.setStyleSheet("border-radius: 75px;")  # ça fonctionne uniquement si l'image est carrée
            self.layout_image.addWidget(label)


            self.frame_input_email = QFrame()
            self.layout_input_email = QVBoxLayout(self.frame_input_email)
            self.layout_input_email.setContentsMargins(0,0,0,0)
            self.frame_input_email.setContentsMargins(0,0,0,0)
            self.label_email = QLabel("Votre Email")
            self.layout_input_email.addWidget(self.label_email)

            self.input_email = QLineEdit() 
            self.layout_input_email.addWidget(self.input_email)

            # Frame for input
            self.frame_input = QFrame()
            self.layout_input = QVBoxLayout(self.frame_input)  
            self.layout_input.setContentsMargins(0,5,0,0)      
            self.frame_input.setContentsMargins(0,0,0,0)      
            self.label = QLabel("Mot de passe")
            self.layout_input.addWidget(self.label)
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            self.layout_input.addWidget(self.password_input)

            # Frame for button
            self.frame_buttons = QFrame()
            self.layout_buttons = QVBoxLayout(self.frame_buttons)
            self.layout_buttons.setContentsMargins(0,10,0,0)

            self.delete = QPushButton("Confirmer")
            self.delete.setCursor(Qt.PointingHandCursor)
            self.delete.clicked.connect(self.authorisation_status)
            self.layout_buttons.addWidget(self.delete)

            # Add frames to dialog layout
            vh_layout_confirm.addWidget(self.frame_image)
            vh_layout_confirm.addWidget(self.frame_input_email)
            vh_layout_confirm.addWidget(self.frame_input)
            vh_layout_confirm.addWidget(self.frame_buttons)
            vh_layout_confirm.setSpacing(4)
            self.dialog_delete.setLayout(vh_layout_confirm)
            self.dialog_delete.exec()
        except:
          print('An exception occurred')


    def authorisation_status(self):
        email = self.input_email.text()
        password = self.password_input.text()
        log_url = f"{self.base__url}autorisation-access"
        try:
            response = requests.post(
            log_url,
            json={
                'email':email,
                'password':password, 
                'permission':"Modifier personnel" 
                },
            timeout=50
        )
            response_data = response.json()
            if response.status_code == 200:
                self.token_access=response_data['token']
                print('users update')
            else:
                print('users not update')
        except:
            print('An exception occurred')

        # response = self.api_handler_.authorisation_request(email=email, password=password, permission=self.permissions_delete)


 
# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Mon Application Professionnelle")
#         self.setGeometry(300, 300, 600, 400)

#         # Icône de l'application (remplace par le chemin de ton icône)
#         icon_path = "icon.png"  # ou .ico sur Windows
#         self.setWindowIcon(QIcon(icon_path))



       


# openssl verify -CAfile "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem" "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem"

# openssl verify -CAfile "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem"
# openssl verify -CAfile "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem" "C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/server-cert.pem"


# openssl verify -CAfile "C:/Program Files/ecole-serve/certspath/ca.pem" "C:/Program Files/ecole-serve/certspath/server.crt"
# openssl verify -CAfile "C:/Program Files/ecole-serve/certspath/ca.pem" "C:/Program Files/ecole-serve/certspath/server-cert.pem"



# # Copiez-collez tout ce bloc dans PowerShell Admin
# $mysqlDir = "C:\Program Files\ecole-serve\mysql-8.0.41-winx64"
# $certsDir = "$mysqlDir\certs"

# Write-Host "=== VÉRIFICATION SSL MySQL ===" -ForegroundColor Cyan

# # 1. Existence fichiers
# Write-Host "`n1. FICHIERS:" -ForegroundColor Yellow
# Get-ChildItem $certsDir | Format-Table Name, Length

# # 2. CA auto-signé ?
# Write-Host "`n2. CERTIFICAT CA:" -ForegroundColor Yellow
# openssl x509 -in "$certsDir\ca.pem" -subject -noout
# openssl x509 -in "$certsDir\ca.pem" -issuer -noout

# # 3. Serveur signé par CA ?
# Write-Host "`n3. VÉRIFICATION SERVEUR:" -ForegroundColor Yellow
# openssl verify -CAfile "$certsDir\ca.pem" "$certsDir\server-cert.pem"

# # 4. SAN du serveur
# Write-Host "`n4. SAN DU SERVEUR:" -ForegroundColor Yellow
# openssl x509 -in "$certsDir\server-cert.pem" -text -noout | Select-String -Pattern "DNS:|IP Address:"

# # 5. Test connexion
# Write-Host "`n5. TEST CONNEXION:" -ForegroundColor Yellow
# & "$mysqlDir\bin\mysql.exe" -u lemignon -p@@@@@@@@@@ -h 127.0.0.1 -P 3307 --ssl-mode=REQUIRED -e "SELECT 'SSL Test OK'" 2>&1

# Write-Host "`n=== FIN VÉRIFICATION ===" -ForegroundColor Cyan