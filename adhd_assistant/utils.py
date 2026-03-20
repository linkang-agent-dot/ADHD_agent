"""Shared utilities for the ADHD bot handlers."""

import asyncio
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TimedOut, NetworkError

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")

MAX_RETRIES = 2
RETRY_DELAY = 3

PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "⚪"}
STATUS_EMOJI = {"completed": "✅", "in_progress": "🎯", "pending": "⏳", "postponed": "📌", "cancelled": "🚫"}


async def safe_reply(message, text: str, retries: int = MAX_RETRIES, **kwargs):
    for attempt in range(retries + 1):
        try:
            return await message.reply_text(text, **kwargs)
        except (TimedOut, NetworkError) as e:
            if attempt < retries:
                logger.warning("send retry %d/%d: %s", attempt + 1, retries, e)
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error("send failed after %d retries: %s", retries, e)
                raise


async def safe_send(bot, chat_id, text: str, retries: int = MAX_RETRIES, **kwargs):
    for attempt in range(retries + 1):
        try:
            return await bot.send_message(chat_id=chat_id, text=text, **kwargs)
        except (TimedOut, NetworkError) as e:
            if attempt < retries:
                logger.warning("send retry %d/%d: %s", attempt + 1, retries, e)
                await asyncio.sleep(RETRY_DELAY)
            else:
                logger.error("send failed after %d retries: %s", retries, e)
                raise


def monitor_detail(parsed: dict) -> str:
    intent = parsed.get("intent", "")
    if intent == "command":
        return f"cmd={parsed.get('command', '?')}"
    if intent == "task":
        return f"title={parsed.get('title', '?')!r}"
    if intent == "settings":
        return f"key={parsed.get('key', '?')} val={parsed.get('value', '?')}"
    if intent == "chat":
        reply = parsed.get("reply", "")
        return f"reply={reply[:60]!r}{'...' if len(reply) > 60 else ''}"
    return ""


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
