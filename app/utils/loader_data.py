import json
import os

def load_products():
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'vehicles_data.json')
    with open(file_path, "r") as f:
        return json.load(f)