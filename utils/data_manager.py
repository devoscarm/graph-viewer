from utils.logger import get_logger
import numpy as np

logger = get_logger(__name__)


class DataManager:
    def __init__(self):
        self.file_path = None
        self.header = ""            # Data file header
        self.data = []              # All file data
        self.fields = []            # Column name (field) chosen to be plot
        self.blocks = {}            # To stock {header: [data], } read from file
        self.column_selector = None # Sidebar widget for column selection
        self.plot_manager = None    # Manager of the final plot

    def set_file(self, file_path):
        """
        Carica il file e aggiorna header+data.
        """
        self.file_path = file_path
        self.parse_file(file_path)

        logger.info(f"File loaded > {file_path}")
        

        # When I load a file, if there is already a column_selector
        # (of previous file), we update the column_selector
        if self.column_selector:
            # self.column_selector.update_columns(self.fields)
            self.column_selector.update_blocks(self.blocks)
            self.column_selector.show()

        # Wiping previous plot as we changed file
        if self.plot_manager:
            self.plot_manager.plot_empty()


    def get_header(self):
        return self.header
    
    def print_data(self):
        for line in self.data:
            print(line)
        


    def set_column_selector(self, column_selector):
        """
        Connects the ColumnSelector
        """
        self.column_selector = column_selector
        self.column_selector.set_on_selection_changed_callback(self.on_columns_selected)

    def set_plot_manager(self, plot_manager):
        """
        Connects the PlotManager
        """
        self.plot_manager = plot_manager




    def on_columns_selected(self, selected_columns):
        """
        Richiamato quando l'utente cambia le colonne selezionate.
        """
        # logger.info(f"Columns selected: > {selected_columns}")
        # for key, values in selected_columns.items():
        #     print(key)
        #     for value, col in values.items():
        #         print(value, " > ", col)

        selected_data = self.select_columns(selected_columns)

        #print(selected_data)

        
        # Trasforma da dict con due liste → lista di tuple (x, y)
        data_per_block = {
            header: list(zip(x_vals, y_vals))
            for header, (x_vals, y_vals) in selected_data.items()
            if x_vals and y_vals
        }
        self.plot_manager.set_data(data_per_block)


    


    def on_columns_selected_new(self, selected_columns):
        selected_data = self.select_columns(selected_columns)
        for header, (x_data, y_data, x_name, y_name) in selected_data.items():
            self.plot_data(x_data, y_data, x_name, y_name, header)


    def select_columns(self, selected_columns):
        result = {}
        for header, col_selection in selected_columns.items():
            if header not in self.blocks:
                continue
            x_idx = y_idx = None
            x_name = y_name = None
            for col, axis in col_selection.items():
                if axis == "X":
                    x_name = col
                    x_idx = header.index(col)
                elif axis == "Y":
                    y_name = col
                    y_idx = header.index(col)
            if x_idx is not None and y_idx is not None:
                x_data = []
                y_data = []
                for row in self.blocks[header]:
                    try:
                        x_data.append(float(row[x_idx]))
                        y_data.append(float(row[y_idx]))
                    except Exception:
                        continue
                result[header] = (np.array(x_data), np.array(y_data), x_name, y_name)
        return result






    def select_columns_old(self, selected_columns):
        """
        Estrae le colonne selezionate da ogni blocco.
        Ritorna un dizionario: header → (X_data, Y_data)
        """

        data_per_block = {}
        for header, cols in selected_columns.items():

            if header not in self.blocks:
                continue
            rows = self.blocks[header]
            field_names = list(header)
            x_idx = y_idx = None
            for col_name, axis in cols.items():
                if col_name in field_names:
                    idx = field_names.index(col_name)
                    if axis == 'X':
                        x_idx = idx
                    elif axis == 'Y':
                        y_idx = idx

            if x_idx is not None and y_idx is not None:
                x_data = []
                y_data = []
                for row in rows:
                    try:
                        x_val = float(row[x_idx])
                        y_val = float(row[y_idx])
                        x_data.append(x_val)
                        y_data.append(y_val)
                    except ValueError:
                        continue
                data_per_block[header] = (x_data, y_data)

        return data_per_block    





   


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

    