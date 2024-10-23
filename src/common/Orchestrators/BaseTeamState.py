from operator import add
from typing import List, TypedDict
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage

class BaseTeamState(TypedDict):
    messages: Annotated[List[BaseMessage], add]
    validated: bool
    next: str
    Error: str