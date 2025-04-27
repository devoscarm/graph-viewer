import matplotlib
matplotlib.use('GTK4Agg')  # Importantissimo!
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas

from gi.repository import Gtk

class PlotManager:
    def __init__(self, graph_area):
        self.graph_area = graph_area
        self.header = []
        self.data = []
        self.selected_columns = {}

    def set_data(self, header, data):
        self.header = header
        self.data = data

    def set_selected_columns(self, selected_columns):
        self.selected_columns = selected_columns

    def plot(self):
        if not self.data or not self.selected_columns:
            print("[PlotManager] No data or no columns selected.")
            return
        
        figure = Figure(figsize=(5, 4), dpi=100)
        ax = figure.add_subplot(1, 1, 1)

        x_data = []
        y_data = []

        # Estrai colonne scelte
        for i, row in enumerate(self.data):
            x_val = None
            y_val = None
            for col_name, axis in self.selected_columns.items():
                col_idx = self.header.index(col_name)
                value = float(row[col_idx]) if row[col_idx] else None

                if axis == "X":
                    x_val = value
                elif axis == "Y":
                    y_val = value
            
            if x_val is not None and y_val is not None:
                x_data.append(x_val)
                y_data.append(y_val)

        ax.plot(x_data, y_data)
        ax.set_xlabel("X axis")
        ax.set_ylabel("Y axis")
        ax.set_title("Plot")

        # Rimuovi grafici vecchi dalla graph_area
        for child in self.graph_area.get_children():
            self.graph_area.remove(child)

        canvas = FigureCanvas(figure)
        self.graph_area.append(canvas)
        canvas.show()
