import json
import os

def save_data_to_file(document_key, data):
    filename = f"{document_key}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_data_from_file(document_key):
    filename = f"{document_key}.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return None