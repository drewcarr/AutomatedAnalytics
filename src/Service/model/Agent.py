from dataclasses import dataclass

@dataclass
class Agent:
    id: int
    name: str
    system_prompt: str
    model: str
    functions: list[str]
    response_format: str
    temperature: float
    top_p: float
    api_version: str