
import requests


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
    print(result)

    return result['pois'][0]['address']

get_address("美食")