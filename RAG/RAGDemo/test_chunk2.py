from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings


text = """
# 机器学习 第一章：机器学习基础入门
## 1.1 什么是机器学习
机器学习是**人工智能**的核心分支，它不依赖人工硬编码规则，而是让计算机**从数据中自动学习规律**，并利用规律对未知数据进行预测、分类或决策。

简单理解：
传统编程 = 人写规则 + 数据 → 结果
机器学习 = 数据 + 结果 → 计算机自动学习出规则

## 1.2 机器学习的核心要素
- **数据**：学习的基础，分为特征（输入）和标签（输出）
- **模型**：学习到的规律/函数映射
- **算法**：训练模型、优化参数的方法
- **目标**：预测、分类、聚类、降维、生成等任务

## 1.3 机器学习三大经典分类
### 1. 监督学习（Supervised Learning）
有**标签/标准答案**，模型学习输入到输出的映射。
- 分类：输出离散值（如判断图片是猫/狗、垃圾邮件识别）
- 回归：输出连续值（如房价预测、气温预测）

### 2. 无监督学习（Unsupervised Learning）
无标签，模型自动发现数据内在结构。
- 聚类：把相似样本归为一类（如用户分群、商品推荐）
- 降维：减少特征数量，保留核心信息（如PCA）

### 3. 强化学习（Reinforcement Learning）
智能体通过与环境交互，不断试错学习最优策略，追求长期奖励最大化（如AlphaGo、机器人控制）

## 1.4 机器学习基本流程
1. 问题定义：明确任务（分类/回归/聚类等）
2. 数据收集与预处理：清洗、归一化、划分训练集/测试集
3. 模型选择：选择合适算法（线性回归、决策树、神经网络等）
4. 模型训练：用训练数据拟合参数
5. 模型评估：用测试集验证效果（准确率、MSE等）
6. 模型优化与部署：调参、改进，上线使用

## 1.5 常见基础概念
- **过拟合**：模型在训练集表现极好，在测试集表现差
- **欠拟合**：模型过于简单，训练和测试效果都差
- **泛化能力**：模型对新数据的预测能力
- **训练集/验证集/测试集**：分别用于训练、调参、最终评估

---

如果你需要的是**某本教材（如周志华《机器学习》西瓜书、李航《统计学习方法》）的第一章完整笔记/重点总结**，告诉我书名，我可以按对应教材精确整理。
"""

# 使用语义切分器
splitter = SemanticChunker(
    embeddings=HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ),
    breakpoint_threshold_type="percentile",  # 或 "gradient", "absolute"
    breakpoint_threshold_amount=95
)

chunks = splitter.split_text(text)
print(chunks)