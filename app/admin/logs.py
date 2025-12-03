"""Admin panel delivery logs routes."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.admin.auth import get_current_session
from app.db.connection import get_connection
from app.utils.logger import logger
from app.utils.timezone import get_current_time_msk

router = APIRouter(prefix='/admin/logs', tags=['admin', 'logs'])
templates = Jinja2Templates(directory='templates')


@router.get('', response_class=HTMLResponse)
async def logs_page(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=100),
    message_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    session: dict = Depends(get_current_session)
):
    """
    Display delivery logs with filters and pagination.
    
    Args:
        request: FastAPI request object
        page: Current page number (1-indexed)
        per_page: Items per page (default 50)
        message_type: Filter by type ('morning', 'reminder', 'broadcast')
        status: Filter by status ('sent', 'error')
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        session: Current session
    
    Returns:
        Rendered logs.html template
    """
    conn = await get_connection()
    try:
        # Build WHERE clause with filters
        conditions = []
        params = []
        
        if message_type and message_type in ('morning', 'reminder', 'broadcast'):
            conditions.append("dl.message_type = ?")
            params.append(message_type)
        
        if status and status in ('sent', 'error'):
            conditions.append("dl.status = ?")
            params.append(status)
        
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                conditions.append("dl.delivered_at >= ?")
                params.append(date_from_dt.isoformat())
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                # Add one day to include the entire end date
                date_to_dt = date_to_dt + timedelta(days=1)
                conditions.append("dl.delivered_at < ?")
                params.append(date_to_dt.isoformat())
            except ValueError:
                pass
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Get total count for pagination
        count_query = f"""
            SELECT COUNT(*) FROM delivery_log dl
            {where_clause}
        """
        cursor = await conn.execute(count_query, params)
        row = await cursor.fetchone()
        total_count = row[0] if row else 0
        
        # Calculate pagination
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        page = min(page, total_pages)  # Ensure page is within bounds
        offset = (page - 1) * per_page
        
        # Fetch logs with pagination
        query = f"""
            SELECT 
                dl.id,
                dl.delivered_at,
                dl.message_type,
                dl.status,
                dl.error_message,
                u.id as user_id,
                u.tg_id,
                u.name as user_name,
                d.name as direction_name,
                d.course
            FROM delivery_log dl
            LEFT JOIN users u ON dl.user_id = u.id
            LEFT JOIN directions d ON u.direction_id = d.id
            {where_clause}
            ORDER BY dl.delivered_at DESC
            LIMIT ? OFFSET ?
        """
        cursor = await conn.execute(query, params + [per_page, offset])
        rows = await cursor.fetchall()
        
        # Format logs
        logs = []
        for row in rows:
            try:
                delivery_time = datetime.fromisoformat(row[1]).strftime('%d.%m.%Y %H:%M:%S')
            except (ValueError, TypeError):
                delivery_time = str(row[1]) if row[1] else 'N/A'
            
            logs.append({
                'id': row[0],
                'delivery_time': delivery_time,
                'message_type': row[2],
                'status': row[3],
                'error_message': row[4],
                'user_id': row[5],
                'tg_id': row[6],
                'user_name': row[7] or 'Удалён',
                'direction_name': row[8] or 'N/A',
                'course': row[9] or 'N/A'
            })
        
        # Get statistics for filters display
        stats_query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors,
                SUM(CASE WHEN message_type = 'morning' THEN 1 ELSE 0 END) as morning,
                SUM(CASE WHEN message_type = 'reminder' THEN 1 ELSE 0 END) as reminder,
                SUM(CASE WHEN message_type = 'broadcast' THEN 1 ELSE 0 END) as broadcast
            FROM delivery_log
        """
        cursor = await conn.execute(stats_query)
        stats_row = await cursor.fetchone()
        
        stats = {
            'total': stats_row[0] or 0,
            'sent': stats_row[1] or 0,
            'errors': stats_row[2] or 0,
            'morning': stats_row[3] or 0,
            'reminder': stats_row[4] or 0,
            'broadcast': stats_row[5] or 0
        }
        
        # Build pagination info
        pagination = {
            'page': page,
            'per_page': per_page,
            'total_count': total_count,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'pages': list(range(max(1, page - 2), min(total_pages + 1, page + 3)))
        }
        
        # Current filters for template
        filters = {
            'message_type': message_type or '',
            'status': status or '',
            'date_from': date_from or '',
            'date_to': date_to or ''
        }
        
        return templates.TemplateResponse(
            'logs.html',
            {
                'request': request,
                'username': session.get('username', 'admin'),
                'logs': logs,
                'stats': stats,
                'pagination': pagination,
                'filters': filters
            }
        )
    finally:
        await conn.close()


@router.get('/export')
async def export_logs(
    message_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    session: dict = Depends(get_current_session)
):
    """
    Export logs as CSV file.
    
    Args:
        message_type: Filter by type
        status: Filter by status
        date_from: Start date filter
        date_to: End date filter
        session: Current session
    
    Returns:
        CSV file download
    """
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    
    conn = await get_connection()
    try:
        # Build WHERE clause with filters
        conditions = []
        params = []
        
        if message_type and message_type in ('morning', 'reminder', 'broadcast'):
            conditions.append("dl.message_type = ?")
            params.append(message_type)
        
        if status and status in ('sent', 'error'):
            conditions.append("dl.status = ?")
            params.append(status)
        
        if date_from:
            try:
                date_from_dt = datetime.fromisoformat(date_from)
                conditions.append("dl.delivered_at >= ?")
                params.append(date_from_dt.isoformat())
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_dt = datetime.fromisoformat(date_to)
                date_to_dt = date_to_dt + timedelta(days=1)
                conditions.append("dl.delivered_at < ?")
                params.append(date_to_dt.isoformat())
            except ValueError:
                pass
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Fetch all logs matching filters
        query = f"""
            SELECT 
                dl.id,
                dl.delivered_at,
                dl.message_type,
                dl.status,
                dl.error_message,
                u.tg_id,
                u.name as user_name,
                d.name as direction_name,
                d.course
            FROM delivery_log dl
            LEFT JOIN users u ON dl.user_id = u.id
            LEFT JOIN directions d ON u.direction_id = d.id
            {where_clause}
            ORDER BY dl.delivered_at DESC
        """
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Дата', 'Тип', 'Статус', 'Ошибка',
            'Telegram ID', 'Имя', 'Направление', 'Курс'
        ])
        
        # Write rows
        for row in rows:
            writer.writerow([
                row[0],
                row[1],
                row[2],
                row[3],
                row[4] or '',
                row[5] or '',
                row[6] or 'Удалён',
                row[7] or 'N/A',
                row[8] or 'N/A'
            ])
        
        output.seek(0)
        
        # Generate filename with current date
        filename = f"delivery_logs_{get_current_time_msk().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    finally:
        await conn.close()
