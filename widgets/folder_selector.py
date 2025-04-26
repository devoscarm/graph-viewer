from gi.repository import Gtk


# Proviamo a vedere se FileDialog esiste
HAS_FILE_DIALOG = hasattr(Gtk, 'FileDialog')

class FolderSelector(Gtk.Box):
    def __init__(self, parent_window, on_folder_selected_callback, title="Seleziona una cartella"):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.parent_window = parent_window
        self.on_folder_selected_callback = on_folder_selected_callback
        self.title = title

        self.select_button = Gtk.Button(label=self.title)
        self.select_button.connect("clicked", self.on_select_folder)
        self.append(self.select_button)

        self.folder_label = Gtk.Label(label="Nessuna cartella selezionata")
        self.append(self.folder_label)

    def on_select_folder(self, button):
        if HAS_FILE_DIALOG:
            print("Uso Gtk.FileDialog")
            self.select_with_file_dialog()
        else:
            print("Uso Gtk.FileChooserDialog (fallback)")
            self.select_with_file_chooser_dialog()


    def select_with_file_dialog(self):
        dialog = Gtk.FileDialog()
        dialog.set_title(self.title)
        dialog.set_modal(True)
        dialog.select_folder(self.parent_window, None, self.on_folder_chosen, None)

    def select_with_file_chooser_dialog(self):
        dialog = Gtk.FileChooserDialog(
            title=self.title,
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
                self.folder_label.set_label(folder_path)
                if self.on_folder_selected_callback:
                    self.on_folder_selected_callback(folder_path)
        dialog.destroy()

    def on_folder_chosen(self, dialog, result, user_data):
        try:
            folder = dialog.select_folder_finish(result)
            folder_path = folder.get_path()
            self.folder_label.set_label(folder_path)
            if self.on_folder_selected_callback:
                self.on_folder_selected_callback(folder_path)
        except Exception as e:
            print(f"Errore: {e}")
