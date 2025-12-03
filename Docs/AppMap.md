# ScheduleBot — Detailed Application Map (MVP)

**Version:** 1.0

**Purpose:** This document is a comprehensive application map for the ScheduleBot MVP — a Telegram bot and small admin web interface that delivers daily class schedules and per-class reminders to students. It describes every page, endpoint, backend function, scheduler behavior, database schema, UI interactions, error handling, and edge cases in detail.

---

## Table of Contents

1. Overview
2. Goals and Constraints
3. High-level Architecture
4. Data Model (Detailed)
5. User Flows (Student)

   1. Onboarding (/start)
   2. Settings
   3. Daily Morning Message
   4. 5-minute Reminder
   5. Pause / Resume
   6. Share Bot
6. Admin Flows

   1. Secure Access
   2. Admin Dashboard
   3. CRUD: Pairs
   4. Assign Pairs to Directions (multi-assign)
   5. Preview & Test Mode
   6. Broadcast Messaging
   7. Delivery Log & Basic Stats
7. Web Admin — Page-by-page Specification

   1. Login Page
   2. Dashboard (Home)
   3. Directions Management
   4. Time Slots Management
   5. Pairs Management — List View
   6. Pair Edit/Create View
   7. Assignments Panel (multi-select)
   8. Preview/Test Message Modal
   9. Broadcast Page
   10. Delivery Log Page
   11. Settings Page (Admin)
8. Bot — Commands, Callbacks, and Message Templates

   1. Commands Summary
   2. Inline Keyboards & Buttons
   3. Message Templates (final text examples)
9. Backend API Endpoints (FastAPI) — Contract & Examples
10. Scheduler & Delivery Engine — Design & Behavior

    1. Morning Job
    2. Reminder Job
    3. Batching, Rate-limiting and Retry Logic
    4. Failure Modes and Recovery
11. Error Handling & Monitoring
12. Security & Privacy
13. Deployment & Local Development Notes
14. Testing Plan
15. Future Enhancements (Roadmap)
16. Appendix: Example SQL Schema and Seed data

---

## 1. Overview

ScheduleBot is a minimal, reliable MVP that:

* stores weekly schedules (pairs) for multiple study directions and courses in a local SQLite database;
* provides a private web admin interface for the administrator to create and assign pairs to directions using multi-select checkboxes;
* allows students to register in the Telegram bot, pick their course and direction, and receive:

  * a daily text message at **08:00 MSK** containing all pairs for the current day;
  * optional additional reminders **5 minutes** before each pair if they enabled reminders in settings.

The product is intentionally lightweight: no PDF parsing, no export/import, no roles except admin and student, and no Docker for deployment — it runs locally initially and can be migrated to a more permanent host later.

## 2. Goals and Constraints

**Primary goals:**

* fast, reliable daily delivery of schedules to students;
* simple admin interface for quick data entry and mass assignment of schedule items;
* low operational complexity for local testing and simple migration.

**Constraints:**

* Use aiogram 3 for the Telegram bot and FastAPI for the admin interface.
* Use SQLite as the database.
* No Docker; run using a local Python environment on the developer's PC.
* Admin web interface is private (admin-only).
* Messages are text-only for students; admin can optionally attach a photo to broadcast messages.
* Reminder logic: only 5-minute reminders (no other intervals).
* Daily message sent at exactly 08:00 MSK (timezone-aware logic must be used).

## 3. High-level Architecture

Components:

* **Telegram Bot (aiogram 3)** — handles user onboarding, settings, command processing, and receiving admin commands (/admin) from the admin account.
* **Scheduler (async background task)** — responsible for running the morning job and the reminder job.
* **FastAPI Admin App** — local web UI for admin to create/edit pairs and initiate broadcasts.
* **SQLite Database** — single file storing users, directions, time slots, pairs, assignments, and delivery logs.
* **Config & Secrets** — .env file to store BOT_TOKEN, ADMIN_TG_ID, and optional web password.

Communication paths:

* Bot <-> Database: read/write user records, read pairs and assignments.
* Admin Web App <-> Database: CRUD operations on pairs/directions/time slots.
* Scheduler <-> Bot API: sends messages to students using bot token.

Process model:

* Single-process approach for MVP is acceptable: a single Python process runs the bot and the web server concurrently using `asyncio` and `uvicorn` with background tasks. Alternatively, run bot and web server as separate processes (recommended for stability).

## 4. Data Model (Detailed)

All timestamps are ISO8601 strings in UTC when stored (unless stored as plain local times for slot definitions). The logic converts times between MSK and UTC for scheduling.

### Tables (fields and descriptions)

1. **users**

* `id` INTEGER PRIMARY KEY — internal DB id
* `tg_id` INTEGER UNIQUE NOT NULL — Telegram user id
* `tg_username` TEXT — Telegram username (optional)
* `name` TEXT NOT NULL — user-provided name displayed by bot
* `course` INTEGER NOT NULL — 1..4
* `direction_id` INTEGER NOT NULL — foreign key to `directions(id)`
* `remind_before` BOOLEAN DEFAULT 0 — whether 5-min reminders enabled
* `paused_until` TEXT NULL — optional ISO date string representing when pause ends
* `created_at` TEXT DEFAULT CURRENT_TIMESTAMP

2. **directions**

* `id` INTEGER PRIMARY KEY
* `name` TEXT NOT NULL
* `course` INTEGER NOT NULL

3. **time_slots**

* `id` INTEGER PRIMARY KEY (1..5)
* `start_time` TEXT NOT NULL — e.g. `09:00` (local MSK time)
* `end_time` TEXT NOT NULL — e.g. `10:45`

4. **pairs**

* `id` INTEGER PRIMARY KEY
* `title` TEXT NOT NULL — name of subject
* `teacher` TEXT NULL — full FIO
* `room` TEXT NULL — audience
* `type` TEXT NULL — Lecture / Seminar / Practice
* `extra_link` TEXT NULL — optional link, shown only if present
* `day_of_week` INTEGER NOT NULL — 0 = Monday ... 6 = Sunday
* `slot_id` INTEGER NOT NULL — FK to time_slots.id
* `created_at` TEXT DEFAULT CURRENT_TIMESTAMP

5. **pair_assignments**

* `id` INTEGER PRIMARY KEY
* `pair_id` INTEGER NOT NULL — FK to pairs.id
* `direction_id` INTEGER NOT NULL — FK to directions.id

6. **delivery_log**

* `id` INTEGER PRIMARY KEY
* `user_id` INTEGER NULL — FK to users.id
* `pair_id` INTEGER NULL — FK to pairs.id (if relevant)
* `message_type` TEXT NOT NULL — 'morning' | 'reminder' | 'broadcast'
* `status` TEXT NOT NULL — 'sent' | 'error'
* `tg_message_id` INTEGER NULL — Telegram message id when available
* `error` TEXT NULL — brief error message
* `ts` TEXT DEFAULT CURRENT_TIMESTAMP

**Indexes**: create indexes on `users.tg_id`, `pair_assignments.direction_id`, and `pairs.day_of_week, pairs.slot_id` for quick lookups.

## 5. User Flows (Student)

The following are full, step-by-step flows with UI and backend behavior.

### 5.1 Onboarding (/start)

**Trigger:** user sends `/start` to bot.

**Sequence:**

1. Bot checks `users` for existing `tg_id`.

   * If found: show "You're already registered" summary and offer commands: `/settings`, `/help`.
   * If not found: start new onboarding.
2. Bot captures `tg_username` (if present) and stores temporarily.
3. Bot asks: "Hi! Please enter your name as you'd like me to call you in messages." — expecting a text reply.

   * On reply: sanitize and store in `users.name`.
4. Bot shows inline keyboard to pick `course` (1,2,3,4). Buttons: `1`, `2`, `3`, `4`.

   * On selection: store `course` in the user record temporarily.
5. Bot shows inline keyboard with `directions` filtered for the selected course. The keyboard lists each direction as a button (`Математика`, `ПМ`, etc.).

   * On selection: store `direction_id` in user record.
6. Bot shows a confirmation message with two inline buttons: **All correct!** and **Start over**.

   * If **All correct!** clicked: finalize registration, set `remind_before` default = 0, reply with welcome message:

```
Congratulations! You will receive a daily schedule at 08:00 (MSK). In Settings you can enable 5-minute reminders before each class.
```

* If **Start over**: clear user record and restart onboarding.

**Notes & validations:**

* `name` must be <= 50 chars; disallow only emoji or empty strings.
* If `tg_username` exists, it will be used as fallback greeting; otherwise `name` is used.
* Any invalid input or timeout (no response within configurable timeout) results in a friendly reminder or restart prompt.

### 5.2 Settings

**Accessible via:** `/settings` command or menu button.

**Settings screen fields & actions:**

* **Reminders before class:** Toggle `On` / `Off` — toggles `remind_before` boolean in DB.
* **Pause notifications:** Button "Pause notifications" — brings a small flow: ask for number of days OR "Indefinite". Set `paused_until` accordingly. Also provide "Resume now" button if paused.
* **Change registration:** "Change course/direction" button — take user through the inline keyboard course → direction flow again (same as onboarding confirmation flow).
* **Account:** Display stored `name`, `tg_username`, `course`, `direction` with `Edit` buttons for name and change course.
* **Share bot:** Button that produces `tg://resolve?domain=<bot_username>` share link or a simple message template the user can forward.

**Notes:**

* If user toggles reminders ON and there is an upcoming pair in less than 5 minutes, the system will send the 5-minute reminder for that pair immediately (per the user's input earlier).

### 5.3 Daily Morning Message

**Schedule:** send at 08:00 MSK every day.

**Behavior:**

1. Scheduler determines the current day of week (MSK) and fetches all `pairs` for that day assigned to the user's direction.
2. Format the message according to the template in Section 8. If no classes that day, send a short message: "Good morning, {name}! There are no classes for {weekday} ({date})."
3. Send message to users who: are not paused (no valid `paused_until` in the future) and are registered.
4. Each individual send is recorded in `delivery_log` with `message_type = 'morning'` and status `sent` or `error`.

**Message composition:**

* Header: greeting with `name` (prefer `tg_username` if user didn't enter name), weekday and full date in `DD.MM.YYYY` format.
* For each pair: index: subject, room, type, teacher (full FIO). If `extra_link` is present for a pair, append on a new line.

**Example:**

```
Good morning, Alex!
Monday (02.12.2025)

1 pair: Mathematical Analysis
Room: 312
Type: Seminar
Teacher: Ivanov Ivan Ivanovich

2 pair: ...
```

### 5.4 5-minute Reminder

**Trigger:** job runs continuously and checks for upcoming slot times. Alternatively, a timed scheduler triggers events exactly at times computed as `slot_start - 5 minutes` MSK.

**Behavior:**

* For a given slot starting at HH:MM MSK, the system finds all users whose assigned direction has a pair scheduled at that day_of_week and slot_id, and who have `remind_before = true` and are not paused.
* Send a short reminder message constructed with the specific pair details.
* Log delivery in `delivery_log` with message_type = 'reminder'.
* If user enabled reminders in the last 5 minutes before the pair, the reminder is still sent (per requirement).

**Important edge cases:**

* If admin edits/deletes a pair after the morning message but before the reminder, the reminder reflects the DB at the time of sending (i.e., latest state). This is acceptable for MVP.

### 5.5 Pause / Resume

* Pause is implemented via `paused_until`. If user sets pause for N days, `paused_until` = current_date + N days at 23:59:59 MSK. If indefinite, set a long date or `paused = true`; for simplicity use `paused_until` as nullable.
* Scheduler checks `paused_until` before sending messages.

### 5.6 Share Bot

* Implemented via a simple share URL and a small inline keyboard with the bot link and an invitation text. Also a built-in `Share` button in the settings UI.

## 6. Admin Flows

Admin is a single person (you). Admin access is controlled by Telegram ID for bot commands and by a secure login for the admin web interface.

### 6.1 Secure Access

* Bot: `/admin` command is accepted only when `message.from.id == ADMIN_TG_ID`. If not, reply "Access denied.".
* Web Admin: simple password-protected login or token-based check; on first design use a static password stored in `.env`. Optionally require admin's TG ID and a second password for web access.

### 6.2 Admin Dashboard

* Quick stats: total users, users per direction, today's total class count across all directions, number of scheduled pairs.
* Shortcuts to CRUD pages: Pairs, Directions, Time Slots, Broadcast, Delivery Log.

### 6.3 CRUD: Pairs

Admin can create, edit, and delete `pairs`. Create form fields are:

* Title (required)
* Day of Week (required)
* Slot (required; select from existing time_slots)
* Type (Lecture/Seminar/Practice) (required)
* Teacher (full FIO) (optional but recommended)
* Room (optional)
* Extra Link (optional)
* Assign to directions (multi-select checkboxes) — this will create entries in `pair_assignments`.

Validation:

* Prevent duplicate exact pair (same title, slot, day, and direction) on assignment; show warning and allow override.

### 6.4 Assign Pairs to Directions (multi-assign)

* The UI shows checkboxes grouped by course (1..4). Admin checks 1..N directions and clicks "Assign".
* Backend creates `pair_assignments` entries for each selected direction.
* The UI should show an immediate preview of affected directions and the approximate number of users who will be impacted.

### 6.5 Preview & Test Mode

* Preview: show exactly how the morning message will look for a selected direction and optionally a specific student `name`.
* Test mode: send the morning message or a reminder to a specified Telegram ID (admin's test account) to verify formatting and delivery.

### 6.6 Broadcast Messaging

* Admin invokes `/admin` in bot or uses web UI to open Broadcast page.
* Flow: compose text → optionally upload a photo → select preview → choose "Send to all".
* Confirmation: a modal lists number of recipients and estimated duration; admin confirms to start.
* Delivery: broadcast is processed in batches and recorded in `delivery_log` with message_type = 'broadcast'.

### 6.7 Delivery Log & Basic Stats

* Delivery log shows each send attempt, user, message_type, status, and timestamp.
* Basic stats: total messages today, errors, and per-message-type counts.

## 7. Web Admin — Page-by-page Specification

Below each page is described with its full UI fields, validation, and backend endpoints.

### 7.1 Login Page

**URL:** `/admin/login`

**Fields:**

* `password` (required)
* `remember_me` (optional)

**Behavior:**

* Validate password against `.env` stored admin password or a hashed value in a config file.
* On success: set session cookie and redirect to Dashboard.
* On failure: show 1-line error `Invalid password`.

**Security:**

* Rate-limit login attempts (e.g., 5 per minute) and show a captcha if many failures (optional for MVP).

### 7.2 Dashboard (Home)

**URL:** `/admin/`

**Widgets:**

* Quick stats: `Total users`, `Users by course`, `Users by direction`, `Today's total pairs`.
* Short links to: Create Pair, Manage Directions, Manage Time Slots, Broadcast, Delivery Log.
* Recent activity: last 10 delivery_log entries.

**Actions:**

* Button: Create new pair (leads to Pair Create page)
* Button: Broadcast (leads to Broadcast page)

### 7.3 Directions Management

**URL:** `/admin/directions`

**UI:**

* Table of directions: columns = id, name, course, actions (edit/delete).
* Form: create new direction (name, course select 1..4).

**Validations:**

* Direction name required, max 100 chars.

### 7.4 Time Slots Management

**URL:** `/admin/slots`

**UI:**

* Table of slots: id, start_time, end_time, actions (edit).
* Default slots seeded on init: 1..5 with times provided.
* Edit allows changing times; any change shows a warning that it affects scheduler timing.

### 7.5 Pairs Management — List View

**URL:** `/admin/pairs`

**UI:**

* Table of pairs: id, title, day_of_week, slot, type, teacher, assigned_directions (comma list), actions (edit, delete, preview, test send).
* Filters: by course, by direction, by day_of_week.

**Bulk actions:**

* Delete selected
* Assign selected to additional directions

### 7.6 Pair Edit/Create View

**URL:** `/admin/pairs/new` and `/admin/pairs/{id}/edit`

**Form fields with details:**

* `Title` (required, text)
* `Day of week` (required, select Monday..Sunday)
* `Slot` (required, select from time_slots)
* `Type` (required, select: Lecture / Seminar / Practice)
* `Teacher` (text, full FIO; optional columns for surname/firstname/middlename are unnecessary for MVP but acceptable)
* `Room` (optional text)
* `Extra link` (optional, URL field, validated for http/https)
* `Assign to directions` — *checkbox list*, grouped by course. Each checkbox labeled "Course X — DirectionName". A search box filters directions.

**Buttons:**

* Save & Close
* Save & Create another
* Preview

**Validations / UX:**

* If no directions selected, show warning and refuse save (pairs must be assigned to >=1 direction).
* If a pair with identical `title`/`day_of_week`/`slot` exists for a selected direction, show a non-blocking warning and require confirmation before override.

### 7.7 Assignments Panel (Multi-select)

* The assignments control in the Pair Edit page shows a list of all directions grouped by course with checkboxes. Each checkbox also shows a small badge with the approximate number of users currently assigned to that direction for admin context.

### 7.8 Preview/Test Message Modal

* Shows a WYSIWYG-text preview of the morning message for a selected direction and optionally a sample name.
* Button: "Send test to TG ID" — input for a TG id (default = admin TG id) and a Send button. Logs that send as a `broadcast` or `test` type.

### 7.9 Broadcast Page

**URL:** `/admin/broadcast`

**Fields:**

* `Message text` (textarea, required)
* `Image` (optional file input)
* `Preview` (shows how the message will look in Telegram)
* `Recipients` — default = All registered users; advanced: allow filter by course/direction (optional)

**Flow:**

* Admin clicks Send → confirmation modal with recipient count and expected duration; must confirm.
* Start broadcast: show progress bar; show errors per user if any.

### 7.10 Delivery Log Page

**URL:** `/admin/logs`

**UI:**

* Table with columns: timestamp, user (tg_id and name), message_type, pair_id, status, error.
* Filters: date range, message_type, status.
* Export: button to export visible rows as CSV (optional, not required per constraints).

### 7.11 Settings Page (Admin)

**URL:** `/admin/settings`

**Fields:**

* `Time zone` (fixed to Europe/Moscow for MVP but show as read-only)
* `Admin TG ID` — show the configured ID
* `Broadcast batch size` — integer used by scheduler
* `Retry attempts` — integer (default 1)

## 8. Bot — Commands, Callbacks, and Message Templates

### 8.1 Commands Summary

* `/start` — onboarding flow
* `/settings` — user settings
* `/help` — short help text
* `/admin` — admin-only command that shows admin menu in the bot (only for ADMIN_TG_ID)

### 8.2 Inline Keyboards & Buttons

**Onboarding course selection:** buttons `1`, `2`, `3`, `4` — each returns payload `course:<n>`.

**Direction selection:** dynamic buttons generated from directions for the selected course with payload `direction:<id>`.

**Confirmation:** two buttons — `confirm_registration` and `restart_registration`.

**Settings toggles:** small inline buttons toggling `remind_before`.

**Admin broadcast:** confirm/cancel inline buttons.

### 8.3 Message Templates (final text examples)

**Morning (multiple pairs):**

```
Good morning, {name}!
{weekday} ({DD.MM.YYYY})

{if no pairs} No classes today. Enjoy! {else}
1 pair: {title}
Room: {room}
Type: {type}
Teacher: {teacher}

2 pair: ...
{end}
```

**Reminder (single pair):**

```
In 5 minutes — {slot_number} pair: {title}
Room: {room}
Type: {type}
Teacher: {teacher}
```

**Broadcast (admin):** raw text typed by admin; if image included, send as multipart message with caption.

**Onboarding prompts:**

* "Please enter your name as you'd like me to call you in messages."
* Course selection inline.
* Direction selection inline.
* Confirmation card with `All correct!` and `Start over`.

## 9. Backend API Endpoints (FastAPI) — Contract & Examples

For internal use by the admin UI. All endpoints require admin session.

* `POST /api/login` — body: `{ password }` → returns session cookie.
* `GET /api/stats` — returns `{ total_users, users_by_course: {...}, users_by_direction: {...} }`.
* `GET /api/directions` — returns list of directions.
* `POST /api/directions` — create direction `{ name, course }`.
* `GET /api/slots` — returns time_slots.
* `PUT /api/slots/{id}` — update slot times.
* `GET /api/pairs` — query params: `course, direction_id, day_of_week` → list pairs with assigned directions.
* `POST /api/pairs` — body: `{ title, day_of_week, slot_id, type, teacher, room, extra_link, direction_ids: [] }` → creates pair and assignments.
* `PUT /api/pairs/{id}` — update pair and its assignments.
* `DELETE /api/pairs/{id}` — delete pair and related assignments.
* `POST /api/preview` — body: `{ direction_id, sample_name }` → returns generated message text (no send).
* `POST /api/test_send` — body: `{ tg_id, content }` → sends a test message via bot.
* `POST /api/broadcast` — body: `{ content, include_image: boolean, filters? }` → triggers broadcast.
* `GET /api/logs` — returns `delivery_log` entries.

All endpoints return standard JSON: `{ success: bool, data: ..., error: null | string }`.

## 10. Scheduler & Delivery Engine — Design & Behavior

### 10.1 Morning Job

**Goal:** trigger at 08:00 MSK daily and send each user a consolidated message with all pairs for that user's direction for that day.

**Implementation details:**

* Use `apscheduler` with timezone support, or an internal `asyncio` loop that computes the next 08:00 MSK and sleeps until then.
* On trigger:

  1. Query all users where `paused_until` is null or `paused_until < now`.
  2. For each user: fetch pairs `WHERE day_of_week = current_weekday AND pair_assignments.direction_id = user.direction_id` joined with slots and order by `slot_id`.
  3. Format message and send using bot.
  4. Record each send in `delivery_log`.
* Send in batches to respect Telegram rate limits.

### 10.2 Reminder Job

**Goal:** send reminders 5 minutes before each slot to eligible students.

**Implementation approaches:**

* **Event-based:** For each slot time, schedule a one-off scheduled job at `slot_start_time - 5 minutes` MSK that executes every day for each slot. This is simple because slot times are fixed.
* **Polling-based:** run a worker every 30 seconds to find pairs starting in 5 minutes (taking MSK time into account). For MVP recommend event-based scheduling using `apscheduler` as it is simpler and more accurate.

**Reminder flow:**

1. Find all pairs where `pair.slot_id` has `start_time` equal to `current_time + 5 minutes` MSK and where `day_of_week` matches.
2. For each matching pair, find all `users` assigned to directions in `pair_assignments` and with `remind_before = true` and not paused.
3. Send reminder messages in batches. Log results.

### 10.3 Batching, Rate-limiting and Retry Logic

**Batching:**

* Default `BATCH_SIZE = 30` means send messages to 30 users concurrently using `asyncio.gather` constrained by a semaphore.
* Insert a small delay between batches (e.g., 0.1 to 0.3 seconds) to reduce burst traffic.

**Rate limits & 429 handling:**

* If HTTP 429 is received from Telegram, read `Retry-After` header. Pause sending for that period, then retry. For MVP, if 429 occurs, the scheduler will back off exponentially with at most one retry per user for morning/reminder messages.

**Retry policy:**

* One immediate retry on transient network error or 5xx response.
* For persistent failures (user blocked bot, chat not found) mark as `error` and do not retry further.
* All failures are logged with the `error` text in `delivery_log`.

### 10.4 Failure Modes and Recovery

* **Bot token invalid:** scheduler should halt and admin must be notified on web UI (or console logs) — no messages are sent.
* **DB locked (SQLite)**: use short transactions and retries; if frequent, recommend migrating to PostgreSQL.
* **Process restarted:** scheduler should reconcile and resume next scheduled jobs normally.

## 11. Error Handling & Monitoring

* Minimal logging to console + a logfile (rotating) that records errors, delivery failures, scheduler events.
* The admin web UI displays recent errors in the Dashboard.
* Delivery_log accessible to admin for postmortem.

## 12. Security & Privacy

* Store only `tg_id`, `tg_username`, and `name` for users. No email/phone.
* Admin web UI protected by a password and accessible locally only by default.
* Use HTTPS when exposing admin UI publicly (Let's Encrypt recommended).
* Restrict `/admin` bot command to ADMIN_TG_ID.
* Keep the bot token and admin password in an `.env` file and never checked into source control.

## 13. Deployment & Local Development Notes

**Local development steps (no Docker):**

1. Create a Python virtual environment and install requirements:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` with: `BOT_TOKEN`, `ADMIN_TG_ID`, `ADMIN_PASSWORD` etc.
3. Initialize database: `python scripts/init_db.py` (creates schema and seeds directions and slots).
4. Run bot and web admin — options:

   * Single process using `uvicorn admin_app:app --reload` and a separate terminal for bot `python bot.py`.
   * Or start both in a single process using `asyncio.create_task` for the web server (less recommended).

**Production notes:**

* Vercel is not suitable for the scheduler long-running background process. Consider VPS, Railway, Render, or DigitalOcean.
* If moving to production, consider switching DB to PostgreSQL to avoid SQLite locking issues at scale.

## 14. Testing Plan

**Unit tests:**

* DB functions: CRUD for pairs, assignments, users.
* Message formatting: given a user/direction and day, produce the exact text output.
* Scheduler utility functions that compute next 08:00 MSK and slot offsets.

**Integration tests (manual):**

* End-to-end onboarding in Telegram and receiving a test morning message.
* Admin web UI: create a pair and assign to directions; verify appropriate students receive messages.
* Broadcast test: send a test broadcast to admin and verify logs.

**Load testing:**

* Simulate 3500 users in a local test environment by mocking the bot API responses to validate batching and rate-limit behavior.

## 15. Future Enhancements (Roadmap)

1. PDF parsing for auto-importing schedules.
2. Support for odd/even week patterns and semester calendars.
3. Multi-language (English) support.
4. Move to PostgreSQL and add background worker queue (e.g. RQ/Celery) for scalability.
5. Add Web UI for students to view schedules online.
6. Analytics dashboard with open rates and delivery metrics.
7. Multi-admin roles, audit logs, and two-factor admin auth.

## 16. Appendix: Example SQL Schema and Seed data

**Seeded time_slots:**

* 1: 09:00 - 10:45
* 2: 10:45 - 12:20
* 3: 13:00 - 14:35
* 4: 14:45 - 16:20
* 5: 16:30 - 18:05

**Seeded directions (examples):**

* Course 1: Math, Math foundations of AI, AI in Math and IT, PM, MOAIS, IB
* Courses 2..4: Math, PM, MOAIS, IB

**SQL Schema:**
A `schema.sql` file is created with the tables described in section 4. (Admin will receive separately if requested.)

---

# Final notes

This document is intentionally thorough to serve as the base for the MVP development. It includes UI flows, data model, scheduler design, and admin functionality. If you want, I can now:

* generate the `schema.sql` and seed file,
* scaffold the aiogram project and FastAPI admin with skeleton files,
* produce a minimal frontend HTML prototype for the admin UI,
* or convert this Markdown into a GitHub-ready `README.md` and a task backlog (Jira/Asana style).
