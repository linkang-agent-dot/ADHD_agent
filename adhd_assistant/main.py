"""
ADHD Task Assistant — Entry Point

Starts the Telegram bot with scheduled push notifications.
"""

import asyncio
import logging
from config import Config
from database import init_db
from bot import build_bot
from scheduler import setup_scheduled_jobs

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not Config.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Please configure .env file.")
        return

    if not Config.AI_API_KEY:
        logger.error("AI_API_KEY is not set. Please configure .env file.")
        return

    # init database
    asyncio.run(init_db())
    logger.info("Database initialized")

    # build bot
    app = build_bot()

    # setup scheduled jobs
    setup_scheduled_jobs(app.job_queue)
    logger.info("Scheduled jobs configured")

    # start polling
    logger.info("Bot is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
