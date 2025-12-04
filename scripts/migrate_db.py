"""
Database migration script.

Run this to update database schema to include payments table.
Safe to run multiple times - uses CREATE TABLE IF NOT EXISTS.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.connection_cloud import init_database
from app.utils.logger import logger


async def migrate():
    """Run database migration."""
    logger.info("Starting database migration...")
    
    try:
        await init_database()
        logger.info("✓ Migration completed successfully!")
        logger.info("  - All tables created/verified")
        logger.info("  - Payments table is now available")
        
    except Exception as e:
        logger.error(f"✗ Migration failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    print("=" * 50)
    print("AGU ScheduleBot - Database Migration")
    print("=" * 50)
    print()
    print("This will update your database schema to include:")
    print("  - payments table (for Telegram Stars donations)")
    print()
    print("Safe to run - uses CREATE IF NOT EXISTS")
    print()
    
    response = input("Continue? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        asyncio.run(migrate())
        print()
        print("✓ Migration complete!")
    else:
        print("Migration cancelled.")
