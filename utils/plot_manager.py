import matplotlib
matplotlib.use('GTK4Agg')  # Importantissimo!
from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg as FigureCanvas

from gi.repository import Gtk
from utils.logger import get_logger

logger = get_logger(__name__)

class PlotManager:
    def __init__(self, graph_area):
        self.graph_area = graph_area
        self.header = []
        self.data = []
        self.selected_columns = {}

        # Creating figure
        self.figure = Figure(figsize=(10, 10), dpi=100)

        # Creating canvas in the figure or around figure?
        self.canvas = FigureCanvas(self.figure)

        self.graph_area.append(self.canvas)

        # Creating "Axes"
        self.ax = self.figure.add_subplot(111)

        self.plot_empty()

    
    def set_data(self, data_block):
        self.data = data_block
        self.plot()



    def set_data_old(self, header, data):
        self.header = header
        self.data = data
        self.plot()

    def set_selected_columns(self, selected_columns):
        self.selected_columns = selected_columns

    def plot_empty(self):
        self.ax.clear()
        self.ax.set_title("No data loaded")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.canvas.draw()
        logger.info("Plot empty")



    def plot(self):
        self.ax.clear()

        if not self.data:
            self.plot_empty()
            return

        for block_index, (header, xy_data) in enumerate(self.data.items()):

            # logger.debug(header)
            # for row in xy_data:
            #     logger.debug(row)
                
            if not xy_data:
                continue
            x_data, y_data = zip(*xy_data)
            # label = " - ".join(header) if isinstance(header, tuple) else str(header)
            label = f"Block {block_index + 1}"
            self.ax.plot(x_data, y_data, label=label)

        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.set_title("Plot")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()



    def plot_old(self):
        if not self.data or not self.selected_columns:
            logger.info(f"No data columns selected > {self.selected_columns}")

        #logger.info(f"Columns selected > {self.selected_columns}") 
        # logger.info       

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

        self.ax.plot(x_data, y_data)
        self.ax.set_xlabel("X axis")
        self.ax.set_ylabel("Y axis")
        self.ax.set_title("Plot")

        # Rimuovi grafici vecchi dalla graph_area
        # for child in self.graph_area.get_children():
        # self.graph_area.remove(child)

        
        self.canvas.show()
