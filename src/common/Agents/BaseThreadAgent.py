
from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional, Union
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.tools import tool
from typing_extensions import override

from openai import OpenAI
from openai.types.beta.threads.run import Run


class BaseAgent(ABC):
    def __init__(self, name: str, assistant_id: Optional[str] = None, system_prompt: Optional[str] = None, openai_api_key: str = None, tools: List[tool] = None, temperature: float = 0.7, top_p: float = 1.0, debug_mode=False):
        self.name = name
        self.available_tools = tools if tools else []
        self.assistant_id = assistant_id
        self.system_prompt = system_prompt

        self.client = OpenAI(api_key=openai_api_key)
        # Setup logging
        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.name)
        self.logger.debug(f"Agent '{self.name}' initialized")

    @abstractmethod
    def execute(self) -> Optional[Dict]:
        """ Should be defined to perform the action of the agent """
        pass

    def invoke(self, content: str, thread_id: Optional[str] = None, system_prompt: str="") -> Optional[Dict]:
        """
        Generic method to invoke the llm based on the provided mode.
        
        """
        # If no thread set, then create thread for this run
        try:
            if not thread_id:
                thread_id = self.client.beta.threads.create()
                self.logger.debug(f"Created thread for {self.name}: ", thread_id)
        except Exception as e:
            self.logger.error(f"Invocation failed: {e}")
            return None
        
        # Append Content to the thread
        if not content.strip():  # Ensure the content is non-empty and non-whitespace
            raise ValueError("Message content must be non-empty.")
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )

        # Run thread - Have the assistant generate in the thread - this can be changed to stream the output
        try:
            run: Run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                instructions=system_prompt
            )
            if run.status == 'completed': 
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                self.logger.debug(f"Run {run.id} completed with steps")
                return messages # Returning entire conversation
            else:
                self.logger.error(f"Run {run.id} in thread {thread_id} resolved to {run.status}")
        except Exception as e:
            print(f"Error during streaming: {e}")

