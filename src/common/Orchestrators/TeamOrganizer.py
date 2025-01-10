
from common.Agents import TeamOrganizerAgent
from openai import OpenAI

class TeamOrganizer():
    max_iterations = 30
    def __init__(self):
        self.team_organizer_agent = TeamOrganizerAgent()

    def create_thread(self) -> int:
        # If goal given start the thread with it
        client = OpenAI()
        thread = client.beta.threads.create()
        return thread.id

    def run(self):
        thread_id = self.create_thread()

        iterations = 0
        while iterations < self.max_iterations:
            self.team_organizer_agent.execute(thread_id=thread_id)
            iterations += 1
    
