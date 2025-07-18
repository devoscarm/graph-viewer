import matplotlib
import time  # Per il ritardo del doppio click del reset zoom
matplotlib.use('GTK4Agg') 
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

        # For subplot settings on right sidebar
        self.selected_axes = None
        self.on_subplot_selected_callback = None
        self.canvas.mpl_connect("button_press_event", self._on_click)

        # Provo a forzare il focus per gli scroll event
        # Infine non funziona, uso motion_notify_event
        # self.canvas.set_can_focus(True)
        # self.canvas.grab_focus()

        # We register the last valid event.inaxes to access also if
        # scroll_event can't receive it
        self._last_active_axes = None


        self.subplots = {"default": self.figure.add_subplot(1, 1, 1)}
        self.curves = {"default": {}}

        # Aggiunte per zoom, reset zoom, pan
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_motion)
        self.canvas.mpl_connect("scroll_event", self.on_mouse_scroll)

        self._zoom_start = None
        self._zoom_rect = None
        self._original_xlim = {}
        self._original_ylim = {}

        # Per reset zoom (fallback al doppio click simulato)
        self._last_click_time = 0
        self._click_interval = 0.3

        # Variabili per pan
        self._pan_start = None
        self._pan_xlim = None
        self._pan_ylim = None

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
            self.subplots[subplot_id] = self.figure.add_subplot(1, 1, 1)  # Placeholder per layout dinamico
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
            #ax.autoscale_view()
            ax.autoscale()
        self.canvas.draw()  # draw() è più veloce di queue_draw()

    def _refresh_plot(self, subplot_id="default"):
        ax = self.subplots[subplot_id]
        #ax.relim() # Ricalcola i limiti e mi sembra che non serva
        #ax.autoscale_view()
        ax.autoscale()
        self.canvas.draw()


    # For subplot settings on right sidebar
    def _on_click(self, event):
        if event.inaxes in self.figure.axes:
            self.selected_axes = event.inaxes
            if self.on_subplot_selected_callback:
                self.on_subplot_selected_callback(event.inaxes)



    # Funzioni per zoom, zoom reset e pan

    def on_mouse_press(self, event):
        # logger.debug(f"ON MOUSE PRESS > {event}")

        if event.inaxes is None:
            return

        ax = event.inaxes
        subplot_id = self._get_subplot_id_by_ax(ax)

        # RESET DELLO ZOOM (dblclick o click veloce)
        if event.dblclick:
            logger.info("Zoom reset by event.dblclick")
            self._refresh_plot(subplot_id)
            # ax.set_xlim(self._original_xlim.get(subplot_id, ax.get_xlim()))
            # ax.set_ylim(self._original_ylim.get(subplot_id, ax.get_ylim()))
            # self.canvas.draw()
            return

        # Fallback se non funziona il dblclick
        t = time.time()
        if t - self._last_click_time < self._click_interval:
            logger.info("Zoom reset by delay scamuffo")
            self._refresh_plot(subplot_id)
            # ax.set_xlim(self._original_xlim.get(subplot_id, ax.get_xlim()))
            # ax.set_ylim(self._original_ylim.get(subplot_id, ax.get_ylim()))
            # self.canvas.draw()
            self._last_click_time = 0
            return
        else:
            self._last_click_time = t

        # Salva limiti originali (una sola volta)
        if subplot_id not in self._original_xlim:
            self._original_xlim[subplot_id] = ax.get_xlim()
            self._original_ylim[subplot_id] = ax.get_ylim()

        # Rettangolo di selezione per zoom
        if event.button == 1:
            self._zoom_start = (event.xdata, event.ydata)

        if self._zoom_rect:
            self._zoom_rect.remove()
            self._zoom_rect = None

        self._zoom_rect = Rectangle(
            (event.xdata, event.ydata), 0, 0,
            fill=False, edgecolor='black', linewidth=1.0, linestyle='--'
        )
        ax.add_patch(self._zoom_rect)
        self.canvas.draw()

        # PAN (col tasto destro)
        if event.button == 3:  # tasto destro
            self._pan_start = (event.xdata, event.ydata)
            self._pan_xlim = ax.get_xlim()
            self._pan_ylim = ax.get_ylim()
            self._pan_ax = ax

    def on_mouse_release(self, event):
        # logger.debug(f"ON MOUSE RELEASE > {event}")

        if event.inaxes is None or self._zoom_start is None:
            return

        x0, y0 = self._zoom_start
        x1, y1 = event.xdata, event.ydata
        ax = event.inaxes

        if None not in (x0, y0, x1, y1) and abs(x1 - x0) > 1e-5 and abs(y1 - y0) > 1e-5:
            ax.set_xlim(min(x0, x1), max(x0, x1))
            ax.set_ylim(min(y0, y1), max(y0, y1))
            self.canvas.draw()

        self._zoom_start = None

        # Elimina rettangolo di selezione
        if self._zoom_rect:
            self._zoom_rect.remove()
            self._zoom_rect = None
            self.canvas.draw()

        # Reset pan
        self._pan_start = None
        self._pan_ax = None

    def on_mouse_motion(self, event):

        #logger.debug(f"ON MOUSE MOTION > {event}")

        # Registering last valid event.inaxes (for scroll zoom)
        if event.inaxes:
            self._last_active_axes = event.inaxes

        # Rettangolo di selezione zoom
        if self._zoom_start and self._zoom_rect and event.inaxes:
            x0, y0 = self._zoom_start
            x1, y1 = event.xdata, event.ydata
            if None not in (x0, y0, x1, y1):
                self._zoom_rect.set_width(x1 - x0)
                self._zoom_rect.set_height(y1 - y0)
                self._zoom_rect.set_xy((x0, y0))
                self.canvas.draw()

        # PAN
        if self._pan_start and event.inaxes and self._pan_ax:
            dx = event.xdata - self._pan_start[0]
            dy = event.ydata - self._pan_start[1]
            new_xlim = (self._pan_xlim[0] - dx, self._pan_xlim[1] - dx)
            new_ylim = (self._pan_ylim[0] - dy, self._pan_ylim[1] - dy)
            self._pan_ax.set_xlim(new_xlim)
            self._pan_ax.set_ylim(new_ylim)
            self.canvas.draw()


    def on_mouse_scroll(self, event):

        #logger.debug(f"ON MOUSE SCROLL > {event}")

        ax = event.inaxes or self._last_active_axes

        if ax is None:
            return
        
        subplot_id = self._get_subplot_id_by_ax(ax)

        # Manually converting x, y to data coordinates (same problem of
        # ax for scroll on GTK)
        try:
            # Forza conversione coordinate pixel → dati
            xdata, ydata = ax.transData.inverted().transform((event.x, event.y))
        except Exception as e:
            logger.warning(f"Could not transform scroll coordinates: {e}")
            return

        base_scale = 1.1
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale
        # if event.button == 'up':
        #     scale_factor = 1 / base_scale  # Zoom in
        # elif event.button == 'down':
        #     scale_factor = base_scale      # Zoom out
        # else:
        #     return

        # Coordinate attuali
        # xdata = event.xdata
        # ydata = event.ydata

        # Limiti attuali
        # cur_xlim = ax.get_xlim()
        # cur_ylim = ax.get_ylim()

        # # Nuovi limiti basati sulla posizione del mouse
        # new_xlim = [
        #     xdata - (xdata - cur_xlim[0]) * scale_factor,
        #     xdata + (cur_xlim[1] - xdata) * scale_factor
        # ]
        # new_ylim = [
        #     ydata - (ydata - cur_ylim[0]) * scale_factor,
        #     ydata + (cur_ylim[1] - ydata) * scale_factor
        # ]

        # Limiti attuali degli assi
        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()

        # Calcolo nuovi limiti mantenendo il centro sul puntatore
        x_range = (x_right - x_left) * scale_factor
        y_range = (y_top - y_bottom) * scale_factor

        new_x_left = xdata - (xdata - x_left) * scale_factor
        new_x_right = xdata + (x_right - xdata) * scale_factor

        new_y_bottom = ydata - (ydata - y_bottom) * scale_factor
        new_y_top = ydata + (y_top - ydata) * scale_factor

        # Applica i nuovi limiti
        ax.set_xlim(new_x_left, new_x_right)
        ax.set_ylim(new_y_bottom, new_y_top)

        # ax.set_xlim(new_xlim)
        # ax.set_ylim(new_ylim)
        self.canvas.draw()

        # logger.debug(f"Scroll zoom @ data coords: ({xdata:.2f}, {ydata:.2f})")



    def _get_subplot_id_by_ax(self, ax):
        for subplot_id, subplot_ax in self.subplots.items():
            if subplot_ax == ax:
                return subplot_id
        return "default"
