# Week 2 Day 3-4：检索优化 - Query 处理

> **学习目标**：掌握 Query 优化技术，让检索更准确  
> **时间分配**：6-8 小时  
> **产出物**：可运行的 Query 优化代码 + 对比实验报告

---

## 一、核心问题：为什么需要 Query 优化？

### 1.1 真实场景中的问题

```
用户提问 vs 文档内容的"语义鸿沟"

用户问："怎么重置密码？"
文档里写："如果您忘记了登录凭证，可以通过以下步骤恢复账户访问权限..."

❌ 直接检索：匹配度低（用词完全不同）
✅ Query 优化：改写后能匹配到相关文档
```

### 1.2 常见查询问题

| 问题类型 | 例子 | 影响 |
|---------|------|------|
| **过于简短** | "报错"、"失败了" | 缺乏上下文，无法检索 |
| **表达模糊** | "那个功能怎么用？" | 指代不明 |
| **用词差异** | "登陆"vs"登录" | 关键词不匹配 |
| **缺少背景** | "怎么配置？" | 不知道配置什么 |
| **多轮对话** | "那第二个呢？" | 依赖上文 |

---

## 二、Query Rewriting（查询改写）

### 2.1 核心思想

**用 LLM 把用户模糊的查询改写成更适合检索的形式。**

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   用户原始查询   │  →   │   LLM 改写       │  →   │   向量检索       │
│  "密码忘了咋办"  │      │ "如何重置密码"   │      │  找到相关文档   │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

### 2.2 实现代码

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

def rewrite_query(original_query: str) -> str:
    """
    使用 LLM 改写查询，使其更适合向量检索
    """
    prompt = f"""
你是一个查询改写助手。请把用户的问题改写成更清晰、更具体的形式，
便于从知识库中检索相关文档。

要求：
1. 保持原意，但表达更清晰
2. 补充隐含的上下文
3. 使用更正式、更具体的词汇
4. 不要添加额外信息

用户问题：{original_query}

改写后的问题：
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # 低温度，保证输出稳定
    )
    
    return response.choices[0].message.content

# 测试
original = "密码忘了咋办"
rewritten = rewrite_query(original)
print(f"原始查询：{original}")
print(f"改写后：{rewritten}")
# 输出：原始查询：密码忘了咋办
#       改写后：如何重置或恢复忘记的密码
```

### 2.3 完整 RAG 集成

```python
class OptimizedRAG:
    def __init__(self, retriever, llm_client):
        self.retriever = retriever  # 向量检索器
        self.llm_client = llm_client  # LLM 客户端
    
    def rewrite_query(self, query: str) -> str:
        """改写查询"""
        prompt = f"""
请改写以下问题，使其更适合从文档中检索相关信息：
{query}
"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def retrieve(self, query: str, k: int = 5):
        """检索相关文档"""
        # 使用改写后的查询检索
        rewritten_query = self.rewrite_query(query)
        print(f"[检索查询] {rewritten_query}")
        return self.retriever.search(rewritten_query, k=k)
    
    def generate_answer(self, query: str, contexts: list) -> str:
        """生成答案"""
        # 生成答案时使用原始查询
        prompt = f"""
基于以下信息回答问题：{query}

相关信息：
{''.join(contexts)}

答案：
"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def answer(self, query: str) -> dict:
        """完整的 RAG 流程"""
        # 检索
        contexts = self.retrieve(query, k=5)
        
        # 生成
        answer = self.generate_answer(query, contexts)
        
        return {
            "query": query,
            "contexts": contexts,
            "answer": answer
        }
```

---

## 三、HyDE（Hypothetical Document Embeddings）

### 3.1 核心思想

**不直接检索用户问题，而是先让 LLM 生成一个"假设性答案"，用答案的向量去检索。**

```
传统 RAG:
用户问题 → [向量化] → 检索 → 文档

HyDE:
用户问题 → LLM 生成假设答案 → [假设答案向量化] → 检索 → 真实文档
                              ↑
                      答案和文档在同一个向量空间！
```

### 3.2 为什么 HyDE 有效？

```
问题："Python 中如何读取 CSV 文件？"

直接检索的问题：
- 问题向量和文档向量分布不同
- 问题很短，文档很长

HyDE 的优势：
- 假设答案："在 Python 中，可以使用 pandas 库的 read_csv 函数..."
- 假设答案的词汇和真实文档更相似
- 在同一个语义空间，检索更准确
```

### 3.3 实现代码

```python
class HyDERetriever:
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client
    
    def generate_hypothetical_answer(self, query: str) -> str:
        """生成假设性答案"""
        prompt = f"""
请针对以下问题，写一个可能的答案。
答案应该详细、具体，包含相关专业术语。
不需要确保答案正确，只需要帮助检索相关文档。

问题：{query}

假设答案：
"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def search(self, query: str, k: int = 5):
        """使用 HyDE 检索"""
        # 1. 生成假设答案
        hypothetical_answer = self.generate_hypothetical_answer(query)
        print(f"[假设答案] {hypothetical_answer[:100]}...")
        
        # 2. 用假设答案的向量检索
        results = self.retriever.search(hypothetical_answer, k=k)
        
        return results, hypothetical_answer
```

### 3.4 HyDE vs 传统检索对比

```python
# 对比实验
def compare_retrieval_methods(query: str, retriever, hyde_retriever):
    print(f"\n=== 查询：{query} ===\n")
    
    # 传统方法
    print("--- 传统检索 ---")
    traditional_results = retriever.search(query, k=3)
    for i, doc in enumerate(traditional_results):
        print(f"{i+1}. {doc[:80]}...")
    
    # HyDE
    print("\n--- HyDE 检索 ---")
    hyde_results, hypo_answer = hyde_retriever.search(query, k=3)
    for i, doc in enumerate(hyde_results):
        print(f"{i+1}. {doc[:80]}...")
    
    return traditional_results, hyde_results

# 测试查询
test_queries = [
    "怎么导出数据？",
    "API 调用失败怎么办？",
    "如何优化性能？"
]

for query in test_queries:
    compare_retrieval_methods(query, retriever, hyde_retriever)
```

---

## 四、Multi-Query（多查询）

### 4.1 核心思想

**让 LLM 从不同角度生成多个版本的查询，分别检索后合并结果。**

```
用户问题
   │
   ├─→ 查询 1（专业术语版）→ 检索 → 结果 1
   ├─→ 查询 2（通俗解释版）→ 检索 → 结果 2
   ├─→ 查询 3（场景应用版）→ 检索 → 结果 3
   │
   └─→ 合并去重 → TopK → 最终结果
```

### 4.2 实现代码

```python
class MultiQueryRetriever:
    def __init__(self, retriever, llm_client, num_queries: int = 3):
        self.retriever = retriever
        self.llm_client = llm_client
        self.num_queries = num_queries
    
    def generate_queries(self, original_query: str) -> list[str]:
        """生成多个不同角度的查询"""
        prompt = f"""
请为以下问题生成 {self.num_queries} 个不同版本的改写，
每个版本从不同角度提问，便于全面检索相关信息。

原问题：{original_query}

请直接输出改写后的问题，每行一个：
"""
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8  # 较高温度，增加多样性
        )
        
        queries = response.choices[0].message.content.strip().split('\n')
        return [q.strip() for q in queries if q.strip()]
    
    def search(self, query: str, k: int = 5) -> list:
        """多查询检索"""
        # 1. 生成多个查询
        queries = self.generate_queries(query)
        print(f"[原始查询] {query}")
        print(f"[生成查询] {queries}")
        
        # 2. 分别检索
        all_results = []
        for q in queries:
            results = self.retriever.search(q, k=k)
            all_results.extend(results)
        
        # 3. 去重（简单去重，可优化）
        unique_results = list(dict.fromkeys(all_results))
        
        # 4. 返回 TopK
        return unique_results[:k]
```

### 4.3 实际效果示例

```python
# 测试
multi_retriever = MultiQueryRetriever(retriever, client, num_queries=3)

query = "怎么配置数据库连接？"
results = multi_retriever.search(query, k=5)

print("\n=== 检索结果 ===")
for i, doc in enumerate(results):
    print(f"{i+1}. {doc[:100]}...")
```

**生成的多版本查询示例**：
```
原始查询：怎么配置数据库连接？

生成查询：
1. 数据库连接的配置参数有哪些？
2. 如何在代码中设置数据库连接字符串？
3. 数据库连接池的配置方法是什么？
```

---

## 五、三种方法对比

| 方法 | 核心思路 | 优点 | 缺点 | 适用场景 |
|------|---------|------|------|---------|
| **Query Rewriting** | 改写查询更清晰 | 简单、快速 | 依赖 LLM 质量 | 用户表达模糊时 |
| **HyDE** | 用假设答案检索 | 桥接问题 - 文档鸿沟 | 多一次 LLM 调用 | 问题与文档词汇差异大 |
| **Multi-Query** | 多角度检索 | 覆盖更全面 | 多次检索，成本高 | 复杂问题、需要全面信息 |

### 组合使用建议

```python
class AdvancedRAG:
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client
    
    def hybrid_retrieve(self, query: str, k: int = 10) -> list:
        """组合多种检索策略"""
        all_results = []
        
        # 1. 直接检索
        direct = self.retriever.search(query, k=k)
        all_results.extend(direct)
        
        # 2. Query Rewriting 后检索
        rewritten = self.rewrite_query(query)
        rewritten_results = self.retriever.search(rewritten, k=k)
        all_results.extend(rewritten_results)
        
        # 3. HyDE 检索
        hypo_answer = self.generate_hypothetical_answer(query)
        hyde_results = self.retriever.search(hypo_answer, k=k)
        all_results.extend(hyde_results)
        
        # 去重 + 排序
        unique_results = self.deduplicate_and_rank(all_results, query)
        return unique_results[:k]
```

---

## 六、实践任务

### Task 1：实现 Query Rewriting

```python
# TODO: 完成以下任务

# 1. 实现 rewrite_query 函数
def rewrite_query(query: str) -> str:
    # 使用 LLM 改写查询
    pass

# 2. 测试以下查询的改写效果
test_cases = [
    "报错了",
    "怎么弄那个",
    "密码",
    "连不上"
]

# 3. 记录改写前后的检索结果差异
```

### Task 2：实现 HyDE

```python
# TODO: 完成以下任务

# 1. 实现 HyDE 检索器
class HyDERetriever:
    def generate_hypothetical_answer(self, query: str) -> str:
        pass
    
    def search(self, query: str, k: int = 5):
        pass

# 2. 对比 HyDE vs 直接检索的效果
# 记录哪些查询 HyDE 检索到了直接检索没找到的文档
```

### Task 3：对比实验报告

```markdown
## Query 优化对比实验报告

### 测试查询
1. [查询 1]
2. [查询 2]
3. [查询 3]

### 检索结果对比

| 查询 | 方法 | 相关文档数 | 最佳结果排名 |
|------|------|-----------|-------------|
| 查询 1 | 直接检索 | | |
| 查询 1 | Query Rewriting | | |
| 查询 1 | HyDE | | |
| 查询 1 | Multi-Query | | |

### 结论
- 哪种方法在什么场景下效果最好？
- 延迟和成本的权衡？
- 你的项目应该采用哪种策略？
```

---

## 七、延伸学习

### 7.1 相关论文

- [HyDE: Improving Dense Retrieval with Hypothetical Document Embeddings](https://arxiv.org/abs/2212.10496)
- [Query Rewriting for Retrieval-Augmented Large Language Models](https://arxiv.org/abs/2305.14283)

### 7.2 开源实现

- [LangChain MultiQueryRetriever](https://python.langchain.com/docs/modules/data_connection/retrievers/MultiQueryRetriever)
- [LlamaIndex Query Transformations](https://docs.llamaindex.ai/en/stable/examples/query_transformations/query_transformations_cookbook/)

### 7.3 进阶技巧

```python
# 1. 上下文感知的 Query 改写（多轮对话）
def rewrite_with_context(query: str, conversation_history: list) -> str:
    pass

# 2. 领域特定的改写提示
def domain_specific_rewrite(query: str, domain: str) -> str:
    domain_prompts = {
        "legal": "请用法律专业术语改写...",
        "medical": "请用医学术语改写...",
        "tech": "请用技术术语改写..."
    }
    pass

# 3. 基于反馈的迭代优化
def iterative_rewrite(query: str, initial_results: list, feedback: str) -> str:
    # 根据检索结果的相关性反馈，进一步优化查询
    pass
```

---

## 八、Checklist

- [ ] 理解 Query Rewriting 的原理和实现
- [ ] 理解 HyDE 为什么有效
- [ ] 理解 Multi-Query 的优势和成本
- [ ] 实现至少一种 Query 优化方法
- [ ] 完成对比实验报告
- [ ] 将优化方法集成到自己的 RAG 项目中

---

*学习日期：2026-04-XX*  
*参考资料：RAG 学习计划 - Week 2 Day 3-4*
