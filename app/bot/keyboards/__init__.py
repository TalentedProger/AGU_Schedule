"""Bot keyboards package."""

from .onboarding import (
    get_course_keyboard,
    get_direction_keyboard,
    get_confirmation_keyboard
)

from .settings import (
    get_settings_keyboard,
    get_pause_duration_keyboard
)

from .main_menu import (
    get_main_menu_keyboard,
    remove_keyboard
)

__all__ = [
    'get_course_keyboard',
    'get_direction_keyboard',
    'get_confirmation_keyboard',
    'get_settings_keyboard',
    'get_pause_duration_keyboard',
    'get_main_menu_keyboard',
    'remove_keyboard'
]
