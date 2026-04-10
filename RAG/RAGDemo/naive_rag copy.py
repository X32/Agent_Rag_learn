"""
Naive RAG Pipeline 实现（FAISS 版本）
基于 learn.txt 文本文件的简单检索增强生成示例

RAG (Retrieval-Augmented Generation) 检索增强生成：
1. 将文档分块并向量化存储到向量数据库
2. 用户提问时，先检索相关文档块
3. 将检索到的上下文和问题一起交给大模型生成回答

核心流程：文档处理 → 向量化 → 存储 → 检索 → 生成
"""

import os
import pickle            # 用于序列化 Python 对象，存储文档块和元数据
import numpy as np       # 数值计算库，用于向量运算
from typing import List, Tuple
from dotenv import load_dotenv

# 向量化和向量存储
from sentence_transformers import SentenceTransformer  # HuggingFace 的句子嵌入模型，用于将文本转换为向量
import faiss         # Facebook AI 向量检索库，用于存储和搜索向量

# 大模型接口
from openrouter import OpenRouter  # OpenRouter API 客户端，用于访问各种大语言模型
import re

# 加载环境变量（从 .env 文件读取 API 密钥等配置）
load_dotenv()

# ============================================================
# 1. 默认配置参数
# ============================================================

# 文本分块默认配置
DEFAULT_CHUNK_SIZE = 400      # 每个文本块的字符数（控制分块大小，影响检索精度）
DEFAULT_CHUNK_OVERLAP = 200    # 相邻块之间的重叠字符数（避免信息被切断，保持上下文连贯性）

# 检索默认配置
DEFAULT_TOP_K = 5             # 检索时返回最相关的 K 个文档块（数量影响上下文长度和信息量）

# Embedding 模型默认配置
DEFAULT_EMBEDDING_MODEL = "moka-ai/m3e-base"  # 中文场景推荐模型，512 维向量
                                              # 备选："bge-large-zh-v1.5" 或 "paraphrase-multilingual-MiniLM-L12-v2"

# 向量数据库默认配置
DEFAULT_INDEX_PATH = "./faiss_index/index.faiss"    # FAISS 索引文件存储路径
DEFAULT_METADATA_PATH = "./faiss_index/metadata.pkl"  # 元数据（文档块）存储路径

# ============================================================
# 2. 文本分块函数
# ============================================================

import nltk
from nltk.tokenize import sent_tokenize

# 下载必要的 nltk 资源（只需要运行一次）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def split_chinese_sentences(text: str) -> List[str]:
    """
    中文句子分割，支持中英文混排

    分割规则：
    - 中文句末标点：。！？！？‼️⁇⁈⁉
    - 英文句末标点：.!?
    - 换行符也作为分割点（访谈录中段落是自然语义单元）

    参数:
        text: 要分割的文本
    返回:
        List[str]: 分割后的句子列表
    """
    if not text:
        return []

    # 首先按换行符分割，保留段落结构
    lines = text.split('\n')

    sentences = []
    # 中文句末标点模式（包括中英文）
    eos_pattern = r'([.!?。！？])(\s*[)"\'\u300d\u300f\u300e\u300c]?)'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过纯标题行（以 # 开头）
        if line.startswith('#'):
            sentences.append(line)
            continue

        # 跳过 Markdown 表格行
        if line.startswith('|') or line.startswith('-|'):
            sentences.append(line)
            continue

        # 对普通文本进行句子分割
        parts = re.split(eos_pattern, line)

        # 重新组合：parts 会是 [内容 1, 标点 1, 后缀 1, 内容 2, 标点 2, 后缀 2, ...]
        current_sentence = ""
        i = 0
        while i < len(parts):
            current_sentence += parts[i]
            if i + 2 < len(parts):  # 有标点和一个后缀
                current_sentence += parts[i + 1] + parts[i + 2]
                sentences.append(current_sentence.strip())
                current_sentence = ""
            i += 3

        # 添加剩余部分
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

    # 过滤空句子
    return [s for s in sentences if s.strip()]


def chunk_text_optimized(text: str, chunk_size: int = 500, chunk_overlap: int = 150) -> List[str]:
    """
    优化的文本分块函数，专门针对访谈录等段落型文档

    优化特性：
    1. 使用中文句子分割，正确处理中文标点
    2. 按章节切分（## 开头），保持章节完整性
    3. 识别强调内容（**...**），确保不被截断
    4. 优先保持段落完整性（访谈录中段落是自然语义单元）
    5. 每个块包含章节标题作为上下文

    参数:
        text: 要分块的文本
        chunk_size: 每个块的最大字符数（默认 500，适合访谈录段落）
        chunk_overlap: 相邻块之间的重叠字符数（默认 150）

    返回:
        List[str]: 分块后的文本列表
    """
    if not text:
        return []

    # 1. 按## 章节分割（只识别## 及更高级别，忽略# 大标题）
    chapters = re.split(r'\n(?=##\s)', text)
    chapters = [ch.strip() for ch in chapters if ch.strip()]

    # 如果没有章节，使用改进的段落切分
    if len(chapters) <= 1:
        return chunk_text_by_paragraph(text, chunk_size, chunk_overlap)

    chunks = []
    current_chapter_title = ""

    for chapter in chapters:
        chapter = chapter.strip()
        if not chapter:
            continue

        # 提取章节标题（第一行）
        first_line = chapter.split('\n')[0].strip()
        if first_line.startswith('##'):
            current_chapter_title = first_line
        elif first_line.startswith('#'):
            # 跳过一级标题（如"# 第一部分"），继续使用上一个二级标题
            pass

        # 获取章节内容（去掉标题行）
        lines = chapter.split('\n')
        if len(lines) > 1 and lines[0].strip().startswith('#'):
            chapter_content = '\n'.join(lines[1:])
        else:
            chapter_content = chapter

        # 跳过只有标题没有内容的章节
        if not chapter_content.strip():
            continue

        # 2. 按段落分割
        paragraphs = re.split(r'\n\s*\n', chapter_content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        if not paragraphs:
            continue

        # 3. 合并段落成块，每个块带上章节标题
        current_chunk_parts = []
        current_chunk_length = 0

        for para in paragraphs:
            para_length = len(para)

            # 如果段落本身就超过 chunk_size，需要拆分
            if para_length > chunk_size:
                # 先保存当前块
                if current_chunk_parts:
                    chunk_text = '\n\n'.join(current_chunk_parts)
                    if current_chapter_title:
                        chunk_text = f"{current_chapter_title}\n\n{chunk_text}"
                    chunks.append(chunk_text)
                    current_chunk_parts = []
                    current_chunk_length = 0

                # 拆分超长段落
                sub_chunks = split_long_paragraph(para, chunk_size, chunk_overlap)
                for sub_chunk in sub_chunks:
                    if current_chapter_title:
                        chunks.append(f"{current_chapter_title}\n\n{sub_chunk}")
                    else:
                        chunks.append(sub_chunk)
                continue

            # 检查添加段落后是否超过限制
            new_length = current_chunk_length + para_length + 2  # +2 for \n\n

            if new_length > chunk_size and current_chunk_parts:
                # 保存当前块
                chunk_text = '\n\n'.join(current_chunk_parts)
                if current_chapter_title:
                    chunk_text = f"{current_chapter_title}\n\n{chunk_text}"
                chunks.append(chunk_text)

                # 处理重叠：保留最近的段落
                overlap_chars = 0
                overlap_parts = []
                for p in reversed(current_chunk_parts):
                    if overlap_chars + len(p) + 2 > chunk_overlap:
                        break
                    overlap_chars += len(p) + 2
                    overlap_parts.insert(0, p)

                current_chunk_parts = overlap_parts
                current_chunk_length = sum(len(p) + 2 for p in current_chunk_parts) - 2 if current_chunk_parts else 0

            # 添加当前段落
            current_chunk_parts.append(para)
            current_chunk_length += para_length + 2

        # 添加最后一个块
        if current_chunk_parts:
            chunk_text = '\n\n'.join(current_chunk_parts)
            if current_chapter_title:
                chunk_text = f"{current_chapter_title}\n\n{chunk_text}"
            chunks.append(chunk_text)

    return chunks


def chunk_text_by_paragraph(text: str, chunk_size: int = 500, chunk_overlap: int = 150) -> List[str]:
    """
    按段落分块，适用于没有章节结构的文档

    参数:
        text: 要分块的文本
        chunk_size: 每个块的最大字符数
        chunk_overlap: 相邻块之间的重叠字符数

    返回:
        List[str]: 分块后的文本列表
    """
    if not text:
        return []

    # 按段落分割
    paragraphs = re.split(r'\n\s*\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    if not paragraphs:
        return []

    chunks = []
    current_chunk_parts = []
    current_chunk_length = 0

    for para in paragraphs:
        para_length = len(para)

        # 如果段落本身就超过 chunk_size，需要拆分
        if para_length > chunk_size:
            if current_chunk_parts:
                chunks.append('\n\n'.join(current_chunk_parts))
                current_chunk_parts = []
                current_chunk_length = 0

            sub_chunks = split_long_paragraph(para, chunk_size, chunk_overlap)
            chunks.extend(sub_chunks)
            continue

        new_length = current_chunk_length + para_length + 2

        if new_length > chunk_size and current_chunk_parts:
            chunks.append('\n\n'.join(current_chunk_parts))

            # 处理重叠
            overlap_chars = 0
            overlap_parts = []
            for p in reversed(current_chunk_parts):
                if overlap_chars + len(p) + 2 > chunk_overlap:
                    break
                overlap_chars += len(p) + 2
                overlap_parts.insert(0, p)

            current_chunk_parts = overlap_parts
            current_chunk_length = sum(len(p) + 2 for p in current_chunk_parts) - 2 if current_chunk_parts else 0

        current_chunk_parts.append(para)
        current_chunk_length += para_length + 2

    if current_chunk_parts:
        chunks.append('\n\n'.join(current_chunk_parts))

    return chunks


def split_long_paragraph(paragraph: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    拆分超长段落，尽量在句子边界处分割

    参数:
        paragraph: 要拆分的段落
        chunk_size: 每个块的最大字符数
        chunk_overlap: 重叠字符数

    返回:
        List[str]: 拆分后的块列表
    """
    if len(paragraph) <= chunk_size:
        return [paragraph]

    chunks = []
    start = 0

    while start < len(paragraph):
        end = min(start + chunk_size, len(paragraph))

        if end >= len(paragraph):
            # 最后一段
            chunks.append(paragraph[start:end])
            break

        # 尝试在句子边界处分割
        # 中文句末标点
        punctuation = '.!??.!?‼️⁇⁈⁉!?。！？'
        best_split = -1
        for p in punctuation:
            pos = paragraph.rfind(p, start, end)
            if pos > best_split:
                best_split = pos

        if best_split > start + chunk_size * 0.3:  # 至少在 30% 位置之后
            end = best_split + 1

        chunks.append(paragraph[start:end])

        # 处理重叠
        if end < len(paragraph):
            start = max(end - chunk_overlap, start + 1)
        else:
            break

    return chunks

def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """
    将文本分割成指定大小的块，支持块间重叠，保持句子完整性

    参数:
        text: 要分块的文本
        chunk_size: 每个文本块的最大字符数
        chunk_overlap: 相邻块之间的重叠字符数

    返回:
        List[str]: 分块后的文本列表
    """
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


# ============================================================
# 3. FAISS 向量数据库操作
# ============================================================

class NaiveRAG:
    def __init__(self,
                 index_path: str = DEFAULT_INDEX_PATH,
                 metadata_path: str = DEFAULT_METADATA_PATH,
                 embedding_model: str = DEFAULT_EMBEDDING_MODEL,
                 chunk_size: int = DEFAULT_CHUNK_SIZE,
                 chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
                 top_k: int = DEFAULT_TOP_K):
        """
        初始化 RAG 系统（FAISS 版本）

        参数:
            index_path: FAISS 索引文件存储路径
            metadata_path: 元数据（文档块）存储路径
            embedding_model: 用于生成向量的模型名称
            chunk_size: 文本分块大小
            chunk_overlap: 文本分块重叠大小
            top_k: 默认检索返回的文档块数量
        """
        # 存储配置参数
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k

        # 存储文档块和元数据的列表
        self.chunks: List[str] = []
        self.metadatas: List[dict] = []

        # FAISS 索引对象
        self.index = None

        # 懒加载 Embedding 模型（只在需要时才加载）
        self._embed_model = None
        self._embedding_dim = None

        # 加载或创建 FAISS 索引
        self._load_or_create_index()

    @property
    def embed_model(self):
        """懒加载 Embedding 模型"""
        if self._embed_model is None:
            print(f"🔄 加载 Embedding 模型：{self.embedding_model}")
            self._embed_model = SentenceTransformer(self.embedding_model)
            self._embedding_dim = self._embed_model.get_sentence_embedding_dimension()
            print(f"✅ Embedding 维度：{self._embedding_dim}")
        return self._embed_model

    @property
    def embedding_dim(self):
        """懒加载 Embedding 维度"""
        if self._embedding_dim is None:
            _ = self.embed_model  # 触发加载
        return self._embedding_dim

    def _load_or_create_index(self):
        """
        从磁盘加载 FAISS 索引，如果不存在则创建新的索引
        """
        # 检查索引文件是否存在
        index_exists = os.path.exists(self.index_path)
        metadata_exists = os.path.exists(self.metadata_path)

        if index_exists and metadata_exists:
            # 两个文件都存在，加载现有索引（不需要加载 embedding 模型）
            print(f"🔄 从磁盘加载 FAISS 索引：{self.index_path}")
            self.index = faiss.read_index(self.index_path)

            print(f"🔄 从磁盘加载元数据：{self.metadata_path}")
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data.get('chunks', [])
                self.metadatas = data.get('metadatas', [])

            print(f"✅ 加载完成，当前文档块数：{len(self.chunks)}")
        else:
            # 文件不存在，创建新的索引（需要加载 embedding 模型获取维度）
            print("🔄 创建新的 FAISS 索引")
            # 创建 L2 距离的索引（欧几里得距离）
            # self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.chunks = []
            self.metadatas = []
            print("✅ 新索引创建完成")

    def _save_index(self):
        """
        保存 FAISS 索引和元数据到磁盘
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # 保存 FAISS 索引
        faiss.write_index(self.index, self.index_path)
        print(f"💾 FAISS 索引已保存到：{self.index_path}")
        #打印元数据
        print(f"✅ 元数据已保存，当前文档块数：{len(self.chunks)}")

        # 打印第一个文档块和元数据（仅当有数据时）
        if self.chunks:
            print(f"第一个文档块：{self.chunks[0]}")
            print(f"第一个文档块的元数据：{self.metadatas[0]}")



        # 保存元数据
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'metadatas': self.metadatas
            }, f)
        print(f"💾 元数据已保存到：{self.metadata_path}")

    def index_document(self, file_path: str, replace_existing: bool = False) -> int:
        """
        索引文档：读取、分块、向量化、存储

        参数:
            file_path: 要索引的文档路径
            replace_existing: 如果文档已存在，是否替换现有索引

        返回:
            int: 索引的文档块数

        异常:
            FileNotFoundError: 当文件不存在时
            IOError: 当文件读取失败时
            Exception: 当索引过程中发生其他错误时
        """
        # 输入验证
        if not file_path:
            raise ValueError("文件路径不能为空")

        # 读取文档
        print(f"📄 读取文档：{file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ 文件不存在：{file_path}")
        except IOError as e:
            raise IOError(f"❌ 文件读取失败：{str(e)}")

        # 检查是否已存在该文档的索引
        doc_name = os.path.basename(file_path)
        existing_indices = []

        # 查找该文档已有的块
        for i, meta in enumerate(self.metadatas):
            if meta.get('source') == doc_name:
                existing_indices.append(i)

        if existing_indices:
            if replace_existing:
                print(f"🔄 文档 '{doc_name}' 已存在 {len(existing_indices)} 个块，正在替换...")
                # 标记要删除的索引（从后往前删除，避免索引变化）
                for i in sorted(existing_indices, reverse=True):
                    # FAISS 不支持直接删除，需要重建索引
                    pass
                # 简单方案：过滤掉要删除的文档，重建整个索引
                self._rebuild_index_excluding(doc_name)
                print("🗑️  已删除现有索引")
            else:
                print(f"⚠️  文档 '{doc_name}' 已存在 {len(existing_indices)} 个块，跳过索引")
                return 0

        # 分块 - 使用优化的分块函数
        chunks = chunk_text_optimized(text, self.chunk_size, self.chunk_overlap)
        print(f"📦 分块完成：{len(chunks)} 个块")

        # 生成 embedding
        print("🔄 生成向量...")
        try:
            embeddings = self.embed_model.encode(chunks)
            # FAISS 需要 float32 类型的 numpy 数组
            embeddings = np.array(embeddings).astype('float32')
            # 归一化向量（用于余弦相似度）
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        except Exception as e:
            raise Exception(f"❌ 向量生成失败：{str(e)}")

        # 添加到 FAISS 索引
        try:
            # FAISS add 会自动分配连续的 ID
            self.index.add(embeddings)
        except Exception as e:
            raise Exception(f"❌ 向量存储失败：{str(e)}")

        # 添加文档块和元数据
        for i, chunk in enumerate(chunks):
            self.chunks.append(chunk)
            self.metadatas.append({"source": doc_name, "chunk_id": len(self.chunks) - 1})

        # 保存到磁盘
        self._save_index()

        print(f"✅ 索引完成，总块数：{len(self.chunks)}")
        return len(chunks)

    def _rebuild_index_excluding(self, source_name: str):
        """
        重建索引，排除指定来源的文档

        参数:
            source_name: 要排除的文档来源名称
        """
        # 收集要保留的索引、块和元数据
        new_chunks = []
        new_metadatas = []

        for chunk, meta in zip(self.chunks, self.metadatas):
            if meta.get('source') != source_name:
                new_chunks.append(chunk)
                new_metadatas.append(meta)

        # 重新生成 embeddings
        if new_chunks:
            embeddings = self.embed_model.encode(new_chunks)
            embeddings = np.array(embeddings).astype('float32')
            # 归一化向量（用于余弦相似度）
            embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            # 创建新索引（使用内积）
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            self.index.add(embeddings)
        else:
            # 如果没有文档了，创建空索引
            self.index = faiss.IndexFlatIP(self.embedding_dim)

        # 更新存储
        self.chunks = new_chunks
        self.metadatas = new_metadatas

    def add_documents(self, documents: List[str], metadatas: List[dict] = None):
        """
        直接添加文档块到索引中（支持增量添加）

        参数:
            documents: 文档块列表
            metadatas: 元数据列表（可选）
        """
        if not documents:
            return

        print(f"🔄 添加 {len(documents)} 个文档块...")

        # 生成 embeddings
        embeddings = self.embed_model.encode(documents)
        embeddings = np.array(embeddings).astype('float32')
        # 归一化向量（用于余弦相似度）
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

        # 添加到 FAISS 索引
        self.index.add(embeddings)

        # 添加到文档块列表
        for i, doc in enumerate(documents):
            self.chunks.append(doc)
            if metadatas:
                self.metadatas.append(metadatas[i])
            else:
                self.metadatas.append({"chunk_id": len(self.chunks) - 1})

        # 保存到磁盘
        self._save_index()

        print(f"✅ 添加完成，总块数：{len(self.chunks)}")

    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[str, float]]:
        """
        检索相关文档块
        返回：[(文档块，相似度分数), ...]

        参数:
            query: 查询文本
            top_k: 返回的相关文档块数量（默认为初始化时设置的值）

        返回:
            List[Tuple[str, float]]: 文档块和相似度分数的列表

        异常:
            ValueError: 当查询为空或 top_k 无效时
            Exception: 当检索过程中发生错误时
        """
        # 输入验证
        if not query:
            raise ValueError("查询文本不能为空")

        # 使用默认值如果 top_k 为 None
        if top_k is None:
            top_k = self.top_k

        if top_k <= 0:
            raise ValueError("top_k 必须大于 0")

        # 检查索引是否为空
        if self.index.ntotal == 0:
            return []

        # 限制 top_k 不超过总文档数
        top_k = min(top_k, self.index.ntotal)

        try:
            # 查询向量化
            query_embedding = self.embed_model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')

            # 归一化查询向量（用于余弦相似度）
            query_embedding = query_embedding / np.linalg.norm(query_embedding)

            # FAISS 检索（返回余弦相似度和索引）
            distances, indices = self.index.search(query_embedding, top_k)

            # 整理结果
            retrieved = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.chunks):  # 确保索引有效
                    # 检查距离是否为 NaN 或无穷大
                    if not np.isnan(dist) and not np.isinf(dist):
                        retrieved.append((self.chunks[idx], float(dist)))

            return retrieved
        except Exception as e:
            raise Exception(f"❌ 检索失败：{str(e)}")

    def build_context(self, query: str, top_k: int = None) -> str:
        """
        构建上下文字符串

        参数:
            query: 查询文本
            top_k: 使用的相关文档块数量（默认为初始化时设置的值）

        返回:
            str: 构建好的上下文字符串

        异常:
            ValueError: 当查询为空时
            Exception: 当构建上下文过程中发生错误时
        """
        # 输入验证
        if not query:
            raise ValueError("查询文本不能为空")

        # 使用默认值如果 top_k 为 None
        if top_k is None:
            top_k = self.top_k

        try:
            results = self.retrieve(query, top_k)
            context = "\n\n---\n\n".join([doc for doc, _ in results])
            return context
        except Exception as e:
            raise Exception(f"❌ 上下文构建失败：{str(e)}")

    def query(self, query: str, top_k: int = None) -> dict:
        """
        执行完整查询：检索 + 返回结果

        参数:
            query: 查询文本
            top_k: 返回的相关文档块数量（默认为初始化时设置的值）

        返回:
            dict: 查询结果，包含查询文本、上下文、距离和上下文文本

        异常:
            ValueError: 当查询为空时
            Exception: 当查询过程中发生错误时
        """
        # 输入验证
        if not query:
            raise ValueError("查询文本不能为空")

        # 使用默认值如果 top_k 为 None
        if top_k is None:
            top_k = self.top_k

        try:
            results = self.retrieve(query, top_k)

            return {
                "query": query,
                "contexts": [doc for doc, _ in results],
                "distances": [dist for _, dist in results],
                "context_text": "\n\n---\n\n".join([doc for doc, _ in results])
            }
        except Exception as e:
            raise Exception(f"❌ 查询失败：{str(e)}")

    def clear(self):
        """
        清空向量库

        异常:
            Exception: 当清空向量库过程中发生错误时
        """
        try:
            # 重建空索引
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.chunks = []
            self.metadatas = []

            # 保存到磁盘
            self._save_index()

            print("🗑️ 向量库已清空")
        except Exception as e:
            raise Exception(f"❌ 清空向量库失败：{str(e)}")

    def get_stats(self) -> dict:
        """
        获取索引统计信息

        返回:
            dict: 包含索引统计信息的字典
        """
        return {
            "total_chunks": len(self.chunks),
            "index_size": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "index_path": self.index_path,
            "metadata_path": self.metadata_path
        }


# ============================================================
# 4. 简单的 LLM 接口（可选）
# ============================================================

def generate_answer_with_context(query: str, context: str, model: str = "openai/gpt-5.4") -> str:
    """
    使用上下文生成回答
    通过 OpenRouter 调用大模型

    参数:
        query: 用户的问题
        context: 用于回答问题的上下文信息
        model: 使用的大语言模型名称（默认为 openai/gpt-5.4）

    返回:
        str: 大模型生成的回答

    异常:
        ValueError: 当 OPENROUTER_API_KEY 环境变量未设置时
        Exception: 当调用大模型时发生错误时
    """
    # 检查 API 密钥是否存在
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("请设置 OPENROUTER_API_KEY 环境变量")

    # 构建提示词模板
    prompt = f"""基于以下上下文回答问题。如果上下文中没有相关信息，请说明。

上下文：
{context}

问题：{query}

回答："""

    with OpenRouter(api_key=api_key) as client:
        response = client.chat.send(
            model=model,  # 使用函数参数传入的模型
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content


# ============================================================
# 5. 主程序
# ============================================================

def main():
    """
    主程序入口，演示 NaiveRAG 的基本功能
    包括：初始化、索引文档、测试查询和交互式查询
    """
    try:
        # 初始化 RAG
        rag = NaiveRAG()

        if rag.chunks:
            print(f"第一个文档块：{rag.chunks[0][:100]}...")
            print(f"第一个文档块的元数据：{rag.metadatas[0]}")
        else:
            print("📭 当前没有索引的文档")

        # 打印统计信息
        stats = rag.get_stats()
        print(f"📊 索引统计：{stats['total_chunks']} 个文档块，维度：{stats['embedding_dim']}")
    except Exception as e:
        print(f"❌ 初始化失败：{str(e)}")
        return

    # 交互式菜单
    print("\n" + "="*60)
    print("🤖 RAG 交互系统")
    print("="*60)

    while True:
        try:
            print("\n" + "-"*40)
            print("请选择操作：")
            print("1. 添加新文档（文件或目录）")
            print("2. 查询文档")
            print("3. 查看统计信息")
            print("4. 清空索引")
            print("5. 退出")
            print("-"*40)

            choice = input("\n请输入选项 (1-5): ").strip()

            if choice == '1':
                # 添加新文档
                path = input("请输入文件或目录路径: ").strip()
                
                if not path:
                    print("❌ 路径不能为空")
                    continue

                if not os.path.exists(path):
                    print(f"❌ 路径不存在：{path}")
                    continue

                if os.path.isfile(path):
                    # 添加单个文件
                    print(f"\n📄 正在索引文件：{path}")
                    try:
                        chunk_count = rag.index_document(path)
                        print(f"✅ 索引完成，添加了 {chunk_count} 个文档块")
                        
                        # 更新统计信息
                        stats = rag.get_stats()
                        print(f"📊 当前总文档块数：{stats['total_chunks']}")
                    except Exception as e:
                        print(f"❌ 索引失败：{str(e)}")

                elif os.path.isdir(path):
                    # 添加目录中的所有文件
                    print(f"\n📁 正在扫描目录：{path}")
                    
                    # 获取目录中的所有文件
                    files = []
                    for item in os.listdir(path):
                        item_path = os.path.join(path, item)
                        if os.path.isfile(item_path):
                            files.append(item_path)
                    
                    if not files:
                        print("❌ 目录中没有文件")
                        continue

                    print(f"📋 找到 {len(files)} 个文件")
                    
                    # 询问是否继续
                    confirm = input(f"是否索引这 {len(files)} 个文件？(y/n): ").strip().lower()
                    if confirm != 'y':
                        print("❌ 已取消索引")
                        continue

                    # 索引所有文件
                    total_chunks = 0
                    success_count = 0
                    failed_files = []

                    for file_path in files:
                        try:
                            print(f"\n📄 正在索引：{os.path.basename(file_path)}")
                            chunk_count = rag.index_document(file_path)
                            total_chunks += chunk_count
                            success_count += 1
                            print(f"✅ 成功添加 {chunk_count} 个文档块")
                        except Exception as e:
                            print(f"❌ 索引失败：{str(e)}")
                            failed_files.append((file_path, str(e)))

                    # 显示摘要
                    print("\n" + "="*60)
                    print("� 索引摘要")
                    print("="*60)
                    print(f"✅ 成功索引文件数：{success_count}/{len(files)}")
                    print(f"📦 总共添加文档块数：{total_chunks}")
                    
                    if failed_files:
                        print(f"\n❌ 失败的文件：")
                        for file_path, error in failed_files:
                            print(f"  - {os.path.basename(file_path)}: {error}")

                    # 更新统计信息
                    stats = rag.get_stats()
                    print(f"\n📊 当前总文档块数：{stats['total_chunks']}")

            elif choice == '2':
                # 查询文档
                user_query = input("\n请输入问题：").strip()
                
                if not user_query:
                    print("❌ 问题不能为空")
                    continue

                result = rag.query(user_query, top_k=3)

                print(f"\n📚 检索到 {len(result['contexts'])} 个相关块:")
                print("-" * 40)

                contexts = result["contexts"]
                distances = result["distances"]

                for i in range(len(contexts)):
                    ctx = contexts[i]
                    dist = distances[i]

                    block_number = i + 1
                    formatted_distance = f"{dist:.4f}"

                    print(f"\n[块 {block_number}] (相似度距离：{formatted_distance})")

                    # if len(ctx) > 300:
                    #     display_text = ctx[:300] + "..."
                    # else:
                    #    display_text = ctx
                    display_text = ctx

                    print("_" * 40)
                    print(display_text)

                # 调用大模型生成回答
                print("\n🤖 AI 回答:")
                print("-" * 40)
                answer = generate_answer_with_context(user_query, result["context_text"])
                print(answer)

            elif choice == '3':
                # 查看统计信息
                stats = rag.get_stats()
                print("\n" + "="*60)
                print("📊 索引统计信息")
                print("="*60)
                print(f"📦 总文档块数：{stats['total_chunks']}")
                print(f"📐 向量维度：{stats['embedding_dim']}")
                print(f"💾 索引路径：{stats['index_path']}")
                print(f"📋 元数据路径：{stats['metadata_path']}")
                
                # 显示文档来源统计
                if rag.metadatas:
                    from collections import Counter
                    doc_stats = Counter(meta['source'] for meta in rag.metadatas)
                    print(f"\n📄 文档来源统计：")
                    for source, count in doc_stats.items():
                        print(f"  - {source}: {count} 个块")

            elif choice == '4':
                # 清空索引
                confirm = input("确定要清空所有索引吗？(y/n): ").strip().lower()
                if confirm == 'y':
                    rag.clear()
                    print("✅ 索引已清空")
                else:
                    print("❌ 已取消清空")

            elif choice == '5':
                # 退出
                print("\n👋 再见!")
                break

            else:
                print("❌ 无效选项，请重新输入")

        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 操作失败：{str(e)}")
            print("请检查您的输入或系统配置后重试")

        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 交互查询失败：{str(e)}")
            print("请检查您的输入或系统配置后重试")


if __name__ == "__main__":
    main()
