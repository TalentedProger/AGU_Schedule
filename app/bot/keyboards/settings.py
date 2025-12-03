"""
Keyboards for settings menu.

Creates inline keyboards for user settings management.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_settings_keyboard(remind_before: bool = True, is_paused: bool = False) -> InlineKeyboardMarkup:
    """
    Create settings menu keyboard.
    
    Args:
        remind_before: Current reminder setting
        is_paused: Whether notifications are paused
    
    Returns:
        InlineKeyboardMarkup with settings options
    """
    buttons = []
    
    # Toggle reminders
    reminder_text = "🔕 Выключить напоминания" if remind_before else "🔔 Включить напоминания"
    buttons.append([InlineKeyboardButton(text=reminder_text, callback_data="toggle_reminders")])
    
    # Pause/Resume notifications
    if is_paused:
        buttons.append([InlineKeyboardButton(text="▶️ Возобновить уведомления", callback_data="resume_notifications")])
    else:
        buttons.append([InlineKeyboardButton(text="⏸ Приостановить уведомления", callback_data="pause_notifications")])
    
    # Change direction
    buttons.append([InlineKeyboardButton(text="🔄 Сменить направление", callback_data="change_direction")])
    
    # Share bot
    buttons.append([InlineKeyboardButton(text="📤 Поделиться ботом", callback_data="share_bot")])
    
    # Close
    buttons.append([InlineKeyboardButton(text="❌ Закрыть", callback_data="close_settings")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_pause_duration_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for pause duration selection.
    
    Returns:
        InlineKeyboardMarkup with duration options
    """
    buttons = [
        [InlineKeyboardButton(text="1 день", callback_data="pause:1")],
        [InlineKeyboardButton(text="3 дня", callback_data="pause:3")],
        [InlineKeyboardButton(text="7 дней", callback_data="pause:7")],
        [InlineKeyboardButton(text="14 дней", callback_data="pause:14")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
