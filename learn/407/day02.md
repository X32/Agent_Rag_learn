# Week 2 Day 2：向量数据库进阶与选型

> 理解索引原理，选择合适的工具

---

## 今日目标

- [X] 理解 FAISS 进阶索引类型（IVF、HNSW）
- [X] 了解主流向量数据库的特点
- [X] 能根据场景选择合适的工具
- [X] 完成学习打卡

---

## 一、核心问题（30 分钟）

### 1.1 复习：昨天的 FAISS 有什么问题？

**回忆一下**：昨天用的 `IndexFlatL2` 或 `IndexFlatIP` 是什么索引？

```
答案：扁平索引（Flat Index）

原理：存储所有向量，检索时遍历比较
优点：100% 准确（不会漏掉任何可能的结果）
缺点：数据量大时慢（还是要遍历）
```

**问题**：如果有 100 万个向量，会怎样？

```
IndexFlatL2：要计算 100 万次相似度 → 慢
需要：一种"大概定位 + 精细搜索"的方法
```

### 1.2 IVF 索引：倒排文件索引

**核心思想**：先分类，再搜索

```
想象图书馆的书：
┌─────────────────────────────────────────────────────────────┐
│  没有 IVF：一本本翻 → 找到跟"机器学习"相关的书              │
│  有 IVF：先去"计算机"区 → 再找"机器学习"书架 → 精确找书     │
└─────────────────────────────────────────────────────────────┘
```

**IVF 工作流程**：

```
训练阶段（一次性）：
1. 用 k-means 把所有向量聚成 n 类（比如 100 类）
2. 每类有个"中心向量"（centroid）
3. 每个向量属于最近的中心

检索阶段：
1. 计算 query 向量属于哪几个类
2. 只在这几个类里搜索
3. 返回最相似的结果
```

**代码示例**：

```python
import faiss

# 参数
dimension = 1536      # 向量维度
n_centroids = 100     # 聚类中心数（一般设为 sqrt(n) 左右）

# 创建 IVF 索引
quantizer = faiss.IndexFlatL2(dimension)  # 先有个扁平索引做"量化的基础"
index = faiss.IndexIVFFlat(quantizer, dimension, n_centroids)

# 训练（需要一些样本向量）
index.train(training_vectors)  # 训练 k-means 聚类

# 添加向量
index.add(vectors)

# 搜索前设置探查的聚类数（默认 1，越大越准但越慢）
index.nprobe = 5  # 探查 5 个最近的聚类

# 搜索
distances, indices = index.search(query_vector, k=5)
```

**IVF 的权衡**：

| nprobe | 速度 | 准确率    | 适用场景         |
| ------ | ---- | --------- | ---------------- |
| 1      | 最快 | 较低      | 对速度要求极高   |
| 5      | 快   | 中等      | 一般场景         |
| 10-20  | 中等 | 高        | 对准确率有要求   |
| 50+    | 慢   | 接近 100% | 对准确率要求极高 |

### 1.3 HNSW 索引：图结构搜索

**一句话**：用"图"的方式组织向量，搜索时"跳着走"。

**类比理解**：

```
想象找一个人：
Flat：挨家挨户敲门找 → 100% 找到，但慢
IVF：先去他可能住的片区，再挨户找 → 快一些
HNSW：先问居委会（高层节点），再问楼长（中层节点），再问邻居（底层节点）→ 更快
```

**HNSW 特点**：

| 优点         | 缺点         |
| ------------ | ------------ |
| 检索速度最快 | 占用内存大   |
| 准确率高     | 构建索引慢   |
| 适合高维向量 | 参数调优复杂 |

**代码示例**：

```python
import faiss

# HNSW 索引
index = faiss.IndexHNSWFlat(dimension, M=32)

# M: 每个节点最多连接多少个邻居（默认 32，越大越准但越占空间）
index.hnsw.efSearch = 64  # 搜索时的探索范围

# 添加向量
index.add(vectors)

# 搜索
distances, indices = index.search(query_vector, k=5)
```

---

## 二、向量数据库选型指南（1 小时）

### 2.1 主流工具对比

| 工具               | 类型      | 索引类型      | 特点                   | 适用场景           |
| ------------------ | --------- | ------------- | ---------------------- | ------------------ |
| **FAISS**    | 本地库    | IVF/HNSW/Flat | 免费、快、功能全       | 本地开发/原型验证  |
| **Chroma**   | 本地/服务 | HNSW          | 简单易用、支持元数据   | 快速开发/小型项目  |
| **Qdrant**   | 本地/服务 | HNSW          | 功能丰富、API 友好     | 中小型项目         |
| **Milvus**   | 分布式    | 多种          | 大规模、企业级         | 千万级以上数据     |
| **Pinecone** | 云服务    | 专有          | 托管、免运维           | 不想运维的团队     |
| **Weaviate** | 本地/服务 | HNSW          | 支持 GraphQL、模块丰富 | 需要复杂查询的场景 |

### 2.2 选型决策树

```
你的需求是什么？
│
├─ 🧪 学习/原型验证
│   └─ 选 FAISS（免费、资料多）
│
├─ 🚀 快速开发/小项目（<10 万条）
│   ├─ 想简单 → Chroma
│   └─ 想功能多 → Qdrant
│
├─ 📈 中等规模（10 万 -1000 万条）
│   ├─ 能自己运维 → Milvus 单机版
│   └─ 不想运维 → Pinecone
│
├─ 🏢 大规模（>1000 万条）
│   └─ 选 Milvus 分布式或云服务
│
├─ 🔒 数据敏感/不能外传
│   └─ 选 FAISS/Chroma/Qdrant 本地部署
│
└─ 🌐 需要复杂查询（过滤 + 向量 + 全文）
    └─ 选 Weaviate 或 Elasticsearch + 向量插件
```

### 2.3 一个真实案例

**场景**：公司内部知识库，10 万篇文档

```
需求：
- 每天新增约 100 篇文档
- 响应时间 <500ms
- 数据不能外传

选型过程：
1. 云服务排除（数据敏感）
2. Milvus 太重（运维成本高）
3. 在 FAISS 和 Chroma 之间选
4. 最终选 Chroma（支持元数据过滤，API 更友好）
```

---

## 三、实战任务（1 小时）

### 3.1 对比不同索引的速度和准确率

**任务**：用你的数据集测试不同索引

```python
import faiss
import time
import numpy as np

# 准备数据
n = 10000       # 1 万条向量
dimension = 768
vectors = np.random.random((n, dimension)).astype('float32')

# 归一化（用于余弦相似度）
faiss.normalize_L2(vectors)

# ========= 1. Flat 索引 =========
index_flat = faiss.IndexFlatIP(dimension)
index_flat.add(vectors)

# 测试检索速度
query = vectors[0:1]  # 用第一条做查询
start = time.time()
distances, indices = index_flat.search(query, k=10)
flat_time = time.time() - start
print(f"Flat 索引耗时：{flat_time*1000:.2f}ms")

# ========= 2. IVF 索引 =========
n_centroids = 100
quantizer = faiss.IndexFlatIP(dimension)
index_ivf = faiss.IndexIVFFlat(quantizer, dimension, n_centroids)
index_ivf.train(vectors)  # 训练
index_ivf.add(vectors)
index_ivf.nprobe = 5

start = time.time()
distances, indices = index_ivf.search(query, k=10)
ivf_time = time.time() - start
print(f"IVF 索引耗时：{ivf_time*1000:.2f}ms")

# ========= 3. HNSW 索引 =========
index_hnsw = faiss.IndexHNSWFlat(dimension, M=32)
index_hnsw.hnsw.efSearch = 64
index_hnsw.add(vectors)

start = time.time()
distances, indices = index_hnsw.search(query, k=10)
hnsw_time = time.time() - start
print(f"HNSW 索引耗时：{hnsw_time*1000:.2f}ms")
```

**记录结果**：

| 索引类型 | 构建时间 | 检索耗时 | 准确率（对比 Flat） |
| -------- | -------- | -------- | ------------------- |
| Flat     | -        | ms       | 100%（基准）        |
| IVF      |          | ms       | %                   |
| HNSW     |          | ms       | %                   |

### 3.2 尝试 Chroma（可选）

```bash
pip install chromadb
```

```python
import chromadb

# 创建客户端
client = chromadb.Client()

# 创建集合
collection = client.create_collection("my_docs")

# 添加文档（自动计算 Embedding）
collection.add(
    documents=["这是第一篇文档", "这是第二篇文档"],
    ids=["doc1", "doc2"]
)

# 检索
results = collection.query(
    query_texts=["用户问题"],
    n_results=5
)

print(results)
```

---

## 四、递归追问（30 分钟）

### 4.1 自测问题

**问题 1**：IVF 索引中的 `nprobe` 是什么意思？调大或调小有什么影响？

<details>
<summary>参考答案</summary>

nprobe 是检索时探查的聚类中心数量。

- 调大：准确率提高，速度变慢
- 调小：速度变快，准确率降低

</details>

**问题 2**：HNSW 为什么比 IVF 快？

<details>
<summary>参考答案</summary>

HNSW 用图结构组织向量，搜索时可以"跳跃式"前进。
IVF 还是要在他确定的聚类里遍历搜索。
HNSW 的时间复杂度接近 O(log n)，IVF 是 O(n/k)（k 是聚类数）。

</details>

**问题 3**：如果你的项目有 100 万条文档，你会选什么索引/数据库？为什么？

<details>
<summary>参考思路</summary>

考虑因素：

- 数据规模：100 万条属于中等规模
- 查询延迟要求
- 是否需要实时更新
- 运维能力

可能的选择：

- 追求速度：HNSW 索引
- 追求性价比：IVF 索引（nprobe 调高）
- 长期运维：Milvus 或云服务

</details>

---

## 五、知识卡片（15 分钟）

### 索引类型速查表

| 索引           | 速度 | 准确率 | 内存 | 适用场景     |
| -------------- | ---- | ------ | ---- | ------------ |
| IndexFlatL2/IP | 慢   | 100%   | 中   | 测试/小数据  |
| IndexIVFFlat   | 快   | 80-95% | 低   | 中等数据     |
| IndexIVFPQ     | 很快 | 70-90% | 很低 | 大数据       |
| IndexHNSWFlat  | 最快 | 90-98% | 高   | 对速度要求高 |

### 向量数据库核心概念

| 概念                 | 解释                   | 比喻           |
| -------------------- | ---------------------- | -------------- |
| 索引（Index）        | 加速检索的数据结构     | 图书馆目录     |
| 聚类（Clustering）   | 把相似向量分组         | 图书分类       |
| 量化（Quantization） | 用更少空间存储向量     | 压缩图片       |
| nprobe               | IVF 搜索时探查几个聚类 | 查几个分类区域 |
| efSearch             | HNSW 搜索时的探索范围  | 搜索半径       |

---

## 六、今日打卡（15 分钟）

### 6.1 实战结果

- [ ] 完成了不同索引的对比测试
- [ ] 记录了速度和准确率数据
- [X] （可选）尝试了 Chroma 或其他数据库

### 6.2 学习总结（200-500 字）

**提示**：

1. 我今天理解了哪些索引类型？它们各有什么特点？
2. 如果让我选型，我会选什么？为什么？
3. 我还有什么疑问？

```

今日总结：
1，IndexFlatL2/IP 
IndexFlatL2 和 IndexFlatIP 是 FAISS 的暴力搜索索引
两种索引的对比
IndexFlatL2
本质上是欧式距离
index = faiss.IndexFlatL2(dim)
距离度量：欧氏距离平方（L2²）
公式：||A - B||² = Σ(aᵢ - bᵢ)²
返回：距离越小越相似
适用：需要欧氏距离的场景

IndexFlatIP
本质上是求弦相似度
index = faiss.IndexFlatIP(dim)
距离度量：内积（Inner Product）
公式：A · B = Σ(aᵢ × bᵢ)
返回：内积越大越相似（但 FAISS 仍返回"最小距离"，内部取负）
适用：配合归一化向量 = 余弦相似度




```

### 6.3 本周后续计划

- [ ] Day 3-4：Query 优化（Query Rewriting、HyDE）
- [ ] Day 5-6：Rerank（Cross-Encoder 重排序）
- [ ] Day 7：输出笔记

---

## 七、延伸阅读

- [FAISS 官方 Wiki](https://github.com/facebookresearch/faiss/wiki)
- [HNSW 原理论文](https://arxiv.org/abs/1603.09320)
- [Chroma 文档](https://docs.trychroma.com/)
- [向量数据库对比](https://www.zilliz.com/learn/vector-database)

---

*学习日期：2026-04-03*
