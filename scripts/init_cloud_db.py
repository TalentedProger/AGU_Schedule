#!/usr/bin/env python3
"""
Database initialization script for cloud deployment.

Run this script after deploying to initialize the database schema
and seed initial data (time slots, directions).

Usage:
    python scripts/init_cloud_db.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_database, get_connection, is_postgres
from app.utils.logger import logger


async def seed_directions():
    """Seed initial directions for all courses."""
    conn = await get_connection()
    
    try:
        # Check if directions already exist
        if is_postgres():
            # For PostgreSQL wrapper
            cursor = await conn.execute("SELECT COUNT(*) as count FROM directions")
            row = await cursor.fetchone()
            count = row['count'] if row else 0
        else:
            # For SQLite
            async with conn.execute("SELECT COUNT(*) as count FROM directions") as cursor:
                row = await cursor.fetchone()
                count = row['count'] if row else 0
        
        if count > 0:
            logger.info(f"Directions already seeded ({count} found)")
            return
        
        # Seed directions for each course
        directions = [
            # Course 1
            (1, "Математика"),
            (1, "Мат. основы ИИ"),
            (1, "ИИ в мат. и IT"),
            (1, "ПМ"),
            (1, "МОАИС"),
            (1, "ИБ"),
            # Course 2
            (2, "Математика"),
            (2, "ПМ"),
            (2, "МОАИС"),
            (2, "ИБ"),
            # Course 3
            (3, "Математика"),
            (3, "ПМ"),
            (3, "МОАИС"),
            (3, "ИБ"),
            # Course 4
            (4, "Математика"),
            (4, "ПМ"),
            (4, "МОАИС"),
            (4, "ИБ"),
        ]
        
        for course, name in directions:
            await conn.execute(
                "INSERT INTO directions (course, name) VALUES (?, ?)",
                (course, name)
            )
        
        await conn.commit()
        logger.info(f"✓ Seeded {len(directions)} directions")
        
    except Exception as e:
        logger.error(f"Failed to seed directions: {e}")
        raise
    finally:
        await conn.close()


async def main():
    """Initialize database for cloud deployment."""
    print("=" * 50)
    print("AGU ScheduleBot - Database Initialization")
    print("=" * 50)
    
    # Detect database type
    if is_postgres():
        print("📦 Database: PostgreSQL (cloud)")
    else:
        print("📦 Database: SQLite (local)")
    
    print("\n1. Initializing database schema...")
    await init_database()
    
    print("\n2. Seeding initial directions...")
    await seed_directions()
    
    print("\n" + "=" * 50)
    print("✅ Database initialization complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
