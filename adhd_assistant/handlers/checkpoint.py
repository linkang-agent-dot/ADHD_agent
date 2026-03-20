"""Checkpoint response handler."""

import re
from telegram.ext import ContextTypes
import database as db
import ai_engine as ai


async def handle_checkpoint_response(query, context, response: str):
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

    assess = re.sub(r"\[TRACK:\{.*?\}]", "", assess).strip()
    await query.edit_message_text(assess)
