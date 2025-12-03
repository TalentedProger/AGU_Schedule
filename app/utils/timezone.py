"""
Timezone conversion utilities.

Handles conversion between MSK (Europe/Moscow) and UTC.
"""

from datetime import datetime, time
from zoneinfo import ZoneInfo
from app.config import settings


# Moscow timezone
MSK = ZoneInfo(settings.TIMEZONE)
UTC = ZoneInfo("UTC")


def get_current_time_msk() -> datetime:
    """
    Get current time in Moscow timezone.
    
    Returns:
        datetime: Current time with MSK timezone
    """
    return datetime.now(MSK)


def time_to_msk(hour: int, minute: int = 0) -> time:
    """
    Create time object with MSK timezone.
    
    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
    
    Returns:
        time: Time object with MSK timezone info
    """
    return time(hour, minute, tzinfo=MSK)


def convert_to_utc(dt_msk: datetime) -> datetime:
    """
    Convert MSK datetime to UTC.
    
    Args:
        dt_msk: Datetime in MSK timezone
    
    Returns:
        datetime: Datetime in UTC timezone
    """
    if dt_msk.tzinfo is None:
        dt_msk = dt_msk.replace(tzinfo=MSK)
    return dt_msk.astimezone(UTC)


def convert_to_msk(dt_utc: datetime) -> datetime:
    """
    Convert UTC datetime to MSK.
    
    Args:
        dt_utc: Datetime in UTC timezone
    
    Returns:
        datetime: Datetime in MSK timezone
    """
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=UTC)
    return dt_utc.astimezone(MSK)


def format_time_msk(dt: datetime) -> str:
    """
    Format datetime in human-readable MSK format.
    
    Args:
        dt: Datetime to format
    
    Returns:
        str: Formatted time string (e.g., "14:30 MSK")
    """
    dt_msk = convert_to_msk(dt) if dt.tzinfo != MSK else dt
    return dt_msk.strftime("%H:%M MSK")


def get_weekday_name_ru(day_of_week: int) -> str:
    """
    Get Russian weekday name.
    
    Args:
        day_of_week: Day number (0=Monday, 6=Sunday)
    
    Returns:
        str: Russian weekday name
    """
    weekdays = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]
    return weekdays[day_of_week]
