from PySide6.QtCore import QObject, Signal, QUrl, QByteArray
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QSslCertificate, QSslSocket

import json
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager
from urllib.parse import urlencode

class BaseAsyncRequestHandler(QObject):
    request_complete = Signal(str,str, dict) 
    request_failed = Signal(str,str, str, dict)  
    request_binary_complete = Signal(str, str, bytes,str)
    admin_auth_required = Signal(str, str, str, dict)
    def __init__(self):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._handle_response)
        self.timeout = 60000

        self.token_manager = TokenManager()
        self.ip_manager = Ip_manager()
        

    def _prepare_request(self, endpoint, data=None, types=None):
        
        url = QUrl(f"{self.base_url()}{endpoint}")
        # print(f"url     {url}")
        request = QNetworkRequest(url)
        
        headers = self._get_headers()
        if types:
            if types == "pdf":
                request.setRawHeader("Content-Type".encode('utf-8'), "application/json".encode('utf-8'))
                request.setRawHeader("Accept".encode('utf-8'), "application/pdf".encode('utf-8'))
                request.setRawHeader("Authorization".encode('utf-8'), f"Bearer {self._get_token()}".encode('utf-8'))
            elif types == "excel": 
                request.setRawHeader("Content-Type".encode('utf-8'), "application/json".encode('utf-8'))
                request.setRawHeader(b"Accept", b"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                request.setRawHeader("Authorization".encode('utf-8'), f"Bearer {self._get_token()}".encode('utf-8'))

        else:
            for key, value in headers.items():
                request.setRawHeader(key.encode(), value.encode())
        request.setTransferTimeout(self.timeout)
        
        if data:
            return request, QByteArray(json.dumps(data).encode())
        return request, None

    def _get_headers(self):
        token_access = TokenManager().get_token_access()
    
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {self._get_token()}"
        }

        if self._get_token():
           headers['Authorization'] = f"Bearer {self._get_token()}"

        if token_access:
            headers['X-Approval-Token'] = token_access

            print(f"token_access   {token_access}")
        return headers


    def _get_token(self):
        """À implémenter dans la classe enfant ou via composition"""
        return self.token_manager.get_token()

    def base_url(self):
        """À implémenter dans la classe enfant"""
        domain = bool(self.token_manager.get_adress_type())
        # return f"http://127.0.0.1:9002/api/"
        if domain:
            return f"https://aplekol360.local/api/"
        else:
            return f"https://aplekol360.local/api/"
            # return f"https://{self.ip_manager.get_server_ip()}/api/"

 

    def _send_request(self, endpoint, method="POST", data=None, types=None):
        method = method.upper()

        if method == "GET" and data:
            endpoint += "?" + urlencode(data)

        request, payload = self._prepare_request(
            endpoint,
            data if method not in ("GET", "DELETE") else None,
            types
        )

        if method == "POST":
            reply = self.network_manager.post(request, payload)

        elif method == "GET":
            reply = self.network_manager.get(request)

        elif method == "DELETE":
            reply = self.network_manager.deleteResource(request)

        elif method == "PATCH":
            reply = self.network_manager.sendCustomRequest(
                request,
                b"PATCH",
                payload
            )
        elif method == "PUT":
            reply = self.network_manager.sendCustomRequest(
                request,
                b"PUT",
                payload
            )
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")

        reply.setProperty("endpoint", endpoint)
        reply.setProperty("method", method)
        reply.setProperty("types", types)
        return reply

 
    def _handle_response(self, reply):
        endpoint = reply.property("endpoint")
        method = reply.property("method")
        types = reply.property("types")
        try:
             
            raw_bytes = bytes(reply.readAll())
            # response_data = reply.readAll()
            # response_text = bytes(response_data).decode('utf-8')
            status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)

            # raw_header_dataww = reply.rawHeader("X-Authorization-Required")
            # print(raw_header_dataww)
            # is_admin_auth_required = str(raw_header_data.data(), 'utf-8').lower() == "true"

            # auth_message = reply.rawHeader(b"X-Message").data().decode() if reply.hasRawHeader(b"X-Message") else ""
            # print(status_code)
            is_admin_auth_required = False
            if reply.hasRawHeader("X-Authorization-Required"):
                header_bytes = reply.rawHeader("X-Authorization-Required").data()
                is_admin_auth_required = str(header_bytes, 'utf-8').lower() == "true"
                print(is_admin_auth_required)

            auth_message = ""
            if reply.hasRawHeader("X-Message"):
                auth_message = str(reply.rawHeader("X-Message").data(), 'utf-8')
                print(auth_message)

            try:
                raw_data = raw_bytes.decode('utf-8')
                response_data = json.loads(raw_data) if raw_data else {}
            except UnicodeDecodeError:
                self.request_binary_complete.emit(endpoint, method, raw_bytes,types)
                return
            except json.JSONDecodeError as e:
                self.request_failed.emit(endpoint, method, f"Invalid JSON: {str(e)}", {})
                return
            
            if status_code == 202 and is_admin_auth_required:
                self.admin_auth_required.emit(endpoint, method, auth_message, response_data)
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


class AsyncDataHandler(BaseAsyncRequestHandler):
    vente_data_ready = Signal(dict)
    def __init__(self):
        super().__init__()
        self.token_manager = TokenManager()
        self.ip_manager = Ip_manager()
        # self.request_complete.connect(self._on_request_complete)
        # print(f"\n\n{self.ip_manager}\n\n--")
    def _get_token(self):
        return self.token_manager.get_token()

    def base_url(self): 
        domain = bool(self.token_manager.get_adress_type())
        # return f"http://127.0.0.1:9002/api/"
        if domain:
            return f"https://aplekol360.local/api/"
        else:
            return f"https://aplekol360.local/api/"
            # return f"https://{self.ip_manager.get_server_ip()}/api/"

    def verifier_health(self):
        return self._send_request("v1/health", method='GET')
    # Méthodes spécifiques
    def enregistrer_etudiant(self, student_id,nom,prenom,telephone,sexe,date_de_naissance, adresse,lieu_de_naissance,  religion,niveau_id,classe_actuelle_id,annee_academique_id,faculte_id,email,nom_responsable,prenom_responsable,email_responsable,sexe_responsable,telephone_responsable,adresse_responsable,aide_financiere,documentss,nisu,dernier_etablissement):
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
            "nisu": nisu,
            "dernier_etablissement": dernier_etablissement,

            "documentss":documentss
        }
        
        return self._send_request("v1/etudiant", data=student_data)

    def enregistrer_professeur(self, professor_data):
        return self._send_request("v1/professeur", data=professor_data)
    
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
        print(personnel_data)
        return self._send_request("v1/personnel", data=personnel_data)
    def login(self, email, password):
        """Méthode spécialisée pour le login"""
        data = {
            "email": email,
            "password": password,
            "device_name": "qt-desktop-app",
            "login_as": "as_desktop"
        }
        return self._send_request("v1/auth/login", data=data)
        # self.post("login", data, success_callback, error_callback)

    def enregistrer_cours(self, CoursesObject):
        course_data={
            'CoursesObject':CoursesObject
        } 
        return self._send_request("v1/cours", data=course_data)

    def enregistrer_programme(self, programmeCoursObject):
        program_data={
            'programmeCoursObject':programmeCoursObject
        } 
        print(programmeCoursObject)
        return self._send_request("v1/programme", data=program_data)
    
    def enregistrer_paiement(self, montant_verser,niveau_id,etudiant_id,identifiant,classe,echeance,prenom,nom,annee_academique,mois,accessoires,must_refresh_paiement, index_paiement=None):
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
            'must_refresh_paiement':must_refresh_paiement,
            'paiement_details':{
            'depot':montant_verser if must_refresh_paiement == False else 0,                
            'depot_et_avance': None,
            'montant': None,
            'status': 0,
            'total_verse': 0,
            'total_annuel': 0,
            'devise': 0,
            'employer': '',
            'balance': None,
            'avance': None,
                },   
                'mois': mois,
                'accessoires': accessoires
        } 
        return self._send_request("v1/post-payment-save", data=paiement_data)
    
    def enregistrer_cours_notes(self, controle,examen,cours,type_matiere,coefficients,session,note_de_passage,professeur_id,annee_academique,notes): 
        notes_data={
            'controle':controle,
            'examen':examen,
            'cours':cours,
            'type_matiere':type_matiere,
            'coefficients':coefficients,
            'session':session,
            'note_de_passage':note_de_passage if note_de_passage not in (None, '') else 0.0,
            'professeur_id':professeur_id,
            'annee_academique':annee_academique,
            'notes':notes,
        } 
        print(notes_data)
        return self._send_request("v1/coursEtudiant", data=notes_data)
    
    def active_teacher(self, id):
        id={
            'id':id
        }
        return self._send_request("v1/active-teacher",method="PATCH", data=id) 

    def active_personnel(self, id):
        id={
            'id':id
        } 
        return self._send_request("v1/active-personnel",method="PATCH", data=id) 

    def save_badge_image(self,data):
        payload={
            'etudiant_id':data.get("etudiant_id"),
            'image_base64':data.get("image_base64")
        } 
        return self._send_request("v1/save-badge-image",method="PATCH", data=payload)
    
    def reset_password_and_connect(self,password, password_confirm,user_id):
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "user_id": user_id
        }
        return self._send_request("v1/password-change-user",method="PATCH", data=data_pass)
    
    def reset_password_prof(self,password, password_confirm,user_id):
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "professeur_id": user_id
        }
        
        return self._send_request("v1/change-password-teacher",method="PATCH", data=data_pass)
    
    def reset_password_perso(self,password, password_confirm,user_id): 
        data_pass = {
            "password": password,
            "password_confirm": password_confirm,
            "personnel_id": user_id
        }
        return self._send_request("v1/change-password-personnel",method="PATCH", data=data_pass)
    
    def authorization_connect(self,mac,username):
        data_pass = {
            "client_mac": mac,
            "client_name": username
        }
        return self._send_request("v1/client-authorisation-connect",method="POST", data=data_pass)
    
    def enregistrer_vente(self,id,items, etudiant_id,user_id): 
        data_vente={        
            'id':id,
            'items':items,
            'etudiant_id':etudiant_id,
            'user_id' :user_id
        }
        return self._send_request("v1/vente", data=data_vente) 
    
    def authorisation_request(self,email, password,permission): 
        data_authorrisation={        
            'email':email,
            'password':password, 
            'permission':permission
        }
        return self._send_request("v1/auth/autorisation-access", data=data_authorrisation)
    
    def enregistrer_depense(self,id,description_depense, prix_depense): 
        data_vente={        
            'id':id,
            'description':description_depense,
            'prix':prix_depense
        }
        return self._send_request("v1/depense", data=data_vente)
    
    def enregistrer_frais_divers(self,id, prix,description, niveau_id, anneeAc): 
        data_frais_divers={
            'description':description,
            'prix':prix,
            'id':id,
            'niveau_id':niveau_id,
            'anneeAc':anneeAc,
        }
        return self._send_request("v1/frais-divers-store", data=data_frais_divers)
    
    def enregistrer_faculte(self,id,nom, nb_annee): 
        data_frais_divers={
            'id':id, 
            'nom':nom,
            'nb_annee':nb_annee,
        }
        return self._send_request("v1/post-faculte", data=data_frais_divers)
        
    
    def etudiant_promus_to(self,annee_actuelle,niveau_actuel,classe_actuelle,annee_f,niveau_f,classe_f):
        data_promus = {
            'annee_academique_id' : annee_actuelle,
            'niveau_id' : niveau_actuel,
            'classes_id' : classe_actuelle,

            'annee_academique_future' : annee_f,
            'niveau_future' : niveau_f,
            'classe_future' : classe_f
            }
        return self._send_request("v1/etudiant-promus-to", data=data_promus) 
    
    def student_live(self,search_term):    
        params = {
            "val": search_term
            }
        return self._send_request(f"v1/live-student", method='POST', data=params) 

    def supprimer_paiement_recu(self, id, indexs,user_id):
        params ={
            'id' : id, 
            'index' : indexs, 
            'user_id': user_id
        }
        return self._send_request("v1/delete-paiement", data=params)

    def logout(self): 
        return self._send_request("v1/auth/logout")
    
    def all_ventes(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/vente", method='GET', data=params)
    
    def all_cours(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/cours", method='GET', data=params)
    
    def cours_show(self,cours):
        return self._send_request(f"v1/cours/{cours}", method='GET') 

    def all_programme(self, search=None, page=1, anneeId=None,class_id=None,niveauId=None):
        params = { 
            "page": page or 1, 
        }
        if search:
            params["search"] = search
        if anneeId:
            params["annee_academique_id"] = anneeId
        if class_id:
            params["class_id"] = class_id
        if niveauId:
            params["niveau_id"] = niveauId
 
        # params = {k: v for k, v in params.items() if v is not None}
        return self._send_request("v1/programme", method='GET', data=params)      
        # params = {"search": search_term, "page": page,"class_id":class_id,"annee_academique_id":anneeId,"niveau_id":niveauId} #if search_term else {"page": page}
        # return self._send_request("v1/programme", method='GET', data=params)
    
    def programme_show(self,programme):
        return self._send_request(f"v1/programme/{programme}", method='GET') 

    def all_admin(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page} 
        return self._send_request("v1/personnel", method='GET', data=params) 
    
    def admin_show(self,personnel):
        return self._send_request(f"v1/personnel/{personnel}", method='GET') 

    def all_teacher(self,search_term=None, page=1): 
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/professeur", method='GET', data=params) 
    
    def teacher_show(self,professeur):
        return self._send_request(f"v1/professeur/{professeur}", method='GET') 
        # try:
        #     url = f"{self.ip()}professeur/{professeur}"
    
    def all_student(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/etudiant", method='GET', data=params) 
    
    def student_show(self,etudiant):
        return self._send_request(f"v1/etudiant/{etudiant}", method='GET') 
    
    def all_student_(self): 
        return self._send_request("load-etudiant", method='GET') 

    def all_notes(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page} 
        return self._send_request("v1/coursEtudiant", method='GET', data=params) 
    
    def notes_show(self,coursEtudiant):
        return self._send_request(f"v1/coursEtudiant/{coursEtudiant}", method='GET') 

    def all_paiement(self,search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/paiement", method='GET', data=params) 
    
    def paiement_show(self,paiement):
        return self._send_request(f"v1/paiement/{paiement}", method='GET') 
    
    def all_depenses(self,search_term=None,page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request("v1/depense", method='GET', data=params)
    
 
    def all_logs(self,search_term=None, page=1, action=None, model=None): 
        params = {
            "page": page
        }
        if search_term:
            params["search"] = search_term
        if action:
            params["action"] = action
        if model:
            params["model"] = model

        return self._send_request("v1/logs-graphic", method='GET', data=params)
    
    def logs_row_show(self,item): 
        return self._send_request(f"v1/logs-graphic-show/{item}", method='GET')
    
    def delete_depense(self, id_depense):
        params ={
            'id_depense' : id_depense, 
        }
        return self._send_request("v1/delete-depense", method='GET', data=params)
    
    def delete_student(self, id):
        params ={
            'student_id' : id, 
        }
        return self._send_request("v1/delete-student", method='GET', data=params)

    
    def delete_order(self, vente, id):
        params ={
            'vente' : vente,
            'vente_id' : id,
        } 
        return self._send_request("v1/vente-delete", method='GET', data=params)
    def verifier_donnees(self):
        return self._send_request("v1/get-profile", method='GET')
    
    def enregistrer_profile(self, nom,email,ligne1,ligne2,adresse,logo_image_path):
        # url = f"{self.ip()}profile"
        payload={
        'nom':nom,
        'email':email,
        'ligne1':ligne1,
        'ligne2':ligne2,
        'adresse':adresse,
        "logo_image_base64": logo_image_path,
        'logo_image_path':logo_image_path,
        }
        return self._send_request("v1/profile", method='POST', data=payload)
    
    def enregistrer_classe(self,id, niveau_id, nom_classe):
        # url = f"{self.ip()}classes"
        payload={           
            'id':id,
            'niveau_id':niveau_id,
            'nom_classe':nom_classe,
        }
        return self._send_request("v1/classes", method='POST', data=payload)
    
    def config_donnees(self):
        return self._send_request("v1/get-profile", method='GET')
    
    def verify_sanctum_token(self):
        return self._send_request("v1/verify-token", method='GET')
    
    def get(self, endpoint):
        return self._send_request(endpoint, method='GET')
        # url_str = f"{self.ip()}{endpoint}"
    
    
    def toggleAccordionAndPay(self,niveauId,anneeId, studentId,classeId,  annee_academique, faculte_id):
        params = {
            'niveau': niveauId,
            'annee_a': anneeId,
            'etudiant': studentId,
            'classe': classeId,
            'annee_academique': annee_academique,
            'faculte': faculte_id,
        }
        # print(params)
        return self._send_request("v1/next-payment-step", method='GET', data=params) 
    
    def data_for_dashbord(self, search_term=None):
        params = {"search": search_term } if search_term else {}
        return self._send_request("v1/dashboard", method='GET',data=params)

    def get_abonnement(self):
        return self._send_request("v1/abonnement", method='GET')

    def teacher_combo(self):
        return self._send_request("v1/prof-for-combo", method='GET') 
    
    def roles(self):
        return self._send_request("v1/role", method='GET')  
    
    def permissions(self):
        return self._send_request("v1/permission", method='GET')  
    
    def cours_combo(self):
        return self._send_request("v1/for-combo-cours", method='GET')
     
    
    def classes_show_check(self):
        return self._send_request("v1/cl-load-asses_", method='GET') 
    
    def verify_authorization_token(self, mac):
        return self._send_request(f"v1/client-authorisation-connect/{mac}", method='GET')
     
    
    def get_student_with_params_payment(self,etudiant):
        return self._send_request(f"v1/fetch-data-with-payment-params/{etudiant}", method='GET')
    
    def all_year(self, page=1):
        params = {"page": page}
        return self._send_request("v1/anneeAcademique", method='GET', data=params) 
    
    def year_show(self,anneeAcademique):
        return self._send_request(f"v1/anneeAcademique/{anneeAcademique}", method='GET') 
    
    def enregistrer_annee_academique(self,id, date_debut, date_fin, niveau_detude,combo_status): 
        payload={
            'id':id,
            'date_debut':date_debut,
            'date_fin':date_fin,
            'niveau_detude':niveau_detude,
            'status' :combo_status
        }
        return self._send_request("v1/anneeAcademique", method='POST', data=payload)


    def all_classes(self, page=1):
        params = {"page": page}
        return self._send_request("v1/classes", method='GET', data=params)
    
    def classes_show(self,classes):  
        return self._send_request(f"v1/classes/{classes}", method='GET')
    
    def all_register_fee(self, page=1):
        # params = {"search": search_term, "page": page} if search_term else {"page": page}
        params = {"page": page}
        return self._send_request("v1/fraisDinscription", method='GET', data=params)
    
    def register_fee_show(self,fraisDinscription):
        return self._send_request(f"v1/fraisDinscription/{fraisDinscription}", method='GET') 
    
    
    def enregistrer_frais_dinscription(self,id, prix, niveau_id, anneeAc): 
        payload={
            'prix':prix,
            'id':id,
            'niveau_id':niveau_id,
            'anneeAc':anneeAc,
        }
        return self._send_request("v1/fraisDinscription", method='POST', data=payload)

        # try:
        #     url = f"{self.ip()}fraisDinscription"
    
    def all_faculte(self, page=1):
        params = {"page": page}
        return self._send_request("v1/faculte", method='GET', data=params)
    
    def get_all_faculte(self): 
        return self._send_request("v1/get-all-faculte", method='GET')
    
    def faculte_param_show(self, faculte):
        return self._send_request(f"v1/show-faculte/{faculte}", method='GET')
 
    def all_params_exam(self, page=1):
        params = {"page": page}
        return self._send_request("v1/paramsExam", method='GET', data=params) 
    
    def params_exam_show(self,paramsExam):
        return self._send_request(f"v1/paramsExam/{paramsExam}", method='GET' )    
    
    def params_exam_show(self,paramsExam):
        return self._send_request(f"v1/paramsExam/{paramsExam}", method='GET')

    def all_payment_param(self, page=1):
        params = {"page": page}
        return self._send_request("v1/parametrePaiement", method='GET', data=params) 
    
    def enregistrer_parametre_de_paiement(self, id,niveau_id,faculte_id,classe,echeance,devise,anneeAcademique,nb_echeance,montant,montant_par,accessoires): 
        payload={
            'id':  id,
            'niveau_id':  niveau_id,
            'faculte_id':  faculte_id,
            'classe':  classe,
            'echeance':  echeance,
            'devise':  devise,
            'anneeAcademique':  anneeAcademique,
            'nb_echeance':  nb_echeance,
            'montant':  montant or 0.0,
            'montant_par':  montant_par,
            'accessoires':  accessoires
        } 
        return self._send_request("v1/parametrePaiement", method='POST', data=payload)
    
    def enregistrer_param_exams(self,id, niveau_id, annee_academique_id, evaluation_par): 
        payload={
            'id':id,
            'niveau_id':niveau_id,
            'annee_academique_id':annee_academique_id,
            'evaluation_par':evaluation_par,
        }
        return self._send_request("v1/paramsExam", method='POST', data=payload)
        
    
    def payment_param_show(self,parametrePaiement):
        return self._send_request(f"v1/parametrePaiement/{parametrePaiement}", method='GET') 
 

    def all_frais_divers_param(self, page=1):
        params = {"page": page}
        return self._send_request("v1/frais-divers-index", method='GET', data=params)

    def frais_divers_param_show(self, fraisDivers):
        return self._send_request(f"v1/show-frais-divers/{fraisDivers}", method='GET')
    
    def student_print_recu_inscrit(self,student_id):
        return self._send_request(f"v1/print-recu-inscrit/{student_id}", method='GET', types='pdf')


    def recu_paiement(self,id, keys):
        data_recu = {
            "id": id,
            "key": keys, 
            }
        return self._send_request(f"v1/print-recu", method='POST',data=data_recu)#, types='pdf') 
    
    def student_print(self,id, mois=None, session=None):        
        data_bulletin = {
            "bulletin": id,
            "mois": mois,
            "session":session
            } 
        return self._send_request("v1/imprime-bulletin", data=data_bulletin)#, types='pdf') 
    
    def student_print_mas_bulletin(self,annee_academique, mois, classe):    
        data_bulletin = {
            "annee_academique": annee_academique,
            "mois": mois,
            "classe": classe,
            }
        return self._send_request("v1/imprime-mas-bulletin", data=data_bulletin)#, types='pdf') 
    
    def global_rapport(self, date_debut, date_fin,type_): 
        data__for_print = {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'type':type_
        }
        return self._send_request("v1/print-global-repport", data=data__for_print, types='pdf') 

    def administratif_imprimer_rapport(self, identifiant,classe,annee_ac,cycle): 
        data__for_print = {
        'identifiant':identifiant,
        'classe':classe,
        'annee_ac':annee_ac,
        'cycle':cycle,
        } 
        return self._send_request("v1/print-repport-register", data=data__for_print, types='pdf') 
    
    def pedagogique_imprimer_rapport(self, identifiant,classe,annee_ac,cycle,mois): 
        data__for_print = {
        'identifiant':identifiant,
        'classe':classe,
        'annee_ac':annee_ac,
        'cycle':cycle,
        'mois':mois
        } 
        print(data__for_print)
        return self._send_request("v1/print-repport-pedagogique", data=data__for_print, types='pdf')
        

    def desicion_de_fin_dannee(self, classe,annee_ac,is_excel): 
        data__for_print = {
        'classe':classe,
        'annee_ac':annee_ac,
        'is_excel':is_excel
        } 
        type_ = 'excel' if is_excel else 'pdf'
        return self._send_request("v1/print-repport-decision", data=data__for_print, types=type_)

    def pedagogique_imprimer_rapport_exel(self, identifiant,classe,annee_ac,cycle): 
        data__for_print = {
        'identifiant':identifiant,
        'classe':classe,
        'annee_ac':annee_ac,
        'cycle':cycle,
        }
        return self._send_request("v1/print-repport-pedagogique-exel", data=data__for_print, types='pdf')   

    def financier_imprimer_rapport(self, classe, date_debut,date_fin,versement): 
        data__for_print = {
            "classe":classe,
            "date_debut":date_debut,
            "date_fin":date_fin,
            "versement":versement,
        }
        print(data__for_print)
        return self._send_request("v1/print-rapport-paiement", data=data__for_print, types='pdf')
    
    def student_print_details(self, student_id): 
        data__for_print = {
          'student_id': student_id,
        } 
        return self._send_request("v1/student-print-details", data=data__for_print, types='pdf')
    
    def get_Vente_receipt(self,id): 
        payload = {
            'id':id,
            }
        return self._send_request(f"v1/print-recu-vente/{id}", method="GET", types='pdf')






    ###############################################################################################################################################          #####################################################
    def niveau_index(self):
        return self._send_request("v1/niveau", method="GET")

    def class_and_other(self,niveau_id):
        return self._send_request(f"v1/niveau-with-class/{niveau_id}", method="GET")
    
    def annee_academique(self):
        return self._send_request("v1/annee-academique", method="GET")
    
    def delete___students(self, etudiant):
        return self._send_request(f"v1/etudiant/{etudiant}", method="GET")
    
    def update_student_status_classe(self, classe_id, new_state, delete):
        payload = {
            'delete' : delete,
            "classe_student_id": classe_id,
            "state": new_state,
            }
        return self._send_request(f"v1/update-etudiant-classe", method="PATCH", data=payload)

    def get_student_details(self, payload): 
        return self._send_request(f"v1/student-specific-details", method="POST", data=payload)
    
    def student_live(self,search_term):
        payload = {
            "val": search_term
            }
        return self._send_request(f"v1/live-student", method="POST", data=payload)
    
    def search_student(self,search_term):
        payload = {
            "val": search_term
            }
        return self._send_request(f"v1/search/etudiant/", method="POST", data=payload)
    
    def student_with_classe(self, classe,annee_id):
        params ={
                'classe_id':classe,
                'annee_id':annee_id
            }
        print(params)
        return self._send_request("v1/student-with-classe", method="GET", data=params)
    
    # def teacher_combo(self):
    #     return self._send_request("prof-for-combo", method="GET")
    
    def roles(self):
        return self._send_request("v1/role", method="GET") 
    
    def permissions(self):
        return self._send_request("v1/permission", method="GET") 

    # def cours_combo(self):
    #     return self._send_request("cours-for-combo", method="GET") 

    # def get_student_with_params_payment(self,etudiant):
    #     return self._send_request(f"fetch-data-with-payment-params/{etudiant}", method="GET") 
    
    # def toggleAccordionAndPay(self,niveauId,anneeId, studentId,classeId,  annee_academique, faculte_id):
    #     params = {
    #         'niveau': niveauId,
    #         'annee_a': anneeId,
    #             'etudiant': studentId,
    #             'classe': classeId,
    #             'annee_academique': annee_academique,
    #             'faculte': faculte_id,
    #     } 
    #     return self._send_request("next-payment-step", method="GET", data=params) 
    
    def students_for_notes(self,niveau,cours,classe,annee_academique,faculte,session):
    
        params = {
            "niveau": niveau,
            "cours": cours,
            "class": classe,
            "annee_academique": annee_academique,
            'faculte':faculte,
            'session':session,
            } 
        return self._send_request("v1/cours-etudiant-add-note", method="POST", data=params)
    
    
    def getPermissionByRole(self,role):
        return self._send_request(f"v1/get-permission-by-role/{role}", method="GET")
    
    def fetchDataWithPermission(self, data):
        params = {"data": data} 
        return self._send_request("v1/fetch-data-with-permission", method="GET", data=params)
    
    def fetchDataWithRole(self, data):
        params = {"data": data} 
        return self._send_request("v1/fetch-data-with-role", method="GET", data=params)
    
    def assign_permission_to_role(self,role, user_id, permission): 
        payload={        
            'role':role,
            'user_id':user_id,
            'permission':permission,
        }
        return self._send_request("v1/assign-permission-to-role", method="POST", data=payload)
    
    def assign_role_to_user(self,role, user_id): 
        payload={        
            'user_id':user_id,
            'role':role
        }
        return self._send_request("v1/assign-role-to-user", method="POST", data=payload)

    def vente_show(self,vente):
        return self._send_request(f"v1/order-vente/{vente}", method="GET")
    
    def delete_order(self, vente, id):
        params ={
            'vente' : vente,
            'vente_id' : id,
        }
        return self._send_request("v1/vente-delete", method="GET", data=params)

    def store_other_transaction(self,data):
        return self._send_request("v1/other-transaction", data=data)

    def store_other_transaction_show(self,trans_id):
        return self._send_request(f"v1/other-transaction/{trans_id}", method="GET")
    
    def edit_other_transaction(self,trans_id,payload):
        return self._send_request(f"v1/edit-other-transaction/{trans_id}", method="PATCH",data=payload)

    def all_other_transaction(self, search_term=None, page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}
        return self._send_request(f"v1/other-transaction", method="GET", data=params)

    
    def delete_prof(self, professeur):
        return self._send_request(f"v1/delete-professeur/{professeur}", method="GET")
    
    def delete_perso(self, personnel):
        return self._send_request(f"v1/delete-personnel/{personnel}", method="GET")
    
    def fetch_data_note_for_edit(self, notes,evaluation_examen,cours,annee_academique,cours_type):
        payload = {
            'notes':notes,
            'examen':evaluation_examen,
            'cours':cours,
            'annee_academique':annee_academique,
            'type_matiere':cours_type
            }
        return self._send_request("v1/cours-etudiant-edit-note", method="POST", data=payload)

    def get_promus(self,annee, niveau, classe):
        payload = {
           'data':{
            'annee_academique_id':annee,
            'niveau_id':niveau,
            'classes_id':classe,
           }
            }
        return self._send_request("v1/get-promus", method="POST", data=payload)
    
    def etudiant_promus_to(self,annee_actuelle,niveau_actuel,classe_actuelle,annee_f,niveau_f,classe_f):
        payload = {
            'annee_academique_id' : annee_actuelle,
            'niveau_id' : niveau_actuel,
            'classes_id' : classe_actuelle,

            'annee_academique_future' : annee_f,
            'niveau_future' : niveau_f,
            'classe_future' : classe_f
            }
        return self._send_request("v1/etudiant-promus-to", method="POST", data=payload)
    
    def delete_params_exam(self, paramsExam):
        return self._send_request(f"v1/delete-paramsExam/{paramsExam}", method="GET")

    def delete_classe(self, classe):
        return self._send_request(f"v1/delete-classe/{classe}", method="GET")

    def delete_faculte(self, faculte):
        return self._send_request(f"v1/delete-faculte/{faculte}", method="GET")

    def delete_anneeAcademique(self, anneeAcademique):
        return self._send_request(f"v1/delete-anneeAcademique/{anneeAcademique}", method="GET")

    def delete_frais_divers(self, frais_divers):
        return self._send_request(f"v1/delete-frais_divers/{frais_divers}", method="GET")

    def delete_frais(self, frais):
        return self._send_request(f"v1/delete-frais/{frais}", method="GET")

    def delete_payment_param(self,parametrePaiement):
        return self._send_request(f"v1/delete-parametrePaiement/{parametrePaiement}", method='GET') 
    
    def delete_programme(self, programme):
        return self._send_request(f"v1/delete-programme/{programme}", method="GET")
    
    def delete_cours(self, cours):
        return self._send_request(f"v1/delete-cours/{cours}", method="GET")
    

    def all_loans(self,search_term=None,page=1):
        params = {"search": search_term, "page": page} if search_term else {"page": page}     
        return self._send_request("v1/get-loans", method="GET", data=params)
    
    def store_loans(self,data_):
        payload = {
          'user_id':data_['user_id'],
            'amount':data_['amount'],
            'term_months':data_['term_months'] if 'term_months' in data_ else 1,
            'interest_rate':data_['interest_rate'] if 'interest_rate' in data_ else 0, 
            'monthly_payment':data_['monthly_payment'] if 'monthly_payment' in data_ else None, 
            }
        return self._send_request("v1/post-loans", method="POST", data=payload)

    def get_data_user_for_loans(self):     
        return self._send_request("v1/get-data-user-for-loans", method="GET")
    
    def store_loans_repayment(self, data):
        return self._send_request("v1/loans/repay", method="POST", data=data)
    




    

#     from PyQt5.QtNetwork import QSslConfiguration, QSslCertificate

# def configure_ssl(manager):
#     # Charger le certificat racine
#     with open("C:/ecole_1/mysql-8.0.41-winx64/certs/ca.pem", "rb") as f:
#         ca_cert = QSslCertificate(f.read())

#     # Ajouter à la config SSL globale
#     ssl_config = QSslConfiguration.defaultConfiguration()
#     existing_cas = ssl_config.caCertificates()
#     existing_cas.append(ca_cert)
#     ssl_config.setCaCertificates(existing_cas)

#     QSslConfiguration.setDefaultConfiguration(ssl_config)

#     # Optionnel: connecter un gestionnaire d'erreur SSL
#     manager.sslErrors.connect(lambda reply, errors: handle_ssl_errors(reply, errors))

# def handle_ssl_errors(reply, errors):
#     for err in errors:
#         print(f"❌ SSL Error: {err.errorString()}")
    
#     # 👉 Accepter les erreurs SSL (auto-signé par ex)
#     reply.ignoreSslErrors()


# certutil -addstore -f "Root" "C:\Program Files\ecole-serve\Apache24\conf\ca.pem"


    # "C:\Program Files\ecole-serve\Apache24\conf\ca.pem"

    # certutil -addstore -f "Root" "C:\Program Files\ecole-serve\Apache24\conf\ca.pem"

    # icacls "C:\Program Files\ecole-serve\Apache24\conf\ca.pem" /grant "Everyone:(R)"

    # {"identifiant": "false", "classe": "0ec8281b-7171-49fe-b656-901c3f5c67ae", "annee_ac": "8b0f7424-e2db-42f6-a64d-d1d1ea2f68d8", "cycle": "e7f8d26b-e3c5-11ef-9913-3e7db61a5f8d", 'mois': 'Octobre'}


    

    



    
    

   