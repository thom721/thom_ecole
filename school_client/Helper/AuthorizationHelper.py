import bcrypt
from Helper.AdminAuthorization import AdminAuthorization
from Models.db import Database

db = Database()


class AuthorizationHelper:
    def __init__(self):
        pass

    # 🔹 Vérifie si un utilisateur a une permission donnée
    def user_has_permission(self, user_id, permission_name):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT DISTINCT p.name
                FROM permissions p
                LEFT JOIN role_has_permissions rp ON rp.permission_id = p.id
                LEFT JOIN model_has_roles mr ON mr.role_id = rp.role_id AND mr.model_id = %s
                LEFT JOIN model_has_permissions mp ON mp.permission_id = p.id AND mp.model_id = %s
                WHERE mr.model_id IS NOT NULL OR mp.model_id IS NOT NULL
            """

            # Exécuter la requête avec deux fois le model_id
            cursor.execute(query, (user_id, user_id))
            permissions = [row['name'] for row in cursor.fetchall()]
 
            return permission_name in permissions

        except Exception as e:
            print(f"[Erreur] user_has_permission → {e}")
            return False
        finally:
            if conn:
                conn.close()

    # 🔹 Vérifie l’existence de l’admin via email + mot de passe
    def find_user_by_credentials(self, email, password):
        try:
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT id, password FROM users WHERE email = %s LIMIT 1", (email,))
            user = cursor.fetchone()

            if not user:
                return None

            # Vérifie le mot de passe hashé (bcrypt)
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user
            return None

        except Exception as e:
            print(f"[Erreur] find_user_by_credentials → {e}")
            return None
        finally:
            if conn:
                conn.close()

    # 🔹 Vérifie les permissions d’un utilisateur ou d’un admin (email + mot de passe)
    def authorize_with_admin_token(self, user_id=None, admin_data=None, required_permission=None):
        """
        Vérifie les permissions d’un utilisateur connecté ou d’un administrateur.
        :param user_id: ID de l’utilisateur connecté (UUID)
        :param admin_data: { "email": "...", "password": "..." }
        :param required_permission: Nom de la permission à vérifier
        :return: dict → {success, id, role, message?}
        """

        # 1️⃣ Vérifie l’utilisateur courant
        if user_id and self.user_has_permission(user_id, required_permission):
            return {"success": True, "id": user_id, "role": "user"}

        # 2️⃣ Si l’utilisateur n’a pas la permission, on demande une autorisation admin
        if not admin_data: # or "email" not in admin_data or "password" not in admin_data:
            return {
                "success": False,
                "Authorization": False,
                "message": "Action non autorisée. Veuillez fournir un autre compte pour autorisation.",
                "required_permission":required_permission,
                "require_admin_auth": True
            }

        # 3️⃣ Vérifie les identifiants de l’admin
        # admin = self.find_user_by_credentials(admin_data["email"], admin_data["password"])
        # admin = self.user_has_permission(admin_data, required_permission)
        # if not admin:
        #     return {
        #         "success": False,
        #         "Authorization": False,
        #         "message": "L’administrateur n’a pas la permission requise pour cette action."
        #     }

        # 4️⃣ Vérifie les permissions de l’admin
        if not self.user_has_permission(admin_data, required_permission):
            return {
                "success": False,
                "Authorization": False,
                "message": "L’administrateur n’a pas la permission requise pour cette action."
            }

        # ✅ Tout est bon
        # AdminAuthorization.set_admin_id(admin["id"])
        return {"success": True, "id": admin_data, "role": "admin"}
    

def find_user_by_credentials(email, password,permission_name):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        

        cursor.execute("SELECT id, password FROM users WHERE email = %s LIMIT 1", (email,))
        user = cursor.fetchone()

        if not user:
            return {"errors": "Identifiant ou mot de passe incorrect"}

        # Vérifie le mot de passe hashé (bcrypt)
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            permission = user_has_permission(user.get('id'), permission_name)
            if permission:
                return {"user":user, 'premission':permission}
            return {"errors": "Identifiant n’a pas la permission requise pour cette action"}
        return {"errors": "Identifiant ou mot de passe incorrect"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Erreur] find_user_by_credentials → {e}")
        return {"errors": "Identifiant ou mot de passe incorrect"}
    finally:
        if conn:
            conn.close()

def user_has_permission(user_id, permission_name):
    try:
        conn = db.get_connection()
        cursor = conn.cursor()

        query = """
            SELECT DISTINCT p.name
            FROM permissions p
            LEFT JOIN role_has_permissions rp ON rp.permission_id = p.id
            LEFT JOIN model_has_roles mr ON mr.role_id = rp.role_id AND mr.model_id = %s
            LEFT JOIN model_has_permissions mp ON mp.permission_id = p.id AND mp.model_id = %s
            WHERE mr.model_id IS NOT NULL OR mp.model_id IS NOT NULL
        """

        # Exécuter la requête avec deux fois le model_id
        cursor.execute(query, (user_id, user_id))

        permissions = [row['name'] for row in cursor.fetchall()]
  
        return permission_name in permissions

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Erreur] user_has_permission → {e}")
        return False
    finally:
        if conn:
            conn.close()
