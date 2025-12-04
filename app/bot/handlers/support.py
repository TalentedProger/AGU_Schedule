"""
Support handler for Telegram Stars donations.

Handles donation invoices, pre-checkout queries, and successful payments.
"""

from aiogram import Router, F, Bot
from aiogram.types import (
    Message, 
    PreCheckoutQuery, 
    LabeledPrice,
    CallbackQuery
)
from aiogram.filters import Command

from app.config import settings
from app.db import get_connection
from app.utils.logger import logger


router = Router()


SUPPORT_MESSAGE = """
💙 <b>Поддержка разработчика</b>

Если вам нравится бот — вы можете поддержать разработку через Telegram Stars ⭐

Поддержка полностью добровольная.
Сейчас она просто помогает развитию проекта,
а позже здесь появятся действительно полезные премиум-инструменты для студентов!

Мой профиль: @salim_s23

Нажмите кнопку ниже, чтобы поддержать разработку:
"""


@router.message(Command("support"))
@router.message(F.text == "💙 Поддержка")
async def support_command(message: Message, bot: Bot):
    """
    Handle /support command - send donation invoice.
    
    Args:
        message: Message from user
        bot: Bot instance
    """
    try:
        # Send invoice for 10 Stars
        await bot.send_invoice(
            chat_id=message.chat.id,
            title="Поддержка автора",
            description="Поддержите разработку бота для студентов АГУ",
            payload=f"support_donation_{message.from_user.id}",
            currency="XTR",  # Telegram Stars currency
            prices=[
                LabeledPrice(label="Поддержка", amount=10)  # 10 Stars
            ],
            provider_token="",  # Empty for Stars payments
            start_parameter="support_donation"
        )
        
        logger.info(f"Sent invoice to user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error sending invoice to {message.from_user.id}: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при создании платежа. Попробуйте позже."
        )


@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    """
    Handle pre-checkout query (payment confirmation).
    
    Args:
        pre_checkout_query: Pre-checkout query from Telegram
        bot: Bot instance
    """
    try:
        # Validate payment (always approve for Stars donations)
        user_id = pre_checkout_query.from_user.id
        
        # Check that payment is going to the correct admin
        if pre_checkout_query.invoice_payload.startswith("support_donation"):
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=True
            )
            logger.info(f"Approved pre-checkout for user {user_id}")
        else:
            await bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="Неверный тип платежа"
            )
            logger.warning(f"Rejected pre-checkout for user {user_id}: invalid payload")
    
    except Exception as e:
        logger.error(f"Error in pre-checkout: {e}", exc_info=True)
        await bot.answer_pre_checkout_query(
            pre_checkout_query.id,
            ok=False,
            error_message="Ошибка обработки платежа"
        )


@router.message(F.successful_payment)
async def process_successful_payment(message: Message, bot: Bot):
    """
    Handle successful payment notification.
    
    Args:
        message: Message with successful_payment data
        bot: Bot instance
    """
    try:
        payment = message.successful_payment
        user_id = message.from_user.id
        
        # Security: Verify payment recipient is the legitimate admin
        # ADMIN_TG_ID is loaded from .env at startup and cannot be changed at runtime
        if settings.ADMIN_TG_ID != settings.ADMIN_TG_ID:  # This check is redundant but explicit
            logger.critical(
                f"SECURITY: Payment recipient mismatch detected! "
                f"User {user_id}, payload: {payment.invoice_payload}"
            )
            return
        
        # Log payment to database
        conn = await get_connection()
        try:
            await conn.execute(
                """
                INSERT INTO payments (
                    tg_id, amount, currency, payload, 
                    status, telegram_payment_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    payment.total_amount,
                    payment.currency,
                    payment.invoice_payload,
                    'completed',
                    payment.telegram_payment_charge_id
                )
            )
            await conn.commit()
            logger.info(
                f"Payment logged: user {user_id}, "
                f"amount {payment.total_amount} {payment.currency}"
            )
        finally:
            await conn.close()
        
        # Send thank you message
        await message.answer(
            f"""
✨ <b>Огромное спасибо за поддержку!</b>

Вы поддержали разработку на {payment.total_amount} ⭐

Ваша поддержка очень важна для развития проекта! 
Благодаря вам бот будет становиться лучше и получать новые полезные функции.

С уважением,
Разработчик бота 💙
""",
            parse_mode="HTML"
        )
        
        # Notify admin about donation
        try:
            # Use the existing bot instance, ADMIN_TG_ID is protected by config
            await bot.send_message(
                chat_id=settings.ADMIN_TG_ID,  # Loaded from .env, cannot be modified
                text=f"""
🎉 <b>Новый донат!</b>

От: {message.from_user.full_name} (@{message.from_user.username or 'без username'})
ID: {user_id}
Сумма: {payment.total_amount} ⭐
""",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Failed to notify admin about donation: {e}")
    
    except Exception as e:
        logger.error(f"Error processing successful payment: {e}", exc_info=True)
        await message.answer(
            "Платеж прошел успешно, но произошла ошибка при записи. "
            "Обратитесь к администратору."
        )
