import pytest
from unittest.mock import MagicMock, patch
from DataCollection.DataCollectionTeamState import DataCollectionTeamState
from DataCollection.DataValidatorAgent import DataValidatorAgent
from DataCollection.LocalDatasetAgent import LocalDatasetAgent
from DataCollection.DataCollectionTeam import DataCollectionTeam
from common.Agents.DynamicOrchestratorAgent import DynamicOrchestratorAgent

@pytest.fixture
def mock_state():
    state = MagicMock(spec=DataCollectionTeamState)
    return state

@pytest.fixture
def data_collection_team():
    with patch.object(DataCollectionTeam, 'create_thread', return_value=123):
        team = DataCollectionTeam(debug_mode=True)
    return team

def test_initialization(data_collection_team):
    # Test that the team is initialized correctly
    assert len(data_collection_team.agents) == 1
    assert isinstance(data_collection_team.agents[0], LocalDatasetAgent)
    assert isinstance(data_collection_team.validation_agent, DataValidatorAgent)
    assert data_collection_team.thread_id == 123

@patch('DataCollection.LocalDatasetAgent.LocalDatasetAgent.execute')
def test_agent_node(mock_execute, data_collection_team, mock_state):
    # Test that the agent node properly executes
    local_dataset_agent = data_collection_team.agents[0]
    data_collection_team.agent_node(mock_state, local_dataset_agent)
    mock_execute.assert_called_once_with(mock_state, thread_id=123)

@patch('DataCollection.DataValidatorAgent.DataValidatorAgent.execute')
def test_validate(mock_validate, data_collection_team, mock_state):
    # Test that the validate method calls the validation agent's execute method
    data_collection_team.validate(mock_state)
    mock_validate.assert_called_once_with(mock_state)

def test_create_graph(data_collection_team):
    # Test the creation of the state graph
    state_graph = data_collection_team.create_graph()
    assert state_graph is not None
    assert DataCollectionTeam.ORCHESTRATOR_NODE in state_graph.nodes
    assert DataCollectionTeam.VALIDATION_NODE in state_graph.nodes
    assert data_collection_team.agents[0].name in state_graph.nodes

def test_create_supervisor(data_collection_team):
    # Test supervisor creation
    supervisor = data_collection_team.create_supervisor()
    assert supervisor is not None
    assert isinstance(supervisor, DynamicOrchestratorAgent)