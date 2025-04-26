class DataManager:
    def __init__(self):
        self.file_path = None
        self.header = []
        self.data = []
        self.column_selector = None
        self.plot_manager = None

    def set_file(self, file_path):
        """
        Carica il file e aggiorna header+data.
        """
        self.file_path = file_path
        self.header, self.data = self.parse_file(file_path)

        print(f"[DataManager] File caricato: {file_path}")
        print(f"[DataManager] Header: {self.header}")

        if self.column_selector:
            self.column_selector.update_columns(self.header)
            self.column_selector.show()


    def get_header(self):
        return self.header


    def set_column_selector(self, column_selector):
        """
        Connetti il ColumnSelector.
        """
        self.column_selector = column_selector
        self.column_selector.set_on_selection_changed_callback(self.on_columns_selected)

    def set_plot_manager(self, plot_manager):
        """
        Connetti il PlotManager.
        """
        self.plot_manager = plot_manager

    def on_columns_selected(self, selected_columns):
        """
        Richiamato quando l'utente cambia le colonne selezionate.
        """
        print(f"[DataManager] Colonne selezionate: {selected_columns}")
        self.plot(selected_columns)

    def plot(self, selected_columns=None):
        """
        Plotta i dati selezionati.
        """
        if not self.data or not self.plot_manager:
            print("[DataManager] Plot non eseguito: dati o plot manager mancante.")
            return

        if selected_columns is None and self.column_selector:
            selected_columns = self.column_selector.get_selected_columns()

        if not selected_columns:
            print("[DataManager] Nessuna colonna selezionata.")
            return

        self.plot_manager.set_data(self.header, self.data)
        self.plot_manager.set_selected_columns(selected_columns)
        self.plot_manager.plot()



    def parse_file(self, file_path):
        """
        Parsea file CSV/TXT e restituisce header + dati.
        """
        header = []
        data = []
        separators = [',', '\t', ' ']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                separator = self.guess_separator(first_line, separators)
                header = first_line.split(separator)

                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    row = line.split(separator)
                    data.append(row)

        except Exception as e:
            print(f"[DataManager] Errore parsing file: {e}")

        return header, data

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