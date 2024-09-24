from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage
from typing import Annotated, TypedDict, List
from langgraph.prebuilt import ToolNode
from enum import Enum
from DatasetMetadata import DatasetMetadata  # Import the new DatasetMetadata class
from DataRequirements import DataRequirements


class DataGathererNodes(Enum):
    CHECK_METADATA = "check_metadata"
    WEB_SCRAPING = "web_scraping"
    NEW_API_CONNECTION = "new_api_connection"
    END = "end"

# State to track data gathering process
class DataGathererState(TypedDict):
    data_requirements: DataRequirements
    collected_data: dict
    data_source: str
    dataset_id: str  # To track if a dataset ID is used

class DataGatherer:
    def __init__(self):
        self.graph_builder = StateGraph(DataGathererState)

        """ Setup tools for gathering data """
        tools = [
            self.check_metadata,  # Check metadata for local or API data
            self.web_scraping,    # Web scraping as fallback
            self.create_new_api   # Create a new API connection if necessary
        ]
        tool_node = ToolNode(tools)

        """ Add LLM """
        self.orchestrator = ChatOpenAI().bind_tools(tools)

        """ Add nodes """
        self.graph_builder.add_node(DataGathererNodes.CHECK_METADATA.value, self.check_metadata)
        self.graph_builder.add_node(DataGathererNodes.WEB_SCRAPING.value, self.web_scraping)
        self.graph_builder.add_node(DataGathererNodes.NEW_API_CONNECTION.value, self.create_new_api)
        self.graph_builder.add_node(DataGathererNodes.END.value, END)

        """ Define edges for decision making """
        self.graph_builder.add_edge(DataGathererNodes.CHECK_METADATA.value, DataGathererNodes.WEB_SCRAPING.value)
        self.graph_builder.add_edge(DataGathererNodes.WEB_SCRAPING.value, DataGathererNodes.NEW_API_CONNECTION.value)
        self.graph_builder.add_edge(DataGathererNodes.NEW_API_CONNECTION.value, DataGathererNodes.END.value)

    def invoke_orchestrator(self, state: DataGathererState):
        """Orchestrator invokes the current state"""
        messages = [AIMessage(content="Starting Data Gathering...")]
        response = self.orchestrator.invoke(messages)
        return {"messages": [response]}

    def compile_graph(self):
        """Compile the graph"""
        return self.graph_builder.compile()

    """ Define tool methods """

    def check_metadata(self, state: DataGathererState):
        """
        Check the metadata file for an existing dataset that matches the requirements.
        If a match is found, retrieve the data.
        """
        requirement_description = state['data_requirements'].requirements

        # Search by description in metadata
        matching_dataset = DatasetMetadata.search_by_description(requirement_description)
        
        if matching_dataset:
            state["dataset_id"] = matching_dataset["id"]
            state["data_source"] = matching_dataset["data_source"]
            
            # Fetch the raw data
            state["collected_data"] = DatasetMetadata.get_raw_data(matching_dataset["id"])
            return {"messages": [AIMessage(content=f"Found matching dataset: {matching_dataset['description']}")], "current_tool": DataGathererNodes.END.value}
        else:
            return {"messages": [AIMessage(content="No matching dataset found in metadata. Proceeding to web scraping.")], "current_tool": DataGathererNodes.WEB_SCRAPING.value}

    def web_scraping(self, state: DataGathererState):
        """ Perform web scraping if the data isn't available locally or via an API """
        # Simulate web scraping
        state["collected_data"] = {"data": "Scraped data from website"}
        return {"messages": [AIMessage(content="Web scraping completed.")], "current_tool": DataGathererNodes.END.value}

    def create_new_api(self, state: DataGathererState):
        """ Create a new API connection if needed """
        # Simulate setting up a new API connection
        state["collected_data"] = {"data": "Data from newly established API connection"}
        # Add the new API connection to metadata for future use
        new_dataset = {
            "id": "new_api_2024",
            "description": "New API for stock prices 2024",
            "data_source": "api",
            "data_link": "https://api.newsource.com/stock_prices_2024",
            "date_created": "2024-01-01",
            "date_modified": "2024-01-01"
        }
        DatasetMetadata.add_dataset(new_dataset)
        return {"messages": [AIMessage(content="New API connection created and data fetched.")], "current_tool": DataGathererNodes.END.value}
