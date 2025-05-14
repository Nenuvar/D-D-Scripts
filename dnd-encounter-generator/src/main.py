# filepath: src/main.py
from encounter_generator import load_monsters  # Import the function to load monsters

def main():
    # Load the monster data from the JSON file
    data = load_monsters('src/data/bestiary-mm.json')  # Adjust the path to your JSON file
    monsters = data["monster"]  # Access the list of monsters under the "monster" key

    # Print the loaded monsters to the console
    print("Monster Data:")
    for monster in monsters:
        # Safely access monster details, as some fields might be missing
        name = monster.get("name", "Unknown")
        cr = monster.get("cr", "Unknown")
        hp = monster.get("hp", {}).get("average", "Unknown")
        print(f"- {name} (CR: {cr}, HP: {hp})")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed
