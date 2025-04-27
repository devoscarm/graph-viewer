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
            
        # 'activate' signal pass as first parametere, the calling app!
        self.connect('activate', self.do_activate)

        # Loading last session app configurations
        self.settings_manager = SettingsManager()

        # Saving useful "global" objects
        self.app_context = AppContext(
            app=self, 
            settings_manager=self.settings_manager
        )

        
    # 'activate' signal pass as first parametere, the calling app!
    def do_activate(self, app):
        print("[GraphApp] APPLICATION STARTED!")
        self.create_new_window()
        
    # 'clicked' signal pass the button pressed and other parameters
    # *args accept all extra parameters as list
    # **kwargs accept all extra name parameters as dictionary
    def create_new_window(self, *args):
        window = Window(self.app_context)
        self.app_context.windows.append(window)
        print("[GraphApp] Created new window: ", self.app_context.windows)

        

if __name__ == '__main__':
    app = GraphApp()

    app.run(sys.argv)