import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.repositories.redis import redis_client
from app.services.rate_limit.rate_limiter import RateLimiterService
from app.core.entities import RequestInfo, EndpointRateLimitConfig
from app.utils.logger import logger
from app.core.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, rate_limiter_service: RateLimiterService):
        super().__init__(app)
        self.rate_limiter = rate_limiter_service
        self.endpoint_limits = {
            "/api/v1/posts": (3, 10),  # 2/10 soniya
            "/api/v1/login": (5, 15),  # 5/15 soniya
        }

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        user_id = request.headers.get("X-User-ID")
        endpoint = request.url.path
        method = request.method

        request_info = RequestInfo(
            client_ip=client_ip,
            user_id=user_id,
            endpoint=endpoint,
            method=method
        )

        factory_data = await redis_client.get("rate_limit_rules_v1")
        if factory_data:
            raw_config = json.loads(factory_data) or {}
        else:
            raw_config = self.endpoint_limits
        endpoint_config = raw_config.get(endpoint)
        parsed_config = None
        if endpoint_config and endpoint_config.get("method") == method:
            parsed_config = EndpointRateLimitConfig(**endpoint_config)


        allowed, retry_after = await self.rate_limiter.is_allowed(
            request_info=request_info,
            endpoint_config=parsed_config
        )

        if not allowed:
            logger.warning("Rate limit exceeded",
                           extra={"client_ip": client_ip, "user_id": user_id, "endpoint": endpoint})
            return Response(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                content="Rate limit exceeded. Try again later."
            )

        response = await call_next(request)
        return response
