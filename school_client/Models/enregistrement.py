import requests
# from Config import BASE_URL 
from Config import HEADERS
from Helper.Token_manager import TokenManager
from Helper.Ip_manager import Ip_manager


class Save_data:
    def __init__(self):
        self.ip_manager = Ip_manager()
        self.token__manager = TokenManager()
        

    def ip(self):
        print()
        return f"https://{self.ip_manager.get_server_ip()}/api/v1/"
    
    def token_manager(self):
        return self.token__manager.get_token()

    def headers_token(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {self.token_manager()}"
        }
    def authorization_connect(self,mac,username):
        url = f"{self.ip()}client-authorisation-connect"
        payload = {
            "client_mac": mac,
            "client_name": username
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15) 

            response_data = response.json()   
        
            if response.status_code == 200:
                return response_data  
            else:
                print(response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def connect(self,email, password):
        url = f"{self.ip()}login" 

        payload = {
            "email": email,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # print(url)
        try:
            response = requests.post(url, json=payload, headers=self.headers_token(), timeout=15) 

            response_data = response.json()   
        
            if response.status_code == 200:
                return response_data  
            else:
                print(response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def reset_password_and_connect(self,password, password_confirm,user_id):
        url = f"{self.ip()}password-change-user" 

        payload = {
            "password": password,
            "password_confirm": password_confirm,
            "user_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # print(url)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=35) 

            response_data = response.json()   
        
            if response.status_code == 200:
                return response_data  
            else:
                print(response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")
        
    def reset_password_prof(self,password, password_confirm,user_id):
        url = f"{self.ip()}change-password-teacher" 

        payload = {
            "password": password,
            "password_confirm": password_confirm,
            "professeur_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {self.token_manager()}"
        }
        # print(url)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=33) 

            response_data = response.json()   
        
            if response.status_code == 200:
                return response_data  
            else:
                print(response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def reset_password_perso(self,password, password_confirm,user_id):
        url = f"{self.ip()}change-password-personnel" 

        payload = {
            "password": password,
            "password_confirm": password_confirm,
            "personnel_id": user_id
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Authorization": f"Bearer {self.token_manager()}"
        }
        # print(url)
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=33) 

            response_data = response.json()   
        
            if response.status_code == 200:
                return response_data  
            else:
                print(response_data)
                return response_data

        except requests.exceptions.RequestException as e:
            return print(f"{e}")

    def enregistrer_etudiant(self, student_id,nom,prenom,telephone,sexe,date_de_naissance, adresse,lieu_de_naissance,  religion,niveau_id,classe_actuelle_id,annee_academique_id,faculte_id,email,nom_responsable,prenom_responsable,email_responsable,sexe_responsable,telephone_responsable,adresse_responsable,aide_financiere,documentss):
        token_manager = TokenManager()
        url = f"{self.ip()}etudiant" 

        payload = {
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

        # headers = {
        #     'Content-Type': 'application/json',
        #     'Accept': 'application/json',
        #     "Authorization": f"Bearer {self.headers_token}"
        # }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    print("La réponse n'est pas au format JSON.")
                    return None
            else:
                print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()


        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # =============================================== __PROFESSEUR__===============================
        
    def enregistrer_professeur(self,id,nom, prenom, email, sexe, adresse, matiere_enseignee,telephone,notif_prof):
        url = f"{self.ip()}professeur"

        payload={
            'id':id,
            'nom':nom,
            'prenom':prenom,
            'email':email,
            'notification':notif_prof,
            'sexe':sexe,
            'adresse':adresse,
            'matiere_enseignee':matiere_enseignee,
            'telephone':telephone,
        } 
    
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    print("La réponse n'est pas au format JSON.")
                    return None
            else:
                return response.json()
                

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None

    def active_teacher(self, id):
        url = f"{self.ip()}active-teacher"
        payload={
            'id':id
        } 
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    return response.json()
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    def active_personnel(self, id):
        url = f"{self.ip()}active-personnel"
        payload={
            'id':id
        } 
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    return response.json()
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
    # ========================================== __ADMINISTRATION__ ========================================
    def enregistrer_admin(self,id, nom, prenom, email, sexe, adresse, role,telephone):
        url = f"{self.ip()}personnel"
        payload={
            'id':id,
            'nom':nom,
            'prenom':prenom,
            'email':email,
            'sexe':sexe,
            'adresse':adresse,
            'role':role,
            'telephone':telephone,
        }         
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # ========================================== __COURS__ ========================================
    def enregistrer_cours(self, CoursesObject):
        url = f"{self.ip()}cours"
        payload={
            'CoursesObject':CoursesObject
        } 
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    def enregistrer_programme(self, programmeCoursObject):
        url = f"{self.ip()}programme"
        payload={
            'programmeCoursObject':programmeCoursObject
        } 
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    
    # ========================================== __PAIEMENT__ ========================================
    def enregistrer_paiement(self, montant_verser,niveau_id,etudiant_id,identifiant,classe,echeance,prenom,nom,annee_academique,mois,accessoires):
        url = f"{self.ip()}post-payment-save"
        payload={
            'niveau_id':niveau_id,
            'etudiant_id':etudiant_id,
            'identifiant':identifiant,
            'classe':classe,
            'echeance':echeance,
            'prenom':prenom,
            'nom':nom,
            'annee_academique':annee_academique,
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
        # print(payload)
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # ========================================== __NOTES COURS__ ========================================
    def enregistrer_cours_notes(self, controle,examen,cours,type_matiere,coefficients,session,note_de_passage,professeur_id,annee_academique,notes):
        url = f"{self.ip()}coursEtudiant"
        payload={
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
        print(payload)
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}  \n\n {payload} \n\n ")
            return None
        
    # =================================== __ANNEE ACADEMIQUE__ =====================================
    def enregistrer_annee_academique(self,id, date_debut, date_fin, niveau_detude,combo_status):
        url = f"{self.ip()}anneeAcademique"
        payload={
            'id':id,
            'date_debut':date_debut,
            'date_fin':date_fin,
            'niveau_detude':niveau_detude,
            'status' :combo_status
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # ============================== __ANNEE PARAMETRE DE PAIEMENT__ ================================
    def enregistrer_parametre_de_paiement(self, id,niveau_id,faculte_id,classe,echeance,devise,anneeAcademique,nb_echeance,montant,montant_par,accessoires):
        url = f"{self.ip()}parametrePaiement"
        payload={
    'id':  id,
    'niveau_id':  niveau_id,
    'faculte_id':  faculte_id,
    'classe':  classe,
    'echeance':  echeance,
    'devise':  devise,
    'anneeAcademique':  anneeAcademique,
    'nb_echeance':  nb_echeance,
    'montant':  montant,
    'montant_par':  montant_par,
    'accessoires':  accessoires
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None


    # =================================== __PARAMETRE DES EXAMENS__ =====================================
    def enregistrer_param_exams(self,id, niveau_id, annee_academique_id, evaluation_par):
        url = f"{self.ip()}paramsExam"
        payload={
            'id':id,
            'niveau_id':niveau_id,
            'annee_academique_id':annee_academique_id,
            'evaluation_par':evaluation_par,
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
        

    # =================================== __FRAIS DINSCRIPTION__ =====================================
    def enregistrer_frais_dinscription(self,id, prix, niveau_id, anneeAc):
        url = f"{self.ip()}fraisDinscription"
        payload={
            'prix':prix,
            'id':id,
            'niveau_id':niveau_id,
            'anneeAc':anneeAc,
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
            # =================================== __FRAIS DINSCRIPTION__ =====================================
    def enregistrer_frais_divers(self,id, prix,description, niveau_id, anneeAc):
        url = f"{self.ip()}fraisDivers"
        payload={
            'description':description,
            'prix':prix,
            'id':id,
            'niveau_id':niveau_id,
            'anneeAc':anneeAc,
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # =================================== __classe__ =====================================
    def enregistrer_classe(self,id, niveau_id, nom_classe):
        url = f"{self.ip()}classes"
        payload={
            
            'id':id,
            'niveau_id':niveau_id,
            'nom_classe':nom_classe,
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    # =================================== __ profile__ =====================================
    def enregistrer_profile(self, nom,email,ligne1,ligne2,adresse,logo_image_path):
        url = f"{self.ip()}profile"
        payload={
        'nom':nom,
        'email':email,
        'ligne1':ligne1,
        'ligne2':ligne2,
        'adresse':adresse,
        'logo_image_path':logo_image_path,
        }
        # print(HEADERS)
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    return response.json()
            else:
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    def logout(self):
        url = f"{self.ip()}logout"
        try:
            response = requests.post(url,headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return True
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        

    # =================================== __PERMISSION AND ROLE__ =====================================
    def assign_permission_to_role(self,role, user_id, permission):
        url = f"{self.ip()}assign-permission-to-role"
        payload={        
            'role':role,
            'user_id':user_id,
            'permission':permission,
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    def assign_role_to_user(self,role, user_id):
        url = f"{self.ip()}assign-role-to-user"
        payload={        
            'user_id':user_id,
            'role':role
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
    def enregistrer_vente(self,id,items, etudiant_id):
        url = f"{self.ip()}vente"
        payload={        
            'id':id,
            'items':items,
            'etudiant_id':etudiant_id
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None 

    def enregistrer_depense(self,id,description_depense, prix_depense):
        url = f"{self.ip()}depense"
        payload={        
            'id':id,
            'description':description_depense,
            'prix':prix_depense
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers_token())

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return response_data
                except ValueError:
                    # print(f"La réponse n'est pas au admin format JSON. : {response.json()}" )
                    return response.json()
            else:
                # print(f"Erreur dans la requête, code de statut: {response.json()}")
                return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête : {e}")
            return None
        
        

     
    
