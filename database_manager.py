import sqlite3
import ipaddress


def connect_to_db(db_name):
    try:
        return sqlite3.connect(db_name)
    except sqlite3.Error as e:
        print(f"Erreur de connexion à la base de données {db_name}: {e}")
        return None


def create_logs_db():
    with connect_to_db("logs.db") as conn:
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY,
                        timestamp TEXT,
                        ip_source TEXT,
                        event_type TEXT,
                        description TEXT,
                        UNIQUE(timestamp, ip_source, event_type)
                    )
                ''')
                conn.commit()
            except sqlite3.Error as e:
                print(f"Erreur lors de la création de la table logs : {e}")


def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def execute_query(db_name, query, params=()):
    try:
        with connect_to_db(db_name) as conn:
            if conn is not None:
                cursor = conn.cursor()

                if len(params) > 1 and not is_valid_ip(params[1]):
                    raise ValueError(f"Adresse IP invalide : {params[1]}")

                cursor.execute(query, params)
                conn.commit()

                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
    except ValueError as ve:
        print(ve)
    return []


create_logs_db()
