"""
Application configuration using Pydantic Settings.

Loads environment variables from .env file and provides type-safe access.
Supports both local development and cloud deployment (Railway, Render).
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # === Telegram Bot ===
    BOT_TOKEN: str
    ADMIN_TG_ID: int
    
    # === Database ===
    # SQLite for local, PostgreSQL URL for cloud (auto-detected)
    DATABASE_PATH: str = "data/schedule.db"
    DATABASE_URL: Optional[str] = None  # Set by Railway/Render
    
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
    
    # === Cloud Deployment ===
    # These are auto-set by cloud platforms
    PORT: Optional[int] = None  # Railway/Render set this
    RAILWAY_ENVIRONMENT: Optional[str] = None
    RENDER: Optional[str] = None
    
    # === Development ===
    DEBUG: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars from cloud platforms
    )
    
    @property
    def is_cloud(self) -> bool:
        """Check if running in cloud environment."""
        return bool(self.DATABASE_URL or self.RAILWAY_ENVIRONMENT or self.RENDER)
    
    @property
    def effective_port(self) -> int:
        """Get the effective port to use."""
        return self.PORT or self.ADMIN_PORT


# Global settings instance
settings = Settings()
