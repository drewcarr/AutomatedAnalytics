import json
from typing import List, Dict, Optional
from DataCollection.DataCollectionTeamState import DataCollectionTeamState
from common.Agents.BaseAgent import BaseAgent
from langchain_core.messages import AIMessage

class Response:
    validated: bool
    reason: str


class DataValidatorAgent(BaseAgent):
    """ This assistant will return in json mode"""
    ASSISTANT_ID = "asst_rKWTpHMdWfZDeuxpTootQyhi"
    name = "DataValidatorAgent"

    def __init__(self):
        super().__init__(self.name, assistant_id=self.ASSISTANT_ID)

    def execute(self, state: DataCollectionTeamState, thread_id: Optional[int]) -> DataCollectionTeamState:
        data_info = {
            "data_requirements": state.get("data_requirements").__dict__,
            "data_coverage": state.get("data_coverage").__dict__
        }

        llm_message = json.dumps(data_info)

        agent_response = self.invoke(llm_message)

        if "validated" in agent_response and "reason" in agent_response:
            state["validated"] = agent_response["validated"]
            state["messages"].append(
                AIMessage(content=f"Validated: {agent_response['validated']}, reason: {agent_response['reason']}")
            )
        else:
            self.logger.error("Invalid response from validator agent", agent_response)
            state["Error"] = state["Error"] = "Invalid response from validator agent"
        return state
        


        


        