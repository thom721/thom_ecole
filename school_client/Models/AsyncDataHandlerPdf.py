from PySide6.QtCore import QObject, Signal, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest
import json
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
from urllib.parse import urlencode

class BaseAsyncRequestHandler(QObject):
    request_complete = Signal(str,str, dict) 
    request_failed = Signal(str,str, str, dict)  
    request_binary_complete = Signal(str, str, bytes)
    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_response)

        self.token_manager = TokenManager()
        self.ip_manager = Ip_manager()

    def _prepare_request(self, endpoint, data=None, types=None):
        url = QUrl(f"{self.base_url()}{endpoint}")
        request = QNetworkRequest(url)
        
        headers = self._get_headers()
        if types:
            request.setRawHeader("Content-Type".encode('utf-8'), "application/json".encode('utf-8'))
            request.setRawHeader("Accept".encode('utf-8'), "application/pdf".encode('utf-8'))
        else:
            for key, value in headers.items():
                request.setRawHeader(key.encode(), value.encode())
        
        if data:
            return request, QByteArray(json.dumps(data).encode())
        return request, None

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self._get_token()}"
        }

    def _get_token(self):
        """À implémenter dans la classe enfant ou via composition"""
        return self.token_manager.get_token()

    def base_url(self):
        """À implémenter dans la classe enfant"""
        return f"https://{self.ip_manager.get_server_ip()}/api/"

    def _send_request(self, endpoint, method="POST", data=None, types=None):
        # return reply
    
        if method == "GET" and data:
        # Ajouter les paramètres à l'URL
            endpoint += "?" + urlencode(data)
            # print(endpoint)
        request, payload = self._prepare_request(endpoint, data if method != "GET" else None,types)
        
        if method == "POST":
            reply = self.network_manager.post(request, payload)
        elif method == "GET":
            reply = self.network_manager.get(request)
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")
        
        reply.setProperty("endpoint", endpoint)
        reply.setProperty("method", method)
        return reply

    # def _handle_response(self, reply):
    #     endpoint = reply.property("endpoint")
    #     method = reply.property("method")
    #     try:
    #         raw_data = bytes(reply.readAll()).decode()
    #         status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
 
    #         response_data = json.loads(raw_data) if raw_data else {}

    #         print(f"response_data000000000--------  {response_data} --------- {status_code}")
          
    #         if reply.error() and status_code != 200:
    #             error_msg = reply.errorString()
    #             self.request_failed.emit(endpoint, method, error_msg, response_data)
    #         else:
    #             self.request_complete.emit(endpoint, method, response_data)
        
    #     except json.JSONDecodeError as e:
    #         self.request_failed.emit(endpoint, f"Invalid JSON: {str(e)}", None)
    #     except Exception as e:
    #         self.request_failed.emit(endpoint, f"Unexpected error: {str(e)}", None)
    #     finally:
    #         reply.deleteLater()

    def _handle_response(self, reply):
        endpoint = reply.property("endpoint")
        method = reply.property("method")
        try:
            raw_bytes = bytes(reply.readAll())
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)

            # content_type = #reply.rawHeader(b"Content-Type").data().decode('utf-8', errors='ignore').lower()

            # if 'application/pdf' in content_type:
            #     # Réponse binaire (PDF)
            #     self.request_binary_complete.emit(endpoint, method, raw_bytes)
            #     return

            try:
                raw_data = raw_bytes.decode()
                response_data = json.loads(raw_data) if raw_data else {}
            except UnicodeDecodeError:
                self.request_binary_complete.emit(endpoint, method, raw_bytes)
                return
            except json.JSONDecodeError as e:
                self.request_failed.emit(endpoint, method, f"Invalid JSON ..: {str(e)}", {})
                return

            if reply.error() and status_code != 200:
                error_msg = reply.errorString()
                self.request_failed.emit(endpoint, method, error_msg, response_data)
            else:
                self.request_complete.emit(endpoint, method, response_data)

        except Exception as e:
            self.request_failed.emit(endpoint, method, f"Unexpected error: {str(e)}", {})
        finally:
            reply.deleteLater()


class AsyncDataHandlerPdf(BaseAsyncRequestHandler):
    vente_data_ready = Signal(dict)
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.ip_manager = Ip_manager()
        # self.request_complete.connect(self._on_request_complete)

    def _get_token(self):
        return self.token_manager.get_token()

    def base_url(self):
        return f"https://{self.ip_manager.get_server_ip()}/api/"

    # Méthodes spécifiques
    def enregistrer_etudiant(self, student_id,nom,prenom,telephone,sexe,date_de_naissance, adresse,lieu_de_naissance,  religion,niveau_id,classe_actuelle_id,annee_academique_id,faculte_id,email,nom_responsable,prenom_responsable,email_responsable,sexe_responsable,telephone_responsable,adresse_responsable,aide_financiere,documentss):
        student_data = {
            'id':student_id,
            "nom" : nom,
            "prenom" : prenom,
            "telephone" : telephone,
            "sexe" : sexe,
            "date_de_naissance" : date_de_naissance,  
            "adresse" : adresse,
            "lieu_de_naissance" : lieu_de_naissance, 
            "religion" : religion,
            "niveau_id" : niveau_id,
            "classe_actuelle_id" : classe_actuelle_id,
            "annee_academique_id" : annee_academique_id,
            "faculte_id" : faculte_id,
            "email" : email,
            "aide_financiere" : aide_financiere,

            "nom_responsable" : nom_responsable,
            "email_responsable" : email_responsable,
            "sexe_responsable" : sexe_responsable,
            "adresse_responsable" : adresse_responsable,
            "prenom_responsable":prenom_responsable,
            "telephone_responsable" : telephone_responsable,

            "documentss":documentss
        }
        return self._send_request("etudiant", data=student_data)

    def enregistrer_professeur(self, professor_data):
        return self._send_request("professeur", data=professor_data)
    
    def enregistrer_admin(self, id, nom, prenom, email, sexe, adresse, role,telephone):
        personnel_data={
            'id':id,
            'nom':nom,
            'prenom':prenom,
            'email':email,
            'sexe':sexe,
            'adresse':adresse,
            'role':role,
            'telephone':telephone,
        } 
        return self._send_request("personnel", data=personnel_data)

    def enregistrer_cours(self, CoursesObject):
        course_data={
            'CoursesObject':CoursesObject
        } 
        return self._send_request("cours", data=course_data)

    def enregistrer_programme(self, programmeCoursObject):
        program_data={
            'programmeCoursObject':programmeCoursObject
        } 
        return self._send_request("programme", data=program_data)
    
    def enregistrer_paiement(self, montant_verser,niveau_id,etudiant_id,identifiant,classe,echeance,prenom,nom,annee_academique,mois,accessoires, index_paiement=None):
        paiement_data={
            'niveau_id':niveau_id,
            'etudiant_id':etudiant_id,
            'identifiant':identifiant,
            'classe':classe,
            'echeance':echeance,
            'prenom':prenom,
            'nom':nom,
            'annee_academique':annee_academique,
            'index_paiement':index_paiement,
            'paiement_details':{
                'depot':montant_verser,
                
            'depot_et_avance': '',
            'montant': '',
            'status': 0,
            'total_verse': 0,
            'total_annuel': 0,
            'devise': 0,
            'employer': 0,
            'balance': '',
            'avance': '',
                },   
                'mois': mois,
                'accessoires': accessoires
        } 
        return self._send_request("post-payment-save", data=paiement_data)
    
    def enregistrer_cours_notes(self, controle,examen,cours,type_matiere,coefficients,session,note_de_passage,professeur_id,annee_academique,notes): 
        notes_data={
            'controle':controle,
            'examen':examen,
            'cours':cours,
            'type_matiere':type_matiere,
            'coefficients':coefficients,
            'session':session,
            'note_de_passage':note_de_passage,
            'professeur_id':professeur_id,
            'annee_academique':annee_academique,
            'notes':notes,
        } 
        return self._send_request("coursEtudiant", data=notes_data)
    
    def active_teacher(self, id):
        id={
            'id':id
        }
        return self._send_request("active-teacher", data=id) 

    def active_personnel(self, id):
        id={
            'id':id
        } 
        return self._send_request("active-personnel", data=id) 
    
    def reset_password_and_connect(self,password, password_confirm,user_id):
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "user_id": user_id
        }
        return self._send_request("password-change-user", data=data_pass)
    
    def reset_password_prof(self,password, password_confirm,user_id):
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "professeur_id": user_id
        }
        return self._send_request("change-password-teacher", data=data_pass)
    
    def reset_password_perso(self,password, password_confirm,user_id): 
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "personnel_id": user_id
        }
        return self._send_request("change-password-personnel", data=data_pass)
    
    def authorization_connect(self,mac,username):
        data_pass = {
            "client_mac": mac,
            "client_name": username
        }
        return self._send_request("client-authorisation-connect", data=data_pass)
    
    def enregistrer_vente(self,id,items, etudiant_id): 
        data_vente={        
            'id':id,
            'items':items,
            'etudiant_id':etudiant_id
        }
        return self._send_request("vente", data=data_vente) 
    
    def enregistrer_depense(self,id,description_depense, prix_depense): 
        data_vente={        
            'id':id,
            'description':description_depense,
            'prix':prix_depense
        }
        return self._send_request("depense", data=data_vente)
    
    def student_live(self,search_term):    
        params = {
            "val": search_term
            }
        return self._send_request(f"live-student", method='POST', data=params) 

    def logout(self): 
        return self._send_request("logout")
    
    def all_ventes(self, search_term=None, page=1):
        params = {"search_cours": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("vente", method='GET', data=params)
    
    def all_cours(self, search_term=None, page=1):
        params = {"search_cours": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("cours", method='GET', data=params)

    def all_programme(self, search_term=None, page=1):
        params = {"search_programme": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("programme", method='GET', data=params)

    def all_admin(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page} 
        return self._send_request("personnel", method='GET', data=params) 

    def all_teacher(self,search_term=None, page=1): 
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("professeur", method='GET', data=params) 
    
    def all_student(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("etudiant", method='GET', data=params) 
    
    # def all_student_(self,search_term=None, page=None):
    #     params = {"search": search_term, "page": page} if search_term else {"page": page}
    #     return self._send_request("etudiant_load", method='GET', data=params) 

    def all_notes(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page} 
        return self._send_request("coursEtudiant", method='GET', data=params) 

    def all_paiement(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("paiement", method='GET', data=params) 
    
    def all_depenses(self,page=1):
        params = {"page": page}
        return self._send_request("depense", method='GET', data=params)

    
    def toggleAccordionAndPay(self,niveauId,anneeId, studentId,classeId,  annee_academique, faculte_id):
        params = {
            'niveau': niveauId,
            'annee_a': anneeId,
                'etudiant': studentId,
                'classe': classeId,
                'annee_academique': annee_academique,
                'faculte': faculte_id,
        }
        return self._send_request("next-payment-step", method='GET', data=params) 
    
    def data_for_dashbord(self):
        return self._send_request("dashboard", method='GET') 
    
    # def teacher_combo(self):
    #     return self._send_request("prof-for-combo", method='GET') 
    
    def roles(self):
        return self._send_request("role", method='GET')  
    
    def permissions(self):
        return self._send_request("permission", method='GET')  
    
    # def cours_combo(self):
    #     return self._send_request("cours-for-combo", method='GET')
     
    # def annee_academique(self):
    #     return self._send_request("annee-academique", method='GET') 
    
    # def niveau_index(self):
    #     return self._send_request("niveau", method='GET') 
    
    # def classes_show_check(self,search_term=None, page=None):
    #     params = {"search": search_term, "page": page} if search_term else {"page": page} 
    #     return self._send_request("classes_", method='GET') 
    
    def verify_authorization_token(self, mac):
        return self._send_request(f"client-authorisation-connect/{mac}", method='GET')
    
    def verify_sanctum_token(self, token):
        return self._send_request(f"verify-token", method='GET')
    
    def get_student_with_params_payment(self,etudiant):
        return self._send_request(f"fetch-data-with-payment-params/{etudiant}", method='GET')
    
    def all_year(self, page=1):
        params = {"page": page}
        return self._send_request("anneeAcademique", method='GET', data=params) 
    def all_classes(self, page=1):
        params = {"page": page}
        return self._send_request("classes", method='GET', data=params)
 
    def all_params_exam(self, page=1):
        params = {"page": page}
        return self._send_request("paramsExam", method='GET', data=params) 

    def all_payment_param(self, page=1):
        params = {"page": page}
        return self._send_request("parametrePaiement", method='GET', data=params)

        # try:
        #     url = f"{self.ip()}parametrePaiement"
    
    def student_print_recu_inscrit(self,student_id):
        return self._send_request(f"print-recu-inscrit/{student_id}", method='GET', types='pdf')


    def recu_paiement(self,id, keys):
        return self._send_request(f"print-recu/{id}/{keys}", method='GET', types='pdf') 
    
    def student_print(self,id, mois):
        print(f"student_print   {id}  {mois}")
        data_bulletin = {
            "bulletin": id,
            "mois": mois,
            }
        return self._send_request("imprime-bulletin", data=data_bulletin, types='pdf') 
    
    def student_print_mas_bulletin(self,annee_academique, mois, classe):    
        data_bulletin = {
            "annee_academique": annee_academique,
            "mois": mois,
            "classe": classe,
            }
        return self._send_request("imprime-mas-bulletin", data=data_bulletin, types='pdf') 
    
    def global_rapport(self, date_debut, date_fin): 
        data__for_print = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        return self._send_request("print-global-repport", data=data__for_print, types='pdf') 

    def administratif_imprimer_rapport(self, identifiant,classe,annee_ac,cycle): 
        data__for_print = {
        'identifiant':identifiant,
        'classe':classe,
        'annee_ac':annee_ac,
        'cycle':cycle,
        }
        return self._send_request("print-repport-register", data=data__for_print, types='pdf') 

    def financier_imprimer_rapport(self, classe, date_debut,date_fin,versement): 
        data__for_print = {
            "classe":classe,
            "date_debut":date_debut,
            "date_fin":date_fin,
            "versement":versement,
        }
        return self._send_request("print-rapport-paiement", data=data__for_print, types='pdf') 
    
    

    

    
    

   