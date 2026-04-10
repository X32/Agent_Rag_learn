#!/usr/bin/env python3
# 验证分块结果的脚本

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 复制必要的函数和常量
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

# 读取文档
with open('/Volumes/H/python/RAG_Agent_learn/Day1/RAGDemo/chatWithNavar-2.md', 'r', encoding='utf-8') as f:
    text = f.read()

print(f"文档总字符数: {len(text)}")
print(f"文档总行数: {len(text.splitlines())}")

# 手动实现一个简单的分块函数来测试
def simple_chunk(text, chunk_size, chunk_overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start = end - chunk_overlap
    return chunks

# 测试简单分块
chunks = simple_chunk(text, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)
print(f"\n简单字符分块结果:")
print(f"块数: {len(chunks)}")
print(f"平均块大小: {sum(len(c) for c in chunks) / len(chunks):.2f} 字符")
print(f"块大小范围: {min(len(c) for c in chunks)} - {max(len(c) for c in chunks)} 字符")

# 检查分块完整性
combined = "".join(chunks)
print(f"\n分块完整性检查:")
print(f"合并后字符数: {len(combined)}")
print(f"与原文档的差异: {abs(len(text) - len(combined))} 字符")
print(f"是否完全一致: {'是' if combined == text else '否'}")

# 计算理论块数
theoretical_min = len(text) // DEFAULT_CHUNK_SIZE
if len(text) % DEFAULT_CHUNK_SIZE > 0:
    theoretical_min += 1

with_overlap = len(text) // (DEFAULT_CHUNK_SIZE - DEFAULT_CHUNK_OVERLAP)
if len(text) % (DEFAULT_CHUNK_SIZE - DEFAULT_CHUNK_OVERLAP) > 0:
    with_overlap += 1

print(f"\n理论块数:")
print(f"无重叠: {theoretical_min}")
print(f"有重叠: {with_overlap}")
print(f"实际块数: {len(chunks)}")
print(f"块数合理性: {'合理' if len(chunks) >= theoretical_min and len(chunks) <= with_overlap + 5 else '可能有问题'}")