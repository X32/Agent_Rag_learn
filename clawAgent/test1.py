from openrouter import OpenRouter
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))

# Try these specific free models:
free_models = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "openchat/openchat-7b:free"
]

for model in free_models:
    try:
        response = client.chat.send(
            model=model,
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(f"✅ {model}: {response.choices[0].message.content[:50]}...")
        break  # Use the first working model
    except Exception as e:
        print(f"❌ {model}: {str(e)}")
        continue
