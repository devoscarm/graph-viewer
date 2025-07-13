from gi.repository import Gtk
from utils.logger import get_logger
from components.base import ButtonBase

logger = get_logger(__name__)


# Proviamo a vedere se FileDialog esiste
HAS_FILE_DIALOG = hasattr(Gtk, 'FileDialog')

class FolderSelector(Gtk.Box):
    def __init__(
            self, 
            parent_window, 
            on_folder_selected_callback=None, 
        ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.parent_window = parent_window
        self.on_folder_selected_callback = on_folder_selected_callback

        self.select_button = ButtonBase()
        icon = Gtk.Image.new_from_icon_name("document-open-symbolic")
        self.select_button.set_child(icon)
        #self.select_button = Gtk.Button(label=self.title)
        self.select_button.connect("clicked", self.on_select_folder)
        self.append(self.select_button)

        self.set_tooltip_text("Choose a folder")

        #self.folder_label = Gtk.Label(label="No")
        #self.append(self.folder_label)

    def on_select_folder(self, button):
        #logger.debug("Qua faccio la scelta del FileDialog")

        if HAS_FILE_DIALOG:
            logger.info("Using Gtk.FileDialog (modern, gtk 4.12+)")
            self.select_with_file_dialog()
        else:
            logger.info("Using Gtk.FileChooserDialog (legacy, gtk 4.12-)")
            self.select_with_file_chooser_dialog()

    # GTK > 4.12
    def select_with_file_dialog(self):
        dialog = Gtk.FileDialog()
        dialog.set_title("Select a folder")
        dialog.set_modal(True)
        dialog.select_folder(self.parent_window, None, self.on_folder_chosen, None)

    def on_folder_chosen(self, dialog, result, user_data):
        try:
            folder = dialog.select_folder_finish(result)
            folder_path = folder.get_path()
            self.folder_label.set_label(folder_path)
            #self.set_tooltip_text(folder_path)
            if self.on_folder_selected_callback:
                self.on_folder_selected_callback(folder_path)
        except Exception as e:
            logger.error(f"Aiuto! errore > {e}")


    # GTK < 4.12
    def select_with_file_chooser_dialog(self):
        dialog = Gtk.FileChooserDialog(
            title="Select a folder",
            transient_for=self.parent_window,
            modal=True,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(
            "_Annulla", Gtk.ResponseType.CANCEL,
            "_Seleziona", Gtk.ResponseType.ACCEPT
        )
        # Connetti il segnale di risposta
        dialog.connect("response", self.on_folder_chooser_response)
        dialog.show()
    #    response = dialog.run()
    #    if response == Gtk.ResponseType.ACCEPT:
            # folder_path = dialog.get_file().get_path()
            # self.folder_label.set_label(folder_path)
            # if self.on_folder_selected_callback:
                # self.on_folder_selected_callback(folder_path)
        # dialog.destroy()

    def on_folder_chooser_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                folder_path = file.get_path()
                #self.set_tooltip_text(folder_path)
                #self.folder_label.set_label(folder_path)
                if self.on_folder_selected_callback:
                    self.on_folder_selected_callback(folder_path)
        dialog.destroy()

    
