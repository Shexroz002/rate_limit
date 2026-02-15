import time
from typing import Tuple
from redis.asyncio import Redis
from app.core.interfaces import RateLimitRepository
from app.repositories.redis.redis_client import redis_client


class RedisRateLimitRepository(RateLimitRepository):
    def __init__(self, redis: Redis = redis_client):
        self.redis = redis
        self._init_scripts()

    def _init_scripts(self):
        # Fixed Window Lua skripti
        self.fixed_window_script = self.redis.register_script("""
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            local current = redis.call('GET', key)
            if current then
                current = tonumber(current)
                if current >= limit then
                    local ttl = redis.call('TTL', key)
                    return {current, ttl}
                else
                    redis.call('INCR', key)
                    return {current+1, ttl}
                end
            else
                redis.call('SETEX', key, window, 1)
                return {1, window}
            end
        """)

        # Sliding Window Log Lua skripti (Sorted Set)
        self.sliding_window_script = self.redis.register_script("""
            local key = KEYS[1]
            local limit = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])
            -- eski elementlarni tozalash
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
            local count = redis.call('ZCARD', key)
            if count < limit then
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window)
                return {count+1, window}
            else
                local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
                local ttl = math.ceil(window - (now - tonumber(oldest[2])))
                return {count, ttl}
            end
        """)

        # Token Bucket Lua skripti
        self.token_bucket_script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local refill_rate = tonumber(ARGV[2])  -- token/sek
            local now = tonumber(ARGV[3])
            local tokens_key = key .. ':tokens'
            local ts_key = key .. ':ts'
            local tokens = redis.call('GET', tokens_key)
            local last_refill = redis.call('GET', ts_key)
            if not tokens then
                tokens = capacity
                last_refill = now
            else
                tokens = tonumber(tokens)
                last_refill = tonumber(last_refill)
                local delta = now - last_refill
                tokens = math.min(capacity, tokens + delta * refill_rate)
                last_refill = now
            end
            if tokens >= 1 then
                tokens = tokens - 1
                redis.call('SETEX', tokens_key, 3600, tokens)  -- TTL uzoqroq
                redis.call('SETEX', ts_key, 3600, last_refill)
                return {tokens, 0}
            else
                local wait_time = (1 - tokens) / refill_rate
                return {0, wait_time}
            end
        """)

        self.leaky_bucket_script = self.redis.register_script("""
            local key = KEYS[1]
            local capacity = tonumber(ARGV[1])
            local leak_rate = tonumber(ARGV[2])  -- token/sek
            local now = tonumber(ARGV[3])
            local tokens_key = key .. ':tokens'
            local last_leak_key = key .. ':last_leak'
            local tokens = redis.call('GET', tokens_key)
            local last_leak = redis.call('GET', last_leak_key)
            if not tokens then
                tokens = 0
                last_leak = now
            else
                tokens = tonumber(tokens)
                last_leak = tonumber(last_leak)
                local delta = now - last_leak
                tokens = math.max(0, tokens - delta * leak_rate)
                last_leak = now
            end
            if tokens < capacity then
                tokens = tokens + 1
                redis.call('SETEX', tokens_key, 3600, tokens)  -- TTL uzoqroq
                redis.call('SETEX', last_leak_key, 3600, last_leak)
                return {tokens, 0}
            else
                local wait_time = (tokens - capacity + 1) / leak_rate
                return {capacity, wait_time}
            end
        """)

    async def increment_and_check(self, key: str, limit: int, window: int) -> Tuple[int, int]:
        now = int(time.time())
        result = await self.fixed_window_script(keys=[key], args=[limit, window, now])
        return result[0], result[1]

    async def sliding_window_log(self, key: str, limit: int, window: int) -> Tuple[int, int]:
        now = int(time.time())
        result = await self.sliding_window_script(keys=[key], args=[limit, window, now])
        return result[0], result[1]

    async def token_bucket(self, key: str, capacity: int, refill_rate: float) -> Tuple[int, float]:
        now = int(time.time())
        result = await self.token_bucket_script(keys=[key], args=[capacity, refill_rate, now])
        return int(result[0]), float(result[1])

    async def leaky_bucket(self, key: str, capacity: int, leak_rate: float) -> Tuple[int, float]:
        now = int(time.time())
        result = await self.leaky_bucket_script(keys=[key], args=[capacity, leak_rate, now])
        return int(result[0]), float(result[1])

