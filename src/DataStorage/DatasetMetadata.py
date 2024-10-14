import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from typing_extensions import Optional, List, Dict, Literal, TypedDict

class Dataset(TypedDict):
    id: str
    description: str
    data_source: Literal["webscraping", "api"]
    data_link: str  # Should be a url which was scraped from or an api connection
    date_created: str
    date_modified: str

class DatasetMetadata:
    """Static-like class to access dataset metadata and raw data."""
    
    METADATA_FILE = "./metadata.json"  # Default path to the metadata file
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')  # Preload similarity model

    @classmethod
    def set_metadata_file(cls, file_path: str):
        """Set the metadata file path for unit testing."""
        cls.METADATA_FILE = file_path

    @classmethod
    def load_metadata(cls) -> List[Dataset]:
        """Load metadata from the JSON file."""
        try:
            with open(cls.METADATA_FILE, 'r') as file:
                metadata = json.load(file).get("datasets", [])
                return metadata
        except FileNotFoundError:
            print(f"Metadata file not found at {cls.METADATA_FILE}.")
            return []

    @classmethod
    def save_metadata(cls, metadata: List[Dataset]):
        """Save metadata to the JSON file."""
        with open(cls.METADATA_FILE, 'w') as file:
            json.dump({"datasets": metadata}, file, indent=4)

    @classmethod
    def add_dataset(cls, dataset: Dataset):
        """Add a new dataset to the metadata."""
        metadata = cls.load_metadata()
        dataset["date_created"] = datetime.now().isoformat()
        dataset["date_modified"] = dataset["date_created"]
        metadata.append(dataset)
        cls.save_metadata(metadata)

    @classmethod
    def update_dataset(cls, dataset_id: str, updates: Dict):
        """Update an existing dataset and save the changes."""
        metadata = cls.load_metadata()
        for dataset in metadata:
            if dataset["id"] == dataset_id:
                dataset.update(updates)
                dataset["date_modified"] = datetime.now().isoformat()
                cls.save_metadata(metadata)
                return dataset
        return None

    @classmethod
    def search_by_id(cls, dataset_id: str) -> Optional[Dataset]:
        """Find a dataset by its unique ID."""
        metadata = cls.load_metadata()
        for dataset in metadata:
            if dataset["id"] == dataset_id:
                return dataset
        return None

    @classmethod
    def search_by_description(cls, query: str) -> Optional[Dataset]:
        """Perform a semantic search to find datasets by their description."""
        metadata = cls.load_metadata()
        best_matches = []

        query_embedding = cls.similarity_model.encode(query, convert_to_tensor=True)

        for dataset in metadata:
            description_embedding = cls.similarity_model.encode(dataset["description"], convert_to_tensor=True)
            similarity_score = util.pytorch_cos_sim(query_embedding, description_embedding).item()

            if similarity_score > 0.8:  # Set a threshold for matching
                best_matches.append(dataset)

        return best_matches

    @classmethod
    def get_raw_data(cls, dataset_id: str) -> Optional[Dict]:
        """Fetch the raw data for a dataset by ID."""
        dataset = cls.search_by_id(dataset_id)
        if dataset:
            if dataset["data_source"] == "local":
                file_path = dataset["data_link"]
                if file_path and os.path.exists(file_path):
                    with open(file_path, 'r') as file:
                        return json.load(file)  # Assume JSON for now, but could support other formats
            elif dataset["data_source"] == "api":
                api_url = dataset["data_link"]
                # Simulate fetching data from API, could use requests here
                return {"data": f"Fetched data from API: {api_url}"}
        return None

    @classmethod
    def list_datasets(cls) -> List[Dataset]:
        """List all datasets currently stored in the metadata."""
        return cls.load_metadata()

# Example usage
if __name__ == "__main__":
    # Setting a different metadata file for unit testing
    DatasetMetadata.set_metadata_file("./test_metadata.json")

    # Example of adding a dataset
    new_dataset = {
        "id": "stock_prices_2024",
        "description": "Stock prices data for 2024, including daily trading volumes.",
        "data_source": "API",
        "data_link": "https://example.api/stock-prices"
    }
    DatasetMetadata.add_dataset(new_dataset)

    # Example of searching by description
    found_dataset = DatasetMetadata.search_by_description("stock prices data for 2024")
    if found_dataset:
        print(f"Found matching dataset: {found_dataset}")

    # Example of fetching raw data
    raw_data = DatasetMetadata.get_raw_data("stock_prices_2024")
    if raw_data:
        print(f"Raw data: {raw_data}")
