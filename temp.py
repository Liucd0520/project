from tools import * 
from langgraph.prebuilt import create_react_agent


tools = [get_datetime, # 查日期
    get_weather, # 查天气
    web_search, # 查网络
    get_city_name, get_address, # 查城市名、地址 
    get_knowledge, # 查政策知识
    navigation, # 导航 
    # medical_graphrag, # 医学知识查询
]


graph = create_react_agent(llm_qwen_14b, tools=tools, )

query = '请讲个笑话'

inputs = {"messages": [
            ('system', '你是一个AI助手，请以简洁的方式回复用户。'), 
            ("user", query)]}
        
response =  graph.invoke(inputs)
result = response['messages']
print(result)
