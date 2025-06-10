from langchain_community.tools.tavily_search import TavilySearchResults
import os 
from tavily import TavilyClient
from langchain_core.tools import tool
from typing import Literal
import requests
# from langchain.vectorstores import FAISS, Chroma
# from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.embeddings import OpenAIEmbeddings
import pandas as pd
from typing import Literal
from langchain_community.vectorstores import FAISS
from datetime import datetime
from models import embedding_vllm
from langchain.prompts import PromptTemplate
from function_guide.prompt import prompt_function_guide
from models import llm_qwen_14b
# from html_transfer_md import html_converter
from langchain_core.output_parsers import  CommaSeparatedListOutputParser
from langchain.output_parsers import EnumOutputParser
import pandas as pd 
from typing import List
import config 
from function_guide.guide import recommand_function
from utils import *




def excel_to_dict(excel_path, sheet_name=0):
    # 读取Excel文件
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    dict_data = df.to_dict(orient='records')

    use_dict = {}
    for item in dict_data:
        use_dict.update({item['中文名']: item["adcode"]})
    return use_dict



@tool
def get_datetime():
    """当需要查询当前的时间时才使用此工具."""
    logger.info('查询当前时间工具 ...')
    
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



# @tool
# def web_search(query):
#     """当需要联网搜索获取实时信息时，调用此工具。"""
#     logger.info(f'进入联网搜索节点，查询内容：{query}')

#     TAVILY_API_KEY = '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'
#     tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
#     response = tavily_client.search(query, max_results=3)
#     logger.info(f'联网搜索结果：{response}')

#     return response

@tool
def web_search(query):
    """当需要联网搜索获取实时信息时，调用此工具。"""
    
    api_key = "bce-v3/ALTAK-o0b6jAzPzhS0sA8K1IQsm/3eced8c128438d0327b12284dda020219361366e"
    # 请求地址
    url = "https://qianfan.baidubce.com/v2/ai_search/chat/completions"
    # 请求头
    headers = {
        'X-Appbuilder-Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # 请求体
    data = {
        "messages": [{
                "content": query, "role": "user"
            }],
        "resource_type_filter": [{
                "type": "web", "top_k": 5  # 搜索的记录个数
            }]
    }

    # 发送请求
    response = requests.post(url, headers=headers, json=data)

    # 输出响应内容
    if response.status_code == 200:
        return response.json()
    else:
        return response.text


@tool
def get_weather(city_name: str):
    """
    当查询天气时才使用此工具.
    输入：city_name: 城市的名称。如果不含有“市”、“县”等后缀，需要加上后缀。
    """
    logger.info(f'进入天气查询天气节点，城市名称：{city_name}')

    # 高德天气查询API的URL
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    city2code = excel_to_dict('AMap_adcode_citycode.xlsx')
    city_code = city2code[city_name]
    parameters = {
        'key': 'e213e15747cac80c28c541585825d8fa',  # 请替换为你的实际API密钥
        'city': city_code,  #str(city_code),  # 示例中使用的是东城区的代码，请替换为你需要查询的城市代码
        'extensions': 'all',  # 或者 'all' 来获取更详细的天气预报信息
        'output': 'JSON',  # 返回的数据格式，支持 JSON 和 XML
    }
    # 发送GET请求
    response = requests.get(url, params=parameters)
    result = response.json()
    logger.info(f'查询天气结果：{result}')

    return result

@tool
def get_city_name():
    """查询当前所在的城市名称信息."""
    logger.info('进入查询当前所在城市名称节点 ...')

    url = "https://restapi.amap.com/v3/ip?parameters"
    parameters = {
        'key': '1a4460bc4e30e4ffb8db28ce0726513d',  
    }
    # 发送GET请求
    response = requests.get(url, params=parameters)
    result = response.json()
    logger.info(f'查询当前所在城市名称结果：{result}')

    return result['city']


@tool
def get_address(location_info):
    """
    当查询某个具体位置时才使用此工具.
    location_info: 需要查询的地址信息，例如：上海市申城佳苑1期C块
    """
    logger.info(f'进入查询地址节点，查询内容：{location_info}')

    url = "https://restapi.amap.com/v3/place/text?parameters"

    parameters = {
        'key': '1a4460bc4e30e4ffb8db28ce0726513d',  # 请替换为你的实际API密钥
        'keywords': location_info,  # 查询的关键字
        'types': '120000|150000',  
        'offset': 1
    }
    # 发送GET请求
    response = requests.get(url, params=parameters)
    result = response.json()
    logger.info(f'查询地址结果：{result['pois'][0]}')

    return result['pois'][0]['address']



@tool
def get_knowledge(query):
    """当查询关于政策方面的知识时，调用此工具."""
    print('进入政策查询节点 ...')
    vector = FAISS.load_local("faiss_index", embedding_vllm,  allow_dangerous_deserialization=True)
    docs = vector.similarity_search(query, k=3,)
    print('end', docs)
    return  [doc.page_content for doc in docs] 




@tool
def navigation(start_name: str, end_name: str,mode: Literal['driving', 'walking', 'bicycling'] = 'driving'):
    """当需要查询两地之间的导航信息时，调用此工具."""
    
    logger.info(f'进入导航查询节点，起点：{start_name}，终点：{end_name}，导航模式：{mode}')

    start_longitude, start_latitude = get_location(start_name)
    end_longitude, end_latitude = get_location(end_name)

    parameters = {
        'key': '1a4460bc4e30e4ffb8db28ce0726513d',  # 请替换为你的实际API密钥
        'origin': f"{start_longitude},{start_latitude}",  # 查询的关键字
        'destination': f"{end_longitude},{end_latitude}",
    }
    version = 'v4' if mode == 'bicycling' else 'v3'
    api_endpoint = f'https://restapi.amap.com/{version}/direction/{mode}'
    response = requests.get(api_endpoint, params=parameters)
    result = response.json()
    for path in result["route"]["paths"]:
        if "steps" in path:
            path["steps"] = [{"instruction": step["instruction"]} for step in path["steps"]]
    
    logger.info(f'导航查询结果：{result}')

    return result


if __name__ == '__main__':

    tools = [get_weather, web_search, get_address, get_knowledge, navigation]

    # result = web_search('2024年的中国进博会时间范围')
    # print(result)
    
    # result = get_weather('北京')
    # print(result)

    # result = get_address('上海市申城佳苑1期C块')
    # print(result)
    
    # print(result['浦东新区'])

    # result = verify_api('从上海市申城佳苑1期C块到上海市申城佳苑2期B块的走路怎么走')
    # print(result)

    # result = get_knowledge('我今年82岁了，我能享受什么养老政策')
    # print(result)