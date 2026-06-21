import requests
import sqlite3
from Config import BASE_URL
 
API_URL= BASE_URL +'schema'

class Check_db:
    def __init__(self):
        pass

        schema_response = requests.get(API_URL)
        schema = schema_response.json()


        self.conn = sqlite3.connect('local_database.db')
        cursor = self.conn.cursor()


        def map_column_type(sql_type):
            if 'int' in sql_type:
                return 'INTEGER'
            elif 'varchar' in sql_type or 'text' in sql_type:
                return 'TEXT'
            elif 'datetime' in sql_type or 'timestamp' in sql_type:
                return 'DATETIME'
            elif 'float' in sql_type or 'double' in sql_type or 'decimal' in sql_type:
                return 'REAL'
            elif 'boolean' in sql_type:
                return 'BOOLEAN'
            else:
                return 'TEXT'  
            
        def table_exists(table_name):
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            return cursor.fetchone() is not None

        # Fonction pour récupérer les colonnes existantes d'une table
        def get_existing_columns(table_name):
            cursor.execute(f"PRAGMA table_info({table_name});")
            return [column[1] for column in cursor.fetchall()]  # Retourne la liste des noms de colonnes

        # Fonction pour créer ou mettre à jour une table
        def create_or_update_table(table_name, columns):
            if not table_exists(table_name):
                # Créer la table si elle n'existe pas
                columns_sql = []
                for column in columns:
                    column_name = column['Field']
                    column_type = map_column_type(column['Type'])
                    column_nullable = 'NULL' if column['Null'] == 'YES' else 'NOT NULL'
                    column_primary_key = 'PRIMARY KEY' if column['Key'] == 'PRI' else ''
                    column_default = f"DEFAULT {column['Default']}" if column['Default'] is not None else ''
                    columns_sql.append(f"{column_name} {column_type} {column_nullable} {column_primary_key} {column_default}")
                
                create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns_sql)});"
                cursor.execute(create_table_sql)
                print(f"Table '{table_name}' créée.")
            else:
                # Mettre à jour la table si elle existe déjà
                existing_columns = get_existing_columns(table_name)
                for column in columns:
                    column_name = column['Field']
                    if column_name not in existing_columns:
                        # Ajouter la colonne si elle n'existe pas
                        column_type = map_column_type(column['Type'])
                        column_nullable = 'NULL' if column['Null'] == 'YES' else 'NOT NULL'
                        column_default = f"DEFAULT {column['Default']}" if column['Default'] is not None else ''
                        add_column_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {column_nullable} {column_default};"
                        cursor.execute(add_column_sql)
                        print(f"Colonne '{column_name}' ajoutée à la table '{table_name}'.")

        # Créer ou mettre à jour les tables en fonction du schéma
        for table_name, columns in schema.items():
            create_or_update_table(table_name, columns)

        # Valider les changements et fermer la connexion
        self.conn.commit()
        self.conn.close()