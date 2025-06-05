#This file works well with the v6-main.py and onwards
import requests
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set this in your environment variables

def generate_environment_description(environment):
    """
    Calls DeepSeek Chat API via OpenRouter to generate a short D&D environment description.
    """
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
        return "A mysterious place awaits..."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    if isinstance(environment, dict):
        env_name = environment.get("name", "unknown environment")
        main_monster = environment.get("main_monster", "unknown creature")
        minions = environment.get("minions", [])
        if minions:
            minion_names = ", ".join(minions)
            prompt = (
                f"Write a D&D environment description for a {env_name}. "
                f"Include subtle details or traces of {main_monster}. "
                f"Include some vague detail about one of these: {minion_names}. "
                "Maximum 480 characters including spaces."
            )
        else:
            prompt = (
                f"Write a D&D environment description for a {env_name}. "
                f"Include details or traces of the main monster: {main_monster}. "
                "Maximum 480 characters including spaces."
            )
    else:
        prompt = (
            f"Write a D&D environment description for a {environment}. "
            "Maximum 480 characters including spaces."
        )

    print(f"\n[AI Prompt]: {prompt}\n")

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a creative D&D encounter designer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI description error: {e}")
        return "A mysterious place awaits..."
def generate_battlemap_prompt(environment):
    """
    Calls DeepSeek Chat API via OpenRouter to generate a D&D battlemap prompt.
    """
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
        return "A mysterious battlemap awaits..."

    # Prepare environment string for prompt
    if isinstance(environment, dict):
        env_name = environment.get("name", "unknown environment")
    else:
        env_name = str(environment)

    prompt = (
        f"You must strictly use the following environment for the battlemap: {env_name}. "
        "Do not use any other environment or setting. "
        "Fill in the template below for a D&D battlemap prompt: "
        "`Top-down view battlemap for Dungeons & Dragons, high-resolution, fantasy style. `"
        f"`Environment:` [One sentence describing the chosen environment: {env_name}.] "
        "`Includes terrain features like` [details that fit in the environment.] "
        "`Designed for tabletop RPG use. No characters or monsters, only terrain.` "
        "`Lighting:` [Lighting description fitting for the scene.] "
        "`Realistic textures.` "
        "Include the text within `` as is, but remove the ``. Replace all bracketed sections with creative, setting-appropriate details that fit the environment above. "
        "Do not include the bracket labels in your output. Maximum 480 characters including spaces."
    )

    print(f"\n[AI Battlemap Prompt]: {prompt}\n")

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a creative D&D battlemap designer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 120,
        "temperature": 0.8
    }
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=15
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI battlemap prompt error: {e}")
        return "A mysterious battlemap awaits..."

def generate_encounter_title(environment, main_monster):
    """
    Calls DeepSeek Chat API via OpenRouter to generate a creative D&D encounter title
    based on the environment and main monster.
    """
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
        return "A Mysterious Encounter"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"Suggest a short, creative Dungeons & Dragons encounter title (max 8 words) "
        f"for an adventure set in a {environment} featuring a {main_monster}. "
        "Do not use quotes or punctuation at the start or end."
    )

    print(f"\n[AI Title Prompt]: {prompt}\n")

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a creative D&D encounter designer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 20,
        "temperature": 0.9
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI title error: {e}")
        return "A Mysterious Encounter"
    
