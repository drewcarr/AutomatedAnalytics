from openai import OpenAI
import time

class OpenAIHandler:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def create_thread(self, messages):
        try:
            thread = self.client.beta.threads.create(
                messages=messages
            )
            return thread
        except Exception as e:
            print(f"Error in creating thread: {e}")
            return None

    def create_run(self, thread_id, assistant_id):
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            return run
        except Exception as e:
            print(f"Error in creating run: {e}")
            return None

    def retrieve_run_status(self, run_id, thread_id):
        try:
            run_status = self.client.beta.threads.runs.retrieve(
                run_id=run_id,
                thread_id=thread_id,
            )
            return run_status.status
        except Exception as e:
            print(f"Error in retrieving run status: {e}")
            return None

    def list_messages(self, thread_id):
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            return messages
        except Exception as e:
            print(f"Error in listing messages: {e}")
            return None
        
    def execute_openai_workflow(self, initial_message, assistant_id):
        # Create a thread
        thread = self.create_thread(messages=[initial_message])
        if not thread:
            return None

        # Create a run
        run = self.create_run(thread_id=thread.id, assistant_id=assistant_id)
        if not run:
            return None

        # Wait for the run to complete
        while True:
            run_status = self.retrieve_run_status(run_id=run.id, thread_id=thread.id)
            if run_status == "completed":
                break
            elif run_status is None:
                return None
            time.sleep(2)

        # Retrieve and return messages
        return self.list_messages(thread_id=thread.id)
