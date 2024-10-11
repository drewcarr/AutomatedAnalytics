import pytest
import json
import os
from unittest.mock import patch, mock_open
from DataStorage.DatasetMetadata import DatasetMetadata


@pytest.fixture
def mock_metadata_file():
    """Fixture to create a mock metadata file."""
    mock_data = {
        "datasets": [
            {
                "id": "dataset_1",
                "description": "Description of dataset 1.",
                "data_source": "webscraping",
                "data_link": "https://example.com/data1",
                "date_created": "2024-01-01T00:00:00",
                "date_modified": "2024-01-01T00:00:00"
            },
            {
                "id": "dataset_2",
                "description": "Description of dataset 2.",
                "data_source": "api",
                "data_link": "https://example.com/data2",
                "date_created": "2024-02-01T00:00:00",
                "date_modified": "2024-02-01T00:00:00"
            }
        ]
    }
    mock_data_str = json.dumps(mock_data)
    with patch("builtins.open", mock_open(read_data=mock_data_str)):
        yield DatasetMetadata.METADATA_FILE


@pytest.fixture
def set_metadata_path(tmp_path):
    """Fixture to set up temporary metadata path for testing."""
    test_metadata_file = tmp_path / "metadata.json"
    DatasetMetadata.METADATA_FILE = str(test_metadata_file)
    return test_metadata_file


def test_load_metadata(mock_metadata_file):
    """Test that the metadata file can be loaded correctly."""
    metadata = DatasetMetadata.load_metadata()
    assert len(metadata) == 2
    assert metadata[0]["id"] == "dataset_1"


def test_add_dataset(set_metadata_path):
    """Test adding a new dataset to the metadata."""
    new_dataset = {
        "id": "new_dataset",
        "description": "New dataset description.",
        "data_source": "api",
        "data_link": "https://example.com/new_dataset"
    }
    DatasetMetadata.add_dataset(new_dataset)
    metadata = DatasetMetadata.load_metadata()
    assert len(metadata) == 1
    assert metadata[0]["id"] == "new_dataset"
    assert "date_created" in metadata[0]
    assert "date_modified" in metadata[0]


def test_update_dataset(mock_metadata_file, set_metadata_path):
    """Test updating an existing dataset."""
    updates = {
        "description": "Updated description of dataset 1."
    }
    updated_dataset = DatasetMetadata.update_dataset("dataset_1", updates)
    assert updated_dataset is not None
    assert updated_dataset["description"] == "Updated description of dataset 1."
    assert "date_modified" in updated_dataset
    assert updated_dataset["date_modified"] != "2024-01-01T00:00:00"


def test_search_by_id(mock_metadata_file):
    """Test searching for a dataset by its ID."""
    dataset = DatasetMetadata.search_by_id("dataset_1")
    assert dataset is not None
    assert dataset["id"] == "dataset_1"


def test_search_by_description(mock_metadata_file):
    """Test searching for a dataset by its description using the DatasetMetadata method."""
    dataset = DatasetMetadata.search_by_description("Description of dataset 1.")
    assert dataset is not None
    assert dataset["id"] == "dataset_1"


def test_list_datasets(mock_metadata_file):
    """Test listing all datasets."""
    datasets = DatasetMetadata.list_datasets()
    assert len(datasets) == 2
    assert datasets[0]["id"] == "dataset_1"
    assert datasets[1]["id"] == "dataset_2"