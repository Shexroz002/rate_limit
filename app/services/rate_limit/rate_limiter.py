from typing import Optional
from app.core.config import settings
from app.core.entities import RequestInfo, EndpointRateLimitConfig
from app.services.rate_limit.factory import AlgorithmFactory
from app.repositories.redis import RedisRateLimitRepository


class RateLimiterService:
    def __init__(self, repo: RedisRateLimitRepository):
        self.repo = repo

    async def is_allowed(
            self,
            request_info: RequestInfo,
            endpoint_config: Optional[EndpointRateLimitConfig] = None
    ) -> tuple[bool, int]:

        if endpoint_config:
            limit = endpoint_config.limit
            window = endpoint_config.window
            algorithm_name = endpoint_config.algorithm
            key_type = endpoint_config.key_type
        else:
            limit = settings.default_rate_limit
            window = settings.default_rate_limit_window
            algorithm_name = settings.rate_limit_algorithm
            key_type = "ip"

        if key_type == "user" and request_info.user_id:
            identifier = request_info.user_id
            key = f"rate_limit:user:{identifier}:{request_info.endpoint}:{request_info.method}"
        else:
            identifier = request_info.client_ip
            key = f"rate_limit:ip:{identifier}:{request_info.endpoint}:{request_info.method}"

        algorithm = AlgorithmFactory.create(algorithm_name, self.repo)
        return await algorithm.check(key, limit, window)
