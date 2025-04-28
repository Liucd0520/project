from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import os  
from langchain.vectorstores import FAISS, Chroma
from tools import *
from langchain import hub
from langchain_openai import ChatOpenAI
from typing import List
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain.prompts import PromptTemplate
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from typing import Literal
from typing_extensions import TypedDict

from langgraph.graph import MessagesState, END
from langgraph.types import Command




llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=0, api_key='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')

# Create Agent Supervisor

members = ["web_search", "navigation", "get_weather", ]
# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed
options = members + ["FINISH"]

system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""

    next: Literal[*options]


class State(MessagesState):
    next: str


def supervisor_node(state: State) -> Command[Literal[*members, "__end__"]]:
    messages = [
        {"role": "system", "content": system_prompt},
    ] + state["messages"]
    response = llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END

    return Command(goto=goto, update={"next": goto})


from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent



research_agent = create_react_agent(llm, tools=[web_search],)


def research_node(state: State) -> Command[Literal["supervisor"]]:
    result = research_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="researcher")
            ]
        },
        goto="supervisor",
    )


# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
navigation_agent = create_react_agent(llm, tools=[navigation, ])


def navigation_node(state: State) -> Command[Literal["supervisor"]]:
    result = navigation_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="navigation")
            ]
        },
        goto="supervisor",
    )



# NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
weather_agent = create_react_agent(llm, tools=[get_weather, ])


def weather_node(state: State) -> Command[Literal["supervisor"]]:
    result = weather_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="weather")
            ]
        },
        goto="supervisor",
    )


builder = StateGraph(State)
builder.add_edge(START, "supervisor")
builder.add_node("supervisor", supervisor_node)
builder.add_node("researcher", research_node)
builder.add_node("navigation", navigation_node)
builder.add_node("weather", weather_node)
graph = builder.compile()

from IPython.display import display, Image

display(Image(graph.get_graph().draw_mermaid_png()))