# RAG 学习计划 - Day 4 详细计划

> **主题**：递归追问 - 文本切分
> **所属周**：Week 1
> **预计时间**：2-3 小时

---

## 今日目标

1. 深入理解文本切分（Chunking）的原理和必要性
2. 掌握不同切分策略的优缺点
3. 通过实验对比不同参数的效果差异

---

## 核心问题清单

### Q1: 为什么要切分？不切分行不行？

**思考方向**：
- LLM 的 context window 有限制
- 向量检索的精度问题
- 成本和效率的考量

**向 AI 提问的提示词**：
```
我在 RAG 系统中，为什么不直接把整个文档转成向量？
请从以下角度解释：
1. 技术限制（LLM context window）
2. 检索精度（向量相似度的特性）
3. 成本考虑（API 调用费用）
4. 给一个具体的例子说明不切分的问题
```

---

### Q2: chunk_size 多大合适？为什么？

**思考方向**：
- 太小：丢失上下文，信息碎片化
- 太大：检索精度下降，噪音增加
- 平衡点取决于：文档类型、问题类型、Embedding 模型

**向 AI 提问的提示词**：
```
RAG 中的 chunk_size 应该怎么选择？

请：
1. 解释 chunk_size 太小和太大各自的问题
2. 不同场景下的推荐值（代码、长文、问答、对话）
3. 为什么没有一个"万能"的 chunk_size
4. 给出一个决策流程图
```

---

### Q3: chunk_overlap 是什么？为什么需要？

**思考方向**：
- 防止关键信息被切断在 chunk 边界
- 保持语义连续性
- overlap 的代价：存储和计算成本增加

**向 AI 提问的提示词**：
```
RAG 中的 chunk_overlap 是什么？

请：
1. 用一个具体例子说明没有 overlap 会出什么问题
2. overlap 一般设置为 chunk_size 的多少比例？
3. overlap 会带来什么代价？
4. 什么情况下可以不用 overlap？
```

---

### Q4: 有哪些切分策略？各有什么优缺点？

**四种主要策略**：

| 策略 | 原理 | 优点 | 缺点 | 适用场景 |
|-----|------|------|------|---------|
| 固定长度 | 按字符/token 数切分 | 简单可控 | 可能切断句子 | 通用场景 |
| 句子切分 | 按句号、换行等分割 | 语义完整 | 长度不均 | 短文档 |
| 语义切分 | 用 Embedding 相似度判断边界 | 语义连贯 | 计算成本高 | 高质量需求 |
| 递归切分 | 先按段落，再按句子，再按字符 | 灵活 | 复杂 | 通用推荐 |

**向 AI 提问的提示词**：
```
请介绍 RAG 中常用的文本切分策略：

1. 固定长度切分（CharacterTextSplitter）
2. 递归字符切分（RecursiveCharacterTextSplitter）
3. 句子切分
4. 语义切分（Semantic Splitter）

对每种策略：
- 原理是什么
- 用 LangChain 的代码示例
- 优缺点
- 最佳适用场景
```

---

## 实践任务

### 任务 1：准备测试文档

创建一个测试用的文本文档 `test_doc.txt`，内容建议：
- 一篇技术文章（500-1000 字）
- 或者复制一段 Wikipedia 条目

---

### 任务 2：对比不同 chunk_size 的效果

**代码模板**：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 读取文档
with open("test_doc.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 测试不同的 chunk_size
chunk_sizes = [128, 256, 512, 1024]

for size in chunk_sizes:
    print(f"\n{'='*50}")
    print(f"chunk_size = {size}")
    print(f"{'='*50}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=size // 5,  # overlap 为 chunk_size 的 20%
        length_function=len,
    )

    chunks = splitter.split_text(text)

    print(f"切分后的块数: {len(chunks)}")
    print(f"第一块长度: {len(chunks[0])}")
    print(f"第一块内容预览:\n{chunks[0][:200]}...")
```

**记录观察结果**：

| chunk_size | 块数 | 第一块长度 | 观察到的问题 |
|-----------|------|-----------|-------------|
| 128 | | | |
| 256 | | | |
| 512 | | | |
| 1024 | | | |

---

### 任务 3：对比有无 overlap 的差异

**代码模板**：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

with open("test_doc.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 无 overlap
splitter_no_overlap = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=0,
)

# 有 overlap
splitter_with_overlap = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=40,  # 20%
)

chunks_no = splitter_no_overlap.split_text(text)
chunks_with = splitter_with_overlap.split_text(text)

print("无 overlap:")
print(f"  块数: {len(chunks_no)}")
for i, chunk in enumerate(chunks_no[:3]):
    print(f"  块{i+1} 结尾: ...{chunk[-50:]}")

print("\n有 overlap:")
print(f"  块数: {len(chunks_with)}")
for i, chunk in enumerate(chunks_with[:3]):
    print(f"  块{i+1} 结尾: ...{chunk[-50:]}")
```

**思考**：
- 有 overlap 时，相邻块之间有什么关系？
- overlap 对检索有什么帮助？
- 代价是什么（块数增加了多少）？

---

### 任务 4：测试不同切分策略

**代码模板**：

```python
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

with open("test_doc.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 策略 1: 固定字符切分
char_splitter = CharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separator="\n",  # 按换行切分
)

# 策略 2: 递归字符切分（推荐）
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=20,
    separators=["\n\n", "\n", "。", "！", "？", " ", ""],  # 中文优先按段落、句子
)

char_chunks = char_splitter.split_text(text)
recursive_chunks = recursive_splitter.split_text(text)

print(f"固定字符切分: {len(char_chunks)} 块")
print(f"递归字符切分: {len(recursive_chunks)} 块")

print("\n递归切分的第一块:")
print(recursive_chunks[0])
```

---

## 今日输出

完成以下笔记（可以用 AI 辅助整理）：

### 笔记模板

```markdown
# 文本切分（Chunking）学习笔记

## 1. 为什么要切分？
[用 2-3 句话总结]

## 2. chunk_size 的选择
- 太小的问题：
- 太大的问题：
- 我的经验：对于 [X] 类型的文档，推荐 [Y]

## 3. chunk_overlap 的作用
[用 1-2 句话总结]

## 4. 切分策略对比
| 策略 | 我的使用场景 |
|-----|-------------|
| 固定长度 | |
| 递归切分 | |

## 5. 我遇到的坑
[记录实验中发现的问题]

## 6. 还有的疑问
[列出还没搞懂的问题]
```

---

## 延伸阅读（可选）

- [LangChain Text Splitters 文档](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [LlamaIndex 分块指南](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/)

---

## 完成检查

- [ ] 回答了 4 个核心问题
- [ ] 运行了 chunk_size 对比实验
- [ ] 运行了 overlap 对比实验
- [ ] 完成了今日笔记
- [ ] 记录了还有的疑问

---

*Day 4 计划生成日期：2026-03-27*
