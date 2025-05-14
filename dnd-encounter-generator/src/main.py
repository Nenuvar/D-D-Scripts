# filepath: src/main.py
from encounter_generator import load_monsters  # Import the function in encounter_generator.py.

def main():
    # Load the monster data from the JSON file.
    monsters = load_monsters('data/bestiary-mm.json')
    
    # Print the loaded monsters to the console.
    print("Monster Data:")
    for monster in monsters:
        print(f"- {monster['name']} (CR: {monster['challenge_rating']}, HP: {monster['hit_points']})")

if __name__ == "__main__":
    main()  # Run the main function when the script is executed.
