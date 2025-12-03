"""
User database queries.

CRUD operations for users table.
"""

import aiosqlite
from typing import Optional, List
from datetime import datetime

from app.db.models.user import User, UserCreate


async def get_user_by_tg_id(conn: aiosqlite.Connection, tg_id: int) -> Optional[dict]:
    """
    Get user by Telegram ID.
    
    Args:
        conn: Database connection
        tg_id: Telegram user ID
    
    Returns:
        User dict or None if not found
    """
    async with conn.execute(
        """
        SELECT 
            u.*,
            d.name as direction_name
        FROM users u
        LEFT JOIN directions d ON u.direction_id = d.id
        WHERE u.tg_id = ?
        """,
        (tg_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


# Alias for consistency
async def get_user_by_telegram_id(conn: aiosqlite.Connection, tg_id: int) -> Optional[dict]:
    """Alias for get_user_by_tg_id."""
    return await get_user_by_tg_id(conn, tg_id)


async def create_user(conn: aiosqlite.Connection, user_data: UserCreate) -> int:
    """
    Create new user.
    
    Args:
        conn: Database connection
        user_data: User creation data
    
    Returns:
        ID of created user
    """
    cursor = await conn.execute(
        """
        INSERT INTO users (tg_id, name, course, direction_id, remind_before)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_data.tg_id, user_data.name, user_data.course, 
         user_data.direction_id, user_data.remind_before)
    )
    await conn.commit()
    return cursor.lastrowid


async def update_user_settings(
    conn: aiosqlite.Connection,
    tg_id: int,
    remind_before: Optional[bool] = None,
    paused_until: Optional[str] = None
) -> bool:
    """
    Update user settings.
    
    Args:
        conn: Database connection
        tg_id: Telegram user ID
        remind_before: Enable reminders
        paused_until: Pause until date (ISO format)
    
    Returns:
        True if updated successfully
    """
    updates = []
    params = []
    
    if remind_before is not None:
        updates.append("remind_before = ?")
        params.append(remind_before)
    
    if paused_until is not None:
        updates.append("paused_until = ?")
        params.append(paused_until)
    
    if not updates:
        return False
    
    updates.append("updated_at = ?")
    params.append(datetime.now().isoformat())
    
    params.append(tg_id)
    
    query = f"UPDATE users SET {', '.join(updates)} WHERE tg_id = ?"
    
    await conn.execute(query, params)
    await conn.commit()
    return True


async def update_user_direction(
    conn: aiosqlite.Connection,
    tg_id: int,
    course: int,
    direction_id: int
) -> bool:
    """
    Update user course and direction.
    
    Args:
        conn: Database connection
        tg_id: Telegram user ID
        course: New course number
        direction_id: New direction ID
    
    Returns:
        True if updated successfully
    """
    await conn.execute(
        """
        UPDATE users 
        SET course = ?, direction_id = ?, updated_at = ?
        WHERE tg_id = ?
        """,
        (course, direction_id, datetime.now().isoformat(), tg_id)
    )
    await conn.commit()
    return True


async def get_active_users(conn: aiosqlite.Connection) -> List[User]:
    """
    Get all active users (not paused).
    
    Args:
        conn: Database connection
    
    Returns:
        List of active users
    """
    async with conn.execute(
        """
        SELECT * FROM users 
        WHERE paused_until IS NULL OR paused_until < datetime('now')
        """
    ) as cursor:
        rows = await cursor.fetchall()
        return [User(**dict(row)) for row in rows]


async def get_users_by_direction(
    conn: aiosqlite.Connection,
    direction_id: int,
    active_only: bool = True
) -> List[User]:
    """
    Get users by direction ID.
    
    Args:
        conn: Database connection
        direction_id: Direction ID
        active_only: Only active users
    
    Returns:
        List of users
    """
    query = "SELECT * FROM users WHERE direction_id = ?"
    params = [direction_id]
    
    if active_only:
        query += " AND (paused_until IS NULL OR paused_until < datetime('now'))"
    
    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [User(**dict(row)) for row in rows]


async def delete_user(conn: aiosqlite.Connection, tg_id: int) -> bool:
    """
    Delete user by Telegram ID.
    
    Args:
        conn: Database connection
        tg_id: Telegram user ID
    
    Returns:
        True if deleted successfully
    """
    await conn.execute("DELETE FROM users WHERE tg_id = ?", (tg_id,))
    await conn.commit()
    return True
