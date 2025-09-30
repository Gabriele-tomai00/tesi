import json
import os

# Percorso del file JSON
filename = 'response_grid/resp.json'

# Verifica che il file esista
if not os.path.exists(filename):
    print(f"Il file '{filename}' non è stato trovato.")
else:
    # Carica il contenuto del file JSON
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Estrai curricula_course e file_timestamp
    curricula_course = data.get('curricula_course')
    file_timestamp = str(data.get('file_timestamp'))  # Convertito in stringa

    print(f"curricula_course: {curricula_course}")
    print(f"file_timestamp: {file_timestamp}")

    # Cerca l'elemento con timestamp corrispondente
    matched = None
    for entry in data.get('date_inizio_fine_curriculum', []):
        timestamp_value = entry.get('timestamp', {}).get('0')
        if str(timestamp_value) == file_timestamp:
            matched = entry
            break

    # Stampa l'elemento corrispondente
    if matched:
        date_info = matched.get('date', {}).get('1', {})
        print("\nElemento corrispondente:")
        print(f"  AnnoCorso: {date_info.get('AnnoCorso')}")
        print(f"  DataInizio: {date_info.get('DataInizio')}")
        print(f"  DataFine: {date_info.get('DataFine')}")
    else:
        print("\nNessun elemento con timestamp corrispondente trovato.")
