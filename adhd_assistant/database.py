import aiosqlite
import os
from datetime import datetime, date
from config import Config

DB_PATH = Config.DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('high', 'medium', 'low')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'postponed', 'cancelled')),
    estimated_minutes INTEGER DEFAULT 0,
    deadline TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    postpone_count INTEGER DEFAULT 0,
    progress_note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS work_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS daily_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_date TEXT NOT NULL UNIQUE,
    task_order TEXT NOT NULL DEFAULT '[]',
    ai_summary TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkpoint_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_response TEXT DEFAULT '',
    was_on_track INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS user_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL CHECK(role IN ('user', 'bot')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


async def get_db() -> aiosqlite.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.executescript(SCHEMA)
    await db.commit()
    await db.close()


# ── Task CRUD ──


async def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    estimated_minutes: int = 0,
    deadline: str | None = None,
) -> dict:
    db = await get_db()
    now = datetime.now().isoformat()
    cursor = await db.execute(
        """INSERT INTO tasks (title, description, priority, estimated_minutes, deadline, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, priority, estimated_minutes, deadline, now),
    )
    await db.commit()
    task_id = cursor.lastrowid
    await db.close()
    return {"id": task_id, "title": title, "priority": priority}


async def get_task(task_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None


async def get_pending_tasks() -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM tasks WHERE status IN ('pending', 'in_progress', 'postponed') ORDER BY id"
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def get_today_tasks() -> list[dict]:
    today = date.today().isoformat()
    db = await get_db()
    cursor = await db.execute(
        """SELECT * FROM tasks
           WHERE status IN ('pending', 'in_progress', 'postponed')
              OR (status = 'completed' AND DATE(completed_at) = ?)
           ORDER BY
             CASE status WHEN 'in_progress' THEN 0 WHEN 'pending' THEN 1 WHEN 'postponed' THEN 2 ELSE 3 END,
             CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END
        """,
        (today,),
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def get_current_task() -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM tasks WHERE status = 'in_progress' LIMIT 1"
    )
    row = await cursor.fetchone()
    await db.close()
    if row:
        return dict(row)
    return None


async def update_task_status(task_id: int, status: str, note: str = "") -> dict | None:
    db = await get_db()
    now = datetime.now().isoformat()

    if status == "completed":
        await db.execute(
            "UPDATE tasks SET status = ?, completed_at = ?, progress_note = ? WHERE id = ?",
            (status, now, note, task_id),
        )
    elif status == "postponed":
        await db.execute(
            "UPDATE tasks SET status = ?, postpone_count = postpone_count + 1 WHERE id = ?",
            (status, task_id),
        )
    elif status == "in_progress":
        # only one task in_progress at a time
        await db.execute(
            "UPDATE tasks SET status = 'pending' WHERE status = 'in_progress'"
        )
        await db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)
        )
    else:
        await db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", (status, task_id)
        )

    await db.commit()
    cursor = await db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


async def save_progress_note(task_id: int, note: str):
    db = await get_db()
    await db.execute(
        "UPDATE tasks SET progress_note = ? WHERE id = ?", (note, task_id)
    )
    await db.commit()
    await db.close()


# ── Work Sessions ──


async def start_work_session(task_id: int) -> int:
    db = await get_db()
    now = datetime.now().isoformat()
    cursor = await db.execute(
        "INSERT INTO work_sessions (task_id, started_at) VALUES (?, ?)",
        (task_id, now),
    )
    await db.commit()
    session_id = cursor.lastrowid
    await db.close()
    return session_id


async def end_work_session(task_id: int):
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        "UPDATE work_sessions SET ended_at = ? WHERE task_id = ? AND ended_at IS NULL",
        (now, task_id),
    )
    await db.commit()
    await db.close()


async def get_active_session() -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM work_sessions WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 1"
    )
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else None


# ── Daily Plan ──


async def save_daily_plan(plan_date: str, task_order: str, ai_summary: str):
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO daily_plans (plan_date, task_order, ai_summary, created_at)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(plan_date) DO UPDATE SET task_order = ?, ai_summary = ?""",
        (plan_date, task_order, ai_summary, now, task_order, ai_summary),
    )
    await db.commit()
    await db.close()


# ── Checkpoint Logs ──


async def log_checkpoint(user_response: str, was_on_track: bool):
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        "INSERT INTO checkpoint_logs (timestamp, user_response, was_on_track) VALUES (?, ?, ?)",
        (now, user_response, 1 if was_on_track else 0),
    )
    await db.commit()
    await db.close()


# ── Stats ──


async def get_setting(key: str, default: str | None = None) -> str | None:
    db = await get_db()
    cursor = await db.execute("SELECT value FROM user_settings WHERE key = ?", (key,))
    row = await cursor.fetchone()
    await db.close()
    return row["value"] if row else default


async def set_setting(key: str, value: str):
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        """INSERT INTO user_settings (key, value, updated_at) VALUES (?, ?, ?)
           ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?""",
        (key, value, now, value, now),
    )
    await db.commit()
    await db.close()


async def get_all_settings() -> dict:
    db = await get_db()
    cursor = await db.execute("SELECT key, value FROM user_settings")
    rows = await cursor.fetchall()
    await db.close()
    return {r["key"]: r["value"] for r in rows}


async def add_chat_message(role: str, content: str):
    db = await get_db()
    now = datetime.now().isoformat()
    await db.execute(
        "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, now),
    )
    await db.execute(
        "DELETE FROM chat_history WHERE id NOT IN (SELECT id FROM chat_history ORDER BY id DESC LIMIT 50)"
    )
    await db.commit()
    await db.close()


async def get_recent_chat(limit: int = 6) -> list[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in reversed(rows)]


async def get_today_stats() -> dict:
    today = date.today().isoformat()
    db = await get_db()

    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM tasks WHERE DATE(completed_at) = ?", (today,)
    )
    completed = (await cursor.fetchone())["cnt"]

    cursor = await db.execute(
        "SELECT COUNT(*) as cnt FROM tasks WHERE status IN ('pending', 'in_progress', 'postponed')"
    )
    remaining = (await cursor.fetchone())["cnt"]

    cursor = await db.execute(
        """SELECT SUM(
             CAST((julianday(COALESCE(ended_at, datetime('now'))) - julianday(started_at)) * 24 * 60 AS INTEGER)
           ) as total_minutes
           FROM work_sessions WHERE DATE(started_at) = ?""",
        (today,),
    )
    row = await cursor.fetchone()
    work_minutes = row["total_minutes"] or 0

    await db.close()
    return {
        "completed": completed,
        "remaining": remaining,
        "total": completed + remaining,
        "work_minutes": work_minutes,
    }
