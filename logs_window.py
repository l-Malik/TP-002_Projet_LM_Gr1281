import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, \
    QLineEdit, QLabel, QHBoxLayout, QMessageBox
from logs_graphique import MplWidget
from import_manager import import_log_file
from anomalies_detection import analyze_anomalies
from anomalies_window import AnomaliesWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.anomalies_window = None

        self.setWindowTitle("Analyseur de Logs Réseau")

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        left_layout = QVBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_logs)
        left_layout.addWidget(QLabel("Recherche :"))
        left_layout.addWidget(self.search_input)

        import_button = QPushButton("Importer les Logs")
        import_button.clicked.connect(self.import_logs)
        left_layout.addWidget(import_button)

        graph_button = QPushButton("Afficher le Graphique")
        graph_button.clicked.connect(self.show_graph)
        left_layout.addWidget(graph_button)

        export_button = QPushButton("Exporter les Logs")
        export_button.clicked.connect(self.export_logs)
        left_layout.addWidget(export_button)

        analyze_button = QPushButton("Analyser les Anomalies")
        analyze_button.clicked.connect(self.analyze_anomalies)
        left_layout.addWidget(analyze_button)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(4)
        self.log_table.setHorizontalHeaderLabels(["Horodatage", "IP Source", "Type d'événement", "Description"])
        left_layout.addWidget(self.log_table)

        self.log_table.setSortingEnabled(True)

        main_layout.addLayout(left_layout)

        self.graph_widget = MplWidget()
        self.graph_widget.setFixedWidth(1000)
        self.graph_widget.setFixedHeight(800)
        main_layout.addWidget(self.graph_widget)

        quit_button = QPushButton("Quitter")
        quit_button.clicked.connect(self.close)

        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addStretch()
        bottom_right_layout.addWidget(quit_button)

        left_layout.addLayout(bottom_right_layout)

        self.load_logs()

        self.center()

    def center(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()

        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)


    def import_logs(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier log", "", "Fichiers texte (*.txt *.log)")

        if file_path:
            try:
                import_log_file(file_path)
                self.load_logs()
                self.show_alert("Importation réussie.")
            except Exception as e:
                self.show_alert(f"Erreur lors de l'importation : {e}")


    def load_logs(self):
        self.log_table.setRowCount(0)

        try:
            with sqlite3.connect("logs.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp, ip_source, event_type, description FROM logs")
                rows = cursor.fetchall()
                for row_data in rows:
                    row_number = self.log_table.rowCount()
                    self.log_table.insertRow(row_number)
                    for column_number, data in enumerate(row_data):
                        item = QTableWidgetItem(str(data))
                        item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                        self.log_table.setItem(row_number, column_number, item)

                self.log_table.resizeColumnsToContents()

                total_table_width = sum(self.log_table.columnWidth(i) for i in range(self.log_table.columnCount())) + 80
                self.setFixedWidth(total_table_width + 1000)
                self.setFixedHeight(800)

        except sqlite3.Error as e:
            self.show_alert(f"Erreur SQL : {e}")


    def filter_logs(self):
        search_text = self.search_input.text().lower()

        for row in range(self.log_table.rowCount()):
            match = False
            for column in range(self.log_table.columnCount()):
                item = self.log_table.item(row, column)
                if item and search_text in item.text().lower():
                    match = True
                    break

            self.log_table.setRowHidden(row, not match)

    def show_graph(self):
        try:
            with sqlite3.connect("logs.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT event_type, COUNT(*) FROM logs GROUP BY event_type")
                data = cursor.fetchall()

            if not data:
                self.show_alert("Aucune donnée disponible pour générer le graphique.")
                return

            event_types = [row[0] for row in data]
            counts = [row[1] for row in data]

            self.graph_widget.ax.clear()

            bar_width = 0.5
            self.graph_widget.ax.bar(event_types, counts, color='skyblue', width=bar_width)
            self.graph_widget.ax.set_xlabel("Type d'événement")
            self.graph_widget.ax.set_ylabel("Nombre d'événements")
            self.graph_widget.ax.set_title("Nombre d'événements par type")

            self.graph_widget.ax.set_xticks(range(len(event_types)))
            self.graph_widget.ax.set_xticklabels(event_types, rotation=30, ha="right")

            self.graph_widget.ax.margins(x=0.1)

            self.graph_widget.canvas.figure.subplots_adjust(bottom=0.2)

            self.graph_widget.canvas.draw()

        except sqlite3.Error as e:
            self.show_alert(f"Erreur lors de l'exécution SQL : {e}")

        except Exception as e:
            self.show_alert(f"Erreur lors de l'affichage du graphique : {e}")


    def export_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exporter les Logs", "", "Text Files (*.txt)")

        if not file_path:
            return

        rows = []
        for row in range(self.log_table.rowCount()):
            if not self.log_table.isRowHidden(row):
                row_data = [
                    self.log_table.item(row, column).text() if self.log_table.item(row, column) else ""
                    for column in range(self.log_table.columnCount())
                ]
                rows.append(row_data)

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                headers = ["Horodatage", "IP Source", "Type d'événement", "Description"]
                file.write(",".join(headers) + "\n")

                for row_data in rows:
                    file.write(",".join(row_data) + "\n")

            self.show_alert("Exportation réussie.")
        except Exception as e:
            self.show_alert(f"Erreur lors de l'exportation : {e}")


    def analyze_anomalies(self):
        try:
            anomalies = analyze_anomalies()

            if anomalies:
                self.anomalies_window = AnomaliesWindow(anomalies)
                self.anomalies_window.window_closed.connect(self.showNormal)
                self.anomalies_window.show()
                self.showMinimized()
            else:
                self.showNormal()
                self.show_alert("Aucune anomalie détectée.")
        except Exception as e:
            self.show_alert(f"Erreur lors de l'analyse des anomalies : {e}")


    def show_alert(self, message):
        alert = QMessageBox()
        alert.setText(message)
        alert.exec()
