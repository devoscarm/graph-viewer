
import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from components.base import BoxBase
from utils.logger import get_logger

logger = get_logger(__name__)

class ColumnSelector(BoxBase):
    def __init__(self, on_selection_changed_callback=None):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.on_selection_changed_callback = on_selection_changed_callback
        self.selected_columns = {}  # blocco -> {colonna -> asse}

        # Interruttore per modalità uniforme
        self.uniform_switch = Gtk.Switch()
        self.uniform_switch.set_active(False)
        self.uniform_switch.connect("notify::active", self.on_uniform_mode_toggled)

        switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        switch_box.append(Gtk.Label(label="Uniform column"))
        switch_box.append(self.uniform_switch)
        self.append(switch_box)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.append(self.scrolled)

        self.block_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.scrolled.set_child(self.block_box)

        self.blocks = []

    def set_on_selection_changed_callback(self, callback):
        self.on_selection_changed_callback = callback

    def on_checkbox_toggled(self, checkbox, header, col_name, axis_type):
        is_active = checkbox.get_active()

        if self.uniform_switch.get_active():
            self._propagate_uniform_change(col_index=self._get_column_index(header, col_name),
                                        axis_type=axis_type,
                                        is_active=is_active)
        else:
            checkbox_x, checkbox_y = self._get_row_widgets(header, col_name)

            if axis_type == "X":
                if is_active:
                    checkbox_y.set_active(False)
                    self.selected_columns[header][col_name] = "X"
                else:
                    if not checkbox_y.get_active():
                        self.selected_columns[header][col_name] = "Ignore"
            elif axis_type == "Y":
                if is_active:
                    checkbox_x.set_active(False)
                    self.selected_columns[header][col_name] = "Y"
                else:
                    if not checkbox_x.get_active():
                        self.selected_columns[header][col_name] = "Ignore"

            if self.on_selection_changed_callback:
                self.on_selection_changed_callback(self.get_selected_columns())




    def _propagate_uniform_change(self, col_index, axis_type, is_active):
        if not self._all_blocks_have_same_length():
            logger.warning("Uniform selection skipped: structures differ.")
            return

        for block in self.blocks:
            block_key = block['key']
            col_names = list(block['rows'].keys())
            if col_index >= len(col_names):
                continue

            col_name = col_names[col_index]
            cbx, cby = block['rows'][col_name]

            # Blocca i segnali per evitare ricorsione
            cbx.handler_block_by_func(self.on_checkbox_toggled)
            cby.handler_block_by_func(self.on_checkbox_toggled)

            if axis_type == "X":
                cbx.set_active(is_active)
                cby.set_active(False)
                self.selected_columns[block_key][col_name] = "X" if is_active else "Ignore"
            elif axis_type == "Y":
                cby.set_active(is_active)
                cbx.set_active(False)
                self.selected_columns[block_key][col_name] = "Y" if is_active else "Ignore"

            cbx.handler_unblock_by_func(self.on_checkbox_toggled)
            cby.handler_unblock_by_func(self.on_checkbox_toggled)

        if self.on_selection_changed_callback:
            self.on_selection_changed_callback(self.get_selected_columns())



    def _get_column_index(self, header, col_name):
        for block in self.blocks:
            if block['key'] == header:
                try:
                    return list(block['rows'].keys()).index(col_name)
                except ValueError:
                    return -1
        return -1



    def get_selected_columns(self):
        return {
            block_key: {
                col: axis for col, axis in cols.items() if axis != "Ignore"
            }
            for block_key, cols in self.selected_columns.items()
        }

    def update_blocks(self, block_headers: dict):
        self.blocks.clear()
        self.selected_columns.clear()

        child = self.block_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.block_box.remove(child)
            child = next_child

        for index, (header, _) in enumerate(block_headers.items()):
            grid = Gtk.Grid(column_spacing=10, row_spacing=6)
            label = Gtk.Label(label=f"Block {index+1}")
            label.get_style_context().add_class("heading")
            grid.attach(label, 0, 0, 3, 1)

            grid.attach(Gtk.Label(label="X"), 0, 1, 1, 1)
            grid.attach(Gtk.Label(label="Y"), 1, 1, 1, 1)
            grid.attach(Gtk.Label(label="Column"), 2, 1, 1, 1)

            rows = {}
            for i, col_name in enumerate(header):
                checkbox_x = Gtk.CheckButton()
                checkbox_y = Gtk.CheckButton()
                label = Gtk.Label(label=col_name, halign=Gtk.Align.START)

                checkbox_x.connect("toggled", self.on_checkbox_toggled, header, col_name, "X")
                checkbox_y.connect("toggled", self.on_checkbox_toggled, header, col_name, "Y")

                grid.attach(checkbox_x, 0, i + 2, 1, 1)
                grid.attach(checkbox_y, 1, i + 2, 1, 1)
                grid.attach(label, 2, i + 2, 1, 1)

                rows[col_name] = (checkbox_x, checkbox_y)

            self.blocks.append({'key': header, 'rows': rows})
            self.selected_columns[header] = {}
            self.block_box.append(grid)
            grid.set_vexpand(True)

    def _get_row_widgets(self, block_key, col_name):
        for block in self.blocks:
            if block['key'] == block_key:
                return block['rows'][col_name]
        return None, None

    def _all_blocks_have_same_length(self):
        if len(self.blocks) < 2:
            return True
        first_len = len(self.blocks[0]['rows'])
        for block in self.blocks[1:]:
            if len(block['rows']) != first_len:
                return False
        return True

    def on_uniform_mode_toggled(self, switch, _):
        logger.debug(f"on_uniform_mode_toggled: {switch.get_active()}")
        if not switch.get_active():
            self.selected_columns = {k: {} for k in self.selected_columns.keys()}
            for block in self.blocks:
                for cbx, cby in block['rows'].values():
                    cbx.handler_block_by_func(self.on_checkbox_toggled)
                    cby.handler_block_by_func(self.on_checkbox_toggled)
                    cbx.set_active(False)
                    cby.set_active(False)
                    cbx.handler_unblock_by_func(self.on_checkbox_toggled)
                    cby.handler_unblock_by_func(self.on_checkbox_toggled)

            if self.on_selection_changed_callback:
                self.on_selection_changed_callback(self.get_selected_columns())
