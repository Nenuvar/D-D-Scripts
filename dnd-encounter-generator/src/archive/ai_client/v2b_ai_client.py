# This version has a problem with feeding the AI with the right environment

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

    # print(f"\n[AI Title Prompt]: {prompt}\n")

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
    
# def generate_environment_description(environment):

#     """
#     Calls DeepSeek Chat API via OpenRouter to generate a short D&D environment description.
#     """
#     if not OPENROUTER_API_KEY:
#         print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
#         return "A mysterious place awaits..."

#     url = "https://openrouter.ai/api/v1/chat/completions"
#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json"
#     }
#     if isinstance(environment, dict):
#         env_name = environment.get("name", "unknown environment")
#         main_monster = environment.get("main_monster", "unknown creature")
#         battlemap_prompt = environment.get("battlemap_prompt", "")
#         prompt = (
#             f"Given this D&D battlemap prompt:\n"
#             f"\"\"\"\n{battlemap_prompt}\n\"\"\"\n"
#             f"Write a short, vivid environment description for a {env_name} featuring a {main_monster}. "
#             "Make sure the description matches the details and mood of the battlemap prompt above. "
#             "Maximum 480 characters including spaces."
#         )
#     else:
#         prompt = (
#             f"Write a D&D environment description for a {environment}. "
#             "Maximum 480 characters including spaces."
#         )

#     data = {
#         "model": "deepseek/deepseek-chat-v3-0324:free",
#         "messages": [
#             {"role": "system", "content": "You are a creative D&D encounter designer."},
#             {"role": "user", "content": prompt}
#         ],
#         "max_tokens": 100,
#         "temperature": 0.8
#     }
#     try:
#         response = requests.post(url, headers=headers, json=data, timeout=15)
#         response.raise_for_status()
#         result = response.json()
#         return result["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         print(f"AI description error: {e}")
#         return "A mysterious place awaits..." 
    
def generate_battlemap_prompt(environment): # Add ", environment_description=None" after "environment" if you want to use the AI-generated environment description
    """
    Calls DeepSeek Chat API via OpenRouter to generate a battlemap prompt for the chosen environment,
    following a structured template. Uses the environment description for correlation.
    """
    if not OPENROUTER_API_KEY:
        print("OpenRouter API key not set. Set OPENROUTER_API_KEY environment variable.")
        return "A generic battlemap for this environment."

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    template = (
        f"You must strictly use the following environment for the battlemap: {environment}. "
        "Do not use any other environment or setting. "
        "Fill in the template below for a D&D battlemap prompt:\n"
        "`Top-down view battlemap for Dungeons & Dragons, high-resolution, fantasy style. `"
        f"`Environment:` [One sentence describing the chosen environment: {environment}]. "
        f"`Includes terrain features like` [details that fit in the {environment}]. "
        "`Designed for tabletop RPG use. No characters or monsters, only terrain.` "
        "`Lighting: `[Lighting description fitting for the scene]. "
        "`Realistic textures.`\n"
        "Include the text within `` as is, but remove the ``. Replace all bracketed sections with creative, setting-appropriate details that fit the environment above. "
        "Do not include the bracket labels in your output. Maximum 480 characters including spaces."
    )
    
    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a creative D&D battlemap designer."},
            {"role": "user", "content": template}
        ],
        "max_tokens": 120,
        "temperature": 0.8
    }

    # Print the message sent to the AI for debugging
    print("\n[AI Battlemap Message]:")
    for msg in data["messages"]:
        print(f"{msg['role']}: {msg['content']}\n")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        result = response.json()
        prompt = result["choices"][0]["message"]["content"].strip()
        print(f"\n[AI Battlemap Prompt]: {prompt}\n")
        return prompt
    except Exception as e:
        print(f"AI battlemap prompt error: {e}")
        return "A generic battlemap for this environment."
