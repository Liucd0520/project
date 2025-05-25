from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_openai import OpenAI
import numpy as np 


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

llm_qwen_14b = ChatOpenAI(model="Qwen2.5-14B", #   Qwen2.5-14B
                    base_url='http://192.168.0.11:8011/v1', 
                    api_key='EMPTY',
                    temperature=0,
                    )

# 换成私有化模型
embedding_openai = OpenAIEmbeddings(api_key='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',
                             )

openai_api_key_emb = "EMPTY"
openai_api_base_emb = 'http://172.31.24.23:8002/v1' # 'http://192.168.0.11:8076/v1' 
client_emb = OpenAI(api_key=openai_api_key_emb,
                base_url=openai_api_base_emb
                )
# bge_model = OpenAIEmbeddings(client=client_emb, model='bge-large-embedding')

def embedding_bge(query_list):
    
    responses = client_emb.embeddings.create(
        input=query_list,
        model='bge-large-embedding',
    )
    return responses
    embedding_list = [output_data.embedding for output_data in  responses.data]
    
    return np.array(embedding_list)
