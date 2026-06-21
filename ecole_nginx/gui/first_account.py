"""
Création du premier compte administrateur — équivalent de insert_user() /
ask_for_user_data() dans Controllers/Main_run.py (installateur Windows natif,
qui le fait via des prompts console + msvcrt). Ici via des boîtes de dialogue
Qt puisque app_gui.py est une application graphique.

Sans cette étape, une installation fraîche (base vide) n'a aucun utilisateur
et personne ne peut se connecter depuis school_client.
"""
import requests
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox

from app.Helper.license_check import get_host_mac

INFINI_SAVE_DATA_URL = "https://www.infini-software.cloud/api/save-data"


def _first_account_exists(api_base_url: str) -> bool:
    try:
        response = requests.get(f"{api_base_url}first-check", timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        # Si l'API est injoignable, ce n'est pas à cette étape de le signaler ;
        # on n'empêche pas l'ouverture de la fenêtre de contrôle pour ça.
        return True


def ensure_first_account(api_base_url: str) -> None:
    if _first_account_exists(api_base_url):
        return

    QMessageBox.information(
        None, "Première configuration",
        "Aucun compte administrateur n'existe encore sur ce serveur.\n"
        "Créons le premier compte administrateur.",
    )

    nom, ok = QInputDialog.getText(None, "Premier compte administrateur", "Nom :")
    if not ok or not nom.strip():
        return
    prenom, ok = QInputDialog.getText(None, "Premier compte administrateur", "Prénom :")
    if not ok or not prenom.strip():
        return
    email, ok = QInputDialog.getText(None, "Premier compte administrateur", "Email :")
    if not ok or not email.strip():
        return
    password, ok = QInputDialog.getText(
        None, "Premier compte administrateur", "Mot de passe :", QLineEdit.Password
    )
    if not ok or not password:
        return

    try:
        fill = requests.get(f"{api_base_url}first-account-fill", timeout=30)
        if fill.status_code != 200:
            QMessageBox.critical(
                None, "Erreur",
                f"Initialisation des rôles/permissions échouée ({fill.status_code})."
            )
            return

        response = requests.post(
            f"{api_base_url}first-account",
            json={
                "nom": nom.strip(), "prenom": prenom.strip(), "email": email.strip(),
                "first": True, "password": password,
            },
            timeout=30,
        )
        if response.status_code == 200:
            # Comme Windows (insert_user() dans Controllers/Main_run.py) : enregistre
            # le premier compte côté infini-software.cloud. Volontairement sans
            # try/except imbriqué bloquant : un échec ici ne doit jamais empêcher
            # l'installation locale de continuer (même comportement que Windows).
            try:
                requests.post(
                    INFINI_SAVE_DATA_URL,
                    json={
                        "nom": nom.strip(), "prenom": prenom.strip(),
                        "email": email.strip(), "mac": get_host_mac(),
                    },
                    headers={"Content-Type": "application/json", "Accept": "application/json"},
                    timeout=15,
                )
            except requests.exceptions.RequestException:
                pass

            QMessageBox.information(
                None, "Succès",
                "Compte administrateur créé. Vous pouvez maintenant vous connecter depuis school_client."
            )
        else:
            QMessageBox.critical(None, "Erreur", f"Création du compte échouée : {response.text}")
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Erreur réseau", str(e))
