#!/usr/bin/env python3
"""
Final deployment readiness check script.
Verifies all components are working correctly before deployment.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def check_all():
    """Run all checks."""
    print("=" * 60)
    print("🚀 AGU ScheduleBot - Deployment Readiness Check")
    print("=" * 60)
    
    all_passed = True
    
    # 1. Check database
    print("\n📊 1. Database Check...")
    try:
        import aiosqlite
        db_path = Path(__file__).parent.parent / "data" / "schedule.db"
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM time_slots")
            slots = (await cursor.fetchone())[0]
            cursor = await db.execute("SELECT COUNT(*) FROM directions")
            directions = (await cursor.fetchone())[0]
            
            if slots == 5 and directions >= 10:
                print(f"   ✅ Database OK: {slots} time slots, {directions} directions")
            else:
                print(f"   ❌ Database issue: {slots} time slots, {directions} directions")
                all_passed = False
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        all_passed = False
    
    # 2. Check config
    print("\n⚙️ 2. Configuration Check...")
    try:
        from app.config import settings
        checks = [
            ("BOT_TOKEN", bool(settings.BOT_TOKEN)),
            ("ADMIN_TG_ID", settings.ADMIN_TG_ID > 0),
            ("ADMIN_PASSWORD", len(settings.ADMIN_PASSWORD) >= 8),
            ("SECRET_KEY", len(settings.SECRET_KEY) >= 32),
            ("TIMEZONE", settings.TIMEZONE == "Europe/Moscow"),
        ]
        for name, valid in checks:
            if valid:
                print(f"   ✅ {name}: OK")
            else:
                print(f"   ❌ {name}: Invalid")
                all_passed = False
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        all_passed = False
    
    # 3. Check bot imports
    print("\n🤖 3. Bot Modules Check...")
    try:
        from app.bot.handlers import start, registration, settings, common
        from app.scheduler.scheduler import setup_scheduler
        from app.scheduler.jobs.morning_message import morning_schedule_job
        from app.scheduler.jobs.reminders import reminder_job
        print("   ✅ All bot modules import successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        all_passed = False
    
    # 4. Check admin imports
    print("\n🖥️ 4. Admin Panel Modules Check...")
    try:
        from app.admin.routes import router as admin_router
        from app.admin.pairs import router as pairs_router
        from app.admin.directions import router as directions_router
        from app.admin.slots import router as slots_router
        from app.admin.broadcast import router as broadcast_router
        from app.admin.logs import router as logs_router
        print("   ✅ All admin modules import successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        all_passed = False
    
    # 5. Check templates
    print("\n📄 5. Templates Check...")
    template_dir = Path(__file__).parent.parent / "templates"
    required_templates = [
        "base.html", "login.html", "dashboard.html",
        "pairs_list.html", "pair_form.html",
        "directions_list.html", "direction_form.html",
        "slots_list.html", "slot_form.html",
        "broadcast.html", "logs.html",
        "errors/404.html", "errors/500.html"
    ]
    missing = []
    for t in required_templates:
        if not (template_dir / t).exists():
            missing.append(t)
    
    if not missing:
        print(f"   ✅ All {len(required_templates)} templates present")
    else:
        print(f"   ❌ Missing templates: {', '.join(missing)}")
        all_passed = False
    
    # 6. Check deploy files
    print("\n📦 6. Deployment Files Check...")
    deploy_dir = Path(__file__).parent.parent / "deploy"
    required_deploy = [
        "schedulebot.service",
        "schedulebot-admin.service",
        "nginx.conf",
        "install.sh"
    ]
    missing = []
    for f in required_deploy:
        if not (deploy_dir / f).exists():
            missing.append(f)
    
    if not missing:
        print(f"   ✅ All {len(required_deploy)} deployment files present")
    else:
        print(f"   ❌ Missing deploy files: {', '.join(missing)}")
        all_passed = False
    
    # 7. Check scripts
    print("\n🔧 7. Utility Scripts Check...")
    scripts_dir = Path(__file__).parent
    required_scripts = ["backup_db.py", "check_db.py", "check_scheduler.py"]
    missing = []
    for s in required_scripts:
        if not (scripts_dir / s).exists():
            missing.append(s)
    
    if not missing:
        print(f"   ✅ All {len(required_scripts)} utility scripts present")
    else:
        print(f"   ❌ Missing scripts: {', '.join(missing)}")
        all_passed = False
    
    # 8. Check documentation
    print("\n📚 8. Documentation Check...")
    docs_dir = Path(__file__).parent.parent / "Docs"
    required_docs = [
        "Implementation.md", "PRD.md", "TechStack.md",
        "DEPLOYMENT.md", "USER_GUIDE.md", "ADMIN_GUIDE.md"
    ]
    missing = []
    for d in required_docs:
        if not (docs_dir / d).exists():
            missing.append(d)
    
    if not missing:
        print(f"   ✅ All {len(required_docs)} documentation files present")
    else:
        print(f"   ❌ Missing docs: {', '.join(missing)}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED - PROJECT READY FOR DEPLOYMENT!")
    else:
        print("❌ SOME CHECKS FAILED - Please fix issues before deployment")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(check_all())
    sys.exit(0 if success else 1)
