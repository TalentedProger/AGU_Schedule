"""Admin panel routes."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.admin.auth import (
    verify_credentials,
    create_session,
    destroy_session,
    get_session,
    get_current_session
)
from app.db.connection import get_connection
from app.utils.logger import logger
from app.utils.timezone import get_current_time_msk

router = APIRouter(prefix='/admin', tags=['admin'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
async def admin_root(session_id: Optional[str] = Cookie(None)):
    """Redirect /admin to /admin/login or /admin/dashboard."""
    session = get_session(session_id)
    
    if session and session.get('authenticated'):
        return RedirectResponse(url='/admin/dashboard', status_code=302)
    else:
        return RedirectResponse(url='/admin/login', status_code=302)


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    """
    Display login page.
    
    Args:
        request: FastAPI request object
        error: Optional error message to display
    
    Returns:
        Rendered login.html template
    """
    return templates.TemplateResponse(
        'login.html',
        {
            'request': request,
            'error': error
        }
    )


@router.post('/login')
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Process login form submission.
    
    Args:
        request: FastAPI request object
        username: Username from form
        password: Password from form
    
    Returns:
        Redirect to dashboard on success, login page with error on failure
    """
    # Verify credentials
    if not verify_credentials(username, password):
        logger.warning(f"Failed login attempt for username: {username}")
        return RedirectResponse(
            url='/admin/login?error=invalid',
            status_code=303
        )
    
    # Create session
    session_id = create_session(username)
    
    # Set cookie and redirect to dashboard
    response = RedirectResponse(url='/admin/dashboard', status_code=302)
    response.set_cookie(
        key='session_id',
        value=session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        max_age=86400,  # 24 hours
        samesite='lax',
        path='/'
    )
    
    logger.info(f"Successful login for user: {username}")
    return response


@router.post('/logout')
async def logout(session_id: Optional[str] = Cookie(None)):
    """
    Process logout request.
    
    Args:
        session_id: Session ID from cookie
    
    Returns:
        Redirect to login page with session destroyed
    """
    # Destroy session
    destroy_session(session_id)
    
    # Redirect to login page
    response = RedirectResponse(url='/admin/login', status_code=303)
    response.delete_cookie('session_id')
    
    return response


@router.get('/dashboard', response_class=HTMLResponse)
async def dashboard(
    request: Request,
    session: dict = Depends(get_current_session)
):
    """
    Display admin dashboard with statistics.
    
    Args:
        request: FastAPI request object
        session: Current session (from dependency)
    
    Returns:
        Rendered dashboard.html template
    """
    conn = await get_connection()
    try:
        # Get total users
        cursor = await conn.execute(
            "SELECT COUNT(*) as count FROM users"
        )
        row = await cursor.fetchone()
        total_users = row[0] if row else 0
        
        # Get total pairs
        cursor = await conn.execute(
            "SELECT COUNT(*) as count FROM pairs"
        )
        row = await cursor.fetchone()
        total_pairs = row[0] if row else 0
        
        # Get messages sent today
        today_start = get_current_time_msk().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cursor = await conn.execute(
            """
            SELECT COUNT(*) as count FROM delivery_log
            WHERE delivered_at >= ?
            """,
            (today_start.isoformat(),)
        )
        row = await cursor.fetchone()
        messages_today = row[0] if row else 0
        
        # Calculate error rate today
        cursor = await conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
            FROM delivery_log
            WHERE delivered_at >= ?
            """,
            (today_start.isoformat(),)
        )
        row = await cursor.fetchone()
        if row and row[0] > 0:
            error_rate = ((row[1] or 0) / row[0]) * 100
        else:
            error_rate = 0.0
        
        # Get recent delivery logs (last 50)
        cursor = await conn.execute(
            """
            SELECT 
                dl.delivered_at,
                dl.message_type,
                u.name,
                dl.status,
                dl.error_message
            FROM delivery_log dl
            LEFT JOIN users u ON dl.user_id = u.id
            ORDER BY dl.delivered_at DESC
            LIMIT 50
            """
        )
        rows = await cursor.fetchall()
        
        # Format delivery logs
        delivery_logs = []
        for row in rows:
            try:
                delivery_time = datetime.fromisoformat(row[0]).strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                delivery_time = str(row[0]) if row[0] else 'N/A'
            
            delivery_logs.append({
                'delivery_time': delivery_time,
                'message_type': row[1],
                'username': row[2] or 'N/A',
                'success': row[3] == 'sent',
                'error_message': row[4]
            })
        
        # Render dashboard template
        return templates.TemplateResponse(
            'dashboard.html',
            {
                'request': request,
                'username': session.get('username', 'admin'),
                'stats': {
                    'total_users': total_users,
                    'total_pairs': total_pairs,
                    'messages_today': messages_today,
                    'error_rate': f"{error_rate:.2f}%"
                },
                'delivery_logs': delivery_logs
            }
        )
    finally:
        await conn.close()
