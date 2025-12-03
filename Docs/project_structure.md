# Project Structure - ScheduleBot

**Version:** 1.0  
**Date:** 03.12.2025  
**Project:** AGU Schedule Telegram Bot + Admin Panel

---

## Table of Contents

1. [Complete Directory Hierarchy](#complete-directory-hierarchy)
2. [File Naming Conventions](#file-naming-conventions)
3. [Module Organization Patterns](#module-organization-patterns)
4. [Configuration Structure](#configuration-structure)
5. [Development vs Production](#development-vs-production)

---

## Complete Directory Hierarchy

```
AGU_Schedule/
│
├── .env                        # Environment variables (NEVER commit)
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── README.md                   # Project overview and setup guide
│
├── Docs/                       # Project documentation
│   ├── PRD.md                  # Product Requirements Document
│   ├── AppMap.md               # Application Architecture Map
│   ├── TechStack.md            # Technology Stack Documentation
│   ├── Implementation.md       # Implementation Plan (this file)
│   ├── project_structure.md    # Project Structure (current file)
│   ├── UI_UX_doc.md            # UI/UX Design System
│   ├── Bug_tracking.md         # Bug tracking and resolution log
│   ├── generatefile.md         # Workflow for PRD analysis
│   └── workflowfile.md         # Development agent workflow
│
├── app/                        # Main application package
│   │
│   ├── __init__.py             # Package initializer
│   ├── main.py                 # Main entry point (runs bot + scheduler)
│   ├── config.py               # Configuration management (pydantic-settings)
│   │
│   ├── bot/                    # Telegram bot logic
│   │   ├── __init__.py
│   │   ├── handlers/           # Command and message handlers
│   │   │   ├── __init__.py
│   │   │   ├── start.py        # /start command and onboarding
│   │   │   ├── settings.py     # /settings command
│   │   │   ├── registration.py # FSM for user registration
│   │   │   └── common.py       # Common handlers (errors, unknown)
│   │   │
│   │   ├── keyboards/          # Inline and reply keyboards
│   │   │   ├── __init__.py
│   │   │   ├── onboarding.py   # Course and direction selection keyboards
│   │   │   ├── settings.py     # Settings menu keyboards
│   │   │   └── utils.py        # Keyboard builder utilities
│   │   │
│   │   ├── states/             # FSM states
│   │   │   ├── __init__.py
│   │   │   └── registration.py # RegistrationStates class
│   │   │
│   │   ├── utils/              # Bot utilities
│   │   │   ├── __init__.py
│   │   │   ├── formatters.py   # Message formatting (schedule, reminders)
│   │   │   └── validators.py   # Input validators
│   │   │
│   │   └── middlewares/        # Custom middlewares (if needed)
│   │       ├── __init__.py
│   │       └── logging.py      # Logging middleware
│   │
│   ├── web/                    # Admin web panel (FastAPI)
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI app initialization
│   │   │
│   │   ├── routes/             # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Login/logout routes
│   │   │   ├── dashboard.py    # Dashboard route
│   │   │   ├── directions.py   # Directions CRUD
│   │   │   ├── pairs.py        # Pairs CRUD (schedule management)
│   │   │   ├── slots.py        # Time slots management
│   │   │   ├── broadcast.py    # Broadcast messaging
│   │   │   └── logs.py         # Delivery logs viewer
│   │   │
│   │   ├── dependencies/       # Route dependencies
│   │   │   ├── __init__.py
│   │   │   └── auth.py         # Authentication dependency
│   │   │
│   │   ├── templates/          # Jinja2 HTML templates
│   │   │   ├── base.html       # Base layout with navigation
│   │   │   ├── login.html      # Login page
│   │   │   ├── dashboard.html  # Main dashboard
│   │   │   ├── directions_list.html
│   │   │   ├── directions_form.html
│   │   │   ├── pairs_list.html
│   │   │   ├── pairs_form.html
│   │   │   ├── slots_list.html
│   │   │   ├── broadcast.html
│   │   │   ├── logs.html
│   │   │   └── errors/         # Error pages
│   │   │       ├── 404.html
│   │   │       └── 500.html
│   │   │
│   │   └── static/             # Static files (CSS, JS, images)
│   │       ├── css/
│   │       │   └── style.css   # Custom styles
│   │       ├── js/
│   │       │   └── main.js     # Custom JavaScript
│   │       └── images/
│   │           └── logo.png
│   │
│   ├── scheduler/              # APScheduler jobs
│   │   ├── __init__.py
│   │   ├── scheduler.py        # Scheduler initialization
│   │   ├── jobs/               # Job definitions
│   │   │   ├── __init__.py
│   │   │   ├── morning_message.py  # Daily 08:00 schedule delivery
│   │   │   └── reminders.py        # 5-minute before reminders
│   │   │
│   │   └── utils/              # Scheduler utilities
│   │       ├── __init__.py
│   │       ├── delivery.py     # Batch delivery logic
│   │       └── logging.py      # Delivery logging
│   │
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py       # Database connection management
│   │   ├── schema.sql          # Database schema (CREATE TABLE statements)
│   │   ├── seed.sql            # Seed data (time_slots, initial directions)
│   │   │
│   │   ├── models/             # Pydantic models (data validation)
│   │   │   ├── __init__.py
│   │   │   ├── user.py         # User model
│   │   │   ├── direction.py    # Direction model
│   │   │   ├── pair.py         # Pair model
│   │   │   ├── time_slot.py    # TimeSlot model
│   │   │   └── delivery_log.py # DeliveryLog model
│   │   │
│   │   └── queries/            # Database queries (repository pattern)
│   │       ├── __init__.py
│   │       ├── users.py        # User CRUD operations
│   │       ├── directions.py   # Direction CRUD
│   │       ├── pairs.py        # Pair CRUD + assignments
│   │       ├── time_slots.py   # Time slot queries
│   │       └── delivery_logs.py # Delivery log queries
│   │
│   └── utils/                  # Shared utilities
│       ├── __init__.py
│       ├── timezone.py         # Timezone conversion utilities (MSK)
│       ├── logger.py           # Logging configuration
│       └── constants.py        # Application constants
│
├── tests/                      # Test suite (optional for MVP)
│   ├── __init__.py
│   ├── test_bot/
│   ├── test_web/
│   ├── test_scheduler/
│   └── test_db/
│
└── logs/                       # Log files (auto-generated)
    ├── bot.log
    ├── scheduler.log
    └── web.log
```

---

## File Naming Conventions

### Python Files
- **Modules:** `lowercase_with_underscores.py` (e.g., `morning_message.py`)
- **Classes:** `PascalCase` (e.g., `RegistrationStates`, `User`)
- **Functions:** `lowercase_with_underscores` (e.g., `send_schedule`, `get_user_by_id`)
- **Constants:** `UPPERCASE_WITH_UNDERSCORES` (e.g., `MAX_BATCH_SIZE`, `TIMEZONE`)
- **Private functions/methods:** Prefix with `_` (e.g., `_validate_input`)

### HTML Templates
- **Files:** `lowercase_with_underscores.html` (e.g., `pairs_list.html`, `directions_form.html`)
- **Base templates:** `base.html`, `base_form.html` (reusable)
- **Partials:** Prefix with `_` (e.g., `_navigation.html`, `_footer.html`)

### Static Files
- **CSS:** `style.css`, `admin.css`, `login.css`
- **JavaScript:** `main.js`, `broadcast.js`, `form_validation.js`
- **Images:** `logo.png`, `icon_settings.svg`

### Configuration Files
- **Environment:** `.env` (never commit), `.env.example` (commit)
- **Python dependencies:** `requirements.txt`, `requirements-dev.txt`
- **Git:** `.gitignore`

---

## Module Organization Patterns

### 1. Bot Handlers Pattern

**File:** `app/bot/handlers/start.py`

```python
from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    """Handle /start command"""
    # Handler logic here
```

**Registration:** All routers registered in `app/bot/handlers/__init__.py`:

```python
from aiogram import Dispatcher
from .start import router as start_router
from .settings import router as settings_router

def register_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(settings_router)
```

### 2. Database Queries Pattern (Repository)

**File:** `app/db/queries/users.py`

```python
import aiosqlite
from app.db.models.user import User

async def get_user_by_tg_id(conn: aiosqlite.Connection, tg_id: int) -> User | None:
    """Fetch user by Telegram ID"""
    async with conn.execute(
        "SELECT * FROM users WHERE tg_id = ?", (tg_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return User(**dict(row)) if row else None

async def create_user(conn: aiosqlite.Connection, user: User) -> int:
    """Create new user and return ID"""
    # Insert logic here
```

### 3. FastAPI Routes Pattern

**File:** `app/web/routes/pairs.py`

```python
from fastapi import APIRouter, Depends, Request
from app.web.dependencies.auth import require_auth

router = APIRouter(prefix="/admin/pairs", tags=["pairs"])

@router.get("/", dependencies=[Depends(require_auth)])
async def pairs_list(request: Request):
    """Display pairs list page"""
    # Logic here

@router.post("/", dependencies=[Depends(require_auth)])
async def pairs_create(request: Request):
    """Create new pair"""
    # Logic here
```

**Registration:** In `app/web/app.py`:

```python
from fastapi import FastAPI
from app.web.routes import pairs, directions

app = FastAPI()
app.include_router(pairs.router)
app.include_router(directions.router)
```

### 4. Pydantic Models Pattern

**File:** `app/db/models/user.py`

```python
from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    tg_id: int = Field(..., description="Telegram user ID")
    name: str = Field(..., min_length=1, max_length=100)
    course: int = Field(..., ge=1, le=4)
    direction_id: int
    remind_before: bool = True
    paused_until: Optional[str] = None  # ISO date string
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True
```

### 5. APScheduler Jobs Pattern

**File:** `app/scheduler/jobs/morning_message.py`

```python
from aiogram import Bot
from app.db.queries import users, pairs
from app.scheduler.utils.delivery import batch_send

async def morning_schedule_job(bot: Bot):
    """Send morning schedule to all active users at 08:00 MSK"""
    # Fetch all users not paused
    # For each user, fetch schedule
    # Batch send messages
```

**Registration:** In `app/scheduler/scheduler.py`:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scheduler.jobs.morning_message import morning_schedule_job

def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    
    scheduler.add_job(
        morning_schedule_job,
        CronTrigger(hour=8, minute=0),
        args=[bot],
        id="morning_schedule"
    )
    
    scheduler.start()
    return scheduler
```

---

## Configuration Structure

### Configuration File: `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application configuration"""
    
    # Telegram Bot
    BOT_TOKEN: str
    ADMIN_TG_ID: int
    
    # Database
    DATABASE_PATH: str = "data/schedule.db"
    
    # Admin Panel
    ADMIN_PASSWORD: str
    SECRET_KEY: str  # For session encryption
    
    # Scheduler
    TIMEZONE: str = "Europe/Moscow"
    MORNING_MESSAGE_HOUR: int = 8
    MORNING_MESSAGE_MINUTE: int = 0
    REMINDER_MINUTES_BEFORE: int = 5
    
    # Delivery
    BATCH_SIZE: int = 30
    BATCH_DELAY: float = 0.2  # seconds between batches
    MAX_RETRIES: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    
    # Web Server
    WEB_HOST: str = "127.0.0.1"
    WEB_PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Global settings instance
settings = Settings()
```

### Usage Example:

```python
from app.config import settings

print(settings.BOT_TOKEN)
print(settings.TIMEZONE)
```

---

## Development vs Production

### Development Environment

**Location:** Local machine or development server

**Configuration:**
- `.env` file with development values
- `LOG_LEVEL=DEBUG`
- `WEB_HOST=127.0.0.1` (localhost only)
- Hot reload enabled for FastAPI and bot

**Running:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run bot + scheduler
python -m app.main

# Or run web panel separately
uvicorn app.web.app:app --reload --host 127.0.0.1 --port 8000
```

### Production Environment

**Location:** VPS or dedicated server

**Configuration:**
- `.env` file with production values (secure passwords)
- `LOG_LEVEL=INFO` or `WARNING`
- `WEB_HOST=0.0.0.0` (if exposing admin panel)
- No hot reload

**Running (systemd services):**

**File:** `/etc/systemd/system/schedulebot.service`

```ini
[Unit]
Description=AGU Schedule Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/AGU_Schedule
Environment="PATH=/home/botuser/AGU_Schedule/venv/bin"
ExecStart=/home/botuser/AGU_Schedule/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
sudo systemctl enable schedulebot
sudo systemctl start schedulebot
sudo systemctl status schedulebot
```

### .gitignore Configuration

```gitignore
# Environment
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.db-journal
data/*.db

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary files
tmp/
temp/
```

---

## Key Principles

### 1. Separation of Concerns
- **Bot logic** (`app/bot/`) handles Telegram interactions only
- **Web logic** (`app/web/`) handles HTTP requests only
- **Scheduler logic** (`app/scheduler/`) handles background jobs only
- **Database logic** (`app/db/`) handles data persistence only

### 2. Single Responsibility
- Each module has ONE clear purpose
- Each function does ONE thing well
- Each class represents ONE concept

### 3. Dependency Injection
- Pass database connections as function arguments
- Pass Bot instance to scheduler jobs
- Use FastAPI's Depends() for route dependencies

### 4. Configuration Management
- All environment-specific values in `.env`
- Use `pydantic-settings` for type-safe config
- Never hardcode secrets or paths

### 5. Error Handling
- Log all errors with context
- Return user-friendly messages
- Implement retry logic for critical operations

---

**Last Updated:** 03.12.2025  
**Status:** Reference document for all development  
**Next:** Consult this structure before creating any new file
