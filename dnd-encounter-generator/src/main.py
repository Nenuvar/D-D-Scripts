# filepath: src/main.py
import json

def main():
    with open('bestiary-mm.json', 'r') as file:
        monsters = json.load(file)
    
    print("Monster Data:")
    for monster in monsters:
        print(f"- {monster}")  # Only prints the monster name

if __name__ == "__main__":
    main()
