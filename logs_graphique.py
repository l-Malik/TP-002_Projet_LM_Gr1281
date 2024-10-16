from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.canvas = FigureCanvas(Figure())
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.ax = self.canvas.figure.subplots()
