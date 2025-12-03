"""
Logging configuration for the application.

Sets up rotating file handler and console output.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import settings


def setup_logging():
    """
    Configure application logging with file and console handlers.
    
    - File handler: Rotating log file (max 10MB, 5 backups)
    - Console handler: Stdout with colored output (if available)
    """
    # Ensure logs directory exists
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        settings.LOG_FILE_PATH,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Silence noisy loggers in production
    if not settings.DEBUG:
        logging.getLogger('aiogram').setLevel(logging.WARNING)
        logging.getLogger('aiosqlite').setLevel(logging.WARNING)
        logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized (level: {settings.LOG_LEVEL})")
    
    return logger


# Initialize logger
logger = setup_logging()
