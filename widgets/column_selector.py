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


    def create_rows(self, header):
        for col_name in header:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.set_hexpand(True)

            label = Gtk.Label(label=col_name)
            label.set_halign(Gtk.Align.START)
            label.set_xalign(0.0)
            row.append(label)

            # Checkbox per X
            checkbox_x = Gtk.CheckButton(label="X")
            checkbox_x.connect("toggled", self.on_checkbox_toggled, col_name, "X")
            row.append(checkbox_x)

            # Checkbox per Y
            checkbox_y = Gtk.CheckButton(label="Y")
            checkbox_y.connect("toggled", self.on_checkbox_toggled, col_name, "Y")
            row.append(checkbox_y)

            # Associo i due bottoni alla colonna
            row.checkbox_x = checkbox_x
            row.checkbox_y = checkbox_y

            self.selected_columns[col_name] = "Ignora"

            self.append(row)

    def on_checkbox_toggled(self, checkbox, col_name, axis_type):
        # Trova il row corrispondente
        for row in self:
            if isinstance(row, Gtk.Box) and any(child.get_label() == col_name for child in row):
                checkbox_x = row.checkbox_x
                checkbox_y = row.checkbox_y

                if axis_type == "X" and checkbox.get_active():
                    checkbox_y.set_active(False)
                    self.selected_columns[col_name] = "X"
                elif axis_type == "Y" and checkbox.get_active():
                    checkbox_x.set_active(False)
                    self.selected_columns[col_name] = "Y"
                elif not checkbox_x.get_active() and not checkbox_y.get_active():
                    self.selected_columns[col_name] = "Ignora"

                break

        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.get_selected_columns())

    def get_selected_columns(self):
        """
        Ritorna un dizionario delle colonne selezionate con asse associato.
        Solo colonne che sono assegnate ad X o Y.
        """
        return {col: axis for col, axis in self.selected_columns.items() if axis != "Ignora"}

    def update_columns(self, header):
        # Pulisce le vecchie righe (tranne il titolo)
        for child in list(self):
            if child != self.title:
                self.remove(child)

        self.selected_columns.clear()

        # Ricrea i nuovi elementi
        self.create_rows(header)

