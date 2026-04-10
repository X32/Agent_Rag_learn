#!/usr/bin/env python3
# 列出向量数据库中的所有集合

import chromadb

# 连接到向量数据库
db_path = "./chroma_db"

print(f"连接到向量数据库: {db_path}")
client = chromadb.PersistentClient(path=db_path)

# 获取所有集合
collections = client.list_collections()
print(f"数据库中的集合数: {len(collections)}")

for collection in collections:
    print(f"- 集合名称: {collection.name}, 文档块数: {collection.count()}")