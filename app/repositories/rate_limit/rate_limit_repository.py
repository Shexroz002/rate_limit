from typing import List, Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.db.models.rate_limit import RateLimitRule
from app.schemas.rate_limit import (
    RateLimitCreate,
    RateLimitUpdate,
)


class RateLimitRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: RateLimitCreate) -> RateLimitRule:
        rule = RateLimitRule(**data.model_dump())

        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)

        return rule

    async def get(self, rule_id: int) -> RateLimitRule | None:
        result = await self.db.execute(
            select(RateLimitRule).where(RateLimitRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_active_rules(self) -> Sequence[RateLimitRule]:
        result = await self.db.execute(
            select(RateLimitRule).where(RateLimitRule.is_active == True).order_by(RateLimitRule.priority.desc())
        )
        return result.scalars().all()

    async def update(self, rule: RateLimitRule, data: RateLimitUpdate) -> RateLimitRule:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(rule, key, value)

        await self.db.commit()
        await self.db.refresh(rule)

        return rule

    async def delete(self, rule: RateLimitRule) -> None:
        await self.db.delete(rule)
        await self.db.commit()

