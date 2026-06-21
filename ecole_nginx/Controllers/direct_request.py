import pymysql
from decimal import Decimal
import logging
import pymysql
import uuid
import bcrypt
import re
from datetime import datetime

from Helper.db import Database  
import random
import string
import json

db = Database()

def update_certificat(request):
    # Validation des données
    data = request
    
    if not data or 'certi_key' not in data:
        return {
            'errors': {'certi_key': ['Le champ certi_key est requis.']}
        }, 422
    
    certi_key = data['certi_key']
    
    if not isinstance(certi_key, str) or not certi_key.strip():
        return {
            'errors': {'certi_key': ['Le champ certi_key doit être une chaîne valide.']}
        }, 422
    
    try:
        connection = db.get_connection()
        
        with connection:
            with connection.cursor() as cursor:
                # Récupérer tous les clients avec certi_key non null
                sql_select = "SELECT * FROM client_infos WHERE certi_key IS NOT NULL"
                cursor.execute(sql_select)
                clients = cursor.fetchall()
                
                # Mettre à jour chaque client
                for client in clients:
                    sql_update = "UPDATE client_infos SET certi_key = %s WHERE id = %s"
                    cursor.execute(sql_update, (certi_key, client['id']))
                
                # Valider les modifications
                connection.commit()
                
                # Récupérer les données mises à jour
                sql_updated = "SELECT * FROM client_infos WHERE certi_key IS NOT NULL"
                cursor.execute(sql_updated)
                updated_data = cursor.fetchall()
                
            return {
                'success': 'Autorisation modifiée',
                'data': updated_data
            }, 200
            
    except pymysql.MySQLError as e:
        logging.error(f"Erreur MySQL: {e}")
        return {
            'errors': str(e)
        }, 422
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        return {
            'errors': str(e)
        }, 422
    
def first_check():
    try:
        connection = db.get_connection()
        
        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM users LIMIT 1"
                cursor.execute(sql)
                user = cursor.fetchone()
                
                if user:
                    return {'status': True}, 200
                else:
                    return {'status': False}, 422
                    
    except Exception as e:
        print(f"Erreur: {e}")
        return {'error': str(e)}, 500
    

def fill_roles_and_permission():
    try:        
        connection = db.get_connection()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with connection:
            with connection.cursor() as cursor:
                # 1. Rôles avec UUID
                roles = [
                    'admin', 'user', 'student', 'teacher', 'Directeur',
                    'Responsable financier', 'Responsable pédagogique', 'Enseignant',
                    'Secrétaire général', 'Responsable des admissions', 'Conseiller pédagogique',
                    'Responsable informatique', 'Surveillant', 'Psychologue scolaire',
                    'Gestionnaire de la bibliothèque', 'Responsable des transports', 'Comptable',
                    'Chargé de la communication', 'Responsable des activités extrascolaires',
                    'Responsable des ressources humaines', 'Chef de département', 'Formateur',
                    'Technicien de laboratoire', 'Coordinateur de projet'
                ]
                
                # UPSERT des rôles avec UUID
                for role in roles:
                    role_id = str(uuid.uuid4())
                    sql = """
                    INSERT INTO roles (id, name, guard_name, created_at, updated_at) 
                    VALUES (%s, %s, 'web', %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), guard_name = VALUES(guard_name), updated_at = VALUES(updated_at)
                    """
                    cursor.execute(sql, (role_id, role, current_time, current_time))
                
                # 2. Permissions individuelles avec UUID
                permissions = [
                    'Ajouter etudiant', 'Modifier permission', 'Supprimer etudiant', 'Voir permission',
                    'Ajouter paiement', 'Modifier paiement', 'Supprimer paiement', 'Voir paiement',
                    'Ajouter classe', 'Modifier classe', 'Supprimer classe', 'Voir classe',
                    'Ajouter cours', 'Modifier cours', 'Supprimer cours', 'Voir cours',
                    'Ajouter note', 'Modifier note', 'Supprimer note', 'Voir note',
                    'Ajouter personnel', 'Modifier personnel', 'Supprimer personnel', 'Voir personnel',
                    'Ajouter profile', 'Modifier profile', 'Supprimer profile', 'Voir profile',
                    'Ajouter professeur', 'Modifier professeur', 'Supprimer professeur', 'Voir professeur',
                    'Ajouter role', 'Modifier role', 'Supprimer role', 'Voir role',
                    'Ajouter parametre', 'Modifier parametre', 'Supprimer parametre', 'Voir parametre'
                ]
                
                # UPSERT des permissions individuelles avec UUID
                for permission in permissions:
                    permission_id = str(uuid.uuid4())
                    sql = """
                    INSERT INTO permissions (id, name, guard_name, created_at, updated_at) 
                    VALUES (%s, %s, 'web', %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), guard_name = VALUES(guard_name), updated_at = VALUES(updated_at)
                    """
                    cursor.execute(sql, (permission_id, permission, current_time, current_time))
                
                # 3. Permissions générées automatiquement avec UUID
                resources = [
                    'etudiant', 'paiement', 'classe', 'cours', 'note', 
                    'personnel', 'profile', 'professeur', 'role', 'parametre'
                ]
                actions = ['Ajouter', 'Modifier', 'Supprimer', 'Voir']
                
               #  for resource in resources:
               #      for action in actions:
               #          permission_name = f"{action} {resource}"
               #          permission_id = str(uuid.uuid4())
               #          sql = """
               #          INSERT INTO permissions (id, name, guard_name, created_at, updated_at) 
               #          VALUES (%s, %s, 'web', %s, %s)
               #          ON DUPLICATE KEY UPDATE name = VALUES(name), guard_name = VALUES(guard_name), updated_at = VALUES(updated_at)
               #          """
               #          cursor.execute(sql, (permission_id, permission_name, current_time, current_time))
                
                # 4. Niveaux avec UUID
                niveaux = ['Maternelle', 'Primaire', 'Secondaire', 'Universitaire']
                
                for niveau in niveaux:
                    niveau_id = str(uuid.uuid4())
                    sql = """
                    INSERT INTO niveaux (id, name,status, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE name = VALUES(name), updated_at = VALUES(updated_at)
                    """
                    cursor.execute(sql, (niveau_id, niveau,1, current_time, current_time))
                
                # 5. Assigner toutes les permissions au premier utilisateur avec le rôle admin
                # Récupérer le premier utilisateur
                cursor.execute("SELECT id FROM users LIMIT 1")
                user = cursor.fetchone()
                
                if user:
                    user_id = user['id']
                    
                    # Récupérer ou créer le rôle admin
                    cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
                    admin_role = cursor.fetchone()
                    
                    if not admin_role:
                        # Créer le rôle admin s'il n'existe pas
                        admin_role_id = str(uuid.uuid4())
                        sql_role = """
                        INSERT INTO roles (id, name, guard_name, created_at, updated_at) 
                        VALUES (%s, 'admin', 'web', %s, %s)
                        """
                        cursor.execute(sql_role, (admin_role_id, current_time, current_time))
                    else:
                        admin_role_id = admin_role['id']
                    
                    # Assigner le rôle admin à l'utilisateur avec UUID pour la table pivot
                    user_role_id = str(uuid.uuid4())
                    sql_user_role = """
                    INSERT INTO model_has_roles (role_id, model_type, model_id) 
                    VALUES (%s, %s, 'App\\\\Models\\\\User', %s)
                    ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
                    """
                    cursor.execute(sql_user_role, (admin_role_id, user_id))
                    
                    # Récupérer toutes les permissions
                    cursor.execute("SELECT id FROM permissions")
                    all_permissions = cursor.fetchall()
                    
                    # Assigner toutes les permissions à l'utilisateur avec UUID pour la table pivot
                    for permission in all_permissions:
                        user_permission_id = str(uuid.uuid4())
                        sql_user_permission = """
                        INSERT INTO model_has_permissions (permission_id, model_type, model_id) 
                        VALUES (%s, %s, 'App\\\\Models\\\\User', %s)
                        ON DUPLICATE KEY UPDATE permission_id = VALUES(permission_id)
                        """
                        cursor.execute(sql_user_permission, (permission['id'], user_id))
                
                connection.commit()
                return {'success': 'Rôles et permissions initialisés avec succès'}, 200
                
    except Exception as e:
        print(f"Erreur: {e}")
        return {'error': str(e)}, 500
    

def store_personnel_first(request):
    errors = {}

    # 🔹 1. Validation de base
    first = request.get("first", False)
    id_val = request.get("id")
    nom = request.get("nom")
    prenom = request.get("prenom")
    sexe = request.get("sexe")
    email = request.get("email")
    telephone = request.get("telephone")
    adresse = request.get("adresse")
    role = request.get("role")

    if not nom:
        errors["nom"] = ["Le champ nom est requis."]
    if not prenom:
        errors["prenom"] = ["Le champ prenom est requis."]
    if not email:
        errors["email"] = ["Le champ email est requis."]
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        errors["email"] = ["Le champ email doit être un email valide."]
    elif len(email) > 255:
        errors["email"] = ["Email trop long."]

    # requiredIf pour certains champs si not first
    if not first:
        if sexe is None:
            errors["sexe"] = ["Le champ sexe est requis."]
        if telephone is None:
            errors["telephone"] = ["Le champ telephone est requis."]
        if adresse is None:
            errors["adresse"] = ["Le champ adresse est requis."]
        if role is None:
            errors["role"] = ["Le champ role est requis."]

    if errors:
        return {"errors": errors}, 422
    connection=None
    cursor=None
    try:
        connection = db.get_connection()
        cursor = connection.cursor()

        # 🔹 2. Vérifier unicité email
        cursor.execute("SELECT id,userable_id FROM users WHERE email=%s", (email,))
        user_email_exists = cursor.fetchone()
        if user_email_exists and id_val != user_email_exists['userable_id']:
            return {"errors": {"email": ["Email déjà utilisé dans users."]}}, 422

        cursor.execute("SELECT id FROM personnels WHERE email=%s", (email,))
        perso_email_exists = cursor.fetchone()
        if perso_email_exists and id_val != perso_email_exists["id"]:
            return {"errors": {"email": ["Email déjà utilisé dans personnels."]}}, 422

        # 🔹 3. Defaults si first
        if first:
            sexe = ""
            telephone = "0000 000 00"
            adresse = "Mon Adresse"
            # récupérer rôle admin
            cursor.execute("SELECT id FROM roles WHERE name='admin' LIMIT 1")
            role_row = cursor.fetchone()
            role = role_row["id"] if role_row else None

        # 🔹 4. Transaction
        # connection.start_transaction()

        if id_val:
            # Update
            update_fields = {
                "nom": nom,
                "prenom": prenom,
                "sexe": sexe,
                "email": email,
                "telephone": telephone,
                "adresse": adresse,
            }
            set_clause = ", ".join(f"{k}=%s" for k in update_fields.keys())
            cursor.execute(f"UPDATE personnels SET {set_clause} WHERE id=%s", list(update_fields.values()) + [id_val])

            # Mettre à jour user
            cursor.execute("SELECT * FROM users WHERE userable_id=%s AND userable_type='App\\\\Models\\\\Personnel'", (id_val,))
            user = cursor.fetchone()
            if user:
                cursor.execute("UPDATE users SET name=%s, email=%s,updated_at=NOW() WHERE id=%s", (prenom, email, user["id"]))
                # Supprimer anciens rôles et assigner nouveau
                cursor.execute("DELETE FROM model_has_roles WHERE model_id=%s AND model_type='App\\Models\\User'", (user["id"],))
                cursor.execute("INSERT INTO model_has_roles (role_id, model_type, model_id) VALUES (%s, %s, %s)", (role, "App\\Models\\User", user["id"]))
        else:
            # Create
            new_id = str(uuid.uuid4())
            columns = "id,nom,prenom,sexe,email,telephone,adresse,created_at, updated_at"
            placeholders = "%s,%s,%s,%s,%s,%s,%s,NOW(),NOW()"
            values = [new_id,nom, prenom, sexe, email, telephone, adresse]
            cursor.execute(f"INSERT INTO personnels ({columns}) VALUES ({placeholders})", values)
            new_personnel_id = new_id

            # Créer user
            new_ids = str(uuid.uuid4())
            password_to_use = request.get("password") if first else "@#Itsme1"
            hashed_password = hash_password_for_laravel(password_to_use)
            cursor.execute(
                "INSERT INTO users (id,name,email,password,userable_id,userable_type,status,created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,1,NOW(),NOW())",
                (new_ids,prenom, email, hashed_password, new_personnel_id, "App\\Models\\Personnel")
            )
            new_user_id = new_ids

            # Assigner rôle
            cursor.execute("INSERT INTO model_has_roles (role_id, model_type, model_id) VALUES (%s,%s,%s)", (role, "App\\Models\\User", new_user_id))

        connection.commit()
        return {"success": "Operation reussie"}, 200

    except Exception as e:
        connection.rollback()
        import traceback
        traceback.print_exc()
        return {"errors": str(e)}, 500

    finally:
        if connection:
            cursor.close()
            connection.close()  
def hash_password_for_laravel(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8").replace("$2b$", "$2y$") 
    

def authorisation(request):
    
    # Si un ID est présent dans la requête
    if request and 'id' in request:
        # Validation des données
        data = request
        errors = {}
        
        # Validation de l'ID
        if not data.get('id'):
            errors['id'] = ['Le champ id est requis.']
        else:
            # Vérifier si l'ID existe dans la base de données
            try:
                connection = db.get_connection()
                with connection:
                    with connection.cursor() as cursor:
                        sql_check = "SELECT id FROM client_infos WHERE id = %s"
                        cursor.execute(sql_check, (data['id'],))
                        if not cursor.fetchone():
                            errors['id'] = ['Le id sélectionné est invalide.']
            except Exception as e:
                return {'errors': str(e)}, 422
        
        # Validation de certi_key
        if not data.get('certi_key'):
            errors['certi_key'] = ['Le champ certi_key est requis.']
        elif not isinstance(data.get('certi_key'), str):
            errors['certi_key'] = ['Le champ certi_key doit être une chaîne.']
        
        if errors:
            return {'errors': errors}, 422
        
        # Vérification de l'autorisation (simplifiée - à adapter selon votre logique)
        # authorize_with_admin_token(request, 'Modifier personnel')
        
        try:
            connection = db.get_connection()
            with connection:
                with connection.cursor() as cursor:
                    # Récupérer le client actuel
                    sql_select = "SELECT * FROM client_infos WHERE id = %s"
                    cursor.execute(sql_select, (data['id'],))
                    client = cursor.fetchone()
                    
                    if not client:
                        return {'errors': 'Client non trouvé'}, 404
                    
                    # Inverser l'autorisation (1 -> 0 ou 0 -> 1)
                    new_authorisation = 0 if client['authorisation'] == 1 else 1
                    
                    # Mettre à jour le client
                    sql_update = """
                    UPDATE client_infos 
                    SET authorisation = %s, certi_key = %s, updated_at = %s 
                    WHERE id = %s
                    """
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(sql_update, (new_authorisation, data['certi_key'], current_time, data['id']))
                    
                    connection.commit()
                    
                    return {
                        'success': 'Autorisation modifiée',
                        'authorisation': new_authorisation,
                        'id': data['id']
                    }, 200
                    
        except Exception as e:
            return {'errors': str(e)}, 422
    
    # Si pas d'ID → création/mise à jour
    data = request
    errors = {}
    
    # Validation des données
    if not data.get('client_mac'):
        errors['client_mac'] = ['Le champ client_mac est requis.']
    elif not isinstance(data.get('client_mac'), str):
        errors['client_mac'] = ['Le champ client_mac doit être une chaîne.']
    
    if not data.get('client_name'):
        errors['client_name'] = ['Le champ client_name est requis.']
    elif not isinstance(data.get('client_name'), str):
        errors['client_name'] = ['Le champ client_name doit être une chaîne.']
    
    if data.get('certi_key') and not isinstance(data.get('certi_key'), str):
        errors['certi_key'] = ['Le champ certi_key doit être une chaîne.']
    
    if errors:
        return {'errors': errors}, 422
    
    try:
        connection = db.get_connection()
        with connection:
            with connection.cursor() as cursor:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Vérifier si le client existe déjà
                sql_select = "SELECT * FROM client_infos WHERE client_mac = %s"
                cursor.execute(sql_select, (data['client_mac'],))
                existing_client = cursor.fetchone()
                
                if existing_client:
                    # Mise à jour du client existant
                    sql_update = """
                    UPDATE client_infos 
                    SET client_name = %s, certi_key = %s, updated_at = %s 
                    WHERE client_mac = %s
                    """
                    cursor.execute(sql_update, (
                        data['client_name'], 
                        data.get('certi_key'), 
                        current_time, 
                        data['client_mac']
                    ))
                    client_id = existing_client['id']
                    authorisation_status = existing_client['authorisation']
                else:
                    # Création d'un nouveau client 
                    client_id = str(uuid.uuid4())
                    sql_insert = """
                    INSERT INTO client_infos (id, client_mac, client_name, certi_key, authorisation, created_at, updated_at) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql_insert, (
                        client_id,
                        data['client_mac'],
                        data['client_name'],
                        data.get('certi_key'),
                        0,  # authorisation par défaut à 0
                        current_time,
                        current_time
                    ))
                    authorisation_status = 0
                
                connection.commit()
                
                return {
                    'success': 'Client enregistré',
                    'authorisation': authorisation_status,
                    'id': client_id
                }, 200
                
    except Exception as e:
        return {'errors': str(e)}, 422
    
def get_authorisation():
    try:
        connection = db.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, client_mac, client_name, authorisation, certi_key FROM client_infos")
        clients = cursor.fetchall()
        return {"data_client": clients}, 200
    except Exception as e:
        return {"errors": str(e)}, 500
    
def insert_load_data():
    conn = None
    connect_db = None
    try:
        conn = db.get_connection()
        connect_db = conn.cursor()
        
        load_id = str(uuid.uuid4())
        sql_insert = """
        INSERT INTO direct_configs (id, value, created_at, updated_at)
        VALUES (%s, %s, NOW(), NOW())
        """
        connect_db.execute(sql_insert, (load_id, 1))
        conn.commit()  # <-- Don’t forget to commit changes
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        if connect_db:
            connect_db.close()
        if conn:
            conn.close()


def insert_load_data1():
    conn = None
    connect_db = None
    try: 
        conn = db.get_connection()
        connect_db = conn.cursor()
        # connect_db.execute("INSERT INTO direct_configs LIMIT 1")
        # return connect_db.fetchone() 
        load_id = str(uuid.uuid4())
        sql_insert = """
        INSERT INTO direct_configs (id, value, created_at, updated_at) 
        VALUES (%s, %s, NOW(), NOW(),)
        """
        connect_db.execute(sql_insert, (
            load_id,
            1,  
                    ))
    except Exception as e:
        # connect_db.close()
        # conn.close()
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        if connect_db:
            connect_db.close()
        if conn:
            conn.close() 





def load_data():
    conn = None
    connect_db = None
    try: 
        conn = db.get_connection()
        connect_db = conn.cursor()
        connect_db.execute("SELECT * FROM direct_configs LIMIT 1")
        return connect_db.fetchone() 
    except Exception as e:
        connect_db.close()
        conn.close()
        import traceback
        traceback.print_exc()
    finally:
        if connect_db:
            connect_db.close()
        if conn:
            conn.close() 



    
def store_log_activate(request_data):
    errors = _validate_store_log_activate(request_data)
    
    if errors:
        return {'errors': errors}, 422
    
    data_valid = {
        'last_key': request_data.get('last_key'),
        'new_key': request_data.get('new_key'),
        'exprired_at': request_data.get('exprired_at')
    }
    
    try:
        connection = db.get_connection()
        with connection:
            with connection.cursor() as cursor:
                # Premier utilisateur
                cursor.execute("SELECT id FROM users LIMIT 1")
                user = cursor.fetchone()
                data_valid['user_id'] = user['id'] if user else None
                
                # Insertion
                active_log_id = str(uuid.uuid4())
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                sql = """
                INSERT INTO log_actives (id, last_key, new_key, exprired_at, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    active_log_id,
                    data_valid['last_key'],
                    data_valid['new_key'],
                    data_valid['exprired_at'],
                    data_valid['user_id'],
                    current_time,
                    current_time
                ))
                
                connection.commit()
                
                # Appel à getAlluser
                get_all_user(22)
                
                return {'success': 'success'}, 200
                
    except Exception as e:
        return {'errors': str(e)}, 422

def get_all_user(int_value):
    try:
        connection = db.get_connection()
        with connection:
            with connection.cursor() as cursor:
                # Utilisateurs non étudiants
                sql = "SELECT id, userable_type FROM users WHERE userable_type != %s"
                cursor.execute(sql, ('App\\Models\\Etudiant',))
                users = cursor.fetchall()
                
                letters = ''.join(random.choices(string.ascii_lowercase, k=2))
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for user in users:
                    # Modification de l'ID
                    parts = user['id'].split('-')
                    if len(parts) > 1:
                        parts[1] = f"{parts[1]}-{int_value}{letters}"
                    
                    new_id = '-'.join(parts)
                    client_infos_value = f"{user['id']}-{int_value}{letters}"
                    
                    # Mise à jour utilisateur
                    sql_update = "UPDATE users SET client_infos = %s, updated_at = %s WHERE id = %s"
                    cursor.execute(sql_update, (client_infos_value, current_time, user['id']))
                    
                    # UPSERT heart_autos
                    heart_id = str(uuid.uuid4())
                    sql_heart = """
                    INSERT INTO heart_autos (id, user_id, descript, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        descript = VALUES(descript),
                        updated_at = VALUES(updated_at)
                    """
                    cursor.execute(sql_heart, (
                        heart_id,
                        user['id'],
                        f"{user['id']}--{int_value}",
                        current_time,
                        current_time
                    ))
                
                connection.commit()
                
    except Exception as e:
        print(f"Erreur getAlluser: {e}")
        raise e

def store(request_data):
    errors = _validate_store(request_data)
    
    if errors:
        return {'errors': errors}, 422
    
    data_valid = {'status': request_data.get('status')}
    
    # Appel à getAlluser
    get_all_user(data_valid['status'])
    
    try:
        connection = db.get_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM client_infos")
                clients = cursor.fetchall()
                
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for client in clients:
                    # if client['ss_certi'] is None:
                    ss_certi_json = json.dumps({
                        'ssl_ca': request_data.get('ssl_ca'),
                        'ssl_cert': request_data.get('ssl_cert'),
                        'ssl_key': request_data.get('ssl_key')
                    })
                    
                    sql = "UPDATE client_infos SET ss_certi = %s, updated_at = %s WHERE id = %s"
                    cursor.execute(sql, (ss_certi_json, current_time, client['id']))
                
                connection.commit()
                
                return {'success': 'Opération réussie'}, 200
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'errors': str(e)}, 422
    # finally:
    #     if cursor:
    #         cursor.close()
    #     if conn:
    #         conn.close() 

def _validate_store_log_activate(data):
    errors = {}
    if data.get('last_key') is not None and not isinstance(data.get('last_key'), str):
        errors['last_key'] = ['Le champ last key doit être une chaîne.']
    if not data.get('new_key'):
        errors['new_key'] = ['Le champ new key est requis.']
    elif not isinstance(data.get('new_key'), str):
        errors['new_key'] = ['Le champ new key doit être une chaîne.']
    if not data.get('exprired_at'):
        errors['exprired_at'] = ['Le champ exprired at est requis.']
    elif not isinstance(data.get('exprired_at'), str):
        errors['exprired_at'] = ['Le champ exprired at doit être une chaîne.']
    return errors

def _validate_store(data):
    errors = {}
    if not data.get('status'):
        errors['status'] = ['Le champ status est requis.']
    elif not isinstance(data.get('status'), (int, float)) and not str(data.get('status')).isdigit():
        errors['status'] = ['Le champ status doit être un nombre.']
    return errors

