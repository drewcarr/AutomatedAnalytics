import pytest
from unittest.mock import MagicMock
from DataCollection.LocalDatasetAgent import LocalDatasetAgent
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
    agent.invoke = MagicMock(return_value={"messages": [{"content": "Coverage analysis result."}]})
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
    state = {"data_requirements": sample_data_requirements, "messages": []}
    result = mock_agent.execute(state=state)

    # Check if the search_for_datasets and invoke methods were called
    mock_agent.invoke.assert_called_once()
    assert result == {"messages": [{"content": "Coverage analysis result."}]}


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
    assert result == {"message": "No matching datasets found."}

def test_validate_requirements_failure(mock_agent):
    """
    Test the execute method when data requirements fail validation.
    """
    invalid_requirements = DataRequirements(requirement=None, requirements_gathered=True)
    state = {"data_requirements": invalid_requirements, "messages": []}
    result = mock_agent.execute(state=state)

    # Ensure validation error is logged
    mock_agent.logger.error.assert_called()
    assert result is None