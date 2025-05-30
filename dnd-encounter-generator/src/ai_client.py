#This file works with the v5-main.py and onwards
import requests
import os
from dotenv import load_dotenv
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set this in your environment variables

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
                f"Include subtle details or traces of a {main_monster}. "
                f"Include some vague detail about one of these: {minion_names}. "
                "Maximum 480 characters including spaces."
            )
        else:
            prompt = (
                f"Write a D&D environment description for a {env_name}. "
                f"Include subtle details or traces of a {main_monster}. "
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
    Calls DeepSeek Chat API via OpenRouter to generate a battlemap prompt for the chosen environment.
    """
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
        return "A generic battlemap for this environment."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"Write a detailed, vivid description of a D&D battlemap. "
        f"The map should be set in a {environment} environment. "
        "The style should be hand-painted digital illustration, no photorealism. Describe the terrain, features, and mood. Maximum 480 characters including spaces."
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
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"AI battlemap prompt error: {e}")
        return "A generic battlemap for this environment."
