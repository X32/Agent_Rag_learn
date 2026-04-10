from openrouter import OpenRouter
import os
import time
from dotenv import load_dotenv

load_dotenv()
message = []
agentmd = open("Agent.md").read()
skillmd = open("skill.md").read()
message.append({"role": "system", "content": agentmd + skillmd})
with OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY")
) as client:
    while True:
        user_input = input("你`: ")
        message.append({"role": "user", "content": user_input})

        # 重试逻辑
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.chat.send(
                    model="anthropic/claude-sonnet-4.6",
                    messages=message
                )
                reply = response.choices[0].message.content
                message.append({"role": "assistant", "content": reply})

                print(f"Response: {reply}")
                print(f"Model used: {response.model}")

                if reply.strip().startswith("完成："):
                    print("\n- - Agent 循环结束 -")
                    print(f" [AI] {reply.strip().split('完成：')[1].strip()}")
                    break
                command = reply.strip().split("命令：")[1].strip()
                command_result = os.popen(command).read()
                content = f"命令：{command}\n结果：{command_result}"
                print(f"Agent: {content}")
                message.append({"role": "user", "content": content})

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"连接失败，重试中... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    print(f"错误: {e}")
