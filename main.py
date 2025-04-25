import sys
import os
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

from window.panel import TopBar
from utils.settings_manager import SettingsManager




class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_default_size(800, 600)
        self.set_title('Nuova finestra')

        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_child(self.root_box)

        self.top_bar = TopBar(self)
        self.root_box.append(self.top_bar)

        # Nella top bar c'è un pulsante per creare nuove finestre, lo agganciamo qui
        self.top_bar.new_window_button.connect('new-window-requested', app.create_new_window)

        self.present()


class GraphApp(Gtk.Application):

    def __init__(self):
        unique_id = f"com.osan.graphviewer.instance_{os.getpid()}"
        super().__init__(application_id=unique_id, flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.connect('activate', self.do_activate)

        # Carico le impostazioni iniziali per tutta l'app
        self.settings_manager = SettingsManager()

        # Tutte le finestre che potrebbero essere aperte
        self.windows = []
        

    def do_activate(self, app):
        print("APP AVVIATA")
        self.create_new_window()
        
    
    def create_new_window(self, *args):
        window = Window(self)
        self.windows.append(window)



        

if __name__ == '__main__':
    print("PROGRAMMA AVVIATO")
    app = GraphApp()

    app.run(sys.argv)