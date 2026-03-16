"""
Telegram Bot — the user-facing interface.

Handles:
  - Text messages → capture tasks / natural language commands
  - Button callbacks → complete, postpone, start, rest
  - Commands → /start, /today, /now, /plan, /review
"""

import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import Config
import database as db
import ai_engine as ai

logger = logging.getLogger(__name__)

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}
STATUS_EMOJI = {"completed": "✅", "in_progress": "🎯", "pending": "⏳", "postponed": "📌", "cancelled": "🚫"}


# ── Helpers ──


def task_line(t: dict, show_status: bool = True) -> str:
    p = PRIORITY_EMOJI.get(t["priority"], "⚪")
    s = STATUS_EMOJI.get(t["status"], "")
    est = f" ({t['estimated_minutes']}min)" if t.get("estimated_minutes") else ""
    postponed = f" [推迟{t['postpone_count']}次]" if t.get("postpone_count", 0) > 0 else ""
    prefix = f"{s} " if show_status else f"{p} "
    return f"{prefix}{t['title']}{est}{postponed}"


def task_buttons(task_id: int, status: str) -> InlineKeyboardMarkup:
    buttons = []
    if status in ("pending", "postponed"):
        buttons.append([
            InlineKeyboardButton("▶️ 开始做", callback_data=f"start:{task_id}"),
            InlineKeyboardButton("📌 推迟", callback_data=f"postpone:{task_id}"),
        ])
    elif status == "in_progress":
        buttons.append([
            InlineKeyboardButton("✅ 完成", callback_data=f"complete:{task_id}"),
            InlineKeyboardButton("📌 推迟", callback_data=f"postpone:{task_id}"),
        ])
        buttons.append([
            InlineKeyboardButton("💾 记录进度", callback_data=f"save_progress:{task_id}"),
        ])
    return InlineKeyboardMarkup(buttons)


# ── Command Handlers ──


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"👋 你好！我是你的 ADHD 任务助手\n\n"
        f"我会帮你：\n"
        f"📥 记住所有事情（直接发消息给我）\n"
        f"🧠 每天帮你规划（AI 评估负荷）\n"
        f"🧭 完成后告诉你下一步做什么\n"
        f"⏰ 定时提醒你（不让你跑偏）\n"
        f"🫂 在你累的时候安慰你\n\n"
        f"你的 Chat ID: `{chat_id}`\n"
        f"请把这个 ID 填到 .env 文件的 TELEGRAM_CHAT_ID 里\n\n"
        f"📝 现在就发消息给我，记录你的第一个任务吧！",
        parse_mode="Markdown",
    )


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await db.get_today_tasks()
    if not tasks:
        await update.message.reply_text("📋 今天还没有任务\n\n直接发消息给我就能添加任务")
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

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )


async def cmd_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await db.get_current_task()
    if not current:
        tasks = await db.get_pending_tasks()
        if tasks:
            await update.message.reply_text(
                "😶 你现在没有在做任何任务\n\n要不要开始一个？",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        f"▶️ {tasks[0]['title'][:25]}",
                        callback_data=f"start:{tasks[0]['id']}",
                    )
                ]]),
            )
        else:
            await update.message.reply_text("🎉 没有待做的任务！享受自由吧")
        return

    note = f"\n📝 上次进度：{current['progress_note']}" if current.get("progress_note") else ""
    session = await db.get_active_session()
    duration = ""
    if session:
        from datetime import datetime
        started = datetime.fromisoformat(session["started_at"])
        mins = int((datetime.now() - started).total_seconds() / 60)
        duration = f"\n⏱ 已经做了 {mins} 分钟"

    await update.message.reply_text(
        f"🎯 *当前任务*\n\n"
        f"*{current['title']}*\n"
        f"{PRIORITY_EMOJI.get(current['priority'], '')} {current['priority']} 优先级"
        f"{duration}{note}",
        parse_mode="Markdown",
        reply_markup=task_buttons(current["id"], current["status"]),
    )


async def cmd_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 AI 正在分析你的任务...")
    tasks = await db.get_pending_tasks()
    plan_text = await ai.plan_daily(tasks)
    await update.message.reply_text(plan_text)


async def cmd_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 正在生成今日复盘...")
    tasks = await db.get_today_tasks()
    stats = await db.get_today_stats()
    review = await ai.daily_review(tasks, stats)
    await update.message.reply_text(review)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *使用指南*\n\n"
        "*记录任务*\n"
        "直接发消息就是记录任务\n"
        "例：明天和策划对需求\n"
        "例：紧急 提交活动配置\n\n"
        "*快捷命令*\n"
        "/today — 查看今日任务\n"
        "/now — 查看当前正在做的\n"
        "/plan — AI 帮你规划今天\n"
        "/review — 今日复盘\n"
        "/help — 本帮助\n\n"
        "*快捷文字*\n"
        "「完成」或「做完了」 — 完成当前任务\n"
        "「休息」 — 休息一下\n"
        "「今天」 — 同 /today\n"
        "「现在」 — 同 /now",
        parse_mode="Markdown",
    )


# ── Message Handler ──


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text:
        return

    # shortcut: natural language commands
    if text in ("完成", "做完了", "搞定", "done"):
        await _complete_current(update, context)
        return
    if text in ("今天", "今日"):
        await cmd_today(update, context)
        return
    if text in ("现在", "当前"):
        await cmd_now(update, context)
        return
    if text in ("休息", "歇会", "累了"):
        await _rest_now(update, context)
        return
    if text in ("规划", "计划"):
        await cmd_plan(update, context)
        return

    # AI classifies: task or chat?
    parsed = await ai.classify_message(text)

    if parsed.get("intent") == "chat":
        await update.message.reply_text(parsed.get("reply", "有什么我能帮你的？"))
        return

    # it's a task
    task = await db.add_task(
        title=parsed.get("title", text[:50]),
        description=parsed.get("description", ""),
        priority=parsed.get("priority", "medium"),
        estimated_minutes=parsed.get("estimated_minutes", 0),
        deadline=parsed.get("deadline"),
    )

    p = PRIORITY_EMOJI.get(task["priority"], "⚪")
    est = f" | 预估 {parsed.get('estimated_minutes', 0)}min" if parsed.get("estimated_minutes") else ""
    await update.message.reply_text(
        f"📥 已记录：*{task['title']}*\n"
        f"{p} {task['priority']}{est}\n\n"
        f"记住了！不会忘的 🧠",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("▶️ 现在就做", callback_data=f"start:{task['id']}"),
            InlineKeyboardButton("📋 查看今天", callback_data="show_today"),
        ]]),
    )


# ── Callback Query Handlers ──


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("start:"):
        await _start_task(query, context, int(data.split(":")[1]))
    elif data.startswith("complete:"):
        await _complete_task(query, context, int(data.split(":")[1]))
    elif data.startswith("postpone:"):
        await _postpone_task(query, context, int(data.split(":")[1]))
    elif data.startswith("save_progress:"):
        await _prompt_save_progress(query, context, int(data.split(":")[1]))
    elif data == "plan_today":
        await _plan_today_callback(query, context)
    elif data == "show_today":
        await _show_today_callback(query, context)
    elif data.startswith("rest:"):
        minutes = int(data.split(":")[1])
        await _schedule_rest_end(query, context, minutes)
    elif data == "rest_now":
        await _rest_from_callback(query, context)
    elif data.startswith("water:"):
        await _handle_water_response(query, context, data.split(":")[1])
    elif data.startswith("checkpoint:"):
        response = data.split(":", 1)[1]
        await _handle_checkpoint_response(query, context, response)


async def _start_task(query, context, task_id: int):
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


async def _complete_task(query, context, task_id: int):
    task = await db.update_task_status(task_id, "completed")
    await db.end_work_session(task_id)
    if not task:
        await query.edit_message_text("❌ 找不到这个任务")
        return

    remaining = await db.get_pending_tasks()
    stats = await db.get_today_stats()
    nav_text = await ai.navigate_next(task, remaining, stats)

    # try to extract recommended next task ID
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


async def _complete_current(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = await db.get_current_task()
    if not current:
        await update.message.reply_text("🤔 你现在没有正在做的任务\n发 /today 看看有什么要做的")
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

    await update.message.reply_text(
        nav_text,
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )


async def _postpone_task(query, context, task_id: int):
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


async def _prompt_save_progress(query, context, task_id: int):
    context.user_data["saving_progress_for"] = task_id
    await query.edit_message_text(
        "💾 请输入当前进度\n\n"
        "下次回来做的时候，我会提醒你做到哪了\n"
        "（直接发消息，简短描述即可）"
    )


async def _plan_today_callback(query, context):
    await query.edit_message_text("🧠 AI 正在分析你的任务...")
    tasks = await db.get_pending_tasks()
    plan_text = await ai.plan_daily(tasks)
    await query.edit_message_text(plan_text)


async def _show_today_callback(query, context):
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


# ── Rest ──


async def _rest_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "☕ 好的，休息一下吧\n\n"
        "站起来走走、喝口水、看看远处 🌿\n"
        "我会在你选的时间后叫你回来",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5 分钟", callback_data="rest:5"),
                InlineKeyboardButton("10 分钟", callback_data="rest:10"),
                InlineKeyboardButton("15 分钟", callback_data="rest:15"),
            ]
        ]),
    )


async def _rest_from_callback(query, context):
    await query.edit_message_text(
        "☕ 好的，休息一下吧\n\n"
        "站起来走走、喝口水、看看远处 🌿",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5 分钟", callback_data="rest:5"),
                InlineKeyboardButton("10 分钟", callback_data="rest:10"),
                InlineKeyboardButton("15 分钟", callback_data="rest:15"),
            ]
        ]),
    )


async def _schedule_rest_end(query, context, minutes: int):
    await query.edit_message_text(
        f"⏰ 好的，{minutes} 分钟后叫你\n\n放松一下吧 ☁️"
    )
    context.job_queue.run_once(
        _rest_end_callback,
        when=minutes * 60,
        chat_id=query.message.chat_id,
        name=f"rest_{query.message.chat_id}",
    )


async def _rest_end_callback(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    current = await db.get_current_task()
    if current:
        text = (
            f"⏰ 休息时间到！\n\n"
            f"回来继续「{current['title']}」吧\n"
            f"你可以的 💪"
        )
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("▶️ 继续做", callback_data=f"start:{current['id']}"),
            InlineKeyboardButton("🔄 再休息5分钟", callback_data="rest:5"),
        ]])
    else:
        tasks = await db.get_pending_tasks()
        text = "⏰ 休息时间到！精力恢复了吗？\n\n看看接下来做什么"
        buttons = None
        if tasks:
            buttons = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    f"▶️ {tasks[0]['title'][:25]}",
                    callback_data=f"start:{tasks[0]['id']}",
                )
            ]])

    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons)


# ── Water Response ──


async def _handle_water_response(query, context, response: str):
    if response == "done":
        praise = await ai.water_praise()
        await query.edit_message_text(praise)
    elif response == "soda":
        scold = await ai.water_scold()
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ 好，去喝水了", callback_data="water:done"),
        ]])
        await query.edit_message_text(scold, reply_markup=buttons)


# ── Checkpoint Response ──


async def _handle_checkpoint_response(query, context, response: str):
    label_map = {
        "on_track": "还在做",
        "almost": "快完了",
        "stuck": "卡住了",
        "drifted": "在做别的事",
        "tired": "今天真的累了",
    }
    user_text = label_map.get(response, response)
    current = await db.get_current_task()
    stats = await db.get_today_stats()

    if response == "tired":
        await db.log_checkpoint(user_text, False)
        await query.edit_message_text(
            "收到，累了就是累了，不硬撑 🫂\n\n"
            "今天剩下的任务我帮你推到明天\n"
            "去做点让自己开心的事吧\n\n"
            "明天又是新的一天 🌅"
        )
        return

    if response == "on_track" or response == "almost":
        await db.log_checkpoint(user_text, True)
        suffix = "快了快了，冲一把！🔥" if response == "almost" else "很好，继续保持 👍"
        await query.edit_message_text(suffix)
        return

    assess = await ai.checkpoint_assess(current, user_text, stats)
    is_on_track = "on_track" not in assess or '"on_track": true' in assess
    await db.log_checkpoint(user_text, is_on_track)

    # clean up JSON tags
    assess = re.sub(r"\[TRACK:\{.*?\}]", "", assess).strip()
    await query.edit_message_text(assess)


# ── Progress Save (via message handler intercept) ──


async def _check_progress_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    task_id = context.user_data.get("saving_progress_for")
    if not task_id:
        return False
    note = update.message.text.strip()
    await db.save_progress_note(task_id, note)
    context.user_data.pop("saving_progress_for", None)
    task = await db.get_task(task_id)
    await update.message.reply_text(
        f"💾 进度已保存\n\n"
        f"「{task['title']}」— {note}\n\n"
        f"下次回来做的时候我会提醒你 ✅",
        reply_markup=task_buttons(task_id, task["status"]),
    )
    return True


# ── Build Bot App ──


def build_bot() -> Application:
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("now", cmd_now))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CommandHandler("review", cmd_review))
    app.add_handler(CallbackQueryHandler(handle_callback))

    async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await _check_progress_save(update, context):
            return
        await handle_message(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    return app
