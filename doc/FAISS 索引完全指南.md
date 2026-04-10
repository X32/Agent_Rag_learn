# FAISS 索引完全指南

本文档整理了 RAG 系统中 FAISS 向量索引的核心知识，涵盖索引类型、选择策略和代码示例。

---

## 一、IndexFlatL2 与 IndexFlatIP

### 基本概念

`IndexFlatL2` 和 `IndexFlatIP` 是 FAISS 的**暴力搜索索引**（Brute-Force）。

| 特性 | 说明 |
|------|------|
| **原理** | 查询时计算与**所有向量**的距离 |
| **精度** | 100% 精确（无近似） |
| **速度** | O(n)，数据量大时慢 |
| **内存** | 连续存储，紧凑 |

### IndexFlatL2

```python
index = faiss.IndexFlatL2(dim)
```

- **距离度量**：欧氏距离平方（L2²）
- **公式**：`||A - B||² = Σ(aᵢ - bᵢ)²`
- **返回**：距离**越小**越相似
- **适用**：需要欧氏距离的场景

### IndexFlatIP

```python
index = faiss.IndexFlatIP(dim)
```

- **距离度量**：内积（Inner Product）
- **公式**：`A · B = Σ(aᵢ × bᵢ)`
- **返回**：内积**越大**越相似（FAISS 内部取负值返回）
- **适用**：配合归一化向量 = 余弦相似度

### 内积 vs 余弦相似度

| 度量 | 公式 | 是否考虑向量长度 |
|------|------|------------------|
| **内积** | `A · B` | ✓ 受长度影响 |
| **余弦相似度** | `(A · B) / (||A|| × ||B||)` | ✗ 只看方向 |

**关键技巧**：归一化后，内积 = 余弦相似度

```python
# L2 归一化
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# 此时 IndexFlatIP 的内积 = 余弦相似度
# 因为 ||A|| = ||B|| = 1，所以 A · B = cos(A, B)
```

### 代码示例

```python
import faiss
import numpy as np

# 归一化向量
v1 = np.array([[1, 0]], dtype='float32')
v2 = np.array([[0, 1]], dtype='float32')
v3 = np.array([[0.707, 0.707]], dtype='float32')

index = faiss.IndexFlatIP(2)
index.add(v1)

# 搜索
D, I = index.search(v2, 1)  # 垂直，内积=0
print(D)  # [0.]

D, I = index.search(v3, 1)  # 45 度，内积≈0.707
print(D)  # [0.707]
```

---

## 二、IVF 索引（Inverted File Index）

### 核心思想

**先聚类缩小搜索范围，再在候选集合内暴力搜索。**

### 工作原理

```
1. 训练阶段：用 k-means 将向量聚类成 n 个簇
2. 添加数据：每个向量分配到最近的簇
3. 搜索阶段：只搜索最近的 nprobe 个簇
```

### 可视化

```
IndexFlatL2:                    IndexIVFFlat:
┌─────────────────────┐         ┌─────────────────────┐
│  ● ● ● ● ● ● ● ● ●  │         │ 簇 1: ● ● ●         │
│  ● ● ● ● ● ● ● ● ●  │         │ 簇 2: ● ● ● ●       │
│  ● ● ● ● 查询 ● ● ●  │   vs    │ 簇 3: ● ● [查询] ●   │ ← 只搜这个
│  ● ● ● ● ● ● ● ● ●  │         │ 簇 4: ● ● ●         │
│  ● ● ● ● ● ● ● ● ●  │         │ 簇 5: ● ● ●         │
└─────────────────────┘         └─────────────────────┘
     全量扫描                        只搜最近的几个簇
```

### 关键参数

#### `nlist`（簇数量）
```python
# 经验法则：nlist ≈ √n (总向量数)
nlist = 100   # 适合 1 万向量
nlist = 1000  # 适合 100 万向量
```

#### `nprobe`（搜索簇数）
```python
index.nprobe = 10   # 默认值，平衡速度与精度
index.nprobe = 1    # 最快，但精度低
index.nprobe = 100  # 最慢，精度高
```

### 代码示例

```python
import faiss

dim = 384
nlist = 100  # 100 个簇

# 1. 创建量化器（聚类器）
quantizer = faiss.IndexFlatL2(dim)

# 2. 创建 IVF 索引
index = faiss.IndexIVFFlat(quantizer, dim, nlist)

# 3. 训练（必须先训练）
index.train(vectors)

# 4. 添加向量
index.add(vectors)

# 5. 搜索前设置 nprobe
index.nprobe = 10
D, I = index.search(query, k=5)
```

### IVF 变体

| 索引类型 | 说明 |
|----------|------|
| `IndexIVFFlat` | 簇内暴力搜索（精确） |
| `IndexIVFPQ` | 簇内 + 乘积量化（压缩） |
| `IndexIVFScalarQuantizer` | 簇内 + 标量量化 |

---

## 三、HNSW 索引（Hierarchical Navigable Small World）

### 核心概念

**用多层图结构实现快速近似搜索**，类似"地铁 + 公交 + 步行"的分层导航。

### 分层结构

```
Layer 3:  A ───────────── B      ← 顶层：长距离连接（稀疏）
          │              │
Layer 2:  C ──── D ───── E       ← 中层：中等距离
          │      │      │
Layer 1:  F ─ G ─ H ──── I       ← 底层：短距离连接（稠密）
          │   │   │     │
Layer 0:  J ─ K ─ L ──── M       ← 底层：所有向量（最密）
```

### 搜索过程

```
查询点 Q 的搜索路径：

Layer 3:  Q → 找到 A → 找到 B ─────────────┐
                                           ↓
Layer 2:  ─────────────────→ 找到 E → 找到 D → C
                                           ↓
Layer 1:  ──────────────────────────────→ H → G
                                           ↓
Layer 0:  ──────────────────────────────→ L → K (最近邻)

效率：每层指数级缩小范围，类似二分查找
```

### 关键参数

#### `M`（最大连接数）
```python
index = faiss.IndexHNSW(dim, M=32)
```
- 每个节点最多有 M 条边
- M 越大，图越稠密，搜索越快，内存越高
- 推荐值：16-64

#### `efConstruction`（构建时搜索范围）
```python
index.hnsw.efConstruction = 200
```
- 构建索引时的搜索精度
- 越大 → 图质量越好，构建越慢

#### `efSearch`（搜索时范围）
```python
index.hnsw.efSearch = 50
```
- 搜索时维护的候选集大小
- 越大 → 精度越高，速度越慢

### 代码示例

```python
import faiss

dim = 384
M = 32

# 创建 HNSW 索引
index = faiss.IndexHNSW(dim, M)

# 添加向量（不需要训练）
index.add(vectors)

# 配置搜索参数
index.hnsw.efConstruction = 200  # 构建精度
index.hnsw.efSearch = 50         # 搜索精度

# 搜索
D, I = index.search(query, k=10)
```

---

## 四、索引类型对比与选择

### 性能对比表

| 索引类型 | 构建速度 | 搜索速度 | 精度 | 内存 | 适用数据量 |
|----------|----------|----------|------|------|------------|
| `IndexFlatL2/IP` | 快 | O(n) 慢 | 100% | 低 | < 10K |
| `IndexIVFFlat` | 中 | 中 | 95-99% | 中 | 10K - 1M |
| `IndexHNSW` | 慢 | **极快** | 95-99% | 高 | > 100K |

### 选择决策树

```
数据量多少？
│
├── < 10,000 向量
│   └── 用 IndexFlatIP（精确 + 简单）
│
├── 10K - 1M 向量
│   └── 用 IndexIVFFlat（平衡速度与精度）
│       nlist ≈ √n
│       nprobe = 10-20
│
└── > 100K 向量 且需要低延迟
    └── 用 IndexHNSW（最快搜索）
        M = 32
        efConstruction = 200
        efSearch = 50
```

### HNSW vs IVF 对比

```
IVF:                          HNSW:
┌─────────────────┐          ┌─────────────────┐
│  聚类 → 分配簇   │          │  逐层插入图中    │
│       ↓         │          │       ↓         │
│  搜索 nprobe 个簇 │          │  贪心逐层逼近    │
└─────────────────┘          └─────────────────┘
     分区搜索                      图遍历

优点：内存低，可预测            优点：搜索最快，无训练
缺点：需要训练，精度受限        缺点：内存高，构建慢
```

---

## 五、在 RAG 项目中的应用

### 小规模 RAG（当前项目）

```python
# naive_rag.py - 数据量小，用 IndexFlatIP
self.index = faiss.IndexFlatIP(self.embedding_dim)
embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
self.index.add(embeddings)
```

### 大规模 RAG（扩展建议）

```python
# 如果向量数 > 10 万，考虑改用 IVF
if len(vectors) > 100000:
    nlist = int(np.sqrt(len(vectors)))
    quantizer = faiss.IndexFlatL2(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist)
    index.train(vectors)
    index.add(vectors)
    index.nprobe = max(5, nlist // 10)
```

```python
# 如果需要极低延迟，考虑改用 HNSW
if len(vectors) > 100000:
    index = faiss.IndexHNSW(384, M=32)
    index.hnsw.efConstruction = 200
    index.hnsw.efSearch = 50
    index.add(vectors)
```

---

## 六、总结

| 索引 | 本质 | 核心优势 | 适用场景 |
|------|------|----------|----------|
| `IndexFlatIP` | 暴力搜索 + 内积 | 精确、简单 | 小数据量 RAG |
| `IndexFlatL2` | 暴力搜索 + 欧氏距离 | 精确、简单 | 空间距离敏感场景 |
| `IndexIVFFlat` | 聚类 + 分区搜索 | 平衡速度与精度 | 中等数据量 |
| `IndexHNSW` | 多层图遍历 | 搜索速度最快 | 大数据量 + 低延迟 |

---

## 参考资料

- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS Wiki - Index Factory](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [HNSW 原理论文](https://arxiv.org/abs/1603.09320)
