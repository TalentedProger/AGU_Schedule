"""
Application configuration using Pydantic Settings.

Loads environment variables from .env file and provides type-safe access.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # === Telegram Bot ===
    BOT_TOKEN: str
    ADMIN_TG_ID: int
    
    # === Database ===
    DATABASE_PATH: str = "data/schedule.db"
    
    # === Admin Panel ===
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    ADMIN_HOST: str = "127.0.0.1"
    ADMIN_PORT: int = 8000
    SECRET_KEY: str  # For session encryption
    
    # === Scheduler ===
    TIMEZONE: str = "Europe/Moscow"
    MORNING_MESSAGE_HOUR: int = 8
    MORNING_MESSAGE_MINUTE: int = 0
    REMINDER_MINUTES_BEFORE: int = 5
    
    # === Delivery ===
    BATCH_SIZE: int = 30
    BATCH_DELAY: float = 0.2  # seconds between batches
    MAX_RETRIES: int = 1
    
    # === Logging ===
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    
    # === Web Server ===
    WEB_HOST: str = "127.0.0.1"
    WEB_PORT: int = 8000
    
    # === Development ===
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
