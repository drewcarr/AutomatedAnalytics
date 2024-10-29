import logging
from Service.db.model.AgentStored import AgentStored
from Service.model.Agent import Agent

class MockAgentDb:
    def __init__(self):
        self.data = {}
    
    def get_agent_by_id(self, agent_id: int) -> AgentStored:
        return self.data.get(agent_id)
    
    def upsert_agent(self, agent: AgentStored):
        if agent.id is None:
            agent.id = len(self.data) + 1 
        self.data[agent.id] = agent
        logging.debug(f"Upserted data: {self.data}")
        return self.data[agent.id]
