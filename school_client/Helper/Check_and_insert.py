import requests
import sqlite3
from Config import BASE_URL

class Check_and_insert:
    def __init__(self):
        # Récupérer les données depuis l'API
        def fetch_data_from_api(table_name):
            url = f"{BASE_URL}{table_name}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Erreur : Impossible de récupérer les données de la table {table_name}")
                return []

        # Générer les requêtes d'insertion
        def generate_insert_queries(table_name, data):
            insert_queries = []
            for row in data:
                columns = ', '.join(row.keys())
                values = ', '.join([f"'{value}'" if isinstance(value, str) else str(value) for value in row.values()])
                insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                insert_queries.append(insert_query)
            return insert_queries

        # Exécuter les requêtes d'insertion
        def execute_insert_queries(insert_queries):
            conn = sqlite3.connect('local_database.db')
            cursor = conn.cursor()
            for query in insert_queries:
                try:
                    cursor.execute(query)
                except sqlite3.OperationalError as e:
                    print(f"Erreur SQLite : {e}")
            conn.commit()
            conn.close()

        # Fonction principale
        def sync_table_data(table_name):
            data = fetch_data_from_api(table_name)
            if data:
                insert_queries = generate_insert_queries(table_name, data)
                execute_insert_queries(insert_queries)
                print(f"Données de la table '{table_name}' synchronisées avec succès.")
            else:
                print(f"Aucune donnée à synchroniser pour la table '{table_name}'.")

        # Synchroniser les données pour une table spécifique
        # sync_table_data('users')