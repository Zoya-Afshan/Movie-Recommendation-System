import sqlite3

conn = sqlite3.connect("users_v2.db", check_same_thread=False)
cursor = conn.cursor()

def signup(username, password):
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        return True
    except:
        return False

def login(username, password):
    cursor.execute(
        "SELECT id FROM users WHERE username=? AND password=?",
        (username, password)
    )
    return cursor.fetchone()
