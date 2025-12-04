"""
Reminder jobs.

Sends 5-minute reminders before each class.
"""

from aiogram import Bot
from datetime import datetime, time, timedelta

from app.db import get_connection
from app.db.queries import get_active_users, get_pairs_by_direction_and_day
from app.bot.utils import format_reminder_message
from app.scheduler.utils import send_message_with_retry, log_delivery
from app.utils.logger import logger
from app.config import settings


async def reminder_job(bot: Bot, slot_number: int, start_time: str, end_time: str):
    """
    Send reminders for specific time slot.
    
    Args:
        bot: Bot instance
        slot_number: Time slot number (1-5)
        start_time: Slot start time (HH:MM)
        end_time: Slot end time (HH:MM)
    """
    logger.info(f"Starting reminder job for slot {slot_number} ({start_time})")
    
    conn = await get_connection()
    
    try:
        # Get all active users with reminders enabled
        all_users = await get_active_users(conn)
        users = [u for u in all_users if u.remind_before]
        
        logger.info(f"Found {len(users)} users with reminders enabled")
        
        if not users:
            logger.info("No users with reminders enabled")
            return
        
        # Get current day of week (0=Monday)
        today = datetime.now().weekday()
        logger.info(f"Today is weekday {today} (0=Monday)")
        
        successful = 0
        errors = 0
        skipped = 0
        
        # Send to each user
        for user in users:
            try:
                # Get user's schedule for today
                pairs = await get_pairs_by_direction_and_day(
                    conn, user.direction_id, today
                )
                
                logger.debug(
                    f"User {user.tg_id} (direction {user.direction_id}): "
                    f"found {len(pairs)} pairs for today"
                )
                
                # Find pair matching this time slot
                matching_pair = None
                for pair, pair_start, pair_end in pairs:
                    logger.debug(
                        f"Checking pair: {pair.title} at {pair_start} "
                        f"(looking for {start_time})"
                    )
                    if pair_start == start_time:
                        matching_pair = (pair, pair_start, pair_end)
                        break
                
                if not matching_pair:
                    # User doesn't have class at this slot
                    logger.debug(
                        f"User {user.tg_id} has no class at {start_time}, skipping"
                    )
                    skipped += 1
                    continue
                
                pair, pair_start, pair_end = matching_pair
                logger.info(
                    f"Sending reminder to user {user.tg_id} for {pair.title} "
                    f"at {pair_start}"
                )
                
                # Format reminder message
                message = format_reminder_message(pair, pair_start, pair_end)
                
                # Send message
                sent = await send_message_with_retry(bot, user.tg_id, message)
                
                # Log delivery
                if sent:
                    await log_delivery(conn, user.tg_id, 'reminder', 'sent')
                    successful += 1
                    logger.info(f"Successfully sent reminder to user {user.tg_id}")
                else:
                    await log_delivery(
                        conn, user.tg_id, 'reminder', 'error',
                        'Failed after retries'
                    )
                    errors += 1
                    logger.error(f"Failed to send reminder to user {user.tg_id}")
            
            except Exception as e:
                logger.error(f"Error sending reminder to user {user.tg_id}: {e}", exc_info=True)
                await log_delivery(
                    conn, user.tg_id, 'reminder', 'error', str(e)
                )
                errors += 1
        
        logger.info(
            f"Reminder job completed for slot {slot_number}: "
            f"{successful} sent, {errors} errors, {skipped} skipped (no class)"
        )
    
    except Exception as e:
        logger.error(f"Reminder job failed for slot {slot_number}: {e}", exc_info=True)
    
    finally:
        await conn.close()


def calculate_reminder_time(slot_start: str, minutes_before: int = 5) -> time:
    """
    Calculate reminder time (slot_start - minutes_before).
    
    Args:
        slot_start: Start time in HH:MM format
        minutes_before: Minutes before class to remind
    
    Returns:
        time object for reminder
    """
    # Parse start time
    hour, minute = map(int, slot_start.split(':'))
    slot_time = time(hour, minute)
    
    # Calculate reminder time
    slot_datetime = datetime.combine(datetime.today(), slot_time)
    reminder_datetime = slot_datetime - timedelta(minutes=minutes_before)
    
    return reminder_datetime.time()
