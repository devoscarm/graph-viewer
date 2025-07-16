
from gi.repository import Gtk, GObject
from components.base import BoxBase

from components.panel import OrizontalSeparator
from widgets.file_selector import FileSelector
from widgets.column_selector import ColumnSelector
from widgets.plot_saver import PlotSaver

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
    def __init__(self, window_context):
        super().__init__()
        self.label.set_label("Right Sidebar")
        self.set_size_request(150, -1)

        # self.window_context = window_context

        self.axes = None  # sarà impostato da plot_manager

        self.grid_checkbox = Gtk.CheckButton(label="Show grid")
        self.grid_checkbox.connect("toggled", self.on_grid_toggled)
        self.append(self.grid_checkbox)

        self.legend_checkbox = Gtk.CheckButton(label="Show legend")
        self.legend_checkbox.connect("toggled", self.on_legend_toggled)
        self.append(self.legend_checkbox)

        
        # Is activated every change, every character modified
        # self.title_entry.connect("changed", self.on_title_changed)
        # Event emitted pressing "Enter"
        # self.title_entry.connect("activate", self.on_title_changed)

        # Qua bisogna ottimizzare in modo da aggiornare il grafico quando
        # il focus esce dall'input box... ma ero stanco e ci capivo poco

        # controller = Gtk.EventControllerFocus()
        # controller.connect("leave", lambda ctrl: self.on_title_changed(self.title_entry, None))
        # self.title_entry.add_controller(controller)
        

        # Event emitted leaving the input box
        # self.title_entry.connect_after("focus-out-event", self.on_title_changed)
        
        self.title_entry = Gtk.Entry(placeholder_text="Title")
        self.title_entry.connect("changed", self.on_title_changed)
        self.append(self.title_entry)

        self.xlabel_entry = Gtk.Entry(placeholder_text="X label")
        self.xlabel_entry.connect("changed", self.on_xlabel_changed)
        self.append(self.xlabel_entry)

        self.ylabel_entry = Gtk.Entry(placeholder_text="Y label")
        self.ylabel_entry.connect("changed", self.on_ylabel_changed)
        self.append(self.ylabel_entry)


        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        self.plot_saver = PlotSaver(window_context)
        self.append(self.plot_saver)
    
    # We set settings state on the real state on the plot
    def set_axes(self, axes):
        self.axes = axes
        # self.grid_checkbox.set_active(axes.xaxis._gridOnMajor) # deprecated
        self.grid_checkbox.set_active(any(line.get_visible() for line in axes.get_xgridlines() + axes.get_ygridlines()))
        # self.legend_checkbox.set_active(bool(axes.get_legend()))
        legend = axes.get_legend()
        self.legend_checkbox.set_active(legend is not None and legend.get_visible())

        self.title_entry.set_text(axes.get_title())
        self.xlabel_entry.set_text(axes.get_xlabel())
        self.ylabel_entry.set_text(axes.get_ylabel())

    def on_grid_toggled(self, button):
        if self.axes:
            self.axes.grid(button.get_active())
            self.axes.figure.canvas.draw_idle()

    def on_legend_toggled(self, button):
        if self.axes:
            if button.get_active():
                self.axes.legend()
            else:
                leg = self.axes.get_legend()
                if leg:
                    leg.remove()
            self.axes.figure.canvas.draw_idle()

    def on_title_changed(self, entry):
        if self.axes:
            self.axes.set_title(entry.get_text())
            self.axes.figure.canvas.draw_idle()

    def on_xlabel_changed(self, entry):
        if self.axes:
            self.axes.set_xlabel(entry.get_text())
            self.axes.figure.canvas.draw_idle()

    def on_ylabel_changed(self, entry):
        if self.axes:
            self.axes.set_ylabel(entry.get_text())
            self.axes.figure.canvas.draw_idle()




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
