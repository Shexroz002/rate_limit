from abc import ABC, abstractmethod


class RateLimitRepository(ABC):
    """
    Rate limiting uchun repository interfeysi. Turli algoritmlar uchun metodlar mavjud:
        - increment_and_check: oddiy counter algoritmi uchun
        - sliding_window_log: sliding window algoritmi uchun
        - token_bucket: token bucket algoritmi uchun
        - leaky_bucket: leaky bucket algoritmi uchun
    # Har bir metod o'ziga xos parametrlar va qaytish qiymatlari bilan ishlaydi, bu esa algoritmlarning talablariga mos keladi.
    Bu nega kerak? Chunki biz turli algoritmlar uchun yagona interfeys yaratmoqchimiz,
    shunda ularni osongina almashtirish va test qilish mumkin bo'ladi.
    Har bir algoritm o'zining maxsus logikasini amalga oshiradi,
    lekin ular barchasi shu interfeys orqali chaqiriladi, bu esa kodning modularligini va qayta foydalanilishini oshiradi.
    """

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
