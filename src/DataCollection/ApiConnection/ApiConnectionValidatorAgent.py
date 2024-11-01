from typing import Optional

from common.Agents import OpenAIAgent

class ApiConnectionValidatorAgent(OpenAIAgent):
    ASSISTANT_ID = "asst_wd88czMW4Yv0OnjhWa9MenZF"
    name = "ApiConnectionValidatorAgent"

    def __init__(self):
        super().__init__(self.name, assistant_id=self.ASSISTANT_ID)

    def execute(self, thread_id: Optional[int]) -> bool:
        agent_response = self.invoke(content="", thread_id=thread_id)

        response_json = agent_response.messages[0]

        return response_json