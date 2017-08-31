# class for loading a json file into memory
import json

PRIVATE_DATA_FILE = 'private_data.json'
private_data = None


def PrivateData(key):
    global private_data
    if not private_data:
        with open(PRIVATE_DATA_FILE) as f:
            private_data = json.load(f)
    return private_data.get(key) if key else private_data
