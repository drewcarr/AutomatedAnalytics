import pytest
from unittest.mock import MagicMock
from DataCollection.LocalDatasetAgent import LocalDatasetAgent, DatasetCoverage
from common.DataRequirements import DataRequirements
from DataStorage.DatasetMetadata import DatasetMetadata

@pytest.fixture
def mock_agent():
    """
    Fixture to create a mock instance of LocalDatasetAgent with mocked dependencies.
    """
    agent = LocalDatasetAgent(
        name="TestLocalDatasetAgent",
        openai_api_key="test_api_key",
        tools=None,
    )
    agent.logger = MagicMock()
    agent.invoke = MagicMock(return_value=[
        {
            "dataset_id": "dataset_1",
            "covered_requirements": {"requirement_1": True},
            "missing_requirements": {"requirement_2": "Not available"}
        }
    ])
    return agent

@pytest.fixture
def sample_data_requirements():
    """
    Fixture to create a sample DataRequirements instance.
    """
    return DataRequirements(
        requirement="Stock prices for 2024",
        domain_context="finance",
        granularity="daily",
        timeframe="2024",
        requirements_gathered=True
    )

@pytest.fixture
def mock_dataset_metadata():
    """
    Fixture to mock DatasetMetadata class for testing purposes.
    """
    original_search_by_description = DatasetMetadata.search_by_description
    DatasetMetadata.search_by_description = MagicMock(return_value={
        "id": "dataset_1",
        "description": "Daily stock prices for 2024",
        "data_source": "api",
        "data_link": "https://example.com/api/stock-prices"
    })
    yield
    DatasetMetadata.search_by_description = original_search_by_description

def test_execute_with_valid_requirements(mock_agent, sample_data_requirements, mock_dataset_metadata):
    """
    Test the execute method with valid data requirements.
    """
    state = {"data_requirements": sample_data_requirements, "messages": [{"content": "Find stock prices for 2024"}]}
    result = mock_agent.execute(state=state)

    # Check if the search_for_datasets and invoke methods were called
    mock_agent.invoke.assert_called_once()
    assert "dataset_coverages" in result
    assert isinstance(result["dataset_coverages"], list)
    assert isinstance(result["dataset_coverages"][0], DatasetCoverage)

def test_execute_with_missing_requirements(mock_agent):
    """
    Test the execute method when data requirements are missing in the state.
    """
    state = {"messages": []}
    result = mock_agent.execute(state=state)

    # Check if error was logged
    mock_agent.logger.error.assert_called_with("Data requirements not provided in state.")
    assert result is None

def test_search_for_datasets(mock_agent, sample_data_requirements, mock_dataset_metadata):
    """
    Test the search_for_datasets method to ensure it returns the correct dataset.
    """
    result = mock_agent.search_for_datasets(sample_data_requirements)

    # Ensure the mocked search_by_description was called
    DatasetMetadata.search_by_description.assert_called_once_with(
        "Stock prices for 2024 finance daily 2024"
    )
    assert result == {
        "id": "dataset_1",
        "description": "Daily stock prices for 2024",
        "data_source": "api",
        "data_link": "https://example.com/api/stock-prices"
    }

def test_execute_no_matching_datasets(mock_agent, sample_data_requirements):
    """
    Test the execute method when no datasets match the requirements.
    """
    mock_agent.search_for_datasets = MagicMock(return_value=None)
    state = {"data_requirements": sample_data_requirements, "messages": []}
    result = mock_agent.execute(state=state)

    # Ensure no dataset found scenario is handled properly
    mock_agent.logger.info.assert_called_with("No matching datasets found.")
    assert "dataset_coverages" in result
    assert isinstance(result["dataset_coverages"], list)
    assert result["dataset_coverages"][0].dataset_id == "None"

def test_validate_requirements_failure(mock_agent):
    """
    Test the execute method when data requirements fail validation.
    """
    invalid_requirements = DataRequirements(requirement=None, requirements_gathered=True)
    state = {"data_requirements": invalid_requirements, "messages": []}
    result = mock_agent.execute(state=state)

    # Ensure validation error is logged
    mock_agent.logger.error.assert_called()
    assert "Error" in result
    assert "Validation error" in result["Error"]

def test_execute_with_invalid_agent_response(mock_agent, sample_data_requirements, mock_dataset_metadata):
    """
    Test the execute method when the agent response is invalid or incorrectly formatted.
    """
    # Simulate an invalid response
    mock_agent.invoke = MagicMock(return_value="Invalid response")
    state = {"data_requirements": sample_data_requirements, "messages": []}
    result = mock_agent.execute(state=state)

    # Ensure error handling for invalid response
    mock_agent.logger.error.assert_called()
    assert "Error" in result
    assert "Error processing agent response" in result["Error"]