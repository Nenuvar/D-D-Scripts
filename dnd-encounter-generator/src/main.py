# filepath: src/main.py
from encounter_generator import load_monsters  # Import the function to load monsters

# XP thresholds per character level (DMG pg. 82)
XP_THRESHOLDS = {
    1: [25, 50, 75, 100],
    2: [50, 100, 150, 200],
    3: [75, 150, 225, 400],
    4: [125, 250, 375, 500],
    5: [250, 500, 750, 1100],
    # Add more levels as needed
}

# CR-to-XP mapping (DMG pg. 274)
CR_TO_XP = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100,
    "1": 200, "2": 450, "3": 700, "4": 1100,
    "5": 1800, "6": 2300, "7": 2900, "8": 3900,
    "9": 5000, "10": 5900, "11": 7200, "12": 8400,
    "13": 10000, "14": 11500, "15": 13000, "16": 15000,
    "17": 18000, "18": 20000, "19": 22000, "20": 25000,
    "21": 33000, "22": 41000, "23": 50000, "24": 62000,
    "25": 75000, "26": 90000, "27": 105000, "28": 120000,
    "29": 135000, "30": 155000
}

# Monster multiplier table (DMG pg. 82)
MONSTER_MULTIPLIERS = {
    1: 1,
    2: 1.5,
    3: 2,
    7: 2.5,
    11: 3,
    15: 4
}

def get_monster_multiplier(num_monsters):
    """
    Get the XP multiplier based on the number of monsters.
    :param num_monsters: Number of monsters in the encounter.
    :return: XP multiplier.
    """
    for threshold, multiplier in sorted(MONSTER_MULTIPLIERS.items(), reverse=True):
        if num_monsters >= threshold:
            return multiplier
    return 1  # Default multiplier for 1 monster

def calculate_party_thresholds(party_level, party_size):
    """
    Calculate the XP thresholds for the party based on their level and size.
    :param party_level: Level of the party members.
    :param party_size: Number of party members.
    :return: A dictionary with XP thresholds for each difficulty.
    """
    thresholds = XP_THRESHOLDS.get(party_level, [0, 0, 0, 0])  # Default to 0 if level is not in the table
    return {
        "easy": thresholds[0] * party_size,
        "medium": thresholds[1] * party_size,
        "hard": thresholds[2] * party_size,
        "deadly": thresholds[3] * party_size
    }

def filter_monsters_by_xp(monsters, max_xp):
    """
    Filter monsters whose XP value is less than or equal to the max XP.
    :param monsters: List of monster dictionaries.
    :param max_xp: Maximum XP for the encounter.
    :return: Filtered list of monsters.
    """
    filtered = []
    for monster in monsters:
        cr = monster.get("cr", "0")
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")
        xp = CR_TO_XP.get(cr, 0)  # Get XP value for the monster's CR
        if xp <= max_xp:
            filtered.append(monster)
    return filtered

def main():
    # Load the monster data from the JSON file
    data = load_monsters('//svgkomm.svgdrift.no/Users/sk5049835/Documents/Notater/Scripts/learn_python/dnd-encounter-generator/src/data/bestiary-mm.json')  # Adjust the path to your JSON file
    monsters = data["monster"]  # Access the list of monsters under the "monster" key

    # Ask the user for the party's level and size
    try:
        party_level = int(input("Enter the party's level: "))
        party_size = int(input("Enter the party's size: "))
    except ValueError:
        print("Invalid input. Defaulting to level 1 and size 4.")
        party_level = 1
        party_size = 4

    # Calculate the party's XP thresholds
    thresholds = calculate_party_thresholds(party_level, party_size)

    # Ask the user about the difficulty of the encounter
    print("How hard will the encounter be?")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    print("4. Deadly")
    difficulty = input("Choose a difficulty (1-4): ")

    # Get the XP threshold for the chosen difficulty
    difficulty_to_key = {"1": "easy", "2": "medium", "3": "hard", "4": "deadly"}
    max_xp = thresholds.get(difficulty_to_key.get(difficulty, "easy"), thresholds["easy"])

    # Filter monsters based on the XP threshold
    filtered_monsters = filter_monsters_by_xp(monsters, max_xp)

    # Display the filtered monsters
    print("\nFiltered Monsters:")
    for monster in filtered_monsters:
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        xp = CR_TO_XP.get(cr, 0)
        print(f"- {name} (CR: {cr}, XP: {xp})")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
