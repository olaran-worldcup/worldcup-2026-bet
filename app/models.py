import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'worldcup.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            submitted INTEGER DEFAULT 0,
            submitted_at TEXT,
            bet_data TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id)
        );

        CREATE TABLE IF NOT EXISTS admin_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id TEXT UNIQUE NOT NULL,
            result TEXT NOT NULL,
            entered_at TEXT DEFAULT (datetime('now'))
        );
    ''')
    # Create default admin user
    conn.execute(
        "INSERT OR IGNORE INTO users (login, display_name, is_admin) VALUES (?, ?, ?)",
        ('admin', 'Administrator', 1)
    )
    conn.commit()
    conn.close()
