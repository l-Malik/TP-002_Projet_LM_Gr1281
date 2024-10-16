import sqlite3


def detect_repeated_login_failures(cursor):
    """Détecte les tentatives de connexion échouées répétées."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Échecs de connexion', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'LOGIN_ATTEMPT' AND description LIKE '%échouée%'
        GROUP BY ip_source, strftime('%Y-%m-%d %H', timestamp)
        HAVING num_failures >= 1
    """)
    return cursor.fetchall()


def detect_unauthorized_file_access(cursor):
    """Détecte les accès non autorisés aux fichiers."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Accès non autorisé', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'FILE_ACCESS' AND description LIKE '%non autorisé%'
        GROUP BY ip_source, strftime('%Y-%m-%d', timestamp)
        HAVING COUNT(*) >= 1
    """)
    return cursor.fetchall()


def detect_firewall_alerts(cursor):
    """Détecte les alertes de pare-feu."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Alerte de pare-feu', COUNT(*) as num_firewall_alerts
        FROM logs
        WHERE event_type = 'FIREWALL_ALERT' AND description LIKE '%tentative autorisée%'
        GROUP BY ip_source, strftime('%Y-%m-%d %H', timestamp)
        HAVING num_firewall_alerts >= 1
    """)
    return cursor.fetchall()


def detect_network_scan(cursor):
    """Détecte les scans de port ou de réseau."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Scan de réseau', COUNT(*) as num_failures
        FROM logs
        WHERE event_type IN ('NETWORK_SCAN', 'PORT_SCAN')
        GROUP BY ip_source, strftime('%Y-%m-%d', timestamp)
        HAVING COUNT(*) >= 1
    """)
    return cursor.fetchall()


def detect_unexpected_shutdown(cursor):
    """Détecte les arrêts inattendus du système."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Arrêt inattendu', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'SYSTEM_RESTART' AND description LIKE '%Arrêt inattendu%'
        GROUP BY ip_source, strftime('%Y-%m-%d', timestamp)
        HAVING num_failures >= 1
    """)
    return cursor.fetchall()


def detect_password_change_failures(cursor):
    """Détecte les échecs répétés de changement de mot de passe."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Échec du changement de mot de passe', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'PASSWORD_CHANGE' AND description LIKE '%Échec du changement de mot de passe%'
        GROUP BY ip_source, strftime('%Y-%m-%d %H', timestamp)
        HAVING num_failures >= 1
    """)
    return cursor.fetchall()


def detect_malware(cursor):
    """Détecte les logiciels malveillants."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Détection de logiciel malveillant', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'MALWARE_DETECTION' AND description LIKE '%Détection de logiciel malveillant%'
        GROUP BY ip_source, strftime('%Y-%m-%d', timestamp)
        HAVING num_failures >= 1
    """)
    return cursor.fetchall()


def detect_software_installation_failures(cursor):
    """Détecte les échecs d'installation de logiciels."""
    cursor.execute("""
        SELECT timestamp, ip_source, 'Échec installation logiciel', COUNT(*) as num_failures
        FROM logs
        WHERE event_type = 'SOFTWARE_INSTALLATION' AND description LIKE '%échouée%'
        GROUP BY ip_source, strftime('%Y-%m-%d %H', timestamp)
        HAVING num_failures >= 1
    """)
    return cursor.fetchall()


def analyze_anomalies():
    conn = sqlite3.connect("logs.db")
    cursor = conn.cursor()

    anomalies = []

    anomalies.extend(detect_repeated_login_failures(cursor))
    anomalies.extend(detect_unauthorized_file_access(cursor))
    anomalies.extend(detect_firewall_alerts(cursor))
    anomalies.extend(detect_network_scan(cursor))
    anomalies.extend(detect_unexpected_shutdown(cursor))
    anomalies.extend(detect_password_change_failures(cursor))
    anomalies.extend(detect_malware(cursor))
    anomalies.extend(detect_software_installation_failures(cursor))

    return anomalies
