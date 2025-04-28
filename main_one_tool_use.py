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


tools = [get_datetime, get_weather, web_search, get_address, get_knowledge, navigation]


graph = create_react_agent(llm_qwen_plus, tools=tools)

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
            inputs = {"messages": [("user", input("User: "))]}
            print_stream(graph.stream(inputs, stream_mode="values"))
            
            # result = graph.invoke(inputs)
            # print(result)

            

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()

# 目前仅仅为单轮，需要实现多轮对话
