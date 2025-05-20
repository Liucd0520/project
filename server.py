from tools import *
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal
import uvicorn
from langgraph.prebuilt import create_react_agent
from models import llm_qwen_14b
import time  

app = FastAPI()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
            
@app.post("/chat")
async def chat(query: str):
    inputs = {"messages": [('system', '你是一个AI助手，请以简洁的方式回复用户，尽量不要超过100字。'), 
                           ("user", query)]}
    
    # print_stream(graph.stream(inputs, stream_mode="values"))
    start_time = time.time()
    result = await graph.ainvoke(inputs)
    
    
    return {"response": result, 'cost_time': time.time() - start_time}



if __name__ == "__main__":

    tools = [get_datetime, # 查日期
        get_weather, # 查天气
        web_search, # 查网络
        get_city_name, get_address, # 查城市名、地址 
        get_knowledge, # 查政策知识
        navigation, # 导航 
    ]
    graph = create_react_agent(llm_qwen_14b, tools=tools, )

    uvicorn.run(app, host="localhost", port=8000)


# 目前仅仅为单轮，需要实现多轮对话 --》 Redis

# 政策知识库查询 -> 固定问答对+政策自由问答
# 功能引导 --> 需要确定一下输出是什么，是标签，还是一段话
