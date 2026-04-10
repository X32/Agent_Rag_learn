# Agent Day 1 详细学习计划

> 日期：_______
> 主题：从零搭建第一个 Agent - 工具调用入门
> 预计时长：3-4 小时

---

## 今日任务速览

### 任务清单

| 类型 | 任务                    | 状态 |
| ---- | ----------------------- | ---- |
| 理论 | 理解 Embedding 是什么   | ⬜   |
| 理论 | 理解向量维度            | ⬜   |
| 理论 | 理解 cosine similarity  | ⬜   |
| 理论 | 了解不同 Embedding 模型 | ⬜   |
| 实践 | 打印文本向量，观察数值  | ⬜   |
| 实践 | 计算文本相似度          | ⬜   |
| 输出 | 整理概念笔记            | ⬜   |
| 输出 | 保存代码和结果          | ⬜   |

### 学习方法

1. **先问 AI** ：用模板让 AI 解释 Embedding 概念
2. **动手跑代码** ：打印向量、计算相似度
3. **观察对比** ：近义词 vs 无关词的相似度差异
4. **记录疑问** ：不懂的地方记下来

### 输出文件

* `learn/notes/embedding-notes.md` - 概念笔记
* `learn/code/embedding-practice.py` - 实践代码
* `learn/code/embedding-results.txt` - 运行结果

## 今日学习目标

| 目标                       | 完成标准                      |
| -------------------------- | ----------------------------- |
| 理解 Agent 的基本概念      | 能用自己的话解释 Agent 是什么 |
| 理解 Function Calling 原理 | 知道 LLM 如何决定调用哪个工具 |
| 跑通第一个 Agent 程序      | 程序能正确调用工具并返回结果  |
| 逐行理解代码               | 能解释每一行代码的作用        |

---

## 前置准备（15分钟）

### 环境检查

- [ ] Python 3.8+ 已安装
- [ ] OpenAI API Key 已准备好
- [ ] 代码编辑器（VS Code / Cursor 等）已就绪

### 安装依赖

```bash
pip install openai
```

### API Key 配置

```bash
# 方式1：环境变量
export OPENAI_API_KEY="your-api-key"

# 方式2：代码中直接设置（不推荐生产环境）
```

---

## 核心概念预习（30分钟）

### 1. 什么是 Agent？

**简单理解**：Agent = LLM + 工具 + 自主决策能力

```
普通 ChatBot：
用户提问 → LLM → 直接回答

Agent：
用户提问 → LLM 思考 → 决定是否需要工具 → 调用工具 → 获取结果 → LLM → 最终回答
```

**类比**：

- 普通 ChatBot 像一个"只能动嘴"的顾问
- Agent 像一个"能动手做事"的助手

### 2. 什么是 Function Calling？

**核心机制**：

1. 你定义一组工具（函数），告诉 LLM 每个工具的功能和参数
2. 用户提问后，LLM 判断是否需要调用工具
3. 如果需要，LLM 返回要调用的工具名称和参数
4. 你的代码执行工具，把结果返回给 LLM
5. LLM 基于工具结果生成最终回答

**关键点**：LLM 不直接执行代码，它只是"决定"调用什么，真正执行的是你的代码。

### 3. Agent 的核心流程

```
┌─────────────┐
│  用户提问    │
└──────┬──────┘
       ▼
┌─────────────┐
│ LLM 分析问题 │
└──────┬──────┘
       ▼
┌─────────────┐     不需要
│ 需要工具吗？ │──────────────→ 直接回答
└──────┬──────┘
       │ 需要
       ▼
┌─────────────┐
│ 选择工具+参数│
└──────┬──────┘
       ▼
┌─────────────┐
│  执行工具    │
└──────┬──────┘
       ▼
┌─────────────┐
│ 返回结果给LLM│
└──────┬──────┘
       ▼
┌─────────────┐
│  生成最终回答 │
└─────────────┘
```

---

## 实践任务（90分钟）

### 任务 1：写一个最简单的 Agent（45分钟）

#### Step 1：定义工具（15分钟）

创建文件 `simple_agent.py`，首先定义两个工具：

```python
import json
from datetime import datetime
from openai import OpenAI

# 初始化客户端
client = OpenAI()

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
```

#### Step 2：定义工具描述（10分钟）

```python
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
```

**⚠️ 重要**：`description` 非常重要！LLM 根据描述来决定调用哪个工具。

#### Step 3：实现 Agent 主逻辑（20分钟）

```python
def run_agent(user_message: str):
    """
    Agent 主函数
    """
    # 1. 发送用户消息给 LLM
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个有用的助手，可以使用工具来帮助用户。"},
            {"role": "user", "content": user_message}
        ],
        tools=tools,  # 告诉 LLM 有哪些工具可用
        tool_choice="auto"  # 让 LLM 自动决定是否需要调用工具
    )

    message = response.choices[0].message

    # 2. 检查 LLM 是否想调用工具
    if message.tool_calls:
        print(f"🤖 LLM 决定调用工具...")

        # 可能有多个工具调用，逐个处理
        tool_results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"   工具名称: {function_name}")
            print(f"   工具参数: {function_args}")

            # 3. 执行工具
            if function_name in tools_map:
                result = tools_map[function_name](**function_args)
                print(f"   执行结果: {result}")

                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "content": str(result)
                })

        # 4. 把工具结果返回给 LLM，生成最终回答
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一个有用的助手。"},
                {"role": "user", "content": user_message},
                message,  # LLM 之前想调用工具的消息
                *tool_results  # 工具执行结果
            ]
        )

        return final_response.choices[0].message.content
    else:
        # 不需要工具，直接返回回答
        return message.content

# ============ 测试 Agent ============
if __name__ == "__main__":
    # 测试1：不需要工具的问题
    print("=" * 50)
    print("测试1：普通问题")
    result = run_agent("你好，请介绍一下自己")
    print(f"回答: {result}")

    # 测试2：需要获取时间
    print("\n" + "=" * 50)
    print("测试2：获取时间")
    result = run_agent("现在几点了？")
    print(f"回答: {result}")

    # 测试3：需要计算
    print("\n" + "=" * 50)
    print("测试3：数学计算")
    result = run_agent("帮我算一下 123 乘以 456 等于多少")
    print(f"回答: {result}")
```

### 任务 2：运行并理解（30分钟）

#### 运行程序

```bash
python simple_agent.py
```

#### 逐行理解（对照下面的问题自查）

| 行号范围 | 代码作用                      | 我理解了吗？ |
| -------- | ----------------------------- | ------------ |
| 1-5      | 导入必要的库                  | [ ]          |
| 8        | 初始化 OpenAI 客户端          | [ ]          |
| 12-17    | get_current_time 工具实现     | [ ]          |
| 19-33    | calculator 工具实现           | [ ]          |
| 36-40    | 工具名称到函数的映射          | [ ]          |
| 44-79    | 工具描述定义（关键！）        | [ ]          |
| 84-130   | Agent 主函数                  | [ ]          |
| 89-92    | 调用 LLM，传入工具定义        | [ ]          |
| 97       | 检查是否需要调用工具          | [ ]          |
| 100-117  | 执行工具并收集结果            | [ ]          |
| 120-129  | 把结果返回给 LLM 生成最终回答 | [ ]          |

### 任务 3：实验与探索（15分钟）

尝试修改代码，观察变化：

#### 实验 1：修改工具描述

把 `get_current_time` 的 description 改成：

```python
"description": "这是一个时间工具"  # 模糊的描述
```

然后问："现在几点了？"，观察 LLM 是否还能正确选择工具。

#### 实验 2：添加一个新工具

添加一个 `get_weather` 工具（可以返回假数据）：

```python
def get_weather(city: str):
    """获取指定城市的天气"""
    # 模拟数据
    weather_data = {
        "北京": "晴天，15°C",
        "上海": "多云，18°C",
        "广州": "小雨，22°C"
    }
    return weather_data.get(city, f"未找到{city}的天气信息")
```

然后在 `tools` 列表中添加对应的描述，测试 "北京今天天气怎么样？"

---

## 检查点

完成以下问题，检验你的理解：

### Q1：Function Calling 中，谁真正执行代码？

<details>
<summary>点击查看答案</summary>
是你的 Python 代码执行，不是 LLM。LLM 只返回要调用的函数名和参数，你的代码负责真正执行。
</details>

### Q2：tool_choice="auto" 是什么意思？

<details>
<summary>点击查看答案</summary>
让 LLM 自动决定是否需要调用工具。其他选项包括：
- "none"：不调用任何工具
- "required"：必须调用工具
- {"type": "function", "function": {"name": "xxx"}}：强制调用指定工具
</details>

### Q3：为什么工具的 description 很重要？

<details>
<summary>点击查看答案</summary>
LLM 根据描述来理解工具的用途，从而决定何时调用。描述写得越清晰，LLM 选择工具就越准确。
</details>

### Q4：如果 LLM 想调用多个工具，代码怎么处理？

<details>
<summary>点击查看答案</summary>
message.tool_calls 是一个列表，可能包含多个工具调用。代码用 for 循环逐个处理。
</details>

---

## 核心代码模板（保存备用）

```python
import json
from openai import OpenAI

client = OpenAI()

# 1. 定义工具函数
def my_tool(param1: str, param2: int):
    """工具描述"""
    # 工具实现
    return "结果"

# 2. 工具映射
tools_map = {
    "my_tool": my_tool
}

# 3. 工具描述（给 LLM 看的）
tools = [
    {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "清晰描述工具的功能",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "参数1描述"},
                    "param2": {"type": "integer", "description": "参数2描述"}
                },
                "required": ["param1", "param2"]
            }
        }
    }
]

# 4. Agent 主循环
def run_agent(user_message: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_message}],
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_results = []
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            result = tools_map[fn_name](**fn_args)

            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "content": str(result)
            })

        # 再次调用 LLM 生成最终回答
        final = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_message},
                message,
                *tool_results
            ]
        )
        return final.choices[0].message.content

    return message.content
```

---

## 笔记区域

### Agent 是什么？

### Function Calling 的流程是什么？

### 工具描述为什么重要？

### 我遇到的问题

### 我还没理解的地方

---

## 今日产出检查

- [ ] 代码运行成功
- [ ] 能解释每一行代码的作用
- [ ] 理解 Function Calling 的基本原理
- [ ] 知道 tool_calls 是什么
- [ ] 完成了至少 1 个实验
- [ ] 记录了不懂的问题




---

## 明日预告

Day 2 将深入探讨：

- Function Calling 的底层原理
- LLM 如何决定调用哪个工具
- description 的写作技巧
- 多工具场景下的选择机制

---

*学习日期：_______*
*完成时间：_______*
*自我评分：⭐⭐⭐⭐⭐*
