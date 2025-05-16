import os
import random
from datetime import datetime
from encounter_generator import load_monsters  # Import the function to load monsters
import json

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

def get_monster_source(config_file):
    """
    Loads monster source from config or prompts the user and saves it.
    Returns the chosen monster source file path.
    """
    # Load config if exists
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    default_source = config.get("monster_source", "bestiary-mm.json")
    print(f"\nCurrent monster source: {default_source}")
    use_default = input("Use this monster source? (y/n): ").strip().lower()
    if use_default == "y":
        chosen_source = default_source
    else:
        chosen_source = input("Enter the monster source file (e.g., 'bestiary-mm.json'): ").strip()
        if not chosen_source:
            print("No input given. Using default.")
            chosen_source = default_source

    # Save to config
    config["monster_source"] = chosen_source
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return chosen_source

def get_party_info(config_file):
    """
    Loads party info from config or prompts the user and saves it.
    Returns (party_level, party_size).
    """
    # Load config if exists
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    party_info = config.get("party_info", {})
    party_level = party_info.get("level")
    party_size = party_info.get("size")

    print("\nParty info:")
    if party_level and party_size:
        print(f"Current: Level {party_level}, {party_size} adventurers")
        use_current = input("Use this party info? (y/n): ").strip().lower()
        if use_current == "y":
            return party_level, party_size

    # Prompt for new info
    while True:
        try:
            party_level = int(input("🎲 The party's level (1-20): "))
            party_size = int(input("🧙 Number of adventurers: "))
            break
        except ValueError:
            print("⚠️ Invalid input. Please enter numbers.")

    # Save to config
    config["party_info"] = {"level": party_level, "size": party_size}
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return party_level, party_size

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
    print("\n⚔️  Choose your battleground")
    environment_map = {str(i + 1): env for i, env in enumerate(sorted(all_environments))}
    for key, env in environment_map.items():
        print(f"{key}. {env.capitalize()}")
    print(f"{len(environment_map) + 1}. 🎲 Surprise me (Any)")

    # Get the user's choice
    environment_choice = input(f"Your choice (1-{len(environment_map) + 1}): ").strip()
    selected_environment = environment_map.get(environment_choice, "any")

    # Filter monsters based on the selected environment
    if selected_environment != "any":
        monsters = [
            monster for monster in monsters
            if selected_environment in monster.get("environment", [])
        ]

    if not monsters:
        print("😢 No monsters found for the chosen environment. The adventurers are safe... for now.")
        return []  # Return an empty encounter if no monsters match the environment

    # Step 2: Choose a main monster within 50%-90% of the max XP pool
    min_main_xp = int(max_xp * 0.5)
    max_main_xp = int(max_xp * 0.9)
    main_candidates = [
        monster for monster in monsters
        if min_main_xp <= CR_TO_XP.get(str(monster.get("cr", "0")), 0) <= max_main_xp
    ]

    if not main_candidates:
        print("🛑 No worthy main monster found within the XP range. The adventurers might get bored!")
        return []  # Return an empty encounter if no main monster is found

    # Select the first suitable main monster
    main_monster = main_candidates[0]
    encounter = [main_monster]
    main_monster_xp = CR_TO_XP.get(str(main_monster.get("cr", "0")), 0)
    remaining_xp = max_xp - main_monster_xp

    # Step 3: Announce the main monster
    print(f"\n 🐲  Your main monster is: {main_monster.get('name', 'Unknown')} (CR: {main_monster.get('cr', 'Unknown')}, XP: {main_monster_xp})")
    if remaining_xp <= 0:
        print("⚔️ The main monster is so powerful that there's no room for minions!")
        return encounter

    # Step 4: Ask if the user wants minions
    add_minions = input("🐭  Would you like to add some minions? (y/n): ").strip().lower()
    if add_minions != 'y':
        print("🛡️ No minions? A bold choice!")
        return encounter

    # Step 5: Add minions to fill the remaining XP
    print("\n🪄  Summoning minions to join the fray...")
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

    if minions:
        print(f" {len(minions)} minions have joined the encounter!")
    else:
        print("🤷 No suitable minions could be found. The main monster stands alone!")

    encounter.extend(minions)
    return encounter

def save_encounter_to_md(encounter, folder_path):
    """
    Save the generated encounter to a Markdown file.
    :param encounter: List of monsters in the encounter.
    :param folder_path: Path to the folder where the file should be saved.
    """
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Generate a random title for the encounter
    titles = [
        "The Lair of Shadows",
        "Ambush in the Misty Woods",
        "The Forgotten Crypt",
        "Battle at the Broken Bridge",
        "The Siege of Emberfall",
        "Chaos in the Crystal Cavern",
        "The Howling Plains Encounter",
        "The Curse of the Blood Moon",
        "The Wrath of the Ancient One",
        "The Final Stand at Dawn"
    ]
    encounter_title = random.choice(titles)

    # Use the title as the filename, replacing spaces with underscores
    file_name = f"{encounter_title.replace(' ', '_')}.md"
    file_path = os.path.join(folder_path, file_name)

    # Write the encounter to the Markdown file
    with open(file_path, "w") as file:
        file.write("### Monsters:\n")
        # Write the table header
        file.write("| Monster | CR | HP | Dead | Note |\n")
        file.write("|---------|----|----|------|------|\n")
        for monster in encounter:
            name = monster.get("name", "Unknown")
            cr = monster.get("cr", "Unknown")
            hp = monster.get("hp", {}).get("average", "Unknown")  # Extract the average HP if available
            obsidian_link = f"[[{name.lower().replace(' ', '-')}\\|{name}]]"
            file.write(f"| **{obsidian_link}** | {cr} | {hp} | [ ] |  |\n")
        file.write("\n---\n")

    print(f"\nEncounter saved to: {file_path}")

def get_save_folder_path():
    """
    Handles config file logic for saving folder paths.
    Returns the chosen folder path.
    """
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.json")

    # Load config or initialize
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    folder_paths = config.get("folder_paths", [])
    chosen_path = None

    if folder_paths:
        default_path = folder_paths[-1]
        print(f"\nDefault folder path: {default_path}")
        use_default = input("Use the default folder path? (y/n): ").strip().lower()
        if use_default == "y":
            chosen_path = default_path
        else:
            print("\nChoose an existing folder path or add a new one:")
            for idx, path in enumerate(folder_paths, 1):
                print(f"{idx}. {path}")
            print(f"{len(folder_paths)+1}. Add a new folder path")
            choice = input(f"Select an option (1-{len(folder_paths)+1}): ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(folder_paths):
                    chosen_path = folder_paths.pop(choice_num-1)
                    folder_paths.append(chosen_path)  # Make it default
                elif choice_num == len(folder_paths)+1:
                    chosen_path = input("Enter the new folder path (e.g., './encounters'): ").strip()
                    if chosen_path:
                        if chosen_path in folder_paths:
                            folder_paths.remove(chosen_path)
                        folder_paths.append(chosen_path)
            if not chosen_path:
                print("No valid selection made. Using default path.")
                chosen_path = default_path
    else:
        print("\nNo folder path or config found.")
        while not chosen_path:
            chosen_path = input("Enter the folder path (e.g., './encounters'): ").strip()
        folder_paths.append(chosen_path)

    # Save updated config
    config["folder_paths"] = folder_paths
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return chosen_path

def main():
    # Config file path (reuse from get_save_folder_path)
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.json")

    # Get party info (load or prompt)
    party_level, party_size = get_party_info(config_file)

    # Get monster source preference
    monster_source = get_monster_source(config_file)
    monster_source_path = os.path.join(os.path.dirname(__file__), "data", monster_source)

    # Load the monster data from the JSON file
    data = load_monsters(monster_source_path)
    monsters = data["monster"]

    # Calculate the party's XP thresholds
    thresholds = calculate_party_thresholds(party_level, party_size)

    # Ask the user about the difficulty of the encounter
    print("\n🔥 How challenging will this encounter be?")
    print("1. 🟢 Easy - Just a taste of danger")
    print("2. 🟡 Medium - A fair fight")
    print("3. 🔴 Hard - A true test of their mettle")
    print("4. ⚫ Deadly - A fight for survival")
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
    for i, monster in enumerate(encounter):
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        xp = CR_TO_XP.get(str(cr), 0)
        if i == 0:  # The first monster is the main monster
            print(f"- 🐲 {name} (CR: {cr}, XP: {xp})")
        else:  # The rest are minions
            print(f"- 🐭 {name} (CR: {cr}, XP: {xp})")
    
    # Determines the folder path to save the encounter
    print("\n💾 Saving the encounter...")
    folder_path = get_save_folder_path()
    save_encounter_to_md(encounter, folder_path)

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
