"""
config.py - Application Configuration

Loads environment variables using pydantic-settings and provides
a centralized configuration object for the entire application.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL: PostgreSQL connection string.
        SECRET_KEY: Secret key used for JWT token signing.
        ALGORITHM: Algorithm used for JWT encoding (default: HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes.
        APP_NAME: Display name of the application.
        APP_VERSION: Current application version.
        DEBUG: Enable/disable debug mode.
    """

    DATABASE_URL: str = "postgresql://postgres:0000@localhost:5432/fitness_tracker"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "Fitness Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the application settings.
    Uses lru_cache to avoid re-reading .env on every call.
    """
    return Settings()
