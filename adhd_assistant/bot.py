"""
Telegram Bot — thin orchestrator.

Registers all handlers and wires up the Application.
All logic lives in handlers/ modules.
"""

import logging
from telegram import Update
from telegram.error import TimedOut, NetworkError
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from config import Config
from handlers.commands import cmd_start, cmd_help, cmd_settings
from handlers.tasks import cmd_today, cmd_now, cmd_plan, cmd_review
from handlers.message import handle_message, check_progress_save
from handlers.callbacks import handle_callback

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler — log and notify user."""
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)
    monitor.info("[ERROR] %s", context.error)

    if isinstance(context.error, (TimedOut, NetworkError)):
        logger.warning("Network issue, will retry on next message")
        return

    if update and hasattr(update, "effective_chat") and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ 出了点小问题，但我还在！重新发一次试试",
            )
        except Exception:
            pass


def build_bot() -> Application:
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # slash commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("today", cmd_today))
    app.add_handler(CommandHandler("now", cmd_now))
    app.add_handler(CommandHandler("plan", cmd_plan))
    app.add_handler(CommandHandler("review", cmd_review))
    app.add_handler(CommandHandler("settings", cmd_settings))

    # inline button callbacks
    app.add_handler(CallbackQueryHandler(handle_callback))

    # free-text messages
    async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await check_progress_save(update, context):
            return
        await handle_message(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler))

    # global error handler
    app.add_error_handler(error_handler)

    return app
