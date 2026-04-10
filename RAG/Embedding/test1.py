"""
Embedding 入门示例 - 使用免费的 HuggingFace 模型
============================================================
免费模型：paraphrase-multilingual-MiniLM-L12-v2
- 支持中文和英文
- 384 维向量
- 无需 API Key，完全免费
"""

from sentence_transformers import SentenceTransformer
import numpy as np

# 加载模型（首次运行会自动下载）
print("正在加载模型...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("模型加载完成！\n")


def get_embedding(text: str) -> np.ndarray:
    """获取文本的嵌入向量"""
    return model.encode(text)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """计算两个向量的余弦相似度"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


# 实践任务 1：查看几个词的向量
texts = ["猫", "狗", "飞机", "happy", "sad"]

print("=" * 50)
print("任务 1：词语的向量表示")
print("=" * 50)

for text in texts:
    embedding = get_embedding(text)
    print(f"\n'{text}' 的向量:")
    print(f"  维度：{len(embedding)}")
    print(f"  前 10 个值：{embedding[:10].round(3).tolist()}")
    print(f"  最大值：{max(embedding):.4f}")
    print(f"  最小值：{min(embedding):.4f}")
    print(f"  平均值：{sum(embedding)/len(embedding):.4f}")

# 实践任务 2：计算词与词之间的相似度
print("\n" + "=" * 50)
print("任务 2：词语相似度比较")
print("=" * 50)

pairs = [
    ("猫", "狗"),       # 都是宠物
    ("猫", "飞机"),     # 不相关
    ("happy", "sad"),   # 反义词
    ("苹果", "香蕉"),   # 都是水果
    ("中国", "北京"),   # 包含关系
]

for word1, word2 in pairs:
    emb1 = get_embedding(word1)
    emb2 = get_embedding(word2)
    sim = cosine_similarity(emb1, emb2)

    # 根据相似度显示 emoji
    if sim > 0.8:
        emoji = "🟢 非常相似"
    elif sim > 0.5:
        emoji = "🟡 有点相似"
    else:
        emoji = "🔴 不太相似"

    print(f"{emoji} | \"{word1}\" vs \"{word2}\": {sim:.4f}")

# 实践任务 3：句子级别的相似度
print("\n" + "=" * 50)
print("任务 3：句子相似度")
print("=" * 50)

sentences = [
    ("我喜欢吃苹果", "我爱吃水果"),
    ("今天天气真好", "外面下雨了"),
    ("Python 很有趣", "Java 也不错"),
]

for s1, s2 in sentences:
    emb1 = get_embedding(s1)
    emb2 = get_embedding(s2)
    sim = cosine_similarity(emb1, emb2)
    print(f"\"{s1}\" vs \"{s2}\": {sim:.4f}")

print("\n" + "=" * 50)
print("总结：Embedding 让文字变成可以计算相似度的数字坐标！")
print("=" * 50)
