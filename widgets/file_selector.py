import gi
import os

gi.require_version('Gtk', '4.0')
try:
    gi.require_version('Adw', '1')
except ValueError:
    pass  # Se Adw non c'è, non esplodere

from gi.repository import Gtk, Gio, GLib
from components.base import BoxBase, ButtonBase
from widgets.folder_selector import FolderSelector
from utils.logger import get_logger

logger = get_logger(__name__)

# Verifica se Gtk.FileDialog è disponibile (GTK 4.12+)
HAS_FILE_DIALOG = hasattr(Gtk, 'FileDialog')


class FileSelector(Gtk.Box):
    def __init__(
            self, 
            parent_window, 
            on_file_selected_callback=None, 
            settings_manager=None,
        ):
        super().__init__()

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.parent_window = parent_window
        self.settings_manager = settings_manager

        self.plotting_directory = self.settings_manager.get_plotting_directory()

        # Function to be executed
        self.on_file_selected_callback = on_file_selected_callback

        # Horizontal box for choosing a plotting directory and title
        self.dir_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.append(self.dir_selector)

        # Directory selector button
        self.folder_selector = FolderSelector(
            parent_window=self.parent_window,
            on_folder_selected_callback=self.set_plotting_directory
        )
        self.dir_selector.append(self.folder_selector) 

        # Title of the plotting section
        self.dir_label = Gtk.Label()
        #self.title.set_markup("Chose a folder")
        #self.title.set_halign(Gtk.Align.START)
        self.dir_selector.append(self.dir_label)

        if hasattr(self, "settings_manager"):
            self.dir_label.set_label(self.settings_manager.get_plotting_directory())
        else:
            self.dir_label.set_label("Chose a folder")


        # Horizontal box for choosing a file
        self.file_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.append(self.file_selector)

        # Select file button
        self.select_button = ButtonBase()
        icon = Gtk.Image.new_from_icon_name("document-open-symbolic")
        self.select_button.set_child(icon)
        self.select_button.connect("clicked", self.on_select_file)
        self.select_button.set_tooltip_text("Open a file")
        self.file_selector.append(self.select_button)

        # Chose a file label
        self.file_label = Gtk.Label()
        self.file_label.set_markup("<i>No file selected</i>")
        self.file_selector.append(self.file_label)





    # Gestione delle diverse implementazioni tra GTK 4.12+
    def on_select_file(self, button):
        if HAS_FILE_DIALOG:
            logger.info("Using Gtk.FileDialog (modern, gtk 4.12+)")
            self.select_with_file_dialog()
        else:
            logger.info("Using Gtk.FileChooserDialog (legacy, gtk 4.12-)")
            self.select_with_file_chooser_dialog()



    # Implementation in new Gtk (4.12+)
    def select_with_file_dialog(self):
        dialog = Gtk.FileDialog()
        dialog.set_modal(True)
        dialog.set_title("Select a file")
        dialog.open(self.parent_window, None, self.on_file_chosen, None)

    def on_file_chosen(self, dialog, result, user_data):
        try:
            file = dialog.open_finish(result)
            file_path = file.get_path()
            self.file_label.set_label(file_path)
            if self.on_file_selected_callback:
                self.on_file_selected_callback(file_path)
        except GLib.Error as e:
            logger.error(f"Erro in the file section > {e.message}")




    # Legacy Gtk implementation (4.12-)
    def select_with_file_chooser_dialog(self):
        dialog = Gtk.FileChooserDialog(
            title="Select a file",
            transient_for=self.parent_window,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT
        )
        dialog.connect("response", self.on_file_chooser_response)

        if hasattr(self, "plotting_directory") and self.plotting_directory:
            gio_file = Gio.File.new_for_path(self.plotting_directory)
            dialog.set_current_folder(gio_file)

        dialog.show()

    def on_file_chooser_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                file_path = file.get_path()
                file_name = os.path.basename(file_path)
                #self.file_label.set_label(file_name)

                self.file_label.set_label(file_name)

                #self.file_label.set_tooltip_text(file_path)
                if self.on_file_selected_callback:
                    self.on_file_selected_callback(file_path)
        dialog.destroy()





    def set_plotting_directory(self, folder_path):
        logger.info(f"Plotting directory set to > {folder_path}")
        self.plotting_directory = folder_path
        self.dir_label.set_label(folder_path)

        if hasattr(self, "settings_manager"):
            self.settings_manager.set_plotting_directory(folder_path)
        
