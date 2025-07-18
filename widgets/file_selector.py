import gi
from pathlib import Path

gi.require_version('Gtk', '4.0')
try:
    gi.require_version('Adw', '1')
except ValueError:
    pass  # Se Adw non è disponibile, ignora

from gi.repository import Gtk, Gio, GLib, Pango
from components.base import BoxBase, ButtonBase
from widgets.folder_selector import FolderSelector
from utils.logger import get_logger

logger = get_logger(__name__)

HAS_FILE_DIALOG = hasattr(Gtk, 'FileDialog')


class FileSelector(Gtk.Box):
    def __init__(self, 
            parent_window, 
            on_file_selected_callback=None, 
            settings_manager=None
        ):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.parent_window = parent_window
        self.settings_manager = settings_manager
        self.on_file_selected_callback = on_file_selected_callback

        # Loading default settings from config file
        self.plotting_directory = None
        self.file_path = None
        if self.settings_manager:
            self.plotting_directory = Path(self.settings_manager.get_plotting_directory())
            if self.settings_manager.get_last_file_opened():
                self.file_path = Path(self.settings_manager.get_last_file_opened())

        
        # Blocco selezione directory
        self.dir_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.append(self.dir_selector)

        self.folder_selector = FolderSelector(
            parent_window=self.parent_window,
            on_folder_selected_callback=self.save_plotting_directory
        )
        self.dir_selector.append(self.folder_selector)

        self.dir_label = Gtk.Label()
        self.dir_label.set_label(str(self.plotting_directory) if self.plotting_directory else "Chose a folder")
        self.dir_label.set_ellipsize(Pango.EllipsizeMode.START)
        self.dir_selector.append(self.dir_label)

        # Blocco selezione file
        self.file_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.append(self.file_selector)

        self.select_button = ButtonBase()
        icon = Gtk.Image.new_from_icon_name("document-open-symbolic")
        self.select_button.set_child(icon)
        self.select_button.connect("clicked", self.on_select_file)
        self.select_button.set_tooltip_text("Open a file")
        self.file_selector.append(self.select_button)

        self.file_name = Gtk.Label()
        self.file_name.set_markup("<i>No file selected</i>")
        self.file_selector.append(self.file_name)

        


    def on_select_file(self, button):
        """"
            Managing che GTK 4.12 + or - implementation of Dialog
        """

        if HAS_FILE_DIALOG:
            logger.info("Using Gtk.FileDialog (GTK 4.12+)")
            self.select_with_file_dialog()
        else:
            logger.info("Using Gtk.FileChooserDialog (legacy, GTK < 4.12)")
            self.select_with_file_chooser_dialog()


    def on_file_selected(self):
        """
            Calling the callback function
        """

        logger.info(f"Selected file: {self.file_path}")
        self.file_name.set_label(self.file_path.name)
        if self.on_file_selected_callback:
            self.on_file_selected_callback(str(self.file_path))  # keep str if callback expects it
        self.save_last_file_opened()


    def save_last_file_opened(self):
        """
            Saving "last file opened" on file
        """

        # logger.info(f"Saving 'last file opened' on file > {self.file_path}")
        self.settings_manager.set_last_file_opened(str(self.file_path))


    def save_plotting_directory(self, folder_path):
        """
            Callback function for saving the plotting directory on file
        """

        logger.info(f"Saved plotting directory > {folder_path}")
        self.plotting_directory = folder_path
        self.dir_label.set_label(folder_path)

        if self.settings_manager:
            self.settings_manager.set_plotting_directory(folder_path)

    





# Implementation in new Gtk (4.12+)

    def select_with_file_dialog(self):
        """
            Implementation in new Gtk (4.12+)
        """

        dialog = Gtk.FileDialog()
        dialog.set_modal(True)
        dialog.set_title("Select a file")
        dialog.open(self.parent_window, None, self.on_file_chosen_dialog, None)

    def on_file_chosen_dialog(self, dialog, result, user_data):
        """
            Implementation in new Gtk (4.12+)
        """

        try:
            file = dialog.open_finish(result)
            self.file_path = Path(file.get_path())
            self.on_file_selected()
        except GLib.Error as e:
            logger.error(f"Error opening file: {e}")



# Legacy Gtk implementation (4.12-)

    def select_with_file_chooser_dialog(self):
        """
            Legacy Gtk implementation (4.12-)
        """

        dialog = Gtk.FileChooserDialog(
            title="Select a file",
            transient_for=self.parent_window,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT)
        dialog.connect("response", self.on_file_chooser_response)

        if self.plotting_directory:
            gio_file = Gio.File.new_for_path(str(self.plotting_directory))
            dialog.set_current_folder(gio_file)

        dialog.show()

    def on_file_chooser_response(self, dialog, response_id):
        """
            Legacy Gtk implementation (4.12-)
        """

        try:
            if response_id == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                if file:
                    self.file_path = Path(file.get_path())
                    self.on_file_selected()
            dialog.destroy()
        except Exception as e:
            logger.error(f"Error opening file: {e}")

