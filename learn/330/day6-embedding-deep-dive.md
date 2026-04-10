# Day 6：递归追问 - Embedding 深入

> 今天的目标：彻底理解 Embedding 的本质，从原理到实践

---

## 学习目标

- [ ] 理解 Embedding 是什么，为什么能把文字变成数字
- [ ] 理解向量的维度含义
- [ ] 掌握 cosine similarity 的计算原理
- [ ] 对比不同 Embedding 模型的差异
- [ ] 通过实践感受"语义相似"

---

## 时间安排（3-4 小时）

| 时间段 | 内容 | 类型 |
| :----- | :--- | :--- |
| 30min | 核心概念学习 | 主动探索 |
| 60min | 代码实践 - 观察向量 | 项目驱动 |
| 45min | 递归追问 | 主动探索 |
| 45min | 对比实验 | 项目驱动 |
| 30min | 输出总结 | 输出反馈 |

---

## Part 1：核心概念学习（30 分钟）

### 1.1 Embedding 是什么？

**用 12 岁小孩能懂的话解释**：

想象你有一堆乐高积木，每块积木代表一个词。Embedding 就是给每块积木贴上一个"坐标标签"，比如 (3, 5, 7)。意思相近的词（比如"猫"和"狗"），它们的坐标就会很接近；意思差得远的词（比如"猫"和"飞机"），坐标就会离得很远。

这样，计算机虽然不懂文字，但可以通过计算坐标的距离，知道哪些词意思相近！

**技术定义**：
- Embedding 是一个将离散对象（如单词、句子）映射到连续向量空间的函数
- 这个向量空间是低维的（通常 768、1536 维），但能捕捉语义信息
- 向量空间中的"距离"对应语义上的"相似度"

### 1.2 向量的维度是什么意思？

- **维度** = 向量的长度
- 例如：1536 维的向量 = `[0.1, -0.5, 0.8, ..., 0.3]`（1536 个数字）
- 每个维度可以理解为文本的某个"特征"或"属性"
  - 某些维度可能编码"是否为动物"
  - 某些维度可能编码"是否与技术相关"
  - 某些维度可能编码"情感倾向"
- **注意**：人类无法直接理解高维空间，但模型通过这些维度捕捉语义

### 1.3 Cosine Similarity（余弦相似度）

**定义**：衡量两个向量方向的相似程度，而不是距离

**公式**：
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
                        = Σ(Ai × Bi) / (√ΣAi² × √ΣBi²)
```

**取值范围**：
- `1` = 方向完全相同（语义非常相似）
- `0` = 正交（无关）
- `-1` = 方向完全相反（语义相反）

**为什么用余弦相似度而不是欧氏距离？**
- 余弦相似度关注"方向"，对向量的绝对大小不敏感
- 文本长度不同但语义相似时，余弦相似度更鲁棒

---

## Part 2：代码实践 - 观察向量（60 分钟）

### 2.1 打印向量，观察数值

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def get_embedding(text, model="text-embedding-3-small"):
    """获取文本的 embedding"""
    text = text.replace("\n", " ")
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding

# 实践任务 1：打印几个简单文本的向量
texts = ["猫", "狗", "飞机", "happy", "sad"]

for text in texts:
    embedding = get_embedding(text)
    print(f"\n'{text}' 的向量:")
    print(f"  维度：{len(embedding)}")
    print(f"  前 10 个值：{embedding[:10]}")
    print(f"  最大值：{max(embedding):.4f}")
    print(f"  最小值：{min(embedding):.4f}")
    print(f"  平均值：{sum(embedding)/len(embedding):.4f}")
```

**观察任务**：
- [ ] 向量的值大多在什么范围？
- [ ] 不同文本的向量看起来有什么特点？
- [ ] 单字和句子的向量有什么不同？

### 2.2 计算相似度，感受"语义相似"

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(text1, text2):
    """计算两个文本的余弦相似度"""
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)

    # 转为 numpy 数组
    vec1 = np.array(emb1).reshape(1, -1)
    vec2 = np.array(emb2).reshape(1, -1)

    # 计算余弦相似度
    similarity = cosine_similarity(vec1, vec2)[0][0]
    return similarity

# 实践任务 2：计算并比较以下文本对的相似度
pairs = [
    ("猫", "狗"),           # 都是动物
    ("猫", "飞机"),         # 无关
    ("happy", "glad"),      # 近义词
    ("happy", "sad"),       # 反义词
    ("今天天气真好", "今天心情不错"),  # 语义相近的中文
    ("苹果", "水果"),       # 上下位关系
    ("我喜欢编程", "I love coding"),   # 跨语言
]

print("文本对相似度：\n")
for text1, text2 in pairs:
    sim = calculate_similarity(text1, text2)
    print(f"'{text1}' vs '{text2}': {sim:.4f}")
```

**思考任务**：
- [ ] 哪些文本对的相似度高？为什么？
- [ ] 反义词的相似度是正还是负？
- [ ] 跨语言的语义相似度如何？

### 2.3 可视化（可选）

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# 获取多个文本的向量
texts = ["猫", "狗", "鸟", "鱼", "飞机", "汽车", "火车", "苹果", "香蕉", "电脑"]
embeddings = [get_embedding(text) for text in texts]

# 用 PCA 降到 2 维
pca = PCA(n_components=2)
reduced = pca.fit_transform(embeddings)

# 画图
plt.figure(figsize=(10, 8))
plt.scatter(reduced[:, 0], reduced[:, 1])
for i, text in enumerate(texts):
    plt.annotate(text, (reduced[i, 0], reduced[i, 1]))
plt.title("文本 Embedding 的 PCA 降维可视化")
plt.savefig("embedding_visualization.png")
print("可视化已保存到 embedding_visualization.png")
```

---

## Part 3：递归追问（45 分钟）

### 核心问题清单

用以下问题向 AI 提问，记录答案：

**问题 1：为什么需要 Embedding？**
```
为什么不能直接用关键词匹配，而要用 Embedding？
关键词匹配有什么局限性？
```

**问题 2：Embedding 模型是如何训练的？**
```
text-embedding-3-small 是怎么训练出来的？
训练数据是什么？
损失函数是什么？
```

**问题 3：向量归一化**
```
为什么很多 Embedding 会被归一化到单位圆上？
归一化后 cosine similarity 怎么计算更简单？
```

**问题 4：不同模型的差异**
```
OpenAI 的 text-embedding-3-small 和 large 有什么区别？
- 维度？
- 训练数据？
- 性能差异？
- 价格差异？

其他常用 Embedding 模型：
- BGE (BAAI General Embedding)
- M3 (Multilingual, Multimodal, Multi-task)
- Voyage AI 的模型
各有什么特点？
```

**问题 5：多语言支持**
```
Embedding 模型如何处理多语言？
中文和英文的向量在同一个空间吗？
为什么跨语言相似度能工作？
```

**问题 6：上下文长度限制**
```
Embedding 模型有 token 限制吗？
超过限制怎么办？
长文本的 Embedding 质量会下降吗？
```

---

## Part 4：对比实验（45 分钟）

### 4.1 模型对比实验

```python
MODELS = [
    "text-embedding-3-small",   # OpenAI 小型
    "text-embedding-3-large",   # OpenAI 大型
]

# 测试文本
test_texts = [
    "猫是一种可爱的动物",
    "狗是人类忠实的朋友",
    "飞机是一种交通工具",
    "今天心情很好",
]

# 对比不同模型的输出
for model in MODELS:
    print(f"\n{'='*50}")
    print(f"模型：{model}")
    print(f"{'='*50}")

    embeddings = []
    for text in test_texts:
        emb = get_embedding(text, model=model)
        embeddings.append(emb)
        print(f"\n'{text}'")
        print(f"  维度：{len(emb)}")

    # 计算相似度矩阵
    emb_array = np.array(embeddings)
    sim_matrix = cosine_similarity(emb_array)

    print("\n相似度矩阵：")
    print(sim_matrix)
```

### 4.2 成本 - 性能权衡分析

| 模型 | 维度 | 价格 ($/1K tokens) | 适合场景 |
| :--- | :--- | :--- | :--- |
| text-embedding-3-small | 1536 | $0.00002 | 原型、成本敏感 |
| text-embedding-3-large | 3072 | $0.00013 | 高精度需求 |
| BGE-M3 | 1024 | 开源免费 | 本地部署 |

**思考**：你的项目应该选哪个模型？为什么？

---

## Part 5：输出反馈（30 分钟）

### 5.1 知识检查

向 AI 提出以下问题，检查自己的理解：

```
请测试我对 Embedding 的理解程度：

1. 请用简单的语言解释 Embedding 是什么
2. Cosine Similarity 和欧氏距离有什么区别？
3. 为什么向量维度高的 Embedding 通常效果更好？
4. 什么情况下会选择 smaller model 而不是 larger model？

请先让我自己回答，然后指出我理解错误或不完整的地方。
```

### 5.2 今日总结

写一段 200-300 字的总结，回答以下问题：

1. 今天学到的最重要的 3 个概念是什么？
2. 哪个概念最难理解？为什么？
3. 你对 Embedding 的理解有什么变化？
4. 还有什么疑问想进一步了解？

**模板**：
```markdown
## Day 6 学习总结

### 最重要的 3 个概念
1. ...
2. ...
3. ...

### 最难理解的概念
...

### 理解的变化
之前我认为... 现在我理解...

### 遗留问题
...
```

---

## 检查清单

完成今天的学习后，确认以下事项：

- [ ] 能用自己的话解释 Embedding 是什么
- [ ] 能解释 cosine similarity 的计算和意义
- [ ] 实际运行过代码，看过向量输出
- [ ] 计算过文本对的相似度，有直观感受
- [ ] 了解至少 3 种不同的 Embedding 模型
- [ ] 知道如何根据场景选择 Embedding 模型
- [ ] 完成了今日总结

---

## 延伸学习（可选）

### 推荐阅读

- [ ] [The Illustrated Embedding](https://jalammar.github.io/illustrated-word2vec/) - 可视化理解 Embedding
- [ ] [Sentence-BERT 论文](https://arxiv.org/abs/1908.10084) - 句子级别的 Embedding

### 代码探索

- [ ] 查看 LangChain 中 OpenAIEmbeddings 的源码
- [ ] 尝试用 HuggingFace 运行开源的 BGE 模型

---

*第六天计划完成日期：2026-03-30*
