import json

from app.repositories.redis import redis_client


class RateLimitRuleUpdater:
    def __init__(self, repo):
        self.repo = repo

    async def update_rules(self):
        active_rules = await self.fetch_rules_from_db()
        await self.update_redis(active_rules)

    async def fetch_rules_from_db(self) -> dict:
        rules = await self.repo.get_active_rules()
        return {
            rule.path: {
                "limit": rule.limit,
                "window": rule.window,
                "algorithm": rule.algorithm,
                "key_type": rule.key_type,
                "method": rule.method
            }
            for rule in rules
        }

    @staticmethod
    async def update_redis(rules: dict, key: str = "rate_limit_rules_v1"):
        await redis_client.set(key, json.dumps(rules))
        print(f"Updated {len(rules)} rules in Redis")