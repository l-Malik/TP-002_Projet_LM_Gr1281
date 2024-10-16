import sys
from PyQt6.QtWidgets import QApplication
from database_manager import create_logs_db
from logs_window import MainWindow


def main():
    create_logs_db()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    close_connection("logs.db")


if __name__ == "__main__":
    main()
