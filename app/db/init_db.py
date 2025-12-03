"""
Database initialization script.

Run this script to create database schema and seed initial data.

Usage:
    python -m app.db.init_db
"""

import asyncio
from app.db import init_database


async def main():
    """Initialize database."""
    print("Initializing database...")
    await init_database()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
