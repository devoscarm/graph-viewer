from gi.repository import Gtk
from components.base import BoxBase

class OrizontalSeparator(Gtk.Separator):
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)

class VerticalSeparator(Gtk.Separator):
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

class MainArea(BoxBase):
    '''Orizontal'''
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.HORIZONTAL)


class GraphArea(BoxBase):
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_size_request(200, 200)





