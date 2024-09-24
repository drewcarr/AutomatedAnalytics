from operator import add
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, AnyMessage
from typing import Annotated, Literal, TypedDict, List

from DataRequirements import DataRequirements

from langgraph.prebuilt import ToolNode

class DataCollectorState:
    messages: Annotated[List[BaseMessage], add]
    data_source: str
    data_requirements: DataRequirements


class DataCollector:
    def __init__(self):
        self.graph_builder = StateGraph(DataCollectorState)

    def compile_graph(self):
        return self.graph_builder.compile()