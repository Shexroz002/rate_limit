from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, RedisDsn

class Settings(BaseSettings):
    # FastAPI
    app_name: str = "Rate Limiter Service"
    debug: bool = False
    environment: str = "production"

    # Redis
    redis_dsn: RedisDsn = Field("redis://localhost:6379/0", env="REDIS_DSN")
    redis_pool_size: int = 20

    # Rate Limiting
    rate_limit_algorithm: str = "fixed_window"  # fixed_window, sliding_window_log, token_bucket
    default_rate_limit: int = 100               # So‘rovlar soni
    default_rate_limit_window: int = 60         # soniyalarda

    # Logging
    log_level: str = "INFO"
    json_logs: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    rate_limiter_endpoint_key: str = "rate_limiter:endpoints"

    DATABASE_URL: str ="postgresql+asyncpg://rate_limiter_user:rate_limiter1234@rate-limiter-db:5432/rate_limiter_db"

settings = Settings()