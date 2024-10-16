# import uuid
# from langchain.prompts import (
#     PromptTemplate,
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     ChatPromptTemplate,
# )

# from pydantic import BaseModel, Field

# from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
# from langchain.output_parsers.structured import StructuredOutputParser
# from langchain_community.document_loaders import JSONLoader
# from langchain_openai import OpenAIEmbeddings

# from langchain_chroma import Chroma
# from langchain.schema.runnable import RunnablePassthrough
# from langchain_core.runnables import RunnableParallel

# import re
# from langchain_core.tools import tool

# from langchain.tools.base import StructuredTool
# from langchain.agents import create_openai_functions_agent, Tool, AgentExecutor
# import datetime

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage

import dotenv
from langchain_openai import ChatOpenAI
from typing import List, Annotated, Literal

import os
import sys

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
home_dir_parent = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

if home_dir not in sys.path:
    sys.path.append(home_dir)
if home_dir_parent not in sys.path:
    sys.path.append(home_dir_parent)

from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from core.config import settings

from tools import bot_tools

dotenv.load_dotenv()

model = ChatOpenAI(
    model=os.getenv("BOT_MODEL"), temperature=0, api_key=settings.API_KEY
)


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: all messages
        question: question
        answer: LLM generation
    """

    messages: Annotated[list, add_messages]
    question: str
    answer: str


tool_node = ToolNode(bot_tools.tools)

model_tools = model.bind_tools(bot_tools.tools)


# Define the function that determines whether to continue or not
def should_continue(state: GraphState) -> Literal["tools", "__end__"]:
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END


# Define the function that calls the model
def call_model(state: GraphState):
    # print(state)
    messages = state["messages"]
    response = model_tools.invoke(
        messages[-5:]
    )  ### since we are checkpointing the conversation, to avoid using stale information from memory, we only pass in the last 5 messages

    # print("invoke response", response)
    # print("states prior", messages[-1])
    question = ""

    try:
        last_human_message = [
            x for x in reversed(messages) if isinstance(x, HumanMessage)
        ][0]
        question = last_human_message.content
    except:
        pass

    answer = response.content

    # print("answer", answer)

    return {"messages": [response], "answer": answer, "question": question}


# Define a new graph
workflow = StateGraph(GraphState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    ["tools", END],
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")
