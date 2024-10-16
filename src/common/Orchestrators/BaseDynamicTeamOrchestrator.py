from typing import List
from abc import ABC, abstractmethod
import logging
import functools
from operator import add
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode
from typing_extensions import Annotated, TypedDict
from common.Agents import BaseAgent, DynamicOrchestratorAgent

# Define a generic type for the state
class BaseTeamState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    validated: bool
    next: str
    Error: str

class BaseDynamicTeamOrchestrator(ABC):
    ORCHESTRATOR_NODE = "ORCHESTRATOR_NODE"
    TOOL_NODE = "TOOL_NODE"
    VALIDATION_NODE = "VALIDATION_NODE"

    def __init__(self, agents: List[BaseAgent], tools: List[ToolNode], debug_mode=False):
        """
        Initialize a dynamic team orchestrator.

        :param agents: A list of agents that the orchestrator coordinates.
        :param tools: A list of tools available to agents.
        :param validator: The agent responsible for validation.
        """
        self.agents = agents
        self.agent_map = {agent.name: agent for agent in agents}
        self.tools = tools

        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Orchestrator '{self.__class__.__name__}' initialized with agents: {[agent.name for agent in agents]}")

        # Create the state graph
        self.state_graph = self.create_graph()

    @abstractmethod
    def validate(self, state: BaseTeamState) -> BaseTeamState:
        """
        Abstract method to validate whether the answer is accepted.
        Should set the validated field either True or False
        If False, should give context back to orchestrator by adding message to state

        :param state: The current state of the session.
        :return: True if the state is valid, False otherwise.
        """
        pass

    def create_supervisor(self) -> DynamicOrchestratorAgent:
        """
        Create an LLM-based supervisor for routing tasks.

        :return: The supervisor node.
        """
        team_members = [agent.name for agent in self.agents]
        return DynamicOrchestratorAgent(team_members=team_members)

    def create_graph(self) -> StateGraph:
        """
        Create a state graph for the team orchestration.

        :return: The compiled state graph.
        """
        state_graph = StateGraph(BaseTeamState)

        # Create tool node
        tool_node = ToolNode(self.tools)
        state_graph.add_node(self.TOOL_NODE, tool_node)

        # Create supervisor node
        supervisor_agent = self.create_supervisor()
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
            
        """ Orchestrator can route to tools, agents or validation when it thinks it is done """
        state_graph.add_conditional_edges(
            self.ORCHESTRATOR_NODE,
            lambda x: "tool" if "tool_request" in x else x["next"],
            {agent.name: agent.name for agent in self.agents} | {"tool": self.TOOL_NODE, "FINISH": self.VALIDATION_NODE},
        )

        """
        Validator needs to set the field validated in base class and if True then Finished else back to orchestrator 
        Note: Validator should add a message that says why not validated
        """
        state_graph.add_conditional_edges(
            self.VALIDATION_NODE,
            lambda state: "FINISH" if state.get("validated", False) else self.ORCHESTRATOR_NODE,
            {"FINISH": END, "ORCHESTRATOR_NODE": self.ORCHESTRATOR_NODE}
    )

        return state_graph.compile()

    def agent_node(self, state: BaseTeamState, agent: BaseAgent):
        """
        Wrapper function to invoke an agent.

        :param state: The current state of the session.
        :param agent: The agent to invoke.
        :return: The updated state after the agent invocation.
        """
        return agent.execute(state)
