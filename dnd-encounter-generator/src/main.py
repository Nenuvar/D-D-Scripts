# filepath: src/main.py
from encounter_generator import load_monsters  # Import the function to load monsters

def filter_monsters_by_cr(monsters, max_cr):
    """
    Filters the list of monsters based on the maximum Challenge Rating (CR).
    :param monsters: List of monster dictionaries.
    :param max_cr: Maximum CR for the encounter.
    :return: Filtered list of monsters.
    """
    filtered = []
    for monster in monsters:
        # Extract the CR value
        cr = monster.get("cr", "0")  # Default to "0" if "cr" is missing
        
        # Handle cases where CR is a dictionary
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")  # Extract the "cr" key from the dictionary
        
        # Convert CR to a float for comparison (e.g., "1/4" -> 0.25)
        try:
            cr_value = float(eval(cr)) if "/" in cr else float(cr)
            if cr_value <= max_cr:
                filtered.append(monster)
        except (ValueError, TypeError):
            continue  # Skip monsters with invalid CR values
    return filtered

from encounter_generator import load_monsters  # Import the function to load monsters

def filter_monsters_by_cr(monsters, max_cr):
    """
    Filters the list of monsters based on the maximum Challenge Rating (CR).
    :param monsters: List of monster dictionaries.
    :param max_cr: Maximum CR for the encounter.
    :return: Filtered list of monsters.
    """
    filtered = []
    for monster in monsters:
        # Extract the CR value
        cr = monster.get("cr", "0")  # Default to "0" if "cr" is missing
        
        # Handle cases where CR is a dictionary
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")  # Extract the "cr" key from the dictionary
        
        # Convert CR to a float for comparison (e.g., "1/4" -> 0.25)
        try:
            cr_value = float(eval(cr)) if "/" in cr else float(cr)
            if cr_value <= max_cr:
                filtered.append(monster)
        except (ValueError, TypeError):
            continue  # Skip monsters with invalid CR values
    return filtered

def main():
    # Load the monster data from the JSON file
    data = load_monsters('src/data/bestiary-mm.json')  # Adjust the path to your JSON file
    monsters = data["monster"]  # Access the list of monsters under the "monster" key

    # Ask the user about the difficulty of the encounter
    print("How hard will the encounter be?")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    print("4. Deadly")
    difficulty = input("Choose a difficulty (1-4): ")

    # Map difficulty to maximum CR (you can adjust these values as needed)
    difficulty_to_cr = {
        "1": 0.5,  # Easy: CR <= 0.5
        "2": 1,    # Medium: CR <= 1
        "3": 3,    # Hard: CR <= 3
        "4": 5     # Deadly: CR <= 5
    }

    max_cr = difficulty_to_cr.get(difficulty, 0.5)  # Default to Easy if input is invalid

    # Filter monsters based on the chosen difficulty
    filtered_monsters = filter_monsters_by_cr(monsters, max_cr)

    # Display the filtered monsters
    print("\nFiltered Monsters:")
    for monster in filtered_monsters:
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        print(f"- {name} (CR: {cr})")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
