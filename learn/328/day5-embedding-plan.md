# Day 5: Embedding 深入学习

> 日期：2026-03-28
> 学习主题：理解 Embedding 的原理和实践

---

## 一、任务清单

### 理论理解（约 1.5 小时）

- [X] 理解 Embedding 是什么，为什么能把文字变成数字
- [X] 理解向量的维度是什么意思
- [X] 理解 cosine similarity 在算什么
- [X] 了解 OpenAI text-embedding-3-small 和 large 的区别
- [X] 了解其他 Embedding 模型（BGE, M3, Voyage）

### 实践任务（约 1.5 小时）

- [ ] 打印几个文本的向量，观察数值特征
- [ ] 计算几对文本的相似度，感受"语义相似"
- [ ] 尝试不同类型文本的相似度对比（近义词、反义词、无关词）

### 输出任务（约 1 小时）

- [ ] 整理 Embedding 核心概念笔记
- [ ] 保存实践代码和运行结果
- [ ] 记录 3-5 个不理解或有疑问的地方

---

## 二、学习内容与方法

### 1. Embedding 是什么？

**核心思想**：把文字转换成一串数字（向量），让计算机能"理解"文字的含义。语义相近的词，向量也相近。

**学习方法**：

```
让 AI 解释：
"用 12 岁小孩能懂的话解释 Embedding，并给一个 Python 代码示例"
```

**关键理解点**：

- 文字 → 数字的映射
- 语义相近 = 向量在空间中距离近
- 向量是高维空间中的一个点

---

### 2. 向量的维度

**核心问题**：为什么 OpenAI 的 embedding 是 1536 维？

**学习方法**：

- 打印一个向量的 shape，看维度
- 思考：维度越高越好吗？代价是什么？

---

### 3. Cosine Similarity（余弦相似度）

**核心思想**：计算两个向量的夹角，夹角越小越相似。

**公式**：

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**学习方法**：

```python
# 让 AI 帮你写代码计算以下文本对的相似度：
texts = [
    "我喜欢吃苹果",
    "我爱吃苹果",
    "今天天气很好",
    "机器学习很有趣"
]
```

**预期结果**：

- "我喜欢吃苹果" vs "我爱吃苹果" → 相似度应该很高（>0.9）
- "我喜欢吃苹果" vs "今天天气很好" → 相似度应该很低（<0.5）

---

### 4. Embedding 模型对比

| 模型                   | 维度 | 特点       | 适用场景   |
| ---------------------- | ---- | ---------- | ---------- |
| text-embedding-3-small | 1536 | 便宜、快速 | 日常使用   |
| text-embedding-3-large | 3072 | 更精准     | 高质量需求 |
| BGE (中文)             | 768  | 中文效果好 | 中文场景   |
| M3 (多语言)            | 1024 | 多语言支持 | 跨语言场景 |

---

### 5. 实践代码模板

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embedding(text):
    """获取文本的向量表示"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(v1, v2):
    """计算两个向量的余弦相似度"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# 实践任务
texts = [
    "我喜欢吃苹果",
    "我爱吃苹果",
    "苹果是一种水果",
    "今天天气很好"
]

# 1. 打印向量
for text in texts:
    emb = get_embedding(text)
    print(f"文本: {text}")
    print(f"向量维度: {len(emb)}")
    print(f"向量前5个值: {emb[:5]}")
    print("---")

# 2. 计算相似度
emb_list = [get_embedding(t) for t in texts]
print("相似度矩阵:")
for i, t1 in enumerate(texts):
    for j, t2 in enumerate(texts):
        if i < j:
            sim = cosine_similarity(emb_list[i], emb_list[j])
            print(f"{t1} <-> {t2}: {sim:.4f}")
```

---

## 三、输出内容

### 1. 概念笔记（保存位置）

- 文件：`/Volumes/H/SpeakCube/opreation/learn/notes/embedding-notes.md`

### 2. 实践代码（保存位置）

- 文件：`/Volumes/H/SpeakCube/opreation/learn/code/embedding-practice.py`

### 3. 运行结果（保存位置）

- 文件：`/Volumes/H/SpeakCube/opreation/learn/code/embedding-results.txt`

### 4. 疑问记录

在笔记末尾记录今天不理解的地方，方便后续追问。

---

## 四、学习提示词

### 理解概念

```
我想学习 RAG 中的 Embedding。请：

1. 用 12 岁小孩能懂的话解释核心思想
2. 给我一个可运行的 Python 代码示例
3. 解释每一行代码在做什么
4. 告诉我这个概念在整个 RAG 系统中的位置
5. 列出相关的 3-5 个重要概念
6. 指出初学者容易误解的地方
```

### 验证理解

```
我对 Embedding 的理解是：
[你的理解...]

请：
1. 指出我理解错误或不完整的地方
2. 用反例挑战我的理解
3. 提出延伸问题测试我的掌握程度
```

---

## 五、时间安排建议

| 时段 | 任务                          | 时长 |
| ---- | ----------------------------- | ---- |
| 上午 | 理论学习：理解 Embedding 概念 | 1h   |
| 上午 | 实践：打印向量、观察数值      | 0.5h |
| 下午 | 实践：计算相似度、对比效果    | 1h   |
| 晚上 | 整理笔记、记录疑问            | 0.5h |

---

*计划创建时间：2026-03-28*
