import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.repositories.redis import redis_client
from app.services.rate_limit.rate_limiter import RateLimiterService
from app.core.entities import RequestInfo
from app.utils.logger import logger
from app.core.config import settings

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, rate_limiter_service: RateLimiterService):
        super().__init__(app)
        self.rate_limiter = rate_limiter_service
        self.endpoint_limits = {
            "/api/v1/posts": (3, 10),      # 2/10 soniya
            "/api/v1/login": (5, 15),      # 5/15 soniya
        }


    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        user_id = request.headers.get("X-User-ID")
        endpoint = request.url.path

        request_info = RequestInfo(
            client_ip=client_ip,
            user_id=user_id,
            endpoint=endpoint,
            method=request.method
        )

        factory_data =  await redis_client.get(settings.rate_limiter_endpoint_key)
        if factory_data:
            factory_endpoints = json.loads(factory_data)
        else:
            factory_endpoints = self.endpoint_limits
        custom_limit, custom_window = factory_endpoints.get(endpoint, (None, None))

        allowed, retry_after = await self.rate_limiter.is_allowed(
            request_info, custom_limit, custom_window
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