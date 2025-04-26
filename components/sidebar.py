
from gi.repository import Gtk
from components.base import BoxBase



class SidebarBase(BoxBase):
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)
        self.set_size_request(200, -1)

class LeftSidebar(SidebarBase):
    def __init__(self):
        super().__init__()
        self.label.set_label("Left Sidebar")


class RightSidebar(SidebarBase):
    def __init__(self):
        super().__init__()
        self.label.set_label("Right Sidebar")