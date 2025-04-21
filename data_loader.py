import json

def load_database(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_suppliers_and_buyer(database):
    suppliers = database.get("suppliers", [])
    buyers = database.get("buyers", [])
    return suppliers, buyers[0] if buyers else None