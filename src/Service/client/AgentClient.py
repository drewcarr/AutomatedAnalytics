import requests
from Service.model.Agent import Agent

class AgentClient:
    def __init__(self):
        # TODO: eventually point this towards our load balancer
        self.base_url = "http://localhost:8000"
    
    def get_agent_by_id(self, agent_id: int):
        try:
            response = requests.get(self.base_url + "/v1/agents/" + str(agent_id))
            return Agent(**response.json()['message'])
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def upsert_agent(self, agent: Agent):
        try:
            response = requests.put(self.base_url + "/v1/agents", json=agent.__dict__)
            return Agent(**response.json()['message'])
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}