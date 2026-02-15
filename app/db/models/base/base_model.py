from sqlalchemy import (
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.base import Base


class IDMixin:
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

class BaseModel(Base, IDMixin, TimestampMixin):
    __abstract__ = True
