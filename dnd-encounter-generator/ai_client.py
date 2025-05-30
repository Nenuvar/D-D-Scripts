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
    prompt = (
        f"Write a short, vivid Dungeons & Dragons encounter environment description for a '{environment}' setting. "
        "Keep it under 50 words. Do not mention monsters."
    )
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
