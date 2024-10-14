from typing import Optional, Dict
from DataStorage.DatasetMetadata import DatasetMetadata
from common.DataRequirements import DataRequirements
from common.BaseAgent import BaseAgent
from langchain_core.messages import AIMessage
import json

class DatasetCoverage:
    def __init__(self, dataset_id: str, covered_requirements: Dict[str, bool], missing_requirements: Dict[str, str]):
        """
        Represents the coverage of requirements by a dataset.
        
        :param dataset_id: The ID of the dataset.
        :param covered_requirements: A dictionary indicating which requirements are covered.
        :param missing_requirements: A dictionary indicating which requirements are not covered, with details.
        """
        self.dataset_id = dataset_id
        self.covered_requirements = covered_requirements
        self.missing_requirements = missing_requirements

    def to_dict(self):
        return {
            "dataset_id": self.dataset_id,
            "covered_requirements": self.covered_requirements,
            "missing_requirements": self.missing_requirements
        }

class LocalDatasetAgent(BaseAgent):
    ASSISTANT_ID = "asst_XdqG6soihubjT90lJdk5kkPA"

    def __init__(self, name: str, openai_api_key: str, tools=None):
        """
        Initialize the LocalDatasetAgent.
        
        :param name: The name of the agent.
        :param assistant_id: The assistant ID if using a preconfigured OpenAI assistant.
        :param openai_api_key: The OpenAI API key for accessing LLM.
        :param tools: List of tools available for this agent.
        """
        super().__init__(name, assistant_id=self.ASSISTANT_ID, openai_api_key=openai_api_key, tools=tools)

    def execute(self, state: Dict, thread_id: Optional[str] = None) -> Optional[Dict]:
        """
        Execute the local dataset search based on the requirements provided in the state.
        Then call the LLM with the data requirements and potential datasets to determine coverage.
        
        :param state: The state containing DataRequirements for the dataset search.
        :param thread_id: Optional thread ID for context.
        :return: The updated state with identified datasets and coverage analysis.
        """
        data_requirements: DataRequirements = state.get("data_requirements")
        if not data_requirements:
            self.logger.error("Data requirements not provided in state.")
            return None

        # Validate the data requirements
        try:
            data_requirements.validate_requirements()
        except ValueError as e:
            self.logger.error(f"Validation error: {str(e)}")
            return None

        # Search for potential datasets that match the requirements
        potential_datasets = self.search_for_datasets(data_requirements)
        if potential_datasets:
            self.logger.info(f"Found potential datasets: {potential_datasets}")
        else:
            self.logger.info("No matching datasets found.")
            return {"potential_datasets": None}
        
        llm_input = {
            "data_requirements": data_requirements.__dict__,
            "potential_datasets": potential_datasets
        }

        # Convert llm_input dictionary to a JSON string
        llm_input_str = json.dumps(llm_input)

        # Append the AIMessage with the string content
        state["messages"].append(AIMessage(content=llm_input_str))

        # Call LLM with data requirements and potential datasets
        self.logger.debug(f"Calling LLM with input: {llm_input}")
        agent_response = self.llm.invoke(state)

        return agent_response

    def search_for_datasets(self, data_requirements: DataRequirements) -> Optional[Dict]:
        """
        Search for datasets that match the given data requirements.
        
        :param data_requirements: The data requirements to search for datasets.
        :return: A dictionary of potential datasets or None if no match is found.
        """
        # Construct the search query from the data requirements
        query_parts = []
        if data_requirements.requirement:
            query_parts.append(data_requirements.requirement)
        if data_requirements.domain_context:
            query_parts.append(data_requirements.domain_context)
        if data_requirements.granularity:
            query_parts.append(data_requirements.granularity)
        if data_requirements.timeframe:
            query_parts.append(data_requirements.timeframe)

        search_query = " ".join(query_parts)
        self.logger.debug(f"Constructed search query: {search_query}")

        # Perform semantic search using DatasetMetadata
        best_matches = DatasetMetadata.search_by_description(search_query)
        return best_matches if len(best_matches) > 0 else None


