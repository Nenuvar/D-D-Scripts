# filepath: src/encounter_generator.py
import json  # This is a built-in Python library for working with JSON files.

def load_monsters(file_path):
    """
    Loads monster data from a JSON file.
    :param file_path: Path to the JSON file.
    :return: A list of monsters.
    """
    with open(file_path, 'r') as file:  # Open the file in read mode.
        return json.load(file)  # Parse the JSON data and return it.
