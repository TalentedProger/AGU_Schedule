"""
Theme handler - рекомендации встроенных тем Telegram.

Telegram не позволяет ботам устанавливать темы программно.
Вместо этого рекомендуем пользователям подходящие встроенные темы
с прямыми ссылками на установку.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.utils.logger import logger


router = Router()

# Коллекция рекомендуемых тем с прямыми ссылками
# Формат ссылок: t.me/addtheme/{theme_slug}
THEMES = {
    "dark": {
        "name": "Night Mode",
        "emoji": "🌙",
        "description": "Тёмная тема для комфорта глаз",
        "link": "https://t.me/addtheme/night_mode",
        "colors": "Тёмный фон, мягкие акценты"
    },
    "dark_blue": {
        "name": "Dark Blue",
        "emoji": "🔵",
        "description": "Стильная тёмно-синяя тема",
        "link": "https://t.me/addtheme/dark_blue",
        "colors": "Глубокий синий фон"
    },
    "light": {
        "name": "Day Mode",
        "emoji": "☀️",
        "description": "Светлая классическая тема",
        "link": "https://t.me/addtheme/day",
        "colors": "Чистый белый фон"
    },
    "classic": {
        "name": "Classic",
        "emoji": "📱",
        "description": "Классический Telegram",
        "link": "https://t.me/addtheme/classic",
        "colors": "Стандартные цвета"
    },
    "arctic": {
        "name": "Arctic",
        "emoji": "❄️",
        "description": "Холодная синяя тема",
        "link": "https://t.me/addtheme/arctic",
        "colors": "Ледяные оттенки"
    },
    "crimson": {
        "name": "Crimson",
        "emoji": "🔴",
        "description": "Насыщенная красная тема",
        "link": "https://t.me/addtheme/crimson",
        "colors": "Тёплые красные тона"
    }
}


THEME_MAIN_MESSAGE = """
🎨 <b>Темы оформления чата</b>

Выбери тему из рекомендованных ниже!
После нажатия откроется страница темы в Telegram.

💡 <b>Как установить:</b>
1️⃣ Нажми на кнопку с нужной темой
2️⃣ Откроется превью темы
3️⃣ Нажми «Apply» / «Применить»

🔹 Тема применится ко всем чатам
🔹 Можешь в любой момент сменить тему
"""


def get_theme_main_keyboard():
    """Create main theme selection keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌙 Тёмные темы", callback_data="themes:dark_list"),
            InlineKeyboardButton(text="☀️ Светлые темы", callback_data="themes:light_list")
        ],
        [
            InlineKeyboardButton(text="🎯 Все темы Telegram", url="https://t.me/themes"),
        ],
        [
            InlineKeyboardButton(text="❌ Закрыть", callback_data="themes:close")
        ]
    ])


def get_dark_themes_keyboard():
    """Create dark themes keyboard with direct links."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌙 Night Mode", url=THEMES["dark"]["link"]),
        ],
        [
            InlineKeyboardButton(text="🔵 Dark Blue", url=THEMES["dark_blue"]["link"]),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="themes:back"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data="themes:close")
        ]
    ])


def get_light_themes_keyboard():
    """Create light themes keyboard with direct links."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="☀️ Day Mode", url=THEMES["light"]["link"]),
        ],
        [
            InlineKeyboardButton(text="📱 Classic", url=THEMES["classic"]["link"]),
        ],
        [
            InlineKeyboardButton(text="❄️ Arctic", url=THEMES["arctic"]["link"]),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="themes:back"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data="themes:close")
        ]
    ])


@router.message(F.text == "🎨 Тема чата")
async def theme_button(message: Message):
    """Handle theme button from main menu."""
    await message.answer(
        THEME_MAIN_MESSAGE,
        reply_markup=get_theme_main_keyboard(),
        parse_mode="HTML"
    )
    logger.info(f"Theme menu opened by user {message.from_user.id}")


@router.callback_query(F.data == "themes:dark_list")
async def show_dark_themes(callback: CallbackQuery):
    """Show list of dark themes."""
    message_text = (
        "🌙 <b>Тёмные темы</b>\n\n"
        "Нажми на кнопку — откроется превью темы.\n"
        "Затем нажми «Apply» для установки.\n\n"
        f"<b>{THEMES['dark']['emoji']} {THEMES['dark']['name']}</b>\n"
        f"└ {THEMES['dark']['description']}\n\n"
        f"<b>{THEMES['dark_blue']['emoji']} {THEMES['dark_blue']['name']}</b>\n"
        f"└ {THEMES['dark_blue']['description']}"
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_dark_themes_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "themes:light_list")
async def show_light_themes(callback: CallbackQuery):
    """Show list of light themes."""
    message_text = (
        "☀️ <b>Светлые темы</b>\n\n"
        "Нажми на кнопку — откроется превью темы.\n"
        "Затем нажми «Apply» для установки.\n\n"
        f"<b>{THEMES['light']['emoji']} {THEMES['light']['name']}</b>\n"
        f"└ {THEMES['light']['description']}\n\n"
        f"<b>{THEMES['classic']['emoji']} {THEMES['classic']['name']}</b>\n"
        f"└ {THEMES['classic']['description']}\n\n"
        f"<b>{THEMES['arctic']['emoji']} {THEMES['arctic']['name']}</b>\n"
        f"└ {THEMES['arctic']['description']}"
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=get_light_themes_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "themes:back")
async def back_to_theme_menu(callback: CallbackQuery):
    """Return to main theme menu."""
    await callback.message.edit_text(
        THEME_MAIN_MESSAGE,
        reply_markup=get_theme_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "themes:close")
async def close_theme_menu(callback: CallbackQuery):
    """Close theme selection menu."""
    await callback.message.edit_text(
        "🎨 Меню тем закрыто.\n\n"
        "Нажми «🎨 Тема чата» в главном меню, чтобы открыть снова.",
        parse_mode="HTML"
    )
    await callback.answer()
