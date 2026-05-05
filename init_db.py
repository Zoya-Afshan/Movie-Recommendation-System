import sqlite3

conn = sqlite3.connect("users_v2.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    user_id INTEGER,
    movie TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_ratings (
    user_id INTEGER,
    movie TEXT,
    rating INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    movie_id INTEGER,
    movie_title TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
