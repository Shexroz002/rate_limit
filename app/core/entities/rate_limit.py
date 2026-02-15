from dataclasses import dataclass
from typing import Optional

@dataclass
class RateLimitRule:
    limit: int
    window: int       # seconiyalarda
    algorithm: str
    key_type: str     # "ip" yoki "user"
    method: str

@dataclass
class RequestInfo:
    client_ip: str
    user_id: Optional[str] = None
    endpoint: str = "/"
    method: str = "GET"