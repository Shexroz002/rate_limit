import enum


class RateLimitAlgorithmOption(str, enum.Enum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    SLIDING_LOG = "sliding_log"
    TOKEN_BUCKET = "token_bucket"


class RateLimitKeyOption(str, enum.Enum):
    IP = "ip"
    USER = "user"
    API_KEY = "api_key"
    GLOBAL = "global"
