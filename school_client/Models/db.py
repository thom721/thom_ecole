import os
import pymysql
from pymysql.cursors import DictCursor
from Helper.Ip_manager import Ip_manager
from utils.imports import get_local_data_dir
import traceback
import threading

_connection_lock = threading.Lock()

class Database:
    _thread_local = threading.local()  # ✅ Une connexion par thread

    def __init__(self):
        self.ip_manager = Ip_manager()
        self.database_name = None
        self.user_profile = os.getenv("USERPROFILE") or os.getenv("HOME")
        self.server_path = os.path.join(get_local_data_dir(), ".ecole_360", ".certs")

    # --- Vérifie la présence des certificats SSL ---
    def has_ssl_certs(self):
        return all(
            os.path.exists(os.path.join(self.server_path, f))
            for f in ["ca-cert.pem", "client-cert.pem", "client-key.pem"]
        )

    # --- Récupère la connexion thread-safe ---
    def get_connection(self, host_='aplekol360.local'):
        """Retourne une connexion MySQL valide pour le thread courant."""
        print("Retourne une connexion MySQL valide pour le thread courant.")
        try:
            # 🔒 Verrou temporaire pour éviter les collisions
            with _connection_lock:
                conn = getattr(self._thread_local, "conn", None)

                # ✅ Si une connexion existe et fonctionne, on la garde
                if conn:
                    try:
                        conn.ping(reconnect=True)
                        if conn.open:
                            return conn
                    except Exception:
                        print("⚠️ Connexion du thread invalide, recréation...")
                        conn = None

                # --- Sinon, on crée une nouvelle connexion ---
                host = 'aplekol360.local' #self.ip_manager.get_server_ip() or host_
                ssl_available = self.has_ssl_certs()
                print(f"self.database_name={self.database_name}, host={host}")

                if ssl_available:
                    print("🔐 Connexion MySQL avec SSL complète...")
                    conn = pymysql.connect(
                        host=host,
                        port=3307,
                        user="user_pyside",
                        password="@#Janvier21",
                        database="lemignon",
                        cursorclass=DictCursor,
                        ssl_ca=f"{self.server_path}/ca-cert.pem",
                        ssl_cert=f"{self.server_path}/client-cert.pem",
                        ssl_key=f"{self.server_path}/client-key.pem",
                        ssl_verify_cert=True,
                        autocommit=True,
                        connect_timeout=10
                    )
                    print(f"✅ Nouvelle connexion (thread {threading.get_ident()}) établie avec user_pyside")

                else:
                    print("⚠️ Aucun certificat trouvé, connexion générique SSL...")
                    conn = pymysql.connect(
                        host=host,
                        port=3307,
                        user="ssl_reader",
                        password="@#ssl_reader21",
                        database="lemignon",
                        cursorclass=DictCursor,
                        ssl={"ssl": {}},
                        autocommit=True,
                        connect_timeout=10
                    )
                    print(f"✅ Nouvelle connexion (thread {threading.get_ident()}) établie avec ssl_reader")

                # ✅ Stocke la connexion dans le thread local
                self._thread_local.conn = conn
                return conn

        except Exception as e:
            print(f"❌ Erreur lors de la connexion MySQL : {e}")
            traceback.print_exc()
            return None

    # --- Ferme proprement la connexion du thread ---
    def close_connection(self):
        conn = getattr(self._thread_local, "conn", None)
        if conn and conn.open:
            try:
                conn.close()
                print(f"🔒 Connexion MySQL fermée pour le thread {threading.get_ident()}")
            except Exception as e:
                print(f"⚠️ Erreur lors de la fermeture de la connexion : {e}")
        self._thread_local.conn = None


    # 🔹 Établit (ou réutilise) une connexion MySQL
    def get_connectioneeeee(self, host_=None):
            # ✅ Si une connexion existe déjà et est toujours ouverte, on la réutilise
        if self.conn and self.conn.open:
            return self.conn
        
        if not _connection_lock.acquire(blocking=False):
            print("⏳ Connexion MySQL déjà en cours, on ignore l’appel.")
         
        try:

            host = self.ip_manager.get_server_ip() or host_
            ssl_available = self.has_ssl_certs()
            print(f"self.database_name   {self.database_name}, host {host}")
            if ssl_available:
                print("🔐 Connexion MySQL avec SSL complète...")
                # if not self.database_name:
                #     self.database_name = self.get_data_base_name("@#Janvier21", "user_pyside", host)

                self.conn = pymysql.connect(
                    host=host,
                    port=3307,
                    user="user_pyside",
                    password="@#Janvier21",
                    database='lemignon',
                    cursorclass=DictCursor,
                    ssl_ca=f"{self.server_path}/ca-cert.pem",
                    ssl_cert=f"{self.server_path}/client-cert.pem",
                    ssl_key=f"{self.server_path}/client-key.pem",
                    ssl_verify_cert=True,
                    autocommit=True
                )
                print(f"✅ Connexion MySQL initialisée with user_pyside.  {self.conn}")

            else:
                print("⚠️ Aucun certificat trouvé, tentative de connexion générique SSL...")
                if not self.database_name:
                    self.database_name = self.get_data_base_name("@#ssl_reader21", "ssl_reader",host_=host)
                
                self.conn = pymysql.connect(
                    host=host,
                    port=3307,
                    user="ssl_reader",
                    password="@#ssl_reader21",
                    database=self.database_name,
                    cursorclass=DictCursor,
                    ssl={"ssl": {}},
                    autocommit=True
                )

                print(f"✅ Connexion MySQL initialisée with ssl_reader.  {self.conn}")
            return self.conn

        except Exception as e:
            print(f"❌ Erreur lors de la connexion MySQL: {e}")
            traceback.print_exc()
            self.conn = None
            return None  
 


    # 🔹 Exécute une requête SQL (réutilise la connexion persistante)
    def execute_query00(self, query, params=None, fetch=False):
        try:
            conn = self.get_connection()
            if not conn:
                raise ConnectionError("Impossible d'établir une connexion MySQL.")

            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                return cursor.fetchall() if fetch else None

        except (pymysql.err.OperationalError, pymysql.err.InterfaceError):
            # ⚠️ Si la connexion est morte, on réessaie une fois
            print("🔁 Reconnexion MySQL en cours...")
            self.conn = None
            return self.execute_query(query, params, fetch)

        except Exception as e:
            print(f"❌ Erreur SQL: {e}")
            traceback.print_exc()
            return None
        
    def execute_query(self, query, params=None, fetch=False):
        try:
            conn = self.get_connection()
            if not conn:
                raise ConnectionError("Impossible d'établir une connexion MySQL.")

            with conn.cursor() as cursor:
                cursor.execute(query, params or [])
                result = cursor.fetchall() if fetch else None

            # ✅ Fermeture du curseur et commit isolé
            conn.commit()
            return result
        except (pymysql.err.OperationalError, pymysql.err.InterfaceError):
            # ⚠️ Si la connexion est morte, on réessaie une fois
            print("🔁 Reconnexion MySQL en cours...")
            self.conn = None
            # return self.execute_query(query, params, fetch)

        except Exception as e:
            print(f"❌ Erreur SQL: {e}")
            traceback.print_exc()
            return None

        finally:
            if conn and conn.open:
                conn.close()  # ferme la connexion après chaque exécution


    # 🔹 Exemple d’utilisation : compter les étudiants
    def get_students_count(self):
        try:
            result = self.execute_query("SELECT COUNT(*) AS total FROM etudiants", fetch=True)
            return result[0]["total"] if result else 0
        except Exception as e:
            print(f"Erreur dans get_students_count: {e}")
            traceback.print_exc()
            return 0

    # 🔹 Fermer proprement la connexion quand tu quittes l’appli
    def close(self):
        if self.conn:
            print("🧹 Fermeture de la connexion MySQL...")
            self.conn.close()
            self.conn = None
