"""
Directions database queries.

CRUD operations for directions table.
"""

import aiosqlite
from typing import List, Optional

from app.db.models.direction import Direction, DirectionCreate


async def get_all_directions(conn: aiosqlite.Connection) -> List[Direction]:
    """
    Get all directions.
    
    Args:
        conn: Database connection
    
    Returns:
        List of all directions
    """
    async with conn.execute("SELECT * FROM directions ORDER BY course, name") as cursor:
        rows = await cursor.fetchall()
        return [Direction(**dict(row)) for row in rows]


async def get_directions_by_course(conn: aiosqlite.Connection, course: int) -> List[Direction]:
    """
    Get directions for specific course.
    
    Args:
        conn: Database connection
        course: Course number (1-4)
    
    Returns:
        List of directions for the course
    """
    async with conn.execute(
        "SELECT * FROM directions WHERE course = ? ORDER BY name", (course,)
    ) as cursor:
        rows = await cursor.fetchall()
        return [Direction(**dict(row)) for row in rows]


async def get_direction_by_id(conn: aiosqlite.Connection, direction_id: int) -> Optional[Direction]:
    """
    Get direction by ID.
    
    Args:
        conn: Database connection
        direction_id: Direction ID
    
    Returns:
        Direction object or None
    """
    async with conn.execute(
        "SELECT * FROM directions WHERE id = ?", (direction_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if row:
            return Direction(**dict(row))
        return None


async def create_direction(conn: aiosqlite.Connection, direction: DirectionCreate) -> int:
    """
    Create new direction.
    
    Args:
        conn: Database connection
        direction: Direction creation data
    
    Returns:
        ID of created direction
    """
    cursor = await conn.execute(
        "INSERT INTO directions (name, course) VALUES (?, ?)",
        (direction.name, direction.course)
    )
    await conn.commit()
    return cursor.lastrowid


async def update_direction(
    conn: aiosqlite.Connection,
    direction_id: int,
    name: str,
    course: int
) -> bool:
    """
    Update direction.
    
    Args:
        conn: Database connection
        direction_id: Direction ID
        name: New name
        course: New course
    
    Returns:
        True if updated
    """
    await conn.execute(
        "UPDATE directions SET name = ?, course = ? WHERE id = ?",
        (name, course, direction_id)
    )
    await conn.commit()
    return True


async def delete_direction(conn: aiosqlite.Connection, direction_id: int) -> bool:
    """
    Delete direction.
    
    Args:
        conn: Database connection
        direction_id: Direction ID
    
    Returns:
        True if deleted
    """
    await conn.execute("DELETE FROM directions WHERE id = ?", (direction_id,))
    await conn.commit()
    return True
