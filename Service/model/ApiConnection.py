from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class ApiConnection:
    id: int
    name: str
    endpoint_url: str
    auth_type: str
    api_key: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    headers: Optional[Dict] = None
    rate_limit: Optional[Dict] = None
    timeout: Optional[Dict] = None
    api_version: Optional[str] = None