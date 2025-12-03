# Bug Tracking and Error Documentation

**Project:** AGU Schedule Telegram Bot + Admin Panel  
**Version:** 1.0  
**Date:** 03.12.2025

---

## Purpose

This document tracks all bugs, errors, and issues encountered during development and production. It serves as:
- A comprehensive error log for reference
- A resolution knowledge base
- A quality assurance checklist
- A debugging resource for future issues

---

## Bug Entry Template

When documenting a bug, use the following format:

```markdown
### BUG-XXX: Short Description

**Date Reported:** YYYY-MM-DD  
**Reported By:** Developer Name / User / System  
**Severity:** Critical / High / Medium / Low  
**Status:** Open / In Progress / Resolved / Closed  
**Component:** Bot / Web / Scheduler / Database / Other

**Description:**
Detailed description of the bug, including what happened and what was expected.

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Error Message / Logs:**
```
Paste error message or relevant log entries here
```

**Environment:**
- OS: Windows / Linux / macOS
- Python Version: X.X.X
- Library Versions: aiogram X.X.X, FastAPI X.X.X, etc.
- Deployment: Local / VPS / Production

**Root Cause:**
Explanation of why the bug occurred (filled after investigation)

**Solution:**
How the bug was fixed (code changes, configuration updates, etc.)

**Files Modified:**
- `app/bot/handlers/start.py` - Line XX
- `app/db/queries/users.py` - Line XX

**Prevention:**
Steps taken to prevent similar issues in the future

**Closed Date:** YYYY-MM-DD  
**Verified By:** Developer Name
```

---

## Severity Levels

| Level    | Description                                      | Response Time |
|----------|--------------------------------------------------|---------------|
| Critical | System down, data loss, security breach          | Immediate     |
| High     | Core feature broken, affects many users          | Same day      |
| Medium   | Minor feature issue, affects some users          | 1-3 days      |
| Low      | Cosmetic issue, minor inconvenience              | Next sprint   |

---

## Bug Log

### BUG-001: Example Bug Entry

**Date Reported:** 2025-12-03  
**Reported By:** Developer  
**Severity:** Medium  
**Status:** Resolved  
**Component:** Bot

**Description:**
User registration fails when direction name contains Cyrillic characters with special Unicode modifiers.

**Steps to Reproduce:**
1. Start bot with `/start`
2. Select course 2
3. Select direction "Информатика и ВТ"
4. Registration fails with encoding error

**Error Message / Logs:**
```
UnicodeEncodeError: 'ascii' codec can't encode characters in position 0-10: ordinal not in range(128)
  File "app/bot/handlers/registration.py", line 45, in process_direction
```

**Environment:**
- OS: Windows 10
- Python Version: 3.11.5
- aiogram Version: 3.15.0
- Database: SQLite

**Root Cause:**
Database connection was not using UTF-8 encoding when inserting data. SQLite default encoding on Windows is ASCII.

**Solution:**
Added explicit UTF-8 encoding to database connection in `app/db/connection.py`:

```python
async def get_connection():
    conn = await aiosqlite.connect(settings.DATABASE_PATH)
    await conn.execute("PRAGMA encoding = 'UTF-8'")
    conn.row_factory = aiosqlite.Row
    return conn
```

**Files Modified:**
- `app/db/connection.py` - Added UTF-8 pragma

**Prevention:**
- Added encoding tests to test suite
- Documented encoding requirements in project_structure.md

**Closed Date:** 2025-12-03  
**Verified By:** Developer

---

### BUG-002: [Next Bug Here]

_Template ready for next bug report_

---

## Known Issues

### Issue Backlog (Non-blocking)

1. **Dashboard stats update delay**
   - Stats refresh only on page reload, not real-time
   - Priority: Low
   - Workaround: Manual refresh
   - Future: Implement WebSocket updates

2. **Mobile table scrolling UX**
   - Tables difficult to scroll on small screens
   - Priority: Low
   - Workaround: Use landscape mode
   - Future: Implement card view for mobile

---

## Testing Checklist

Use this checklist during testing phases to catch common issues:

### Bot Functionality
- [ ] `/start` command works correctly
- [ ] Course selection displays all 4 courses
- [ ] Direction selection shows only directions for selected course
- [ ] Registration saves data correctly (check database)
- [ ] `/settings` command displays menu
- [ ] Reminder toggle updates database
- [ ] Pause notifications accepts date input
- [ ] Resume notifications works after pause
- [ ] Share bot link generates correct URL
- [ ] FSM states transition correctly
- [ ] Error handling shows user-friendly messages

### Scheduler
- [ ] Morning message sends at 08:00 MSK
- [ ] Schedule message format matches PRD
- [ ] Batch delivery respects rate limits
- [ ] Retry logic works on delivery failure
- [ ] 5-minute reminders send at correct times
- [ ] Reminders only sent to users with `remind_before=true`
- [ ] Paused users do not receive messages
- [ ] Delivery logs recorded correctly

### Admin Panel
- [ ] Login page requires password
- [ ] Session persists across page reloads
- [ ] Logout clears session
- [ ] Dashboard displays correct stats
- [ ] Directions CRUD works (create, edit, delete)
- [ ] Pairs CRUD works completely
- [ ] Multi-direction assignment saves correctly
- [ ] Preview shows correct message format
- [ ] Test send delivers to admin
- [ ] Broadcast sends to correct user groups
- [ ] Logs display with filters working
- [ ] Pagination works on logs page

### Database
- [ ] All tables created correctly
- [ ] Seed data loads successfully
- [ ] Foreign keys enforce relationships
- [ ] User data persists correctly
- [ ] Pair assignments save properly
- [ ] Delivery logs write without errors
- [ ] Database queries are efficient (no N+1)

### General
- [ ] All environment variables load from `.env`
- [ ] Logging writes to file and console
- [ ] Timezone conversions work (UTC <-> MSK)
- [ ] Error messages are user-friendly
- [ ] No sensitive data in logs
- [ ] All forms validate input
- [ ] CSRF protection enabled

---

## Common Error Patterns

### 1. Database Connection Errors

**Error:**
```
sqlite3.OperationalError: unable to open database file
```

**Common Causes:**
- Database file path incorrect
- Directory does not exist
- Permission issues

**Solution:**
- Verify `DATABASE_PATH` in `.env`
- Create directory: `mkdir -p data/`
- Check file permissions

---

### 2. Telegram API Rate Limit

**Error:**
```
RetryAfter: Flood control exceeded. Retry in 30 seconds
```

**Common Causes:**
- Sending messages too fast
- Batch size too large
- No delay between batches

**Solution:**
- Increase `BATCH_DELAY` in config
- Reduce `BATCH_SIZE` to 20-30
- Implement exponential backoff

---

### 3. FSM State Lost

**Error:**
User registration resets after bot restart

**Common Causes:**
- Using `MemoryStorage` (data lost on restart)
- No persistent storage configured

**Solution:**
- For MVP: Accept this limitation (rare restarts)
- For production: Use Redis or database storage

---

### 4. Timezone Issues

**Error:**
Messages sent at wrong time (e.g., 05:00 instead of 08:00)

**Common Causes:**
- Server timezone not MSK
- Scheduler using wrong timezone
- Times stored as UTC but displayed as local

**Solution:**
- Verify `TIMEZONE=Europe/Moscow` in `.env`
- Use `pytz` or `zoneinfo` for conversions
- Store all times in database as UTC, convert on display

---

### 5. Template Not Found

**Error:**
```
jinja2.exceptions.TemplateNotFound: dashboard.html
```

**Common Causes:**
- Template file missing
- Wrong file path in Jinja2 config
- Typo in template name

**Solution:**
- Verify file exists in `app/web/templates/`
- Check Jinja2 template directory setting
- Ensure filename matches exactly (case-sensitive)

---

## Debug Mode Guidelines

### Enabling Debug Mode

**Development:**
```python
# In app/config.py
LOG_LEVEL = "DEBUG"

# For FastAPI
uvicorn.run(app, host="127.0.0.1", port=8000, reload=True, log_level="debug")

# For aiogram
logging.basicConfig(level=logging.DEBUG)
```

### What to Log

**DO Log:**
- User actions (registration, settings changes)
- Scheduler job executions
- Database queries (in debug mode)
- API requests to Telegram
- Error stack traces with context

**DON'T Log:**
- User passwords or tokens
- Full message content (GDPR)
- Bot token or admin credentials
- Sensitive personal data

---

## Performance Issues

### Slow Database Queries

**Symptoms:**
- Admin panel slow to load
- Queries taking >1 second

**Debugging:**
```sql
EXPLAIN QUERY PLAN SELECT * FROM pairs WHERE direction_id = ?;
```

**Solutions:**
- Add indexes: `CREATE INDEX idx_pairs_direction ON pairs(direction_id);`
- Optimize joins
- Use pagination

---

### Memory Leaks

**Symptoms:**
- Memory usage grows over time
- Bot becomes unresponsive

**Debugging:**
- Monitor with `htop` or Task Manager
- Use `memory_profiler` library

**Solutions:**
- Close database connections properly
- Clear cached data periodically
- Restart bot daily (cron job)

---

## Production Monitoring

### Health Checks

1. **Bot Online:**
   - Test: Send `/start` command
   - Expected: Immediate response

2. **Scheduler Running:**
   - Check: Recent logs in delivery_log table
   - Expected: Entries from today

3. **Admin Panel Accessible:**
   - Test: Visit admin URL
   - Expected: Login page loads

### Automated Alerts (Future)

- Set up alerts for:
  - Bot offline >5 minutes
  - Error rate >10%
  - No deliveries in 24 hours
  - Database size >500MB

---

## Rollback Plan

If critical bug deployed to production:

1. **Immediate:**
   - Stop bot service: `sudo systemctl stop schedulebot`
   - Notify users via broadcast (if possible)

2. **Rollback:**
   - Restore previous code version: `git checkout <previous-commit>`
   - Restore database backup: `cp backup.db schedule.db`
   - Restart service: `sudo systemctl start schedulebot`

3. **Verify:**
   - Test all critical paths
   - Check logs for errors
   - Monitor for 30 minutes

4. **Post-Mortem:**
   - Document bug in this file
   - Identify root cause
   - Update deployment checklist

---

## Contact Information

**Primary Developer:** [Name]  
**Email:** [email]  
**Emergency Contact:** [phone]

---

**Last Updated:** 2025-12-03  
**Next Review:** After each deployment or major bug fix
