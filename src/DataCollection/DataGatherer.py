from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import AIMessage
from typing_extensions import Annotated, TypedDict, List
from langgraph.prebuilt import ToolNode
from enum import Enum
from DataStorage.DatasetMetadata import DatasetMetadata  # Import the new DatasetMetadata class
from common.DataRequirements import DataRequirements


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
