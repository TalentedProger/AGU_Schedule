"""
Main application entry point.

Runs Telegram bot and scheduler simultaneously.
"""

import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.utils.logger import logger


async def main():
    """Main application entry point."""
    logger.info("Starting ScheduleBot...")
    
    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Initialize dispatcher with FSM storage
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register handlers
    from app.bot.handlers import register_handlers
    register_handlers(dp)
    
    # Initialize scheduler
    from app.scheduler import setup_scheduler
    scheduler = await setup_scheduler(bot)
    scheduler.start()
    
    try:
        logger.info("Bot started successfully. Press Ctrl+C to stop.")
        
        # Start polling
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        # Shutdown scheduler
        if 'scheduler' in locals():
            scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        await bot.session.close()
        logger.info("Bot stopped.")


async def start_admin_panel():
    """Start FastAPI admin panel."""
    import os
    import uvicorn
    import traceback
    from fastapi import FastAPI, Request
    from fastapi.responses import RedirectResponse, Response, HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from app.admin import router
    from app.admin.pairs import router as pairs_router
    from app.admin.directions import router as directions_router
    from app.admin.slots import router as slots_router
    from app.admin.broadcast import router as broadcast_router
    from app.admin.logs import router as logs_router
    
    logger.info("Starting Admin Panel...")
    
    app = FastAPI(title="AGU ScheduleBot Admin")
    templates = Jinja2Templates(directory='templates/errors')
    
    # Mount static files
    static_path = os.path.join(os.path.dirname(__file__), "web", "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Exception handler for HTTP errors
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 303 and exc.headers and "Location" in exc.headers:
            return RedirectResponse(url=exc.headers["Location"], status_code=303)
        # Return empty response for favicon.ico to avoid errors
        if request.url.path == "/favicon.ico":
            return Response(status_code=204)
        # Return proper error page for 404
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "404.html",
                {"request": request, "path": request.url.path},
                status_code=404
            )
        # Re-raise other HTTP exceptions
        from fastapi import HTTPException
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    
    # General exception handler for 500 errors
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Internal server error: {exc}", exc_info=True)
        error_detail = str(exc) if settings.DEBUG else None
        return templates.TemplateResponse(
            "500.html",
            {"request": request, "error_detail": error_detail},
            status_code=500
        )
    
    # Favicon route (returns empty if no favicon exists)
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = os.path.join(static_path, "images", "favicon.ico")
        if os.path.exists(favicon_path):
            with open(favicon_path, "rb") as f:
                return Response(content=f.read(), media_type="image/x-icon")
        return Response(status_code=204)
    
    # Root redirect
    @app.get("/")
    async def root():
        return RedirectResponse(url='/admin/login', status_code=302)
    
    app.include_router(router)
    app.include_router(pairs_router)
    app.include_router(directions_router)
    app.include_router(slots_router)
    app.include_router(broadcast_router)
    app.include_router(logs_router)
    
    config = uvicorn.Config(
        app,
        host=settings.ADMIN_HOST,
        port=settings.ADMIN_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Choose which service to run based on command line argument
    if len(sys.argv) > 1 and sys.argv[1] == "admin":
        # Run admin panel
        asyncio.run(start_admin_panel())
    else:
        # Run bot (default)
        asyncio.run(main())
