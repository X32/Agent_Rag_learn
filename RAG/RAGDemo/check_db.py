#!/usr/bin/env python3
# 检查向量数据库中的实际数据

import chromadb

# 连接到向量数据库
db_path = "./chroma_db"
collection_name = "learn_documents1"

print(f"连接到向量数据库: {db_path}")
client = chromadb.PersistentClient(path=db_path)

# 获取集合
print(f"获取集合: {collection_name}")
collection = client.get_collection(collection_name)

# 统计信息
print(f"集合中的文档块数: {collection.count()}")

# 获取所有文档块
print("\n获取所有文档块的ID和大小:")
results = collection.get(include=["documents"])

docs = results["documents"]
ids = results["ids"]

for i, (doc_id, doc) in enumerate(zip(ids, docs)):
    print(f"块 {i+1} ({doc_id}): {len(doc)} 字符")
    
    # 显示前100字符
    if i < 3:  # 只显示前3个块的内容预览
        print(f"  内容预览: {doc[:100]}...")

# 检查是否有重复的块
print(f"\n是否有重复的文档块: {len(set(docs)) != len(docs)}")