import sqlite3


def test_anomalies_detection():
    # Connexion à la base de données
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    # Exécuter une requête simple pour vérifier les données
    cursor.execute("""
        SELECT timestamp, ip_source, COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'LOGIN_ATTEMPT' AND description LIKE '%échouée%'
        GROUP BY ip_source, strftime('%Y-%m-%d %H', timestamp)
        HAVING num_failures >= 1
    """)

    results = cursor.fetchall()
    print("Résultats des tentatives de connexion échouées :")
    for result in results:
        print(result)

    # Fermer la connexion
    conn.close()


# Lancer le test
test_anomalies_detection()
