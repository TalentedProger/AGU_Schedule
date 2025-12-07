"""
Theme handler for custom Telegram chat themes.

Sends .tgtheme file that Telegram can apply natively.
"""

import os
from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.logger import logger
from app.bot.keyboards import get_main_menu_keyboard


router = Router()

THEME_MESSAGE = """
🎨 <b>Тема чата AGU ScheduleBot</b>

Выбери тему оформления для этого чата:

🌙 <b>Тёмная тема</b> — стильный тёмный дизайн с синими акцентами
☀️ <b>Светлая тема</b> — чистый светлый дизайн

После нажатия Telegram предложит применить тему.
Это изменит оформление только для этого чата!
"""


def get_theme_keyboard():
    """Create keyboard for theme selection."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌙 Тёмная тема", callback_data="theme:dark"),
            InlineKeyboardButton(text="☀️ Светлая тема", callback_data="theme:light")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="theme:cancel")
        ]
    ])


@router.message(F.text == "🎨 Тема чата")
async def theme_button(message: Message):
    """Handle theme button from main menu."""
    await message.answer(
        THEME_MESSAGE,
        reply_markup=get_theme_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "theme:dark")
async def send_dark_theme(callback: CallbackQuery):
    """Send dark theme file."""
    try:
        theme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "themes", 
            "agu_dark.attheme"
        )
        
        if not os.path.exists(theme_path):
            await callback.answer("❌ Файл темы не найден", show_alert=True)
            return
        
        theme_file = FSInputFile(theme_path, filename="AGU_ScheduleBot_Dark.tgtheme")
        
        await callback.message.edit_text(
            "🌙 <b>Тёмная тема AGU ScheduleBot</b>\n\n"
            "Нажми на файл ниже — Telegram предложит применить тему!",
            parse_mode="HTML"
        )
        
        await callback.message.answer_document(
            theme_file,
            caption="🎨 Тёмная тема AGU ScheduleBot\n\nНажми → Применить тему"
        )
        
        await callback.answer("🌙 Тёмная тема отправлена!")
        logger.info(f"Dark theme sent to user {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending dark theme: {e}")
        await callback.answer("❌ Ошибка при отправке темы", show_alert=True)


@router.callback_query(F.data == "theme:light")
async def send_light_theme(callback: CallbackQuery):
    """Send light theme file."""
    try:
        theme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "themes", 
            "agu_light.attheme"
        )
        
        if not os.path.exists(theme_path):
            await callback.answer("❌ Файл темы не найден", show_alert=True)
            return
        
        theme_file = FSInputFile(theme_path, filename="AGU_ScheduleBot_Light.tgtheme")
        
        await callback.message.edit_text(
            "☀️ <b>Светлая тема AGU ScheduleBot</b>\n\n"
            "Нажми на файл ниже — Telegram предложит применить тему!",
            parse_mode="HTML"
        )
        
        await callback.message.answer_document(
            theme_file,
            caption="🎨 Светлая тема AGU ScheduleBot\n\nНажми → Применить тему"
        )
        
        await callback.answer("☀️ Светлая тема отправлена!")
        logger.info(f"Light theme sent to user {callback.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending light theme: {e}")
        await callback.answer("❌ Ошибка при отправке темы", show_alert=True)


@router.callback_query(F.data == "theme:cancel")
async def cancel_theme(callback: CallbackQuery):
    """Cancel theme selection."""
    await callback.message.edit_text(
        "🎨 Выбор темы отменён.\n\n"
        "Ты можешь выбрать тему позже через кнопку «🎨 Тема чата» в меню.",
        parse_mode="HTML"
    )
    await callback.answer()
