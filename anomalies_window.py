from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QTableWidget, QTableWidgetItem, QWidget, QPushButton, QHBoxLayout, \
    QInputDialog, QMessageBox
from logs_graphique import MplWidget


class AnomaliesWindow(QMainWindow):

    window_closed = pyqtSignal()

    def __init__(self, anomalies):
        super().__init__()

        self.anomalies = anomalies
        self.setWindowTitle("Anomalies Détectées")

        central_widget = QWidget()
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        left_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        graph_button = QPushButton("Afficher le Graphique")
        graph_button.clicked.connect(self.show_graph)
        left_layout.addWidget(graph_button)

        filter_button = QPushButton("Tri des événements")
        filter_button.clicked.connect(self.filter_anomalies)
        left_layout.addWidget(filter_button)

        reset_button = QPushButton("Réinitialiser le filtre")
        reset_button.clicked.connect(self.reset_filter)
        left_layout.addWidget(reset_button)

        self.anomalies_table = QTableWidget()
        self.anomalies_table.setColumnCount(5)
        self.anomalies_table.setHorizontalHeaderLabels(["Horodatage", "IP Source", "Type d'Anomalie", "Nombre de Tentatives", "Total"])

        self.fill_anomalies_table(self.anomalies)

        left_layout.addWidget(self.anomalies_table)

        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()

        self.graph_widget = MplWidget()
        self.graph_widget.setFixedWidth(1000)
        self.graph_widget.setFixedHeight(800)
        right_layout.addWidget(self.graph_widget)

        main_layout.addLayout(right_layout)

        total_table_width = sum(self.anomalies_table.columnWidth(i) for i in range(self.anomalies_table.columnCount()))
        self.setFixedWidth(total_table_width + 1000 + 50)  # Prendre en compte la largeur du graphique
        self.setFixedHeight(800)

        self.center()


    def center(self):
        screen_geometry = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()

        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2
        self.move(x, y)


    def fill_anomalies_table(self, anomalies):
        self.anomalies_table.setRowCount(0)

        total_attempts_per_type = {}
        for anomaly in anomalies:
            anomaly_type = anomaly[2]
            total_attempts_per_type[anomaly_type] = total_attempts_per_type.get(anomaly_type, 0) + int(anomaly[3])

        for anomaly in anomalies:
            row_number = self.anomalies_table.rowCount()
            self.anomalies_table.insertRow(row_number)
            for column_number, data in enumerate(anomaly):
                item = QTableWidgetItem(str(data))
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.anomalies_table.setItem(row_number, column_number, item)

            anomaly_type = anomaly[2]
            total_attempts = total_attempts_per_type[anomaly_type]
            total_item = QTableWidgetItem(str(total_attempts))
            total_item.setFlags(total_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.anomalies_table.setItem(row_number, 4, total_item)

        self.anomalies_table.resizeColumnsToContents()


    def filter_anomalies(self):

        anomaly_types = list(set([anomaly[2] for anomaly in self.anomalies]))
        selected_type, ok = QInputDialog.getItem(self, "Sélectionner un type d'anomalie",
                                                 "Types d'anomalies :", anomaly_types, 0, False)

        if ok and selected_type:
            filtered_anomalies = [anomaly for anomaly in self.anomalies if anomaly[2] == selected_type]
            self.fill_anomalies_table(filtered_anomalies)


    def reset_filter(self):
        self.fill_anomalies_table(self.anomalies)


    def show_graph(self):

        anomaly_types = {}
        for row in range(self.anomalies_table.rowCount()):
            anomaly_type = self.anomalies_table.item(row, 2).text()
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1

        self.graph_widget.ax.clear()

        event_types = list(anomaly_types.keys())
        counts = list(anomaly_types.values())

        bar_width = 0.5
        self.graph_widget.ax.bar(event_types, counts, color='darkred', width=bar_width)
        self.graph_widget.ax.set_xlabel("Type d'anomalie")
        self.graph_widget.ax.set_ylabel("Nombre d'occurrences")
        self.graph_widget.ax.set_title("Nombre d'anomalies par type")
        self.graph_widget.ax.set_xticks(range(len(event_types)))
        self.graph_widget.ax.set_xticklabels(event_types, rotation=30, ha="right")
        self.graph_widget.ax.margins(x=0.1)
        self.graph_widget.canvas.figure.subplots_adjust(bottom=0.25)
        self.graph_widget.canvas.draw()


    def closeEvent(self, event):
        self.window_closed.emit()
        event.accept()
