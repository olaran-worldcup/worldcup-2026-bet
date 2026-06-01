import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get('DATABASE_URL', '')


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS bets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id),
            submitted INTEGER DEFAULT 0,
            submitted_at TEXT,
            bet_data TEXT NOT NULL DEFAULT '{}',
            resubmit_allowed INTEGER DEFAULT 0,
            UNIQUE(user_id)
        );
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS admin_results (
            id SERIAL PRIMARY KEY,
            match_id TEXT UNIQUE NOT NULL,
            result TEXT NOT NULL,
            entered_at TIMESTAMP DEFAULT NOW()
        );
    ''')
    # Add resubmit_allowed column if it doesn't exist (migration for existing DBs)
    cur.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'bets' AND column_name = 'resubmit_allowed'
            ) THEN
                ALTER TABLE bets ADD COLUMN resubmit_allowed INTEGER DEFAULT 0;
                -- Allow all currently submitted bets to resubmit once
                UPDATE bets SET resubmit_allowed = 1 WHERE submitted = 1;
            END IF;
        END $$;
    """)
    # Create default admin user if not exists
    cur.execute(
        "INSERT INTO users (login, display_name, is_admin) VALUES (%s, %s, %s) ON CONFLICT (login) DO NOTHING",
        ('admin', 'Administrator', 1)
    )
    conn.commit()
    cur.close()
    conn.close()
