"""
Delivery logging utility.

Records message delivery status to database.
"""

import aiosqlite
from datetime import datetime

from app.utils.logger import logger


async def log_delivery(
    conn: aiosqlite.Connection,
    user_id: int,
    message_type: str,
    status: str,
    error_message: str = None
):
    """
    Log message delivery to database.
    
    Args:
        conn: Database connection
        user_id: User Telegram ID
        message_type: 'morning', 'reminder', 'broadcast'
        status: 'sent' or 'error'
        error_message: Error details if failed
    """
    try:
        await conn.execute(
            """
            INSERT INTO delivery_log (user_id, message_type, status, error_message)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, message_type, status, error_message)
        )
        await conn.commit()
    except Exception as e:
        logger.error(f"Failed to log delivery: {e}")
