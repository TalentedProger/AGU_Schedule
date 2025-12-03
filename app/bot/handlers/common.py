"""
Common handlers.

Error handling and unknown commands.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram.filters import Command

from app.utils.logger import logger
from app.bot.keyboards import get_main_menu_keyboard
from app.utils.constants import HELP_MESSAGE, WEEKDAY_NAMES

router = Router()


def get_schedule_keyboard():
    """Create inline keyboard for schedule selection."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    buttons = [
        [
            InlineKeyboardButton(text="📅 На сегодня", callback_data="schedule:today"),
            InlineKeyboardButton(text="📆 На завтра", callback_data="schedule:tomorrow")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    await message.answer(
        HELP_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "ℹ️ Справка")
async def help_button(message: Message):
    """Handle help button from main menu."""
    await message.answer(
        HELP_MESSAGE,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📤 Поделиться")
async def share_button(message: Message):
    """Handle share button from main menu."""
    bot_username = (await message.bot.me()).username
    share_text = (
        f"🎓 <b>AGU ScheduleBot</b>\n\n"
        f"Удобный бот для получения расписания занятий АГУ!\n\n"
        f"✨ <b>Возможности:</b>\n"
        f"📅 Расписание каждое утро\n"
        f"⏰ Напоминания за 5 минут до пары\n"
        f"⚙️ Гибкие настройки уведомлений\n\n"
        f"👉 Попробуй сам: @{bot_username}"
    )
    await message.answer(
        share_text,
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📅 Расписание")
async def schedule_button(message: Message):
    """Handle schedule button from main menu - show day selection."""
    from app.db.connection import get_connection
    from app.db.queries import get_user_by_telegram_id
    
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
            "📅 <b>Расписание</b>\n\n"
            "Выбери, на какой день показать расписание:",
            reply_markup=get_schedule_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await conn.close()


async def get_schedule_for_day(conn, user: dict, day_of_week: int) -> str:
    """
    Get formatted schedule for specific day.
    
    Args:
        conn: Database connection
        user: User dict with direction_id
        day_of_week: Day of week (0=Monday, 6=Sunday)
    
    Returns:
        Formatted schedule message
    """
    # Get schedule from database
    # DB schema: title, teacher, room, type (NOT subject_name, teacher_name, pair_type)
    cursor = await conn.execute(
        """
        SELECT 
            p.title,
            p.teacher,
            p.room,
            p.type,
            ts.start_time,
            ts.end_time,
            ts.slot_number
        FROM pairs p
        JOIN time_slots ts ON p.time_slot_id = ts.id
        JOIN pair_assignments pa ON p.id = pa.pair_id
        WHERE pa.direction_id = ?
        AND p.day_of_week = ?
        ORDER BY ts.slot_number
        """,
        (user['direction_id'], day_of_week)
    )
    pairs = await cursor.fetchall()
    
    day_name = WEEKDAY_NAMES[day_of_week] if day_of_week < len(WEEKDAY_NAMES) else "день"
    
    if not pairs:
        return (
            f"📅 <b>Расписание на {day_name}</b>\n\n"
            f"🎉 В этот день пар нет! Отдыхай!\n\n"
            f"🎓 Направление: {user.get('direction_name', 'Не указано')}"
        )
    
    # Format schedule
    schedule_lines = [f"📅 <b>Расписание на {day_name}</b>\n"]
    schedule_lines.append(f"🎓 {user.get('direction_name', 'Направление')}\n")
    
    for pair in pairs:
        title, teacher, room, pair_type, start_time, end_time, slot_num = pair
        schedule_lines.append(
            f"\n<b>{slot_num}️⃣ {start_time} - {end_time}</b>\n"
            f"📚 {title}\n"
            f"👨‍🏫 {teacher}\n"
            f"🏫 Ауд. {room} • {pair_type}"
        )
    
    return "\n".join(schedule_lines)


@router.callback_query(F.data == "schedule:today")
async def schedule_today(callback: CallbackQuery):
    """Show schedule for today."""
    from app.db.connection import get_connection
    from app.db.queries import get_user_by_telegram_id
    from app.utils.timezone import get_current_time_msk
    
    conn = await get_connection()
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Get current day (0=Monday, 6=Sunday)
        current_time = get_current_time_msk()
        day_of_week = current_time.weekday()
        
        schedule_text = await get_schedule_for_day(conn, user, day_of_week)
        
        await callback.message.edit_text(
            schedule_text,
            parse_mode="HTML"
        )
        await callback.answer()
    finally:
        await conn.close()


@router.callback_query(F.data == "schedule:tomorrow")
async def schedule_tomorrow(callback: CallbackQuery):
    """Show schedule for tomorrow."""
    from app.db.connection import get_connection
    from app.db.queries import get_user_by_telegram_id
    from app.utils.timezone import get_current_time_msk
    
    conn = await get_connection()
    try:
        user = await get_user_by_telegram_id(conn, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        # Get tomorrow's day (0=Monday, 6=Sunday)
        current_time = get_current_time_msk()
        day_of_week = (current_time.weekday() + 1) % 7
        
        schedule_text = await get_schedule_for_day(conn, user, day_of_week)
        
        await callback.message.edit_text(
            schedule_text,
            parse_mode="HTML"
        )
        await callback.answer()
    finally:
        await conn.close()


@router.message(F.text == "👤 Профиль")
async def profile_button(message: Message):
    """Handle profile button from main menu."""
    from app.db.connection import get_connection
    from app.db.queries import get_user_by_telegram_id
    from datetime import datetime
    
    conn = await get_connection()
    try:
        user = await get_user_by_telegram_id(conn, message.from_user.id)
        
        if not user:
            await message.answer(
                "❌ Ты ещё не зарегистрирован!\n\n"
                "Используй команду /start для регистрации."
            )
            return
        
        # Format profile info
        remind_status = "✅ Включены" if user.get('remind_before') else "❌ Выключены"
        
        pause_status = "Нет"
        if user.get('paused_until'):
            try:
                paused_until = datetime.fromisoformat(user['paused_until'])
                if paused_until > datetime.now():
                    pause_status = f"До {paused_until.strftime('%d.%m.%Y')}"
            except:
                pass
        
        profile_text = (
            f"👤 <b>Твой профиль</b>\n\n"
            f"📛 Имя: {user.get('name', 'Не указано')}\n"
            f"📚 Курс: {user.get('course', 'Не указан')}\n"
            f"🎓 Направление: {user.get('direction_name', 'Не указано')}\n\n"
            f"⚙️ <b>Настройки:</b>\n"
            f"🔔 Напоминания: {remind_status}\n"
            f"⏸ Пауза: {pause_status}\n\n"
            f"💡 Используй ⚙️ Настройки для изменения"
        )
        
        await message.answer(
            profile_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML"
        )
    finally:
        await conn.close()


@router.message()
async def unknown_message(message: Message):
    """Handle unknown messages."""
    await message.answer(
        "🤔 Я не понимаю эту команду.\n\n"
        "💡 Используй главное меню внизу или команду /help для списка доступных команд.",
        reply_markup=get_main_menu_keyboard()
    )


@router.error()
async def error_handler(event: ErrorEvent):
    """Global error handler."""
    logger.error(f"Update error: {event.exception}", exc_info=True)
    
    if event.update.message:
        await event.update.message.answer(
            "❌ Произошла ошибка. Попробуй позже или обратись к администратору.",
            reply_markup=get_main_menu_keyboard()
        )
