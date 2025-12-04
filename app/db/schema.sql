-- ===============================================
-- ScheduleBot Database Schema
-- SQLite Database for AGU Schedule Bot
-- ===============================================

-- === Users Table ===
-- Stores registered bot users (students)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER NOT NULL UNIQUE,              -- Telegram user ID
    name TEXT NOT NULL,                          -- Student name
    course INTEGER NOT NULL CHECK(course BETWEEN 1 AND 4),  -- Course number (1-4)
    direction_id INTEGER NOT NULL,               -- FK to directions
    remind_before BOOLEAN NOT NULL DEFAULT 1,    -- Enable 5-min reminders
    paused_until TEXT,                           -- ISO date string (null = not paused)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);
CREATE INDEX IF NOT EXISTS idx_users_direction ON users(direction_id);
CREATE INDEX IF NOT EXISTS idx_users_paused ON users(paused_until);


-- === Directions Table ===
-- Student directions/specializations by course
CREATE TABLE IF NOT EXISTS directions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                          -- Direction name (e.g., "Информатика и ВТ")
    course INTEGER NOT NULL CHECK(course BETWEEN 1 AND 4),  -- Course number
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, course)                         -- One direction per course
);

CREATE INDEX IF NOT EXISTS idx_directions_course ON directions(course);


-- === Time Slots Table ===
-- Fixed time slots for classes (5 slots per day)
CREATE TABLE IF NOT EXISTS time_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_number INTEGER NOT NULL UNIQUE CHECK(slot_number BETWEEN 1 AND 5),
    start_time TEXT NOT NULL,                    -- HH:MM format
    end_time TEXT NOT NULL,                      -- HH:MM format
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_time_slots_number ON time_slots(slot_number);


-- === Pairs Table ===
-- Class schedule entries (lectures, seminars, labs)
CREATE TABLE IF NOT EXISTS pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                         -- Class name (e.g., "Математика")
    teacher TEXT NOT NULL,                       -- Teacher full name
    room TEXT NOT NULL,                          -- Room number/location
    type TEXT NOT NULL DEFAULT 'Лекция',         -- Class type (Лекция/Семинар/Лаб. работа)
    day_of_week INTEGER NOT NULL CHECK(day_of_week BETWEEN 0 AND 6),  -- 0=Monday, 6=Sunday
    time_slot_id INTEGER NOT NULL,               -- FK to time_slots
    extra_link TEXT,                             -- Optional URL (e.g., Zoom link)
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (time_slot_id) REFERENCES time_slots(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_pairs_day ON pairs(day_of_week);
CREATE INDEX IF NOT EXISTS idx_pairs_slot ON pairs(time_slot_id);


-- === Pair Assignments Table ===
-- Many-to-many relationship: pairs <-> directions
-- One pair can be assigned to multiple directions
CREATE TABLE IF NOT EXISTS pair_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id INTEGER NOT NULL,                    -- FK to pairs
    direction_id INTEGER NOT NULL,               -- FK to directions
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (pair_id) REFERENCES pairs(id) ON DELETE CASCADE,
    FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE CASCADE,
    UNIQUE(pair_id, direction_id)                -- Prevent duplicate assignments
);

CREATE INDEX IF NOT EXISTS idx_assignments_pair ON pair_assignments(pair_id);
CREATE INDEX IF NOT EXISTS idx_assignments_direction ON pair_assignments(direction_id);


-- === Delivery Log Table ===
-- Tracks message delivery status for monitoring
CREATE TABLE IF NOT EXISTS delivery_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,                    -- FK to users (or tg_id if user deleted)
    message_type TEXT NOT NULL,                  -- 'morning', 'reminder', 'broadcast'
    status TEXT NOT NULL,                        -- 'sent', 'error'
    error_message TEXT,                          -- Error details if failed
    delivered_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_delivery_log_user ON delivery_log(user_id);
CREATE INDEX IF NOT EXISTS idx_delivery_log_type ON delivery_log(message_type);
CREATE INDEX IF NOT EXISTS idx_delivery_log_status ON delivery_log(status);
CREATE INDEX IF NOT EXISTS idx_delivery_log_date ON delivery_log(delivered_at);


-- === Subjects Table ===
-- Stores unique subject names for autocomplete
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                   -- Subject name
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_subjects_name ON subjects(name);


-- === Teachers Table ===
-- Stores unique teacher names for autocomplete
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                   -- Teacher full name (FIO)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_teachers_name ON teachers(name);


-- === Payments Table ===
-- Stores Telegram Stars donation transactions
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_id INTEGER NOT NULL,                      -- Telegram user ID (donor)
    amount INTEGER NOT NULL,                     -- Amount in Stars
    currency TEXT NOT NULL DEFAULT 'XTR',        -- Currency code (XTR for Stars)
    payload TEXT,                                -- Custom payload/reference
    status TEXT NOT NULL DEFAULT 'pending',      -- Status: 'pending', 'completed', 'failed'
    telegram_payment_id TEXT,                    -- Telegram's payment charge ID
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_payments_tg_id ON payments(tg_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(created_at);
