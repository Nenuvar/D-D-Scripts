# filepath: src/main.py
import random
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
        cr = monster.get("cr", "0")  # Default to "0" if "cr" is missing
        
        # Handle cases where CR is a dictionary
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")  # Extract the "cr" key from the dictionary
        
        # Get XP value for the monster's CR
        xp = CR_TO_XP.get(str(cr), 0)  # Ensure CR is a string before lookup
        if xp <= max_xp:
            filtered.append(monster)
    return filtered

def generate_encounter(monsters, max_xp):
    """
    Generate an encounter by selecting a main monster that fits between 70%-80% of the max XP pool
    and optionally adding minions with the remaining XP.
    :param monsters: List of filtered monsters.
    :param max_xp: Maximum XP for the encounter.
    :return: List of monsters in the encounter.
    """
    # Shuffle the monsters list to ensure randomness
    random.shuffle(monsters)

    # Step 1: Determine all possible environments from the monsters list
    all_environments = set()
    for monster in monsters:
        environments = monster.get("environment", [])
        if isinstance(environments, list):
            all_environments.update(environments)

    # Display the environments to the user
    print("\nSelect the environment for the encounter:")
    environment_map = {str(i + 1): env for i, env in enumerate(sorted(all_environments))}
    for key, env in environment_map.items():
        print(f"{key}. {env.capitalize()}")
    print(f"{len(environment_map) + 1}. Any")

    # Get the user's choice
    environment_choice = input(f"Choose an environment (1-{len(environment_map) + 1}): ").strip()
    selected_environment = environment_map.get(environment_choice, "any")

    # Filter monsters based on the selected environment
    if selected_environment != "any":
        monsters = [
            monster for monster in monsters
            if selected_environment in monster.get("environment", [])
        ]

    if not monsters:
        print("No monsters found for the selected environment.")
        return []  # Return an empty encounter if no monsters match the environment

    # Step 2: Choose a main monster within 50%-90% of the max XP pool
    min_main_xp = int(max_xp * 0.5)
    max_main_xp = int(max_xp * 0.9)
    main_candidates = [
        monster for monster in monsters
        if min_main_xp <= CR_TO_XP.get(str(monster.get("cr", "0")), 0) <= max_main_xp
    ]

    if not main_candidates:
        print("No suitable main monster found within the desired XP range.")
        return []  # Return an empty encounter if no main monster is found

    # Select the first suitable main monster
    main_monster = main_candidates[0]
    encounter = [main_monster]
    main_monster_xp = CR_TO_XP.get(str(main_monster.get("cr", "0")), 0)
    remaining_xp = max_xp - main_monster_xp

    # Step 3: Ask if the user wants minions
    print(f"\nMain monster selected: {main_monster.get('name', 'Unknown')} (CR: {main_monster.get('cr', 'Unknown')}, XP: {main_monster_xp})")
    if remaining_xp <= 0:
        print("No XP left for minions.")
        return encounter

    add_minions = input("Do you want to add minions? (y/n): ").strip().lower()
    if add_minions != 'y':
        return encounter

    # Step 4: Add minions to fill the remaining XP
    minions = []
    for monster in monsters:
        if monster == main_monster:
            continue  # Skip the main monster
        cr = monster.get("cr", "0")
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")
        xp = CR_TO_XP.get(str(cr), 0)

        if xp <= remaining_xp:
            minions.append(monster)
            remaining_xp -= xp

        if len(minions) >= 3 or remaining_xp <= 0:  # Limit to 1-3 minions
            break

    encounter.extend(minions)
    return encounter

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

    # Generate a single encounter
    encounter = generate_encounter(filtered_monsters, max_xp)

    # Display the encounter
    print("\nGenerated Encounter:")
    for monster in encounter:
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        xp = CR_TO_XP.get(str(cr), 0)
        print(f"- {name} (CR: {cr}, XP: {xp})")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
