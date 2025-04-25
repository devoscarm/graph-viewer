import gi

# gi.require_version('Gtc', '4.0')

from gi.repository import Gtk, GObject

from utils.theme_selector import ThemeSwitcher
from window.buttons import ButtonBase


class BoxBase(Gtk.Box):
    def __init__(self):
    # def __init__(self, on_new_window_callback):

        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.set_size_request(-1, 40)
        self.label = Gtk.Label(label="Panel Base")
        self.append(self.label)
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(6)
        self.set_margin_end(6)


class TopBar(BoxBase):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window   
        
        # Pulsante per creare una nuova finestra
        self.new_window_button = NewWindowButton()
        self.append(self.new_window_button)

        # Pulsante per chiudere la finestra corrente
        self.close_window_button = CloseWindowButton(self.parent_window)
        self.append(self.close_window_button)

        # Espansore spingere il selettore di dark mode a dx
        self.append(Gtk.Box(hexpand=True))

        theme_switcher = ThemeSwitcher()
        self.append(theme_switcher)


class NewWindowButton(ButtonBase):
    # Registro il segnale che emetterà
    __gtype_name__ = 'NewWindowButton'
    __gsignals__ = {
        'new-window-requested': (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    def __init__(self):
        super().__init__()
        self.set_icon_name('window-new-symbolic')
        self.connect('clicked', self.on_clicked)

    # Collegando un segnale (evento) a un oggetto di tipo Gtk
    # otteniamo l'argomento self (pulsante che ha emesso il segnale)
    # e l'oggetto Gtk.Button che è stato cliccato
    def on_clicked(self, button):
        self.emit('new-window-requested')


        
class CloseWindowButton(ButtonBase):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.set_icon_name('window-close-symbolic')
        self.connect('clicked', lambda *_: self.parent_window.close())


