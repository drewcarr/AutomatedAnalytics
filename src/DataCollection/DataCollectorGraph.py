from operator import add
from DataCollection.DataGatherer import DataGatherer
from DataCollection.DataValidator import DataValidator
from DataCollection.cleaning.DataCleaner import DataCleaner
from DataCollection.DataFormatter import DataFormatter
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, AIMessage
from typing_extensions import Annotated, Literal, TypedDict, List, Dict
from langchain_core.tools import tool
from enum import Enum

from DataCollection.DataRequirements import DataRequirements
from langgraph.prebuilt import ToolNode

""" 
Built on a ReACT Agent framework 
Encapsulating each stage in its own class to handle responsibilities.
"""

# Enum for naming the nodes
class DataCollectorNodes(Enum):
    ORCHESTRATOR = "orchestrator"
    TOOLS = "tools"
    END = "end"

# State to track the data collection process
class DataCollectorState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    data_source: str
    data_requirements: DataRequirements
    current_tool: str
    collected_data: Dict

# DataCollector class that orchestrates the tools
class DataCollector:
    def __init__(self):
        self.graph_builder = StateGraph(DataCollectorState)
        
        # Initialize the tool classes
        self.data_gatherer = DataGatherer()
        self.data_validator = DataValidator()
        self.data_cleaner = DataCleaner()
        self.data_formatter = DataFormatter()

        """ Setup tools as single calls to the classes """
        tools = [
            self.run_data_gatherer,
            self.run_data_validator,
            self.run_data_cleaner,
            self.run_data_formatter
        ]
        tool_node = ToolNode(tools)

        """ Add LLM with tool calling """
        self.orchestrator = ChatOpenAI().bind_tools(tools)

        """ Add nodes """
        self.graph_builder.add_node(DataCollectorNodes.ORCHESTRATOR.value, self.invoke_orchestrator)
        self.graph_builder.add_node(DataCollectorNodes.TOOLS.value, tool_node)

        """ Add edges """
        self.graph_builder.add_edge(DataCollectorNodes.TOOLS.value, DataCollectorNodes.ORCHESTRATOR.value)
        self.graph_builder.add_conditional_edges(DataCollectorNodes.ORCHESTRATOR.value, self.orchestrator_router)

    def invoke_orchestrator(self, state: DataCollectorState):
        messages = state["messages"]
        response = self.orchestrator.invoke(messages)
        return {"messages": [response]}

    def orchestrator_router(self, state: DataCollectorState) -> Literal[DataCollectorNodes.TOOLS.value, END]:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return DataCollectorNodes.TOOLS.value
        return END

    def compile_graph(self):
        return self.graph_builder.compile()

    """ 
    Define the encapsulated tool steps 
    TODO: Have the error handler catch anything and debug then route back to the orchestrator
    The tool node automatically catches error and returns it so orchestrator can try again. Might be enough for now
    https://langchain-ai.github.io/langgraph/how-tos/tool-calling-errors/?h=error+handling#custom-strategies
    """
    
    @tool
    def run_data_gatherer(self, state: DataCollectorState):
        """ Use the DataGatherer class for source identification and data collection """
        source = self.data_gatherer.identify_data_source(state["data_requirements"])
        state["data_source"] = source
        state["collected_data"] = self.data_gatherer.connect_to_api(source)
        return {"messages": [AIMessage(content="Data gathering complete.")], "current_tool": DataCollectorNodes.TOOLS.value}

    @tool
    def run_data_validator(self, state: DataCollectorState):
        """ Use the DataValidator class to validate the collected data """
        valid, message = self.data_validator.validate_data(state["collected_data"])
        return {"messages": [AIMessage(content=message)], "current_tool": DataCollectorNodes.TOOLS.value}

    @tool
    def run_data_cleaner(self, state: DataCollectorState):
        """ Use the DataCleaner class to clean the raw data """
        cleaned_data = self.data_cleaner.clean_data(state["collected_data"]["raw_data"])
        state["collected_data"]["cleaned_data"] = cleaned_data
        return {"messages": [AIMessage(content="Data cleaning complete.")], "current_tool": DataCollectorNodes.TOOLS.value}

    @tool
    def run_data_formatter(self, state: DataCollectorState):
        """ Use the DataFormatter class to format the cleaned data """
        formatted_data = self.data_formatter.format_data(state["collected_data"]["cleaned_data"])
        state["collected_data"] = formatted_data
        return {"messages": [AIMessage(content="Data formatting complete.")], "current_tool": DataCollectorNodes.END.value}
