from operator import add
from langchain_openai import OpenAI
from langgraph.graph import StateGraph, END, START, MessagesState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, AnyMessage
from typing import Annotated, Literal, TypedDict, List
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from dotenv import load_dotenv, dotenv_values

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from DataRequirements import DataRequirements
from DataCollectorGraph import DataCollector

# Sets the env to local env - good for automatically setting the OPENAI_API_KEY
load_dotenv("DataCollection/.env")

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    data_source: str
    data_requirements: DataRequirements


class EntryGraph:
    def __init__(self, openai_api_key, assistant_id):
        self.requirements = DataRequirements()
        self.assistant_thread_id = None

        """ Set up tools"""
        tools = [self.set_requirements, self.toggle_requirements_gathered]
        tool_node = ToolNode(tools)

        # llm = OpenAI(openai_api_key=openai_api_key, temperature=0).bind_tools(tools)
        self.entry_agent = OpenAIAssistantRunnable(clientOptions={"api_key": openai_api_key}, 
                                                    assistant_id=assistant_id, 
                                                    as_agent=True,
                                                    tools=tools
                                                    )

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
        # name mismatch - open ai expects to send "tools" langchain expects tool_calls
        if "tool" in last_message :
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
        
        # Call the model with the payload - This response can be either a single output or a list
        agent_response = self.entry_agent.invoke(invoke_payload)

        # Check if the response is a list, if not, wrap it in a list
        if not isinstance(agent_response, list):
            agent_response = [agent_response]

        # Now agent_response is guaranteed to be a list, so you can safely access elements
        if agent_response[0].thread_id and not self.assistant_thread_id:
            self.assistant_thread_id = agent_response[0].thread_id

        
        print(agent_response)
        
        return {"messages": agent_response}


    
    def user_input(self, state: State):
        user_message = input("You: ")
        return {"messages": [HumanMessage(content=user_message)]}
    
    def run_graph(self):
        return self.graph.invoke(input={"messages": [AIMessage(content="Hello what would you like to do today?")]})
    
    @tool
    def set_requirements(self, new_requirements: str):
        """ Sets the requirements to a new string """
        print("Activating tool: set_requirements")
        self.requirements.set_requirements(new_requirements)

    @tool
    def toggle_requirements_gathered(self, requirements_gathered: bool):
        """ Toogles whether all requirements have been gathered """
        print("Activating tool: toogle_requirements_gathered to ", requirements_gathered)
        self.requirements.requirements_gathered(requirements_gathered)



if __name__ == "__main__":
    env_variables = dotenv_values("DataCollection/.env")
    api_key = env_variables["OPENAI_API_KEY"]
    assistant_id = env_variables["ENTRY_ASSISTANT_ID"]
    
    chat = EntryGraph(openai_api_key=api_key, assistant_id=assistant_id)
    chat.run_graph()

