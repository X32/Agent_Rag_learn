"""
Embedding 演示代码 - 把文字变成数字坐标
============================================

想象一下：
- 每个词都有一个"GPS坐标"（一串数字）
- 意思相近的词，坐标就靠近
- 意思不同的词，坐标就离得远

这就是 Embedding（嵌入）！
"""

# sentence_transformers: HuggingFace 的嵌入模型库
# 它可以把文字转换成高维向量（一串数字），用于计算文本相似度
from sentence_transformers import SentenceTransformer

# numpy: Python 的科学计算库
# 这里主要用于向量运算：点积、求范数（向量长度）
import numpy as np

# ============ 模型加载部分 ============
# 加载一个轻量级的中文/英文模型
# SentenceTransformer 会自动从 HuggingFace Hub 下载模型（首次需要网络）
print("🔄 正在加载模型，请稍等...")

# 'paraphrase-multilingual-MiniLM-L12-v2' 模型说明：
# - paraphrase: 专门针对"语义相似度"任务训练
# - multilingual: 支持 50+ 种语言（包括中文）
# - MiniLM-L12-v2: 轻量级版本，12层Transformer，速度快、体积小
# - 输出向量维度: 384（每个文本变成384个数字）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print("✅ 模型加载完成！\n")


def text_to_coordinates(text: str) -> list:
    """
    把文字变成数字坐标（Embedding）

    就像给文字一个 GPS 位置！

    参数:
        text: 输入的文本字符串

    返回:
        embedding: 一个 numpy 数组，包含 384 个浮点数
                   这些数字代表文本在高维空间中的"位置"
    """
    # model.encode() 是核心方法：
    # 1. 对文本进行分词（切成小片段）
    # 2. 通过 Transformer 神经网络处理
    # 3. 输出一个固定长度的向量（384维）
    embedding = model.encode(text)

    return embedding  # 返回嵌入向量（numpy 数组）


def how_similar(coord1: list, coord2: list) -> float:
    """
    计算两个坐标的相似度（0 到 1 之间）

    1.0 = 完全一样
    0.0 = 完全不同

    参数:
        coord1: 第一个文本的嵌入向量
        coord2: 第二个文本的嵌入向量

    返回:
        similarity: 余弦相似度值，范围 [-1, 1]，通常为 [0, 1]
    """
    # 余弦相似度公式: cos(θ) = (A·B) / (|A| × |B|)
    # 数学原理解释：
    # - np.dot(coord1, coord2): 向量点积，计算两个向量的"方向一致性"
    # - np.linalg.norm(coord1): 向量的模（长度），即 √(x1² + x2² + ... + xn²)
    # - 除以两个模的乘积: 归一化，消除向量长度的影响
    # 结果含义：
    # - 1.0: 两向量方向完全相同（语义相同）
    # - 0.0: 两向量垂直（语义无关）
    # - -1.0: 两向量方向相反（语义相反，但在嵌入空间中很少出现）
    similarity = np.dot(coord1, coord2) / (np.linalg.norm(coord1) * np.linalg.norm(coord2))

    return similarity  # 返回相似度分数


def print_similarity(word1: str, word2: str):
    """
    打印两个词的相似度，用 emoji 直观展示

    参数:
        word1: 第一个词/句子
        word2: 第二个词/句子
    """
    # 步骤1: 把文字转换成向量坐标
    coord1 = text_to_coordinates(word1)  # 获取第一个词的嵌入向量
    coord2 = text_to_coordinates(word2)  # 获取第二个词的嵌入向量
    #打印向量
    print(f"{word1} 的坐标: {coord1}")
    print(f"{word2} 的坐标: {coord2}\n")
    # 步骤2: 计算两个向量的相似度
    similarity = how_similar(coord1, coord2)  # 使用余弦相似度计算

    # 步骤3: 根据相似度分数选择对应的 emoji
    # 使用条件判断来可视化相似程度
    if similarity > 0.8:
        # 相似度 > 80%: 非常相似（绿色圆圈）
        emoji = "🟢"
    elif similarity > 0.5:
        # 相似度在 50%-80% 之间: 有点相似（黄色圆圈）
        emoji = "🟡"
    else:
        # 相似度 < 50%: 不太相似（红色圆圈）
        emoji = "🔴"

    # 步骤4: 格式化输出结果
    # f-string 格式化说明:
    # - {similarity:.2%}: 将小数转为百分比，保留2位小数
    #   例如: 0.856 -> 85.60%
    print(f"{emoji} \"{word1}\" vs \"{word2}\"")
    print(f"   相似度: {similarity:.2%}\n")


# ============ 主程序开始 ============
# if __name__ == "__main__": 是 Python 的标准入口点写法
# 含义: 只有当这个文件被直接运行时，下面的代码才会执行
# 如果这个文件被 import 到其他文件，下面的代码不会执行
if __name__ == "__main__":
    # 打印程序标题
    print("=" * 50)  # 打印50个等号作为分隔线
    print("🎯 Embedding 演示：文字的 GPS 坐标")
    print("=" * 50)

    # ============ 示例 1: 查看嵌入向量长什么样 ============
    print("\n📝 示例 1：一个词的坐标长什么样？")
    print("-" * 40)  # 打印40个短横线作为分隔线

    word = "小狗"  # 要分析的词语
    coord = text_to_coordinates(word)  # 调用函数，获取嵌入向量

    print(f"词语: \"{word}\"")
    # coord[:10]: 取前10个数字（切片操作）
    # .round(3): 保留3位小数，便于阅读
    # .tolist(): 将 numpy 数组转为 Python 列表，方便显示
    print(f"坐标（前10个数字）: {coord[:10].round(3).tolist()}")
    print(f"向量维度: {coord.shape}")  # 显示 numpy 数组的 shape，如 (384,)
    print(f"向量长度: {len(coord)} 个数字")  # 显示向量维度（384）

    # ============ 示例 2: 词语相似度比较 ============
    print('\n📝 示例 2：哪些词是"朋友"？')
    print("-" * 40)

    # --- 相似的词（预期结果：绿色/黄色）---
    print_similarity("小狗", "小猫")      # 都是宠物 -> 高相似度
    print_similarity("苹果", "香蕉")      # 都是水果 -> 高相似度
    print_similarity("开心", "快乐")      # 意思相近 -> 高相似度

    # --- 不相似的词（预期结果：红色）---
    print_similarity("小狗", "汽车")      # 完全不同类别 -> 低相似度
    print_similarity("香蕉", "电脑")      # 完全不同类别 -> 低相似度
    # ============ 示例 3: 句子级别的相似度 ============
    print("\n📝 示例 3：句子也能变成坐标！")
    print("-" * 40)

    # 句子的嵌入是对整个句子的语义理解
    # 不只是关键词匹配，而是理解整句话的意思
    print_similarity("我喜欢吃苹果", "我爱吃水果")    # 语义相近 -> 高相似度
    print_similarity("我喜欢吃苹果", "今天天气很好")  # 语义无关 -> 低相似度

    # ============ 总结输出 ============
    print("\n" + "=" * 50)
    print("🎓 总结：")
    print("   Embedding 把文字变成数字坐标")
    print("   意思相近的文字，坐标就靠近")
    print('   这样电脑就能"理解"文字的意思了！')
    print("=" * 50)
