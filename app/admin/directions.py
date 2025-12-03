"""Admin directions management routes."""

from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import get_current_session
from app.db.connection import get_connection
from app.utils.logger import logger

router = APIRouter(prefix='/admin/directions', tags=['admin_directions'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
async def directions_list(
    request: Request,
    session: dict = Depends(get_current_session),
    course: Optional[str] = None
):
    """Display list of all directions with optional course filter."""
    # Convert course to int if provided
    course_int: Optional[int] = int(course) if course and course.strip() else None
    
    conn = await get_connection()
    try:
        # Get all directions with user counts
        if course_int:
            cursor = await conn.execute(
                """
                SELECT d.id, d.name, d.course, 
                       (SELECT COUNT(*) FROM users WHERE direction_id = d.id) as user_count
                FROM directions d
                WHERE d.course = ?
                ORDER BY d.course, d.name
                """,
                (course_int,)
            )
        else:
            cursor = await conn.execute(
                """
                SELECT d.id, d.name, d.course, 
                       (SELECT COUNT(*) FROM users WHERE direction_id = d.id) as user_count
                FROM directions d
                ORDER BY d.course, d.name
                """
            )
        
        rows = await cursor.fetchall()
        directions = [
            {'id': r[0], 'name': r[1], 'course': r[2], 'user_count': r[3]}
            for r in rows
        ]
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'directions_list.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'directions': directions,
            'filter_course': course_int
        }
    )


@router.get('/new', response_class=HTMLResponse)
async def direction_new_form(
    request: Request,
    session: dict = Depends(get_current_session)
):
    """Display form for creating new direction."""
    return templates.TemplateResponse(
        'direction_form.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'mode': 'create',
            'direction': None
        }
    )


@router.post('/new')
async def direction_create(
    request: Request,
    session: dict = Depends(get_current_session),
    name: str = Form(...),
    course: int = Form(...)
):
    """Create new direction."""
    conn = await get_connection()
    try:
        await conn.execute(
            "INSERT INTO directions (name, course) VALUES (?, ?)",
            (name, course)
        )
        await conn.commit()
        logger.info(f"Created direction: {name} (course {course})")
    except Exception as e:
        logger.error(f"Failed to create direction: {e}")
        # Likely duplicate
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/directions', status_code=303)


@router.get('/{direction_id}/edit', response_class=HTMLResponse)
async def direction_edit_form(
    request: Request,
    direction_id: int,
    session: dict = Depends(get_current_session)
):
    """Display form for editing direction."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT id, name, course FROM directions WHERE id = ?",
            (direction_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return RedirectResponse(url='/admin/directions', status_code=303)
        
        direction = {'id': row[0], 'name': row[1], 'course': row[2]}
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'direction_form.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'mode': 'edit',
            'direction': direction
        }
    )


@router.post('/{direction_id}/edit')
async def direction_update(
    request: Request,
    direction_id: int,
    session: dict = Depends(get_current_session),
    name: str = Form(...),
    course: int = Form(...)
):
    """Update direction."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE directions SET name = ?, course = ? WHERE id = ?",
            (name, course, direction_id)
        )
        await conn.commit()
        logger.info(f"Updated direction #{direction_id}: {name}")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/directions', status_code=303)


@router.post('/{direction_id}/delete')
async def direction_delete(
    request: Request,
    direction_id: int,
    session: dict = Depends(get_current_session)
):
    """Delete direction (only if no users assigned)."""
    conn = await get_connection()
    try:
        # Check if there are users with this direction
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM users WHERE direction_id = ?",
            (direction_id,)
        )
        user_count = (await cursor.fetchone())[0]
        
        if user_count > 0:
            logger.warning(f"Cannot delete direction #{direction_id}: has {user_count} users")
            # Could add flash message here
        else:
            # Delete pair assignments first
            await conn.execute(
                "DELETE FROM pair_assignments WHERE direction_id = ?",
                (direction_id,)
            )
            await conn.execute(
                "DELETE FROM directions WHERE id = ?",
                (direction_id,)
            )
            await conn.commit()
            logger.info(f"Deleted direction #{direction_id}")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/directions', status_code=303)
