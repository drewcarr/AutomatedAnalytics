import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from DataCollection.Entry import EntryGraph

@pytest.fixture
def entry_graph():
    return EntryGraph(openai_api_key="dummy_key")

def test_initialization(entry_graph):
    assert entry_graph.requirements is not None
    assert entry_graph.assistant_thread_id is None

def test_set_requirements(entry_graph):
    entry_graph.set_requirements("  Analyze sales data ")
    assert entry_graph.requirements.requirement == "Analyze sales data"

def test_set_requirements_gathered(entry_graph):
    entry_graph.set_requirements_gathered(True)
    assert entry_graph.requirements.requirements_gathered is True
    entry_graph.set_requirements_gathered(False)
    assert entry_graph.requirements.requirements_gathered is False

def test_set_other_fields(entry_graph):
    entry_graph.set_other_fields(timeframe="2022", domain_context="finance")
    assert entry_graph.requirements.timeframe == "2022"
    assert entry_graph.requirements.domain_context == "finance"

def test_set_other_fields_invalid(entry_graph):
    with pytest.raises(ValueError, match="not a valid field of DataRequirements"):
        entry_graph.set_other_fields(invalid_field="invalid")

def test_user_router_exit(entry_graph):
    state = {"messages": [HumanMessage(content="exit")]}
    result = entry_graph.user_router(state)
    assert result == "END"

def test_user_router_chatbot(entry_graph):
    state = {"messages": [HumanMessage(content="continue")]}  # Any content that is not "exit"
    result = entry_graph.user_router(state)
    assert result == "chatbot"

@patch("EntryGraph.EntryGraph.call_model")
def test_chatbot_router_tool_calls(mock_call_model, entry_graph):
    mock_call_model.return_value = {"tool_calls": ["set_requirements"]}
    state = {"messages": [AIMessage(content="dummy message", tool_calls=["set_requirements"])]}
    result = entry_graph.chatbot_router(state)
    assert result == "tools"

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

@patch("EntryGraph.EntryGraph.entry_agent")
def test_call_model(mock_entry_agent, entry_graph):
    mock_entry_agent.invoke.return_value = AIMessage(content="response", thread_id="1234")
    state = {"messages": [HumanMessage(content="Hello")]}  # Simulate user input
    result = entry_graph.call_model(state)
    mock_entry_agent.invoke.assert_called_once_with({"content": "Hello"})
    assert result == {"messages": [mock_entry_agent.invoke.return_value]}
    assert entry_graph.assistant_thread_id == "1234"

def test_user_input(entry_graph, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "User message")
    result = entry_graph.user_input(state={})
    assert result == {"messages": [HumanMessage(content="User message")]}

def test_run_graph(entry_graph, monkeypatch):
    # Mocking input and AI response
    monkeypatch.setattr('builtins.input', lambda _: "User message")
    entry_graph.entry_agent.invoke = MagicMock(return_value=AIMessage(content="response"))
    entry_graph.run_graph()
    entry_graph.entry_agent.invoke.assert_called()