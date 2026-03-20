"""Callback query router for inline button presses."""

import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import task_line, task_buttons
import database as db
import ai_engine as ai
from handlers.checkpoint import handle_checkpoint_response
from handlers.water import handle_water_response
from handlers.rest import schedule_rest_end, rest_from_callback
from handlers.rewards import send_reward

monitor = logging.getLogger("monitor")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    monitor.info("[BUTTON] → %s", data)

    if data.startswith("start:"):
        await start_task(query, context, int(data.split(":")[1]))
    elif data.startswith("complete:"):
        await complete_task(query, context, int(data.split(":")[1]))
    elif data.startswith("postpone:"):
        await postpone_task(query, context, int(data.split(":")[1]))
    elif data.startswith("save_progress:"):
        await prompt_save_progress(query, context, int(data.split(":")[1]))
    elif data == "plan_today":
        await plan_today_callback(query, context)
    elif data == "show_today":
        await show_today_callback(query, context)
    elif data.startswith("rest:"):
        minutes = int(data.split(":")[1])
        await schedule_rest_end(query, context, minutes)
    elif data == "rest_now":
        await rest_from_callback(query, context)
    elif data.startswith("water:"):
        await handle_water_response(query, context, data.split(":")[1])
    elif data.startswith("checkpoint:"):
        response = data.split(":", 1)[1]
        await handle_checkpoint_response(query, context, response)


async def start_task(query, context, task_id: int):
    task = await db.update_task_status(task_id, "in_progress")
    if not task:
        await query.edit_message_text("❌ 找不到这个任务")
        return
    await db.start_work_session(task_id)
    stats = await db.get_today_stats()
    encouragement = await ai.get_encouragement(task["title"], stats["completed"])

    note_text = f"\n\n📝 上次进度：{task['progress_note']}" if task.get("progress_note") else ""
    await query.edit_message_text(
        f"🎯 *开始：{task['title']}*\n\n{encouragement}{note_text}",
        parse_mode="Markdown",
        reply_markup=task_buttons(task_id, "in_progress"),
    )


async def complete_task(query, context, task_id: int):
    task = await db.update_task_status(task_id, "completed")
    await db.end_work_session(task_id)
    if not task:
        await query.edit_message_text("❌ 找不到这个任务")
        return

    remaining = await db.get_pending_tasks()
    stats = await db.get_today_stats()
    nav_text = await ai.navigate_next(task, remaining, stats)

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
    elif remaining:
        buttons.append([
            InlineKeyboardButton("📋 看看还有什么", callback_data="show_today"),
        ])

    await query.edit_message_text(
        nav_text,
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )

    await send_reward(context.bot, query.message.chat_id)


async def postpone_task(query, context, task_id: int):
    task = await db.update_task_status(task_id, "postponed")
    await db.end_work_session(task_id)
    if not task:
        await query.edit_message_text("❌ 找不到这个任务")
        return

    count = task["postpone_count"]
    if count >= 3:
        msg = (
            f"📌 已推迟「{task['title']}」(第 {count} 次)\n\n"
            f"⚠️ 这个任务已经推迟了 {count} 次了\n"
            f"下次 AI 规划时会建议你把它拆成小步骤\n"
            f"小步走也是走 🐢"
        )
    else:
        msg = f"📌 已推迟「{task['title']}」\n没关系，之后再做"

    remaining = await db.get_pending_tasks()
    buttons = []
    if remaining:
        buttons.append([
            InlineKeyboardButton(
                f"▶️ 做别的：{remaining[0]['title'][:20]}",
                callback_data=f"start:{remaining[0]['id']}",
            )
        ])

    await query.edit_message_text(
        msg, reply_markup=InlineKeyboardMarkup(buttons) if buttons else None
    )


async def prompt_save_progress(query, context, task_id: int):
    context.user_data["saving_progress_for"] = task_id
    await query.edit_message_text(
        "💾 请输入当前进度\n\n"
        "下次回来做的时候，我会提醒你做到哪了\n"
        "（直接发消息，简短描述即可）"
    )


async def plan_today_callback(query, context):
    await query.edit_message_text("🧠 AI 正在分析你的任务...")
    tasks = await db.get_pending_tasks()
    plan_text = await ai.plan_daily(tasks)
    await query.edit_message_text(plan_text)


async def show_today_callback(query, context):
    tasks = await db.get_today_tasks()
    if not tasks:
        await query.edit_message_text("📋 今天没有任务")
        return

    lines = ["📋 *今日任务*\n"]
    for i, t in enumerate(tasks, 1):
        lines.append(f"  {i}. {task_line(t)}")

    pending = [t for t in tasks if t["status"] in ("pending", "postponed")]
    buttons = []
    if pending:
        buttons.append([
            InlineKeyboardButton(
                f"▶️ {pending[0]['title'][:25]}",
                callback_data=f"start:{pending[0]['id']}",
            )
        ])

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )
