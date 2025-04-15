import sqlite3

conn = sqlite3.connect('health.db', check_same_thread=False)
cursor = conn.cursor()

# 建表：用户、基本信息、健康信息、对话记录、日志表
cursor.executescript('''
CREATE TABLE IF NOT EXISTS accounts (
    phone TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS profile (
    phone TEXT PRIMARY KEY,
    name TEXT, gender TEXT, birthday TEXT, height TEXT, weight TEXT, 
    blood_pressure TEXT, blood_sugar TEXT
);

CREATE TABLE IF NOT EXISTS health_info (
    phone TEXT PRIMARY KEY,
    chronic TEXT, medication TEXT, avoid TEXT
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    message TEXT, sender TEXT
);

CREATE TABLE IF NOT EXISTS user_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT, action TEXT, detail TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')
conn.commit()

# 供 main.py 调用
__all__ = ["conn", "cursor"]