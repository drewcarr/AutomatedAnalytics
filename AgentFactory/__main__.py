import json
from dotenv import load_dotenv
import os

# Assuming OpenAIHandler and FileHandler are defined in separate modules or above in the same file
from OpenAIHandler import OpenAIHandler
from FileHandler import FileHandler



class AgentFactory:
    def __init__(self, api_key):
        self.openai_handler = OpenAIHandler(api_key)
        self.CREATE_AGENT_ASSISTANT=os.getenv("CREATE_AGENT_ASSISTANT")
        self.AGENT_SCHEMA_ASSITANT=os.getenv("AGENT_SCHEMA_ASSITANT")
        self.FUNCTION_CREATION_ASSISTANT=os.getenv("FUNCTION_CREATION_ASSISTANT")
        self.file_handler = FileHandler()

    def execute_openai_workflow(self, initial_message, assistant_id):
        messages = self.openai_handler.execute_openai_workflow(initial_message, assistant_id)
        if not messages:
            print(f"Failed to execute workflow for assistant ID {assistant_id}")
            return None
        return messages
    
    def create_agent_schema(self, project_text):
        initial_message = {
            "role": "user",
            "content": f"Here is a project outline:\n {project_text}"
        }
        project_agent_creation_agent_id = self.CREATE_AGENT_ASSISTANT
        messages = self.execute_openai_workflow(initial_message, project_agent_creation_agent_id)
        if not messages:
            return None

        message_str = messages.data[0].content[0].text.value
        filename = self.file_handler.save_code_from_markdown("agents", message_str)
        with open(filename, "r") as file:
            agent_schema = json.loads(file.read())

        return agent_schema

    def process_agent_schema(self, agent_schema):
        new_agent_schema = []
        function_schema_agent = self.AGENT_SCHEMA_ASSITANT

        for obj in agent_schema:
            initial_message = {
                "role": "user",
                "content": f"Create a function schema for {obj['name']} trying to achieve {obj['description']}"
            }
            messages = self.execute_openai_workflow(initial_message, function_schema_agent)
            if messages:
                message_str = messages.data[0].content[0].text.value
                filename = self.file_handler.save_code_from_markdown(obj['name'], message_str)
                with open(filename, "r") as file:
                    function_definition = json.loads(file.read())
                obj["tools"] = function_definition
                new_agent_schema.append(obj)

        return new_agent_schema

    def create_function_code_blocks(self, new_agent_schema):
        function_code_writer_agent = self.FUNCTION_CREATION_ASSISTANT
        for agent in new_agent_schema:
            agent_name = agent['name']
            os.makedirs(agent_name, exist_ok=True)

            for function in agent['tools']:
                initial_message = {
                    "role": "user",
                    "content": f"Here is the function schema for {function['function']['name']} :\n {json.dumps(function)}"
                }
                messages = self.execute_openai_workflow(initial_message, function_code_writer_agent)
                if messages:
                    message_str = messages.data[0].content[0].text.value
                    filename = f"{agent_name}/{function['function']['name']}.json"
                    self.file_handler.save_code_from_markdown(filename, message_str)

def main():
    load_dotenv("../.env")
    api_key = os.getenv("OPEN_AI_KEY")  # Replace with your actual OpenAI API key
    driver = AgentFactory(api_key)

    # Read project outline from markdown file
    project_text = driver.file_handler.read_file("project_outline.md")
    if project_text is None:
        print("Failed to read project outline.")
        return

    # OpenAI workflow for project outline
    agent_schema = driver.create_agent_schema(project_text)

    # Process each agent in the schema
    agent_schema_with_functions = driver.process_agent_schema(agent_schema)

    # Create code blocks for each function and save to files
    driver.create_function_code_blocks(agent_schema_with_functions)

if __name__ == "__main__":
    main()
