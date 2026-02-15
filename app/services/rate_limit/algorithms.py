from abc import ABC, abstractmethod
from typing import Tuple
from app.core.interfaces import RateLimitRepository

class RateLimitAlgorithm(ABC):
    """Rate limiting algoritmlarining umumiy interfeysi"""
    @abstractmethod
    async def check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """(allowed, retry_after)"""
        pass

class FixedWindowAlgorithm(RateLimitAlgorithm):
    def __init__(self, repo: RateLimitRepository):
        self.repo = repo

    async def check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        count, ttl = await self.repo.increment_and_check(key, limit, window)
        if count > limit:
            return False, ttl
        return True, 0

class SlidingWindowLogAlgorithm(RateLimitAlgorithm):
    def __init__(self, repo: RateLimitRepository):
        self.repo = repo

    async def check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        count, ttl = await self.repo.sliding_window_log(key, limit, window)
        if count >= limit:
            return False, ttl
        return True, 0

class TokenBucketAlgorithm(RateLimitAlgorithm):
    def __init__(self, repo: RateLimitRepository):
        self.repo = repo

    async def check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        # limit = bucket capacity, window = refill rate (tokens per second)
        tokens, wait = await self.repo.token_bucket(key, limit, window)
        if tokens == 0:
            return False, int(wait) + 1  # Retry-After soniyalarda
        return True, 0

class LeakyBucketAlgorithm(RateLimitAlgorithm):
    def __init__(self, repo: RateLimitRepository):
        self.repo = repo

    async def check(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        # limit = bucket capacity, window = leak rate (tokens per second)
        tokens, wait = await self.repo.leaky_bucket(key, limit, window)
        if tokens >= limit:
            return False, int(wait) + 1  # Retry-After soniyalarda
        return True, 0