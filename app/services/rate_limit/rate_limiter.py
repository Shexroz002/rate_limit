from typing import Optional
from app.core.config import settings
from app.core.entities import RequestInfo
from app.services.rate_limit.factory import AlgorithmFactory
from app.repositories.redis import RedisRateLimitRepository


class RateLimiterService:
    """
        Core service that handles rate limiting logic. It uses the configured algorithm
        to check if a request is allowed based on the user's ID or IP address.
        The service can also accept custom limits and windows for specific endpoints.
    """

    def __init__(self, repo: RedisRateLimitRepository):
        self.repo = repo
        self.algorithm = AlgorithmFactory.create(settings.rate_limit_algorithm, repo)

    async def is_allowed(self, request_info: RequestInfo,
                         custom_limit: Optional[int] = None,
                         custom_window: Optional[int] = None) -> tuple[bool, int]:

        if request_info.user_id:
            key = f"rate_limit:user:{request_info.user_id}"
        else:
            key = f"rate_limit:ip:{request_info.client_ip}"

        limit = custom_limit or settings.default_rate_limit
        window = custom_window or settings.default_rate_limit_window
        return await self.algorithm.check(key, limit, window)
