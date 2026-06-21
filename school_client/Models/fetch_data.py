from Config import HEADERS
import sys
import requests
from PySide6.QtWidgets import QMessageBox
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
from PySide6.QtWidgets import QProgressDialog
from PySide6.QtCore import QTimer


def _ssl_verify_param():
    """Valeur à passer à requests(..., verify=...) : chemin local pinné sur
    Windows (comportement historique inchangé), ou True sur Mac/Linux, où ce
    fichier .crt local n'est jamais déposé — la vérification y passe alors par
    le magasin de confiance du système via truststore.inject_into_ssl() (voir
    app.py), qui fait déjà confiance à la CA installée par
    scripts/setup-local-https.sh côté serveur."""
    if sys.platform == "win32":
        return r"C:\Program Files\gestion ecole\crt\server.crt"
    return True


class Fech_data:
    def __init__(self):
        self.ip_manager = Ip_manager()
        self.token__manager = TokenManager()
        # self.make_request()

    def ip(self):
        return f"https://{self.ip_manager.get_server_ip()}/api/v1/"
    
    def token_manager(self):
        return self.token__manager.get_token()

    def headers_token(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {self.token_manager()}"
        }
    

    def make_request(self):
        # Créer un dialogue de progression
        self.progress = QProgressDialog("Traitement en cours...", "Annuler", 0, 0, None)
        self.progress.setWindowTitle("Veuillez patienter")
        self.progress.setModal(True)
        self.progress.show()
        
        # Simuler une requête avec un timer
        QTimer.singleShot(2000, self.request_finished)

    def request_finished(self):
        self.progress.close()


    def niveau_index(self):
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        try:
            url = f"{self.ip()}niveau"
            response = requests.get(url, headers=headers, verify=_ssl_verify_param())

            response_data = response.json()

            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")


    def class_and_other(self,niveau):
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        
        try:
            url = f"{self.ip()}niveau-with-class/{niveau}"
            response = requests.get(url, headers=headers, verify=_ssl_verify_param())

            response_data = response.json()

            if response.status_code == 200:
                return response_data['classe_actuelle']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        

    def annee_academique(self):
        headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
        }
        try:
            url = f"{self.ip()}annee-academique"
            response = requests.get(url, headers=headers, verify=_ssl_verify_param())

            response_data = response.json()

            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # =============================================ETUDIANT===================================================

    def all_student(self,search_term=None, page=1):
        # params = {"search": search_term} if search_term else {}  
        # print(params)
        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}etudiant"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [] 

        
    def student_show(self,etudiant):
        try:
            url = f"{self.ip()}etudiant/{etudiant}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def delete___students(self, etudiant):
        try:
            url = f"{self.ip()}etudiant/{etudiant}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def update_student_status_classe(self, p, t):
        try:
            payload = {
            "classe_student_id": p,
            "state": t,
            }
            url = f"{self.ip()}update-etudiant-classe"
            response = requests.post(url,json=payload, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def student_live(self,search_term):
    
        payload = {
            "val": search_term
            }
        # if search_term:
        try:
            url = f"{self.ip()}live-student"
            response = requests.post(url, json=payload, timeout=10, headers=self.headers_token(), verify=_ssl_verify_param())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                return response_data   
            
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            # return response.json()


    def student_print_details(self, student_id):
        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf',
        }
        print(f"student_print_details   {student_id}")
        payload = {
            'student_id': student_id,
        }

        try:
            url = f"{self.ip()}student-print-details" #student-print-details
            response = requests.post(
                url,
                json=payload,
                headers=HEADER,
                timeout=60,
                stream=True, verify=_ssl_verify_param()  # Permet de gérer les gros fichiers
            )

            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            QMessageBox.critical(
                self, 
                "Erreur réseau", 
                f"Impossible de se connecter au serveur:\n{str(e)}"
            )
            return None
   
    # ===========================================ETUDIANT===================================================
    def data_for_dashbord(self):

        try:
            url = f"{self.ip()}dashboard"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def student_with_classe(self, classe,annee_id):

        try:
            params ={
                'classe_id':classe,
                'annee_id':annee_id
            }
            url = f"{self.ip()}student-with-classe"
            response = requests.get(url,params=params, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
    # =============================================PROFESSEUR===================================================

    def all_teacher(self,search_term=None, page=1):
        # params = {"search": search_term} if search_term else {}  
        # print(params)
        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}professeur"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

        
    def teacher_show(self,professeur):
        try:
            url = f"{self.ip()}professeur/{professeur}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def teacher_combo(self):
        try:
            url = f"{self.ip()}prof-for-combo"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['prof']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
    # =============================================PROFESSEURS===================================================

    # =============================================PERSONNEL===================================================

    def all_admin(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        # HEADER  = {
        #     'Content-Type': 'application/json',
        #     'Accept': 'application/json',
        #     "Authorization": f"Bearer {token}"
        # }
        try:
            url = f"{self.ip()}personnel"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

        
    def admin_show(self,personnel):
        try:
            url = f"{self.ip()}personnel/{personnel}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # =============================================PERSONNEL===================================================


    # =========================================== __ROLE__ ================================================

    def roles(self): 
        try:
            url = f"{self.ip()}role"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json()

            if response.status_code == 200: 
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def permissions(self): 
        try:
            url = f"{self.ip()}permission"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json()

            if response.status_code == 200: 
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    # =========================================== __ROLE__ ================================================

    # =========================================== __COURS__ =================================================

    def all_cours(self,search_term=None, page=1):
        # params = {"search": search_term} if search_term else {}  
        # print(params)
        params = {"search_cours": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}cours"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

        
    def cours_show(self,cours):
        try:
            url = f"{self.ip()}cours/{cours}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def cours_combo(self):
        try:
            url = f"{self.ip()}cours-for-combo"
            # params = {"niveau": niveau} if niveau else {} 

            response = requests.get(url, headers=HEADERS, verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['cours']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    # =========================================== __COURS__ =================================================

    # ======================================__PROGRAMME__ =============================================

    def all_programme(self,search_term=None, page=1):
        # params = {"search": search_term} if search_term else {}  
        # print(params)
        params = {"search_programme": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}programme"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

        
    def programme_show(self,programme):
        try:
            url = f"{self.ip()}programme/{programme}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # ======================================__PROGRAMME__ =============================================

    # ======================================__PAIEMENT__ =============================================

    def all_paiement(self,search_term=None, page=1):

        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}paiement"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def paiement_show(self,paiement):
        try:
            url = f"{self.ip()}paiement/{paiement}"
        
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response.json() 

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        

    def get_student_with_params_payment(self,etudiant):
        try:
            url = f"{self.ip()}fetch-data-with-payment-params/{etudiant}"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def toggleAccordionAndPay(self,niveauId,anneeId, studentId,classeId,  annee_academique, faculte_id):
        try:
            params = {
                'niveau': niveauId,
                'annee_a': anneeId,
                 'etudiant': studentId,
                 'classe': classeId,
                 'annee_academique': annee_academique,
                 'faculte': faculte_id,
            }
            url = f"{self.ip()}next-payment-step"#/{niveauId}/{anneeId}/{studentId}/{classeId}/{annee_academique}/{faculte_id}"
        
            response = requests.get(url,params=params, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                print(response_data)
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
    # ======================================__PAIEMENT__ =============================================


    # ======================================__NOTES__ =============================================

    def all_notes(self,search_term=None, page=1):

        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}coursEtudiant"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            #return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def notes_show(self,coursEtudiant):
        try:
            url = f"{self.ip()}coursEtudiant/{coursEtudiant}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def students_for_notes(self,niveau,cours,classe,annee_academique,faculte,session):
    
        payload = {
            "niveau": niveau,
            "cours": cours,
            "class": classe,
            "annee_academique": annee_academique,
            'faculte':faculte,
            'session':session,
            }
        # if search_term:
        try:
            url = f"{self.ip()}cours-etudiant-add-note"
            response = requests.post(url, json=payload, timeout=10, headers=self.headers_token(), verify=_ssl_verify_param())
            response_data = response.json()
            if response.status_code == 200 and "datas" in response_data:
                # print(response_data)
                return response_data['datas']   
            
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            # return response.json()

    def student_print(self,id, mois):
        print(f"student_print   {id}  {mois}")
        payload = {
            "bulletin": id,
            "mois": mois,
            }
        print(payload)
        try:
            url = f"{self.ip()}imprime-bulletin"
            HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf', 
        }
            response = requests.post(url, json=payload, headers=HEADER, timeout=60,stream=True   
            )  
            # response.raise_for_status()
            # print(response.json())
            # Vérifie si le PDF est retourné par l'API
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    print(response.json())
                    return None
                return response.content  # Le contenu du PDF
            else:
                print(f"Erreur API : {response.json()}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return None
        
    def student_print_mas_bulletin(self,annee_academique, mois, classe):
    
        payload = {
            "annee_academique": annee_academique,
            "mois": mois,
            "classe": classe,
            }
        print(payload)
        try:
            url = f"{self.ip()}imprime-mas-bulletin"
            HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf', 
        }
            response = requests.post(
                url,
                json=payload,
                headers=HEADER,
                timeout=60,
                stream=True   
            )             
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    print(response.json())
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None


        # try:
        #     url = f"{self.ip()}imprime-mas-bulletin"
        #     response = requests.post(url, json=payload, headers=HEADERS, timeout=60)
        #     response.raise_for_status()
        #     # response_data = response.json()
            
        #     # Vérifie si le PDF est retourné par l'API
        #     if response.status_code == 200:
        #         return response.content  # Le contenu du PDF
        #         # return response_data['data'] 
        #     else:
        #         print(f"Erreur API : {response.json()}")
        #         return None

        # except requests.exceptions.RequestException as e:
        #     print(f"Erreur de connexion à l'API : {e}")
        #     return None
        
        # ======================================__ANNEE ACADEMIQUE__ =============================================

    def all_year(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}anneeAcademique"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def year_show(self,anneeAcademique):
        try:
            url = f"{self.ip()}anneeAcademique/{anneeAcademique}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # ======================================__CLASSES__ =============================================

    def all_classes(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}classes"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def classes_show(self,classes):
        try:
            url = f"{self.ip()}classes/{classes}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def classes_show_check(self):
        try:
            url = f"{self.ip()}classes"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        

    # ======================================__PARAMS EXAM__ =============================================

    def all_params_exam(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}paramsExam"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def params_exam_show(self,paramsExam):
        try:
            url = f"{self.ip()}paramsExam/{paramsExam}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # ======================================__PARAMETRE PAIEMENT__ =============================================

    def all_payment_param(self,search_term=None, page=1):

        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}parametrePaiement"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                #return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def payment_param_show(self,parametrePaiement):
        try:
            url = f"{self.ip()}parametrePaiement/{parametrePaiement}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    # ======================================__NOTES__ =============================================

    def all_register_fee(self,search_term=None, page=1):

        params = {"search": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}fraisDinscription"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return [response.json()]  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return [response.json()]  # Retourne une liste vide pour éviter un crash

        
    def register_fee_show(self,fraisDinscription):
        try:
            url = f"{self.ip()}fraisDinscription/{fraisDinscription}"
            response = requests.get(url, headers=self.headers_token())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        

    def global_rapport(self, date_debut, date_fin):

        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf',
        }
        
        payload = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        print(payload)
        try:
            url = f"{self.ip()}print-global-repport"
            response = requests.post(
                url,
                json=payload,
                headers=HEADER,
                timeout=60,
                stream=True  # Permet de gérer les gros fichiers
            )
            
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None

    
    def administratif_imprimer_rapport(self, identifiant,classe,annee_ac,cycle):

        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf',
        }
        
        payload = {
        'identifiant':identifiant,
        'classe':classe,
        'annee_ac':annee_ac,
        'cycle':cycle,
        }
        print(payload)
        try:
            url = f"{self.ip()}print-repport-register"
            response = requests.post(
                url,
                json=payload,
                headers=HEADER,
                timeout=120,
                stream=True  # Permet de gérer les gros fichiers
            )
            
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None

    
    def financier_imprimer_rapport(self, classe, date_debut,date_fin,versement):
        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf',
        }
        
        payload = {
            "classe":classe,
            "date_debut":date_debut,
            "date_fin":date_fin,
            "versement":versement,
        }
        print(payload)
        try:
            url = f"{self.ip()}print-rapport-paiement"
            response = requests.post(
                url,
                json=payload,
                headers=HEADER,
                timeout=120,
                stream=True  # Permet de gérer les gros fichiers
            )
            
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None

    def recu_paiement(self,id, keys):
        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf', 
        }
        payload = {
            'id':id,
            'keys':keys
            }
        try:
            url = f"{self.ip()}print-recu/{id}/{keys}"
            response = requests.get(
                url, 
                headers=HEADER,
                timeout=60,
                stream=True  # Permet de gérer les gros fichiers
            )
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '') 
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None

    def get_Vente_receipt(self,id):
        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf', 
        }
        payload = {
            'id':id,
            }
        try:
            url = f"{self.ip()}print-recu-vente/{id}"
            response = requests.get(
                url,
                # json=payload,
                headers=HEADER,
                timeout=60,
                stream=True  # Permet de gérer les gros fichiers
            )
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                print(response.content, content_type)
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
            #QMessageBox.critical(
            #     self, 
            #     "Erreur réseau", 
            #     f"Impossible de se connecter au serveur:\n{str(e)}"
            # )
            return None


    def student_print_recu_inscrit(self,student_id):
        HEADER = {
            'Content-Type': 'application/json',
            'Accept': 'application/pdf', 
        }
        try:
            url = f"{self.ip()}print-recu-inscrit/{student_id}"
            response = requests.get(
                url,
                headers=HEADER,
                timeout=60,
                stream=True  # Permet de gérer les gros fichiers
            )
            # Vérification approfondie de la réponse
            if response.status_code == 200:
                # Vérifie que c'est bien un PDF qui est retourné
                content_type = response.headers.get('Content-Type', '')
                if 'application/pdf' not in content_type:
                    print("L'API n'a pas retourné un PDF (Content-Type: %s)" % content_type)
                    return None
                    
                return response.content
            
            # Gestion des erreurs HTTP spécifiques
            elif response.status_code == 401:
                print("Erreur d'authentification - Token peut-être expiré")
               # self.token_manager.refresh_token()  # À implémenter si nécessaire
            elif response.status_code == 404:
                print("Endpoint API introuvable")
            elif response.status_code >= 500:
                print(f"Erreur serveur API  code {response.status_code}")

            # Essaie de récupérer un message d'erreur JSON si disponible
            try:
                error_msg = response.json().get('message', 'Pas de message d\'erreur')
                print(f"Erreur API ({response.status_code}): {error_msg}")
            except ValueError:
                print(f"Erreur API ({response.status_code}): Réponse non JSON")

            return None

        except requests.exceptions.Timeout:
            print("Timeout: Le serveur n'a pas répondu dans les 60 secondes")
            #QMessageBox.warning(self, "Timeout", "Le serveur met trop de temps à répondre")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion: {str(e)}")
        
            return None



        # try:
        #     url = f"{self.ip()}print-recu/{id}/{keys}"
        #     response = requests.get(url, json=payload, headers=HEADER, timeout=80)
        #     response.raise_for_status()
            
    
        #     if response.status_code == 200:
        #         return response.content 
        #     else:
        #         print(f"Erreur API : {response.json()}")
        #         return None

        # except requests.exceptions.RequestException as e:
        #     print(f"Erreur de connexion à l'API : {e}")
        #     return None


    def getPermissionByRole(self,role):
        try:
            url = f"{self.ip()}get-permission-by-role/{role}"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")  
        
    def fetchDataWithPermission(self, data):
        params = {"data": data,} 
        try:
            url = f"{self.ip()}fetch-data-with-permission"
            response = requests.get(url,params=params, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}") 

    def fetchDataWithRole(self, data):
        params = {"data": data,} 
        try:
            url = f"{self.ip()}fetch-data-with-role"
            response = requests.get(url,params=params, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")   
        
    def all_ventes(self,search_term=None, page=1):
        params = {"search_cours": search_term, "page": page} if search_term else {"page": page}

        try:
            url = f"{self.ip()}vente"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token(), verify=_ssl_verify_param())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

    def all_depenses(self,page=1):
        params = {"page": page}

        try:
            url = f"{self.ip()}depense"
            response = requests.get(url, params=params, timeout=10, headers=self.headers_token(), verify=_ssl_verify_param())
            response_data = response.json()
            if response.status_code == 200 and "data" in response_data:
                # print(response_data)
                # return response_data["data"]   
                return {
                    "data": response_data["data"],  # Liste des étudiants
                    "total_pages": response_data.get("meta", {}).get("last_page", 1),  # Nombre total de pages
                    "current_page": response_data.get("meta", {}).get("current_page", 1)  # Page actuelle
                }
            else:
                print(f"Erreur API : {response_data}")  # Affiche l'erreur sans crasher
                return []  # Retourne une liste vide en cas d'erreur

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return []  # Retourne une liste vide pour éviter un crash

        
    def vente_show(self,vente):
        try:
            url = f"{self.ip()}order-vente/{vente}"
            response = requests.get(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data['data']
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def delete_order(self, vente, id):
        params ={
            'vente' : vente,
            'vente_id' : id,
        }
        try:
            url = f"{self.ip()}vente-delete"
            response = requests.get(url,params=params, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                print(f"response_data  -00 {response_data}")
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def delete_prof(self, professeur):
        try:
            url = f"{self.ip()}professeur/{professeur}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")


    def delete_perso(self, personnel):
        try:
            url = f"{self.ip()}personnel/{personnel}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def fetch_data_note_for_edit(self, notes,evaluation_examen,cours,annee_academique,cours_type):
        payload = {
            'notes':notes,
            'examen':evaluation_examen,
            'cours':cours,
            'annee_academique':annee_academique,
            'type_matiere':cours_type
            }
        print(payload)
        try:
            url = f"{self.ip()}cours-etudiant-edit-note"
            response = requests.post(url,json=payload, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def get_promus(self,annee, niveau, classe):
        payload = {
           'data':{
            'annee_academique_id':annee,
            'niveau_id':niveau,
            'classes_id':classe,
           }
            }
        try:
            url = f"{self.ip()}get-promus"
            response = requests.post(url,json=payload, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def etudiant_promus_to(self,annee_actuelle,niveau_actuel,classe_actuelle,annee_f,niveau_f,classe_f):
        payload = {
            'annee_academique_id' : annee_actuelle,
            'niveau_id' : niveau_actuel,
            'classes_id' : classe_actuelle,

            'annee_academique_future' : annee_f,
            'niveau_future' : niveau_f,
            'classe_future' : classe_f
            }
        try:
            url = f"{self.ip()}etudiant-promus-to"
            response = requests.post(url,json=payload, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def delete_params_exam(self, paramsExam):
        try:
            url = f"{self.ip()}paramsExam/{paramsExam}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        


    def delete_programme(self, programme):
        try:
            url = f"{self.ip()}programme/{programme}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        

    def delete_cours(self, cours):
        try:
            url = f"{self.ip()}cours/{cours}"
            response = requests.delete(url, headers=self.headers_token(), verify=_ssl_verify_param())

            response_data = response.json() 
            if response.status_code == 200:
                return response_data
            else:
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")


