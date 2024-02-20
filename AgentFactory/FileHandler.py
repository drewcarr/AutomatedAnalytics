import re
import json

class FileHandler:
    def __init__(self):
        self.code_block_pattern = re.compile(r"```(\w+?)\n(.*?)```", re.DOTALL)
        self.file_extension_map = {
            "python": ".py",
            "javascript": ".js",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            # Add other mappings as needed
        }

    def read_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def write_file(self, file_path, content):
        try:
            with open(file_path, "w") as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False

    def parse_markdown(self, filename, markdown_content):
        code_blocks = self.code_block_pattern.findall(markdown_content)
        if not code_blocks:
            print("No code blocks found.")
            return None

        parsed_content = []
        for index, (language, code) in enumerate(code_blocks):
            file_extension = self.file_extension_map.get(language.lower(), ".txt")
            file_name = f"{filename}_{index}{file_extension}"
            parsed_content.append((file_name, code))

        return parsed_content

    def save_code_from_markdown(self, filename, markdown_content):
        code_blocks = self.parse_markdown(markdown_content)
        if not code_blocks:
            return []

        saved_files = []
        for file_name, code in code_blocks:
            full_file_name = f"{filename}_{file_name}"
            if self.write_file(full_file_name, code):
                print(f"Saved {full_file_name}")
                saved_files.append(full_file_name)

        return saved_files
