
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.base import get_db
from app.repositories.rate_limit.rate_limit_repository import RateLimitRepository


async def get_rate_limit_repo(
    db: AsyncSession = Depends(get_db),
):
    return RateLimitRepository(db)