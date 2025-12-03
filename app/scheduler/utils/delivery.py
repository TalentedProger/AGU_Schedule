"""
Batch delivery utility.

Sends messages in batches with rate limiting to avoid Telegram limits.
"""

import asyncio
from typing import List, Callable, Any
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from app.config import settings
from app.utils.logger import logger


async def batch_send(
    bot: Bot,
    user_ids: List[int],
    message_func: Callable[[Bot, int], Any],
    batch_size: int = None,
    delay: float = None
) -> tuple[int, int]:
    """
    Send messages in batches with rate limiting.
    
    Args:
        bot: Bot instance
        user_ids: List of user Telegram IDs
        message_func: Async function(bot, user_id) that sends message
        batch_size: Messages per batch (default from config)
        delay: Delay between batches in seconds (default from config)
    
    Returns:
        Tuple of (successful_count, error_count)
    """
    if batch_size is None:
        batch_size = settings.BATCH_SIZE
    
    if delay is None:
        delay = settings.BATCH_DELAY
    
    successful = 0
    errors = 0
    
    # Process in batches
    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        
        # Send messages concurrently within batch
        tasks = [message_func(bot, user_id) for user_id in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count results
        for result in results:
            if isinstance(result, Exception):
                errors += 1
            else:
                successful += 1
        
        # Delay between batches (except last)
        if i + batch_size < len(user_ids):
            await asyncio.sleep(delay)
    
    logger.info(f"Batch send completed: {successful} sent, {errors} errors")
    return successful, errors


async def send_message_with_retry(
    bot: Bot,
    user_id: int,
    text: str,
    parse_mode: str = "HTML",
    max_retries: int = None
) -> bool:
    """
    Send message with retry on failure.
    
    Args:
        bot: Bot instance
        user_id: User Telegram ID
        text: Message text
        parse_mode: Parse mode (HTML, Markdown)
        max_retries: Maximum retry attempts (default from config)
    
    Returns:
        True if sent successfully, False otherwise
    """
    if max_retries is None:
        max_retries = settings.MAX_RETRIES
    
    for attempt in range(max_retries + 1):
        try:
            await bot.send_message(
                chat_id=user_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        
        except TelegramAPIError as e:
            logger.warning(f"Failed to send to {user_id} (attempt {attempt + 1}): {e}")
            
            if attempt < max_retries:
                await asyncio.sleep(1)  # Wait before retry
            else:
                logger.error(f"All retry attempts failed for user {user_id}")
                return False
        
        except Exception as e:
            logger.error(f"Unexpected error sending to {user_id}: {e}", exc_info=True)
            return False
    
    return False
