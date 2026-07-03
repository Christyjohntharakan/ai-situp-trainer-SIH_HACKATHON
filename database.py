import sqlite3

DB = "athletes.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS athletes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        reps INTEGER,
        badge TEXT,
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_result(name, reps, badge, feedback):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO athletes(name, reps, badge, feedback)
    VALUES (?,?,?,?)
    """, (name, reps, badge, feedback))

    conn.commit()
    conn.close()


def get_leaderboard():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    SELECT name, reps, badge, timestamp
    FROM athletes
    ORDER BY reps DESC
    """)

    data = cur.fetchall()
    conn.close()
    return data