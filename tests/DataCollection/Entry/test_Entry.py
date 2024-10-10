import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from DataCollection.Entry import EntryGraph
from dotenv import load_dotenv, dotenv_values


load_dotenv("./src/DataCollection/.env")

@pytest.fixture
def entry_graph():
    return EntryGraph(openai_api_key="")

def test_initialization(entry_graph):
    assert entry_graph.requirements is not None
    assert entry_graph.assistant_thread_id is None

def test_user_router_chatbot(entry_graph):
    state = {"messages": [HumanMessage(content="continue")]}  # Any content that is not "exit"
    result = entry_graph.user_router(state)
    assert result == "chatbot"

def test_chatbot_router_user_input(entry_graph):
    state = {"messages": [AIMessage(content="dummy message")]}  # No tool_calls attribute
    result = entry_graph.chatbot_router(state)
    assert result == "user_input"

def test_tools_router_requirements_gathered(entry_graph):
    entry_graph.requirements.requirements_gathered = True
    state = {"data_requirements": entry_graph.requirements}
    result = entry_graph.tools_router(state)
    assert result == "data_collection"

def test_tools_router_chatbot(entry_graph):
    entry_graph.requirements.requirements_gathered = False
    state = {"data_requirements": entry_graph.requirements}
    result = entry_graph.tools_router(state)
    assert result == "chatbot"

def test_user_input(entry_graph, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "User message")
    result = entry_graph.user_input(state={})
    assert result == {"messages": [HumanMessage(content="User message")]}
