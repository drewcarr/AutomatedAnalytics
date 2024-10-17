import json
from typing import List, Dict
from langgraph.prebuilt import ToolNode
from DataCollection.DataCollectorGraph import DataCollectionTeamState
from DataCollection.LocalDatasetAgent import DatasetCoverage, LocalDatasetAgent
from common.Agents import BaseAgent
from langchain_core.messages import HumanMessage

from common.DataRequirements import DataRequirements
from common.Orchestrators.BaseDynamicTeamOrchestrator import BaseDynamicTeamOrchestrator, BaseTeamState

class Response:
    validated: bool
    reason: str


class DataValidatorAgent(BaseAgent):
    """ This assistant will return in json mode"""
    ASSISTANT_ID = "asst_rKWTpHMdWfZDeuxpTootQyhi"
    name = "DataValidatorAgent"

    def __init__(self):
        super().__init__(name=self.name, assistant_id=self.ASSISTANT_ID)

    def execute(self, state: DataCollectionTeamState):
        data_info = {
            "data_requirements": state.get("data_requirements").__dict__,
            "data_coverage": state.get("data_coverage").__dict__
        }

        llm_message = json.dumps(data_info)

        agent_response = self.invoke(llm_message)

        if "validated" in agent_response and "reason" in agent_response:
            validated = agent_response["validated"]
            reason = agent_response["reason"]
            return {validated, reason}
        else:
            return {"Error": "Missing 'validated' or 'reason' in response from DataValidatorAgent."}
        


        


        