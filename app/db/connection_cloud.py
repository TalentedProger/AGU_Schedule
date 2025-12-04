"""
Database connection management with PostgreSQL support.

Provides functions for connecting to SQLite (local) or PostgreSQL (cloud) database.
Maintains compatibility with existing SQLite-based queries.
"""

import os
from pathlib import Path
from typing import Union, Optional, Any, List
from contextlib import asynccontextmanager
from app.config import settings
from app.utils.logger import logger


def is_postgres() -> bool:
    """Check if we should use PostgreSQL instead of SQLite."""
    return bool(os.environ.get('DATABASE_URL'))


if is_postgres():
    # PostgreSQL mode (cloud deployment)
    import asyncpg
    
    _pool: Optional[asyncpg.Pool] = None
    
    def convert_query(query: str) -> str:
        """
        Convert SQLite query syntax to PostgreSQL.
        - ? placeholders to $1, $2, etc.
        - datetime('now') to NOW()
        - AUTOINCREMENT to SERIAL
        """
        # Convert ? placeholders
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
        
        query = ''.join(result)
        
        # Convert SQLite functions to PostgreSQL
        query = query.replace("datetime('now')", "NOW()")
        query = query.replace("AUTOINCREMENT", "")  # PostgreSQL uses SERIAL
        
        return query
    
    async def init_pool():
        """Initialize PostgreSQL connection pool."""
        global _pool
        if _pool is None:
            database_url = os.environ.get('DATABASE_URL')
            # Railway/Render use postgres://, asyncpg needs postgresql://
            if database_url and database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            _pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
            logger.info("PostgreSQL connection pool initialized")
        return _pool
    
    class PostgresConnectionWrapper:
        """
        Wrapper to make asyncpg connection compatible with aiosqlite interface.
        Allows existing SQLite-based code to work with PostgreSQL.
        """
        def __init__(self, conn: asyncpg.Connection):
            self._conn = conn
            self._in_transaction = False
        
        async def execute(self, query: str, params: tuple = ()) -> 'PostgresCursorWrapper':
            """Execute query and return cursor-like wrapper."""
            pg_query = convert_query(query)
            
            # Check if it's a SELECT query
            is_select = pg_query.strip().upper().startswith('SELECT')
            
            if is_select:
                rows = await self._conn.fetch(pg_query, *params)
                return PostgresCursorWrapper(rows)
            else:
                # For INSERT, UPDATE, DELETE
                result = await self._conn.execute(pg_query, *params)
                return PostgresCursorWrapper([], result)
        
        async def executescript(self, script: str):
            """Execute multiple SQL statements."""
            # Split by ; and execute each statement
            statements = [s.strip() for s in script.split(';') if s.strip()]
            for stmt in statements:
                if stmt:
                    try:
                        pg_stmt = convert_query(stmt)
                        await self._conn.execute(pg_stmt)
                    except Exception as e:
                        logger.warning(f"Script statement failed: {e}")
        
        async def commit(self):
            """Commit transaction (no-op for asyncpg with autocommit)."""
            pass
        
        async def close(self):
            """Close/release connection back to pool."""
            global _pool
            if _pool:
                await _pool.release(self._conn)
        
        @property
        def row_factory(self):
            """Compatibility property."""
            return None
        
        @row_factory.setter
        def row_factory(self, value):
            """Compatibility setter."""
            pass
    
    class PostgresCursorWrapper:
        """
        Wrapper to make asyncpg results compatible with aiosqlite cursor.
        """
        def __init__(self, rows: List[asyncpg.Record], result: str = None):
            self._rows = rows
            self._result = result
            self._index = 0
            self._lastrowid = None
            
            # Try to extract lastrowid from RETURNING clause result
            if rows and len(rows) > 0 and 'id' in rows[0]:
                self._lastrowid = rows[0]['id']
        
        @property
        def lastrowid(self) -> Optional[int]:
            """Get last inserted row ID."""
            return self._lastrowid
        
        async def fetchone(self) -> Optional[dict]:
            """Fetch one row."""
            if self._index < len(self._rows):
                row = self._rows[self._index]
                self._index += 1
                return dict(row)
            return None
        
        async def fetchall(self) -> List[dict]:
            """Fetch all rows."""
            return [dict(row) for row in self._rows]
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
    
    async def get_connection() -> PostgresConnectionWrapper:
        """Get async connection from PostgreSQL pool."""
        pool = await init_pool()
        conn = await pool.acquire()
        return PostgresConnectionWrapper(conn)
    
    async def release_connection(conn: PostgresConnectionWrapper):
        """Release connection back to pool."""
        await conn.close()
    
    # Helper functions for simpler queries
    async def fetch_all(query: str, params: tuple = ()) -> List[dict]:
        """Execute query and fetch all results."""
        pool = await init_pool()
        async with pool.acquire() as conn:
            pg_query = convert_query(query)
            rows = await conn.fetch(pg_query, *params)
            return [dict(row) for row in rows]
    
    async def fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
        """Execute query and fetch one result."""
        pool = await init_pool()
        async with pool.acquire() as conn:
            pg_query = convert_query(query)
            row = await conn.fetchrow(pg_query, *params)
            return dict(row) if row else None
    
    async def execute(query: str, params: tuple = ()):
        """Execute query without returning results."""
        pool = await init_pool()
        async with pool.acquire() as conn:
            pg_query = convert_query(query)
            return await conn.execute(pg_query, *params)
    
    async def execute_returning(query: str, params: tuple = ()) -> Optional[int]:
        """Execute query and return last inserted id."""
        pool = await init_pool()
        async with pool.acquire() as conn:
            pg_query = convert_query(query)
            # Add RETURNING id if not present for INSERT statements
            if 'INSERT' in pg_query.upper() and 'RETURNING' not in pg_query.upper():
                pg_query = pg_query.rstrip(';') + ' RETURNING id;'
            row = await conn.fetchrow(pg_query, *params)
            return row['id'] if row else None
    
    async def init_database():
        """Initialize PostgreSQL database schema."""
        pool = await init_pool()
        
        schema_sql = '''
        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            course INTEGER NOT NULL CHECK(course BETWEEN 1 AND 4),
            direction_id INTEGER NOT NULL,
            remind_before BOOLEAN NOT NULL DEFAULT TRUE,
            paused_until TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);
        CREATE INDEX IF NOT EXISTS idx_users_direction ON users(direction_id);
        
        -- Directions table
        CREATE TABLE IF NOT EXISTS directions (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            course INTEGER NOT NULL CHECK(course BETWEEN 1 AND 4),
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(name, course)
        );
        CREATE INDEX IF NOT EXISTS idx_directions_course ON directions(course);
        
        -- Time slots table
        CREATE TABLE IF NOT EXISTS time_slots (
            id SERIAL PRIMARY KEY,
            slot_number INTEGER NOT NULL UNIQUE CHECK(slot_number BETWEEN 1 AND 5),
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        
        -- Pairs table
        CREATE TABLE IF NOT EXISTS pairs (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            teacher TEXT NOT NULL,
            room TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'Лекция',
            day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),
            time_slot_id INTEGER NOT NULL REFERENCES time_slots(id),
            extra_link TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_pairs_day ON pairs(day_of_week);
        
        -- Pair assignments table
        CREATE TABLE IF NOT EXISTS pair_assignments (
            id SERIAL PRIMARY KEY,
            pair_id INTEGER NOT NULL REFERENCES pairs(id) ON DELETE CASCADE,
            direction_id INTEGER NOT NULL REFERENCES directions(id) ON DELETE CASCADE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(pair_id, direction_id)
        );
        
        -- Delivery log table
        CREATE TABLE IF NOT EXISTS delivery_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message_type TEXT NOT NULL,
            status TEXT NOT NULL,
            error_message TEXT,
            delivered_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_delivery_log_date ON delivery_log(delivered_at);
        
        -- Subjects table (for autocomplete)
        CREATE TABLE IF NOT EXISTS subjects (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        
        -- Teachers table (for autocomplete)
        CREATE TABLE IF NOT EXISTS teachers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
        '''
        
        async with pool.acquire() as conn:
            # Execute schema
            for statement in schema_sql.split(';'):
                statement = statement.strip()
                if statement:
                    try:
                        await conn.execute(statement)
                    except Exception as e:
                        # Ignore "already exists" errors
                        if 'already exists' not in str(e).lower():
                            logger.warning(f"Schema statement warning: {e}")
            
            # Seed time slots if empty
            count = await conn.fetchval("SELECT COUNT(*) FROM time_slots")
            if count == 0:
                await conn.execute('''
                    INSERT INTO time_slots (slot_number, start_time, end_time) VALUES
                    (1, '08:30', '10:00'),
                    (2, '10:10', '11:40'),
                    (3, '11:50', '13:20'),
                    (4, '14:00', '15:30'),
                    (5, '15:40', '17:10')
                ''')
                logger.info("Time slots seeded")
            
            logger.info("✓ PostgreSQL database initialized")

else:
    # SQLite mode (local development)
    import aiosqlite
    
    async def get_connection() -> aiosqlite.Connection:
        """Get async connection to SQLite database."""
        db_path = Path(settings.DATABASE_PATH)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = await aiosqlite.connect(settings.DATABASE_PATH)
        await conn.execute("PRAGMA encoding = 'UTF-8'")
        await conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = aiosqlite.Row
        
        return conn
    
    async def fetch_all(query: str, params: tuple = ()) -> List[dict]:
        """Execute query and fetch all results."""
        conn = await get_connection()
        try:
            async with conn.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
        """Execute query and fetch one result."""
        conn = await get_connection()
        try:
            async with conn.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        finally:
            await conn.close()
    
    async def execute(query: str, params: tuple = ()):
        """Execute query without returning results."""
        conn = await get_connection()
        try:
            await conn.execute(query, params)
            await conn.commit()
        finally:
            await conn.close()
    
    async def execute_returning(query: str, params: tuple = ()) -> Optional[int]:
        """Execute query and return last inserted id."""
        conn = await get_connection()
        try:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor.lastrowid
        finally:
            await conn.close()
    
    async def release_connection(conn: aiosqlite.Connection):
        """Close SQLite connection."""
        await conn.close()
    
    async def init_database():
        """Initialize SQLite database schema and seed data."""
        conn = await get_connection()
        
        try:
            schema_path = Path(__file__).parent / "schema.sql"
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            await conn.executescript(schema_sql)
            
            seed_path = Path(__file__).parent / "seed.sql"
            if seed_path.exists():
                with open(seed_path, 'r', encoding='utf-8') as f:
                    seed_sql = f.read()
                await conn.executescript(seed_sql)
            
            await conn.commit()
            logger.info("✓ SQLite database initialized")
            
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            raise
        finally:
            await conn.close()
