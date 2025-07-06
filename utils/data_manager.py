


class DataManager:
    def __init__(self):
        self.file_path = None
        self.header = ""            # Data file header
        self.data = []              # All file data
        self.fields = []            # Column name (field) chosen to be plot
        self.dataset =[]            # Column to be plot
        self.column_selector = None # Sidebar widget for column selection
        self.plot_manager = None    # Manager of the final plot

    def set_file(self, file_path):
        """
        Carica il file e aggiorna header+data.
        """
        self.file_path = file_path
        self.parse_file(file_path)

        print(f"[DataManager] File caricato: {file_path}")
        print(f"[DataManager] Header: {self.header}")

        if self.column_selector:
            self.column_selector.update_columns(self.fields)
            self.column_selector.show()


    def get_header(self):
        return self.header


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
        print(f"[DataManager] Colonne selezionate: {selected_columns}")
        self.select_columns()
        self.plot_manager.set_data(self.header, self.data)

    def select_columns(self):
        '''
        Extracts the desired columns from the entire dataset
        '''
        print(f"[DataManager] All files: ")
        for idx, data_row in enumerate(self.data):
            print(f"{idx} - {data_row}")


    def parse_file(self, file_path):
        """
        Parse a file CSV/TXT and updates the attributes
        for header, fields and data
        """

        separators = [',', '\t', ' ']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.header = f.readline().strip()
                separator = self.guess_separator(self.header, separators)
                self.fields = self.header.split(separator)

                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = line.split(separator)
                    self.data.append(row)

        except Exception as e:
            print(f"[DataManager] Errore parsing file: {e}")


    def guess_separator(self, line, separators):
        """
        Indovina il separatore più probabile.
        """
        best_separator = ' '
        best_count = 0
        for sep in separators:
            count = line.count(sep)
            if count > best_count:
                best_separator = sep
                best_count = count
        return best_separator

    def convert_data_to_numbers(self):
        """
        Converte ogni valore nei dati da stringa a float se possibile.
        Se la conversione fallisce, lascia la stringa originale.
        """
        converted_data = []

        for row in self.data:
            new_row = []
            for value in row:
                try:
                    new_row.append(float(value))
                except ValueError:
                    new_row.append(value)  # Mantieni stringa se non è numero
            converted_data.append(new_row)

        self.data = converted_data