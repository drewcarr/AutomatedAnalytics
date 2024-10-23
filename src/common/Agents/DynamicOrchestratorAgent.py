from typing import List, Optional, Dict
from common.Agents.BaseAgent import BaseAgent
import tiktoken

from common.Orchestrators.BaseTeamState import BaseTeamState

class DynamicOrchestratorAgent(BaseAgent):
    TOKEN_MAX = 50000
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

    def count_tokens(self, text: str) -> int:
        """Counts tokens using a tokenizer."""
        tokenizer = tiktoken.encoding_for_model("o200k_base")  # Encoding name for gpt-4o
        return len(tokenizer.encode(text))

    def extract_recent_tokens(self, messages: List[str]) -> str:
        """Extracts the last `TOKEN_MAX` from the messages."""
        result = []
        current_tokens = 0

        # Traverse messages from the end to gather recent tokens
        for message in reversed(messages):
            token_count = self.count_tokens(message)
            if current_tokens + token_count > self.TOKEN_MAX:
                break  # Stop if adding this message exceeds the token limit

            result.append(message)
            current_tokens += token_count

        # Join the selected messages in chronological order
        return "\n".join(reversed(result))

    def execute(self, state: BaseTeamState, thread_id: Optional[str] = None) -> Dict:
        """ 
        TODO: add different strategies for selection in future
        Semantic Similarity on descriptions of agents 
            - Might be better for BabyAGI implementation where a clear next task is already defined
        Compression Agent: Have agent summarize the older messages when hitting a token limit
        Capability Weighting with Agent Scoring: constantly updating agent relevance scores
        Reinforcement Learning: capture outcome scores and inject here to reinforce good behavior
        """
        recent_context = self.extract_recent_tokens(state["messages"])

        # I am not sending the thread because I don't want the open ai thread to have more in it than it needs
        agent_response = self.invoke(recent_context)

        next = agent_response.content
        if next not in self.options:
            self.logger.debug("Received invalid next option from orchestrator", {str(agent_response)})
            state.update({"Error": f"Received invalid next option from orchestrator: {str(next)}"})
            return state
        
        state.update({"next": next})
        return state
        
        