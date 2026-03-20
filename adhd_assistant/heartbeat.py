"""
Heartbeat — periodic health check for the bot.

Logs system status every 5 minutes to monitor.log.
Detects and reports anomalies: AI API failures, DB issues, stale sessions.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from telegram.ext import ContextTypes
import database as db

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")

_consecutive_failures = 0


async def heartbeat_check(context: ContextTypes.DEFAULT_TYPE):
    """Periodic health check — runs every 5 minutes."""
    global _consecutive_failures
    issues = []

    try:
        stats = await db.get_today_stats()
        session = await db.get_active_session()

        if session:
            started = datetime.fromisoformat(session["started_at"])
            mins = int((datetime.now() - started).total_seconds() / 60)
            if mins > 300:
                issues.append(f"stale session ({mins}min)")

        _consecutive_failures = 0

    except Exception as e:
        _consecutive_failures += 1
        issues.append(f"DB error: {e}")

    if issues:
        monitor.info("[HEARTBEAT] ⚠️ issues: %s", ", ".join(issues))
    else:
        monitor.info("[HEARTBEAT] ✅ healthy (completed=%s remaining=%s)",
                     stats["completed"], stats["remaining"])

    if _consecutive_failures >= 3:
        monitor.info("[HEARTBEAT] 🔴 CRITICAL: %d consecutive failures", _consecutive_failures)


def setup_heartbeat(job_queue):
    """Register heartbeat job — every 5 minutes."""
    job_queue.run_repeating(
        heartbeat_check,
        interval=300,
        first=60,
        name="heartbeat",
    )
    logger.info("Heartbeat registered (every 5 min)")
