"""
Database connection management.

Provides functions for connecting to SQLite database with proper configuration.
"""

import aiosqlite
from pathlib import Path
from app.config import settings


async def get_connection() -> aiosqlite.Connection:
    """
    Get async connection to SQLite database.
    
    Returns:
        aiosqlite.Connection: Connected database instance
    """
    # Ensure database directory exists
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect with UTF-8 encoding
    conn = await aiosqlite.connect(settings.DATABASE_PATH)
    await conn.execute("PRAGMA encoding = 'UTF-8'")
    await conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    conn.row_factory = aiosqlite.Row  # Access rows as dictionaries
    
    return conn


async def init_database():
    """
    Initialize database schema and seed data.
    
    Runs schema.sql and seed.sql to create tables and insert initial data.
    """
    conn = await get_connection()
    
    try:
        # Read and execute schema
        schema_path = Path(__file__).parent / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        await conn.executescript(schema_sql)
        
        # Read and execute seed data
        seed_path = Path(__file__).parent / "seed.sql"
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_sql = f.read()
        
        await conn.executescript(seed_sql)
        
        await conn.commit()
        print("✓ Database initialized successfully")
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        raise
    finally:
        await conn.close()
