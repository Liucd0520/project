from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import numpy as np 
from typing import List
from langchain_core.embeddings import Embeddings

llm_chatgpt = ChatOpenAI(model="gpt-3.5-turbo",temperature=0, api_key='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')
llm_deepseek = ChatOpenAI(model="deepseek-chat",
                    base_url='https://api.deepseek.com',
                    api_key='sk-84dd90701fe6471696cf24136d340a74',
                    temperature=0,
                    )

llm_qwen_plus = ChatOpenAI(model="qwen-plus",
                    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                    api_key='sk-4e27d583808849128b07458af74724a6',
                    temperature=0,
                    )

llm_qwen_14b = ChatOpenAI(model="Qwen2.5-14B-Instruct", #   Qwen2.5-14B
                    base_url='http://172.31.24.110:33079/v1', 
                    api_key='EMPTY',
                    temperature=0,
                    )

# 换成私有化模型
embedding_openai = OpenAIEmbeddings(
    api_key='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',
    )


# 私有模型
class LocalEmbeddingsVllm(Embeddings):
    """`Zhipuai Embeddings` embedding models."""

    def __init__(self, api_key, base_url):
        
        self.client_emb = OpenAI(api_key=api_key,
                    base_url=base_url)
   
    def embed_query(self, text: str) -> List[float]:
        
        embeddings = self.client_emb.embeddings.create(
            model="bge-large-embedding",
            input=text
        )
        return embeddings.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        
        return [self.embed_query(text) for text in texts]


openai_api_key_emb = "EMPTY"
openai_api_base_emb = 'http://172.31.24.111:8003/v1' # 'http://192.168.0.11:8076/v1' 

embedding_vllm = LocalEmbeddingsVllm(
    api_key=openai_api_key_emb,
    base_url=openai_api_base_emb
)

res = embedding_vllm.embed_query('你好')
# print(res)

res2 = llm_qwen_14b.invoke('讲个笑话')
print(res2)
