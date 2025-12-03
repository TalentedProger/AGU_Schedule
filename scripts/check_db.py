#!/usr/bin/env python3
"""Database verification script."""
import asyncio
import aiosqlite
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def check_database():
    """Verify database structure and data."""
    db_path = Path(__file__).parent.parent / "data" / "schedule.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"📂 Database: {db_path}")
    print("=" * 50)
    
    async with aiosqlite.connect(db_path) as db:
        # Check tables
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = await cursor.fetchall()
        print(f"\n📋 Tables ({len(tables)}):")
        for t in tables:
            print(f"   ✓ {t[0]}")
        
        # Check time_slots
        cursor = await db.execute("SELECT * FROM time_slots ORDER BY slot_number")
        slots = await cursor.fetchall()
        print(f"\n⏰ Time Slots ({len(slots)}):")
        for s in slots:
            print(f"   Пара {s[1]}: {s[2]} - {s[3]}")
        
        # Check directions
        cursor = await db.execute("SELECT * FROM directions ORDER BY course, name")
        directions = await cursor.fetchall()
        print(f"\n📚 Directions ({len(directions)}):")
        current_course = None
        for d in directions:
            if d[2] != current_course:
                current_course = d[2]
                print(f"\n   [{current_course} курс]")
            print(f"      - {d[1]}")
        
        # Check indexes
        cursor = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
        )
        indexes = await cursor.fetchall()
        print(f"\n🔍 Indexes ({len(indexes)}):")
        for i in indexes:
            print(f"   ✓ {i[0]}")
        
        # Check users count
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        users_count = (await cursor.fetchone())[0]
        print(f"\n👥 Users: {users_count}")
        
        # Check pairs count
        cursor = await db.execute("SELECT COUNT(*) FROM pairs")
        pairs_count = (await cursor.fetchone())[0]
        print(f"📅 Pairs: {pairs_count}")
        
        # Check delivery_log count
        cursor = await db.execute("SELECT COUNT(*) FROM delivery_log")
        logs_count = (await cursor.fetchone())[0]
        print(f"📝 Delivery Logs: {logs_count}")
        
        print("\n" + "=" * 50)
        print("✅ Database verification complete!")
        return True

if __name__ == "__main__":
    success = asyncio.run(check_database())
    sys.exit(0 if success else 1)
