from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional, Union
from langchain_openai import OpenAI, ChatOpenAI
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.tools import tool

class LLMWrapper:
    """
    A wrapper for LLM objects to abstract away differences in method signatures.
    """
    def __init__(self, llm: Union[OpenAI, OpenAIAssistantRunnable]):
        self.llm = llm

    def invoke(self, content: str, thread_id: Optional[str] = None) -> Optional[Dict]:
        # Handle invocation based on the type of LLM
        if isinstance(self.llm, OpenAIAssistantRunnable):
            # Use assistant invocation with thread_id if provided
            invoke_payload = {"content": content}
            if thread_id:
                invoke_payload["thread_id"] = thread_id
            return self.llm.invoke(invoke_payload)
        elif isinstance(self.llm, OpenAI):
            # Use regular OpenAI invocation
            return self.llm.invoke(input=content)
        else:
            raise TypeError("Unsupported LLM type provided to LLMWrapper.")

class BaseAgent(ABC):
    def __init__(self, name: str, assistant_id: Optional[str] = None, system_prompt: str = None, openai_api_key: str = None, tools: List[tool] = None, temperature: float = 0.7, top_p: float = 1.0, debug_mode=False):
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
        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.name)
        self.logger.debug(f"Agent '{self.name}' initialized")

    @abstractmethod
    def execute(self) -> Optional[Dict]:
        """ Should be defined to perform the action of the agent """
        pass

    def invoke(self, content: str, thread_id: Optional[str] = None) -> Optional[Dict]:
        """
        Generic method to invoke the llm based on the provided mode.
        
        :param thread_id: Optional thread ID for context.
        :return: The updated state after execution.
        """
        try:
            agent_response = self.llm.invoke(content, thread_id)
            self.logger.debug(f"Agent '{self.name}' invoked model with response: {agent_response}" +
                              (f" on thread {thread_id}" if thread_id else ""))
            return agent_response
        except Exception as e:
            self.logger.error(f"Invocation failed: {e}")
            return None

    def get_tools(self):
        """
        Get the list of tools available to the agent.
        
        :return: List of available tools.
        """
        return self.available_tools
