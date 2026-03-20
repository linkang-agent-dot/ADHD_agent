"""
ADHD Task Assistant — Entry Point

Starts the Telegram bot with scheduled push notifications.
"""

import asyncio
import logging
import os
from pathlib import Path
from config import Config
from database import init_db, get_all_settings
from bot import build_bot
from scheduler import setup_scheduled_jobs
from heartbeat import setup_heartbeat

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
MONITOR_FORMAT = "%(asctime)s %(message)s"

logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

# Suppress noisy httpx polling logs
logging.getLogger("httpx").setLevel(logging.WARNING)

# Monitor log — only bot interactions, clean and readable
monitor_logger = logging.getLogger("monitor")
monitor_logger.setLevel(logging.INFO)
monitor_handler = logging.FileHandler(LOG_DIR / "monitor.log", encoding="utf-8")
monitor_handler.setFormatter(logging.Formatter(MONITOR_FORMAT, datefmt="%H:%M:%S"))
monitor_logger.addHandler(monitor_handler)

# Full debug log for troubleshooting
debug_handler = logging.FileHandler(LOG_DIR / "debug.log", encoding="utf-8")
debug_handler.setFormatter(logging.Formatter(LOG_FORMAT))
debug_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(debug_handler)

logger = logging.getLogger(__name__)


def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Please configure .env file.")
        return

    if not Config.AI_API_KEY:
        logger.error("AI_API_KEY is not set. Please configure .env file.")
        return

    asyncio.run(init_db())
    logger.info("Database initialized")

    dynamic_settings = asyncio.run(get_all_settings())
    if dynamic_settings:
        logger.info("Loaded dynamic settings: %s", dynamic_settings)

    app = build_bot()

    setup_scheduled_jobs(app.job_queue, dynamic_settings=dynamic_settings)
    logger.info("Scheduled jobs configured")

    setup_heartbeat(app.job_queue)

    logger.info("Bot is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
