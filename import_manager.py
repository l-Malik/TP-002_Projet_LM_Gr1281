import sqlite3


def import_log_file(file_path):
    success_count = 0
    duplicate_count = 0
    error_lines = []

    with sqlite3.connect("logs.db") as conn:
        cursor = conn.cursor()

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    parts = line.strip().split(", ")
                    if len(parts) == 4:
                        timestamp, ip_source, event_type, description = parts

                        try:
                            cursor.execute('''
                                INSERT OR IGNORE INTO logs (timestamp, ip_source, event_type, description)
                                VALUES (?, ?, ?, ?)
                            ''', (timestamp, ip_source, event_type, description))
                            if cursor.rowcount == 1:
                                success_count += 1
                            else:
                                duplicate_count += 1
                        except sqlite3.Error as e:
                            error_lines.append((line_number, line.strip(), f"Erreur SQL : {e}"))
                    else:
                        error_lines.append((line_number, line.strip(), "Format de ligne invalide"))

            conn.commit()

        except Exception as e:
            raise ValueError(f"Erreur lors de l'import du fichier : {e}")

    return {
        "success_count": success_count,
        "duplicate_count": duplicate_count,
        "error_lines": error_lines
    }
