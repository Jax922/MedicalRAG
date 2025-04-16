# --- backend/db.py ---
import sqlite3

conn = sqlite3.connect('health.db', check_same_thread=False)
cursor = conn.cursor()

# 建表：用户、基本信息、对话记录、日志表、饮食推荐
cursor.executescript('''
CREATE TABLE IF NOT EXISTS accounts (
    phone TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS profile (
    phone TEXT PRIMARY KEY,
    gender TEXT,
    age TEXT,
    height TEXT,
    weight TEXT,
    blood_pressure TEXT,
    blood_sugar TEXT
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message TEXT,
    sender TEXT
);

CREATE TABLE IF NOT EXISTS user_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    action TEXT,
    detail TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS diet_recommendation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    date TEXT,
    recommendation TEXT,  -- JSON string containing meals
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

conn.commit()
__all__ = ["conn", "cursor"]