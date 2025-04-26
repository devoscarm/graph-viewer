import gi
from gi.repository import Gtk



class BoxBase(Gtk.Box):
    def __init__(self):
    # def __init__(self, on_new_window_callback):

        super().__init__()
        self.label = Gtk.Label(label="Base Box")
        self.append(self.label)
        self.label.set_visible(False)

        # self.set_vexpand(False)
        # self.set_hexpand(False)

        # Children separation
        self.set_spacing(6)

        # Margin around the box
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(6)
        self.set_margin_end(6)


class ButtonBase(Gtk.Button):
    def __init__(self):
        super().__init__()
        self.set_margin_top(4)
        self.set_margin_bottom(4)
        self.set_margin_start(4)
        self.set_margin_end(4)



class FrameBase(Gtk.Frame):
    def __init__(self):
        super().__init__()
        self.set_margin_top(10)
        self.set_margin_bottom(10)
        self.set_margin_start(5)
        self.set_margin_end(5)
        self.set_label_align(0.5)
