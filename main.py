import sys
import os
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

from components.panel import OrizontalSeparator, VerticalSeparator, MainArea, GraphArea
from components.sidebar import LeftSidebar, RightSidebar
from components.top_bar import TopBar
from utils.settings_manager import SettingsManager

from components.base import BoxBase




class Window(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)

        self.set_default_size(800, 600)
        self.set_title('Nuova finestra')

        # self.window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.window_box = BoxBase()
        self.window_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_child(self.window_box)

        self.top_bar = TopBar(self)
        self.window_box.append(self.top_bar)

        self.orizontal_separator = OrizontalSeparator()
        self.window_box.append(self.orizontal_separator)

        # Nella top bar c'è un pulsante per creare nuove finestre, lo agganciamo qui
        self.top_bar.new_window_button.connect('new-window-requested', app.create_new_window)

        self.main_area = MainArea()
        self.window_box.append(self.main_area)

        self.left_sidebar = LeftSidebar()
        self.main_area.append(self.left_sidebar)

        self.vertical_separator = VerticalSeparator()
        self.main_area.append(self.vertical_separator)

        self.graph_area = GraphArea()
        self.main_area.append(self.graph_area)

        self.vertical_separator1 = VerticalSeparator()
        self.main_area.append(self.vertical_separator1)

        self.right_sidebar = RightSidebar()
        self.main_area.append(self.right_sidebar)

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