import os
import sqlite3

os.makedirs("data", exist_ok=True)

DB_PATH = "data/bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guild_settings (
            guild_id TEXT PRIMARY KEY,
            target_language TEXT DEFAULT 'EN',
            enabled INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


def get_guild_settings(guild_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT target_language, enabled FROM guild_settings WHERE guild_id = ?",
        (str(guild_id),)
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return {"target_language": row[0], "enabled": row[1]}

    return {"target_language": "EN", "enabled": 1}


def set_guild_language(guild_id: int, lang: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO guild_settings (guild_id, target_language, enabled)
        VALUES (?, ?, 1)
        ON CONFLICT(guild_id)
        DO UPDATE SET target_language = excluded.target_language
    """, (str(guild_id), lang))

    conn.commit()
    conn.close()


def set_guild_enabled(guild_id: int, enabled: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO guild_settings (guild_id, target_language, enabled)
        VALUES (?, 'EN', ?)
        ON CONFLICT(guild_id)
        DO UPDATE SET enabled = excluded.enabled
    """, (str(guild_id), int(enabled)))

    conn.commit()
    conn.close()