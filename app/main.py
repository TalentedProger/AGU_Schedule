"""
Main application entry point.

Runs Telegram bot and scheduler simultaneously.
Supports both local (polling) and cloud (webhook) modes.
"""

import asyncio
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings
from app.utils.logger import logger


def is_cloud_deployment() -> bool:
    """Check if running in cloud environment."""
    return bool(os.environ.get('RAILWAY_ENVIRONMENT') or 
                os.environ.get('RENDER') or 
                os.environ.get('DATABASE_URL'))


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
    
    # Add middleware for handling OPTIONS requests (CORS preflight)
    @app.middleware("http")
    async def catch_all_middleware(request: Request, call_next):
        # Handle OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            })
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error but don't crash the server
            if "405" not in str(e):  # Don't spam 405 errors
                logger.error(f"Request error on {request.method} {request.url.path}: {e}")
            raise
    
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
    
    # Use PORT from environment (for cloud deployment) or fallback to config
    port = int(os.environ.get('PORT', settings.ADMIN_PORT))
    host = os.environ.get('HOST', '0.0.0.0' if is_cloud_deployment() else settings.ADMIN_HOST)
    
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


async def start_combined():
    """Start both bot and admin panel together (for single-service cloud deployment)."""
    import os
    import uvicorn
    from fastapi import FastAPI, Request
    from fastapi.responses import RedirectResponse, Response
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from app.admin import router
    from app.admin.pairs import router as pairs_router
    from app.admin.directions import router as directions_router
    from app.admin.slots import router as slots_router
    from app.admin.broadcast import router as broadcast_router
    from app.admin.logs import router as logs_router
    
    logger.info("Starting Combined Mode (Bot + Admin Panel)...")
    
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
    
    # Create FastAPI app
    app = FastAPI(title="AGU ScheduleBot Admin")
    templates = Jinja2Templates(directory='templates/errors')
    
    # Add middleware for handling OPTIONS requests (CORS preflight)
    @app.middleware("http")
    async def catch_all_middleware(request: Request, call_next):
        # Handle OPTIONS requests for CORS preflight
        if request.method == "OPTIONS":
            return Response(status_code=200, headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            })
        
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error but don't crash the server
            if "405" not in str(e):  # Don't spam 405 errors
                logger.error(f"Request error on {request.method} {request.url.path}: {e}")
            raise
    
    # Mount static files
    static_path = os.path.join(os.path.dirname(__file__), "web", "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Exception handlers
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 303 and exc.headers and "Location" in exc.headers:
            return RedirectResponse(url=exc.headers["Location"], status_code=303)
        if request.url.path == "/favicon.ico":
            return Response(status_code=204)
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "404.html",
                {"request": request, "path": request.url.path},
                status_code=404
            )
        from fastapi import HTTPException
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Internal server error: {exc}", exc_info=True)
        error_detail = str(exc) if settings.DEBUG else None
        return templates.TemplateResponse(
            "500.html",
            {"request": request, "error_detail": error_detail},
            status_code=500
        )
    
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = os.path.join(static_path, "images", "favicon.ico")
        if os.path.exists(favicon_path):
            with open(favicon_path, "rb") as f:
                return Response(content=f.read(), media_type="image/x-icon")
        return Response(status_code=204)
    
    @app.get("/")
    async def root():
        return RedirectResponse(url='/admin/login', status_code=302)
    
    # Health check endpoint for cloud platforms
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "mode": "combined"}
    
    app.include_router(router)
    app.include_router(pairs_router)
    app.include_router(directions_router)
    app.include_router(slots_router)
    app.include_router(broadcast_router)
    app.include_router(logs_router)
    
    # Get port from environment (Railway/Render set PORT)
    port = int(os.environ.get('PORT', settings.ADMIN_PORT))
    
    # Start web server in background
    config = uvicorn.Config(app, host='0.0.0.0', port=port, log_level="info")
    server = uvicorn.Server(config)
    
    # Run both concurrently
    async def run_bot():
        try:
            logger.info("Bot polling started...")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
    
    try:
        # Run web server and bot together
        await asyncio.gather(
            server.serve(),
            run_bot()
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Services stopped.")


if __name__ == "__main__":
    # Choose which service to run based on command line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "admin":
            # Run admin panel only
            asyncio.run(start_admin_panel())
        elif mode == "combined":
            # Run both bot and admin panel together (for single-service cloud)
            asyncio.run(start_combined())
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python -m app.main [admin|combined]")
            sys.exit(1)
    else:
        # Run bot only (default for local development)
        asyncio.run(main())
