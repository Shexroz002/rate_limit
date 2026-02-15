from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings


pool = ConnectionPool.from_url(str(settings.redis_dsn), max_connections=settings.redis_pool_size)
redis_client = Redis.from_pool(pool)
