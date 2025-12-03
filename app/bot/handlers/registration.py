"""
Registration flow handlers.

Multi-step FSM-based user registration.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.db import get_connection
from app.db.queries import get_directions_by_course, get_direction_by_id, create_user, update_user_direction
from app.db.models.user import UserCreate
from app.bot.states import RegistrationStates
from app.bot.keyboards import (
    get_course_keyboard,
    get_direction_keyboard,
    get_confirmation_keyboard,
    get_main_menu_keyboard
)
from app.bot.utils import format_registration_confirmation
from app.utils.constants import REGISTRATION_COMPLETE

router = Router()


@router.message(RegistrationStates.awaiting_name)
async def process_name(message: Message, state: FSMContext):
    """Process user name input."""
    name = message.text.strip()
    
    if len(name) < 2 or len(name) > 100:
        await message.answer(
            "❌ Имя должно быть от 2 до 100 символов.\n\n"
            "Попробуй ещё раз:"
        )
        return
    
    # Save name to state
    await state.update_data(name=name)
    
    # Ask for course
    await message.answer(
        f"Приятно познакомиться, {name}! 😊\n\n"
        f"На каком курсе ты учишься?",
        reply_markup=get_course_keyboard()
    )
    await state.set_state(RegistrationStates.awaiting_course)


@router.callback_query(RegistrationStates.awaiting_course, F.data.startswith("course:"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    """Process course selection."""
    course = int(callback.data.split(":")[1])
    
    # Save course to state
    await state.update_data(course=course)
    
    # Get directions for this course
    conn = await get_connection()
    try:
        directions = await get_directions_by_course(conn, course)
        
        if not directions:
            await callback.message.edit_text(
                f"❌ К сожалению, для {course} курса пока нет доступных направлений.\n\n"
                f"Обратись к администратору."
            )
            await state.clear()
            return
        
        await callback.message.edit_text(
            f"Отлично! Теперь выбери своё направление:",
            reply_markup=get_direction_keyboard(directions)
        )
        await state.set_state(RegistrationStates.awaiting_direction)
    
    finally:
        await conn.close()
    
    await callback.answer()


@router.callback_query(RegistrationStates.awaiting_direction, F.data == "back_to_course")
async def back_to_course(callback: CallbackQuery, state: FSMContext):
    """Go back to course selection."""
    data = await state.get_data()
    name = data.get('name', 'Студент')
    
    await callback.message.edit_text(
        f"{name}, на каком курсе ты учишься?",
        reply_markup=get_course_keyboard()
    )
    await state.set_state(RegistrationStates.awaiting_course)
    await callback.answer()


@router.callback_query(RegistrationStates.awaiting_direction, F.data.startswith("direction:"))
async def process_direction(callback: CallbackQuery, state: FSMContext):
    """Process direction selection."""
    direction_id = int(callback.data.split(":")[1])
    
    # Get direction details
    conn = await get_connection()
    try:
        direction = await get_direction_by_id(conn, direction_id)
        
        if not direction:
            await callback.message.edit_text("❌ Направление не найдено. Попробуй ещё раз.")
            await state.clear()
            return
        
        # Save direction to state
        await state.update_data(
            direction_id=direction_id,
            direction_name=direction.name
        )
        
        # Show confirmation
        data = await state.get_data()
        name = data.get('name', 'Студент')
        course = data.get('course', 1)
        
        # Check if this is a direction change or new registration
        is_changing = data.get('changing_direction', False)
        
        if is_changing:
            confirmation_text = (
                f"📋 <b>Подтверди изменения:</b>\n\n"
                f"📚 Новый курс: {course}\n"
                f"🎓 Новое направление: {direction.name}\n\n"
                f"Всё верно?"
            )
        else:
            confirmation_text = (
                f"📋 <b>Проверь свои данные:</b>\n\n"
                f"👤 Имя: {name}\n"
                f"📚 Курс: {course}\n"
                f"🎓 Направление: {direction.name}\n\n"
                f"Всё верно?"
            )
        
        await callback.message.edit_text(
            confirmation_text,
            reply_markup=get_confirmation_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.confirming)
    
    finally:
        await conn.close()
    
    await callback.answer()


@router.callback_query(RegistrationStates.confirming, F.data == "confirm_registration")
async def confirm_registration(callback: CallbackQuery, state: FSMContext):
    """Confirm and save registration."""
    data = await state.get_data()
    
    name = data.get('name', 'Студент')
    course = data.get('course', 1)
    direction_id = data.get('direction_id')
    direction_name = data.get('direction_name', '')
    is_changing = data.get('changing_direction', False)
    
    # Connect to database
    conn = await get_connection()
    try:
        if is_changing:
            # Update existing user's direction
            await update_user_direction(conn, callback.from_user.id, course, direction_id)
            
            await callback.message.edit_text(
                f"✅ <b>Направление успешно изменено!</b>\n\n"
                f"📚 Курс: {course}\n"
                f"🎓 Направление: {direction_name}\n\n"
                f"Теперь ты будешь получать расписание для нового направления.",
                parse_mode="HTML"
            )
            
            # Clear state
            await state.clear()
            
            await callback.answer("✅ Направление изменено!")
        else:
            # Create new user
            user_data = UserCreate(
                tg_id=callback.from_user.id,
                name=name,
                course=course,
                direction_id=direction_id,
                remind_before=True
            )
            
            await create_user(conn, user_data)
            
            # Send confirmation message
            confirmation_msg = format_registration_confirmation(
                name=name,
                course=course,
                direction_name=direction_name,
                remind_before=True
            )
            
            await callback.message.edit_text(
                confirmation_msg,
                parse_mode="HTML"
            )
            
            # Clear state
            await state.clear()
            
            # Send completion message with main menu
            await callback.message.answer(
                f"🎉 <b>Регистрация завершена!</b>\n\n"
                f"Теперь ты будешь получать расписание каждое утро.\n"
                f"Используй кнопки меню ниже для навигации.",
                reply_markup=get_main_menu_keyboard(),
                parse_mode="HTML"
            )
            
            await callback.answer("✅ Регистрация завершена!")
    
    finally:
        await conn.close()


@router.callback_query(RegistrationStates.confirming, F.data == "restart_registration")
async def restart_registration(callback: CallbackQuery, state: FSMContext):
    """Restart registration from beginning."""
    data = await state.get_data()
    is_changing = data.get('changing_direction', False)
    
    if is_changing:
        # If changing direction, go back to course selection
        await callback.message.edit_text(
            "🔄 <b>Выбор направления</b>\n\n"
            "На каком курсе ты учишься?",
            reply_markup=get_course_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(RegistrationStates.awaiting_course)
    else:
        # Full restart for new registration
        await callback.message.edit_text(
            "Хорошо, начнём заново! 🔄\n\n"
            "Скажи мне, как тебя зовут?"
        )
        await state.set_state(RegistrationStates.awaiting_name)
    
    await callback.answer()
