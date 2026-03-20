"""Rest/break handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils import safe_reply
import database as db


async def rest_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(
        update.message,
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


async def rest_from_callback(query, context):
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


async def schedule_rest_end(query, context, minutes: int):
    await query.edit_message_text(
        f"⏰ 好的，{minutes} 分钟后叫你\n\n放松一下吧 ☁️"
    )
    context.job_queue.run_once(
        rest_end_callback,
        when=minutes * 60,
        chat_id=query.message.chat_id,
        name=f"rest_{query.message.chat_id}",
    )


async def rest_end_callback(context: ContextTypes.DEFAULT_TYPE):
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
