"""Main navigation keyboard with reply buttons."""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create main navigation keyboard with reply buttons.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📅 Расписание"),
                KeyboardButton(text="👤 Профиль")
            ],
            [
                KeyboardButton(text="⚙️ Настройки"),
                KeyboardButton(text="ℹ️ Справка")
            ],
            [
                KeyboardButton(text="🎨 Тема чата"),
                KeyboardButton(text="💙 Поддержка")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Выберите действие..."
    )
    
    return keyboard


def remove_keyboard() -> ReplyKeyboardMarkup:
    """
    Remove reply keyboard.
    
    Returns:
        Empty ReplyKeyboardMarkup to remove keyboard
    """
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
