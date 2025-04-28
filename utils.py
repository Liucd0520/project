import requests
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

def get_location(key_word):

    url = "https://restapi.amap.com/v3/place/text?parameters"

    parameters = {
        'key': '1a4460bc4e30e4ffb8db28ce0726513d',  # 请替换为你的实际API密钥
        'keywords': key_word,  # 查询的关键字
        'types': '120000|150000',  
        'offset': 1
    }
    # 发送GET请求
    response = requests.get(url, params=parameters)
    result = response.json()
    
    location  = result['pois'][0]['location']
    longitude, latitude = location.split(',')
    return longitude, latitude



def verify_api(query):
    """验证API是否可用."""

    print('------------------->>>>>', query)
    llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0, api_key='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')
    print('llm -> ', llm)

    prompt = ChatPromptTemplate.from_messages(
        f"""
        你是一个参数查询助手，根据用户的输入内容找出相关的参数并以json的格式返回。
        JSON字段如下：
        - "start_name": 起点的地点信息
        - "end_name": 终点的地点信息
        - "mode": 导航模式，包括：'driving', 'walking', 'bicycling'
        如果没有找到相关参数，则需要提醒用户告诉你这些内容，只返回数据结构，不要有其他的评论。
        用户输入：{query}
        """)
    parser = JsonOutputParser()
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    print('prompt -> ', prompt)
    chain = prompt | llm | parser
    data = chain.invoke({"query": query})
    return data 