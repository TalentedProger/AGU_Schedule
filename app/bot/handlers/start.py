"""
/start command handler.

Handles bot initialization and registration start.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.db import get_connection
from app.db.queries import get_user_by_telegram_id
from app.bot.states import RegistrationStates
from app.bot.keyboards import get_main_menu_keyboard
from app.utils.constants import WELCOME_MESSAGE

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    Handle /start command.
    
    If user exists, show welcome back message.
    If new user, start registration flow.
    """
    conn = await get_connection()
    
    try:
        # Check if user already registered
        user = await get_user_by_telegram_id(conn, message.from_user.id)
        
        if user:
            await message.answer(
                f"🎉 С возвращением, {user['name']}!\n\n"
                f"📅 Твоё расписание будет приходить каждое утро в 08:00 МСК.\n"
                f"⏰ Напоминания {'✅ включены' if user['remind_before'] else '❌ выключены'}.\n\n"
                f"💡 Используй главное меню внизу или команду /settings для изменения настроек.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # Start registration
            await message.answer(WELCOME_MESSAGE)
            await message.answer(
                "Для начала, скажи мне, как тебя зовут? 😊\n\n"
                "✏️ Напиши своё имя:"
            )
            await state.set_state(RegistrationStates.awaiting_name)
    
    finally:
        await conn.close()
