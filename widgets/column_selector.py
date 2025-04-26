import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

class ColumnSelector(Gtk.Box):
    def __init__(self, on_selection_changed_callback=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        print("DENTRO A COLUMN SELECTOR")
        self.on_selection_changed_callback = on_selection_changed_callback
        self.selected_columns = {}  # nome_colonna -> asse (X/Y/None)

        # Titolo
        self.title = Gtk.Label(label="Select plot columns")
        self.title.set_halign(Gtk.Align.START)
        self.title.set_xalign(0.0)
        self.append(self.title)

        
    # Callback function for udating selectable columns
    def set_on_selection_changed_callback(self, callback):
        self.on_selection_changed_callback = callback

    def on_checkbox_toggled(self, checkbox, col_name):
        active = checkbox.get_active()
        old_axis = self.selected_columns[col_name][1]
        self.selected_columns[col_name] = (active, old_axis)
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.selected_columns)

    def on_axis_changed(self, combo, col_name):
        axis = combo.get_active_text()
        old_active = self.selected_columns[col_name][0]
        self.selected_columns[col_name] = (old_active, axis)
        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.selected_columns)

    def get_selected_columns(self):
        """
        Ritorna dizionario delle colonne selezionate con asse associato.
        """
        return {col: axis for col, (active, axis) in self.selected_columns.items() if active and axis != "Ignora"}


    def update_columns(self, header):
        # Prima svuoto tutto tranne il titolo
        for child in list(self):
            if child != self.title:
                self.remove(child)

        self.selected_columns = {}

        for col_name in header:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.set_hexpand(True)

            checkbox = Gtk.CheckButton(label=col_name)
            checkbox.set_halign(Gtk.Align.START)
            checkbox.connect("toggled", self.on_checkbox_toggled, col_name)
            row.append(checkbox)

            axis_selector = Gtk.ComboBoxText()
            axis_selector.append_text("Ignora")
            axis_selector.append_text("Asse X")
            axis_selector.append_text("Asse Y")
            axis_selector.set_active(0)
            axis_selector.connect("changed", self.on_axis_changed, col_name)
            row.append(axis_selector)

            self.append(row)

            self.selected_columns[col_name] = (False, "Ignora")