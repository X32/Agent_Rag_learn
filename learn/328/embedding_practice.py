"""
Day 6: Embedding 实践练习
目标：通过动手实验理解向量、维度、相似度
"""

import os
from openai import OpenAI
import numpy as np

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    """获取文本的 embedding 向量"""
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def cosine_similarity(vec1: list, vec2: list) -> float:
    """
    计算余弦相似度

    公式: cos(θ) = (A·B) / (||A|| * ||B||)

    几何意义: 两个向量之间的夹角
    - 1.0 = 完全相同方向
    - 0.0 = 垂直（无关）
    - -1.0 = 完全相反
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)  # 点积
    norm1 = np.linalg.norm(vec1)      # 向量长度
    norm2 = np.linalg.norm(vec2)

    return dot_product / (norm1 * norm2)

# ============================================
# 实验一：观察向量
# ============================================
print("=" * 50)
print("实验一：观察向量数值")
print("=" * 50)

# 语义相关的句子
related_sentences = [
    "我喜欢吃苹果",
    "我喜欢吃水果",
    "苹果是一种美味的水果"
]

# 语义不相关的句子
unrelated_sentences = [
    "我喜欢吃苹果",
    "今天股市大跌",
    "Python 是一种编程语言"
]

print("\n📌 获取第一个句子的向量...")
vec = get_embedding(related_sentences[0])
print(f"向量维度: {len(vec)}")
print(f"向量前 10 个值: {vec[:10]}")
print(f"向量最大值: {max(vec):.4f}")
print(f"向量最小值: {min(vec):.4f}")
print(f"向量平均值: {np.mean(vec):.4f}")

# ============================================
# 实验二：计算相似度
# ============================================
print("\n" + "=" * 50)
print("实验二：语义相似度对比")
print("=" * 50)

print("\n📌 语义相关的句子对:")
for i in range(len(related_sentences)):
    for j in range(i + 1, len(related_sentences)):
        vec1 = get_embedding(related_sentences[i])
        vec2 = get_embedding(related_sentences[j])
        sim = cosine_similarity(vec1, vec2)
        print(f"\n  句子A: {related_sentences[i]}")
        print(f"  句子B: {related_sentences[j]}")
        print(f"  相似度: {sim:.4f}")

print("\n" + "-" * 50)
print("\n📌 语义不相关的句子对:")
for i in range(len(unrelated_sentences)):
    for j in range(i + 1, len(unrelated_sentences)):
        vec1 = get_embedding(unrelated_sentences[i])
        vec2 = get_embedding(unrelated_sentences[j])
        sim = cosine_similarity(vec1, vec2)
        print(f"\n  句子A: {unrelated_sentences[i]}")
        print(f"  句子B: {unrelated_sentences[j]}")
        print(f"  相似度: {sim:.4f}")

# ============================================
# 实验三：Small vs Large 模型对比
# ============================================
print("\n" + "=" * 50)
print("实验三：text-embedding-3-small vs large")
print("=" * 50)

test_text = "这是一段测试文本，用来对比不同模型的效果。"

vec_small = get_embedding(test_text, "text-embedding-3-small")
vec_large = get_embedding(test_text, "text-embedding-3-large")

print(f"\nSmall 模型:")
print(f"  维度: {len(vec_small)}")
print(f"  价格: $0.02 / 1M tokens")

print(f"\nLarge 模型:")
print(f"  维度: {len(vec_large)}")
print(f"  价格: $0.13 / 1M tokens")

print(f"\n💡 选择建议:")
print(f"  - 小项目/原型 → Small (便宜、够用)")
print(f"  - 生产环境/高精度需求 → Large (更准确)")

# ============================================
# 实验四：有趣的知识
# ============================================
print("\n" + "=" * 50)
print("实验四：语义运算（类比）")
print("=" * 50)

print("\n📌 经典例子：国王 - 男人 + 女人 ≈ 女王")
print("（这个实验需要英文，因为中文模型可能不支持这种类比）")

words = {
    "king": get_embedding("king"),
    "man": get_embedding("man"),
    "woman": get_embedding("woman"),
    "queen": get_embedding("queen")
}

# 向量运算: king - man + woman
result = np.array(words["king"]) - np.array(words["man"]) + np.array(words["woman"])
result = result.tolist()

# 计算结果与 queen 的相似度
sim_to_queen = cosine_similarity(result, words["queen"])
sim_to_king = cosine_similarity(result, words["king"])

print(f"\n  'king - man + woman' 与 'queen' 的相似度: {sim_to_queen:.4f}")
print(f"  'king - man + woman' 与 'king' 的相似度: {sim_to_king:.4f}")

print("\n" + "=" * 50)
print("✅ 实验完成！")
print("=" * 50)
print("\n📝 今日思考题:")
print("1. 为什么语义相关的句子相似度更高？")
print("2. 向量维度越高越好吗？为什么？")
print("3. cosine similarity 能到 -1 吗？什么情况下会到？")

# ============================================
# 实验五：RAG 检索模拟
# ============================================
print("\n" + "=" * 50)
print("实验五：RAG 检索 - 如何找到最相关文档")
print("=" * 50)

# 模拟文档库
document_chunks = [
    "苹果是一种常见的水果，富含维生素 C 和膳食纤维。",
    "苹果公司发布了新款 iPhone，搭载 A17 芯片。",
    "小红帽是一个著名的童话故事。",
    "苹果树喜欢温和的气候，需要充足的阳光。",
    "特斯拉股价今天上涨了 5%。",
    "吃苹果对心脏健康有益，可以降低胆固醇。",
]

# 用户问题
query = "吃苹果有什么好处？"

print(f"\n📌 用户问题：{query}")
print(f"\n📌 文档库 ({len(document_chunks)} 个片段):")
for i, doc in enumerate(document_chunks, 1):
    print(f"  [{i}] {doc}")

# 1. 将问题转成向量
query_vec = get_embedding(query)

# 2. 计算与每个文档的相似度
print("\n📌 计算相似度...")
results = []
for i, doc in enumerate(document_chunks, 1):
    doc_vec = get_embedding(doc)
    sim = cosine_similarity(query_vec, doc_vec)
    results.append((i, doc, sim))
    print(f"  文档 [{i}]: 相似度 = {sim:.4f}")

# 3. 排序，取 Top-3
results.sort(key=lambda x: x[2], reverse=True)
top_k = results[:3]

print(f"\n📌 Top-3 最相关文档 (将用于生成答案):")
for rank, (idx, doc, sim) in enumerate(top_k, 1):
    print(f"\n  【第{rank}名】相似度 {sim:.4f}")
    print(f"  内容：{doc}")

print("\n💡 RAG 检索核心思想:")
print("  1. 问题 → 向量")
print("  2. 计算与所有文档的余弦相似度")
print("  3. 返回 Top-K 最相似的文档")
print("  4. 将文档 + 问题一起发给 LLM 生成答案")

# ============================================
# 实验六：chunk_overlap 演示
# ============================================
print("\n" + "=" * 50)
print("实验六：理解 chunk_overlap 的作用")
print("=" * 50)

def chunk_text_without_overlap(text: str, chunk_size: int) -> list:
    """无重叠切分"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def chunk_text_with_overlap(text: str, chunk_size: int, overlap: int) -> list:
    """有重叠切分"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

# 示例文本
sample_text = "乔布斯在 2007 年发布了第一代 iPhone。这款产品彻底改变了智能手机行业。苹果的股价随后大幅上涨。"

print(f"\n📌 原文：{sample_text}")
print(f"\n📌 无 overlap 切分 (chunk_size=20):")
chunks_no_overlap = chunk_text_without_overlap(sample_text, 20)
for i, chunk in enumerate(chunks_no_overlap, 1):
    print(f"  块{i}: [{chunk}]")

print(f"\n📌 有 overlap 切分 (chunk_size=20, overlap=5):")
chunks_with_overlap = chunk_text_with_overlap(sample_text, 20, 5)
for i, chunk in enumerate(chunks_with_overlap, 1):
    print(f"  块{i}: [{chunk}]")

print("\n💡 观察:")
print("  - 无 overlap: 切分处可能切断语义")
print("  - 有 overlap: 重叠部分保留上下文，检索时不容易丢失信息")

# 演示 overlap 如何帮助检索
print("\n📌 检索场景演示:")
query = "iPhone 什么时候发布？"
query_vec = get_embedding(query)

print("\n  用无 overlap 的块检索:")
for i, chunk in enumerate(chunks_no_overlap, 1):
    chunk_vec = get_embedding(chunk)
    sim = cosine_similarity(query_vec, chunk_vec)
    print(f"    块{i}: 相似度 = {sim:.4f}")

print("\n  用有 overlap 的块检索:")
for i, chunk in enumerate(chunks_with_overlap, 1):
    chunk_vec = get_embedding(chunk)
    sim = cosine_similarity(query_vec, chunk_vec)
    print(f"    块{i}: 相似度 = {sim:.4f}")
