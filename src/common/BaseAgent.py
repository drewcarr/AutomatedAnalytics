from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional
from langchain_openai import OpenAI
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.tools import tool

class BaseAgent(ABC):
    def __init__(self, name: str, assistant_id: str, openai_api_key: str, tools: List[tool] = None, temperature: float = 0.7, top_p: float = 1.0, debug_mode=False):
        """
        Initialize a generic agent.
        
        :param name: The name of the agent (for identification purposes).
        :param openai_api_key: The API key to access OpenAI services.
        :param tools: A list of tools that the agent can use.
        :param temperature: The temperature parameter for the language model.
        :param top_p: The top_p parameter for the language model.
        """
        self.name = name
        self.available_tools = tools if tools else []
        if assistant_id:
            self.llm = OpenAIAssistantRunnable(assistant_id=assistant_id, 
                                                as_agent=True,
                                                tools=tools,
                                                temperature=temperature,
                                                top_p=top_p)
        else:
            self.llm = OpenAI(openai_api_key=openai_api_key, temperature=temperature, top_p=top_p).bind_tools(self.available_tools)

        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.name)
        self.logger.debug(f"Agent '{self.name}' initialized")

    def invoke(self, state: Dict, thread_id: Optional[str] = None) -> Optional[Dict]:
        """
        Generic method to invoke the agent based on the provided mode.
        
        :param state: The state of the agent session.
        :param thread_id: Optional thread ID for context.
        :return: The updated state after execution.
        """
        last_message = state.get("messages", [])[-1]
        invoke_payload = {"content": last_message.content}

        # Add thread_id if provided
        if thread_id:
            invoke_payload["thread_id"] = thread_id

        agent_response = self.llm.invoke(invoke_payload)

        self.logger.debug(f"Agent '{self.name}' invoked model with response: {agent_response}" +
                 (f" on thread {thread_id}" if thread_id else ""))

        return {"messages": [agent_response]}


    def get_tools(self):
        """
        Get the list of tools available to the agent.
        
        :return: List of available tools.
        """
        return self.available_tools