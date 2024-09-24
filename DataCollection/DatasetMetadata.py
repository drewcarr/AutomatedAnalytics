import json
from datetime import datetime
from sentence_transformers import SentenceTransformer, util
from typing import Optional, List, Dict, Literal, TypedDict

class Dataset(TypedDict):
    id: str
    description: str
    data_source: Literal["local", "api"]
    data_link: str  # Could be a file path for local, or URL for API
    date_created: str
    date_modified: str

class DatasetMetadata:
    """Static-like class to access dataset metadata and raw data."""
    
    METADATA_FILE = "./metadata.json"  # Hardcoded path to the metadata file
    similarity_model = SentenceTransformer('all-MiniLM-L6-v2')  # Preload similarity model

    @classmethod
    def load_metadata(cls) -> List[Dataset]:
        """Load metadata from the hardcoded JSON file."""
        try:
            with open(cls.METADATA_FILE, 'r') as file:
                metadata = json.load(file).get("datasets", [])
                return metadata
        except FileNotFoundError:
            print("Metadata file not found.")
            return []

    @classmethod
    def save_metadata(cls, metadata: List[Dataset]):
        """Save metadata to the hardcoded JSON file."""
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
        best_match = None
        best_score = -1

        query_embedding = cls.similarity_model.encode(query, convert_to_tensor=True)

        for dataset in metadata:
            description_embedding = cls.similarity_model.encode(dataset["description"], convert_to_tensor=True)
            similarity_score = util.pytorch_cos_sim(query_embedding, description_embedding).item()

            if similarity_score > best_score and similarity_score > 0.8:  # Set a threshold for matching
                best_score = similarity_score
                best_match = dataset

        return best_match

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
    # Example of adding a dataset
    new_dataset = {
        "id": "stock_prices_2024",
        "description": "Stock prices data for 2024, including daily trading volumes.",
        "data_source": "local",
        "data_link": "./data/stock_prices_2024.json"
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
