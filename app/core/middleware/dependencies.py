from app.repositories.redis import RedisRateLimitRepository
from app.services.rate_limit.rate_limiter import RateLimiterService


def get_rate_limiter_repo() -> RedisRateLimitRepository:
    return RedisRateLimitRepository()


def get_rate_limiter_service() -> RateLimiterService:
    repo = get_rate_limiter_repo()
    return RateLimiterService(repo)
