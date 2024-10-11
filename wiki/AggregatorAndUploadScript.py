import os
from openai import OpenAI
from dotenv import load_dotenv



def aggregate_markdown_files(directory):
    """
    Aggregates markdown files from a given directory into a single file. THIS DOES NOT HANDLE SUBDIRECTORIES.
    Args:
    directory (str): The directory containing markdown files.
    Returns:
    str: Path to the aggregated file.
    """
    aggregated_content = ""
    aggregated_file_name = "aggregated_notes.md"
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r') as file:
                content = file.read()
                aggregated_content += f"\n# {filename}\n\n{content}\n"
    
    with open(aggregated_file_name, 'w') as aggregated_file:
        aggregated_file.write(aggregated_content)
    
    return aggregated_file_name

def upload_to_openai(file_path, api_key):
    """
    Uploads a file to OpenAI.
    Args:
    file_path (str): The path to the file to be uploaded.
    api_key (str): Your OpenAI API key.
    Returns:
    dict: The response from the OpenAI API.
    """
    client = OpenAI(api_key=api_key)

    with open(file_path, 'rb') as file:
        # response = requests.post(url, headers=headers, files={"file": file})
        file = client.files.create(
            file=file,
            purpose='assistants'
        )

    ## Rename the file to the file.id
    os.rename(file_path, file.id + ".md")
    
    return file.id

load_dotenv()
# Example usage
directory = "/Users/drewcarr/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"  # Replace with your actual directory path
api_key = os.getenv("OPEN_AI_KEY")  

# Aggregate markdown files
aggregated_file = aggregate_markdown_files(directory)

# Upload to OpenAI
# Uncomment the line below to perform the upload. Make sure you have a valid API key.
response = upload_to_openai(aggregated_file, api_key)
print(response)
