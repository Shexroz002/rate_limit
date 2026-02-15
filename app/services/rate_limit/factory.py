from app.services.rate_limit.algorithms import (
    FixedWindowAlgorithm,
    SlidingWindowLogAlgorithm,
    TokenBucketAlgorithm,
    LeakyBucketAlgorithm,
    RateLimitAlgorithm
)
from app.repositories.redis import RedisRateLimitRepository


class AlgorithmFactory:
    """
        Factory class to create rate limiting algorithm instances based on configuration.
        That way we can easily switch between different algorithms without changing
        the core logic of the rate limiter service.
    """

    @staticmethod
    def create(algorithm_name: str, repo: RedisRateLimitRepository) -> RateLimitAlgorithm:
        if algorithm_name == "fixed_window":
            return FixedWindowAlgorithm(repo)
        elif algorithm_name == "sliding_window_log":
            return SlidingWindowLogAlgorithm(repo)
        elif algorithm_name == "token_bucket":
            return TokenBucketAlgorithm(repo)
        elif algorithm_name == "leaky_bucket":
            return LeakyBucketAlgorithm(repo)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm_name}")
