from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
# from langchain.embeddings.openai import OpenAIEmbeddings
import os  
# from langchain.vectorstores import FAISS, Chroma
from tools import *
from langchain import hub
from typing import List
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
from models import llm_chatgpt, llm_deepseek, llm_qwen_plus
from typing import Union
from typing import List
from typing_extensions import TypedDict


tools = [get_datetime, get_weather, web_search, get_address, get_knowledge, navigation]
llm = llm_qwen_plus


graph = create_react_agent(llm, tools=tools)


class ReWOO(TypedDict):
    message: str
    steps: List = []
    results: dict = {}
    result: str = ""


tools_instructions =  [
    """Tool(
        name="日期时间查询",
        func=get_datetime,
        description="当需要查询当前的时间时才使用此工具"
    )""",
    """Tool(
        name="天气查询",
        func=get_weather,
        description="当查询天气时才使用此工具. 输入：city_name: 城市的名称，例如：北京市，虞城县，浦东新区，如果不含有“市”、“县”等后缀，需要加上后缀。"
    )""",
    """Tool(
        name="网络搜索",
        func=web_search,
        description="当需要联网搜索获取实时信息时，调用此工具。"
    )""",
    """Tool(
        name="地址查询",
        func=get_address,
        description="当查询某个具体位置时才使用此工具.。"
    )""",
    """Tool(
        name="导航查询",
        func=navigation,
        description="当需要查询两地之间的导航信息时，调用此工具."
    )""",
    """Tool(
        name="中国政策信息查询",
        func=get_knowledge,
        description="当查询关于政策方面的知识时，调用此工具."
    )"""
]



#---------------------planner--------------------------------
class Plan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )

task_decompse_prompt = """
# 指令：
    针对给定的目标，制定一个简单的逐步计划。
    制定的计划要充分考虑现有的工具，尽量把计划分解成工具可以调用的步骤。
    这个计划应当包含独立的任务，如果这些任务被正确执行，将会得出正确的答案。不要添加任何多余的步骤。
    最后一步的结果应当是最终答案。确保每一步都包含了所需的所有信息——不要跳过任何步骤。

    注意：如果给定的目标可以直接由一个工具完成，那么不需要制定计划。

# 可使用的工具：
    {function}

# 任务：
    {message}

# 分解的计划：

"""


planner_prompt = PromptTemplate(template=task_decompse_prompt, 
                                    input_variables=["function", "message"])
planner = planner_prompt | llm_qwen_plus.with_structured_output(Plan)


def get_plan(state: ReWOO):
    task = state["message"]
    
    results = planner.invoke({"message": task, "function": str(tools_instructions)})
    print(results)

    return {"steps": results.steps}

# 串行执行计划，默认step之间没有依赖关系
def execute_plan(state: ReWOO):
    steps = state["steps"]
    results_dict = {}
    for step in steps:
        result = graph.invoke({"messages": step})
        results_dict[step] = result['messages'][-1].content
        print(result['messages'][-1].content)
        print("--------------------------------")
    return {"results": results_dict}


task_summary_prompt = """
# 指令：
    根据给定的任务和中间过程的结果，总结出最终的答案。

# 任务：
    {message}

# 中间过程的结果：
    {results}

# 最终的答案：

"""

summary_prompt = PromptTemplate(template=task_summary_prompt, 
                                    input_variables=["results", "message"])
summary_chain = summary_prompt | llm_qwen_plus


def get_result(state: ReWOO):
    message = state["message"]
    results = state["results"]
    
    result_str = summary_chain.invoke({"message": message, "results": results}) 
    print(result_str)
    return {"result": result_str}

def workflow():
    from langgraph.graph import END, StateGraph, START

    graph = StateGraph(ReWOO)
    graph.add_node("plan", get_plan)
    graph.add_node("tool", execute_plan)
    graph.add_node("solve", get_result)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "tool")
    graph.add_edge("tool", "solve")
    graph.add_edge("solve", END)

    app = graph.compile()

    return app

def main():



    app = workflow()
    
    while True:
        try:
            inputs = {"message": input("User: "), }
            result = app.invoke(inputs)
            print(result)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
    #  特朗普第二次当总统那年，中国的退休政策
    #  从北京到上海旅游，一些出行的旅游规划
    #  从川杨新苑3期到东方明珠怎么出行方便,当地的天气怎么样
    

