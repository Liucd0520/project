from langchain_mcp_adapters.client import MultiServerMCPClient
from tools import * 
from langgraph.prebuilt import create_react_agent

async def obtain_mcp_tools():
    client = MultiServerMCPClient(
        {
            # 高德地图
            # "amap-maps": {
            # "transport": "sse",
            # "url": "https://mcp-9783d44e-d45f-4414.api-inference.modelscope.cn/sse"
            # },
            # 必应搜索
            # "bing-cn-mcp-server": {
            # "transport": "sse",
            # "url": "https://mcp.api-inference.modelscope.cn/sse/a366ca375cbb4c"
            # },
            # # 12306 购票
            # "12306-mcp": {
            # "transport": "sse",
            # "url": "https://mcp.api-inference.modelscope.cn/sse/c54cc07d7a8a4b"
            # },
            # 热点新闻
            "mcp-hotnews-server": {
            "transport": "sse",
            "url": "https://mcp.api-inference.modelscope.cn/sse/ef06b73cd2c848"
            }
        })
    
    # 从MCP Server中获取可提供使用的全部工具
    tools = await client.get_tools()
    
    return tools


async def main():
    query = '微博的最新新闻热点'
    tools = await  obtain_mcp_tools()
    print(tools)
    inputs = {"messages": [
                ('system', '你是一个AI助手，请以简洁的方式回复用户，尽量不要超过100字。'), 
                ("user", query)]}

    graph = create_react_agent(llm_qwen_14b, tools=tools, )  
    import time 
    start = time.time()
    response =  graph.invoke(inputs)
    result = response['messages'][-1].content
    print(result)
    print(time.time() - start)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
