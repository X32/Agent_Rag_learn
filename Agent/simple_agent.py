import json
from datetime import datetime
import os
from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

client = OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# ============ 工具定义 ============

def get_current_time():
    """
    工具1：获取当前时间
    返回当前的日期和时间
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculator(operation: str, a: float, b: float):
    """
    工具2：计算器
    支持加减乘除运算

    参数：
        operation: 运算类型，可选 "add", "subtract", "multiply", "divide"
        a: 第一个数字
        b: 第二个数字
    """
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "错误：除数不能为零"
    }
    return operations.get(operation, "错误：未知运算类型")

# ============ 工具映射（用于根据名称调用对应函数）============
tools_map = {
    "get_current_time": get_current_time,
    "calculator": calculator
}

# ============ 告诉 LLM 有哪些工具可用 ============
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "执行数学计算，支持加减乘除",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "要执行的运算类型"
                    },
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    }
]

def run_agent(user_message: str):
    """
    Agent 主函数
    """
    response = client.chat.send(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个有用的助手，可以使用工具来帮助用户。"},
            {"role": "user", "content": user_message}
        ],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        print(f"🤖 LLM 决定调用工具...")

        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"   工具名称: {function_name}")
            print(f"   工具参数: {function_args}")

            if function_name in tools_map:
                result = tools_map[function_name](**function_args)
                print(f"   执行结果: {result}")

                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": str(result)
                })

        final_response = client.chat.send(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": user_message},
                message,
                *tool_results
            ]
        )

        return final_response.choices[0].message.content
    else:
        return message.content

# ============ 测试 Agent ============
if __name__ == "__main__":
    print("=" * 50)
    print("Agent 已启动！输入问题或输入 'quit' 退出")
    print("=" * 50)
    
    while True:
        user_input = input("\n请输入问题: ").strip()
        
        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("再见！")
            break
        
        if not user_input:
            continue
        
        result = run_agent(user_input)
        print(f"\n回答: {result}")
