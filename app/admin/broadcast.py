"""Admin panel broadcast routes."""

import asyncio
from typing import Optional, List

from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import get_current_session
from app.db.connection import get_connection
from app.utils.logger import logger
from app.utils.timezone import get_current_time_msk
from app.config import settings

router = APIRouter(prefix='/admin/broadcast', tags=['admin', 'broadcast'])
templates = Jinja2Templates(directory='templates')


async def get_users_by_filter(
    course: Optional[int] = None,
    direction_id: Optional[int] = None
) -> List[dict]:
    """
    Get users filtered by course and/or direction.
    
    Args:
        course: Filter by course number (1-4)
        direction_id: Filter by direction ID
    
    Returns:
        List of user dicts with id, tg_id, name
    """
    conn = await get_connection()
    try:
        query = """
            SELECT u.id, u.tg_id, u.name, d.name as direction_name, d.course
            FROM users u
            JOIN directions d ON u.direction_id = d.id
            WHERE (u.paused_until IS NULL OR u.paused_until < datetime('now'))
        """
        params = []
        
        if course:
            query += " AND d.course = ?"
            params.append(course)
        
        if direction_id:
            query += " AND u.direction_id = ?"
            params.append(direction_id)
        
        query += " ORDER BY u.name"
        
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        
        return [
            {
                'id': row[0],
                'tg_id': row[1],
                'name': row[2],
                'direction_name': row[3],
                'course': row[4]
            }
            for row in rows
        ]
    finally:
        await conn.close()


async def log_broadcast_delivery(
    user_id: int,
    status: str,
    error_message: Optional[str] = None
):
    """Log broadcast delivery to delivery_log table."""
    conn = await get_connection()
    try:
        await conn.execute(
            """
            INSERT INTO delivery_log (user_id, message_type, status, error_message, delivered_at)
            VALUES (?, 'broadcast', ?, ?, ?)
            """,
            (user_id, status, error_message, get_current_time_msk().isoformat())
        )
        await conn.commit()
    finally:
        await conn.close()


@router.get('', response_class=HTMLResponse)
async def broadcast_page(
    request: Request,
    session: dict = Depends(get_current_session)
):
    """
    Display broadcast form page.
    
    Args:
        request: FastAPI request object
        session: Current session
    
    Returns:
        Rendered broadcast.html template
    """
    conn = await get_connection()
    try:
        # Get all directions grouped by course
        cursor = await conn.execute(
            """
            SELECT d.id, d.name, d.course, COUNT(u.id) as user_count
            FROM directions d
            LEFT JOIN users u ON u.direction_id = d.id 
                AND (u.paused_until IS NULL OR u.paused_until < datetime('now'))
            GROUP BY d.id
            ORDER BY d.course, d.name
            """
        )
        rows = await cursor.fetchall()
        
        directions_by_course = {}
        for row in rows:
            course = row[2]
            if course not in directions_by_course:
                directions_by_course[course] = []
            directions_by_course[course].append({
                'id': row[0],
                'name': row[1],
                'user_count': row[3]
            })
        
        # Get total active users count
        cursor = await conn.execute(
            """
            SELECT COUNT(*) FROM users
            WHERE paused_until IS NULL OR paused_until < datetime('now')
            """
        )
        row = await cursor.fetchone()
        total_users = row[0] if row else 0
        
        # Get user counts by course
        cursor = await conn.execute(
            """
            SELECT d.course, COUNT(u.id) as count
            FROM users u
            JOIN directions d ON u.direction_id = d.id
            WHERE u.paused_until IS NULL OR u.paused_until < datetime('now')
            GROUP BY d.course
            """
        )
        rows = await cursor.fetchall()
        users_by_course = {row[0]: row[1] for row in rows}
        
        return templates.TemplateResponse(
            'broadcast.html',
            {
                'request': request,
                'username': session.get('username', 'admin'),
                'directions_by_course': directions_by_course,
                'total_users': total_users,
                'users_by_course': users_by_course
            }
        )
    finally:
        await conn.close()


@router.post('/send', response_class=HTMLResponse)
async def send_broadcast(
    request: Request,
    message_text: str = Form(...),
    target: str = Form(...),  # 'all', 'course_X', or 'direction_X'
    session: dict = Depends(get_current_session)
):
    """
    Send broadcast message to selected users.
    
    Args:
        request: FastAPI request object
        message_text: Message text to send
        target: Target filter ('all', 'course_1', 'direction_5', etc.)
        session: Current session
    
    Returns:
        Redirect to broadcast page with results
    """
    from aiogram import Bot
    from aiogram.client.default import DefaultBotProperties
    from aiogram.enums import ParseMode
    from aiogram.exceptions import TelegramAPIError
    
    # Parse target filter
    course = None
    direction_id = None
    
    if target.startswith('course_'):
        course = int(target.replace('course_', ''))
    elif target.startswith('direction_'):
        direction_id = int(target.replace('direction_', ''))
    # else target == 'all'
    
    # Get filtered users
    users = await get_users_by_filter(course=course, direction_id=direction_id)
    
    if not users:
        return RedirectResponse(
            url='/admin/broadcast?error=no_users',
            status_code=303
        )
    
    # Initialize bot for sending
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    successful = 0
    errors = 0
    
    try:
        # Send to all users with rate limiting
        for i, user in enumerate(users):
            try:
                await bot.send_message(
                    chat_id=user['tg_id'],
                    text=message_text
                )
                await log_broadcast_delivery(user['id'], 'sent')
                successful += 1
            except TelegramAPIError as e:
                logger.warning(f"Failed to send broadcast to {user['tg_id']}: {e}")
                await log_broadcast_delivery(user['id'], 'error', str(e))
                errors += 1
            except Exception as e:
                logger.error(f"Unexpected error sending broadcast to {user['tg_id']}: {e}")
                await log_broadcast_delivery(user['id'], 'error', str(e))
                errors += 1
            
            # Rate limiting: small delay every 30 messages
            if (i + 1) % 30 == 0:
                await asyncio.sleep(0.5)
        
        logger.info(f"Broadcast sent: {successful} successful, {errors} errors")
        
    finally:
        await bot.session.close()
    
    return RedirectResponse(
        url=f'/admin/broadcast?success={successful}&errors={errors}',
        status_code=303
    )


@router.get('/api/user_count')
async def get_user_count(
    target: str,
    session: dict = Depends(get_current_session)
):
    """
    API endpoint to get user count for a target filter.
    
    Args:
        target: Target filter ('all', 'course_1', 'direction_5', etc.)
        session: Current session
    
    Returns:
        JSON with user count
    """
    course = None
    direction_id = None
    
    if target.startswith('course_'):
        course = int(target.replace('course_', ''))
    elif target.startswith('direction_'):
        direction_id = int(target.replace('direction_', ''))
    
    users = await get_users_by_filter(course=course, direction_id=direction_id)
    
    return {'count': len(users)}
