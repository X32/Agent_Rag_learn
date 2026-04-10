#!/usr/bin/env python3
# 简单测试脚本，直接分析文档结构

# 读取文档
with open('/Volumes/H/python/RAG_Agent_learn/Day1/RAGDemo/chatWithNavar-2.md', 'r', encoding='utf-8') as f:
    text = f.read()

print(f"文档总字符数: {len(text)}")
print(f"文档总行数: {len(text.splitlines())}")

# 检查句子分割的简单方法（用句号分割）
sentences_with_period = text.split('.')
print(f"\n用句号分割的句子数: {len(sentences_with_period)}")
print(f"平均句子长度: {len(text) / len(sentences_with_period) if sentences_with_period else 0:.2f} 字符")

# 检查是否有超长句子
long_sentences = [s for s in sentences_with_period if len(s) > 500]
print(f"\n超过500字符的句子数: {len(long_sentences)}")
if long_sentences:
    print(f"最长句子长度: {max(len(s) for s in long_sentences)} 字符")
    print(f"第一个超长句子的前200字符: {long_sentences[0][:200]}...")

# 手动测试简单的分块逻辑
print("\n手动测试简单分块逻辑:")
chunk_size = 500
chunk_overlap = 50

# 简单的字符分块
chunks = []
start = 0
while start < len(text):
    end = min(start + chunk_size, len(text))
    chunks.append(text[start:end])
    start = end - chunk_overlap

print(f"简单字符分块的块数: {len(chunks)}")
print(f"平均块大小: {len(text) / len(chunks) if chunks else 0:.2f} 字符")
print(f"前3块大小: {[len(chunk) for chunk in chunks[:3]]}")