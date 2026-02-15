from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Enum,

)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base.base_model import BaseModel
from app.db.models.enum.rate_limit import RateLimitAlgorithmOption, RateLimitKeyOption


class RateLimitRule(BaseModel):
    __tablename__ = "rate_limit_rules"

    path: Mapped[str] = mapped_column(String(255), index=True)
    method: Mapped[str | None] = mapped_column(String(10), nullable=True)

    algorithm: Mapped[RateLimitAlgorithmOption] = mapped_column(
        Enum(RateLimitAlgorithmOption),
        nullable=False,
    )

    limit: Mapped[int] = mapped_column(Integer, nullable=False)
    window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)

    key_type: Mapped[RateLimitKeyOption] = mapped_column(
        Enum(RateLimitKeyOption),
        default=RateLimitKeyOption.IP,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)

    class Config:
        orm_mode = True
