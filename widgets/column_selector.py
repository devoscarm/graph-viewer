import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from components.base import BoxBase

class ColumnSelector(BoxBase):
    def __init__(self, on_selection_changed_callback=None):
        super().__init__()
        self.set_orientation=Gtk.Orientation.VERTICAL
        self.on_selection_changed_callback = on_selection_changed_callback
        self.selected_columns = {}  # nome_colonna -> asse (X/Y/None)

        # Grid for data list and selection
        self.grid = Gtk.Grid(column_spacing=10, row_spacing=6)
        self.append(self.grid)

        # Table header
        header_x = Gtk.Label(label='X', halign=Gtk.Align.CENTER)
        header_y = Gtk.Label(label='Y', halign=Gtk.Align.CENTER)
        header_col = Gtk.Label(label='Select data', halign=Gtk.Align.START)

        self.grid.attach(header_x, 0, 1, 1 ,1)
        self.grid.attach(header_y, 1, 1, 1 ,1)
        self.grid.attach(header_col, 2, 1, 1 ,1)

        
    # Callback function for udating selectable columns
    def set_on_selection_changed_callback(self, callback):
        self.on_selection_changed_callback = callback


    def create_rows(self, header):
        '''
        Populates rows of data bin and axis selection
        '''
        self.rows = {}
        for idx, col_name in enumerate(header):
            
            # Apparently the first 2, are header lines
            row_idx = idx + 2

            checkbox_x = Gtk.CheckButton()
            checkbox_y = Gtk.CheckButton()
            label = Gtk.Label(label=col_name, halign=Gtk.Align.START)

            checkbox_x.connect('toggled', self.on_checkbox_toggled, col_name, 'X')
            checkbox_y.connect('toggled', self.on_checkbox_toggled, col_name, 'Y')

            self.grid.attach(checkbox_x, 0, row_idx, 1, 1)
            self.grid.attach(checkbox_y, 1, row_idx, 1, 1)
            self.grid.attach(label, 2, row_idx, 1, 1)
            

            self.rows[col_name] = (checkbox_x, checkbox_y)


    def on_checkbox_toggled(self, checkbox, col_name, axis_type):
        '''
        Alternate the choice of X or Y display of the data bin
        Somehow notify of choices updates
        '''
        # Scompatto la t-upla
        checkbox_x, checkbox_y = self.rows[col_name]
        
        if axis_type == "X" and checkbox.get_active():
            checkbox_y.set_active(False)
            self.selected_columns[col_name] = "X"
        elif axis_type == "Y" and checkbox.get_active():
            checkbox_x.set_active(False)
            self.selected_columns[col_name] = "Y"
        elif not checkbox_x.get_active() and not checkbox_y.get_active():
            self.selected_columns[col_name] = "Ignora"        

        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.get_selected_columns())


    def get_selected_columns(self):
        """
        Ritorna un dizionario delle colonne selezionate con asse associato.
        Solo colonne che sono assegnate ad X o Y.
        """
        return {col: axis for col, axis in self.selected_columns.items() if axis != "Ignora"}


    def update_columns(self, header):
        '''
        To be called when a different file is selected
        '''
        # Rimuove tutti i figli tranne le prime tre intestazioni
        child = self.grid.get_first_child()
        count = 0
        while child:
            next_child = child.get_next_sibling()
            if count >= 3:
                self.grid.remove(child)
            count += 1
            child = next_child

        self.selected_columns.clear()

        self.create_rows(header)