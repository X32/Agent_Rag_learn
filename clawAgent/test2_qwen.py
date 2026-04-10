from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 使用 OpenAI 风格 API 访问阿里千问
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),  # 阿里云 DashScope API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

response = client.chat.completions.create(
    model="qwen-plus",  # 可选: qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext
    messages=[
        {"role": "user", "content": "你是谁?"}
    ]
)

print(f"Response: {response.choices[0].message.content}")
print(f"Model used: {response.model}")
