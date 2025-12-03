"""
/settings command handler.

User settings management.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from app.db import get_connection
from app.db.queries import get_user_by_telegram_id, update_user_settings, get_directions_by_course, update_user_direction
from app.bot.keyboards import (
    get_settings_keyboard,
    get_pause_duration_keyboard,
    get_main_menu_keyboard,
    get_course_keyboard,
    get_direction_keyboard
)
from app.bot.states import RegistrationStates
from app.utils.constants import SETTINGS_MESSAGE, PAUSE_MESSAGE, RESUME_MESSAGE
from app.config import settings

router = Router()


def is_user_paused(user: dict) -> bool:
    """Check if user notifications are paused."""
    paused_until = user.get('paused_until')
    if paused_until:
        try:
            paused_dt = datetime.fromisoformat(paused_until)
            return paused_dt > datetime.now()
        except:
            pass
    return False


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Handle /settings command."""
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, message.from_user.id)
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Используй команду /start для регистрации."
            )
            return
        
        await message.answer(
            SETTINGS_MESSAGE,
            reply_markup=get_settings_keyboard(
                remind_before=user.get('remind_before', True),
                is_paused=is_user_paused(user)
            )
        )
    finally:
        await conn.close()


@router.message(F.text == "⚙️ Настройки")
async def settings_button(message: Message):
    """Handle settings button from main menu."""
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, message.from_user.id)
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Используй команду /start для регистрации."
            )
            return
        
        await message.answer(
            SETTINGS_MESSAGE,
            reply_markup=get_settings_keyboard(
                remind_before=user.get('remind_before', True),
                is_paused=is_user_paused(user)
            )
        )
    
    finally:
        await conn.close()


@router.callback_query(F.data == "toggle_reminders")
async def toggle_reminders(callback: CallbackQuery):
    """Toggle reminder notifications."""
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Toggle reminder setting
        new_value = not user.get('remind_before', True)
        await update_user_settings(conn, user['tg_id'], remind_before=new_value)
        
        status = "включены" if new_value else "выключены"
        await callback.message.edit_text(
            f"⚙️ <b>Настройки</b>\n\n"
            f"✅ Напоминания {status}.\n\n"
            f"Что ещё хочешь изменить?",
            reply_markup=get_settings_keyboard(new_value, is_user_paused(user)),
            parse_mode="HTML"
        )
        
        await callback.answer(f"✅ Напоминания {status}")
    
    finally:
        await conn.close()


@router.callback_query(F.data == "pause_notifications")
async def pause_notifications(callback: CallbackQuery):
    """Show pause duration menu."""
    await callback.message.edit_text(
        "⏸ <b>Приостановить уведомления</b>\n\n"
        "На сколько дней?",
        reply_markup=get_pause_duration_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pause:"))
async def process_pause_duration(callback: CallbackQuery):
    """Process pause duration selection."""
    days = int(callback.data.split(":")[1])
    
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Calculate pause until date
        pause_until = datetime.now() + timedelta(days=days)
        await update_user_settings(conn, user['tg_id'], paused_until=pause_until.isoformat())
        
        await callback.message.edit_text(
            f"⏸ <b>Уведомления приостановлены</b>\n\n"
            f"Ты не будешь получать сообщения до <b>{pause_until.strftime('%d.%m.%Y')}</b>.\n\n"
            f"Используй /settings для возобновления.",
            parse_mode="HTML"
        )
        
        await callback.answer(f"✅ Приостановлено на {days} дн.")
    
    finally:
        await conn.close()


@router.callback_query(F.data == "resume_notifications")
async def resume_notifications(callback: CallbackQuery):
    """Resume notifications."""
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Clear pause
        await update_user_settings(conn, user['tg_id'], paused_until=None)
        
        await callback.message.edit_text(
            "▶️ <b>Уведомления возобновлены!</b>\n\n"
            "Ты снова будешь получать расписание каждый день в 08:00 по МСК.",
            reply_markup=get_settings_keyboard(user.get('remind_before', True), False),
            parse_mode="HTML"
        )
        
        await callback.answer("✅ Уведомления возобновлены")
    
    finally:
        await conn.close()


@router.callback_query(F.data == "back_to_settings")
async def back_to_settings(callback: CallbackQuery):
    """Go back to settings menu."""
    conn = await get_connection()
    
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        await callback.message.edit_text(
            "⚙️ <b>Настройки</b>\n\n"
            "Что ты хочешь изменить?",
            reply_markup=get_settings_keyboard(
                user.get('remind_before', True), 
                is_user_paused(user)
            ),
            parse_mode="HTML"
        )
        
        await callback.answer()
    
    finally:
        await conn.close()


@router.callback_query(F.data == "share_bot")
async def share_bot(callback: CallbackQuery):
    """Show bot share message."""
    bot_username = (await callback.bot.get_me()).username
    share_link = f"https://t.me/{bot_username}"
    
    await callback.message.edit_text(
        f"📤 <b>Поделиться ботом</b>\n\n"
        f"Вот ссылка на бота:\n"
        f"{share_link}\n\n"
        f"Скопируй и отправь друзьям! 😊",
        parse_mode="HTML"
    )
    
    await callback.answer("Скопируй ссылку из сообщения")


@router.callback_query(F.data == "close_settings")
async def close_settings(callback: CallbackQuery):
    """Close settings menu."""
    await callback.message.delete()
    await callback.answer("✅ Закрыто")


@router.callback_query(F.data == "change_direction")
async def change_direction(callback: CallbackQuery, state: FSMContext):
    """Start direction change flow."""
    # Get current user data to preserve name
    conn = await get_connection()
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        if user:
            # Save user's name to state for the change flow
            await state.update_data(
                name=user.get('name', 'Студент'),
                changing_direction=True  # Flag to indicate we're changing, not registering
            )
    finally:
        await conn.close()
    
    await callback.message.edit_text(
        "🔄 <b>Смена направления</b>\n\n"
        "На каком курсе ты учишься?",
        reply_markup=get_course_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(RegistrationStates.awaiting_course)
    await callback.answer()
