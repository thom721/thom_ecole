import sqlite3
import requests

# 1. Détecter les enregistrements modifiés localement
def get_modified_records(table_name):
    """
    Récupère les enregistrements modifiés dans la base de données SQLite locale.
    """
    conn = sqlite3.connect('local_database.db')
    cursor = conn.cursor()

    # Récupérer les enregistrements marqués comme modifiés
    query = f"SELECT * FROM {table_name} WHERE is_modified = 1;"  # Exemple : utiliser un champ is_modified
    cursor.execute(query)
    records = cursor.fetchall()

    conn.close()
    return records

# 2. Envoyer les modifications à l'API distante
def update_record_on_api(table_name, record):
    """
    Envoie une requête HTTP PUT ou PATCH à l'API pour mettre à jour un enregistrement.
    """
    url = f"http://api-distante.com/update/{table_name}"
    try:
        response = requests.put(url, json=record)  # Utiliser PUT ou PATCH pour la mise à jour
        if response.status_code == 200:
            print(f"Enregistrement mis à jour sur l'API : {record}")
            return True
        else:
            print(f"Erreur lors de la mise à jour de l'enregistrement : {record}")
            return False
    except requests.RequestException as e:
        print(f"Erreur de connexion à l'API : {e}")
        return False

# 3. Marquer un enregistrement comme synchronisé
def mark_record_as_synced(table_name, record_id):
    """
    Marque un enregistrement comme synchronisé dans la base de données locale.
    """
    conn = sqlite3.connect('local_database.db')
    cursor = conn.cursor()

    # Marquer l'enregistrement comme synchronisé
    query = f"UPDATE {table_name} SET is_modified = 0 WHERE id = ?;"
    cursor.execute(query, (record_id,))
    conn.commit()
    conn.close()
    print(f"Enregistrement {record_id} marqué comme synchronisé.")

# 4. Synchroniser les modifications locales avec l'API
def sync_local_changes_to_api(table_name):
    """
    Synchronise les modifications locales avec l'API distante.
    """
    try:
        # Récupérer les enregistrements modifiés localement
        modified_records = get_modified_records(table_name)
        if not modified_records:
            print(f"Aucun enregistrement modifié dans la table '{table_name}'.")
            return

        # Pour chaque enregistrement modifié
        for record in modified_records:
            # Convertir l'enregistrement en dictionnaire
            record_dict = {
                "id": record[0],  # Supposons que la première colonne est l'ID
                "name": record[1],
                "email": record[2],
                # Ajouter d'autres champs ici
            }

            # Mettre à jour l'enregistrement sur l'API
            if update_record_on_api(table_name, record_dict):
                # Marquer l'enregistrement comme synchronisé
                mark_record_as_synced(table_name, record[0])
    except Exception as e:
        print(f"Erreur lors de la synchronisation des modifications : {e}")

# 5. Exemple d'utilisation
# if __name__ == "__main__":
    # Synchroniser les modifications locales avec l'API pour la table 'users'
    sync_local_changes_to_api('users')