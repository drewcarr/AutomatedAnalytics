from operator import add
from langchain_openai import OpenAI
from langgraph.graph import StateGraph, END, START, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, AnyMessage
from typing_extensions import Annotated, Literal, TypedDict, List
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv, dotenv_values

from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from DataCollection.DataRequirements import DataRequirements
from DataCollection.DataCollectorGraph import DataCollector

# Sets the env to local env - good for automatically setting the OPENAI_API_KEY
load_dotenv("./env")

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    data_source: str
    data_requirements: DataRequirements


class EntryGraph:
    def __init__(self, openai_api_key):
        self.requirements = DataRequirements()
        self.assistant_thread_id = None

        """ Set up tools"""
        tools = [self.set_requirements, self.set_requirements_gathered, self.set_other_fields]
        tool_node = ToolNode(tools)

        # llm = OpenAI(openai_api_key=openai_api_key, temperature=0).bind_tools(tools)
        self.entry_agent = OpenAIAssistantRunnable(assistant_id="asst_FoVIrrN19O1HTH1vL2gYgZs4", 
                                                    as_agent=True,
                                                    tools=tools)

        """ Subgraphs"""
        data_collector = DataCollector()
        

        graph_builder = StateGraph(State)
        
        """ Add all the nodes """
        graph_builder.add_node("chatbot", self.call_model)
        graph_builder.add_node("user_input", self.user_input)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_node("data_collection", data_collector.compile_graph())

        """ Connect nodes with their edges and conditional routing """
        graph_builder.add_edge(START, "user_input")
        graph_builder.add_conditional_edges("chatbot", self.chatbot_router)
        graph_builder.add_conditional_edges("tools", self.tools_router)
        graph_builder.add_conditional_edges("user_input", self.user_router)

        self.graph = graph_builder.compile()
        
    def user_router(self, state: State) -> Literal["chatbot", END]:
        messages: List[BaseMessage] = state["messages"]
        last_message = messages[-1]

        if last_message.content == "exit":
            return END
        
        return "chatbot"
    
    def chatbot_router(self, state: State) -> Literal["tools", "user_input"]:
        messages = state["messages"]
        last_message = messages[-1]
        if "tool_calls" in last_message and last_message.tool_calls:
            return "tools"
        return "user_input"
    
    def tools_router(self, state: State) -> Literal["chatbot", "data_collection"]:
        requirements = state["data_requirements"]
        if requirements.requirements_gathered:
            return "data_collection"
        return "chatbot"

    def call_model(self, state: State):
        last_message = state["messages"][-1]
        
        # Build the invoke payload
        invoke_payload = {"content": last_message.content}
        
        # Only add thread_id if it exists
        if self.assistant_thread_id is not None:
            invoke_payload["thread_id"] = self.assistant_thread_id
        
        # Call the model with the payload
        agent_response = self.entry_agent.invoke(invoke_payload)
        
        # If the agent_response doesn't have a thread_id and assistant_thread_id exists, set it
        if agent_response.thread_id and not self.assistant_thread_id:
            self.assistant_thread_id = agent_response.thread_id
        
        print(agent_response)
        
        return {"messages": [agent_response]}


    
    def user_input(self, state: State):
        user_message = input("You: ")
        return {"messages": [HumanMessage(content=user_message)]}
    
    def run_graph(self):
        return self.graph.invoke(input={"messages": [AIMessage(content="Hello what would you like to do today?")]})
    
    @tool
    def set_requirements(self, new_requirements: str):
        """ Sets the requirements to a new string """
        print("Activating tool: set_requirements")
        self.requirements.requirement = new_requirements.strip()

    @tool
    def set_requirements_gathered(self, requirements_gathered: bool):
        """ Sets whether all requirements have been gathered """
        print("Activating tool: set_requirements_gathered to", requirements_gathered)
        self.requirements.requirements_gathered = requirements_gathered

    @tool
    def set_other_fields(self, **kwargs):
        """ Sets other fields of DataRequirements using set_fields.
        Available fields:
        - requirement (str): Main requirement summarized from the user.
        - timeframe (str): The timeframe for the data, specifying the period of interest.
        - granularity (str): The granularity of the data, such as daily, monthly, etc.
        - domain_context (str): The domain or context for the data, e.g., finance, sports.
        - filters (dict): Filters to apply to the data, represented as key-value pairs (both keys and values should be strings).
        - data_source_preferences (str): Preferences for which data sources to use, e.g., specific APIs or websites.
        - requirements_gathered (bool): A flag indicating whether all necessary requirements have been gathered.
        """
        print("Activating tool: set_other_fields with arguments", kwargs)
        self.requirements.set_fields(**kwargs)


if __name__ == "__main__":
    
    
    chat = EntryGraph(api_key)
    chat.run_graph()