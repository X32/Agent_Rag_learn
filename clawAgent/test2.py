from openrouter import OpenRouter
import os
from dotenv import load_dotenv

load_dotenv()

with OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    response = client.chat.send(
        model="openai/gpt-5.4",  # GPT 4.5
        # model="anthropic/claude-sonnet-4.6",
        messages=[
            {"role": "user", "content": "你是谁?"}
        ]
    )
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model used: {response.model}")  # Shows which model was selected
