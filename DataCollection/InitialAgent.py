from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, BaseMessage
from typing import TypedDict, List, Callable
from langgraph.prebuilt import ToolExecutor

# Step 1: Define the state of the graph that will track the conversation
class UserState(TypedDict):
    messages: List[BaseMessage]

# Step 2: Set up the nodes of the graph to handle user input and routing
def collect_user_needs(state: UserState):
    messages = state['messages']
    last_message = messages[-1]
    
    # Analyze the user's input to decide on next steps
    user_input = last_message.content.lower()
    
    # This is a simple decision-making process; it could be enhanced with more complex logic
    if "model" in user_input:
        return "model_creation"
    elif "dataset" in user_input:
        return "dataset_curation"
    else:
        return "ask_for_clarity"

def ask_for_clarity(state: UserState):
    # Respond to ask for clarity if user input isn't clear
    return {"messages": [HumanMessage(content="Can you specify if you need help with model creation or dataset curation?")]}

def model_creation(state: UserState):
    # Start the model creation process (details of implementation go in the actual subgraph)
    return {"messages": [HumanMessage(content="Starting model creation process...")]}

def dataset_curation(state: UserState):
    # Start the dataset curation process (details of implementation go in the actual subgraph)
    return {"messages": [HumanMessage(content="Starting dataset curation process...")]}

# Step 3: Set up the graph
def create_graph():
    # Define the state of the conversation
    graph = StateGraph(UserState)

    # Add nodes to handle conversation
    graph.add_node("collect_needs", collect_user_needs)
    graph.add_node("ask_for_clarity", ask_for_clarity)
    graph.add_node("model_creation", model_creation)
    graph.add_node("dataset_curation", dataset_curation)

    # Entry point is the node that collects user input
    graph.set_entry_point("collect_needs")

    # Add conditional edges to route based on user input
    graph.add_conditional_edges(
        "collect_needs",  # Start node
        lambda state: collect_user_needs(state),  # Decision function
        {
            "model_creation": "model_creation",
            "dataset_curation": "dataset_curation",
            "ask_for_clarity": "ask_for_clarity"
        }
    )

    # Add edges to allow conversation to continue after clarity is requested
    graph.add_edge("ask_for_clarity", "collect_needs")
    
    return graph

# Step 4: Connect the graph to the chat function
class LangGraphChat:
    def __init__(self, api_key):
        self.graph = create_graph()
        self.model = ChatOpenAI(api_key=api_key, temperature=0)

    def start_chat(self):
        print("Welcome to the LangGraph-based command line chat!")
        print("Type 'exit' to end the conversation.\n")

        # Initialize conversation state
        state = {"messages": []}

        while True:
            user_input = input("\nYou: ")

            if user_input.lower() == 'exit':
                print("Ending the conversation.")
                break

            # Add the user input to the state
            state["messages"].append(HumanMessage(content=user_input))

            # Invoke the graph with the current state
            state = self.graph.invoke(state)

            # Print the response from the AI
            ai_response = state["messages"][-1].content
            print(f"AI: {ai_response}")

if __name__ == "__main__":
    api_key = ""  # Provide your OpenAI API key here
    chat = LangGraphChat(api_key)
    chat.start_chat()