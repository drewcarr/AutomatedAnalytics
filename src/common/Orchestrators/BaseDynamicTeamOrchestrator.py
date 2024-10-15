from typing import List, Dict, Optional, Sequence, Type, TypeVar, Generic
from abc import ABC, abstractmethod
import logging
import functools
import operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict
from common.Agents import BaseAgent, DynamicOrchestratorAgent

# Define a generic type for the state
T = TypeVar('T', bound=TypedDict)

class BaseDynamicTeamOrchestrator(ABC, Generic[T]):
    ORCHESTRATOR_NODE = "ORCHESTRATOR_NODE"
    TOOL_NODE = "TOOL_NODE"
    VALIDATION_NODE = "VALIDATION_NODE"

    def __init__(self, agents: List[BaseAgent], tools: List[ToolNode], validator: BaseAgent, debug_mode=False):
        """
        Initialize a dynamic team orchestrator.

        :param agents: A list of agents that the orchestrator coordinates.
        :param tools: A list of tools available to agents.
        :param validator: The agent responsible for validation.
        """
        self.agents = agents
        self.agent_map = {agent.name: agent for agent in agents}
        self.tools = tools
        self.validator = validator

        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Orchestrator '{self.__class__.__name__}' initialized with agents: {[agent.name for agent in agents]}")

        # Create LLM model for orchestration
        self.llm = ChatOpenAI(model="gpt-4o")

        # Create the state graph
        self.state_graph = self.create_graph()

    @property
    @abstractmethod
    def state_class(self) -> Type[T]:
        """
        Property that returns the class representing the state structure, which should be a TypedDict.
        """
        pass

    @abstractmethod
    def validate(self, state: T) -> bool:
        """
        Abstract method to validate whether the answer is accepted.

        :param state: The current state of the session.
        :return: True if the state is valid, False otherwise.
        """
        pass

    def create_supervisor(self, system_prompt: str, members: List[str]) -> DynamicOrchestratorAgent:
        """
        Create an LLM-based supervisor for routing tasks.

        :param system_prompt: The system prompt for the supervisor.
        :param members: The names of the agent team members.
        :return: The supervisor node.
        """
        options = ["FINISH"] + members
        prompt = (
            f"{system_prompt}\nGiven the conversation above, who should act next? Or should we FINISH? Select one of: {options}"
        )
        return DynamicOrchestratorAgent(system_prompt=prompt, function_call="route")

    def create_graph(self) -> StateGraph:
        """
        Create a state graph for the team orchestration.

        :return: The compiled state graph.
        """
        state_graph = StateGraph(self.state_class)

        # Create tool node
        tool_node = ToolNode(self.tools)
        state_graph.add_node(self.TOOL_NODE, tool_node)

        # Create supervisor node
        supervisor_agent = self.create_supervisor(
            "You are a supervisor tasked with managing a conversation between the following workers: {team_members}",
            [agent.name for agent in self.agents],
        )
        state_graph.add_node(self.ORCHESTRATOR_NODE, supervisor_agent.execute)

        state_graph.add_node(self.VALIDATION_NODE, self.validate)

        # Add agent nodes
        for agent in self.agents:
            agent_node = functools.partial(self.agent_node, agent=agent)
            state_graph.add_node(agent.name, agent_node)

        # Define edges
        state_graph.add_edge(START, self.ORCHESTRATOR_NODE)
        state_graph.add_edge(self.TOOL_NODE, self.ORCHESTRATOR_NODE)

        for agent in self.agents:
            state_graph.add_edge(agent.name, self.ORCHESTRATOR_NODE)
            
        state_graph.add_conditional_edges(
            self.ORCHESTRATOR_NODE,
            lambda x: "tool" if "tool_request" in x else x["next"],
            {agent.name: agent.name for agent in self.agents} | {"tool": self.TOOL_NODE, "FINISH": self.VALIDATION_NODE},
        )
        state_graph.add_conditional_edges(
            self.VALIDATION_NODE,
            lambda x: "FINISH" if self.validate(x) else self.ORCHESTRATOR_NODE,
            {"FINISH": END, "ORCHESTRATOR_NODE": self.ORCHESTRATOR_NODE}
        )

        return state_graph.compile()

    def agent_node(self, state: T, agent: BaseAgent):
        """
        Wrapper function to invoke an agent.

        :param state: The current state of the session.
        :param agent: The agent to invoke.
        :return: The updated state after the agent invocation.
        """
        return agent.execute(state)
