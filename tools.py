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

from datetime import datetime
from utils import get_location

TAVILY_API_KEY = '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'

embeddings = OpenAIEmbeddings(
    base_url = "https://ai.devtool.tech/proxy/v1",
    api_key = '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',
    model='text-embedding-3-large'
    )


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
    
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



@tool
def web_search(query):
    """当需要联网搜索获取实时信息时，调用此工具。"""

    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
    response = tavily_client.search(query, max_results=3)

    return response



@tool
def get_weather(city_name: str):
    """
    当查询天气时才使用此工具.
    输入：city_name: 城市的名称。如果不含有“市”、“县”等后缀，需要加上后缀。
    """
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

    return result

@tool
def get_city_name():
    """查询当前所在的城市名称信息."""
    print('**************************************************8')
    url = "https://restapi.amap.com/v3/ip?parameters"
    parameters = {
        'key': '1a4460bc4e30e4ffb8db28ce0726513d',  
    }
    # 发送GET请求
    response = requests.get(url, params=parameters)
    result = response.json()
    return result['city']


@tool
def get_address(location_info):
    """
    当查询某个具体位置时才使用此工具.
    location_info: 需要查询的地址信息，例如：上海市申城佳苑1期C块
    """
    
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
    print(result['pois'][0])

    return result['pois'][0]['address']



@tool
def get_knowledge(query):
    """当查询关于政策方面的知识时，调用此工具."""
    db = Chroma(persist_directory="./db", embedding_function=embeddings,
            )
    docs = db.similarity_search_with_relevance_scores(query, k=3,)

    return [doc[0].page_content for doc in docs] 




@tool
def navigation(start_name: str, end_name: str,mode: Literal['driving', 'walking', 'bicycling'] = 'driving'):
    """当需要查询两地之间的导航信息时，调用此工具."""
    

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

    result = verify_api('从上海市申城佳苑1期C块到上海市申城佳苑2期B块的走路怎么走')
    print(result)