
from gi.repository import Gtk
from components.base import BoxBase, FrameBase

from components.panel import GraphArea, OrizontalSeparator
from widgets.file_selector import FileSelector
from widgets.column_selector import ColumnSelector

from utils.parse_file import parse_file
from utils.data_manager import DataManager





class SidebarBase(BoxBase):
    def __init__(self):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_vexpand(True)
        self.set_size_request(200, -1)

class RightSidebar(SidebarBase):
    def __init__(self):
        super().__init__()
        self.label.set_label("Right Sidebar")

class LeftSidebar(SidebarBase):
    def __init__(self, context):
        super().__init__()
        self.label.set_label("Left Sidebar")
        self.graph_area = context.graph_area

        self.data_manager = DataManager()
        context.data_manager = self.data_manager

        self.file_selector = FileSelector(
            parent_window=context.window,
            on_file_selected_callback=self.data_manager.set_file
        )
        self.append(self.file_selector)

        self.orizontal_separator1 = OrizontalSeparator()
        self.append(self.orizontal_separator1)

        self.column_selector = ColumnSelector()
        self.append(self.column_selector)
        # At first we hide the selector, will appear once a file is chosen
        self.column_selector.hide()

        context.data_manager.set_column_selector(self.column_selector)
        
