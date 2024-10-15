from typing import Optional, Dict
from DataStorage.DatasetMetadata import DatasetMetadata
from common.DataRequirements import DataRequirements
from common.Agents.BaseAgent import BaseAgent
from langchain_core.messages import AIMessage
import json

class DynamicOrchestratorAgent(BaseAgent):
    def __init__(self, name: str, openai_api_key: str, tools=None, system_prompt=None):
        """
        Initialize the LocalDatasetAgent.
        
        :param name: The name of the agent.
        :param assistant_id: The assistant ID if using a preconfigured OpenAI assistant.
        :param openai_api_key: The OpenAI API key for accessing LLM.
        :param tools: List of tools available for this agent.
        """
        super().__init__(name, system_prompt=system_prompt, openai_api_key=openai_api_key, tools=tools)

    def execute(self, state: Dict, thread_id: Optional[str] = None) -> Dict:
        