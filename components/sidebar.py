
from gi.repository import Gtk
from components.base import BoxBase

from components.panel import OrizontalSeparator
from widgets.file_selector import FileSelector
from widgets.folder_selector import FolderSelector
from widgets.column_selector import ColumnSelector

from utils.data_manager import DataManager
from utils.logger import get_logger

logger = get_logger(__name__)




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
        self.set_size_request(150, -1)

class LeftSidebar(SidebarBase):
    def __init__(self, window_context, app_context):
        super().__init__()
        # self.window_context = window_context
        self.label.set_label("Left Sidebar")
        # self.graph_area = context.graph_area

        self.data_manager = DataManager()
        window_context.data_manager = self.data_manager

        # Riga per contenere file e folder selection
        #self.file_folder_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.file_selector = FileSelector(
            parent_window=window_context.window,
            on_file_selected_callback=self.data_manager.set_file,
            settings_manager=app_context.settings_manager,
        )
        self.file_selector.settings_manager = app_context.settings_manager
        self.append(self.file_selector)

        # self.folder_selector = FolderSelector(
        #     parent_window=window_context.window,
        #     on_folder_selected_callback=self.data_manager.set_file
        # )
        # self.file_folder_selector.append(self.folder_selector)
        
        # self.append(self.file_folder_selector·)

        

        self.orizontal_separator1 = OrizontalSeparator()
        self.append(self.orizontal_separator1)

        self.column_selector = ColumnSelector()
        self.append(self.column_selector)
        # At first we hide the selector, will appear once a file is chosen
        self.column_selector.hide()

        # Passing the ColumnSelector to DataManager that populates it
        window_context.data_manager.set_column_selector(self.column_selector)
        window_context.data_manager.set_plot_manager(window_context.plot_manager)
        

    def on_working_directory_selected(self, folder_path):
        logger.info(f"Cartella di lavoro selezionata: {folder_path}")
        # Imposta la working directory nel file selector
        self.file_selector.set_working_directory(folder_path)
        # Salva nel settings manager
        self.window_context.settings_manager.set_working_directory(folder_path)
