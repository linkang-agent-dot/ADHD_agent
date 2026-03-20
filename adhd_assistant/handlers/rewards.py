"""Task completion reward — send a random anime image as positive reinforcement."""

import random
import logging
import aiohttp

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")

SFW_CATEGORIES = ["waifu", "neko", "shinobu", "megumin"]
API_BASE = "https://api.waifu.pics/sfw"

REWARD_LINES = [
    "做完了就是最棒的！来，看看这个 👀",
    "辛苦了～ 奖励你一张图 🎁",
    "任务完成！解锁奖励 🔓",
    "今天的你很厉害，收好 ✨",
    "能做完就比90%的人强，给你看点好东西 🏆",
    "效率王！奖励已到账 💎",
    "完成 = 多巴胺，来一发 🧠",
    "你值得拥有这个 🌟",
]


async def fetch_reward_image() -> str | None:
    """Fetch a random anime image URL from waifu.pics. Returns None on failure."""
    cat = random.choice(SFW_CATEGORIES)
    url = f"{API_BASE}/{cat}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("url")
    except Exception as e:
        logger.warning("Failed to fetch reward image: %s", e)
    return None


async def send_reward(bot, chat_id: int):
    """Send a reward image to the user. Silently skips if API fails."""
    image_url = await fetch_reward_image()
    if not image_url:
        return

    caption = random.choice(REWARD_LINES)
    try:
        await bot.send_photo(chat_id=chat_id, photo=image_url, caption=caption)
        monitor.info("[REWARD] sent image to %s", chat_id)
    except Exception as e:
        logger.warning("Failed to send reward photo: %s", e)
        monitor.info("[REWARD] ⚠️ send failed: %s", e)
