"""
Application configuration.

Loads environment variables from the .env file.
"""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load variables from .env
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "AI Code Review Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"

    # GitHub
    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPOSITORY: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()


settings = get_settings()