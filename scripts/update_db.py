"""Database update script - updates time slots and creates new tables."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'schedule.db')

def update_database():
    """Update database with correct time slots and new tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Updating database...")
    
    # 1. Update time slots to correct AGU times
    print("\n📅 Updating time slots...")
    time_slots = [
        (1, '09:00', '10:45'),
        (2, '10:45', '12:20'),
        (3, '13:00', '14:35'),
        (4, '14:45', '16:20'),
        (5, '16:30', '18:05'),
    ]
    
    for slot_number, start_time, end_time in time_slots:
        cursor.execute(
            """
            UPDATE time_slots 
            SET start_time = ?, end_time = ?
            WHERE slot_number = ?
            """,
            (start_time, end_time, slot_number)
        )
        print(f"  Пара {slot_number}: {start_time} - {end_time}")
    
    # 2. Create subjects table for autocomplete
    print("\n📚 Creating subjects table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name)")
    
    # 3. Create teachers table for autocomplete
    print("👨‍🏫 Creating teachers table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachers_name ON teachers(name)")
    
    # 4. Populate subjects and teachers from existing pairs
    print("\n📝 Populating autocomplete data from existing pairs...")
    
    cursor.execute("SELECT DISTINCT title FROM pairs WHERE title IS NOT NULL")
    subjects = cursor.fetchall()
    for (subject,) in subjects:
        try:
            cursor.execute("INSERT OR IGNORE INTO subjects (name) VALUES (?)", (subject,))
        except:
            pass
    print(f"  Added {len(subjects)} subjects")
    
    cursor.execute("SELECT DISTINCT teacher FROM pairs WHERE teacher IS NOT NULL")
    teachers = cursor.fetchall()
    for (teacher,) in teachers:
        try:
            cursor.execute("INSERT OR IGNORE INTO teachers (name) VALUES (?)", (teacher,))
        except:
            pass
    print(f"  Added {len(teachers)} teachers")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database updated successfully!")

if __name__ == '__main__':
    update_database()
