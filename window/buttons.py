import gi
from gi.repository import Gtk

class ButtonBase(Gtk.Button):
    def __init__(self):
        super().__init__()
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(6)
        self.set_margin_end(6)