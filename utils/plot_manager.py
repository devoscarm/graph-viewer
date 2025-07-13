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
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.graph_area.append(self.canvas)

        self.subplots = {"default": self.figure.add_subplot(1, 1, 1)}
        self.curves = {"default": {}}

    def clear_all_curves(self):
        ax = self.subplots["default"]
        for line in self.curves["default"].values():
            line.remove()
        self.curves["default"].clear()
        ax.legend()
        self._refresh_all_plots()


    def add_curve(self, block_id, x_name, y_name, x_vals, y_vals, subplot_id="default"):
        curve_id = f"{block_id}::{x_name}->{y_name}"
        if subplot_id not in self.subplots:
            self.subplots[subplot_id] = self.figure.add_subplot(1, 1, 1)  # per ora, 1x1 layout
            self.curves[subplot_id] = {}

        if curve_id in self.curves[subplot_id]:
            return

        ax = self.subplots[subplot_id]
        line, = ax.plot(x_vals, y_vals, label=curve_id)
        self.curves[subplot_id][curve_id] = line
        ax.legend()
        self._refresh_all_plots()


    def remove_curve(self, block_id, x_name, y_name, subplot_id="default"):
        curve_id = f"{block_id}::{x_name}->{y_name}"
        if subplot_id in self.curves and curve_id in self.curves[subplot_id]:
            line = self.curves[subplot_id].pop(curve_id)
            line.remove()
            self.subplots[subplot_id].legend()
            self._refresh_all_plots()


    def _refresh_all_plots(self):
        for ax in self.subplots.values():
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw()


    def _refresh_plot(self, subplot_id="default"):
        ax = self.subplots[subplot_id]
        ax.relim()
        ax.autoscale_view()
        self.canvas.draw()