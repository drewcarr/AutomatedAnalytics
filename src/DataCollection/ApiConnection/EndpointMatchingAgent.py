from typing import Optional

from Service.client.ApiConnectionClient import ApiConnectionClient
from common.Agents.BaseAgent import BaseAgent
from common.DataRequirements import DataRequirements


class EndpointMatchingAgent(BaseAgent):
    ASSISTANT_ID = "asst_fo2UaureW9Nn7welyQu488am"
    name = "EndpointMatchingAgent"

    def __init__(self):
        """
        Initialize the EndpointMatchingAgent.
        """
        tools = [self.match_api_connection()]
        self.api_connection_client = ApiConnectionClient()
        super().__init__(self.name, assistant_id=self.ASSISTANT_ID, tools=tools)

    def execute(self, thread_id: Optional[int]=None):
        """
        Execute the endpoint matching process.

        :param thread_id: The thread ID for context.
        """
        agent_response = self.invoke(thread_id=thread_id)
        return agent_response

    def match_api_connection(self, requirements: DataRequirements):
        """
        Fetch the list of endpoints from the API.

        :return: A list of endpoints.
        """

        """
        TODO: We should create a batch GET endpoint using the api connections service
        and hook it up here. We should fetch a page of connections, figure out which one from the batch 
        closest matches the requirements, and continue doing that until we've checked all connections
        
        In the future, it'd be nice to think of a way to minimize the amount of data we need to check for this agent,
        but for now this will do.
        
        This will look something like
        
        best_match = (0.0, None)
        
        while connections := self._get_api_connection_page(id, page_size):
            for connection in connections:
                similarity = self.get_similarity(connection, requirements)
                if similarity > best_match[0]:
                    best_match = (similarity, connection)
        
        return best_match[1]
                    
        """
        pass

    def _get_api_connection_page(self, after_id: int, page_size: int):
        pass