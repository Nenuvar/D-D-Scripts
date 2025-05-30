# filepath: src/main.py
# This only works with the v2_ai_client.py file in /archive/ai_client/
import os
import random
from datetime import datetime
from encounter_generator import load_monsters  # Import the function to load monsters
import json
import sys
import re
from ai_client import generate_environment_description
from dotenv import load_dotenv
load_dotenv()

# XP thresholds per character level (DMG pg. 82)
XP_THRESHOLDS = {
    1: [25, 50, 75, 100], 
    2: [50, 100, 150, 200],
    3: [75, 150, 225, 400],
    4: [125, 250, 375, 500],
    5: [250, 500, 750, 1100],
    6: [300, 600, 900, 1400],
    7: [350, 750, 1100, 1700],
    8: [450, 900, 1400, 2100],
    9: [550, 1100, 1600, 2400],
    10: [600, 1200, 1900, 2800],
    11: [800, 1600, 2400, 3600],
    12: [1000, 2000, 3000, 4500],
    13: [1100, 2200, 3400, 5100],
    14: [1250, 2500, 3800, 5700],
    15: [1400, 2800, 4300, 6400],
    16: [1600, 3200, 4800, 7200],
    17: [2000, 3900, 5900, 8800],
    18: [2100, 4200, 6300, 9500],
    19: [2400, 4900, 7300, 10900],
    20: [2800, 5700, 8500, 12700]
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

def get_monster_source(config_file, edit_mode=False):
    """
    Loads monster source from config or prompts the user and saves it.
    Returns the chosen monster source file path.
    """
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    default_source = config.get("monster_source", "bestiary-mm.json")
    if not edit_mode and "monster_source" in config:
        print(f"\nMonster source: {default_source}")
        return default_source

    # In edit mode, always prompt for new source
    print(f"\nCurrent monster source: {default_source}")
    chosen_source = input("Enter a new monster source file (e.g., 'bestiary-mm.json'): ").strip()
    if not chosen_source:
        print("No input given. Using default.")
        chosen_source = default_source

    config["monster_source"] = chosen_source
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return chosen_source

def get_party_info(config_file, edit_mode=False):
    """
    Loads party info from config or prompts the user and saves it.
    Returns (party_level, party_size).
    """
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    party_info = config.get("party_info", {})
    party_level = party_info.get("level")
    party_size = party_info.get("size")
    party_name = party_info.get("name")
    adventurers = party_info.get("adventurers")

    if not edit_mode and party_level and party_size and party_name and adventurers:
        print(f"\nParty: {party_name}")
        print(f"  Number of adventurers: {party_size}")
        print(f"  Level: {party_level}")
        for i, adv in enumerate(adventurers, 1):
            print(f"    Adventurer {i}: {adv['race']} {adv['class']} | Interest: {adv['interest']} | Fear: {adv['fear']}")
        return party_level, party_size

    # In edit mode, always prompt for new info
    print("\nEnter new party info:")
    while True:
        try:
            party_size = int(input("🧙 Number of adventurers: "))
            party_level = int(input("🎲 The party's level (1-20): "))
            break
        except ValueError:
            print("⚠️ Invalid input. Please enter numbers.")

    adventurers = []
    for i in range(1, party_size + 1):
        print(f"\nAdventurer {i}:")
        name = input("  Name: ").strip()
        race = input("  Race: ").strip()
        adv_class = input("  Class: ").strip()
        interest = input("  Main interest: ").strip()
        fear = input("  Biggest fear: ").strip()
        adventurers.append({
            "name": name,
            "race": race,
            "class": adv_class,
            "interest": interest,
            "fear": fear
        })
    party_name = input("\nParty name: ").strip()
    config["party_info"] = {
        "level": party_level,
        "size": party_size,
        "name": party_name,
        "adventurers": adventurers
    }
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return party_level, party_size

def interactive_input(prompt, config_file=None):
    """
    Enhanced input function that allows the user to enter flags (-p, -m, -f, -e, --help)
    at any prompt to edit config or get help, then returns to the original prompt or signals a section restart.
    Returns:
        - user input string if normal input
        - '_RESTART_SECTION_' if a config edit or help was performed
    """
    while True:
        user_input = input(prompt)
        if user_input.strip() in ("-p", "--party") and config_file:
            get_party_info(config_file, edit_mode=True)
            return "_RESTART_SECTION_"
        elif user_input.strip() in ("-m", "--monster") and config_file:
            get_monster_source(config_file, edit_mode=True)
            return "_RESTART_SECTION_"
        elif user_input.strip() in ("-f", "--folder") and config_file:
            get_save_folder_path(edit_mode=True)
            return "_RESTART_SECTION_"
        elif user_input.strip() in ("-e", "--edit") and config_file:
            while True:
                print("\nEdit Menu:")
                print("1. Party info")
                print("2. Monster source")
                print("3. Save folder path")
                print("a. Edit all above")
                print("x. Exit menu")
                choice = input("Choose an option (1, 2, 3, a, x): ").strip().lower()
                if choice == "1":
                    get_party_info(config_file, edit_mode=True)
                elif choice == "2":
                    get_monster_source(config_file, edit_mode=True)
                elif choice == "3":
                    get_save_folder_path(edit_mode=True)
                elif choice == "a":
                    get_party_info(config_file, edit_mode=True)
                    get_monster_source(config_file, edit_mode=True)
                    get_save_folder_path(edit_mode=True)
                elif choice == "x":
                    break
                else:
                    print("Invalid option. Please try again.")
            return "_RESTART_SECTION_"
        elif user_input.strip() in ("--print-party", "-pp") and config_file:
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
            party_info = config.get("party_info", {})
            if not party_info:
                print("No party info saved.")
            else:
                print(f"\nParty: {party_info.get('name', '[Unnamed Party]')}")
                print(f"  Number of adventurers: {party_info.get('size', '?')}")
                print(f"  Level: {party_info.get('level', '?')}")
                adventurers = party_info.get("adventurers", [])
                for i, adv in enumerate(adventurers, 1):
                    print(f"    Adventurer {i}: {adv.get('name', '[No Name]')} | {adv.get('race', '?')} {adv.get('class', '?')} | Interest: {adv.get('interest', '?')} | Fear: {adv.get('fear', '?')}")
            return "_RESTART_SECTION_"
        elif user_input.strip() == "--help":
            print_help()
            return "_RESTART_SECTION_"
        elif user_input.strip() == "":
            # If the user just presses Enter (empty input), check if prompt is the initial prompt
            # If so, and --help was just shown, restart the section
            # This is handled by returning "_RESTART_SECTION_" after --help above
            return user_input
        else:
            return user_input

def generate_encounter(monsters, max_xp, config_file=None):
    """
    Generate an encounter by selecting a main monster that fits between 50%-90% of the max XP pool
    and optionally adding minions with the remaining XP.
    :param monsters: List of filtered monsters.
    :param max_xp: Maximum XP for the encounter.
    :param config_file: Path to config file for interactive_input.
    :return: List of monsters in the encounter, environment description.
    """
    random.shuffle(monsters)
    environment_description = ""
    selected_environment = "any"

    # Step 1: Determine all possible environments from the monsters list
    while True:
        all_environments = set()
        for monster in monsters:
            environments = monster.get("environment", [])
            if isinstance(environments, list):
                all_environments.update(environments)
        print("\n⚔️  Choose your battleground")
        environment_map = {str(i + 1): env for i, env in enumerate(sorted(all_environments))}
        for key, env in environment_map.items():
            print(f"{key}. {env.capitalize()}")
        print(f"{len(environment_map) + 1}. 🎲 Surprise me (Any)")
        environment_choice = interactive_input(f"Your choice (1-{len(environment_map) + 1}): ", config_file).strip()
        if environment_choice == "_RESTART_SECTION_":
            continue
        if environment_choice in environment_map or environment_choice == str(len(environment_map) + 1):
            break
        print("Invalid choice. Please try again.")

    # Handle 'Surprise me' option
    if environment_choice == str(len(environment_map) + 1):
        if environment_map:
            selected_environment = random.choice(list(environment_map.values()))
            print(f"🎲 Surprise! The environment chosen is: {selected_environment.capitalize()}")
        else:
            selected_environment = "any"
    else:
        selected_environment = environment_map.get(environment_choice, "any")

    # Filter monsters based on the selected environment
    if selected_environment != "any":
        monsters = [
            monster for monster in monsters
            if selected_environment in monster.get("environment", [])
        ]

    if not monsters:
        print("😢 No monsters found for the chosen environment. The adventurers are safe... for now.")
        # Generate environment description if not 'any'
        if selected_environment != "any":
            print("\n🌎 Generating a description for this environment...")
            env_desc_input = {
                "name": selected_environment,
                "main_monster": main_monster.get("name", "unknown creature"),
                "minions": [m.get("name", "unknown minion") for m in minions] if 'minions' in locals() and minions else []
            }
            environment_description = generate_environment_description(env_desc_input)
            print(f"\n📜 Environment Description:\n{environment_description}\n")
        return [], environment_description

    # Step 2: Choose a main monster within 50%-90% of the max XP pool
    min_main_xp = int(max_xp * 0.5)
    max_main_xp = int(max_xp * 0.9)
    main_candidates = [
        monster for monster in monsters
        if min_main_xp <= CR_TO_XP.get(str(monster.get("cr", "0")), 0) <= max_main_xp
    ]

    if not main_candidates:
        print("🛑 No worthy main monster found within the XP range. The adventurers might get bored!")
        if selected_environment != "any":
            print("\n🌎 Generating a description for this environment...")
            env_desc_input = {
                "name": selected_environment,
                "main_monster": main_monster.get("name", "unknown creature"),
                "minions": [m.get("name", "unknown minion") for m in minions] if 'minions' in locals() and minions else []
            }
            environment_description = generate_environment_description(env_desc_input)
            print(f"\n📜 Environment Description:\n{environment_description}\n")
        return [], environment_description

    # Select the first suitable main monster
    main_monster = main_candidates[0]
    encounter = [main_monster]
    main_monster_xp = CR_TO_XP.get(str(main_monster.get("cr", "0")), 0)
    remaining_xp = max_xp - main_monster_xp

    print(f"\n 🐲  Your main monster is: {main_monster.get('name', 'Unknown')} (CR: {main_monster.get('cr', 'Unknown')}, XP: {main_monster_xp})")
    if remaining_xp <= 0:
        print("⚔️ The main monster is so powerful that there's no room for minions!")
        if selected_environment != "any":
            print("\n🌎 Generating a description for this environment...")
            env_desc_input = {
                "name": selected_environment,
                "main_monster": main_monster.get("name", "unknown creature"),
                "minions": [m.get("name", "unknown minion") for m in minions] if 'minions' in locals() and minions else []
            }
            environment_description = generate_environment_description(env_desc_input)
            print(f"\n📜 Environment Description:\n{environment_description}\n")
        return encounter, environment_description

    # Step 4: Ask if the user wants minions
    while True:
        add_minions = interactive_input("🐭  Would you like to add some minions? (y/n): ", config_file).strip().lower()
        if add_minions == "_RESTART_SECTION_":
            print(f"\n 🐲  Your main monster is: {main_monster.get('name', 'Unknown')} (CR: {main_monster.get('cr', 'Unknown')}, XP: {main_monster_xp})")
            continue
        if add_minions in ("y", "n"):
            break
        print("Please enter 'y' or 'n'.")

    if add_minions != 'y':
        print("🛡️ No minions? A bold choice!")
        if selected_environment != "any":
            print("\n🌎 Generating a description for this environment...")
            env_desc_input = {
                "name": selected_environment,
                "main_monster": main_monster.get("name", "unknown creature"),
                "minions": [m.get("name", "unknown minion") for m in minions] if 'minions' in locals() and minions else []
            }
            environment_description = generate_environment_description(env_desc_input)
            print(f"\n📜 Environment Description:\n{environment_description}\n")
        return encounter, environment_description

    # Step 5: Add minions to fill the remaining XP
    print("\n🪄  Summoning minions to join the fray...")
    minions = []
    for monster in monsters:
        if monster == main_monster:
            continue
        cr = monster.get("cr", "0")
        if isinstance(cr, dict):
            cr = cr.get("cr", "0")
        xp = CR_TO_XP.get(str(cr), 0)
        if xp <= remaining_xp:
            minions.append(monster)
            remaining_xp -= xp
        if len(minions) >= 3 or remaining_xp <= 0:
            break

    if minions:
        print(f" {len(minions)} minions have joined the encounter!")
    else:
        print("🤷 No suitable minions could be found. The main monster stands alone!")

    encounter.extend(minions)

    # --- AI Environment Description ---
    if selected_environment != "any":
        print("\n🌎 Generating a description for this environment...")
        env_desc_input = {
            "name": selected_environment,
            "main_monster": main_monster.get("name", "unknown creature"),
            "minions": [m.get("name", "unknown minion") for m in minions] if 'minions' in locals() and minions else []
            }
        environment_description = generate_environment_description(env_desc_input)
        print(f"\n📜 Environment Description:\n{environment_description}\n")
    # --- End AI Environment Description ---

    return encounter, environment_description

def save_encounter_to_md(encounter, folder_path, environment_description=""):
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
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(f"# {encounter_title}\n\n")
        if environment_description:
            file.write(f"## Environment Description\n\n{environment_description}\n\n")
        file.write("### Monsters:\n")
        # Write the table header
        file.write("| Monster | CR | HP | Dead | Note |\n")
        file.write("|---------|----|----|------|------|\n")
        for monster in encounter:
            name = monster.get("name", "Unknown")
            cr = monster.get("cr", "Unknown")
            hp = monster.get("hp", {}).get("average", "Unknown")
            link_name = re.sub(r"[()]", "", name)
            link_name = re.sub(r"\s+", " ", link_name)
            link_name = link_name.strip().lower().replace(" ", "-")
            obsidian_link = f"[[{link_name}\\|{name}]]"
            file.write(f"| {obsidian_link} | {cr} | {hp} | [ ] |  |\n")
        file.write("\n---\n")

    print(f"\nEncounter saved to: {file_path}")

def get_save_folder_path(edit_mode=False):
    """
    Handles config file logic for saving folder paths.
    Returns the chosen folder path.
    If edit_mode is True, prompts user to enter a new path directly.
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

    if edit_mode:
        # Show current default path
        current_path = folder_paths[-1] if folder_paths else None
        print("\nCurrent save folder:")
        print(f"  {current_path if current_path else '[None set]'}")
        while True:
            new_path = input("Enter the new folder path (e.g., './encounters'): ").strip()
            if new_path:
                if new_path in folder_paths:
                    folder_paths.remove(new_path)
                folder_paths.append(new_path)
                chosen_path = new_path
                print(f"New default save folder set: {chosen_path}")
                break
            else:
                print("Please enter a valid, non-empty folder path.")
    elif folder_paths:
        # Auto-select the default (last) path
        chosen_path = folder_paths[-1]
        print(f"\nUsing default folder path: {chosen_path}")
    else:
        # No folder paths at all, prompt for one
        while not chosen_path:
            chosen_path = input("Enter the folder path (e.g., './encounters'): ").strip()
        folder_paths.append(chosen_path)

    # Save updated config
    config["folder_paths"] = folder_paths
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    return chosen_path

def print_help():
    print("""
D&D 5e Encounter Builder - Quick Help
-------------------------------------
Generate and save random D&D 5e encounters based on your party and preferences.

How to Use:
- Press [Enter] to start with your saved setup, or enter new info if none is saved.
- At any prompt, type a flag to edit settings or get help:
    --help      Show this help message
    -p, --party    Edit party info (level, size)
    -m, --monster  Edit monster source file
    -f, --folder   Edit save folder path
    -e, --edit     Open the full edit menu

Workflow:
1. Review or edit your party, monster source, and save folder.
2. Choose encounter difficulty (Easy, Medium, Hard, Deadly).
3. Pick an environment or let the tool surprise you.
4. A main monster is selected; add minions if you wish.
5. Encounter is saved as a Markdown file in your chosen folder.

Tips:
- You can use flags at any prompt to change settings on the fly.
- All settings are saved in src/config/config.json for next time.
- To reset, delete the config file.

""")

def main():
    config_dir = os.path.join(os.path.dirname(__file__), "config")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.json")

    print("Welcome to the Encounter Builder! ⚔️")
    while True:
        user_input = interactive_input("Press [Enter] to start, or type --help for options: ", config_file).strip().lower()
        if user_input == "--help":
            print_help()
            continue  # Prompt again after showing help
        if user_input in ("-f", "--folder"):
            get_save_folder_path(edit_mode=True)
            return
        if user_input in ("-p", "--party"):
            get_party_info(config_file, edit_mode=True)
            return
        if user_input in ("-m", "--monster"):
            get_monster_source(config_file, edit_mode=True)
            return
        if user_input in ("-e", "--edit"):
            while True:
                print("\nEdit Menu:")
                print("1. Party info")
                print("2. Monster source")
                print("3. Save folder path")
                print("a. Edit all above")
                print("x. Exit menu")
                choice = input("Choose an option (1, 2, 3, a, x): ").strip().lower()
                if choice == "1":
                    get_party_info(config_file, edit_mode=True)
                elif choice == "2":
                    get_monster_source(config_file, edit_mode=True)
                elif choice == "3":
                    get_save_folder_path(edit_mode=True)
                elif choice == "a":
                    get_party_info(config_file, edit_mode=True)
                    get_monster_source(config_file, edit_mode=True)
                    get_save_folder_path(edit_mode=True)
                elif choice == "x":
                    break
                else:
                    print("Invalid option. Please try again.")
            return
        if user_input in ("--print-party", "-pp"):
            # Print current party info and exit
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                config = {}
            party_info = config.get("party_info", {})
            if not party_info:
                print("No party info saved.")
            else:
                print(f"\nParty: {party_info.get('name', '[Unnamed Party]')}")
                print(f"  Number of adventurers: {party_info.get('size', '?')}")
                print(f"  Level: {party_info.get('level', '?')}")
                adventurers = party_info.get("adventurers", [])
                for i, adv in enumerate(adventurers, 1):
                    print(f"    Adventurer {i}: {adv.get('name', '[No Name]')} | {adv.get('race', '?')} {adv.get('class', '?')} | Interest: {adv.get('interest', '?')} | Fear: {adv.get('fear', '?')}")
            print(f"\nPress [Enter] to continue...", end="")
            input()  # Wait for user to press Enter
            continue  # Reprint the prompt and context after printing party info
        break  # Exit the loop if no special command was entered

    # Try to load config info
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {}

    party_info = config.get("party_info", {})
    monster_source = config.get("monster_source")
    folder_paths = config.get("folder_paths", [])

    has_saved_info = party_info and monster_source and folder_paths

    if has_saved_info:
        print("\n🎲 Loading your adventure setup from the config file...")
        print (f"🧙 Party: {party_info.get('name', '[Unnamed Party]')}")
        print(f"📚 Monster source: {monster_source}")
        print(f"💾 Save folder: {folder_paths[-1] if folder_paths else '?'}")
        # Remove the prompt and always use the saved info as default
        party_level = party_info.get("level")
        party_size = party_info.get("size")
        folder_path = folder_paths[-1]
    else:
        # No saved info, prompt for everything
        party_level, party_size = get_party_info(config_file)
        monster_source = get_monster_source(config_file)
        folder_path = get_save_folder_path()

    monster_source_path = os.path.join(os.path.dirname(__file__), "data", monster_source)
    data = load_monsters(monster_source_path)
    monsters = data["monster"]

    thresholds = calculate_party_thresholds(party_level, party_size)

    # Difficulty selection section with restart support
    while True:
        print("\n🔥 How challenging will this encounter be?")
        print("1. 🟢 Easy - Just a taste of danger")
        print("2. 🟡 Medium - A fair fight")
        print("3. 🔴 Hard - A true test of their mettle")
        print("4. ⚫ Deadly - A fight for survival")
        difficulty = interactive_input("Choose a difficulty (1-4): ", config_file).strip()
        if difficulty == "_RESTART_SECTION_":
            continue  # Reprint the section header and options
        if difficulty in ("1", "2", "3", "4"):
            break
        print("Please enter 1, 2, 3, or 4.")
    difficulty_to_key = {"1": "easy", "2": "medium", "3": "hard", "4": "deadly"}
    max_xp = thresholds.get(difficulty_to_key.get(difficulty, "easy"), thresholds["easy"])

    filtered_monsters = filter_monsters_by_xp(monsters, max_xp)
    # Pass config_file to generate_encounter for further section restarts
    encounter, environment_description = generate_encounter(filtered_monsters, max_xp, config_file)

    print("\nGenerated Encounter:")
    for i, monster in enumerate(encounter):
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        xp = CR_TO_XP.get(str(cr), 0)
        if i == 0:
            print(f"- 🐲 {name} (CR: {cr}, XP: {xp})")
        else:
            print(f"- 🐭 {name} (CR: {cr}, XP: {xp})")
    
    print("\n💾 Saving the encounter...")
    save_encounter_to_md(encounter, folder_path, environment_description)
    print("\n🎉 Encounter saved successfully! Happy adventuring! ⚔️")

if __name__ == "__main__":
    main()
