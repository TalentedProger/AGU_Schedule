"""
Pairs (schedule) database queries.

CRUD operations for pairs and pair_assignments tables.
"""

import aiosqlite
from typing import List, Optional, Tuple
from datetime import datetime

from app.db.models.pair import Pair, PairCreate


async def get_pairs_by_direction_and_day(
    conn: aiosqlite.Connection,
    direction_id: int,
    day_of_week: int
) -> List[Tuple[Pair, str, str]]:
    """
    Get pairs for specific direction and day with time slot info.
    
    Args:
        conn: Database connection
        direction_id: Direction ID
        day_of_week: Day of week (0=Monday)
    
    Returns:
        List of tuples (Pair, start_time, end_time)
    """
    query = """
    SELECT p.*, ts.start_time, ts.end_time
    FROM pairs p
    JOIN pair_assignments pa ON p.id = pa.pair_id
    JOIN time_slots ts ON p.time_slot_id = ts.id
    WHERE pa.direction_id = ? AND p.day_of_week = ?
    ORDER BY ts.slot_number
    """
    
    async with conn.execute(query, (direction_id, day_of_week)) as cursor:
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            row_dict = dict(row)
            start_time = row_dict.pop('start_time')
            end_time = row_dict.pop('end_time')
            pair = Pair(**row_dict)
            result.append((pair, start_time, end_time))
        return result


async def get_all_pairs(conn: aiosqlite.Connection) -> List[Pair]:
    """
    Get all pairs.
    
    Args:
        conn: Database connection
    
    Returns:
        List of all pairs
    """
    async with conn.execute(
        "SELECT * FROM pairs ORDER BY day_of_week, time_slot_id"
    ) as cursor:
        rows = await cursor.fetchall()
        return [Pair(**dict(row)) for row in rows]


async def get_pair_by_id(conn: aiosqlite.Connection, pair_id: int) -> Optional[Pair]:
    """
    Get pair by ID.
    
    Args:
        conn: Database connection
        pair_id: Pair ID
    
    Returns:
        Pair object or None
    """
    async with conn.execute("SELECT * FROM pairs WHERE id = ?", (pair_id,)) as cursor:
        row = await cursor.fetchone()
        if row:
            return Pair(**dict(row))
        return None


async def create_pair(
    conn: aiosqlite.Connection,
    pair_data: PairCreate,
    direction_ids: List[int]
) -> int:
    """
    Create new pair and assign to directions.
    
    Args:
        conn: Database connection
        pair_data: Pair creation data
        direction_ids: List of direction IDs to assign
    
    Returns:
        ID of created pair
    """
    # Create pair
    cursor = await conn.execute(
        """
        INSERT INTO pairs (title, teacher, room, type, day_of_week, time_slot_id, extra_link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (pair_data.title, pair_data.teacher, pair_data.room, pair_data.type,
         pair_data.day_of_week, pair_data.time_slot_id, pair_data.extra_link)
    )
    pair_id = cursor.lastrowid
    
    # Create assignments
    for direction_id in direction_ids:
        await conn.execute(
            "INSERT INTO pair_assignments (pair_id, direction_id) VALUES (?, ?)",
            (pair_id, direction_id)
        )
    
    await conn.commit()
    return pair_id


async def update_pair(
    conn: aiosqlite.Connection,
    pair_id: int,
    pair_data: PairCreate,
    direction_ids: Optional[List[int]] = None
) -> bool:
    """
    Update pair and optionally reassign directions.
    
    Args:
        conn: Database connection
        pair_id: Pair ID
        pair_data: Updated pair data
        direction_ids: New direction IDs (if None, keep existing)
    
    Returns:
        True if updated
    """
    # Update pair
    await conn.execute(
        """
        UPDATE pairs 
        SET title = ?, teacher = ?, room = ?, type = ?, 
            day_of_week = ?, time_slot_id = ?, extra_link = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (pair_data.title, pair_data.teacher, pair_data.room, pair_data.type,
         pair_data.day_of_week, pair_data.time_slot_id, pair_data.extra_link,
         datetime.now().isoformat(), pair_id)
    )
    
    # Update assignments if provided
    if direction_ids is not None:
        # Delete old assignments
        await conn.execute("DELETE FROM pair_assignments WHERE pair_id = ?", (pair_id,))
        
        # Create new assignments
        for direction_id in direction_ids:
            await conn.execute(
                "INSERT INTO pair_assignments (pair_id, direction_id) VALUES (?, ?)",
                (pair_id, direction_id)
            )
    
    await conn.commit()
    return True


async def delete_pair(conn: aiosqlite.Connection, pair_id: int) -> bool:
    """
    Delete pair (assignments deleted automatically by CASCADE).
    
    Args:
        conn: Database connection
        pair_id: Pair ID
    
    Returns:
        True if deleted
    """
    await conn.execute("DELETE FROM pairs WHERE id = ?", (pair_id,))
    await conn.commit()
    return True


async def get_pair_directions(conn: aiosqlite.Connection, pair_id: int) -> List[int]:
    """
    Get direction IDs assigned to pair.
    
    Args:
        conn: Database connection
        pair_id: Pair ID
    
    Returns:
        List of direction IDs
    """
    async with conn.execute(
        "SELECT direction_id FROM pair_assignments WHERE pair_id = ?",
        (pair_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
