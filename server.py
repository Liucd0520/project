from tools import *
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal
import uvicorn
from langgraph.prebuilt import create_react_agent
from models import llm_qwen_14b
import time  
from pydantic import BaseModel
from function_guide.prompt import prompt_router
from fastapi.middleware.cors import CORSMiddleware
from utils import *
from graphrag.graphrag_langchain import medical_graphrag



app = FastAPI()


# 存在问答与功能引导冲突的情况，比如我今天不舒服应该挂什么科
# 能否可以把调用的各个工具也《显示》在页面上方面用户操作

@app.post("/ai_assistant")
async def chat(query: str):
    logger.info(f"收到的查询问题： {query}")
    
    start_time = time.time()
    output = await router_chain.ainvoke({'query': query, 'function_module': function_module})
    logger.info(f"路由的输出: {output}")

    function_tags = [] # 初始为空，后面如果不为空会有新的赋值
    if output.grade == True:
        type = 'function'
        function_tags = await recommand_function(query=query)
        result = function_tags

    # 如果result为空（意味着大模型输出的功能列表与真实功能列表没有交集），则调用智能体
    if output.grade == False and len(function_tags) == 0:
        type = 'agent'
        inputs = {"messages": [
            ('system', '你是一个AI助手，请以简洁的方式回复用户。'), 
            ("user", query)]}
        
        response = await graph.ainvoke(inputs)
        result = response['messages'][-1].content
    
    cost_time = time.time() - start_time
    logger.info(f"查询的类型{type} 返回的结果: {result} 耗时：{cost_time:.2f}秒")

    return {'type': type, "response": result, 'cost_time': cost_time}



if __name__ == "__main__":

    class RouterBaseModel(BaseModel):
        grade: bool = Field(default=False, description="用户的问题是否可以通过APP里的应用服务功能来解决")
        
    router_prompt = PromptTemplate(
    template=prompt_router, 
    input_variables=["function_module",  "query"]
    )

    router_chain = create_structured_chain(
        prompt=router_prompt,
        model=llm_qwen_14b,
        structured_data=RouterBaseModel
    )

    tools = [get_datetime, # 查日期
        get_weather, # 查天气
        web_search, # 查网络
        get_city_name, get_address, # 查城市名、地址 
        get_knowledge, # 查政策知识
        navigation, # 导航 
        # medical_graphrag, # 医学知识查询  ！！！
    ]
    graph = create_react_agent(llm_qwen_14b, tools=tools, )

    df = pd.read_excel(config.function_path)
    function_module = df.to_html(index=False, justify='center', escape=False, na_rep='')

    uvicorn.run(app, host="0.0.0.0", port=9020)


# 目前仅仅为单轮，需要实现多轮对话 --》 Redis

# 待优化：
# embedding模型似乎不太像，没有openai的号，导致政策检索不出来
# 政策检索的文档解析没搞定，需要Qanything
# 模型目前部署在A100上，没有跑通1080Ti上的vllm部署
