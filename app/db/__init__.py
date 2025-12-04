"""Database package."""

import os

# Determine which database backend to use
_use_postgres = bool(os.environ.get('DATABASE_URL'))

if _use_postgres:
    # Cloud deployment - use PostgreSQL via connection_cloud
    from .connection_cloud import (
        get_connection, 
        init_database,
        fetch_all,
        fetch_one,
        execute,
        execute_returning,
        release_connection,
        is_postgres
    )
else:
    # Local development - use SQLite
    from .connection import get_connection, init_database
    
    # Import helper functions from connection_cloud (SQLite fallback)
    from .connection_cloud import (
        fetch_all,
        fetch_one,
        execute,
        execute_returning,
        release_connection,
        is_postgres
    )

__all__ = [
    'get_connection', 
    'init_database',
    'fetch_all',
    'fetch_one',
    'execute',
    'execute_returning',
    'release_connection',
    'is_postgres'
]
