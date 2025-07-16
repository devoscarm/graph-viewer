from gi.repository import Gtk

from utils.logger import get_logger

logger = get_logger(__name__)

class PlotSaver(Gtk.Box):
    def __init__(self, window_context):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window_context = window_context

        self.save_button = Gtk.Button(label="Salva grafico in PNG")
        self.save_button.connect("clicked", self.on_save_clicked)
        self.append(self.save_button)

    def on_save_clicked(self, button):
        plot_manager = getattr(self.window_context, "plot_manager", None)
        if not plot_manager:
            logger.error("PlotManager non disponibile.")
            return

        fig = plot_manager.figure
        try:
            fig.savefig("grafico_salvato.png", dpi=300)
            logger.info("Grafico salvato in 'grafico_salvato.png'")
        except Exception as e:
            logger.error(f"Salvataggio fallito: {e}")