from utils.logger import get_logger
import numpy as np

logger = get_logger(__name__)


class DataManager:
    def __init__(self):
        self.file_path = None
        self.blocks = {}
        self.column_selector = None
        self.plot_manager = None
        self.current_curves = set()

# In the future, will update Str to Path
    def set_file(self, file_path: str):
        self.file_path = file_path
        self.parse_file(file_path)

        if self.column_selector:
            self.column_selector.update_blocks(self.blocks)
            self.column_selector.show()

        if self.plot_manager:
            self.plot_manager.clear_all_curves()

        self.current_curves.clear()

    def set_column_selector(self, column_selector):
        self.column_selector = column_selector
        self.column_selector.set_on_selection_changed_callback(self.on_columns_selected)

    def set_plot_manager(self, plot_manager):
        self.plot_manager = plot_manager

    def on_columns_selected(self, selected_columns):
        new_curves = set()
        data_to_add = {}

        for header, col_map in selected_columns.items():
            rows = self.blocks.get(header, [])
            field_names = list(header)

            x_names = [col for col, axis in col_map.items() if axis == "X"]
            y_names = [col for col, axis in col_map.items() if axis == "Y"]

            for x_name in x_names:
                if x_name not in field_names:
                    continue
                x_idx = field_names.index(x_name)
                x_vals = [float(r[x_idx]) for r in rows if self.is_float(r[x_idx])]

                for y_name in y_names:
                    if y_name not in field_names:
                        continue
                    y_idx = field_names.index(y_name)
                    y_vals = [float(r[y_idx]) for r in rows if self.is_float(r[y_idx])]
                    if len(x_vals) != len(y_vals):
                        continue
                    curve_id = (header, x_name, y_name)
                    new_curves.add(curve_id)
                    data_to_add[curve_id] = (x_vals, y_vals)

        # Rimuovi curve non più selezionate
        for curve_id in self.current_curves - new_curves:
            block_id, x_name, y_name = curve_id
            self.plot_manager.remove_curve(block_id, x_name, y_name)

        # Aggiungi nuove curve
        for curve_id in new_curves - self.current_curves:
            block_id, x_name, y_name = curve_id
            x_vals, y_vals = data_to_add[curve_id]
            self.plot_manager.add_curve(block_id, x_name, y_name, x_vals, y_vals, subplot_id="default")

        self.current_curves = new_curves


   


    def parse_file(self, file_path):
        """
        Parse a file con potenziali blocchi multipli (ognuno con una propria intestazione).
        """
        separators = [',', '\t', ' ']
        blocks = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]

            
            current_header = None
            separator = None

            for line in lines:
                if separator is None:

                    # potenziale bug!!! questo a ogni giro prova ad interpretare
                    # il separatore! va bene questa cosa o è controproducente?
                    separator = self.guess_separator(line, separators)

                parts = line.split(separator)

                if all(not self.is_float(p) for p in parts):
                    # Linea di intestazione
                    current_header = tuple(parts)
                    blocks[current_header] = []
                else:
                    # Linea di dati
                    float_row = [float(p) if self.is_float(p) else None for p in parts]
                    if current_header is not None:
                        blocks[current_header].append(float_row)

            self.blocks = blocks

        except Exception as e:
            logger.error(f"Error parsing file: {e}")


    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False



    def guess_separator(self, line, separators=None):
        """
        Indovina il separatore più probabile.
        """
        #separators = [',', '\t', ' ']
        best_separator = ' '
        best_count = 0
        for sep in separators:
            count = line.count(sep)
            if count > best_count:
                best_separator = sep
                best_count = count
        return best_separator

    