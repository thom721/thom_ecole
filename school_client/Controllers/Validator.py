
import re
# from win10toast import ToastNotifier
from notifypy import Notify
from PySide6.QtWidgets import (
    QComboBox, QLabel, QLineEdit,QMessageBox
)
from Helper.LoadingOverlay import LoadingOverlay

from Models.db import Database
db = Database()
conn = db.get_connection() 
from typing import Any, Dict, List
from dateutil.relativedelta import relativedelta

from datetime import datetime
import pytz

# haiti_datetime = get_haiti_datetime('%Y-%m-%d %H:%M:%S')  # format SQL standard
# cursor.execute("INSERT INTO table_name (created_at) VALUES (%s)", (haiti_datetime,))

def get_haiti_datetime(format_str='%d-%m-%Y %H:%M'):
    tz = pytz.timezone("America/Port-au-Prince")
    haiti_time = datetime.now(tz)
    return haiti_time.strftime(format_str)

# Exemple d'utilisation
print(get_haiti_datetime())  # Affiche : 13-10-2025 15:42

# import re
# import json
# import hashlib
# from datetime import datetime
# from mysql.connector import Error
# from Models import db  # ou ton module DB

class Validator:
    def __init__(self, data, rules, messages=None, db_config=None):
        self.data = data
        self.rules = rules
        self.messages = messages or {}
        self.errors = {}
        self.db = db_config or db
        self.conn = None

    # --- Méthode principale ---
    def validate(self):
        try:
            self.conn = db.get_connection()
        except Exception as e:
            print(f"Erreur connexion DB : {e}")
            self.conn = None

        for field, rule_string in self.rules.items():
            rules = [r.strip() for r in rule_string.split('|') if r.strip()]

            # --- Gestion des champs imbriqués (ex: items.*.nom) ---
            if '.*.' in field:
                base_field, sub_field = field.split('.*.')
                array_data = self.data.get(base_field, [])

                if isinstance(array_data, list):
                    if not array_data:
                        self.add_error(base_field, f"{base_field} doit contenir au moins 1 élément")
                        return
                    for idx, item in enumerate(array_data):
                        sub_value = item.get(sub_field) if isinstance(item, dict) else None
                        for rule in rules:
                            self.apply_rule(f"{base_field}[{idx}].{sub_field}", sub_value, rule)
                elif isinstance(array_data, dict):
                    for key, item in array_data.items():
                        sub_value = item.get(sub_field) if isinstance(item, dict) else None
                        for rule in rules:
                            self.apply_rule(f"{base_field}[{key}].{sub_field}", sub_value, rule)
                else:
                    self.add_error(base_field, f"{base_field} doit être une liste ou un dictionnaire")
                continue

            # --- Gestion des listes simples (ex: items.*) ---
            elif '.*' in field:
                base_field = field.split('.*')[0]
                array_data = self.data.get(base_field, [])
                if isinstance(array_data, list):
                    if not array_data:
                        self.add_error(base_field, f"{base_field} doit contenir au moins 1 élément")
                    for idx, value in enumerate(array_data):
                        for rule in rules:
                            self.apply_rule(f"{base_field}[{idx}]", value, rule)
                elif isinstance(array_data, dict):
                    for key, value in array_data.items():
                        for rule in rules:
                            self.apply_rule(f"{base_field}[{key}]", value, rule)
                else:
                    self.add_error(base_field, f"{base_field} doit être une liste ou dict")
                continue

            # --- Champs simples ---
            value = self.data.get(field)
            for rule in rules:
                self.apply_rule(field, value, rule)

        if self.conn:
            self.conn.close()

        return len(self.errors) == 0

    # --- Application d’une règle ---
    def apply_rule(self, field, value, rule):
        msg_key_exact = f"{field}.{rule}"
        msg_key_generic = re.sub(r'\[\w+\]', '*', msg_key_exact)
        msg_key_fallback = re.sub(r'\[\d+\]', '*', msg_key_generic)
        message = (
            self.messages.get(msg_key_exact)
            or self.messages.get(msg_key_generic)
            or self.messages.get(msg_key_fallback)
        )

        # --- required ---
        if rule == 'required' and value in [None, '']:
            self.add_error(field, message or f"{field} est obligatoire")#.split('_')[0]
            return

        # --- required_if ---
        if rule.startswith('required_if:'):
            print(rule, field, value)
            if self._check_required_if(rule, field, value):
                return  # erreur déjà ajoutée

        # --- nullable (à évaluer après required_if) ---
        if rule == 'nullable' and value in [None, '']:
            return

        # --- Types ---
        if rule == 'numeric' and value not in [None, ''] and not self.is_numeric(value):
            self.add_error(field, message or f"{field} doit être un nombre")

        elif rule == 'string' and value not in [None, ''] and not isinstance(value, str):
            self.add_error(field, message or f"{field} doit être une chaîne de caractères")

        elif rule == 'array' and value not in [None, ''] and not isinstance(value, (list, dict)):
            self.add_error(field, message or f"{field} doit être une liste ou dict")

        elif rule == 'email' and value not in [None, '']:
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(value)):
                self.add_error(field, message or f"{field} doit être une adresse email valide")

        elif rule == 'alpha_dash' and value not in [None, '']:
            if not re.match(r"^[A-Za-z0-9_-]+$", str(value)):
                self.add_error(field, message or f"{field} ne peut contenir que des lettres, chiffres, tirets et underscores")

        # --- min / max ---
        elif rule.startswith('min:'):
            min_val = int(rule.split(':', 1)[1])
            if value not in [None, ''] and len(str(value)) < min_val:
                self.add_error(field, message or f"{field} doit contenir au moins {min_val} caractères")

        elif rule.startswith('max:'):
            max_val = int(rule.split(':', 1)[1])
            if value not in [None, ''] and len(str(value)) > max_val:
                self.add_error(field, message or f"{field} doit contenir au plus {max_val} caractères")

        # --- in ---
        elif rule.startswith('in:'):
            allowed = rule.split(':', 1)[1].split(',')
            if value not in [None, ''] and str(value) not in allowed:
                self.add_error(field, message or f"{field} doit être parmi {allowed}")

        # --- exists ---
        elif rule.startswith('exists:'):
            if not self.ensure_connection(): return
            if not self.exists_in_db(rule, value):
                self.add_error(field, message or f"{field} n'existe pas dans la base de données")

        # --- unique ---
        elif rule.startswith('unique:'):
            if not self.ensure_connection(): return
            if not self.is_unique(rule, value):
                self.add_error(field, message or f"{field} existe déjà")

    # --- Vérifie la connexion DB ---
    def ensure_connection(self):
        if not self.conn:# or not getattr(self.conn, "is_connected", lambda: False)():
            try:
                self.conn = db.get_connection()
                return True
            except Exception as e:
                print(f"⚠️ Impossible de reconnecter la DB : {e}")
                return False
        return True

    # --- Vérifie required_if ---
    def _check_required_if(self, rule, field, value):
        try:
            params = rule.split(':', 1)[1].split(',')
            other_field = params[0]
            expected_value = ','.join(params[1:])
            other_val = self.data.get(other_field)

            if expected_value.lower() == 'null':
                match =True # other_val is None
            elif expected_value.startswith('!'):
                match = str(other_val) != expected_value[1:]
            else:
                match = str(other_val) == expected_value

            if match and value in [None, '']:
                self.add_error(field, f"{field} est obligatoire")#.split('_')[0]
                return True
        except Exception as e:
            print(f"Erreur required_if: {e}")
        return False

    # --- Vérifie si numérique ---
    def is_numeric(self, value):
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False

    # --- Ajoute une erreur ---
    def add_error(self, field, message):
        clean_field = re.sub(r'\[\d+\]', '.*', field)
        self.errors.setdefault(clean_field, []).append(message)

    # --- Vérifie si existe dans la DB ---
    
    def exists_in_db(self, rule, value):
        print(f"exists: {rule} {value}")
        try:
            if value in [None, '']:
                return True
                
            # Validation du format de la règle
            if ':' not in rule or ',' not in rule:
                print(f"Format de règle invalide: {rule}")
                return False
                
            # Extraire table et colonne de manière sécurisée
            rule_parts = rule.split(':', 1)
            if len(rule_parts) < 2:
                print(f"Format de règle invalide: {rule}")
                return False
                
            table_column = rule_parts[1]
            if ',' not in table_column:
                print(f"Format table/colonne invalide: {table_column}")
                return False
                
            table, column = table_column.split(',', 1)
            
            # Nettoyer les noms de table et colonne (sécurité basique)
            table = table.strip()
            column = column.strip()
            
            cursor = self.conn.cursor()
            
            try:
                # Requête avec gestion d'erreur
                query = f"SELECT COUNT(*) as count FROM `{table}` WHERE `{column}` = %s"
                cursor.execute(query, (value,))
                
                res = cursor.fetchone()
                print(f"Résultat requête: {res} - Table: {table}, Colonne: {column}")
                
                exists = res['count'] > 0 if res and 'count' in res else False
                return exists
                
            finally:
                # Toujours fermer le cursor
                cursor.close()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Erreur exists: {e}")
            return False

    def is_unique(self, rule, value):
        print(f"is_unique: {rule} {value}")
        try:
            if value in [None, '']:
                print("Valeur vide, retourne True")
                return True

            # Validation du format de la règle
            if ':' not in rule:
                print(f"Format de règle invalide: {rule}")
                return False
                
            parts = rule.split(':', 1)[1].split(',')
            if len(parts) < 1:
                print(f"Pas assez de parties dans la règle: {rule}")
                return False
                
            table = parts[0].strip()
            column = parts[1].strip() if len(parts) > 1 else 'id'
            ignore_id = parts[2].strip() if len(parts) > 2 else None
            ignore_column = parts[3].strip() if len(parts) > 3 else 'id'

            print(f"Table: {table}, Column: {column}, Ignore ID: {ignore_id}, Ignore Column: {ignore_column}")

            # Validation de sécurité
            if not re.match(r'^[a-zA-Z0-9_]+$', table) or not re.match(r'^[a-zA-Z0-9_]+$', column):
                print(f"Nom de table ou colonne invalide: {table}, {column}")
                return False

            cursor = self.conn.cursor()
            
            try:
                if ignore_id:
                    query = f"SELECT COUNT(*) as count FROM `{table}` WHERE `{column}`=%s AND `{ignore_column}`!=%s"
                    print(f"Query: {query} avec valeurs: {value}, {ignore_id}")
                    cursor.execute(query, (value, ignore_id))
                else:
                    query = f"SELECT COUNT(*) as count FROM `{table}` WHERE `{column}`=%s"
                    print(f"Query: {query} avec valeur: {value}")
                    cursor.execute(query, (value,))
                
                res = cursor.fetchone()
                print(f"Résultat de la requête: {res}")
                
                count = res['count'] if res and 'count' in res else 0
                is_unique_result = count == 0
                
                print(f"Résultat is_unique: {is_unique_result} (count: {count})")
                return is_unique_result
                
            finally:
                cursor.close()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Erreur unique: {e}")
            return False


    # --- Vérifie unicité ---
    def is_uniquesss(self, rule, value):
        try:
            if value in [None, '']:
                return True

            parts = rule.split(':', 1)[1].split(',')
            table = parts[0].strip()
            column = parts[1].strip() if len(parts) > 1 else 'id'
            ignore_id = parts[2].strip() if len(parts) > 2 else None
            ignore_column = parts[3].strip() if len(parts) > 3 else 'id'

            if not re.match(r'^[a-zA-Z0-9_]+$', table) or not re.match(r'^[a-zA-Z0-9_]+$', column):
                return False

            cursor = self.conn.cursor()
            if ignore_id:
                query = f"SELECT COUNT(*) FROM {table} WHERE {column}=%s AND {ignore_column}!=%s"
                cursor.execute(query, (value, ignore_id))
            else:
                query = f"SELECT COUNT(*) FROM {table} WHERE {column}=%s"
                cursor.execute(query, (value,))
            return cursor.fetchone()[0] == 0
        except Exception as e:
            print(f"Erreur unique: {e}")
            return False



# class Validator:
#     def __init__(self, data, rules, messages=None, db_config=None):
#         self.data = data
#         self.rules = rules
#         self.messages = messages or {}
#         self.errors = {}
#         self.db = db_config or db
#         self.conn = None

#     # --- Méthode principale ---
#     def validate(self):
#         try:
#             self.conn = db.get_connection()
#         except Exception as e:
#             print(f"Erreur connexion DB : {e}")
#             self.conn = None

#         for field, rule_string in self.rules.items():
#             rules = [r.strip() for r in rule_string.split('|') if r.strip()]

#             # --- Gestion des champs imbriqués (ex: items.*.nom) ---
#             if '.*.' in field:
#                 base_field, sub_field = field.split('.*.')
#                 array_data = self.data.get(base_field, [])

#                 if isinstance(array_data, list):
#                     # print(f"in list validator  .*. {array_data}")
#                     for idx, item in enumerate(array_data):
#                         sub_value = item.get(sub_field) if isinstance(item, dict) else None 
#                         for rule in rules:
#                             self.apply_rule(f"{base_field}[{idx}].{sub_field}", sub_value, rule)
#                 elif isinstance(array_data, dict): 
#                     for key, item in array_data.items():
#                         sub_value = item.get(sub_field) if isinstance(item, dict) else None
#                         for rule in rules:
#                             self.apply_rule(f"{base_field}[{key}].{sub_field}", sub_value, rule)
#                 else:
#                     self.add_error(base_field, f"{base_field} doit être une liste ou dict")
#                 continue

#             # --- Gestion des listes/dict simples (ex: items.* ou montant_par.*) ---
#             elif '.*' in field:
#                 base_field = field.split('.*')[0]
#                 array_data = self.data.get(base_field, {})

#                 if isinstance(array_data, dict): 
#                     for key, value in array_data.items():
#                         for rule in rules:
#                             self.apply_rule(f"{base_field}[{key}]", value, rule)
#                 elif isinstance(array_data, list):
#                     for idx, value in enumerate(array_data):
#                         for rule in rules:
#                             self.apply_rule(f"{base_field}[{idx}]", value, rule)
#                 else:
#                     self.add_error(base_field, f"{base_field} doit être une liste ou dict")
#                 # continue

#             # --- Champs simples ---
#             value = self.data.get(field)
#             for rule in rules:
#                 self.apply_rule(field, value, rule)

#         if self.conn:
#             self.conn.close()

#         return len(self.errors) == 0

#     # --- Applique une règle à un champ ---
#     def apply_rule(self, field, value, rule):
#         # --- Message personnalisé ---
#         msg_key_exact = f"{field}.{rule}"
#         msg_key_generic = re.sub(r'\[\w+\]', '*', msg_key_exact)
#         msg_key_fallback = re.sub(r'\[\d+\]', '*', msg_key_generic)  # pour les index numériques

#         message = (
#             self.messages.get(msg_key_exact)
#             or self.messages.get(msg_key_generic)
#             or self.messages.get(msg_key_fallback)
#         )


#         if rule == 'required' and value in [None, '']:
#             self.add_error(field, message or f"{field.split('_')[0]} est obligatoire")
#             return

#         # --- nullable ---
#         if rule == 'nullable' and value in [None, '']:
#             return

#         # --- required_if ---
#         if rule.startswith('required_if:'):            
#             condition = self._check_required_if(rule, field, value)
#             if condition:
#                 return

#         # --- Types ---
#         if rule == 'numeric' and value not in [None, ''] and not self.is_numeric(value):
#             self.add_error(field, message or f"{field} doit être un nombre")
#         elif rule == 'string' and value not in [None, ''] and not isinstance(value, str):
#             self.add_error(field, message or f"{field} doit être une chaîne de caractères")
#         elif rule == 'array' and value not in [None, ''] and not isinstance(value, (list, dict)):
#             self.add_error(field, message or f"{field} doit être une liste ou dict")
#         elif rule == "email" and value not in [None, '']:
#             if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", str(value)):
#                 self.add_error(field, message or f"{field} doit être une adresse email valide")
#         elif rule == "alpha_dash" and value not in [None, '']:
#             if not re.match(r"^[A-Za-z0-9_-]+$", str(value)):
#                 self.add_error(field, message or f"{field} ne peut contenir que des lettres, chiffres, tirets et underscores")


#         # --- min / max ---
#         elif rule.startswith('min:'):
#             min_val = int(rule.split(':', 1)[1])
#             if value not in [None, ''] and len(str(value)) < min_val:
#                 self.add_error(field, message or f"{field} doit contenir au moins {min_val} caractères")

#         elif rule.startswith('max:'):
#             max_val = int(rule.split(':', 1)[1])
#             if value not in [None, ''] and len(str(value)) > max_val:
#                 self.add_error(field, message or f"{field} doit contenir au plus {max_val} caractères")

#         # --- in ---
#         elif rule.startswith('in:'):
#             allowed = rule.split(':', 1)[1].split(',')
#             if value not in [None, ''] and str(value) not in allowed:
#                 self.add_error(field, message or f"{field} doit être parmi {allowed}")

#         # --- exists ---
#         elif rule.startswith('exists:'):
#             if self.conn:
#                 if not self.exists_in_db(rule, value):
#                     self.add_error(field, message or f"{field} n'existe pas dans la base de données")
#             else:
#                 print("⚠️ Aucun accès DB pour 'exists'")

#         # --- unique ---
#         elif rule.startswith('unique:'):
#             if self.conn:
#                 if not self.is_unique(rule, value):
#                     self.add_error(field, message or f"{field} existe déjà")
#             else:
#                 print("⚠️ Aucun accès DB pour 'unique'")

#     # --- Vérifie si une valeur est numérique ---
#     def is_numeric(self, value):
#         try:
#             float(value)
#             return True
#         except (ValueError, TypeError):
#             return False

#     # --- Ajoute une erreur ---
#     def add_error(self, field, message):
#         self.errors.setdefault(field, []).append(message)

#     # --- Vérifie le required_if ---
#     def _check_required_if(self, rule, field, value):
#         try:
#             params = rule.split(':', 1)[1].split(',')
#             other_field = params[0]
#             expected_value = ','.join(params[1:])

#             # Récupération de la valeur du champ dépendant
#             other_val = self.data.get(other_field)
#             print(expected_value)
#             # Gestion spéciale si expected_value est 'null'
#             if expected_value.lower() == 'null':
#                 match =True # other_val is None
#             elif expected_value.startswith('!'):
#                 match = str(other_val) != expected_value[1:]
#             else:
#                 match = str(other_val) == expected_value

#             # Si la condition est remplie mais la valeur est vide ou absente
#             if match and value in [None, '']:
#                 self.add_error(field, f"{field.split('_')[0]} est obligatoire")
#                 return True
#         except Exception as e:
#             print(f"Erreur required_if: {e}")
#         return False


#     # --- Vérifie si une valeur existe dans la DB ---
#     def exists_in_db(self, rule, value):
#         try:
#             if value in [None, '']:
#                 return True
#             table, column = rule.split(':', 1)[1].split(',', 1)
#             cursor = self.conn.cursor()
#             cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column}=%s", (value,))
#             return cursor.fetchone()[0] > 0
#         except Exception as e:
#             print(f"Erreur exists: {e}")
#             return False

#     # --- Vérifie l’unicité d’une valeur ---
   
#     def is_unique(self, rule, value):
#         """
#         Parse rule: unique:table,column[,ignore_id[,ignore_column]]
#         - table: nom de la table
#         - column: colonne à vérifier
#         - ignore_id: valeur à ignorer (souvent l'id du modèle)
#         - ignore_column: colonne d'ignore (par défaut 'id', mais ex: 'userable_id')
#         """
#         try:
#             if value in [None, '']:
#                 return True

#             parts = rule.split(':', 1)[1].split(',')
#             table = parts[0].strip()
#             column = parts[1].strip() if len(parts) > 1 and parts[1].strip() else 'id'
#             ignore_id = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
#             ignore_column = parts[3].strip() if len(parts) > 3 and parts[3].strip() else 'id'

#             # Sécurité basique sur noms de table/colonne
#             if not re.match(r'^[a-zA-Z0-9_]+$', table) or not re.match(r'^[a-zA-Z0-9_]+$', column):
#                 return False

#             cursor = self.conn.cursor()
#             if ignore_id:
#                 # Requête paramétrée : on compare la colonne ignore_column avec la valeur ignore_id
#                 query = f"SELECT COUNT(*) FROM {table} WHERE {column} = %s AND {ignore_column} != %s"
#                 cursor.execute(query, (value, ignore_id))
#             else:
#                 query = f"SELECT COUNT(*) FROM {table} WHERE {column} = %s"
#                 cursor.execute(query, (value,))

#             row = cursor.fetchone()
#             return (row[0] == 0)
#         except Exception as e:
#             print(f"Erreur unique: {e}")
#             # En cas d'erreur DB, on peut considérer que ce n'est pas unique (ou renvoyer False pour safety)
#             return False





class ValidatorError:
     def __init__(self):
          super().__init__()
          self.overlay = LoadingOverlay(None)

     def toast_certificat_installe(self,title, message):
        notify = Notify()
        notify.title =title
        notify.message =message
        notify.send()

     def generic_direct_error_message(self, response_data):
          full_message = ""
          full_error = ""
     
     
          if isinstance(response_data, dict):
               if "errors" in response_data:
                    if isinstance(response_data["errors"], dict):
                         # Cas habituel : {"errors": {"field": ["message"]}}
                         messages = []
                         for field, errors in response_data["errors"].items():
                              
                            if isinstance(errors, list):
                                self.overlay.finish_loading
                                messages.append(f"{errors[0]}")
                            #    messages.append(f"{field.capitalize()} : {errors[0]}")
                            else:
                                self.overlay.finish_loading
                                messages.append(f"{str(errors)}")
                         full_message = "\n- ".join(messages)
                    elif isinstance(response_data["errors"], str):
                         # Cas spécial : {"errors": "message simple"}
                         print('{"errors": "message simple"}')
                         full_message = response_data["errors"]
                        #  full_error = response_data["errors"]
               else:
                    if 'message' in response_data:
                         full_message = response_data['message']
                    full_error = str(response_data)
                    # print(f"full_message in error_msg or str(response_data) {full_message}")
          elif isinstance(response_data, str):
            #    full_message = response_data
               full_error = response_data
               
          else:
               full_message = "Une erreur inconnue est survenue."
               full_error = "L'adresse ip du server n'est pas correspond a celle que vous indiquez."
          self.overlay.finish_loading
    
          if 'SQLSTATE' not in full_message and 'Unauthenticated' not in full_message and full_message != "":
            # NotificationToast(f"{full_message}", "error").show_notification()
            self.toast_certificat_installe("Échec", full_message)
            # QMessageBox.critical(
            #     None,
            #     f"Échec",
            #     full_message
            # )
            return
          

# from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QApplication
# from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
# from PySide6.QtGui import QGraphicsOpacityEffect
# import sys

# # Liste globale pour empiler les notifications
# active_notifications = []

# class NotificationToast(QWidget):
#     def __init__(self, message, notif_type="info", duration=3000, parent=None):
#         super().__init__(parent)
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.ToolTip)
#         self.setAttribute(Qt.WA_TranslucentBackground)

#         # Couleurs selon le type
#         colors = {
#             "success": "#4CAF50",
#             "error": "#F44336",
#             "warning": "#FFC107",
#             "info": "#2196F3"
#         }

#         self.bg_color = colors.get(notif_type, "#333333")
#         self.duration = duration

#         # Layout principal
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(15, 10, 15, 10)
#         layout.setSpacing(10)

#         # Icône (texte emoji ici, tu peux mettre une image)
#         icons = {
#             "success": "✅",
#             "error": "❌",
#             "warning": "⚠️",
#             "info": "ℹ️"
#         }

#         icon_label = QLabel(icons.get(notif_type, "🔔"))
#         icon_label.setStyleSheet("font-size: 18px;")
#         layout.addWidget(icon_label)

#         # Message
#         self.label = QLabel(message)
#         self.label.setStyleSheet("color: white; font-size: 14px;")
#         layout.addWidget(self.label)

#         # Style général
#         self.setStyleSheet(f"""
#             background-color: {self.bg_color};
#             border-radius: 10px;
#         """)

#         self.adjustSize()

#         # Effet de transparence
#         self.opacity_effect = QGraphicsOpacityEffect(self)
#         self.setGraphicsEffect(self.opacity_effect)
#         self.opacity_effect.setOpacity(0)

#         # Animations
#         self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
#         self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")

#     def show_notification(self, position="bottom-right"):
#         """Affiche la notification à l’écran avec animation"""

#         screen = QApplication.primaryScreen().geometry()
#         w, h = self.width(), self.height()

#         # Décalage vertical pour empiler les notifications
#         offset_y = len(active_notifications) * (h + 15)

#         if position == "bottom-right":
#             x = screen.width() - w - 30
#             y = screen.height() - h - 50 - offset_y
#         elif position == "center":
#             x = (screen.width() - w) // 2
#             y = (screen.height() - h) // 2 - offset_y
#         else:
#             x, y = 50, 50 + offset_y

#         self.setGeometry(x, y + 30, w, h)
#         self.show()

#         # Animation de fondu d’entrée
#         self.fade_in.setDuration(400)
#         self.fade_in.setStartValue(0)
#         self.fade_in.setEndValue(1)
#         self.fade_in.setEasingCurve(QEasingCurve.InOutQuad)
#         self.fade_in.start()

#         # Animation de montée
#         anim_pos = QPropertyAnimation(self, b"geometry")
#         anim_pos.setDuration(500)
#         anim_pos.setStartValue(QRect(x, y + 30, w, h))
#         anim_pos.setEndValue(QRect(x, y, w, h))
#         anim_pos.setEasingCurve(QEasingCurve.OutCubic)
#         anim_pos.start()

#         # Ajout à la pile
#         active_notifications.append(self)

#         # Fermeture automatique
#         QTimer.singleShot(self.duration, self.fade_and_close)

#     def fade_and_close(self):
#         """Animation de disparition"""
#         self.fade_out.setDuration(600)
#         self.fade_out.setStartValue(1)
#         self.fade_out.setEndValue(0)
#         self.fade_out.setEasingCurve(QEasingCurve.InOutQuad)
#         self.fade_out.finished.connect(self._remove_from_stack)
#         self.fade_out.start()

#     def _remove_from_stack(self):
#         """Ferme la notif et ajuste les positions restantes"""
#         if self in active_notifications:
#             active_notifications.remove(self)
#         self.close()

#         # Réajuster la pile
#         for i, notif in enumerate(active_notifications):
#             geom = notif.geometry()
#             new_y = QApplication.primaryScreen().geometry().height() - notif.height() - 50 - i * (notif.height() + 15)
#             anim = QPropertyAnimation(notif, b"geometry")
#             anim.setDuration(300)
#             anim.setStartValue(geom)
#             anim.setEndValue(QRect(geom.x(), new_y, geom.width(), geom.height()))
#             anim.setEasingCurve(QEasingCurve.OutCubic)
#             anim.start()



# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     NotificationToast("Sauvegarde réussie 🎉", "success").show_notification()
#     NotificationToast("Erreur lors de la connexion ❌", "error").show_notification()
#     NotificationToast("Attention : Données non enregistrées ⚠️", "warning").show_notification()
#     NotificationToast("Info : Une mise à jour est disponible ℹ️", "info").show_notification()

#     sys.exit(app.exec())






