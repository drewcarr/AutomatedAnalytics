from typing import Optional, Dict
from DataStorage.DatasetMetadata import DatasetMetadata
from common.Agents import OpenAIAgent
from common.DataRequirements import DataRequirements

class LocalDatasetAgent(OpenAIAgent):
    ASSISTANT_ID = "asst_XdqG6soihubjT90lJdk5kkPA"
    name = "LocalDatasetAgent"

    def __init__(self):
        """
        Initialize the LocalDatasetAgent.
        
        :param name: The name of the agent.
        :param assistant_id: The assistant ID if using a preconfigured OpenAI assistant.
        :param openai_api_key: The OpenAI API key for accessing LLM.
        :param tools: List of tools available for this agent.
        """
        tools = self.search_for_datasets
        super().__init__(self.name, assistant_id=self.ASSISTANT_ID, tools=tools)

    def execute(self, thread_id: Optional[int]=None):
        """
        Execute the local dataset search based on the requirements provided in the state.
        Then call the LLM with the data requirements and potential datasets to determine coverage.
        
        :param thread_id: Optional thread ID for context.
        :return: The updated state with identified datasets and coverage analysis.
        """
        agent_response = self.invoke(thread_id=thread_id)
        return 

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
