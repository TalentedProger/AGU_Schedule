"""Bot handlers package."""

from aiogram import Dispatcher

from . import start, registration, settings, support, theme, common


def register_handlers(dp: Dispatcher):
    """
    Register all bot handlers.
    
    Args:
        dp: Dispatcher instance
    """
    # Order matters - more specific handlers first
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(settings.router)
    dp.include_router(support.router)  # Support/payments handler
    dp.include_router(theme.router)     # Theme customization handler
    dp.include_router(common.router)    # Must be last (catches all)
