from openai import OpenAI, AssistantEventHandler
from typing_extensions import override


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        if text:
            print(f"\nassistant > {text}", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        if delta.value:  # Only print if delta contains valid text
            print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs" and output.logs:
                        print(f"\n{output.logs}", flush=True)


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
        if not content.strip():  # Ensure the content is non-empty and non-whitespace
            raise ValueError("Message content must be non-empty.")
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )
        print("Appended message to thread: ", self.thread.id, " with content: ", content)

    def create_run_with_stream(self, assistant_id):
        # Create a run with streaming
        try:
            with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=assistant_id,
                event_handler=EventHandler(),
            ) as stream:
                stream.until_done()
        except Exception as e:
            print(f"Error during streaming: {e}")
    
    def send_message(self, content, assistant_id):
        # Append a message from the user after checking if it's non-empty
        self.append_message(content)

        # Create and stream the response from the assistant
        self.create_run_with_stream(assistant_id)

