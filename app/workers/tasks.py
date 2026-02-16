import json

from app.repositories.rate_limit.rate_limit_repository import RateLimitRepository
from app.repositories.redis import redis_client


from app.db.session import AsyncSessionLocal

class RateLimitRuleUpdater:
    def __init__(self):
        pass

    async def update_rules(self):
        async with AsyncSessionLocal() as db:
            repo = RateLimitRepository(db)

            active_rules = await self.fetch_rules_from_db(repo)
            await self.update_redis(active_rules)

    async def fetch_rules_from_db(self, repo) -> dict:
        rules = await repo.get_active_rules()
        return {
            rule.path: {
                "limit": rule.limit,
                "window": rule.window_seconds,
                "algorithm": rule.algorithm,
                "key_type": rule.key_type,
                "method": rule.method,
            }
            for rule in rules
        }

    @staticmethod
    async def update_redis(rules: dict, key: str = "rate_limit_rules_v1"):
        await redis_client.set(key, json.dumps(rules))
        print(f"Updated {len(rules)} rules in Redis")
