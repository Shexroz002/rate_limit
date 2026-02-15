from fastapi import FastAPI

from app.api.router import api_router
from app.core.lifespan import lifespan
from app.core.middleware.rate_limit import RateLimiterMiddleware

from app.core.config import settings
from app.core.middleware.dependencies import get_rate_limiter_service
from app.utils.logger import setup_logging

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )


    # Middleware
    rate_limiter_service = get_rate_limiter_service()
    app.add_middleware(RateLimiterMiddleware, rate_limiter_service=rate_limiter_service)

    # Routelar
    app.include_router(api_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()