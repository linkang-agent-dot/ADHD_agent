"""Task handlers: /today, /now, /plan, /review, task CRUD."""

import re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import safe_reply, task_line, task_buttons, PRIORITY_EMOJI
import database as db
import ai_engine as ai
from handlers.rewards import send_reward


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await db.get_today_tasks()
    if not tasks:
        await safe_reply(update.message, "📋 今天还没有任务\n\n直接发消息给我就能添加任务")
        return

    current = next((t for t in tasks if t["status"] == "in_progress"), None)
    pending = [t for t in tasks if t["status"] in ("pending", "postponed")]
    completed = [t for t in tasks if t["status"] == "completed"]

    lines = ["📋 *今日任务*\n"]
    if current:
        lines.append(f"🎯 正在做：*{current['title']}*\n")
    if pending:
        lines.append("待处理：")
        for i, t in enumerate(pending, 1):
            lines.append(f"  {i}. {task_line(t, show_status=False)}")
        lines.append("")
    if completed:
        lines.append(f"已完成 {len(completed)} 件 ✅")

    stats = await db.get_today_stats()
    lines.append(f"\n📊 已工作 {stats['work_minutes']} 分钟")

    buttons = []
    if pending:
        buttons.append([
            InlineKeyboardButton(
                f"▶️ 开始：{pending[0]['title'][:20]}",
                callback_data=f"start:{pending[0]['id']}",
            )
        ])
    buttons.append([InlineKeyboardButton("🧠 AI 规划今天", callback_data="plan_today")])

    await safe_reply(
        update.message,
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )


async def cmd_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await db.get_current_task()
    if not current:
        tasks = await db.get_pending_tasks()
        if tasks:
            await safe_reply(
                update.message,
                "😶 你现在没有在做任何任务\n\n要不要开始一个？",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        f"▶️ {tasks[0]['title'][:25]}",
                        callback_data=f"start:{tasks[0]['id']}",
                    )
                ]]),
            )
        else:
            await safe_reply(update.message, "🎉 没有待做的任务！享受自由吧")
        return

    note = f"\n📝 上次进度：{current['progress_note']}" if current.get("progress_note") else ""
    session = await db.get_active_session()
    duration = ""
    if session:
        started = datetime.fromisoformat(session["started_at"])
        mins = int((datetime.now() - started).total_seconds() / 60)
        duration = f"\n⏱ 已经做了 {mins} 分钟"

    await safe_reply(
        update.message,
        f"🎯 *当前任务*\n\n"
        f"*{current['title']}*\n"
        f"{PRIORITY_EMOJI.get(current['priority'], '')} {current['priority']} 优先级"
        f"{duration}{note}",
        parse_mode="Markdown",
        reply_markup=task_buttons(current["id"], current["status"]),
    )


async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update.message, "🧠 AI 正在分析你的任务...")
    tasks = await db.get_pending_tasks()
    plan_text = await ai.plan_daily(tasks)
    await safe_reply(update.message, plan_text)


async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(update.message, "📊 正在生成今日复盘...")
    tasks = await db.get_today_tasks()
    stats = await db.get_today_stats()
    review = await ai.daily_review(tasks, stats)
    await safe_reply(update.message, review)


async def complete_current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await db.get_current_task()
    if not current:
        await safe_reply(update.message, "🤔 你现在没有正在做的任务\n发 /today 看看有什么要做的")
        return
    await db.update_task_status(current["id"], "completed")
    await db.end_work_session(current["id"])

    remaining = await db.get_pending_tasks()
    stats = await db.get_today_stats()
    nav_text = await ai.navigate_next(current, remaining, stats)

    next_task_id = None
    match = re.search(r"\[NEXT:(\d+)]", nav_text)
    if match:
        next_task_id = int(match.group(1))
        nav_text = nav_text.replace(match.group(0), "").strip()

    buttons = []
    if next_task_id:
        buttons.append([
            InlineKeyboardButton("▶️ 开始下一件", callback_data=f"start:{next_task_id}"),
            InlineKeyboardButton("☕ 先休息5分钟", callback_data="rest:5"),
        ])

    await safe_reply(
        update.message,
        nav_text,
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )

    await send_reward(context.bot, update.effective_chat.id)
