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

from app.db import init_database, get_connection, is_postgres, release_connection
from app.utils.logger import logger


def convert_query_local(query: str) -> str:
    """
    Convert SQLite query syntax to PostgreSQL.
    Local copy to avoid circular import issues.
    """
    result = []
    param_count = 0
    i = 0
    while i < len(query):
        if query[i] == '?':
            param_count += 1
            result.append(f'${param_count}')
        else:
            result.append(query[i])
        i += 1
    return ''.join(result)


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
            query = "INSERT INTO directions (course, name) VALUES (?, ?)"
            if is_postgres():
                query = convert_query_local(query)
            await conn.execute(query, (course, name))
        
        await conn.commit()
        logger.info(f"✓ Seeded {len(directions)} directions")
        
    except Exception as e:
        logger.error(f"Failed to seed directions: {e}")
        raise
    finally:
        await release_connection(conn)


async def check_if_initialized() -> bool:
    """
    Check if database is already initialized by checking for existing data.
    Returns True if database has data, False otherwise.
    """
    try:
        conn = await get_connection()
        try:
            # Check if users table has data
            if is_postgres():
                cursor = await conn.execute("SELECT COUNT(*) as count FROM users")
                row = await cursor.fetchone()
                user_count = row['count'] if row else 0
            else:
                async with conn.execute("SELECT COUNT(*) as count FROM users") as cursor:
                    row = await cursor.fetchone()
                    user_count = row['count'] if row else 0
            
            # Check if pairs table has data
            if is_postgres():
                cursor = await conn.execute("SELECT COUNT(*) as count FROM pairs")
                row = await cursor.fetchone()
                pair_count = row['count'] if row else 0
            else:
                async with conn.execute("SELECT COUNT(*) as count FROM pairs") as cursor:
                    row = await cursor.fetchone()
                    pair_count = row['count'] if row else 0
            
            return user_count > 0 or pair_count > 0
        finally:
            await release_connection(conn)
    except Exception as e:
        # If tables don't exist, that's fine - we'll create them
        logger.debug(f"Could not check initialization status: {e}")
        return False


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
    
    # ВАЖНО: Проверяем существуют ли уже данные
    print("\n🔍 Checking if database is already initialized...")
    has_data = await check_if_initialized()
    
    if has_data:
        print("✅ Database already has data - SKIPPING initialization")
        print("   This preserves existing users and pairs!")
        print("\n⚠️  If you need to reinitialize, manually clear the database first")
        print("\n" + "=" * 50)
        print("✅ Database check complete - existing data preserved!")
        print("=" * 50)
        return
    
    print("\n1. Initializing database schema...")
    await init_database()
    
    print("\n2. Seeding initial directions...")
    await seed_directions()
    
    print("\n" + "=" * 50)
    print("✅ Database initialization complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
