# API key is created at https://openrouter.ai/settings/keys
import requests
import json

api_key = "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"  # Replace with your actual API key
model = "deepseek/deepseek-chat-v3-0324:free"

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/Nenuvar",
    "X-Title": "Terminal Chat"
}

messages = []

print("Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    data = {
        "model": model,
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=data)

    try:
        response_json = response.json()
        content = response_json["choices"][0]["message"]["content"]
        print(f"AI: {content}")
        messages.append({"role": "assistant", "content": content})
    except (ValueError, KeyError, IndexError):
        print("Failed to extract content from response:")
        print(response.text)
