import requests
import sqlite3
from Config import BASE_URL

# class Sync_data:
#     def __init__(self):

# 1. Récupérer les données depuis l'API
def fetch_data_from_api(table_name):
    url = f"{BASE_URL}data/{table_name}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur : Impossible de récupérer les données de la table {table_name}")
        return []

# 2. Vérifier si un enregistrement existe déjà
def record_exists(cursor, table_name, primary_key, record):
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {primary_key} = ?"
    cursor.execute(query, (record[primary_key],))
    return cursor.fetchone()[0] > 0

# 3. Insérer ou mettre à jour l'enregistrement
def create_or_update_record(cursor, table_name, primary_key, record):
    if record_exists(cursor, table_name, primary_key, record):
        # Mettre à jour l'enregistrement
        set_clause = ', '.join([f"{key} = ?" for key in record.keys() if key != primary_key])
        update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
        values = [record[key] for key in record.keys() if key != primary_key] + [record[primary_key]]
        cursor.execute(update_query, values)
        print(f"Enregistrement mis à jour dans la table '{table_name}' : {record}")
    else:
        # Insérer l'enregistrement
        columns = ', '.join(record.keys())
        placeholders = ', '.join(['?'] * len(record))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(insert_query, list(record.values()))
        print(f"Enregistrement inséré dans la table '{table_name}' : {record}")

# 4. Synchroniser les données avec "create or update"
def sync_table_data(table_name, primary_key):
        try:
            # Récupérer les données depuis l'API
            data = fetch_data_from_api(table_name)
            if not data:
                print(f"Aucune donnée à synchroniser pour la table '{table_name}'.")
                return

            # Se connecter à la base de données SQLite
            conn = sqlite3.connect('local_database.db')
            cursor = conn.cursor()

            # Synchroniser chaque enregistrement
            for record in data:
                create_or_update_record(cursor, table_name, primary_key, record)

            # Valider les changements et fermer la connexion
            conn.commit()
            conn.close()
            print(f"Données de la table '{table_name}' synchronisées avec succès.")
        except Exception as e:
            print(f"Erreur lors de la synchronisation de la table '{table_name}' : {e}")

        # 5. Exemple d'utilisation
        # if __name__ == "__main__":
            # Synchroniser la table 'users' avec la clé primaire 'id'
            # sync_table_data('users', 'id')