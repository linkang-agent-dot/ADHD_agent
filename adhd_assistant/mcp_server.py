"""
ADHD Task MCP Server — exposes task management as MCP tools for OpenClaw.

Tools are the AI's classification system: the LLM sees tool descriptions
and decides which to call based on conversation context. No hand-written
intent classification needed.
"""

import os
import random
import sqlite3
from datetime import datetime, date

try:
    from fastmcp import FastMCP
    mcp = FastMCP("adhd-tasks", instructions="ADHD 任务管理工具集。帮助用户记录、管理、完成每日待办任务。")
except ImportError:
    class _StubMCP:
        def tool(self):
            return lambda f: f
    mcp = _StubMCP()

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "adhd.db"))

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}
STATUS_EMOJI = {"completed": "✅", "in_progress": "🎯", "pending": "⏳", "postponed": "📌"}

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
"""


def _get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def _task_line(t: dict) -> str:
    p = PRIORITY_EMOJI.get(t["priority"], "⚪")
    s = STATUS_EMOJI.get(t["status"], "")
    est = f" ({t['estimated_minutes']}min)" if t.get("estimated_minutes") else ""
    postponed = f" [推迟{t['postpone_count']}次]" if t.get("postpone_count", 0) > 0 else ""
    note = f" 📝{t['progress_note']}" if t.get("progress_note") else ""
    return f"{s}{p} [{t['id']}] {t['title']}{est}{postponed}{note}"


# ── Task Tools ──


@mcp.tool()
def add_task(
    title: str,
    priority: str = "medium",
    estimated_minutes: int = 0,
    deadline: str | None = None,
    progress_note: str | None = None,
) -> str:
    """记录一个新的待办任务。当用户描述一件需要去做的事情时调用此工具。
    priority 可选 high/medium/low。如果用户提到了已有进度，填入 progress_note。"""
    db = _get_db()
    now = datetime.now().isoformat()
    cursor = db.execute(
        "INSERT INTO tasks (title, description, priority, estimated_minutes, deadline, created_at, progress_note) VALUES (?, '', ?, ?, ?, ?, ?)",
        (title, priority, estimated_minutes, deadline, now, progress_note or ""),
    )
    db.commit()
    task_id = cursor.lastrowid
    db.close()

    p = PRIORITY_EMOJI.get(priority, "⚪")
    est = f" | 预估 {estimated_minutes}min" if estimated_minutes else ""
    note = f"\n📝 进度备注：{progress_note}" if progress_note else ""
    return f"📥 已记录：{title}\n{p} {priority}{est}{note}\n\n记住了！不会忘的 🧠\n\n任务ID: {task_id}"


@mcp.tool()
def list_today_tasks() -> str:
    """列出今天的所有任务（进行中、待做、已完成）和统计数据。当用户问今天有什么任务、剩下什么、还有多少事时调用。"""
    today = date.today().isoformat()
    db = _get_db()

    rows = db.execute(
        """SELECT * FROM tasks
           WHERE status IN ('pending', 'in_progress', 'postponed')
              OR (status = 'completed' AND DATE(completed_at) = ?)
           ORDER BY
             CASE status WHEN 'in_progress' THEN 0 WHEN 'pending' THEN 1 WHEN 'postponed' THEN 2 ELSE 3 END,
             CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END""",
        (today,),
    ).fetchall()
    db.close()

    if not rows:
        return "📋 今天还没有任务\n\n直接告诉我你要做什么，我帮你记"

    tasks = [dict(r) for r in rows]
    current = [t for t in tasks if t["status"] == "in_progress"]
    pending = [t for t in tasks if t["status"] in ("pending", "postponed")]
    completed = [t for t in tasks if t["status"] == "completed"]

    lines = ["📋 今日任务\n"]
    if current:
        lines.append(f"🎯 正在做：{current[0]['title']}\n")
    if pending:
        lines.append("待处理：")
        for t in pending:
            lines.append(f"  {_task_line(t)}")
        lines.append("")
    if completed:
        lines.append(f"已完成 {len(completed)} 件 ✅")

    lines.append(f"\n📊 待做 {len(pending)} 件 | 已完成 {len(completed)} 件")
    return "\n".join(lines)


@mcp.tool()
def get_current_task() -> str:
    """查看当前正在做的任务和已工作时间。当用户问"我在做什么""现在在做啥"时调用。"""
    db = _get_db()
    row = db.execute("SELECT * FROM tasks WHERE status = 'in_progress' LIMIT 1").fetchone()
    if not row:
        pending = db.execute(
            "SELECT * FROM tasks WHERE status IN ('pending', 'postponed') ORDER BY id LIMIT 1"
        ).fetchone()
        db.close()
        if pending:
            return f"😶 你现在没有在做任何任务\n\n要不要开始「{pending['title']}」(ID:{pending['id']})？"
        return "🎉 没有待做的任务！享受自由吧"

    task = dict(row)
    session = db.execute(
        "SELECT * FROM work_sessions WHERE task_id = ? AND ended_at IS NULL ORDER BY started_at DESC LIMIT 1",
        (task["id"],),
    ).fetchone()
    db.close()

    duration = ""
    if session:
        started = datetime.fromisoformat(session["started_at"])
        mins = int((datetime.now() - started).total_seconds() / 60)
        duration = f"\n⏱ 已经做了 {mins} 分钟"

    note = f"\n📝 上次进度：{task['progress_note']}" if task.get("progress_note") else ""
    p = PRIORITY_EMOJI.get(task["priority"], "")
    return f"🎯 当前任务\n\n{task['title']}\n{p} {task['priority']} 优先级{duration}{note}"


@mcp.tool()
def start_task(task_id: int) -> str:
    """开始做某个任务，标记为进行中并创建工作会话。当用户想开始做某个具体任务时调用。"""
    db = _get_db()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not task:
        db.close()
        return f"❌ 找不到ID为 {task_id} 的任务"

    db.execute("UPDATE tasks SET status = 'pending' WHERE status = 'in_progress'")
    db.execute("UPDATE tasks SET status = 'in_progress' WHERE id = ?", (task_id,))
    now = datetime.now().isoformat()
    db.execute("INSERT INTO work_sessions (task_id, started_at) VALUES (?, ?)", (task_id, now))
    db.commit()
    db.close()

    note = f"\n\n📝 上次进度：{task['progress_note']}" if task["progress_note"] else ""
    return f"🎯 开始：{task['title']}{note}\n\n专注这一件就好，做完告诉我 💪"


@mcp.tool()
def complete_current_task() -> str:
    """完成当前正在进行的任务。当用户说做完了、搞定、完成、弄好了、OK了、结束了时调用。"""
    db = _get_db()
    row = db.execute("SELECT * FROM tasks WHERE status = 'in_progress' LIMIT 1").fetchone()
    if not row:
        db.close()
        return "🤔 你现在没有正在做的任务"

    task = dict(row)
    now = datetime.now().isoformat()
    db.execute("UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?", (now, task["id"]))
    db.execute("UPDATE work_sessions SET ended_at = ? WHERE task_id = ? AND ended_at IS NULL", (now, task["id"]))
    db.commit()

    completed_count = db.execute(
        "SELECT COUNT(*) as cnt FROM tasks WHERE DATE(completed_at) = ?", (date.today().isoformat(),)
    ).fetchone()["cnt"]

    remaining = db.execute(
        "SELECT * FROM tasks WHERE status IN ('pending', 'postponed') ORDER BY id"
    ).fetchall()
    db.close()

    lines = [f"✅ 完成了「{task['title']}」！今天已完成 {completed_count} 件\n"]
    if remaining:
        next_task = dict(remaining[0])
        lines.append(f"📌 建议下一个：{next_task['title']} (ID:{next_task['id']})")
        lines.append("要开始吗？还是先休息一下？")
    else:
        lines.append("🎉 所有任务都搞定了！去做点让自己开心的事吧")

    return "\n".join(lines)


@mcp.tool()
def postpone_task(task_id: int) -> str:
    """推迟一个任务。当用户想推迟或暂时不做某个任务时调用。"""
    db = _get_db()
    db.execute("UPDATE tasks SET status = 'postponed', postpone_count = postpone_count + 1 WHERE id = ?", (task_id,))
    db.execute("UPDATE work_sessions SET ended_at = ? WHERE task_id = ? AND ended_at IS NULL",
               (datetime.now().isoformat(), task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    db.close()

    if not task:
        return f"❌ 找不到ID为 {task_id} 的任务"

    count = task["postpone_count"]
    if count >= 3:
        return (
            f"📌 已推迟「{task['title']}」(第 {count} 次)\n\n"
            f"⚠️ 已经推迟了 {count} 次了，要不要把它拆成小步骤？\n小步走也是走 🐢"
        )
    return f"📌 已推迟「{task['title']}」\n没关系，之后再做"


@mcp.tool()
def save_progress(task_id: int, note: str) -> str:
    """保存某个任务的进度备注。当用户描述自己做到哪了、还剩多少时调用。"""
    db = _get_db()
    db.execute("UPDATE tasks SET progress_note = ? WHERE id = ?", (note, task_id))
    db.commit()
    task = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    db.close()
    if not task:
        return f"❌ 找不到ID为 {task_id} 的任务"
    return f"💾 进度已保存\n\n「{task['title']}」— {note}\n\n下次回来做的时候我会提醒你 ✅"


# ── Planning & Review ──


@mcp.tool()
def plan_today() -> str:
    """分析今天的待办任务，按优先级和预估时间生成执行建议。当用户想规划今天、问该先做什么、排优先级时调用。"""
    db = _get_db()
    rows = db.execute(
        "SELECT * FROM tasks WHERE status IN ('pending', 'in_progress', 'postponed') ORDER BY id"
    ).fetchall()
    db.close()

    if not rows:
        return "📋 今天没有待办任务\n\n想加点什么？直接告诉我"

    tasks = [dict(r) for r in rows]
    high = [t for t in tasks if t["priority"] == "high"]
    medium = [t for t in tasks if t["priority"] == "medium"]
    low = [t for t in tasks if t["priority"] == "low"]

    total_minutes = sum(t.get("estimated_minutes", 0) for t in tasks)

    lines = ["🧠 今日规划\n"]
    if high:
        lines.append("🔴 必须做：")
        for t in high:
            lines.append(f"  {_task_line(t)}")
    if medium:
        lines.append("🟡 争取做：")
        for t in medium:
            lines.append(f"  {_task_line(t)}")
    if low:
        lines.append("⚪ 有空再说：")
        for t in low:
            lines.append(f"  {_task_line(t)}")

    lines.append(f"\n📊 共 {len(tasks)} 件 | 预估 {total_minutes} 分钟")
    if total_minutes > 480:
        lines.append("⚠️ 今天安排太满了，建议砍掉一些低优先级的")
    elif total_minutes > 300:
        lines.append("📌 工作量适中，记得中间休息")
    else:
        lines.append("👍 工作量合理，加油！")

    if high:
        lines.append(f"\n💡 建议先做：{high[0]['title']} (ID:{high[0]['id']})")

    return "\n".join(lines)


@mcp.tool()
def daily_review() -> str:
    """生成今日复盘报告：完成了什么、没完成什么、工作时长统计。当用户想复盘、问今天怎么样时调用。"""
    today = date.today().isoformat()
    db = _get_db()

    completed = db.execute(
        "SELECT * FROM tasks WHERE status = 'completed' AND DATE(completed_at) = ?", (today,)
    ).fetchall()
    not_done = db.execute(
        "SELECT * FROM tasks WHERE status IN ('pending', 'postponed')"
    ).fetchall()

    work_row = db.execute(
        """SELECT SUM(
             CAST((julianday(COALESCE(ended_at, datetime('now'))) - julianday(started_at)) * 24 * 60 AS INTEGER)
           ) as total_minutes FROM work_sessions WHERE DATE(started_at) = ?""",
        (today,),
    ).fetchone()
    work_minutes = work_row["total_minutes"] or 0
    db.close()

    completed_list = [dict(r) for r in completed]
    not_done_list = [dict(r) for r in not_done]
    total = len(completed_list) + len(not_done_list)

    lines = [f"📊 今日复盘\n"]
    lines.append(f"完成 {len(completed_list)}/{total} 件 | 工作 {work_minutes} 分钟\n")

    if completed_list:
        lines.append("✅ 已完成：")
        for t in completed_list:
            lines.append(f"  {t['title']}")

    if not_done_list:
        lines.append("\n⏳ 未完成：")
        for t in not_done_list:
            postponed = f" (推迟{t['postpone_count']}次)" if t.get("postpone_count", 0) > 0 else ""
            lines.append(f"  {t['title']}{postponed}")

    lines.append("\n辛苦了，早点休息 🌙")
    return "\n".join(lines)


# ── Settings ──


@mcp.tool()
def get_settings() -> str:
    """查看当前所有配置。当用户想看设置、问当前配置时调用。"""
    db = _get_db()
    rows = db.execute("SELECT key, value FROM user_settings").fetchall()
    db.close()
    settings = {r["key"]: r["value"] for r in rows}

    morning_h = settings.get("morning_hour", "9")
    morning_m = settings.get("morning_minute", "0")
    checkpoint = settings.get("checkpoint_interval", "120")
    rest_int = settings.get("rest_interval", "90")

    return (
        f"⚙️ 当前设置\n\n"
        f"🌅 早报时间：{int(morning_h):02d}:{int(morning_m):02d}\n"
        f"⏰ Checkpoint 间隔：{checkpoint} 分钟\n"
        f"☕ 连续工作提醒：{rest_int} 分钟\n\n"
        f"💡 直接告诉我你想改什么，比如「早报改到10点」"
    )


@mcp.tool()
def update_setting(key: str, value: str) -> str:
    """修改一个配置项。可改的 key: morning_hour, morning_minute, checkpoint_interval, rest_interval。
    当用户想改时间、调整间隔、觉得提醒太早/太晚/太频繁时调用。"""
    VALID_KEYS = {
        "morning_hour": ("早报小时", 0, 23),
        "morning_minute": ("早报分钟", 0, 59),
        "checkpoint_interval": ("Checkpoint间隔(分钟)", 15, 480),
        "rest_interval": ("连续工作提醒(分钟)", 30, 300),
    }

    if key not in VALID_KEYS:
        return f"🤔 不支持修改 {key}\n\n可改的有：{', '.join(VALID_KEYS.keys())}"

    try:
        int_value = int(value)
    except ValueError:
        return "⚠️ 数值格式不对，给个数字就行"

    label, min_v, max_v = VALID_KEYS[key]
    if not (min_v <= int_value <= max_v):
        return f"⚠️ {label} 的范围是 {min_v}-{max_v}，{int_value} 超出范围了"

    db = _get_db()
    now = datetime.now().isoformat()
    db.execute(
        "INSERT INTO user_settings (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = ?",
        (key, str(int_value), now, str(int_value), now),
    )
    db.commit()
    db.close()
    return f"✅ {label}已更新为 {int_value}"


# ── Reward ──


REWARD_LINES = [
    "做完了就是最棒的！来，看看这个 👀",
    "辛苦了～ 奖励你一张图 🎁",
    "任务完成！解锁奖励 🔓",
    "今天的你很厉害，收好 ✨",
    "能做完就比90%的人强，给你看点好东西 🏆",
    "效率王！奖励已到账 💎",
    "完成 = 多巴胺，来一发 🧠",
    "你值得拥有这个 🌟",
]

WAIFU_CATEGORIES = ["waifu", "neko", "shinobu", "megumin"]


@mcp.tool()
def send_reward_image() -> str:
    """完成任务后发送一张随机动漫图片作为奖励。任务完成后应该调用此工具给用户惊喜。"""
    import urllib.request
    import json as _json

    cat = random.choice(WAIFU_CATEGORIES)
    url = f"https://api.waifu.pics/sfw/{cat}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ADHD-Bot/1.0"})
        resp = urllib.request.urlopen(req, timeout=8)
        data = _json.loads(resp.read())
        image_url = data.get("url", "")
        if image_url:
            caption = random.choice(REWARD_LINES)
            return f"{caption}\n\n{image_url}"
    except Exception:
        pass
    return random.choice(REWARD_LINES)


if __name__ == "__main__":
    mcp.run()
