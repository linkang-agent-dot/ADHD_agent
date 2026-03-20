"""Main message handler: classify user intent and dispatch."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
from utils import safe_reply, monitor_detail, PRIORITY_EMOJI, task_buttons
import database as db
import ai_engine as ai
from handlers.commands import cmd_help, cmd_settings, handle_settings_change
from handlers.tasks import cmd_today, cmd_now, cmd_plan, cmd_review, complete_current
from handlers.rest import rest_now

monitor = logging.getLogger("monitor")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return

    monitor.info("[USER] → %s", text)

    current = await db.get_current_task()
    stats = await db.get_today_stats()
    settings = await db.get_all_settings()
    morning_h = settings.get("morning_hour", str(Config.MORNING_REPORT_HOUR))
    morning_m = settings.get("morning_minute", str(Config.MORNING_REPORT_MINUTE))
    cp_interval = settings.get("checkpoint_interval", str(Config.CHECKPOINT_INTERVAL))

    recent_chat = await db.get_recent_chat(6)
    chat_history_text = ""
    if recent_chat:
        lines = []
        for msg in recent_chat:
            role_label = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role_label}: {msg['content'][:100]}")
        chat_history_text = "\n## 最近对话\n" + "\n".join(lines)

    context_lines = ["## 当前状态"]
    if current:
        context_lines.append(f"- 正在做的任务：「{current['title']}」")
    else:
        context_lines.append(f"- 当前没有正在做的任务")
    context_lines.append(f"- 今日已完成 {stats['completed']} 件，剩余 {stats['remaining']} 件")
    context_lines.append(f"- 早报时间：{int(morning_h):02d}:{int(morning_m):02d}")
    context_lines.append(f"- Checkpoint 间隔：{cp_interval} 分钟")
    context_info = "\n".join(context_lines) + chat_history_text

    await db.add_chat_message("user", text)

    parsed = await ai.classify_message(text, context_info=context_info)

    intent = parsed.get("intent")
    monitor.info("[AI] intent=%s %s", intent, monitor_detail(parsed))

    if intent == "command":
        cmd = parsed.get("command", "")
        if cmd == "today":
            await cmd_today(update, context)
        elif cmd == "now":
            await cmd_now(update, context)
        elif cmd == "plan":
            await cmd_plan(update, context)
        elif cmd == "review":
            await cmd_review(update, context)
        elif cmd == "complete":
            await complete_current(update, context)
        elif cmd == "rest":
            await rest_now(update, context)
        elif cmd == "help":
            await cmd_help(update, context)
        elif cmd == "settings":
            await cmd_settings(update, context)
        else:
            await cmd_today(update, context)
        return

    if intent == "settings":
        monitor.info("[BOT] → settings change: %s=%s", parsed.get("key"), parsed.get("value"))
        await handle_settings_change(update, context, parsed)
        return

    if intent == "chat":
        reply = parsed.get("reply", "有什么我能帮你的？")
        monitor.info("[BOT] → chat: %s", reply[:80])
        await safe_reply(update.message, reply)
        await db.add_chat_message("bot", reply)
        return

    # it's a task
    progress_note = parsed.get("progress_note") or ""
    monitor.info("[BOT] → new task: %s (progress: %s)", parsed.get("title", "?"), progress_note or "none")
    task = await db.add_task(
        title=parsed.get("title", text[:50]),
        description=parsed.get("description", ""),
        priority=parsed.get("priority", "medium"),
        estimated_minutes=parsed.get("estimated_minutes", 0),
        deadline=parsed.get("deadline"),
    )

    if progress_note:
        await db.save_progress_note(task["id"], progress_note)

    await db.add_chat_message("bot", f"已记录任务：{task['title']}" + (f"（{progress_note}）" if progress_note else ""))

    p = PRIORITY_EMOJI.get(task["priority"], "⚪")
    est = f" | 预估 {parsed.get('estimated_minutes', 0)}min" if parsed.get("estimated_minutes") else ""
    progress_line = f"\n📝 进度备注：{progress_note}" if progress_note else ""
    await safe_reply(
        update.message,
        f"📥 已记录：*{task['title']}*\n"
        f"{p} {task['priority']}{est}{progress_line}\n\n"
        f"记住了！不会忘的 🧠",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("▶️ 现在就做", callback_data=f"start:{task['id']}"),
            InlineKeyboardButton("📋 查看今天", callback_data="show_today"),
        ]]),
    )


async def check_progress_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    task_id = context.user_data.get("saving_progress_for")
    if not task_id:
        return False
    note = update.message.text.strip()
    await db.save_progress_note(task_id, note)
    context.user_data.pop("saving_progress_for", None)
    task = await db.get_task(task_id)
    await safe_reply(
        update.message,
        f"💾 进度已保存\n\n"
        f"「{task['title']}」— {note}\n\n"
        f"下次回来做的时候我会提醒你 ✅",
        reply_markup=task_buttons(task_id, task["status"]),
    )
    return True
