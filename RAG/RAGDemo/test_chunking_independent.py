#!/usr/bin/env python3
# 独立测试分块函数的脚本，不依赖外部模块

import nltk
from nltk.tokenize import sent_tokenize

# 下载必要的nltk资源
nltk.download('punkt', quiet=True)

# 复制分块函数的实现
def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list:
    if not text:
        return []
    
    # 首先将文本分割成句子
    sentences = sent_tokenize(text)
    if not sentences:
        return [text]
    
    chunks = []
    current_chunk = []
    current_chunk_length = 0
    
    for sentence in sentences:
        sentence_length = len(sentence)
        
        # 如果句子本身就超过了块大小，特殊处理
        if sentence_length > chunk_size:
            # 保存当前块
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_chunk_length = 0
            
            # 将超长句子分割成更小的块
            start = 0
            while start < sentence_length:
                end = min(start + chunk_size, sentence_length)
                # 尽量在标点处分割
                if end < sentence_length:
                    # 查找最后一个标点符号
                    punctuation = ['.', '!', '?', ';', '。', '！', '？', '；']
                    last_punc = -1
                    for p in punctuation:
                        pos = sentence.rfind(p, start, end)
                        if pos > last_punc:
                            last_punc = pos
                    if last_punc != -1:
                        end = last_punc + 1
                
                chunks.append(sentence[start:end])
                # 处理重叠
                if end < sentence_length:
                    start = max(end - chunk_overlap, start + 1)
                else:
                    start = end
            continue
        
        # 计算添加当前句子后的总长度（包括空格）
        new_length = current_chunk_length + sentence_length + (1 if current_chunk else 0)
        
        # 如果添加后超过限制，完成当前块并开始新块
        if new_length > chunk_size:
            # 保存当前块
            chunks.append(' '.join(current_chunk))
            
            # 处理重叠：从当前块末尾开始取句子，直到达到重叠大小
            overlap_chars = 0
            overlap_sentences = []
            
            # 从后往前遍历当前块的句子
            for sent in reversed(current_chunk):
                sent_len_with_space = len(sent) + 1  # +1 for space
                if overlap_chars + sent_len_with_space > chunk_overlap:
                    break
                overlap_chars += sent_len_with_space
                overlap_sentences.insert(0, sent)
            
            # 开始新块，包含重叠句子
            current_chunk = overlap_sentences
            current_chunk_length = sum(len(s) + 1 for s in current_chunk) - 1 if current_chunk else 0
        
        # 添加当前句子到块
        current_chunk.append(sentence)
        current_chunk_length = current_chunk_length + sentence_length + (1 if current_chunk_length > 0 else 0)
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

# 常量定义
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50

def main():
    # 读取测试文档
    doc_path = "/Volumes/H/python/RAG_Agent_learn/Day1/RAGDemo/chatWithNavar-2.md"
    
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