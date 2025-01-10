from abc import ABC, abstractmethod
import logging
from typing import Dict, Optional

from openai import OpenAI

class BaseAgent(ABC):
    def __init__(self, name: str):
        """
        Initialize a generic agent.
        """
        self.name = name
        self.available_tools = tools if tools else []

        # Initialize the LLM based on parameters
        base_llm = OpenAI(openai_api_key=openai_api_key, temperature=temperature, top_p=top_p, system_prompt=system_prompt)
        if assistant_id:
            self.llm = LLMWrapper(OpenAIAssistantRunnable(
                assistant_id=assistant_id,
                as_agent=True,
                tools=self.available_tools,
                llm=base_llm
            ))
        else:
            self.llm = LLMWrapper(base_llm)

        # Setup logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(self.name)
        self.logger.debug(f"Agent '{self.name}' initialized")

        self.client = OpenAI(api_key=openai_api_key)

    @abstractmethod
    def execute(self) -> Optional[Dict]:
        """ Should be defined to perform the action of the agent """
        pass