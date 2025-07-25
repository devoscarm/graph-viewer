from gi.repository import Gtk

from components.base import BoxBase
from components.top_bar import TopBar
from components.panel import MainArea, GraphArea, OrizontalSeparator, VerticalSeparator
from components.sidebar import LeftSidebar, RightSidebar
from utils.plot_manager import PlotManager
from utils.context import WindowContext
from utils.logger import get_logger

logger = get_logger(__name__)



class Window(Gtk.ApplicationWindow):
    def __init__(self, app_context):
        super().__init__(application=app_context.app)
        self.app_context = app_context
        self.window_context = WindowContext(window=self)

        self.set_default_size(1000, 600)
        self.set_title('Nuova finestra')

        self.window_box = BoxBase()
        self.window_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_child(self.window_box)

        # Topbar has to know the window to close it!
        self.top_bar = TopBar(self.window_context.window)
        self.window_box.append(self.top_bar)

        self.orizontal_separator = OrizontalSeparator()
        self.window_box.append(self.orizontal_separator)

        # Nella top bar c'è un pulsante per creare nuove finestre, lo agganciamo qui
        self.top_bar.new_window_button.connect(
            'new-window-requested', 
            app_context.app.create_new_window
        )

        self.main_area = MainArea()
        self.window_box.append(self.main_area)

        self.graph_area = GraphArea()
        self.plot_manager = PlotManager(self.graph_area)
        self.window_context.plot_manager = self.plot_manager


        self.left_sidebar = LeftSidebar(
            self.window_context, 
            self.app_context
        )
        self.main_area.append(self.left_sidebar)

        self.vertical_separator = VerticalSeparator()
        self.main_area.append(self.vertical_separator)

        self.main_area.append(self.graph_area)
        
        self.vertical_separator1 = VerticalSeparator()
        self.main_area.append(self.vertical_separator1)


        self.right_sidebar = RightSidebar(
            window_context = self.window_context, 
            settings_manager = self.app_context.settings_manager,
        )
        self.main_area.append(self.right_sidebar)

        # Linking plot manager to right sidebar for plot settings
        self.plot_manager.on_subplot_selected_callback = self.right_sidebar.set_axes
        
        

        self.present()

        logger.info(f"Created new window")



    def set_square_plot():
        return