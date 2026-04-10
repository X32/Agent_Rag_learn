# RAG Agent Learn

这是一个学习 RAG（检索增强生成）和 AI Agent 开发的 Python 项目。

## 环境要求

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - 现代 Python 包管理器

## 安装 uv

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd RAG_Agent_learn
```

### 2. 配置环境变量
在项目根目录创建 `.env` 文件：
```bash
OPENROUTER_API_KEY=<your-openrouter-api-key>
```

### 3. 安装依赖
```bash
uv sync
```

### 4. 运行项目

#### RAG 示例
```bash
# Naive RAG 实现
uv run python RAG/naive_rag.py

# LangChain RAG 实现
uv run python RAG/langchain_rag.py
```

#### Agent 示例
```bash
# 简单命令执行 Agent
uv run python clawAgent/step0.py
uv run python clawAgent/step1.py

# OpenRouter 测试
uv run python clawAgent/test2.py
```

## 常用 uv 命令

```bash
# 运行 Python 脚本（自动处理依赖）
uv run python <script.py>

# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 更新所有依赖
uv lock --upgrade

# 查看已安装的包
uv pip list
```

## 项目结构

```
RAG_Agent_learn/
├── RAG/                    # RAG 实现
│   ├── naive_rag.py        # 纯 Python RAG (sentence-transformers + ChromaDB)
│   └── langchain_rag.py    # LangChain RAG 实现
├── clawAgent/              # Agent 实现
│   ├── step0.py, step1.py  # 简单命令执行 Agent
│   ├── Agent.md            # Agent 系统提示模板
│   └── skill.md            # 技能定义
├── doc/                    # 文档
├── chroma_db*/             # ChromaDB 向量数据库存储
├── pyproject.toml          # 项目配置和依赖
├── uv.lock                 # 锁定的依赖版本
└── .env                    # 环境变量 (需自行创建)
```

## 技术栈

- **Embedding**: `sentence-transformers` (默认 all-MiniLM-L6-v2)
- **向量数据库**: ChromaDB (持久化存储)
- **LLM 访问**: OpenRouter API
- **RAG 框架**: LangChain (可选)

## 默认模型配置

- Embedding: `all-MiniLM-L6-v2` (384 维度)
- LLM: `openai/gpt-4.5` (via OpenRouter)
- Agent LLM: `anthropic/claude-sonnet-4.6` (via OpenRouter)
# Agent_Rag_learn
