"""
测试新旧切分函数的对比效果
"""

import nltk
from nltk.tokenize import sent_tokenize
from typing import List
import re

# 下载必要的 nltk 资源
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    将文本分割成指定大小的块，支持块间重叠，保持句子完整性
    """
    if not text:
        return []

    sentences = sent_tokenize(text)
    if not sentences:
        return [text]

    chunks = []
    current_chunk = []
    current_chunk_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if sentence_length > chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_chunk_length = 0

            start = 0
            while start < sentence_length:
                end = min(start + chunk_size, sentence_length)
                chunks.append(sentence[start:end])
                start = end - chunk_overlap if chunk_overlap > 0 else end
            continue

        new_length = current_chunk_length + sentence_length + (1 if current_chunk else 0)

        if new_length > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))

            overlap_chars = 0
            overlap_sentences = []

            for sent in reversed(current_chunk):
                sent_len_with_space = len(sent) + 1
                if overlap_chars + sent_len_with_space > chunk_overlap:
                    break
                overlap_chars += sent_len_with_space
                overlap_sentences.insert(0, sent)

            current_chunk = overlap_sentences
            current_chunk_length = sum(len(s) + 1 for s in current_chunk) - 1 if current_chunk else 0

        current_chunk.append(sentence)
        current_chunk_length = current_chunk_length + sentence_length + (1 if current_chunk_length > 0 else 0)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def chunk_text_optimized(text: str, chunk_size: int = 400, chunk_overlap: int = 100) -> List[str]:
    """
    优化的文本分块函数，专门针对访谈录等段落型文档
    
    优化特性：
    1. 识别强调内容（**...**），确保不被截断
    2. 按章节切分（## 开头），保持章节完整性
    3. 使用更小的 chunk_size（400）适合访谈录的段落长度
    4. 保持句子完整性
    """
    if not text:
        return []
    
    # 1. 按章节分割（## 开头）
    chapters = re.split(r'\n##\s+', text)
    chapters = [ch.strip() for ch in chapters if ch.strip()]
    
    # 如果没有章节，直接使用原有切分
    if len(chapters) <= 1:
        return chunk_text(text, chunk_size, chunk_overlap)
    
    chunks = []
    
    for chapter in chapters:
        # 2. 识别强调内容（**...**）
        emphasis_pattern = r'\*\*(.*?)\*\*'
        emphasis_matches = list(re.finditer(emphasis_pattern, chapter))
        
        if not emphasis_matches:
            # 没有强调内容，使用原有切分
            chapter_chunks = chunk_text(chapter, chunk_size, chunk_overlap)
            chunks.extend(chapter_chunks)
            continue
        
        # 有强调内容，确保强调内容不被截断
        sentences = sent_tokenize(chapter)
        if not sentences:
            chunks.append(chapter)
            continue
        
        current_chunk = []
        current_chunk_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # 检查句子是否包含强调内容
            has_emphasis = bool(re.search(emphasis_pattern, sentence))
            
            if has_emphasis:
                # 如果当前块不为空，先保存
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_chunk_length = 0
                
                # 强调内容单独成块
                chunks.append(sentence.strip())
                continue
            
            # 普通句子，按原有逻辑切分
            new_length = current_chunk_length + sentence_length + (1 if current_chunk else 0)
            
            if new_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                # 处理重叠
                overlap_chars = 0
                overlap_sentences = []
                
                for sent in reversed(current_chunk):
                    sent_len_with_space = len(sent) + 1
                    if overlap_chars + sent_len_with_space > chunk_overlap:
                        break
                    overlap_chars += sent_len_with_space
                    overlap_sentences.insert(0, sent)
                
                current_chunk = overlap_sentences
                current_chunk_length = sum(len(s) + 1 for s in current_chunk) - 1 if current_chunk else 0
            
            current_chunk.append(sentence)
            current_chunk_length = current_chunk_length + sentence_length + (1 if current_chunk_length > 0 else 0)
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(' '.join(current_chunk))
    
    return chunks


# 读取测试文档
with open('/Volumes/H/python/RAG_Agent_learn/RAG/RAGDemo/chatWithNavar-2.md', 'r', encoding='utf-8') as f:
    text = f.read()

print("=" * 80)
print("测试文档: chatWithNavar-2.md")
print("=" * 80)
print(f"文档总长度: {len(text)} 字符")
print()

# 使用旧的切分函数
print("=" * 80)
print("旧切分函数 (chunk_text) - chunk_size=1200, chunk_overlap=120")
print("=" * 80)
old_chunks = chunk_text(text, chunk_size=1200, chunk_overlap=120)
print(f"分块数量: {len(old_chunks)}")
print(f"平均块长度: {sum(len(chunk) for chunk in old_chunks) / len(old_chunks):.1f} 字符")
print()

# 显示前3个块的内容
for i, chunk in enumerate(old_chunks[:3]):
    print(f"块 {i+1} (长度: {len(chunk)} 字符):")
    print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    print()

# 使用新的优化切分函数
print("=" * 80)
print("新切分函数 (chunk_text_optimized) - chunk_size=400, chunk_overlap=100")
print("=" * 80)
new_chunks = chunk_text_optimized(text, chunk_size=400, chunk_overlap=100)
print(f"分块数量: {len(new_chunks)}")
print(f"平均块长度: {sum(len(chunk) for chunk in new_chunks) / len(new_chunks):.1f} 字符")
print()

# 显示前3个块的内容
for i, chunk in enumerate(new_chunks[:3]):
    print(f"块 {i+1} (长度: {len(chunk)} 字符):")
    print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
    print()

# 对比分析
print("=" * 80)
print("对比分析")
print("=" * 80)
print(f"旧切分函数:")
print(f"  - 分块数量: {len(old_chunks)}")
print(f"  - 平均块长度: {sum(len(chunk) for chunk in old_chunks) / len(old_chunks):.1f} 字符")
print(f"  - 最大块长度: {max(len(chunk) for chunk in old_chunks)} 字符")
print(f"  - 最小块长度: {min(len(chunk) for chunk in old_chunks)} 字符")
print()
print(f"新切分函数:")
print(f"  - 分块数量: {len(new_chunks)}")
print(f"  - 平均块长度: {sum(len(chunk) for chunk in new_chunks) / len(new_chunks):.1f} 字符")
print(f"  - 最大块长度: {max(len(chunk) for chunk in new_chunks)} 字符")
print(f"  - 最小块长度: {min(len(chunk) for chunk in new_chunks)} 字符")
print()

# 检查强调内容是否被完整保留
emphasis_pattern = r'\*\*(.*?)\*\*'
emphasis_in_text = len(re.findall(emphasis_pattern, text))
emphasis_in_old = sum(len(re.findall(emphasis_pattern, chunk)) for chunk in old_chunks)
emphasis_in_new = sum(len(re.findall(emphasis_pattern, chunk)) for chunk in new_chunks)

print(f"强调内容分析:")
print(f"  - 文档中强调内容总数: {emphasis_in_text}")
print(f"  - 旧切分函数保留的强调内容: {emphasis_in_old}")
print(f"  - 新切分函数保留的强调内容: {emphasis_in_new}")
print()

# 检查是否有强调内容被截断
def has_truncated_emphasis(chunks):
    for chunk in chunks:
        # 检查是否有不完整的强调标记
        if (chunk.count('**') % 2 != 0):
            return True
    return False

print(f"强调内容截断检查:")
print(f"  - 旧切分函数是否有截断: {'是' if has_truncated_emphasis(old_chunks) else '否'}")
print(f"  - 新切分函数是否有截断: {'是' if has_truncated_emphasis(new_chunks) else '否'}")
print()