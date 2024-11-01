from DataCollection.ApiConnection.ApiConnectionValidatorAgent import ApiConnectionValidatorAgent
from DataCollection.ApiConnection.EndpointMatchingAgent import EndpointMatchingAgent
from common.DataRequirements import DataRequirements
from common.Orchestrators.BaseDynamicTeamOrchestrator import BaseDynamicTeamOrchestrator


class ApiConnectionTeam(BaseDynamicTeamOrchestrator):
    def __init__(self, debug_mode=False):
        """
        Initialize an API connection team orchestrator.

        :param debug_mode: Enable or disable debug mode for logging.
        """
        endpoint_matching_agent = EndpointMatchingAgent()
        self.validator_agent = ApiConnectionValidatorAgent()

        agents = [endpoint_matching_agent]

        self.api_connection_id = -1
        super().__init__(agents=agents, debug_mode=debug_mode)


    def validate(self) -> bool:
        """
        Validate the API connection to determine if it meets our requirements.

        :return: True if the connection is successful, False otherwise.
        """
        response = self.validator_agent.execute(thread_id=self.thread_id)

        self.api_connection_id = response.api_connection_id

        return response.validated

    def get_api_connection(self, data_requirements: DataRequirements):
        goal = f"You are tasked with acquiring an api connection to achieve the following data requirements \n {str(data_requirements)}"
        self.execute(goal=goal)

        return self.api_connection_id