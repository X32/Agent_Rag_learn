# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a learning repository for RAG (Retrieval-Augmented Generation) and AI Agent development in Python. It contains experimental implementations of various RAG patterns and simple agent systems.

## Package Management

This project uses **uv** as the package manager. Key commands:

```bash
# Run a Python script (uv handles dependencies automatically)
uv run python <script.py>

# Install dependencies from pyproject.toml
uv sync

# Add a new dependency
uv add <package-name>
```

## Project Structure

```
RAG_Agent_learn/
├── Day1/RAGDemo/          # RAG implementations
│   ├── naive_rag.py       # Pure Python RAG with sentence-transformers + ChromaDB
│   └── langchain_rag.py   # LangChain-based RAG implementation
├── clawAgent/             # Agent implementations
│   ├── step0.py, step1.py # Simple command-execution agents
│   ├── Agent.md           # Agent system prompt template
│   └── skill.md           # Skill definitions (news fetching)
└── doc/                   # Documentation files
```

## Key Technologies

- **Embeddings**: `sentence-transformers` (all-MiniLM-L6-v2 by default)
- **Vector Database**: ChromaDB (persistent storage in `./chroma_db/`)
- **LLM Access**: OpenRouter API (requires `OPENROUTER_API_KEY` in `.env`)
- **RAG Framework**: LangChain (alternative implementation)

## Running the Code

```bash
# Run naive RAG implementation
cd Day1/RAGDemo && uv run python naive_rag.py

# Run LangChain RAG implementation
cd Day1/RAGDemo && uv run python langchain_rag.py

# Run agent implementations
cd clawAgent && uv run python step0.py
```

## Environment Setup

Create a `.env` file in the root directory with:

```
OPENROUTER_API_KEY=<your-key>
```

## Architecture Notes

### RAG Pipeline (naive_rag.py)

1. **Document Loading**: Reads text files using standard Python file I/O
2. **Chunking**: Sentence-aware text splitting with configurable overlap (default: 500 chars, 50 overlap)
3. **Embedding**: HuggingFace sentence-transformers for local embedding generation
4. **Storage**: ChromaDB for persistent vector storage
5. **Retrieval**: Cosine similarity search (top-k=3 by default)
6. **Generation**: OpenRouter API to call LLM with retrieved context

### Agent Pattern (clawAgent/)

Simple ReAct-style agent that:

1. Receives user task
2. Decides whether to execute a shell command or complete
3. Executes command and feeds result back
4. Loops until task is complete

## Model Configuration

Default models used:

- Embedding: `all-MiniLM-L6-v2` (384 dimensions)
- LLM: `openai/gpt-5.4` (via OpenRouter)
- Agent LLM: `anthropic/claude-sonnet-4.6` (via OpenRouter)
