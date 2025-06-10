import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.chat_models import init_chat_model
from typing import Dict, List, Any


from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="Qwen2.5-14B", #   Qwen2.5-14B
                    base_url='http://172.31.24.23:8001/v1', 
                    api_key='EMPTY',
                    temperature=0,
                    )

client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["/root/liucd/project/MCP_Test/math_server.py"],
            "transport": "stdio",
        },
    }
)

async def run():
    tools = await client.get_tools()
    agent = create_react_agent(llm, tools)
    math_response = await agent.ainvoke({"messages": "计算3和5的乘积"})
    print(math_response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())