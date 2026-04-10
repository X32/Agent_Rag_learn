# 📅 LLM 工程师面试 - 30 天学习打卡计划

## 阶段一：基础巩固 (Day 1-7)

### Day 1 - C++ 核心
- [ ] 智能指针 (unique_ptr, shared_ptr, weak_ptr)
- [ ] 移动语义 (std::move, 右值引用)
- [ ] RAII 原则
- [ ] **刷题**: LeetCode 2 题 (数组/链表)
- [ ] **输出**: 整理 C++ 内存管理笔记

### Day 2 - Python 进阶
- [ ] 装饰器原理与应用
- [ ] 生成器与迭代器
- [ ] 异步编程 (asyncio)
- [ ] GIL 与多线程/多进程
- [ ] **刷题**: LeetCode 2 题 (字符串)
- [ ] **输出**: Python 并发编程总结

### Day 3 - 数据结构复习
- [ ] 数组/链表/栈/队列
- [ ] 哈希表实现原理
- [ ] 堆与优先队列
- [ ] **刷题**: LeetCode 3 题 (数据结构综合)

### Day 4 - 算法基础
- [ ] 排序算法 (快排、归并、堆排序)
- [ ] 二分查找
- [ ] 双指针技巧
- [ ] **刷题**: LeetCode 3 题 (排序/查找)

### Day 5 - 动态规划
- [ ] DP 核心思想
- [ ] 背包问题
- [ ] 最长子序列
- [ ] **刷题**: LeetCode 3 题 (DP 入门)

### Day 6 - 深度学习基础
- [ ] 反向传播推导
- [ ] 常见优化器 (SGD, Adam, AdamW)
- [ ] 正则化 (Dropout, LayerNorm, BatchNorm)
- [ ] 损失函数选择
- [ ] **输出**: 手推 BP 算法

### Day 7 - 神经网络架构
- [ ] CNN 原理与应用
- [ ] RNN/LSTM/GRU
- [ ] Seq2Seq 架构
- [ ] **刷题**: LeetCode 2 题 (树)
- [ ] **周总结**: 复习本周内容

---

## 阶段二：LLM 核心 (Day 8-15)

### Day 8 - Transformer 架构 (上)
- [ ] Self-Attention 机制
- [ ] Multi-Head Attention
- [ ] Positional Encoding
- [ ] **输出**: 手推 Attention 计算过程

### Day 9 - Transformer 架构 (下)
- [ ] Encoder-Decoder 结构
- [ ] LayerNorm 位置 (Pre/Post)
- [ ] 残差连接
- [ ] **输出**: 画 Transformer 完整架构图

### Day 10 - Tokenization
- [ ] BPE 算法原理
- [ ] WordPiece vs SentencePiece
- [ ] 特殊 token 设计
- [ ] **实践**: 用 transformers 库测试不同 tokenizer

### Day 11 - Pre-training
- [ ] MLM (Masked Language Modeling)
- [ ] Next Sentence Prediction
- [ ] 因果语言建模
- [ ] 数据配比与清洗
- [ ] **阅读**: GPT/BERT 原论文

### Day 12 - Fine-tuning 技术
- [ ] 全量微调
- [ ] LoRA 原理与实现
- [ ] P-Tuning / Prefix Tuning
- [ ] 指令微调 (Instruction Tuning)
- [ ] **实践**: 用 LoRA 微调一个小模型

### Day 13 - RLHF
- [ ] 奖励模型训练
- [ ] PPO 算法
- [ ] DPO (Direct Preference Optimization)
- [ ] **阅读**: InstructGPT / DPO 论文

### Day 14 - 推理优化
- [ ] KV Cache 原理
- [ ] 量化 (INT8, INT4, GPTQ)
- [ ] 模型蒸馏
- [ ] **实践**: 用 vLLM 部署模型

### Day 15 - 阶段复盘
- [ ] 复习 Transformer 所有细节
- [ ] 整理 LLM 知识图谱
- [ ] **模拟面试**: 自问自答 10 个核心问题

---

## 阶段三：应用场景 (Day 16-22)

### Day 16 - 多轮对话系统
- [ ] 对话状态管理
- [ ] 上下文窗口限制处理
- [ ] 记忆机制 (短期/长期)
- [ ] 对话一致性
- [ ] **输出**: 设计一个多轮对话方案

### Day 17 - RAG 架构
- [ ] 文档切片策略
- [ ] 向量数据库 (FAISS, Milvus)
- [ ] Embedding 模型选择
- [ ] 检索优化 (HyDE, 多路召回)
- [ ] **实践**: 搭建简易 RAG 系统

### Day 18 - RAG 进阶
- [ ] Query 改写与扩展
- [ ] 重排序 (Rerank)
- [ ] 混合检索 (稠密 + 稀疏)
- [ ] **输出**: RAG 优化 checklist

### Day 19 - Agent 设计
- [ ] Function Calling 原理
- [ ] Tool Use 框架
- [ ] ReAct 范式
- [ ] 规划与反思
- [ ] **阅读**: ReAct / Toolformer 论文

### Day 20 - Agent 实践
- [ ] LangChain / LlamaIndex
- [ ] 自定义 Tool 开发
- [ ] 多 Agent 协作
- [ ] **实践**: 实现一个简单的 Agent

### Day 21 - Prompt 工程
- [ ] Few-shot / Zero-shot
- [ ] Chain of Thought
- [ ] Prompt 模板设计
- [ ] Prompt 安全与注入防护
- [ ] **输出**: 常用 Prompt 模板库

### Day 22 - 项目整合
- [ ] 设计完整技术方案
- [ ] 考虑扩展性与维护性
- [ ] 性能与成本评估
- [ ] **输出**: 技术方案文档

---

## 阶段四：模拟面试 (Day 23-30)

### Day 23 - 编程面试准备
- [ ] 复习高频算法题
- [ ] 白板编程练习
- [ ] **刷题**: LeetCode 5 题 (混合)

### Day 24 - 深度学习面试
- [ ] 复习 DL 核心概念
- [ ] 准备常见面试题
- [ ] **输出**: DL 面试 Q&A 文档

### Day 25 - LLM 技术面试 (上)
- [ ] Transformer 细节问答
- [ ] 训练技巧问答
- [ ] **模拟**: 找朋友/自己录音模拟

### Day 26 - LLM 技术面试 (下)
- [ ] 应用场景问答
- [ ] 工程实践问答
- [ ] **模拟**: 继续模拟面试

### Day 27 - 行为面试准备
- [ ] 准备项目经历
- [ ] STAR 法则整理
- [ ] 常见问题准备
- [ ] **输出**: 个人故事库

### Day 28 - 公司/业务研究
- [ ] 了解目标公司业务
- [ ] 研究技术栈
- [ ] 准备反问问题
- [ ] **输出**: 公司调研笔记

### Day 29 - 全真模拟
- [ ] 完整模拟面试流程
- [ ] 计时练习
- [ ] 录像复盘
- [ ] **输出**: 改进清单

### Day 30 - 最后准备
- [ ] 复习所有笔记
- [ ] 调整状态
- [ ] 准备面试材料
- [ ] **休息**: 保证睡眠

---

## 📝 打卡记录模板

```markdown
## Day X - [日期]

### 完成内容
- [ ] 任务 1
- [ ] 任务 2

### 学习笔记
> 记录关键知识点

### 遇到的问题
> 记录卡点

### 明日计划
- [ ] 任务 1
- [ ] 任务 2
```

---

**💡 使用建议:**
1. 每天花 2-4 小时专注学习
2. 周末可适当调整进度
3. 重要内容要做笔记输出
4. 遇到难点可以延长 1-2 天
5. 保持节奏，不要 burnout

**Good Luck! 🚀**
