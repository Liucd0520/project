import requests

# 后端接口地址（假设服务运行在本地的8000端口）
url = "http://localhost:8010/ai_assistant"

# 请求数据
data = {
    "query": "我今天82岁，有哪些适合我的养老政策"
}

print('xxx')
# 发送POST请求
response = requests.post(url, params=data)
print('xxxxxxx')
# 输出响应结果
if response.status_code == 200:
    print("响应结果：", response.json())
else:
    print(f"请求失败，状态码：{response.status_code}")
    print("错误信息：", response.text)