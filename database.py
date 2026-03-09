import sqlite3
import config

def get_db():
    db = sqlite3.connect(config.DATABASE_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ko TEXT NOT NULL UNIQUE,
            name_en TEXT NOT NULL,
            description_ko TEXT,
            icon TEXT DEFAULT '📚'
        );

        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            english TEXT NOT NULL,
            korean TEXT NOT NULL,
            difficulty INTEGER DEFAULT 1,
            source TEXT DEFAULT 'builtin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence_id INTEGER NOT NULL UNIQUE,
            times_studied INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            mastery_level INTEGER DEFAULT 0,
            last_studied_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sentence_id) REFERENCES sentences(id)
        );

        CREATE TABLE IF NOT EXISTS review_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sentence_id INTEGER NOT NULL UNIQUE,
            easiness_factor REAL DEFAULT 2.5,
            interval_days INTEGER DEFAULT 1,
            repetition_count INTEGER DEFAULT 0,
            next_review_date DATE NOT NULL,
            last_quality INTEGER DEFAULT 0,
            FOREIGN KEY (sentence_id) REFERENCES sentences(id)
        );

        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_type TEXT NOT NULL,
            category_id INTEGER,
            sentences_studied INTEGER DEFAULT 0,
            correct_answers INTEGER DEFAULT 0,
            duration_seconds INTEGER DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)
    db.commit()
    db.close()
