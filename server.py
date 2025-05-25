from tools import *
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Literal
import uvicorn
from langgraph.prebuilt import create_react_agent
from models import llm_qwen_14b
import time  
from utils import create_structured_chain
from pydantic import BaseModel
from function_guide.prompt import prompt_router

app = FastAPI()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# 存在问答与功能引导冲突的情况，比如我今天不舒服应该挂什么科
# 能否可以把调用的各个工具也《显示》在页面上方面用户操作

@app.post("/ai_assistant")
async def chat(query: str):
    start_time = time.time()
    output = router_chain.invoke({'query': query, 'function_module': function_module})
    print(output)

    if output.grade == True:
        type = 'function'
        function_tags = recommand_function(query=query)
        result = function_tags
    else:
        type = 'agent'
        inputs = {"messages": [('system', '你是一个AI助手，请以简洁的方式回复用户，尽量不要超过100字。'), 
                            ("user", query)]}
        
        # print_stream(graph.stream(inputs, stream_mode="values"))
        response = await graph.ainvoke(inputs)
        result = response['messages'][-1].content
    
    return {'type': type, "response": result, 'cost_time': time.time() - start_time}



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
    ]
    graph = create_react_agent(llm_qwen_14b, tools=tools, )

    df = pd.read_excel(config.function_path)
    function_module = df.to_html(index=False, justify='center', escape=False, na_rep='')

    uvicorn.run(app, host="localhost", port=8000)


# 目前仅仅为单轮，需要实现多轮对话 --》 Redis

# 政策知识库查询 -> 固定问答对+政策自由问答
# 功能引导 --> 需要确定一下输出是什么，是标签，还是一段话
