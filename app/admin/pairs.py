"""Admin pairs management routes."""

from typing import Optional
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import get_current_session
from app.db.connection import get_connection
from app.db.queries import (
    get_all_pairs,
    get_all_directions,
    get_pair_by_id,
    create_pair,
    update_pair,
    delete_pair
)
from app.db.models.pair import PairCreate
from app.utils.logger import logger
from app.utils.constants import WEEKDAY_NAMES, PAIR_TYPES

router = APIRouter(prefix='/admin/pairs', tags=['admin_pairs'])
templates = Jinja2Templates(directory='templates')


async def get_time_slots(conn):
    """Get all time slots."""
    cursor = await conn.execute(
        "SELECT id, slot_number, start_time, end_time FROM time_slots ORDER BY slot_number"
    )
    rows = await cursor.fetchall()
    return [{'id': r[0], 'slot_number': r[1], 'start_time': r[2], 'end_time': r[3]} for r in rows]


async def save_subject_and_teacher(conn, subject_name: str, teacher_name: str):
    """Save subject and teacher to autocomplete tables."""
    try:
        await conn.execute(
            "INSERT OR IGNORE INTO subjects (name) VALUES (?)",
            (subject_name,)
        )
        await conn.execute(
            "INSERT OR IGNORE INTO teachers (name) VALUES (?)",
            (teacher_name,)
        )
    except Exception as e:
        logger.warning(f"Failed to save autocomplete data: {e}")


@router.get('/api/subjects', response_class=JSONResponse)
async def get_subjects(session: dict = Depends(get_current_session)):
    """Get all subjects for autocomplete."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT name FROM subjects ORDER BY name")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        await conn.close()


@router.get('/api/teachers', response_class=JSONResponse)
async def get_teachers(session: dict = Depends(get_current_session)):
    """Get all teachers for autocomplete."""
    conn = await get_connection()
    try:
        cursor = await conn.execute("SELECT name FROM teachers ORDER BY name")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        await conn.close()


@router.get('', response_class=HTMLResponse)
async def pairs_list(
    request: Request,
    session: dict = Depends(get_current_session),
    direction_id: Optional[str] = None,
    weekday: Optional[str] = None,
    page: int = 1
):
    """
    Display list of all pairs with filters.
    
    Args:
        request: FastAPI request object
        direction_id: Optional filter by direction
        weekday: Optional filter by weekday (0=Monday, 6=Sunday)
        page: Page number for pagination
    
    Returns:
        Rendered pairs_list.html template
    """
    # Convert empty strings to None and parse integers
    direction_id_int: Optional[int] = int(direction_id) if direction_id and direction_id.strip() else None
    weekday_int: Optional[int] = int(weekday) if weekday and weekday.strip() else None
    
    conn = await get_connection()
    try:
        # Get all pairs
        cursor = await conn.execute(
            """
            SELECT 
                p.id,
                p.title,
                p.teacher,
                p.room,
                p.type,
                p.day_of_week,
                ts.start_time,
                ts.end_time,
                ts.slot_number,
                GROUP_CONCAT(d.name, ', ') as directions
            FROM pairs p
            JOIN time_slots ts ON p.time_slot_id = ts.id
            LEFT JOIN pair_assignments pa ON p.id = pa.pair_id
            LEFT JOIN directions d ON pa.direction_id = d.id
            GROUP BY p.id
            ORDER BY p.day_of_week, ts.slot_number
            """
        )
        all_pairs = await cursor.fetchall()
        
        # Apply filters
        pairs = []
        for row in all_pairs:
            # Filter by direction
            if direction_id_int is not None:
                cursor = await conn.execute(
                    """
                    SELECT COUNT(*) FROM pair_assignments
                    WHERE pair_id = ? AND direction_id = ?
                    """,
                    (row[0], direction_id_int)
                )
                count = (await cursor.fetchone())[0]
                if count == 0:
                    continue
            
            # Filter by weekday
            if weekday_int is not None and row[5] != weekday_int:
                continue
            
            pairs.append({
                'id': row[0],
                'subject_name': row[1],
                'teacher_name': row[2],
                'room': row[3],
                'pair_type': row[4],
                'day_of_week': row[5],
                'start_time': row[6],
                'end_time': row[7],
                'slot_number': row[8],
                'directions': row[9] or 'Нет назначений'
            })
        
        # Pagination
        per_page = 20
        total_pages = (len(pairs) + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_pairs = pairs[start_idx:end_idx]
        
        # Get all directions for filter dropdown
        directions_raw = await get_all_directions(conn)
        # Convert to list of dicts for template
        directions = [{'id': d.id, 'name': d.name, 'course': d.course} for d in directions_raw]
    finally:
        await conn.close()
    
    weekday_names = [
        'Понедельник', 'Вторник', 'Среда', 'Четверг',
        'Пятница', 'Суббота', 'Воскресенье'
    ]
    
    return templates.TemplateResponse(
        'pairs_list.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'pairs': paginated_pairs,
            'directions': directions,
            'weekday_names': weekday_names,
            'current_page': page,
            'total_pages': total_pages,
            'filters': {
                'direction_id': direction_id_int,
                'weekday': weekday_int
            }
        }
    )


@router.get('/new', response_class=HTMLResponse)
async def pair_new_form(
    request: Request,
    session: dict = Depends(get_current_session)
):
    """
    Display form for creating new pair.
    
    Args:
        request: FastAPI request object
    
    Returns:
        Rendered pair_form.html template
    """
    conn = await get_connection()
    try:
        # Get all directions grouped by course
        directions = await get_all_directions(conn)
        directions_by_course = {}
        for direction in directions:
            # Direction is a Pydantic model, access attributes with dot notation
            course = direction.course
            if course not in directions_by_course:
                directions_by_course[course] = []
            # Convert to dict for template
            directions_by_course[course].append({
                'id': direction.id,
                'name': direction.name,
                'course': direction.course
            })
        
        # Get time slots
        time_slots = await get_time_slots(conn)
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'pair_form.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'mode': 'create',
            'pair': None,
            'directions_by_course': directions_by_course,
            'time_slots': time_slots,
            'weekday_names': WEEKDAY_NAMES,
            'pair_types': PAIR_TYPES,
            'selected_directions': []
        }
    )


@router.post('/new')
async def pair_create(
    request: Request,
    session: dict = Depends(get_current_session),
    subject_name: str = Form(...),
    teacher_name: str = Form(...),
    room: str = Form(...),
    pair_type: str = Form(...),
    time_slot_id: int = Form(...),
    day_of_week: int = Form(...),
    extra_link: str = Form(""),
    direction_ids: list[int] = Form(...)
):
    """
    Create new pair.
    
    Args:
        request: FastAPI request object
        subject_name: Subject name (title)
        teacher_name: Teacher full name
        room: Room number
        pair_type: Type of pair (Лекция, Семинар, etc)
        time_slot_id: Time slot ID
        day_of_week: Day of week (0=Monday, 6=Sunday)
        extra_link: Optional link (Zoom, etc)
        direction_ids: List of direction IDs
    
    Returns:
        Redirect to pairs list
    """
    conn = await get_connection()
    try:
        # Create pair directly (without using PairCreate model for now)
        cursor = await conn.execute(
            """
            INSERT INTO pairs (title, teacher, room, type, time_slot_id, day_of_week, extra_link)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (subject_name, teacher_name, room, pair_type, time_slot_id, day_of_week, extra_link if extra_link else None)
        )
        pair_id = cursor.lastrowid
        
        # Create pair assignments
        for direction_id in direction_ids:
            await conn.execute(
                "INSERT INTO pair_assignments (pair_id, direction_id) VALUES (?, ?)",
                (pair_id, direction_id)
            )
        
        # Save subject and teacher for autocomplete
        await save_subject_and_teacher(conn, subject_name, teacher_name)
        
        await conn.commit()
        
        logger.info(f"Created pair #{pair_id}: {subject_name} for {len(direction_ids)} directions")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/pairs', status_code=303)


@router.get('/{pair_id}/edit', response_class=HTMLResponse)
async def pair_edit_form(
    request: Request,
    pair_id: int,
    session: dict = Depends(get_current_session)
):
    """
    Display form for editing existing pair.
    
    Args:
        request: FastAPI request object
        pair_id: Pair ID to edit
    
    Returns:
        Rendered pair_form.html template with pair data
    """
    conn = await get_connection()
    try:
        # Get pair data
        cursor = await conn.execute(
            """
            SELECT 
                id, title, teacher, room, type,
                time_slot_id, day_of_week, extra_link
            FROM pairs
            WHERE id = ?
            """,
            (pair_id,)
        )
        pair_row = await cursor.fetchone()
        
        if not pair_row:
            return RedirectResponse(url='/admin/pairs', status_code=303)
        
        pair = {
            'id': pair_row[0],
            'subject_name': pair_row[1],
            'teacher_name': pair_row[2],
            'room': pair_row[3],
            'pair_type': pair_row[4],
            'time_slot_id': pair_row[5],
            'day_of_week': pair_row[6],
            'extra_link': pair_row[7]
        }
        
        # Get assigned directions
        cursor = await conn.execute(
            "SELECT direction_id FROM pair_assignments WHERE pair_id = ?",
            (pair_id,)
        )
        selected_directions = [row[0] for row in await cursor.fetchall()]
        
        # Get all directions grouped by course
        directions = await get_all_directions(conn)
        directions_by_course = {}
        for direction in directions:
            # Direction is a Pydantic model, access attributes with dot notation
            course = direction.course
            if course not in directions_by_course:
                directions_by_course[course] = []
            # Convert to dict for template
            directions_by_course[course].append({
                'id': direction.id,
                'name': direction.name,
                'course': direction.course
            })
        
        # Get time slots
        time_slots = await get_time_slots(conn)
    finally:
        await conn.close()
    
    return templates.TemplateResponse(
        'pair_form.html',
        {
            'request': request,
            'username': session.get('username', 'admin'),
            'mode': 'edit',
            'pair': pair,
            'directions_by_course': directions_by_course,
            'time_slots': time_slots,
            'weekday_names': WEEKDAY_NAMES,
            'pair_types': PAIR_TYPES,
            'selected_directions': selected_directions
        }
    )


@router.post('/{pair_id}/edit')
async def pair_update(
    request: Request,
    pair_id: int,
    session: dict = Depends(get_current_session),
    subject_name: str = Form(...),
    teacher_name: str = Form(...),
    room: str = Form(...),
    pair_type: str = Form(...),
    time_slot_id: int = Form(...),
    day_of_week: int = Form(...),
    extra_link: str = Form(""),
    direction_ids: list[int] = Form(...)
):
    """
    Update existing pair.
    
    Args:
        request: FastAPI request object
        pair_id: Pair ID to update
        subject_name: Subject name (title)
        teacher_name: Teacher full name
        room: Room number
        pair_type: Type of pair
        time_slot_id: Time slot ID
        day_of_week: Day of week
        extra_link: Optional link
        direction_ids: List of direction IDs
    
    Returns:
        Redirect to pairs list
    """
    conn = await get_connection()
    try:
        # Update pair
        await conn.execute(
            """
            UPDATE pairs 
            SET title = ?, teacher = ?, room = ?, type = ?,
                time_slot_id = ?, day_of_week = ?, extra_link = ?,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (subject_name, teacher_name, room, pair_type, time_slot_id, 
             day_of_week, extra_link if extra_link else None, pair_id)
        )
        
        # Delete old assignments
        await conn.execute(
            "DELETE FROM pair_assignments WHERE pair_id = ?",
            (pair_id,)
        )
        
        # Create new assignments
        for direction_id in direction_ids:
            await conn.execute(
                "INSERT INTO pair_assignments (pair_id, direction_id) VALUES (?, ?)",
                (pair_id, direction_id)
            )
        
        # Save subject and teacher for autocomplete
        await save_subject_and_teacher(conn, subject_name, teacher_name)
        
        await conn.commit()
        
        logger.info(f"Updated pair #{pair_id}: {subject_name}")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/pairs', status_code=303)


@router.post('/{pair_id}/delete')
async def pair_delete(
    request: Request,
    pair_id: int,
    session: dict = Depends(get_current_session)
):
    """
    Delete pair (hard delete from database).
    
    Args:
        request: FastAPI request object
        pair_id: Pair ID to delete
    
    Returns:
        Redirect to pairs list
    """
    conn = await get_connection()
    try:
        # Delete pair assignments first (due to foreign key)
        await conn.execute(
            "DELETE FROM pair_assignments WHERE pair_id = ?",
            (pair_id,)
        )
        # Then delete the pair
        await conn.execute(
            "DELETE FROM pairs WHERE id = ?",
            (pair_id,)
        )
        await conn.commit()
        
        logger.info(f"Deleted pair #{pair_id}")
    finally:
        await conn.close()
    
    return RedirectResponse(url='/admin/pairs', status_code=303)
