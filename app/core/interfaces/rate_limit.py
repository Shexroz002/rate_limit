from abc import ABC, abstractmethod


class RateLimitRepository(ABC):
    """Rate limiting algoritmlarini amalga oshirish uchun interfeys"""

    @abstractmethod
    async def increment_and_check(self, key: str, limit: int, window: int) -> tuple[int, int]:
        """(hozirgi count, qolgan TTL) qaytaradi, limit oshib ketgan bo'lsa -1 TTL"""
        pass

    @abstractmethod
    async def sliding_window_log(self, key: str, limit: int, window: int) -> tuple[int, int]:
        """(hozirgi windowdagi so'rovlar soni, eng eski timestamp TTL)"""
        pass

    @abstractmethod
    async def token_bucket(self, key: str, capacity: int, refill_rate: float) -> tuple[int, float]:
        """(qolgan tokenlar, keyingi refillgacha soniya)"""
        pass

    @abstractmethod
    async def leaky_bucket(self, key: str, capacity: int, leak_rate: float) -> tuple[int, float]:
        """(qolgan tokenlar, keyingi leakgacha soniya)"""
        pass
