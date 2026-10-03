import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Developer Webhook Relay & Replay Platform"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://relay_user:relay_password@localhost:5432/webhook_relay"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    
    # Retry worker config
    MAX_RETRIES: int = 5
    INITIAL_BACKOFF_SECONDS: int = 5
    MAX_BACKOFF_SECONDS: int = 405
    JITTER_MAX_SECONDS: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

