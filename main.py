import sys
import os
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

from components.window import Window
from utils.settings_manager import SettingsManager
from utils.context import AppContext





class GraphApp(Gtk.Application):

    def __init__(self):
        unique_id = f"com.osan.graphviewer.instance_{os.getpid()}"
        super().__init__(application_id=unique_id, flags=Gio.ApplicationFlags.FLAGS_NONE)
        
        self.connect('activate', self.do_activate)

        # Carico le impostazioni iniziali per tutta l'app
        self.settings_manager = SettingsManager()

        self.context = AppContext(app=self, settings_manager=self.settings_manager)

        # Tutte le finestre che potrebbero essere aperte
        self.windows = []
        

    def do_activate(self, app):
        print("APP AVVIATA")
        self.create_new_window()
        
    
    def create_new_window(self, *args):
        window = Window(self.context)
        self.windows.append(window)
        print("NUOVA FINESTRA CREATA: ", self.windows)

        

if __name__ == '__main__':
    print("PROGRAMMA AVVIATO")
    app = GraphApp()

    app.run(sys.argv)