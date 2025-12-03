"""
Morning schedule delivery job.

Sends daily schedule to all active users at 08:00 MSK.
"""

from aiogram import Bot
from datetime import datetime

from app.db import get_connection
from app.db.queries import get_active_users, get_pairs_by_direction_and_day
from app.bot.utils import format_schedule_message
from app.scheduler.utils import send_message_with_retry, log_delivery
from app.utils.logger import logger


async def morning_schedule_job(bot: Bot):
    """
    Send morning schedule to all active users.
    
    Fetches all active (not paused) users and sends them today's schedule.
    """
    logger.info("Starting morning schedule delivery...")
    
    conn = await get_connection()
    
    try:
        # Get all active users
        users = await get_active_users(conn)
        logger.info(f"Found {len(users)} active users")
        
        if not users:
            logger.info("No active users to send schedule to")
            return
        
        # Get current day of week (0=Monday)
        today = datetime.now().weekday()
        
        successful = 0
        errors = 0
        
        # Send to each user
        for user in users:
            try:
                # Get user's schedule for today
                pairs = await get_pairs_by_direction_and_day(
                    conn, user.direction_id, today
                )
                
                # Format message
                message = format_schedule_message(pairs, today, user.name)
                
                # Send message
                sent = await send_message_with_retry(bot, user.tg_id, message)
                
                # Log delivery
                if sent:
                    await log_delivery(conn, user.tg_id, 'morning', 'sent')
                    successful += 1
                else:
                    await log_delivery(
                        conn, user.tg_id, 'morning', 'error',
                        'Failed after retries'
                    )
                    errors += 1
            
            except Exception as e:
                logger.error(f"Error sending to user {user.tg_id}: {e}", exc_info=True)
                await log_delivery(
                    conn, user.tg_id, 'morning', 'error', str(e)
                )
                errors += 1
        
        logger.info(
            f"Morning schedule delivery completed: "
            f"{successful} sent, {errors} errors"
        )
    
    except Exception as e:
        logger.error(f"Morning schedule job failed: {e}", exc_info=True)
    
    finally:
        await conn.close()
