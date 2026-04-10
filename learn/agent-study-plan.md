# Agent 学习计划

> 基于「递归式知识填充」方法，4-5 周掌握 Agent 核心技术
>
> **版本**：v2.0（2026-03-30 调整）  
> **调整要点**：增加弹性缓冲机制 / 平衡 Week3 密度 / 补充 OpenRouter 兼容性验证 / 加入中途校准点

---

## 学习目标

**项目目标**：搭建一个能自主调用工具、解决复杂任务的智能助手

**能力目标**：
- 理解 Agent 核心范式（ReAct、Plan-Execute）
- 能设计和实现自定义工具
- 能搭建多 Agent 协作系统

---

## 时间分配

```
每周 12-15 小时（可持续节奏，避免第3周断档）
├── 项目驱动（写代码 + 递归追问）    50%  │ 6-8h
├── 主动探索（论文 + 开源 + 社区）   20%  │ 2-3h
├── 知识索引（概念地图 + 笔记）      10%  │ 1-2h
└── 输出反馈（Demo + 博客 + 验证）   20%  │ 2-3h
```

> ⚡ **弹性规则**：若某天未能完成任务，可将 Day7 输出日顺延 1-2 天，不强行按日历推进。  
> 完成度 > 节奏感，断了就重连，不要因为"落后"而放弃整个计划。

---

## ⚠️ 环境预检（开始前务必完成）

```bash
# 验证 OpenRouter API 是否支持 Function Calling
# 你使用的是 OpenRouter，而非原生 OpenAI，需提前确认兼容性

python3 << 'EOF'
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-openrouter-key",
)

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",   # 换成你常用的模型
    messages=[{"role": "user", "content": "今天几号？"}],
    tools=[{
        "type": "function",
        "function": {
            "name": "get_date",
            "description": "获取当前日期",
            "parameters": {"type": "object", "properties": {}}
        }
    }],
    tool_choice="auto"
)
print(response.choices[0].message)
EOF
```

- [ ] Function Calling 调用成功
- [ ] 确认使用的模型名称（记录到笔记）
- [ ] 如果失败，换用原生 OpenAI SDK 或切换模型重试

> 💡 向量数据库部分：你已有 chroma_db 实验经验，Week2 长期记忆部分对你会轻松很多，可利用节省的时间提前预习 LangGraph。

---

## Week 1：Agent 基础 - 从工具调用开始

### 项目任务：简单工具调用 Agent

**Day 1-2：让 AI 写代码，跑起来**

提示词：
```
写一个最简单的 Agent：
1. 用户提问
2. Agent 判断是否需要调用工具
3. 如果需要，调用工具获取结果
4. 基于结果回答用户

工具1：获取当前时间
工具2：计算器（加减乘除）

用 OpenAI SDK（兼容 OpenRouter）的 Function Calling 实现
要求：代码尽可能简单，每行都要有注释
```

完成后：
- [ ] 运行成功
- [ ] 逐行理解每一行代码
- [ ] 记录不懂的地方

**Day 3-4：递归追问 - Function Calling**

核心问题：
- [ ] Function Calling 的底层原理是什么？
- [ ] LLM 怎么知道要调用哪个函数？
- [ ] function 的 description 为什么重要？
- [ ] tools 和 functions 参数怎么设计？
- [ ] 多个工具时，LLM 怎么选择？

实践：
- [ ] 修改工具描述，观察 LLM 选择的变化
- [ ] 添加一个新工具，测试调用

**Day 5-6：递归追问 - ReAct 范式**

核心问题：
- [ ] ReAct 是什么？（Reasoning + Acting）
- [ ] Thought / Action / Observation 是什么流程？
- [ ] 为什么先"想"再"行动"很重要？
- [ ] 和直接让 LLM 回答有什么区别？

提示词：
```
请展示一个完整的 ReAct 流程：
问题：北京今天天气怎么样？

要求：
1. 展示每一步的 Thought
2. 展示调用的 Action
3. 展示 Observation
4. 最终给出答案
```

**Day 7：输出反馈 + 周末校准**

- [ ] 写笔记：**"我从零理解 Agent 的5个关键概念"**
- [ ] 让 AI 检查你的笔记有没有理解错误

**📍 周末校准**：
> 问自己：下周的长期记忆部分，我对向量数据库掌握程度如何？  
> 如果不确定，用 1 小时速读一遍 Chroma 的基础用法，再开始 Week2。

---

## Week 2：工具开发与记忆系统

### 项目任务：实用 Agent - 个人助手

**Day 1-2：开发自定义工具**

提示词：
```
帮我开发 3 个实用的 Agent 工具：

1. 网页搜索工具（调用 Serper API）
2. 代码执行工具（安全的 Python 执行）
3. 文件读写工具

每个工具要有清晰的描述和参数定义
```

核心问题：
- [ ] 工具描述怎么写才能让 LLM 正确理解？
- [ ] 参数校验怎么做？
- [ ] 错误处理怎么做？
- [ ] 工具执行超时怎么办？

**Day 3-4：记忆系统 - 短期记忆**

核心问题：
- [ ] Agent 怎么记住之前的对话？
- [ ] ConversationBufferMemory 是什么？
- [ ] 对话太长怎么办？（窗口截断、摘要）
- [ ] Message 怎么存储？（HumanMessage, AIMessage, SystemMessage）

实践：
- [ ] 实现 10 轮对话的记忆
- [ ] 测试 Agent 能否记住之前说过的信息

**Day 5-6：记忆系统 - 长期记忆**

> 💡 你已有 Chroma 使用经验，这部分应该比较顺。重点放在"如何从对话中提取关键信息并写入"这个环节，这才是难点。

提示词：
```
给 Agent 加上长期记忆：
1. 把重要信息存入向量数据库（使用 ChromaDB）
2. 下次对话时检索相关记忆
3. 把检索到的记忆注入 Prompt

解释长期记忆的实现原理，以及如何判断哪些信息值得存入
```

核心问题：
- [ ] 什么信息值得存入长期记忆？
- [ ] 怎么从对话中提取关键信息？
- [ ] 检索记忆时怎么排序？
- [ ] LangChain 的 VectorStoreMemory 怎么用？

**Day 7：输出反馈 + 周末校准**

- [ ] Demo：一个能记住用户偏好的个人助手
- [ ] 写笔记：**"Agent 记忆系统的设计与实现"**

**📍 周末校准**：
> 问自己：我对 LangChain 的核心抽象（Chain、Runnable、Memory）清楚吗？  
> 下周 Week3 开始就是多 Agent + LangGraph，如果这些概念还模糊，提前用1小时扫一遍。

---

## Week 3：规划与多 Agent 协作

> ⚠️ **本周难度最高**，内容较密，建议 Day7 设为弹性备用日，遇到卡点可延伸。

### 项目任务：复杂任务 Agent

**Day 1-2：Plan-and-Execute 范式**

提示词：
```
实现一个 Plan-and-Execute Agent：
1. 收到复杂任务后，先制定计划
2. 逐步执行计划的每一步
3. 根据执行结果调整后续计划

示例任务：帮我调研 RAG 的最新进展，写一份报告
```

核心问题：
- [ ] Plan-and-Execute 和 ReAct 有什么区别？
- [ ] 什么任务适合先规划再执行？
- [ ] 计划执行失败怎么办？（重规划）
- [ ] 怎么评估计划的完成度？

**Day 3-4：多 Agent 协作**

提示词：
```
实现一个简单的多 Agent 系统：
- Researcher Agent：负责搜索和收集信息
- Writer Agent：负责整理和写作
- Reviewer Agent：负责审核和修改

它们通过共享的消息队列协作
```

核心问题：
- [ ] 为什么需要多个 Agent？
- [ ] Agent 之间怎么通信？
- [ ] 怎么避免 Agent 之间死循环？
- [ ] 协作中的状态共享怎么设计？

**Day 5-7：LangGraph 入门（3天，给足时间）**

> LangGraph 学习曲线不平缓，StateGraph + 条件分支 + 节点生命周期都需要时间消化。本版本给了3天。

核心问题：
- [ ] LangGraph 和 LangChain 有什么区别？
- [ ] StateGraph 是什么？
- [ ] Node 和 Edge 怎么定义？
- [ ] 怎么实现条件分支（Conditional Edge）？
- [ ] 怎么实现循环（人工审核 / 重试）？

实践：
- [ ] 跑官方最小示例，理解状态流转
- [ ] 用 LangGraph 重写上面的多 Agent 系统
- [ ] 画出你的 Agent 架构图

**📍 周末校准**：
> 问自己：LangGraph 的 StateGraph 我能独立写出来吗？  
> 如果不能，别急着进 Week4，把这个补扎实再整合。  
> 计划可以延伸到第5周，完成度 > 时间表。

---

## Week 4：项目整合 + 工程化

### 项目任务：完整 Agent Demo

**Day 1-3：整合项目**

- [ ] 搭建一个完整的 Agent Demo
- [ ] 功能：能搜索、能记住、能规划、能协作
- [ ] 技术栈：LangChain + LangGraph + OpenRouter API

可选方向：
- **研究助手**：自动搜索、整理、生成报告（推荐，与你的内容方向契合）
- 代码助手：读代码、写代码、调试
- 数据分析助手：读取数据、分析、可视化

**Day 4-5：安全与最佳实践**

核心问题：
- [ ] Agent 的安全风险有哪些？
- [ ] Prompt 注入是什么？怎么防护？
- [ ] 工具调用的权限控制怎么做？
- [ ] 怎么防止 Agent 陷入死循环？
- [ ] Agent 的成本怎么控制？（Token 消耗）
- [ ] 怎么做 Agent 的可观测性（日志 + Trace）？

**Day 6：面试 / 输出准备**

整理以下问题的答案：
- [ ] Agent 和普通 ChatBot 有什么区别？
- [ ] ReAct 范式的优缺点？
- [ ] 怎么设计一个好的工具？
- [ ] 多 Agent 协作有什么挑战？
- [ ] 你的项目中遇到的最大挑战是什么？
- [ ] Agent 的发展趋势是什么？

**Day 7：最终输出**

- [ ] 完成技术博客
- [ ] 整理面试 Q&A 文档
- [ ] Demo 录屏或截图

---

## 主动探索清单

### 论文（每周 30 分钟扫标题）

- [ ] ReAct: Synergizing Reasoning and Acting in Language Models
- [ ] Toolformer: Language Models Can Teach Themselves to Use Tools
- [ ] Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
- [ ] AutoGPT、BabyAGI 等早期 Agent 论文
- [ ] arXiv cs.CL / cs.AI 标签每周新论文

### 开源项目（每周 2 小时读代码）

- [ ] LangChain agents 模块
- [ ] LangGraph 核心示例
- [ ] AutoGPT 核心逻辑
- [ ] CrewAI 多 Agent 框架

### 社区关注

- [ ] Twitter: @hwchase17 (LangChain)
- [ ] Twitter: @LaurieVoss (Agent 动态)
- [ ] Reddit: r/LocalLLaMA, r/LangChain
- [ ] Discord: LangChain 官方社区

---

## 知识索引（概念地图）

```
Agent 系统
│
├── 核心范式
│   ├── ReAct (Reasoning + Acting)
│   ├── Plan-and-Execute
│   ├── Reflexion (自我反思)
│   └── Chain-of-Thought
│
├── 工具系统
│   ├── Function Calling
│   ├── 工具描述设计
│   ├── 参数定义与校验
│   ├── 错误处理
│   └── 自定义工具开发
│
├── 记忆系统
│   ├── 短期记忆
│   │   ├── 完整历史
│   │   ├── 窗口截断
│   │   └── 对话摘要
│   ├── 长期记忆
│   │   ├── 向量存储（ChromaDB）
│   │   ├── 知识图谱
│   │   └── 信息提取
│   └── 混合记忆
│
├── 规划系统
│   ├── 任务分解
│   ├── 计划生成
│   ├── 执行监控
│   └── 动态重规划
│
├── 多Agent 协作
│   ├── 角色定义
│   ├── 通信协议
│   ├── 任务分配
│   └── 结果整合
│
├── 框架
│   ├── LangChain
│   ├── LangGraph  ← 重点掌握
│   ├── LlamaIndex Agents
│   ├── CrewAI
│   └── AutoGen
│
└── 安全与工程
    ├── Prompt 注入防护
    ├── 权限控制
    ├── 成本控制（Token 监控）
    └── 可观测性（日志 + Trace）
```

---

## 提示词模板

### 学习新概念

```markdown
我想学习 Agent 中的 [概念名称]。请：

1. 用 12 岁小孩能懂的话解释核心思想
2. 给我一个可运行的 Python 代码示例
3. 解释每一行代码在做什么
4. 告诉我这个概念在整个 Agent 系统中的位置
5. 列出相关的 3-5 个重要概念
6. 指出初学者容易误解的地方
```

### 验证理解

```markdown
我对 [概念] 的理解是：

[你的解释...]

请：
1. 指出我理解错误或不完整的地方
2. 用反例挑战我的理解
3. 提出延伸问题测试我的掌握程度
```

### 设计工具

```markdown
我想给 Agent 添加一个工具：[工具功能]

请帮我设计：
1. 工具名称和描述（让 LLM 能正确理解）
2. 输入参数定义
3. Python 实现代码
4. 错误处理逻辑
```

### 调试 Agent

```markdown
我的 Agent 遇到了这个问题：

[描述问题：比如工具选择错误、陷入循环、回答不相关]

Agent 的执行日志：
[贴日志]

请帮我：
1. 分析可能的原因
2. 给出排查步骤
3. 提供解决方案
```

---

## 打卡记录

### Week 1

| 日期 | 任务 | 完成 | 笔记 |
|:---|:---|:---|:---|
| Day 1-2 | 简单 Agent 跑起来 | [ ] | |
| Day 3-4 | Function Calling 深入 | [ ] | |
| Day 5-6 | ReAct 范式理解 | [ ] | |
| Day 7 | 输出笔记 + 周末校准 | [ ] | |

### Week 2

| 日期 | 任务 | 完成 | 笔记 |
|:---|:---|:---|:---|
| Day 1-2 | 自定义工具开发 | [ ] | |
| Day 3-4 | 短期记忆 | [ ] | |
| Day 5-6 | 长期记忆（Chroma） | [ ] | |
| Day 7 | Demo 输出 + 周末校准 | [ ] | |

### Week 3

| 日期 | 任务 | 完成 | 笔记 |
|:---|:---|:---|:---|
| Day 1-2 | Plan-and-Execute | [ ] | |
| Day 3-4 | 多 Agent 协作 | [ ] | |
| Day 5-7 | LangGraph 入门（3天） | [ ] | |
| 周末 | 架构图 + 周末校准 | [ ] | |

### Week 4

| 日期 | 任务 | 完成 | 笔记 |
|:---|:---|:---|:---|
| Day 1-3 | 完整 Demo 整合 | [ ] | |
| Day 4-5 | 安全与最佳实践 | [ ] | |
| Day 6 | 面试 / 输出准备 | [ ] | |
| Day 7 | 最终输出 | [ ] | |

---

## 常见问题速查

### Q: Agent 和 RAG 有什么区别？

| 维度 | RAG | Agent |
|:---|:---|:---|
| 核心能力 | 检索知识 | 执行动作 |
| 适用场景 | 知识问答 | 任务执行 |
| 是否有状态 | 无状态 | 有状态（记忆） |
| 是否有工具 | 通常无 | 有 |

### Q: 什么时候用 Agent，什么时候用 RAG？

```
需要"知道"→ RAG
需要"做事" → Agent
既要知道又要做事 → RAG + Agent
```

### Q: LangChain vs LangGraph 怎么选？

| 场景 | 推荐 |
|:---|:---|
| 简单链式调用 | LangChain Chain |
| 复杂状态流转 | LangGraph |
| 多 Agent 协作 | LangGraph |
| 快速原型 | LangChain |

---

*计划生成日期：2026-03-23*  
*v2.0 调整日期：2026-03-30（增加弹性机制、环境预检、校准点、LangGraph 扩展至3天）*
