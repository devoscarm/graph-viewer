import gi
from gi.repository import Gtk, GObject

from components.base import BoxBase, ButtonBase
from widgets.theme_selector import ThemeSwitcher



class TopBar(BoxBase):
    def __init__(self, context):
        super().__init__()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_size_request(-1, 30)
        self.parent_window = context.window  
        
        # Pulsante per creare una nuova finestra
        self.new_window_button = NewWindowButton()
        self.append(self.new_window_button)

        # Pulsante per chiudere la finestra corrente
        self.close_window_button = CloseWindowButton(self.parent_window)
        self.append(self.close_window_button)

        # Espansore spingere il selettore di dark mode a dx
        self.append(Gtk.Box(hexpand=True))

        # Selettore del tema chiaro o scuro
        theme_switcher = ThemeSwitcher()
        self.append(theme_switcher)


class NewWindowButton(ButtonBase):
    '''Open a new window'''
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
    '''Close the current window'''

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.set_icon_name('window-close-symbolic')
        self.connect('clicked', lambda *_: self.parent_window.close())


