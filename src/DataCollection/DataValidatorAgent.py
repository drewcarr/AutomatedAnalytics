import json
from typing import List, Optional
from common.Agents import OpenAIAgent

class DataSource:
    endpoint: str
    coverage: str

class DataValidatorAgent(OpenAIAgent):
    ASSISTANT_ID = "asst_rKWTpHMdWfZDeuxpTootQyhi"
    name = "DataValidatorAgent"

    """ Copy of instructions from api - returns json
    You are a validation agent that will determine whether the team of agents has gathered the correct data sources to serve the DataRequirements.
    Between all DataCoverage the covered requirements need to address the needs laid out by the DataRequirements. 
    Reply in json format 
    {
        validated: bool,
        reason: str
        data_sources: [{
            endpoint: str
            coverage: str
        }...]
    }
    """

    def __init__(self):
        self.data_coverage = {}
        super().__init__(self.name, assistant_id=self.ASSISTANT_ID)

    def execute(self, thread_id: Optional[int]) -> bool:
        agent_response = self.invoke(content="", thread_id=thread_id)

        response_json = agent_response.messages[0]

        return response_json
        
    
        


        


        