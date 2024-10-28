from abc import ABC, abstractmethod
import logging
from typing import List, Dict, Optional, Callable

from openai import OpenAI
from openai.types.beta.threads.run import Run


class BaseThreadAgent(ABC):
    def __init__(self, name: str, assistant_id: Optional[str] = None, system_prompt: Optional[str] = None, openai_api_key: str = None, tools: List[Callable] = None, temperature: float = 0.7, top_p: float = 1.0, debug_mode=False):
        self.name = name
        self.available_tools = {tool.__name__: tool for tool in tools} if tools else {}
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
                self.logger.debug(f"Created thread for {self.name}: {thread_id}")
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
            if run.status == 'requires_action':
                tool_outputs = self._handle_tool_calls(run)
                if tool_outputs:
                    run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                        thread_id=thread_id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )
            if run.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread_id
                )
                self.logger.debug(f"Run {run.id} completed")
                return messages
            else:
                self.logger.error(f"Run {run.id} in thread {thread_id} resolved to {run.status}")
        except Exception as e:
            print(f"Error during streaming: {e}")

    def _handle_tool_calls(self, run: Run) -> List[Dict]:
        """
        Handle tool calls required by the assistant and prepare the outputs.
        """
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            if function_name in self.available_tools:
                try:
                    result = self.available_tools[function_name](**arguments)
                    self.logger.debug(f"Executed function '{function_name}' with arguments {arguments}, result: {result}")
                    tool_outputs.append({
                        "tool_call_id": tool_call["id"],
                        "output": str(result)
                    })
                except Exception as e:
                    self.logger.error(f"Error executing function '{function_name}': {e}")
            else:
                self.logger.error(f"Function '{function_name}' is not available in the tools")
        return tool_outputs

    def register_tool(self, tool_func: Callable):
        """
        Dynamically register a new tool that the agent can use.
        """
        self.available_tools[tool_func.__name__] = tool_func
        self.logger.debug(f"Tool '{tool_func.__name__}' registered successfully")
