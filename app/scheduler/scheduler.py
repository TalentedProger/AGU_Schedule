"""
APScheduler initialization and job scheduling.

Sets up scheduler with cron jobs for morning messages and reminders.
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot

from app.config import settings
from app.scheduler.jobs import morning_schedule_job, reminder_job, calculate_reminder_time
from app.db import get_connection
from app.utils.logger import logger


async def get_time_slots():
    """Fetch time slots from database."""
    conn = await get_connection()
    try:
        async with conn.execute(
            "SELECT slot_number, start_time, end_time FROM time_slots ORDER BY slot_number"
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    finally:
        await conn.close()


async def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    """
    Initialize and configure APScheduler.
    
    Args:
        bot: Bot instance to pass to jobs
    
    Returns:
        Configured AsyncIOScheduler instance
    """
    logger.info("Initializing scheduler...")
    
    # Create scheduler with MSK timezone
    scheduler = AsyncIOScheduler(timezone=settings.TIMEZONE)
    
    # Add morning schedule job (08:00 MSK daily)
    scheduler.add_job(
        morning_schedule_job,
        CronTrigger(
            hour=settings.MORNING_MESSAGE_HOUR,
            minute=settings.MORNING_MESSAGE_MINUTE,
            timezone=settings.TIMEZONE
        ),
        args=[bot],
        id='morning_schedule',
        name='Morning Schedule Delivery',
        replace_existing=True
    )
    
    logger.info(
        f"Scheduled morning job at {settings.MORNING_MESSAGE_HOUR}:"
        f"{settings.MORNING_MESSAGE_MINUTE:02d} {settings.TIMEZONE}"
    )
    
    # Add reminder jobs for each time slot
    time_slots = await get_time_slots()
    
    for slot in time_slots:
        # Calculate reminder time (5 minutes before)
        reminder_time = calculate_reminder_time(
            slot['start_time'],
            settings.REMINDER_MINUTES_BEFORE
        )
        
        scheduler.add_job(
            reminder_job,
            CronTrigger(
                hour=reminder_time.hour,
                minute=reminder_time.minute,
                timezone=settings.TIMEZONE
            ),
            args=[bot, slot['slot_number'], slot['start_time'], slot['end_time']],
            id=f"reminder_slot_{slot['slot_number']}",
            name=f"Reminder for slot {slot['slot_number']} ({slot['start_time']})",
            replace_existing=True
        )
        
        logger.info(
            f"Scheduled reminder for slot {slot['slot_number']} at "
            f"{reminder_time.hour}:{reminder_time.minute:02d} {settings.TIMEZONE}"
        )
    
    logger.info(f"Scheduler configured with {len(scheduler.get_jobs())} jobs")
    
    return scheduler
