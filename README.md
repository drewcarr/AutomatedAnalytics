
# DataCollection Project Setup

This guide outlines the steps required to install and set up the `DataCollection` class and its dependencies from the `src/DataCollection` folder for development and testing.

## Project Structure

The project follows a `src` layout, and the main code resides in the `src/DataCollection/` directory. Below is a simplified view of the project structure:

```
AutomatedAnalysis/
│
├── src/
│   └── DataCollection/
│       ├── __init__.py
|       ├── requirements.txt
│       ├── cleaning
│       └── __init__.py
│
├── tests/
│   └── DataCollection/
│       └── test_files.py
│
└── setup.py
```

## Prerequisites

- **Python 3.x**: Ensure you have Python 3.x installed.
- **pip**: The Python package manager to install dependencies.
  
## Installation

### 1. Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone <repository_url>
cd your_project
```

### 2. Set Up a Virtual Environment (Optional but Recommended)

It’s a good practice to create a virtual environment for isolating your project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

All dependencies required by the project are listed in the `requirements.txt` file located in the `src/DataCollection/` directory. To install them, run:

```bash
pip install -r requirements.txt
```

### 4. Install the Project in Editable Mode

To ensure that the project is set up for development, and the `DataCollection` module can be imported correctly, install the project in editable mode. Run the following command from the project root (where `setup.py` is located):

```bash
pip install -e .
```

This will make sure that the `src/DataCollection/` package is linked to the Python environment.

### 5. Running Tests

To verify that everything is set up correctly, run the tests. From the project root directory, execute:

```bash
pytest
```

This will automatically discover and run all the tests inside the `tests/` directory.

### 6. Example Usage

To use the `DataCollection` class in your scripts, you can import it as follows:

```python
from DataCollection.DataCollector import DataCollector

# Example usage
data_collector = DataCollector()
data_collector.collect_data()
```

## Notes

- If you run into issues with module imports, ensure that `src/` is in your `PYTHONPATH`.
- You can modify the `pytest.ini` file to include `src/` for testing purposes:

  ```ini
  [pytest]
  python_paths = src
  ```

- Ensure the `__init__.py` files exist in all necessary directories to treat them as Python packages.

---

