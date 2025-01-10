from typing import List, Optional, Union
from abc import ABC, abstractmethod
import logging
from common.Agents import OpenAIAgent
from common.Agents.DynamicOrchestratorAgent import DynamicOrchestratorAgent
from common.Agents.BaseAgent import BaseAgent
from openai import OpenAI

class BaseDynamicTeamOrchestrator(ABC):
    def __init__(self, agents: List[BaseAgent], tools: Optional[List[function]] = None, debug_mode=False, max_iterations=30):
        """
        Initialize a dynamic team orchestrator.

        :param agents: A list of agents that the orchestrator coordinates.
        :param tools: A list of tools available to agents.
        """
        self.agents = agents
        self.agent_map = {agent.name: agent for agent in agents}
        self.tools = tools if tools else []

        self.max_iterations = max_iterations

        logging.basicConfig(level=logging.DEBUG if debug_mode else logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Orchestrator '{self.__class__.__name__}' initialized with agents: {[agent.name for agent in agents]}")

    @abstractmethod
    def validate(self) -> bool:
        """
        Abstract method to validate whether the answer is accepted.
        For now can use thread id to say why in the thread so agents can correct
        """
        pass

    def create_thread(self, goal: str = None) -> int:
        # If goal given start the thread with it
        client = OpenAI()
        if goal:
            goal_str = f"Goal of conversation {goal}"
            thread = client.beta.threads.create(messages=[{"content": goal_str}])
        else:
            thread = client.beta.threads.create()
        return thread.id

    def create_supervisor(self) -> DynamicOrchestratorAgent:
        """
        Create an LLM-based supervisor for routing tasks.

        :return: The supervisor node.
        """
        team_members = [agent.name for agent in self.agents]
        return DynamicOrchestratorAgent(team_members=team_members)

    def execute(self, goal: str = None):
        """
        Execute the orchestrator workflow by dynamically routing tasks between agents
        until the task is completed or validated.
        """
        self.logger.info("Execution started for dynamic team orchestration with a max iteration count of {}.".format(self.max_iterations))

        self.thread_id = self.create_thread(goal)

        # Initialize supervisor orchestrator agent
        orchestrator_agent = self.create_supervisor()

        iteration_count = 0
        while iteration_count < self.max_iterations:
            # Determine next agent and process
            next_agent_name = orchestrator_agent.execute(self.thread_id)
            if next_agent_name == "FINISHED":
                self.logger.info("Workflow has reached the FINISHED state.")

                # Perform validation once workflow is marked FINISHED
                self.logger.info("Starting validation phase.")
                validated = self.validate()
                if validated:
                    self.logger.info("Validation successful. Workflow completed.")
                    break 
                else:
                    self.logger.warning("Validation failed. Re-executing workflow for corrections.")
                    # Handle re-execution or revision flow if validation fails

            # Identify the agent from the list
            if next_agent_name in self.agent_map:
                current_agent = self.agent_map[next_agent_name]
                self.logger.info(f"Executing agent: {current_agent.name}")

                # Execute agent with the shared thread context
                current_agent.execute(thread_id=self.thread_id)
            else:
                self.logger.error(f"Unknown agent name '{next_agent_name}' provided by orchestrator.")
            iteration_count += 1

    def execute_round_robin(self, goal: str = None):
        """
        Execute the orchestrator workflow using a round robin strategy for selecting agents.
        Each agent gets a turn to process until the task is completed or validated.
        """
        self.logger.info("Execution started for round robin team orchestration with a max iteration count of {}.".format(self.max_iterations))

        self.thread_id = self.create_thread(goal)

        iteration_count = 0
        agent_index = 0
        num_agents = len(self.agents)

        while iteration_count < self.max_iterations:
            current_agent = self.agents[agent_index]
            self.logger.info(f"Executing agent: {current_agent.name}")

            # Execute agent with the shared thread context
            current_agent.execute(thread_id=self.thread_id)

            # Move to the next agent in round robin fashion
            agent_index = (agent_index + 1) % num_agents

            # Perform validation periodically
            if iteration_count % num_agents == 0 and iteration_count > 0:
                self.logger.info("Starting validation phase.")
                validated = self.validate()
                if validated:
                    self.logger.info("Validation successful. Workflow completed.")
                    break
                else:
                    self.logger.warning("Validation failed. Continuing round robin execution.")

            iteration_count += 1

        if iteration_count >= self.max_iterations:
            self.logger.warning("Max iteration count reached. Workflow did not complete successfully.")
