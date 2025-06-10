from langchain_community.vectorstores import FAISS
from datetime import datetime
from models import embedding_vllm
from langchain_core.documents import BaseDocumentTransformer, Document
import json 


from py2neo import Graph

graph = Graph("bolt://172.31.24.111:7687", auth=("neo4j", "liucd123"))

entity_types = ["Disease", "Symptom", "Drug", "Check", "Department", "Food", "Producer"]
names_by_type = {}
# 获取所有实体及其对应的值
for entity in entity_types:
    query = f"MATCH (n:{entity})  RETURN n.name AS name"
    result = graph.run(query).data()
    names_by_type[entity] = [record['name'] for record in result]


full_Document = []
for entity, values in names_by_type.items():
    for value in values:
        full_Document.append(Document(page_content=value, metadata={'source': entity}))
print(len(full_Document))
print(full_Document[:3])

vector = FAISS.from_documents(full_Document, embedding_vllm)
    
vector.save_local("faiss_index_entity")
print('存库结束 ...')

docs = vector.similarity_search('百日咳', k=3,)
print(docs)
