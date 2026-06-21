
from Helper.Ip_manager import Ip_manager
import pymysql
from pymysql.cursors import DictCursor
from Helper.Ip_manager import Ip_manager

# import pymysql
# conn = pymysql.connect(host="localhost", user="root", password="pass", database="test")


class Database:
    def __init__(self):
        self.ip_manager = Ip_manager()
    def get_connection(self):
        """Retourne une connexion MySQL sécurisée"""
        try:
          
            conn = pymysql.connect(
               host = 'aplekol360.local',
               port = 3307,
               user = "user_pyside",
               password = "@#Janvier21",
               database = "lemignon",      
               ssl_ca='C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/ca.pem',
               ssl_cert='C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-cert.pem',
               ssl_key='C:/Program Files/ecole-serve/mysql-8.0.41-winx64/certs/client-key.pem', 
               cursorclass=pymysql.cursors.DictCursor,
               ssl_verify_cert=True,
               )
            return conn
        except Exception as e:
            print(f"Erreur de connexion MySQL: {e}")
            import traceback
            traceback.print_exc()



    def get_students_count(self):
          conn = None
          cursor = None
          try:
               conn = self.get_connection()  # ta méthode à toi
               cursor = conn.cursor()
               cursor.execute("SELECT COUNT(*) AS total FROM etudiants")
               result = cursor.fetchone()
               return result
          except Exception as e:
               print(f"Erreur dans get_students_count: {e}")
               import traceback
               traceback.print_exc()
               return None
          finally:
               # 🔒 Toujours fermer ici, même si une exception arrive
               if cursor is not None:
                    cursor.close()
               if conn is not None and conn.is_connected():
                    conn.close()



    def execute_query(self, query, params=None, fetch=False):
          """Exécute une requête SQL et retourne les résultats si fetch=True"""
          conn = None
          cursor = None
          try:
               conn = self.get_connection()
               cursor = conn.cursor()
               cursor.execute(query, params or [])
               result = cursor.fetchall() if fetch else None
               conn.commit()
               return result
          except Exception as e:
               if conn:
                    conn.rollback()
               print(f"Erreur SQL: {e}")
               raise
          finally:
               if cursor:
                    cursor.close()
               if conn:
                    conn.close()


