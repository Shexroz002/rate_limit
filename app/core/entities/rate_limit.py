from dataclasses import dataclass
from typing import Optional
from pydantic import BaseModel
from typing import Literal


@dataclass
class RateLimitRule:
    limit: int
    window: int
    algorithm: str
    key_type: str     # "ip" yoki "user"
    method: str

@dataclass
class RequestInfo:
    client_ip: str
    user_id: Optional[str] = None
    endpoint: str = "/"
    method: str = "GET"


class EndpointRateLimitConfig(BaseModel):
    limit: int
    window: int
    algorithm: Literal[
        "fixed_window",
        "sliding_window_log",
        "token_bucket",
        "leaky_bucket"
    ]
    key_type: Literal["ip", "user"]
    method: str
