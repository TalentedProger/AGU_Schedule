"""Admin time slots management routes."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import get_current_session
from app.db.connection import get_connection
from app.utils.logger import logger

router = APIRouter(prefix='/admin/slots', tags=['admin_slots'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
async def slots_list(
    request: Request,
    session: dict = Depends(get_current_session)
):
    """Display list of all time slots."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            """
            SELECT ts.id, ts.slot_number, ts.start_time, ts.end_time,
                   (SELECT COUNT(*) FROM pairs WHERE time_slot_id = ts.id) as pair_count
            FROM time_slots ts
            ORDER BY ts.slot_number
            """
        )
        rows = await cursor.fetchall()
        slots = [
            {
                'id': r[0], 
                'slot_number': r[1], 
                'start_time': r[2], 
                'end_time': r[3],
                'pair_count': r[4]
            }
            for r in rows
        ]
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'slots_list.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'slots': slots
        }
    )


@router.get('/{slot_id}/edit', response_class=HTMLResponse)
async def slot_edit_form(
    request: Request,
    slot_id: int,
    session: dict = Depends(get_current_session)
):
    """Display form for editing time slot."""
    conn = await get_connection()
    try:
        cursor = await conn.execute(
            "SELECT id, slot_number, start_time, end_time FROM time_slots WHERE id = ?",
            (slot_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return RedirectResponse(url='/admin/slots', status_code=303)
        
        slot = {
            'id': row[0], 
            'slot_number': row[1], 
            'start_time': row[2], 
            'end_time': row[3]
        }
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'slot_form.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'slot': slot
        }
    )


@router.post('/{slot_id}/edit')
async def slot_update(
    request: Request,
    slot_id: int,
    session: dict = Depends(get_current_session),
    start_time: str = Form(...),
    end_time: str = Form(...)
):
    """Update time slot."""
    conn = await get_connection()
    try:
        await conn.execute(
            "UPDATE time_slots SET start_time = ?, end_time = ? WHERE id = ?",
            (start_time, end_time, slot_id)
        )
        await conn.commit()
        logger.info(f"Updated time slot #{slot_id}: {start_time} - {end_time}")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/slots', status_code=303)
