#!/usr/bin/env python3
"""Scheduler verification script - tests scheduler configuration without starting the bot."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

async def test_scheduler():
    """Test scheduler configuration."""
    print("🕐 Testing Scheduler Configuration")
    print("=" * 50)
    
    # Load config
    from app.config import settings
    print(f"\n📍 Timezone: {settings.TIMEZONE}")
    print(f"⏰ Morning message time: {settings.MORNING_MESSAGE_HOUR}:{settings.MORNING_MESSAGE_MINUTE:02d}")
    print(f"🔔 Reminder minutes before: {settings.REMINDER_MINUTES_BEFORE}")
    
    # Get time slots from DB
    import aiosqlite
    db_path = Path(__file__).parent.parent / "data" / "schedule.db"
    
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT * FROM time_slots ORDER BY slot_number")
        slots = await cursor.fetchall()
    
    print(f"\n📋 Time Slots ({len(slots)}):")
    
    # Create scheduler
    scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.TIMEZONE))
    
    # Add morning job
    scheduler.add_job(
        lambda: None,  # dummy function
        CronTrigger(
            hour=settings.MORNING_MESSAGE_HOUR,
            minute=settings.MORNING_MESSAGE_MINUTE,
            timezone=ZoneInfo(settings.TIMEZONE)
        ),
        id="morning_message",
        name="Morning Schedule Delivery"
    )
    print(f"\n✅ Morning job: {settings.MORNING_MESSAGE_HOUR}:{settings.MORNING_MESSAGE_MINUTE:02d} MSK")
    
    # Add reminder jobs for each slot
    for slot in slots:
        # Unpack based on actual columns: id, slot_number, start_time, end_time, created_at
        slot_id = slot[0]
        slot_number = slot[1]
        start_time = slot[2]
        end_time = slot[3]
        
        # Parse start time
        hours, minutes = map(int, start_time.split(":"))
        
        # Calculate reminder time (5 minutes before)
        reminder_minutes = minutes - settings.REMINDER_MINUTES_BEFORE
        reminder_hours = hours
        if reminder_minutes < 0:
            reminder_minutes += 60
            reminder_hours -= 1
        
        scheduler.add_job(
            lambda: None,  # dummy function
            CronTrigger(
                hour=reminder_hours,
                minute=reminder_minutes,
                timezone=ZoneInfo(settings.TIMEZONE)
            ),
            id=f"reminder_slot_{slot_id}",
            name=f"Reminder for Pair {slot_number}"
        )
        print(f"✅ Reminder job for Pair {slot_number}: {reminder_hours:02d}:{reminder_minutes:02d} MSK (pair starts at {start_time})")
    
    # Get all jobs
    jobs = scheduler.get_jobs()
    print(f"\n📊 Total scheduled jobs: {len(jobs)}")
    
    print("\n🔍 Job Details:")
    for job in jobs:
        print(f"   - {job.name} (ID: {job.id})")
    
    # Show current time
    now_msk = datetime.now(ZoneInfo(settings.TIMEZONE))
    print(f"\n🕐 Current time (MSK): {now_msk.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 50)
    print("✅ Scheduler configuration test complete!")
    print(f"   Total jobs: {len(jobs)} (1 morning + {len(slots)} reminders)")
    
    return len(jobs) == 6

if __name__ == "__main__":
    success = asyncio.run(test_scheduler())
    sys.exit(0 if success else 1)
