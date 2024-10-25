from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentStored:
    id: int
    name: str
    system_prompt: str
    model: str
    functions: list[str]
    response_format: str
    temperature: float
    top_p: float
    api_version: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()