from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = 'sqlite+aiosqlite:///./prediction_market_tracker.db'
    NEWS_API_PROVIDER: str = 'newsapi'
    NEWS_API_KEY: str = ''
    KALSHI_API_KEY_ID: str = ''
    KALSHI_PRIVATE_KEY_PATH: str = ''
    ANOMALY_THRESHOLD: float = 3.0
    MIN_TRADER_BETS: int = 5
    MIN_MARKET_PARTICIPANTS: int = 3
    NLP_BACKEND: str = 'huggingface'  # 'huggingface' or 'vader'
    MODELS_CACHE_DIR: str = './models_cache'
    USE_FAKE_REDIS: bool = True
    REDIS_URL: str = 'redis://localhost:6379/0'
    HOST: str = '0.0.0.0'
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file='../../.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
