import gi
import os

gi.require_version('Gtk', '4.0')
try:
    gi.require_version('Adw', '1')
except ValueError:
    pass  # Se Adw non c'è, non esplodere

from gi.repository import Gtk, Gio, GLib
from components.base import BoxBase, ButtonBase

# Verifica se Gtk.FileDialog è disponibile (GTK 4.12+)
HAS_FILE_DIALOG = hasattr(Gtk, 'FileDialog')


class FileSelector(Gtk.Box):
    def __init__(self, parent_window, on_file_selected_callback):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.parent_window = parent_window

        # Function to be executed
        self.on_file_selected_callback = on_file_selected_callback
        
        self.title = Gtk.Label()
        self.title.set_markup("<b>Data to plot</b>")
        self.title.set_halign(Gtk.Align.START)
        self.append(self.title)

        # Horizontal box for choosing a file
        self.file_selector = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.append(self.file_selector)
        
        # Chose a file label
        self.label = Gtk.Label()
        self.label.set_markup("<i>Chose a file</i>")
        self.file_selector.append(self.label)

        # Select file button
        self.select_button = ButtonBase()
        icon = Gtk.Image.new_from_icon_name("document-open-symbolic")
        self.select_button.set_child(icon)
        self.select_button.connect("clicked", self.on_select_file)
        self.file_selector.append(self.select_button)

        # Chosen file label
        self.file_label = Gtk.Label(label="No file selected")
        self.file_label.set_halign(Gtk.Align.START)
        self.append(self.file_label)

    # Gestione delle diverse implementazioni tra GTK 4.12+
    def on_select_file(self, button):
        if HAS_FILE_DIALOG:
            print("Using Gtk.FileDialog (modern, gtk 4.12+)")
            self.select_with_file_dialog()
        else:
            print("Using Gtk.FileChooserDialog (legacy, gtk 4.12-)")
            self.select_with_file_chooser_dialog()

    # Implementation in new Gtk
    def select_with_file_dialog(self):
        dialog = Gtk.FileDialog()
        dialog.set_modal(True)
        dialog.set_title(self.title)
        dialog.open(self.parent_window, None, self.on_file_chosen, None)

    def on_file_chosen(self, dialog, result, user_data):
        try:
            file = dialog.open_finish(result)
            file_path = file.get_path()
            self.file_label.set_label(file_path)
            if self.on_file_selected_callback:
                self.on_file_selected_callback(file_path)
        except GLib.Error as e:
            print(f"Errore nella selezione file: {e.message}")

    # Legacy Gtk implementation
    def select_with_file_chooser_dialog(self):
        dialog = Gtk.FileChooserDialog(
            title=self.title,
            transient_for=self.parent_window,
            modal=True,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Open", Gtk.ResponseType.ACCEPT
        )
        dialog.connect("response", self.on_file_chooser_response)
        dialog.show()

    def on_file_chooser_response(self, dialog, response_id):
        if response_id == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            if file:
                file_path = file.get_path()
                file_name = os.path.basename(file_path)
                self.file_label.set_label(file_name)
                self.file_label.set_tooltip_text(file_path)
                if self.on_file_selected_callback:
                    self.on_file_selected_callback(file_path)
        dialog.destroy()
