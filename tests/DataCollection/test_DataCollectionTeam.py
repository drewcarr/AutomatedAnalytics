import pytest
from unittest.mock import MagicMock, patch
from DataCollection.DataCollectionTeamState import DataCollectionTeamState
from DataCollection.DataValidatorAgent import DataValidatorAgent
from DataCollection.LocalDatasetAgent import LocalDatasetAgent
from DataCollection.DataCollectionTeam import DataCollectionTeam


class TestDataCollectionTeam:
    @pytest.fixture
    def mock_state(self):
        state = MagicMock(spec=DataCollectionTeamState)
        return state

    @pytest.fixture
    def data_collection_team(self):
        with patch.object(DataCollectionTeam, 'create_thread', return_value=123):
            team = DataCollectionTeam(debug_mode=True)
        return team

    def test_initialization(self, data_collection_team):
        # Test that the team is initialized correctly
        assert len(data_collection_team.agents) == 1
        assert isinstance(data_collection_team.agents[0], LocalDatasetAgent)
        assert isinstance(data_collection_team.validation_agent, DataValidatorAgent)
        assert data_collection_team.thread_id == 123

    @patch('DataCollection.LocalDatasetAgent.execute')
    def test_agent_node(self, mock_execute, data_collection_team, mock_state):
        # Test that the agent node properly executes
        local_dataset_agent = data_collection_team.agents[0]
        data_collection_team.agent_node(mock_state, local_dataset_agent)
        mock_execute.assert_called_once_with(mock_state, thread_id=123)

    @patch('DataCollection.DataValidatorAgent.execute')
    def test_validate(self, mock_validate, data_collection_team, mock_state):
        # Test that the validate method calls the validation agent's execute method
        data_collection_team.validate(mock_state)
        mock_validate.assert_called_once_with(mock_state)

    def test_create_graph(self, data_collection_team):
        # Test the creation of the state graph
        state_graph = data_collection_team.create_graph()
        assert state_graph is not None
        assert DataCollectionTeam.ORCHESTRATOR_NODE in state_graph.nodes
        assert DataCollectionTeam.VALIDATION_NODE in state_graph.nodes
        assert data_collection_team.agents[0].name in state_graph.nodes

    def test_graph_edges(self, data_collection_team):
        # Test that graph edges are created correctly
        state_graph = data_collection_team.create_graph()
        assert ("START", DataCollectionTeam.ORCHESTRATOR_NODE) in state_graph.edges
        assert (data_collection_team.agents[0].name, DataCollectionTeam.ORCHESTRATOR_NODE) in state_graph.edges
        assert (DataCollectionTeam.VALIDATION_NODE, "FINISH") in state_graph.edges

    @patch('DataCollection.DynamicOrchestratorAgent.execute')
    def test_create_supervisor(self, mock_execute, data_collection_team):
        # Test supervisor creation
        supervisor = data_collection_team.create_supervisor()
        assert supervisor is not None
        assert isinstance(supervisor, DataValidatorAgent) or isinstance(supervisor, LocalDatasetAgent)
        mock_execute.assert_not_called()  # No execute call during supervisor creation
