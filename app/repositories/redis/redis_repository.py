from typing import Tuple
from redis.asyncio import Redis
from app.core.interfaces import RateLimitRepository
from app.repositories.redis.redis_client import redis_client


class RedisRateLimitRepository(RateLimitRepository):
    def __init__(self, redis: Redis = redis_client):
        self.redis = redis
        self._init_scripts()

    def _init_scripts(self):
        self.fixed_window_script = self.redis.register_script("""
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
    
            local current = redis.call('INCR', key)
    
            if current == 1 then
                redis.call('EXPIRE', key, window)
            end
    
            local ttl = redis.call('TTL', key)
    
            return {current, ttl}
        """)

        self.sliding_window_script = self.redis.register_script("""
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
    
            local now = redis.call('TIME')[1]
    
            -- eski yozuvlarni tozalash
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
    
            local count = redis.call('ZCARD', key)
    
            if count < limit then
                local counter_key = key .. ':counter'
                local unique = redis.call('INCR', counter_key)
                local member = now .. '-' .. unique
    
                redis.call('ZADD', key, now, member)
                redis.call('EXPIRE', key, window)
                redis.call('EXPIRE', counter_key, window)
    
                return {count + 1, 0}
            else
                local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
                local ttl = math.ceil(window - (now - tonumber(oldest[2])))
                return {count, ttl}
            end
        """)

        self.token_bucket_script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])
    
            local now = redis.call('TIME')[1]
    
            local tokens_key = key .. ':tokens'
            local ts_key = key .. ':ts'
    
            local tokens = tonumber(redis.call('GET', tokens_key) or capacity)
            local last_refill = tonumber(redis.call('GET', ts_key) or now)
    
            local delta = math.max(0, now - last_refill)
            local refill = delta * refill_rate
            tokens = math.min(capacity, tokens + refill)
    
            local allowed = 0
            local wait_time = 0
    
            if tokens >= 1 then
                tokens = tokens - 1
                allowed = 1
            else
                wait_time = math.ceil((1 - tokens) / refill_rate)
            end
    
            local ttl = math.ceil(capacity / refill_rate * 2)
    
            redis.call('SETEX', tokens_key, ttl, tokens)
            redis.call('SETEX', ts_key, ttl, now)
    
            return {allowed, wait_time}
        """)

        self.leaky_bucket_script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local leak_rate = tonumber(ARGV[2])
    
            local now = redis.call('TIME')[1]
    
            local tokens_key = key .. ':tokens'
            local last_leak_key = key .. ':last_leak'
    
            local tokens = tonumber(redis.call('GET', tokens_key) or 0)
            local last_leak = tonumber(redis.call('GET', last_leak_key) or now)
    
            local delta = math.max(0, now - last_leak)
            tokens = math.max(0, tokens - delta * leak_rate)
    
            local allowed = 0
            local wait_time = 0
    
            if tokens < capacity then
                tokens = tokens + 1
                allowed = 1
            else
                wait_time = math.ceil((tokens - capacity + 1) / leak_rate)
            end
    
            local ttl = math.ceil(capacity / leak_rate * 2)
    
            redis.call('SETEX', tokens_key, ttl, tokens)
            redis.call('SETEX', last_leak_key, ttl, now)
    
            return {allowed, wait_time}
        """)

    async def increment_and_check(
            self, key: str, limit: int, window: int
    ) -> Tuple[int, int]:
        """
        Fixed window
        returns: (current_count, ttl)
        """
        result = await self.fixed_window_script(
            keys=[key],
            args=[limit, window],
        )
        return int(result[0]), int(result[1])

    async def sliding_window_log(
            self, key: str, limit: int, window: int
    ) -> Tuple[int, int]:
        """
        returns: (current_count, retry_after)
        """
        result = await self.sliding_window_script(
            keys=[key],
            args=[limit, window],
        )
        return int(result[0]), int(result[1])

    async def token_bucket(
            self, key: str, capacity: int, refill_rate: float
    ) -> Tuple[int, float]:
        """
        returns: (allowed, retry_after)
        """
        result = await self.token_bucket_script(
            keys=[key],
            args=[capacity, refill_rate],
        )
        return int(result[0]), float(result[1])

    async def leaky_bucket(
            self, key: str, capacity: int, leak_rate: float
    ) -> Tuple[int, float]:
        """
        returns: (allowed, retry_after)
        """
        result = await self.leaky_bucket_script(
            keys=[key],
            args=[capacity, leak_rate],
        )
        return int(result[0]), float(result[1])
