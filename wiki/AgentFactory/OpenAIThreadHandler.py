from openai import OpenAI
import time

class OpenAIThreadHandler:
    def __init__(self, api_key, thread_id=None):
        self.client = OpenAI(api_key=api_key)
        self.run = None
        if thread_id:
            self.thread = self.client.beta.threads.retrieve(thread_id)
            print("Retrieved thread: ", self.thread.id)
        else:
            self.thread = self.create_thread()
            print("Created thread: ", self.thread.id)

    def create_thread(self):
        try:
            thread = self.client.beta.threads.create()
            return thread
        except Exception as e:
            print(f"Error in creating thread: {e}")
            return None
        
    def append_message(self, content):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )
        print("Appended message to thread: ", self.thread.id, " with content: ", content)

    def create_run(self, assistant_id):
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=assistant_id
        )
        print("Created run: ", self.run.id, "with assistant: ", assistant_id, "on thread: ", self.thread.id)

    def retrieve_run_status(self, run_id, thread_id):
        run_status = self.client.beta.threads.runs.retrieve(
            run_id=run_id,
            thread_id=thread_id,
        )
        print("Status of thread", thread_id, "run", run_id, "is", run_status.status)
        return run_status.status
        
        
    def get_messages(self):
        # Wait for the run to complete
        if (self.run is None) or (self.thread is None):
            raise Exception("Run or thread is not initialized")
        while True:
            run_status = self.retrieve_run_status(self.run.id, self.thread.id)
            if run_status == "completed":
                return self.list_messages()
            elif run_status in ["requires_action", "cancelling", "cancelled", "failed", "expired"]:
                raise Exception(f"Run failed with status: {run_status}")
            time.sleep(2)
        
    def send_message(self, content, assistant_id):
        # Append a message
        self.append_message(content)

        # Create a run
        run = self.create_run(assistant_id)

        ## TODO: This could potentially just be a call to refresh the thread and get the messages again
        messages = self.get_messages()

        # Retrieve and return messages
        return messages
    
    def list_messages(self):
        return self.client.beta.threads.messages.list(thread_id=self.thread.id)
