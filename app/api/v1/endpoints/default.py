import json
from typing import List

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.repositories.redis import redis_client
from app.schemas.rate_limit.rate_limit_create import RateLimitBase

default_router = APIRouter(prefix="/api/v1")

@default_router.get("/posts")
async def get_posts():
    return {"message": "Posts list"}

@default_router.post("/posts")
async def create_posts():
    return {"message": "Create a new post"}

@default_router.get("/users")
async def get_users():
    return {"message": "Users list"}

@default_router.post("/login")
async def login():
    return {"message": "Login endpoint"}

@default_router.get("/rate-limited-endpoint")
async def rate_limited_endpoint():
    data = await redis_client.get("rate_limit_rules_v1")
    if data:
        # Redisda saqlangan JSON stringni dict ga o'zgartirish
        factory_endpoints = json.loads(data)
    else:
        factory_endpoints = {}
    return {
        "message": "This endpoint is rate limited",
        "current_limits": factory_endpoints
    }

# Rate-limitlarni yangilash
@default_router.post("/update-rate-limits")
async def update_rate_limits(new_limits: List[RateLimitBase]):
    # List[RateLimitBase] -> dict format: {endpoint: (limit, window)}
    converted_limits = {limit.endpoint: (limit.limit, limit.window) for limit in new_limits}

    # Redisga saqlash uchun JSON stringga o'zgartirish
    await redis_client.set(
        settings.rate_limiter_endpoint_key,
        json.dumps(converted_limits)
    )
    return {
        "message": "Rate limits updated",
        "converted_limits": converted_limits
    }