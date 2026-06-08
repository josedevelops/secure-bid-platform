# config.py — application settings loaded from environment variables
# pydantic-settings reads from .env automatically via model_config
# we use ConfigDict instead of the old class Config style — pydantic v2 requirement
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Secure Bid Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # model_config replaces the old nested class Config style
    # same settings — env_file, case sensitivity, ignore unknown vars
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
