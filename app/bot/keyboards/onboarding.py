"""
Keyboards for onboarding flow.

Creates inline keyboards for course and direction selection.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from app.db.models.direction import Direction


def get_course_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for course selection (1-4).
    
    Returns:
        InlineKeyboardMarkup with 4 course buttons
    """
    buttons = [
        [InlineKeyboardButton(text=f"{i} курс", callback_data=f"course:{i}")]
        for i in range(1, 5)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_direction_keyboard(directions: List[Direction]) -> InlineKeyboardMarkup:
    """
    Create keyboard for direction selection.
    
    Args:
        directions: List of directions for selected course
    
    Returns:
        InlineKeyboardMarkup with direction buttons
    """
    buttons = [
        [InlineKeyboardButton(text=direction.name, callback_data=f"direction:{direction.id}")]
        for direction in directions
    ]
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_course")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard for registration confirmation.
    
    Returns:
        InlineKeyboardMarkup with confirm/restart buttons
    """
    buttons = [
        [InlineKeyboardButton(text="✅ Всё верно!", callback_data="confirm_registration")],
        [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart_registration")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
