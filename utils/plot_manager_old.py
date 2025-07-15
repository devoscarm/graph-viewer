import matplotlib
import time # Per il ritardo del doppio click del reset zoom
matplotlib.use('GTK4Agg')  # Importantissimo!
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
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


        # Aggiunte per zoom, reset zoom, pan
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_motion)

        self._zoom_start = None
        self._zoom_rect = None
        self._original_xlim = {}
        self._original_ylim = {}

        # Per reset zoom
        self._last_click_time = 0
        self._click_interval = 0.3  # secondi ritardo doppio click



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



    # Funzioni per zoom, zoom reset e pan

    def on_mouse_press(self, event):
        if event.inaxes is None:
            return

        ax = event.inaxes
        subplot_id = self._get_subplot_id_by_ax(ax)
        

        # RESET DELLO ZOOM
        # Spesso non è disponibile in GTK
        if event.dblclick:
            logger.info("Zoom reset by event.dblclick")
            # Reset zoom
            ax.set_xlim(self._original_xlim.get(subplot_id, ax.get_xlim()))
            ax.set_ylim(self._original_ylim.get(subplot_id, ax.get_ylim()))
            self.canvas.draw()
            return
        
        # Se non è disponibile l'evento dblclick, famo così
        t = time.time()
        if t - self._last_click_time < self._click_interval:
            logger.info("Zoom reset by delay scamuffo")
            ax.set_xlim(self._original_xlim.get(subplot_id, ax.get_xlim()))
            ax.set_ylim(self._original_ylim.get(subplot_id, ax.get_ylim()))
            self.canvas.draw()
            self._last_click_time = 0
            return
        else:
            self._last_click_time = t


        # Salva limiti originali
        if subplot_id not in self._original_xlim:
            self._original_xlim[subplot_id] = ax.get_xlim()
            self._original_ylim[subplot_id] = ax.get_ylim()

        self._zoom_start = (event.xdata, event.ydata)

        # Rettangolo di selezione per zoom
        if self._zoom_rect:
            self._zoom_rect.remove()
            self._zoom_rect = None

        self._zoom_rect = Rectangle(
            (event.xdata, event.ydata), 0, 0,
            fill=False, edgecolor='black', linewidth=1.0, linestyle='--'
        )
        event.inaxes.add_patch(self._zoom_rect)
        self.canvas.draw()

        # Pan (trascinamento grafico)
        if event.button == 3:  # tasto destro
            self._pan_start = (event.xdata, event.ydata)
            self._pan_xlim = ax.get_xlim()
            self._pan_ylim = ax.get_ylim()



    def on_mouse_release(self, event):
        if event.inaxes is None or self._zoom_start is None:
            return

        x0, y0 = self._zoom_start
        x1, y1 = event.xdata, event.ydata
        ax = event.inaxes
        subplot_id = self._get_subplot_id_by_ax(ax)

        if None not in (x0, y0, x1, y1) and abs(x1 - x0) > 1e-5 and abs(y1 - y0) > 1e-5:
            ax.set_xlim(min(x0, x1), max(x0, x1))
            ax.set_ylim(min(y0, y1), max(y0, y1))
            self.canvas.draw()

        self._zoom_start = None

        # Eliminazione rettangolo di selezione
        if self._zoom_rect:
            self._zoom_rect.remove()
            self._zoom_rect = None
            self.canvas.draw()

        
        # Pan (trascinamento grafico)
        if hasattr(self, "_pan_start"):
            self._pan_start = None



    def on_mouse_motion(self, event):

        # Muove e modifica il rettangolo di selezione
        if self._zoom_start and self._zoom_rect and event.inaxes:
            x0, y0 = self._zoom_start
            x1, y1 = event.xdata, event.ydata

            if None not in (x0, y0, x1, y1):
                self._zoom_rect.set_width(x1 - x0)
                self._zoom_rect.set_height(y1 - y0)
                self._zoom_rect.set_xy((x0, y0))
                self.canvas.draw()
        

        # Pan (trascinamento grafico)
        if hasattr(self, "_pan_start") and self._pan_start and event.inaxes:
            x0, y0 = self._pan_start
            dx = event.xdata - x0
            dy = event.ydata - y0
            ax.set_xlim(self._pan_xlim[0] - dx, self._pan_xlim[1] - dx)
            ax.set_ylim(self._pan_ylim[0] - dy, self._pan_ylim[1] - dy)
            self.canvas.draw()


    
    def _get_subplot_id_by_ax(self, ax):
        for subplot_id, subplot_ax in self.subplots.items():
            if subplot_ax == ax:
                return subplot_id
        return "default"
