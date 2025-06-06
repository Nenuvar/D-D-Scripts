#This file works well with the v10-main.py and onwards
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
        minion_names = ", ".join(minions) if minions else ""
        prompt = (
            f"Generate a Dungeons & Dragons encounter with the following format:\n\n"
            f"'**Location:**' {env_name}  \n"
            f"'**Atmosphere:**' [Describe the sensory details of the environment (light, smell, sound, etc). Keep it evocative but concise.] \n"
            f"'**Objective:**' [Briefly describe what the heroes need to do here. Mention the threat or mystery involving the main monster: {main_monster}, and optionally a relic, ritual, or NPC involvement. Include {minion_names} vaguely if possible.]\n"
            f"'**Twist:**' [Include an unexpected element that changes how the players might approach the situation. Ensure it impacts the heroes' decisions.]\n"
            f"'**Treasure:**' [Mention one or two appropriate and official D&D treasure items hidden or guarded in the environment {env_name}. Use [[item-name|Item Name]] formatting.]\n"
            f"'#### Terrain Hazards'\n"
            f"- [List two or three hazards tied to the environment ({env_name}). Include their effects and mechanics like DCs or penalties. Keep it punchy and game-relevant.]\n"
            f"Include the text within `` as is, but remove the ``. Replace all bracketed sections with creative, setting-appropriate details that fit the environment above. "
            f"Do not include the bracket labels in your output."
        )
    else:
        env_name = str(environment)
        main_monster = "unknown creature"
        minion_names = ""
        prompt = (
            f"Generate a Dungeons & Dragons encounter with the following format:\n\n"
            f"'**Location:**' {env_name}  \n"
            f"'**Atmosphere:**' [Describe the sensory details of the environment (light, smell, sound, etc). Keep it evocative but concise.] \n"
            f"'**Objective:**' [Briefly describe what the heroes need to do here. Mention the threat or mystery involving the main monster: {main_monster}, and optionally a relic, ritual, or NPC involvement. Include {minion_names} vaguely if possible.]\n"
            f"'**Twist:**' [Include an unexpected element that changes how the players might approach the situation. Ensure it impacts the heroes' decisions.]\n"
            f"'**Treasure:**' [Mention one or two appropriate and official D&D treasure items hidden or guarded in the environment {env_name}. Use [[item-name|Item Name]] formatting.]\n"
            f"'#### Terrain Hazards'\n"
            f"- [List two or three hazards tied to the environment ({env_name}). Include their effects and mechanics like DCs or penalties. Keep it punchy and game-relevant.]\n"
            f"Include the text within `` as is, but remove the ``. Replace all bracketed sections with creative, setting-appropriate details that fit the environment above. "
            f"Do not include the bracket labels in your output."
        )

    print(f"\n[AI Prompt]: {prompt}\n")

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a creative D&D encounter designer."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300,
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
        "`Focal point:` [A clear, central feature to organize the scene visually. Keep it short]. "
        f"`{env_name} with` [brief, vivid description of terrain elements specific to the environment.] "
        "`Zoomed-in for token use on VTTs. No characters or monsters. `"
        "`Lighting:` [atmospheric lighting detail suitable for the scene.] "
        "`Realistic textures, grid-friendly layout, detailed terrain.` "
        "Include the text within `` as is, but remove the ``. Replace all bracketed sections with creative, setting-appropriate details that fit the environment above. "
        "Do not include the bracket labels in your output. "
        "Maximum 480 characters including spaces. "
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
    
