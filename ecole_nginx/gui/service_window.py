"""
Fenêtre de contrôle pour l'installation Mac/Linux — équivalent de
Controllers/ShowControl.py (Windows), adapté :
- les services pilotés sont les conteneurs Docker (mysql, nginx) au lieu de
  services Windows (net start/stop, sc query) ;
- la licence est vérifiée via app.Helper.license_check directement, l'API
  tournant dans ce même process (pas besoin de docker compose exec) ;
- le panneau "postes clients" appelle l'API locale embarquée.

Volontairement non repris : les contrôles "serveur PHP artisan" de
ShowControl.py — code mort, résidu d'une ancienne version Laravel du backend.
"""
import subprocess
from pathlib import Path

import requests
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QGroupBox, QScrollArea, QSystemTrayIcon, QMenu, QLineEdit, QFrame,
    QInputDialog, QApplication,
)

from app.Helper.license_check import (
    ensure_trial_license, is_license_valid, verify_and_save_activation_key, get_host_mac,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCKER_SERVICES = {"mysql": "MySQL (Docker)", "nginx": "Nginx (Docker, HTTPS)"}


def docker_service_running(service: str) -> bool:
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "--status", "running", "--services"],
            cwd=PROJECT_DIR, capture_output=True, text=True, timeout=10,
        )
        return service in result.stdout.split()
    except Exception:
        return False


def docker_service_toggle(service: str, start: bool) -> None:
    action = ["up", "-d", service] if start else ["stop", service]
    # 300s : le premier démarrage de "nginx" tire aussi l'image "certgen" (alpine)
    # et nginx:alpine, ce qui peut dépasser largement 60s sur une connexion lente.
    subprocess.run(["docker", "compose", *action], cwd=PROJECT_DIR, capture_output=True, timeout=300)


class ServiceControlWindow(QWidget):
    def __init__(self, api_base_url: str):
        super().__init__()
        self.api_base_url = api_base_url  # ex: http://127.0.0.1:9001/api/v1/
        self.setWindowTitle("Gestion du serveur — Lekol360")
        self.setGeometry(100, 100, 480, 640)
        self.setStyleSheet("""
            QWidget { background-color: #2E2E2E; color: white; }
            QGroupBox { font-size: 12pt; border: 1px solid #555; border-radius: 6px; margin-top: 12px; padding: 6px; }
            QGroupBox::title { color: #4DA3FF; subcontrol-origin: margin; left: 8px; }
            QLineEdit { min-height: 28px; border-radius: 4px; padding-left: 6px; background: #1C1C1C; color: white; }
            QPushButton { padding: 6px 12px; border-radius: 4px; }
        """)

        icon_path = PROJECT_DIR / "icon_server.ico"
        self.tray_icon = QSystemTrayIcon(QIcon(str(icon_path)) if icon_path.exists() else QIcon(), self)
        self.tray_icon.setToolTip("Serveur Lekol360")
        tray_menu = QMenu()
        show_action = QAction("Afficher", self)
        quit_action = QAction("Quitter", self)
        show_action.triggered.connect(self._show_window)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

        self.service_buttons = {}
        self._build_ui()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(15000)
        self.refresh_timer.timeout.connect(self._refresh_service_status)
        self.refresh_timer.start()

    # ---- fenêtre / icône système ----
    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Lekol360", "Le serveur continue de fonctionner en arrière-plan.",
            QSystemTrayIcon.Information, 3000,
        )

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.hide() if self.isVisible() else self._show_window()

    # ---- construction de l'UI ----
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(self._build_services_group())
        layout.addWidget(self._build_license_group())
        layout.addWidget(self._build_clients_group())

        refresh_btn = QPushButton("Tout actualiser")
        refresh_btn.clicked.connect(self._refresh_all)
        layout.addWidget(refresh_btn)

    def _build_services_group(self):
        box = QGroupBox("Services Docker")
        v = QVBoxLayout(box)
        for service, label in DOCKER_SERVICES.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            btn = QPushButton()
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, s=service: self._toggle_service(s, checked))
            row.addWidget(btn)
            self.service_buttons[service] = btn
            v.addLayout(row)
        self._refresh_service_status()
        return box

    def _toggle_service(self, service, checked):
        button = self.service_buttons[service]
        button.setEnabled(False)
        docker_service_toggle(service, start=checked)
        self._refresh_service_status()
        button.setEnabled(True)

    def _refresh_service_status(self):
        for service, button in self.service_buttons.items():
            running = docker_service_running(service)
            button.blockSignals(True)
            button.setChecked(running)
            button.setText("Actif" if running else "Arrêté")
            button.setStyleSheet(
                f"color: white; background-color: {'#2e7d32' if running else '#c62828'};"
            )
            button.blockSignals(False)

    def _build_license_group(self):
        box = QGroupBox("Licence")
        v = QVBoxLayout(box)
        self.license_status_label = QLabel()
        self.license_status_label.setWordWrap(True)
        v.addWidget(self.license_status_label)

        self.license_input_row = QWidget()
        row = QHBoxLayout(self.license_input_row)
        row.setContentsMargins(0, 0, 0, 0)
        self.license_key_input = QLineEdit()
        self.license_key_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
        verify_btn = QPushButton("Activer")
        verify_btn.clicked.connect(self._activate_license)
        row.addWidget(self.license_key_input)
        row.addWidget(verify_btn)
        v.addWidget(self.license_input_row)

        self._refresh_license_status()
        return box

    def _refresh_license_status(self):
        key, expiration_date = ensure_trial_license()
        valid = is_license_valid()
        mac = get_host_mac()
        state = "valide" if valid else "expirée ou invalide"
        self.license_status_label.setText(
            f"MAC : {mac}\nClé : {key}\nExpire le : {expiration_date}\nÉtat : {state}"
        )
        self.license_status_label.setStyleSheet(f"color: {'#4CAF50' if valid else '#FF6B6B'};")
        # Le champ de saisie/activation n'a de sens que tant qu'aucune licence valide
        # n'est active ; une fois validée, on l'efface pour ne pas suggérer de ressaisir.
        self.license_input_row.setVisible(not valid)

    def _activate_license(self):
        key = self.license_key_input.text().strip()
        if not key:
            return
        if verify_and_save_activation_key(key):
            QMessageBox.information(self, "Licence", "Clé acceptée.")
        else:
            QMessageBox.critical(
                self, "Licence",
                "Clé invalide pour cette machine (ou pas générée aujourd'hui)."
            )
        self._refresh_license_status()

    def _build_clients_group(self):
        box = QGroupBox("Postes clients")
        v = QVBoxLayout(box)

        self.clients_scroll = QScrollArea()
        self.clients_scroll.setWidgetResizable(True)
        self.clients_widget = QWidget()
        self.clients_layout = QVBoxLayout(self.clients_widget)
        self.clients_scroll.setWidget(self.clients_widget)
        v.addWidget(self.clients_scroll)

        self._refresh_clients()
        return box

    def _refresh_clients(self):
        for i in reversed(range(self.clients_layout.count())):
            item = self.clients_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        try:
            response = requests.get(f"{self.api_base_url}client-authorisation-connect", timeout=5)
            clients = response.json().get("data_client", []) if response.status_code == 200 else []
        except requests.exceptions.RequestException:
            self.clients_layout.addWidget(QLabel("Impossible de contacter l'API."))
            return

        if not clients:
            self.clients_layout.addWidget(QLabel("Aucun poste connecté pour le moment."))

        for client in clients:
            row = QFrame()
            row_layout = QHBoxLayout(row)
            info = QLabel(f"{client.get('client_name', 'Inconnu')}\n{client.get('client_mac', '')}")
            row_layout.addWidget(info)

            toggle = QPushButton("Autorisé" if client.get("authorisation") else "Bloqué")
            toggle.setStyleSheet(
                f"color: white; background-color: {'#2e7d32' if client.get('authorisation') else '#c62828'};"
            )
            toggle.clicked.connect(lambda _, c=client: self._toggle_client_authorization(c))
            row_layout.addWidget(toggle)

            self.clients_layout.addWidget(row)

    def _toggle_client_authorization(self, client: dict):
        email, ok = QInputDialog.getText(self, "Confirmation requise", "Email administrateur :")
        if not ok or not email:
            return
        password, ok = QInputDialog.getText(
            self, "Confirmation requise", "Mot de passe :", QLineEdit.Password
        )
        if not ok:
            return

        try:
            response = requests.post(
                f"{self.api_base_url}client-authorisation-connect",
                json={
                    "id": client.get("id"), "email": email,
                    "password": password, "login_as": "as_desktop",
                },
                timeout=10,
            )
            if response.status_code == 200:
                QMessageBox.information(self, "Postes clients", "Autorisation mise à jour.")
            else:
                detail = response.json().get("detail", "Échec de la mise à jour.")
                QMessageBox.critical(self, "Postes clients", str(detail))
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Postes clients", f"Erreur réseau : {e}")

        self._refresh_clients()

    def _refresh_all(self):
        self._refresh_service_status()
        self._refresh_license_status()
        self._refresh_clients()
