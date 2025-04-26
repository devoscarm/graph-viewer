import csv

def parse_file(file_path):
    """
    Legge un file CSV-like.
    Restituisce (header, data):
      - header: lista dei nomi delle colonne
      - data: lista di righe (ognuna lista di stringhe)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Prima riga: intestazioni
            data = list(reader)    # Righe successive: dati

        return header, data
    except Exception as e:
        print(f"Errore nella lettura del file: {e}")
        return [], []
