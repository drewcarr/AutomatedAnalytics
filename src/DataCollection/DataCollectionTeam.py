from typing import List, Dict
from DataCollection.DataValidatorAgent import DataValidatorAgent
from DataCollection.LocalDatasetAgent import DatasetCoverage, LocalDatasetAgent

from common.Orchestrators.BaseDynamicTeamOrchestrator import BaseDynamicTeamOrchestrator



class DataCollectionTeam(BaseDynamicTeamOrchestrator):
    def __init__(self, debug_mode=False):
        """
        Initialize a data collection team orchestrator.

        :param local_dataset_agent: An agent responsible for retrieving data from local datasets.
        :param tools: A list of tools available to agents.
        :param validator: The agent responsible for validation.
        :param debug_mode: Enable or disable debug mode for logging.
        """
        local_dataset_agent = LocalDatasetAgent()
        self.validation_agent = DataValidatorAgent()
        """ TODO: Missing a bunch of other agents here. List is subject to change
        - DataSource Identifier
        - API Manager
        - WebScraping Manager
        - Storage Manager
        """
        agents = [local_dataset_agent]
        super().__init__(agents=agents, debug_mode=debug_mode)

    def validate(self) -> bool:
        """
        Validate the collected data to determine if it meets requirements.

        :param state: The current state of the session.
        :return: True if the state is valid, False otherwise.
        """
        response = self.validation_agent.execute(thread_id=self.thread_id)

        self.data_sources = response.data_sources
        
        return response.validated

    def get_data_sources(self, data_requirements: str):
        self.execute()

        return self.data_sources