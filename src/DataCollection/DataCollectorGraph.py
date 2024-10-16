from typing import List, Dict
from langgraph.prebuilt import ToolNode
from DataCollection.LocalDatasetAgent import LocalDatasetAgent
from common.Agents import BaseAgent
from langchain_core.messages import HumanMessage

from common.DataRequirements import DataRequirements
from common.Orchestrators.BaseDynamicTeamOrchestrator import BaseDynamicTeamOrchestrator, BaseTeamState

class DataCollectionTeamState(BaseTeamState):
    """
    Extended state for the DataCollectionTeam.
    messages: Annotated[List[BaseMessage], add]
    validated: bool
    next: str
    Error: str
    """
    data_requirements: DataRequirements

class DataCollectionTeam(BaseDynamicTeamOrchestrator):
    def __init__(self, debug_mode=False):
        """
        Initialize a data collection team orchestrator.

        :param local_dataset_agent: An agent responsible for retrieving data from local datasets.
        :param tools: A list of tools available to agents.
        :param validator: The agent responsible for validation.
        :param debug_mode: Enable or disable debug mode for logging.
        """
        local_dataset_agent = LocalDatasetAgent(
            name="TestLocalDatasetAgent",
            openai_api_key="test_api_key",
            tools=None,
        )
        agents = [local_dataset_agent]
        super().__init__(agents, debug_mode)

    def validate(self, state: DataCollectionTeamState) -> DataCollectionTeamState:
        """
        Validate the collected data to determine if it meets requirements.

        :param state: The current state of the session.
        :return: True if the state is valid, False otherwise.
        """
        if "data" in state and isinstance(state["data"], dict) and state["data"]:
            state["validated"] = True
            self.logger.debug("Validation passed: Data is collected successfully.")
            return True
        else:
            state["validated"] = False
            state["messages"].append(HumanMessage(content="Data validation failed. More data required."))
            self.logger.debug("Validation failed: Data is missing or invalid.")
            return False
