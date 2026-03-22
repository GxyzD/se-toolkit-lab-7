"""Configuration loader for the Telegram bot.

Reads secrets from .env.bot.secret (gitignored) using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    """Bot configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram bot token (required for Telegram mode, not needed for --test)
    bot_token: str = ""

    # LMS API configuration
    lms_api_base_url: str = "http://localhost:42002"
    lms_api_key: str = ""

    # LLM API configuration (for Task 3)
    llm_api_key: str = ""
    llm_api_base_url: str = "http://localhost:42005/v1"
    llm_api_model: str = "coder-model"


# Global config instance
config = BotConfig()
