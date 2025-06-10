
# 我想将该路径添加到项目路径中，从而可以在当前文件运行py文件
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
# from langchain_community.vectorstores import Milvus
from langchain_milvus import Milvus
from langchain_community.vectorstores import FAISS
import config
from models import  embedding_vllm

import os 
import time 

def pdf_split(file_path):
    """
    将pdf文件拆分为合适的大小
    :param file_path: pdf文件路径
    :return: 拆分后的文档列表
    """
    # 初始化pdf 文档加载器
    loader = PyPDFLoader(file_path=file_path)
    # 将pdf中的文档解析为 langchain 的document对象
    documents = loader.load()
    # 将文档拆分为合适的大小
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=100)

    docs = text_splitter.split_documents(documents)

    return docs


def faiss_dump(policy_dir):
    all_documents = []
    for file_name in os.listdir(policy_dir):
        if not file_name.endswith('.pdf'):
            continue

        file_path = os.path.join(policy_dir, file_name)
        print(file_path)
        documents = pdf_split(file_path)
        if len(documents) == 0:
            continue
        all_documents.extend(documents)

        
        
                            
    
    # vector = Milvus.from_documents(
    #     documents=documents, # 设置保存的文档
    #     embedding=embedding, # 设置 embedding model
    #     collection_name="book", # 设置 集合名称
    #     drop_old=True,
    #     connection_args={
    #     "uri": "./milvus_demo.db",
    #     },
    #     # connection_args={"host": "172.31.24.111", "port": "19534"},# Milvus连接配置
    # )

    vector = FAISS.from_documents(all_documents, embedding_vllm)
    
    vector.save_local("faiss_index")
    print('存库结束 ...')

    return vector

if __name__ == "__main__":
    # pdf_split(config.policy_dir)
    faiss_dump(config.policy_dir)
    


    # start = time.time()
    # vector = FAISS.load_local("faiss_index", embedding_vllm,  allow_dangerous_deserialization=True)

    # result = vector.similarity_search_with_score("我今年82岁了，我能享受什么养老政策", k=5,)
    # print(result)
