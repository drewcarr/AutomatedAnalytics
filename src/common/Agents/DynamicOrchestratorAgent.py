from typing import List, Optional, Dict
from common.Agents import OpenAIAgent
import tiktoken


class DynamicOrchestratorAgent(OpenAIAgent):
    name="DynamicOrchestratorAgent"
    def __init__(self, tools: Optional[str]=None, team_members=[]):
        """
        Initialize the LocalDatasetAgent.
        
        :param name: The name of the agent.
        :param assistant_id: The assistant ID if using a preconfigured OpenAI assistant.
        :param openai_api_key: The OpenAI API key for accessing LLM.
        :param tools: List of tools available for this agent.
        """
        self.options = ["FINISH"] + team_members
        system_prompt = (
            f"""You are a supervisor tasked with managing a conversation between the following workers: {team_members}
            \nGiven the conversation above, who should act next? Or should we FINISH? Select one of: {self.options}"""
        )
        super().__init__(self.name, system_prompt=system_prompt, tools=tools)

    def execute(self, thread_id: Optional[str] = None) -> Dict:
        """ 
        TODO: add different strategies for selection in future
        Semantic Similarity on descriptions of agents 
            - Might be better for BabyAGI implementation where a clear next task is already defined
        Compression Agent: Have agent summarize the older messages when hitting a token limit
        Capability Weighting with Agent Scoring: constantly updating agent relevance scores
        Reinforcement Learning: capture outcome scores and inject here to reinforce good behavior
        """
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)

        # I am not sending the thread because I don't want the open ai thread to have more in it than it needs
        agent_response = self.invoke(messages)

        next = agent_response.content[0]
        if next not in self.options:
            self.logger.debug("Received invalid next option from orchestrator", {str(agent_response)})
            # TODO: put in the thread chat that there was an error - either have an error agent handle or have orchestrator contribute to chat
        
        return next
        
        