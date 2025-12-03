"""
Database backup utility.

Creates timestamped backups of the SQLite database.

Usage:
    python scripts/backup_db.py
    python scripts/backup_db.py --output /path/to/backup

Options:
    --output    Custom output directory for backups (default: backups/)
    --keep      Number of backups to keep (default: 7, oldest are deleted)
"""

import argparse
import shutil
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_db_path() -> str:
    """Get database path from environment or default."""
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("DATABASE_PATH", "data/schedule.db")


def create_backup(output_dir: str = "backups", keep: int = 7) -> str:
    """
    Create a timestamped backup of the database.
    
    Args:
        output_dir: Directory to store backups
        keep: Number of recent backups to keep
    
    Returns:
        Path to the created backup file
    """
    db_path = get_db_path()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = Path(db_path).stem
    backup_name = f"{db_name}_backup_{timestamp}.db"
    backup_path = output_path / backup_name
    
    # Copy database file
    print(f"📦 Creating backup...")
    print(f"   Source: {db_path}")
    print(f"   Destination: {backup_path}")
    
    try:
        shutil.copy2(db_path, backup_path)
        
        # Get file size
        size_mb = os.path.getsize(backup_path) / (1024 * 1024)
        print(f"✅ Backup created successfully ({size_mb:.2f} MB)")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        sys.exit(1)
    
    # Cleanup old backups
    if keep > 0:
        cleanup_old_backups(output_path, db_name, keep)
    
    return str(backup_path)


def cleanup_old_backups(output_dir: Path, db_name: str, keep: int):
    """
    Remove old backups, keeping only the most recent ones.
    
    Args:
        output_dir: Directory containing backups
        db_name: Database name prefix
        keep: Number of backups to keep
    """
    # Find all backups
    pattern = f"{db_name}_backup_*.db"
    backups = list(output_dir.glob(pattern))
    
    # Sort by modification time (newest first)
    backups.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # Remove old backups
    if len(backups) > keep:
        old_backups = backups[keep:]
        print(f"🗑️  Cleaning up {len(old_backups)} old backup(s)...")
        
        for backup in old_backups:
            try:
                backup.unlink()
                print(f"   Deleted: {backup.name}")
            except Exception as e:
                print(f"   ⚠️ Failed to delete {backup.name}: {e}")


def list_backups(output_dir: str = "backups"):
    """List all existing backups."""
    output_path = Path(output_dir)
    
    if not output_path.exists():
        print("No backups found.")
        return
    
    backups = list(output_path.glob("*_backup_*.db"))
    
    if not backups:
        print("No backups found.")
        return
    
    # Sort by modification time
    backups.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    print(f"\n📁 Backups in {output_dir}/:")
    print("-" * 60)
    
    for backup in backups:
        stat = backup.stat()
        size_mb = stat.st_size / (1024 * 1024)
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        print(f"  {backup.name} ({size_mb:.2f} MB) - {mtime}")
    
    print("-" * 60)
    print(f"Total: {len(backups)} backup(s)")


def restore_backup(backup_path: str, force: bool = False):
    """
    Restore database from backup.
    
    Args:
        backup_path: Path to backup file
        force: Overwrite existing database without prompt
    """
    if not os.path.exists(backup_path):
        print(f"❌ Backup not found: {backup_path}")
        sys.exit(1)
    
    db_path = get_db_path()
    
    if os.path.exists(db_path) and not force:
        response = input(f"⚠️ Database exists at {db_path}. Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("Restore cancelled.")
            return
    
    # Create backup of current database before restore
    if os.path.exists(db_path):
        pre_restore_backup = f"{db_path}.pre_restore"
        print(f"📦 Backing up current database to {pre_restore_backup}")
        shutil.copy2(db_path, pre_restore_backup)
    
    # Restore from backup
    print(f"🔄 Restoring from {backup_path}...")
    
    try:
        shutil.copy2(backup_path, db_path)
        print(f"✅ Database restored successfully!")
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AGU ScheduleBot Database Backup Utility"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create backup command
    create_parser = subparsers.add_parser("create", help="Create a new backup")
    create_parser.add_argument(
        "--output", "-o",
        default="backups",
        help="Output directory for backups (default: backups/)"
    )
    create_parser.add_argument(
        "--keep", "-k",
        type=int,
        default=7,
        help="Number of backups to keep (default: 7, 0 = keep all)"
    )
    
    # List backups command
    list_parser = subparsers.add_parser("list", help="List existing backups")
    list_parser.add_argument(
        "--dir", "-d",
        default="backups",
        help="Backups directory (default: backups/)"
    )
    
    # Restore backup command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument(
        "backup_file",
        help="Path to backup file"
    )
    restore_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force overwrite without prompt"
    )
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_backup(output_dir=args.output, keep=args.keep)
    elif args.command == "list":
        list_backups(output_dir=args.dir)
    elif args.command == "restore":
        restore_backup(args.backup_file, force=args.force)
    else:
        # Default action: create backup
        create_backup()


if __name__ == "__main__":
    main()
