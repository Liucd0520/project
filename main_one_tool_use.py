from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import os  
from langchain.vectorstores import FAISS, Chroma
from tools import *
from langchain import hub
from langchain_openai import ChatOpenAI

from langgraph.prebuilt import create_react_agent
from models import llm_qwen_plus


tools = [get_datetime, # 查日期
        get_weather, # 查天气
        web_search, # 查网络
        get_city_name, get_address, # 查城市名、地址 
        get_knowledge, # 查政策知识
        navigation, # 导航 
        ]
prompt = """你是一个人工智能助手，能够使用一些工具来帮助用户完成任务。请以简洁的方式回答用户的问题。"""
graph = create_react_agent(llm_qwen_plus, tools=tools, )

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()


def main():
    
    while True:
        try:
            inputs = {"messages": [('system', '你是一个AI助手，请以简洁的方式回复用户，尽量不要超过100字。'), 
                                   ("user", input("User: "))]}
            print_stream(graph.stream(inputs, stream_mode="values"))
            
            # result = graph.invoke(inputs)
            # print(result)

            

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()

# 目前仅仅为单轮，需要实现多轮对话 --》 Redis

# 政策知识库查询 -> 固定问答对+政策自由问答
# 功能引导 --> 需要确定一下输出是什么，是标签，还是一段话
