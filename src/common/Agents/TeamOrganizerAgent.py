from typing import List
from DataCollection.DataCollectionTeam import DataCollectionTeam
from common.Agents import OpenAIAgent
from common.Orchestrators.BaseDynamicTeamOrchestrator import BaseDynamicTeamOrchestrator

prompt = f"Please select the next tool that is best fit for the situation"

class TeamOrganizerAgent(OpenAIAgent):
    """ 
    This agent is reponsible for selecting the next team to execute
    The thread that this is talking in is the main thread of the session
    Each of the teams is treated as a function call and the run will stall until team execution is finished
    The tool call will resolve and place the result in the main thread
    """
    asistant_id = ""
    name="TeamOrganizer"
    def __init__(self):
        self.teams: List[BaseDynamicTeamOrchestrator] = [
            UserInputTeam,
            DataRequirementsTeam,
            DataCollectionTeam
        ]
        tools = [team.execute for team in self.teams]

        super.__init__(name=self.name, assistant_id=self.asistant_id, tools=tools)

    def execute(self, thread_id):
        # This should handle what tool to call next and report any errors
        # Should there be a resolution ever? User could always want to ask for more
        
        self.invoke(content=prompt)
        return 
