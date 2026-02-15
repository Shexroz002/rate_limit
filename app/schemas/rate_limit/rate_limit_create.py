import re
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from app.db.models.rate_limit import (
    RateLimitAlgorithmOption,
    RateLimitKeyOption,
)

HTTP_METHODS = {
    "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"
}


class RateLimitBase(BaseModel):
    path: str = Field(..., max_length=255)
    method: Optional[str] = None

    algorithm: RateLimitAlgorithmOption

    limit: int
    window_seconds: int

    key_type: RateLimitKeyOption = RateLimitKeyOption.IP
    is_active: bool = True
    priority: int = 0

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str):
        if not v.startswith("/"):
            raise ValueError("Path must start with '/'")

        pattern = r"^\/[a-zA-Z0-9\/\-\{\}_]*$"
        if not re.match(pattern, v):
            raise ValueError("Invalid path format")

        return v

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: Optional[str]):
        if v is not None and v.upper() not in HTTP_METHODS:
            raise ValueError(f"Invalid HTTP method: {v}")
        return v.upper() if v else None

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int):
        if v <= 0:
            raise ValueError("Limit must be a positive integer")
        return v

    @model_validator(mode="after")
    def validate_algorithm_logic(self):

        if (
                self.algorithm == RateLimitAlgorithmOption.SLIDING_LOG
                and self.window_seconds > 3600
        ):
            raise ValueError(
                "Sliding log window_seconds cannot exceed 1 hour"
            )

        if (
                self.algorithm == RateLimitAlgorithmOption.TOKEN_BUCKET
                and self.limit < 2
        ):
            raise ValueError(
                "Token bucket requires limit >= 2"
            )

        if (
                self.algorithm == RateLimitAlgorithmOption.FIXED_WINDOW
                and self.window_seconds < 60
        ):
            raise ValueError(
                "Fixed window should have window_seconds >= 60"
            )

        return self


class RateLimitCreate(RateLimitBase):
    pass


class RateLimitUpdate(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    algorithm: Optional[RateLimitAlgorithmOption] = None
    limit: Optional[int] = None
    window_seconds: Optional[int] = None
    key_type: Optional[RateLimitKeyOption] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class RateLimitRead(RateLimitBase):
    id: int

    class Config:
        from_attributes = True
