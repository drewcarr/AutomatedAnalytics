from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional, Callable

from openai import OpenAI
from openai.types.beta.threads.run import Run

from common.Agents.BaseAgent import BaseAgent


class HumanAgent(BaseAgent):
    def __init__(self, name: str = None):
        self.name = name

        super.__init__(name=name)

    def execute(self, thread_id) -> Optional[Dict]:
        """ Should be defined to perform the action of the agent """
        user_message = input("You: ")
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )
