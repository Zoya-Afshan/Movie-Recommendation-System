import sqlite3

conn = sqlite3.connect("users_v2.db", check_same_thread=False)
cursor = conn.cursor()

# ---------------- USERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# ---------------- WATCH HISTORY ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    user_id INTEGER,
    movie TEXT
)
""")

# ---------------- USER RATINGS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_ratings (
    user_id INTEGER,
    movie TEXT,
    rating INTEGER,
    UNIQUE(user_id, movie)
)
""")

# ---------------- FAVORITES TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER,
    movie TEXT,
    UNIQUE(user_id, movie)
)
""")

conn.commit()


# ---------------- GET USER ID ----------------
def get_user_id(username):

    cursor.execute(
        "SELECT id FROM users WHERE username=?",
        (username,)
    )

    r = cursor.fetchone()

    return r[0] if r else None


# ---------------- ADD WATCH HISTORY ----------------
def add_watch_history(username, movie):

    uid = get_user_id(username)

    if not uid:
        return

    # Remove movie if already in history
    cursor.execute(
        "DELETE FROM history WHERE user_id=? AND movie=?",
        (uid, movie)
    )

    # Insert movie again (latest position)
    cursor.execute(
        "INSERT INTO history (user_id, movie) VALUES (?,?)",
        (uid, movie)
    )



    conn.commit()


# ---------------- GET WATCH HISTORY ----------------
def get_watch_history(username):

    uid = get_user_id(username)

    if not uid:
        return []

    cursor.execute(
        "SELECT movie FROM history WHERE user_id=? ORDER BY id DESC ",
        (uid,)
    )

    return [x[0] for x in cursor.fetchall()]
# ---------------- clear WATCH HISTORY ----------------

def clear_watch_history(username):

    uid = get_user_id(username)

    if not uid:
        return

    cursor.execute(
        "DELETE FROM history WHERE user_id=?",
        (uid,)
    )

    conn.commit()

# ---------------- DELETE ONE WATCH HISTORY ----------------

def delete_from_history(username, movie):

    uid = get_user_id(username)

    if not uid:
        return

    cursor.execute(
        "DELETE FROM history WHERE user_id=? AND movie=?",
        (uid, movie)
    )

    conn.commit()
# ================= FAVORITES FUNCTIONS =================

# -------- ADD FAVORITE --------
def add_favorite(username, movie):

    uid = get_user_id(username)

    if not uid:
        return

    try:
        cursor.execute(
            "INSERT INTO favorites (user_id, movie) VALUES (?,?)",
            (uid, movie)
        )
        conn.commit()

    except:
        pass


# -------- REMOVE FAVORITE --------
def remove_favorite(username, movie):

    uid = get_user_id(username)

    if not uid:
        return

    cursor.execute(
        "DELETE FROM favorites WHERE user_id=? AND movie=?",
        (uid, movie)
    )

    conn.commit()


# -------- GET FAVORITES --------
def get_favorites(username):

    uid = get_user_id(username)

    if not uid:
        return []

    cursor.execute(
        "SELECT movie FROM favorites WHERE user_id=?",
        (uid,)
    )

    return [x[0] for x in cursor.fetchall()]


# -------- CHECK IF MOVIE IS FAVORITE --------
def is_favorite(username, movie):

    uid = get_user_id(username)

    if not uid:
        return False

    cursor.execute(
        "SELECT 1 FROM favorites WHERE user_id=? AND movie=?",
        (uid, movie)
    )

    return cursor.fetchone() is not None

