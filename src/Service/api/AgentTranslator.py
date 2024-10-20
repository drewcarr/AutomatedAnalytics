from Service.db.MockAgentDb import MockAgentDb
from Service.model.Agent import Agent
from Service.db.model.AgentStored import AgentStored

class AgentTranslator:
    def __init__(self, mock_db: MockAgentDb):
        self.mock_db = mock_db
    
    def get_agent(self, agent_id: int):
        agent_stored = self.mock_db.get_agent_by_id(agent_id)
        return self._to_agent(agent_stored)

    def upsert_agent(self, agent: Agent):
        agent_stored = self.mock_db.upsert_agent(self._to_agent_stored(agent))
        return self._to_agent(agent_stored)

    @staticmethod
    def _to_agent(agent_stored: AgentStored):
        return Agent(
            id=agent_stored.id,
            name=agent_stored.name,
            prompt=agent_stored.prompt,
            model=agent_stored.model,
            functions=agent_stored.functions,
            response_format=agent_stored.response_format,
            temperature=agent_stored.temperature,
            top_p=agent_stored.top_p,
            api_version=agent_stored.api_version
        )
    
    @staticmethod
    def _to_agent_stored(agent: Agent):
        return AgentStored(
            id=agent.id,
            name=agent.name,
            prompt=agent.prompt,
            model=agent.model,
            functions=agent.functions,
            response_format=agent.response_format,
            temperature=agent.temperature,
            top_p=agent.top_p,
            api_version=agent.api_version
        )
