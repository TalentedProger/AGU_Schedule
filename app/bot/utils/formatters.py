"""
Message formatters for schedule display.

Formats schedule and reminder messages for users.
"""

from typing import List, Tuple
from app.db.models.pair import Pair
from app.utils.timezone import get_weekday_name_ru


def format_schedule_message(
    pairs: List[Tuple[Pair, str, str]],
    day_of_week: int,
    user_name: str
) -> str:
    """
    Format morning schedule message.
    
    Args:
        pairs: List of (Pair, start_time, end_time)
        day_of_week: Day of week (0=Monday)
        user_name: Student name
    
    Returns:
        Formatted message text
    """
    weekday_name = get_weekday_name_ru(day_of_week)
    
    if not pairs:
        return f"""
📅 <b>{weekday_name}</b>

Привет, {user_name}! 👋

Сегодня у тебя нет пар. Отдыхай! 😊
"""
    
    message = f"""
📅 <b>{weekday_name}</b>

Привет, {user_name}! 👋
Вот твоё расписание на сегодня:

"""
    
    for pair, start_time, end_time in pairs:
        message += f"""
🕐 <b>{start_time} - {end_time}</b>
📚 {pair.title}
👨‍🏫 {pair.teacher}
🏛 {pair.room}
📝 {pair.type}
"""
        if pair.extra_link:
            message += f"🔗 <a href='{pair.extra_link}'>Ссылка на занятие</a>\n"
        
        message += "\n"
    
    message += "Удачного дня! 🎓"
    
    return message.strip()


def format_reminder_message(
    pair: Pair,
    start_time: str,
    end_time: str
) -> str:
    """
    Format 5-minute reminder message.
    
    Args:
        pair: Pair object
        start_time: Start time (HH:MM)
        end_time: End time (HH:MM)
    
    Returns:
        Formatted reminder text
    """
    message = f"""
⏰ <b>Напоминание!</b>

Через 5 минут начинается пара:

🕐 {start_time} - {end_time}
📚 <b>{pair.title}</b>
👨‍🏫 {pair.teacher}
🏛 {pair.room}
"""
    
    if pair.extra_link:
        message += f"\n🔗 <a href='{pair.extra_link}'>Перейти к занятию</a>"
    
    return message.strip()


def format_registration_confirmation(
    name: str,
    course: int,
    direction_name: str,
    remind_before: bool
) -> str:
    """
    Format registration confirmation message.
    
    Args:
        name: Student name
        course: Course number
        direction_name: Direction name
        remind_before: Reminders enabled
    
    Returns:
        Formatted confirmation text
    """
    return f"""
✅ <b>Регистрация завершена!</b>

👤 Имя: {name}
📚 Курс: {course}
🎓 Направление: {direction_name}
⏰ Напоминания: {"Включены" if remind_before else "Выключены"}

Отлично! Теперь ты будешь получать расписание каждый день в <b>08:00 по МСК</b>.

Используй команду /settings для изменения настроек.
"""
