#!/usr/bin/env python3
# 测试分块函数的脚本

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from naive_rag import chunk_text, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

def main():
    # 读取测试文档
    doc_path = os.path.join(os.path.dirname(__file__), "chatWithNavar-2.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 打印文档总信息
    print(f"文档总字符数: {len(text)}")
    print(f"文档总单词数: {len(text.split())}")
    print()
    
    # 测试分块函数
    chunks = chunk_text(text, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)
    
    # 打印分块结果统计
    print(f"分块结果统计:")
    print(f"- 块数: {len(chunks)}")
    print(f"- 理论最小块数(无重叠): {len(text) // DEFAULT_CHUNK_SIZE} + {1 if len(text) % DEFAULT_CHUNK_SIZE > 0 else 0}")
    print(f"- 理论最小块数(有重叠): {len(text) // (DEFAULT_CHUNK_SIZE - DEFAULT_CHUNK_OVERLAP)} + {1 if len(text) % (DEFAULT_CHUNK_SIZE - DEFAULT_CHUNK_OVERLAP) > 0 else 0}")
    print()
    
    # 检查每个块的大小
    print(f"各块大小(字符数):")
    total_chunk_chars = 0
    for i, chunk in enumerate(chunks):
        chunk_len = len(chunk)
        total_chunk_chars += chunk_len
        print(f"  块 {i+1}: {chunk_len} 字符")
    
    print()
    print(f"总块字符数: {total_chunk_chars}")
    print(f"重叠率: {(total_chunk_chars - len(text)) / total_chunk_chars * 100:.2f}%")
    print(f"平均块大小: {total_chunk_chars / len(chunks):.2f} 字符")
    print(f"最大块大小: {max(len(chunk) for chunk in chunks)} 字符")
    print(f"最小块大小: {min(len(chunk) for chunk in chunks)} 字符")
    
    # 检查分块是否完整
    combined_chunks = "".join(chunks)
    is_complete = combined_chunks == text
    print(f"\n分块完整性检查: {'通过' if is_complete else '失败'}")
    
    if not is_complete:
        print(f"  原始文本长度: {len(text)}")
        print(f"  合并后长度: {len(combined_chunks)}")
        print(f"  差异: {abs(len(text) - len(combined_chunks))} 字符")

if __name__ == "__main__":
    main()