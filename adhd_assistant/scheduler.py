"""
Scheduler — proactive push notifications.

Three scheduled jobs:
  1. Morning report — daily plan at configurable time
  2. Checkpoint — periodic "what are you doing?" check-in
  3. Rest reminder — after continuous work without a break
  4. Evening review — end-of-day summary
"""

import logging
from datetime import time, datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config
import database as db
import ai_engine as ai
import random

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")


def get_tz():
    return ZoneInfo(Config.TIMEZONE)


def setup_scheduled_jobs(job_queue, dynamic_settings: dict | None = None):
    """Register all scheduled jobs. Uses dynamic_settings from DB if available."""
    tz = get_tz()
    chat_id = Config.TELEGRAM_CHAT_ID
    if not chat_id:
        logger.warning("TELEGRAM_CHAT_ID not set — scheduled jobs disabled")
        return

    ds = dynamic_settings or {}

    morning_h = int(ds.get("morning_hour", Config.MORNING_REPORT_HOUR))
    morning_m = int(ds.get("morning_minute", Config.MORNING_REPORT_MINUTE))
    checkpoint_min = int(ds.get("checkpoint_interval", Config.CHECKPOINT_INTERVAL))
    rest_min = int(ds.get("rest_interval", Config.REST_REMINDER_INTERVAL))

    # 1. Morning report
    job_queue.run_daily(
        morning_report,
        time=time(morning_h, morning_m, tzinfo=tz),
        chat_id=chat_id,
        name="morning_report",
    )
    logger.info("Morning report scheduled at %02d:%02d", morning_h, morning_m)

    # 2. Checkpoint — every N minutes during work hours (9-21)
    job_queue.run_repeating(
        checkpoint_push,
        interval=checkpoint_min * 60,
        first=checkpoint_min * 60,
        chat_id=chat_id,
        name="checkpoint",
    )
    logger.info("Checkpoint scheduled every %d minutes", checkpoint_min)

    # 3. Rest reminder — check continuous work
    job_queue.run_repeating(
        rest_reminder_check,
        interval=30 * 60,
        first=30 * 60,
        chat_id=chat_id,
        name="rest_reminder",
        data={"rest_interval": rest_min},
    )
    logger.info("Rest reminder check every 30 minutes (threshold: %d min)", rest_min)

    # 4. Drink water reminder — every hour
    job_queue.run_repeating(
        drink_water_reminder,
        interval=60 * 60,
        first=60 * 60,
        chat_id=chat_id,
        name="drink_water",
    )
    logger.info("Drink water reminder every 60 minutes")

    # 5. Lunch break reminder
    job_queue.run_daily(
        break_reminder,
        time=time(11, 30, tzinfo=tz),
        days=(0, 1, 2, 3, 4),
        chat_id=chat_id,
        name="lunch_break",
        data={"break_type": "lunch"},
    )
    logger.info("Lunch break reminder at 11:30 (weekdays)")

    # 6. Lunch break end reminder
    job_queue.run_daily(
        break_end_reminder,
        time=time(13, 25, tzinfo=tz),
        days=(0, 1, 2, 3, 4),
        chat_id=chat_id,
        name="lunch_end",
    )
    logger.info("Lunch end reminder at 13:25 (weekdays)")

    # 7. Evening break reminder
    job_queue.run_daily(
        break_reminder,
        time=time(18, 0, tzinfo=tz),
        days=(0, 1, 2, 3, 4),
        chat_id=chat_id,
        name="evening_break",
        data={"break_type": "evening"},
    )
    logger.info("Evening break reminder at 18:00 (weekdays)")

    # 8. Evening break end reminder
    job_queue.run_daily(
        break_end_reminder,
        time=time(19, 25, tzinfo=tz),
        days=(0, 1, 2, 3, 4),
        chat_id=chat_id,
        name="evening_end",
    )
    logger.info("Evening end reminder at 19:25 (weekdays)")

    # 9. Evening review
    job_queue.run_daily(
        evening_review,
        time=time(21, 0, tzinfo=tz),
        chat_id=chat_id,
        name="evening_review",
    )
    logger.info("Evening review scheduled at 21:00")


async def morning_report(context: ContextTypes.DEFAULT_TYPE):
    """Push morning daily plan."""
    monitor.info("[SCHEDULE] morning_report triggered")
    chat_id = context.job.chat_id
    now = datetime.now(get_tz())

    # skip weekends (optional)
    if now.weekday() >= 5:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌅 周末早上好！\n\n今天没有工作安排\n好好休息，做点开心的事 ☀️",
        )
        return

    tasks = await db.get_pending_tasks()
    if not tasks:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌅 早上好！\n\n今天没有待办任务，清爽的一天\n有新任务随时发给我",
        )
        return

    plan_text = await ai.plan_daily(tasks)

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"▶️ 开始第 1 件",
            callback_data=f"start:{tasks[0]['id']}",
        )],
    ])

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🌅 早上好！\n\n{plan_text}",
        reply_markup=buttons,
    )


async def checkpoint_push(context: ContextTypes.DEFAULT_TYPE):
    """Periodic check-in: what are you doing right now?"""
    monitor.info("[SCHEDULE] checkpoint triggered")
    chat_id = context.job.chat_id
    now = datetime.now(get_tz())

    # only during work hours
    if now.hour < 9 or now.hour >= 21:
        return

    current = await db.get_current_task()

    if current:
        session = await db.get_active_session()
        duration = ""
        if session:
            started = datetime.fromisoformat(session["started_at"])
            mins = int((datetime.now() - started).total_seconds() / 60)
            duration = f"（已经做了 {mins} 分钟）"

        text = (
            f"⏰ Checkpoint\n\n"
            f"你现在在做「{current['title']}」{duration}\n"
            f"进展怎么样？"
        )
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ 快完了", callback_data="checkpoint:almost"),
                InlineKeyboardButton("👍 还在做", callback_data="checkpoint:on_track"),
            ],
            [
                InlineKeyboardButton("😵 卡住了", callback_data="checkpoint:stuck"),
                InlineKeyboardButton("🙈 在做别的", callback_data="checkpoint:drifted"),
            ],
            [
                InlineKeyboardButton("😮‍💨 今天真的累了", callback_data="checkpoint:tired"),
            ],
        ])
    else:
        stats = await db.get_today_stats()
        text = (
            f"⏰ Checkpoint\n\n"
            f"你现在没有在做任何任务\n"
            f"今天已完成 {stats['completed']} 件，还有 {stats['remaining']} 件\n\n"
            f"要不要开始一个？"
        )
        tasks = await db.get_pending_tasks()
        buttons_list = []
        if tasks:
            buttons_list.append([
                InlineKeyboardButton(
                    f"▶️ {tasks[0]['title'][:25]}",
                    callback_data=f"start:{tasks[0]['id']}",
                )
            ])
        buttons_list.append([
            InlineKeyboardButton("😮‍💨 今天累了", callback_data="checkpoint:tired"),
        ])
        buttons = InlineKeyboardMarkup(buttons_list)

    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons)


async def rest_reminder_check(context: ContextTypes.DEFAULT_TYPE):
    """Check if user has been working too long without a break."""
    chat_id = context.job.chat_id
    now = datetime.now(get_tz())

    if now.hour < 9 or now.hour >= 21:
        return

    session = await db.get_active_session()
    if not session:
        return

    started = datetime.fromisoformat(session["started_at"])
    work_minutes = int((datetime.now() - started).total_seconds() / 60)

    threshold = context.job.data.get("rest_interval", Config.REST_REMINDER_INTERVAL) if context.job.data else Config.REST_REMINDER_INTERVAL
    if work_minutes >= threshold:
        rest_text = await ai.rest_reminder(work_minutes)
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("☕ 休息5分钟", callback_data="rest:5"),
                InlineKeyboardButton("🚶 休息10分钟", callback_data="rest:10"),
            ],
            [
                InlineKeyboardButton("⏰ 再给我15分钟", callback_data="rest:0"),
            ],
        ])
        await context.bot.send_message(
            chat_id=chat_id, text=rest_text, reply_markup=buttons
        )


LUNCH_TIPS = [
    "🍱 午饭时间到！\n\n提醒你几件事：\n• 先吃饭，别刷手机刷到忘了吃\n• 吃点有蛋白质的，下午不容易困\n• 少吃甜食，血糖坐过山车会让你更难集中",
    "🍱 停下工作，去吃饭\n\n• 别叫外卖奶茶，喝水就行\n• 吃完可以散步 10 分钟，比刷抖音提神\n• 趁午休检查下今天有没有漏掉的消息",
    "🍱 午餐时间！\n\n• 别边吃边工作，你的大脑需要真正休息\n• 吃完饭闭眼 15 分钟比喝咖啡有用\n• 检查一下手机有没有未接来电",
    "🍱 该吃午饭了\n\n• 今天有按时吃早饭吗？没有的话午饭多吃点\n• 记得吃蔬菜，别光吃碳水\n• 下午有会的话，趁现在过一遍议程",
    "🍱 放下键盘，去吃饭\n\n• 别忘了吃药（如果有的话）\n• 充一下手机电量\n• 吃饭时别想工作的事，让大脑换换频道",
]

EVENING_TIPS = [
    "🌆 下班时间到！\n\n• 今天有什么需要回的私人消息吗？\n• 明天需要带什么东西？现在收拾好\n• 运动一下吧，哪怕散步 20 分钟",
    "🌆 收工吃饭！\n\n• 别加班了，效率已经很低了\n• 晚饭别吃太重，影响睡眠\n• 有没有该交的水电费/快递要取？",
    "🌆 工作结束，切换到生活模式\n\n• 今天有没有想联系的朋友/家人？发条消息\n• 检查下快递/外卖/跑腿\n• 晚上安排点让自己开心的事",
    "🌆 下班了！\n\n• 明天要穿的衣服准备好了吗？\n• 冰箱里还有吃的吗？需要采购吗？\n• 今晚试试 11 点前睡觉，ADHD 缺觉会更严重",
    "🌆 下班时间\n\n• 今天有没有忘记回复的重要私人消息？\n• 有没有需要预约的事（医生/理发/快递）？\n• 别一回家就躺着刷手机，先做一件小事再放松",
]

BREAK_END_MESSAGES = [
    "⏰ 休息时间快结束了\n\n还有 5 分钟，准备切回工作模式\n先喝口水，深呼吸，回来继续 💪",
    "⏰ 5 分钟后回归战场\n\n收拾一下，调整状态\n下午/晚上的第一件事我帮你安排好了",
    "⏰ 休息快结束了\n\n伸个懒腰，准备开工\n一会儿发 /today 看看接下来要做什么",
]

WATER_MESSAGES = [
    "💧 喝水时间到！\n\n放下手里的奶茶/可乐/咖啡\n你的身体需要的是水，不是糖",
    "💧 起来喝杯水\n\n饮料里的糖会让你更困更渴\n白开水才是真正的续命神器",
    "💧 嘿，喝水了吗？\n\n别拿快乐水骗自己\n你的大脑 75% 是水做的，不是碳酸做的",
    "💧 喝水提醒 ~\n\n可乐让你爽 3 秒，水让你清醒 3 小时\n去接杯水，现在",
    "💧 水！水！水！\n\n奶茶的快乐是假的，脱水的疲惫是真的\n来一杯温水，对自己好一点",
    "💧 该喝水了\n\n你知道吗？脱水 1% 就会降低注意力\nADHD 已经够难了，别再让缺水帮倒忙",
    "💧 喝水警告 ⚠️\n\n把那瓶饮料放下！\n白水才是打工人的最佳拍档\n喝完这杯水再继续干活",
    "💧 你的身体正在呼唤你\n\n不是呼唤奶茶，是呼唤水\n甜饮料只会让你越喝越渴\n接杯水，谢谢",
    "💧 友情提醒：喝水\n\n咖啡不算、奶茶不算、可乐更不算\n只有水才算水\n去倒一杯，现在立刻",
    "💧 叮！喝水任务\n\n你的饮料含糖量 = 好几勺白糖\n你的白开水含糖量 = 0\n选哪个不用我教吧？",
]


async def break_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Lunch or evening break reminder with life tips."""
    monitor.info("[SCHEDULE] break_reminder triggered (%s)", context.job.data.get("break_type", "?"))
    chat_id = context.job.chat_id
    break_type = context.job.data.get("break_type", "lunch")

    if break_type == "lunch":
        tips = LUNCH_TIPS
    else:
        tips = EVENING_TIPS

    msg = random.choice(tips)

    # also show today's progress as a mini checkpoint
    stats = await db.get_today_stats()
    progress = f"\n\n📊 今日进度：已完成 {stats['completed']} 件，还剩 {stats['remaining']} 件"

    await context.bot.send_message(chat_id=chat_id, text=msg + progress)


async def break_end_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Reminder that break is ending soon."""
    chat_id = context.job.chat_id
    msg = random.choice(BREAK_END_MESSAGES)

    tasks = await db.get_pending_tasks()
    buttons = None
    if tasks:
        buttons = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                f"▶️ 开始：{tasks[0]['title'][:20]}",
                callback_data=f"start:{tasks[0]['id']}",
            )
        ]])

    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=buttons)


async def drink_water_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Hourly reminder to drink water, not sugary drinks."""
    monitor.info("[SCHEDULE] drink_water triggered")
    chat_id = context.job.chat_id
    now = datetime.now(get_tz())

    if now.hour < 9 or now.hour >= 22:
        return

    msg = random.choice(WATER_MESSAGES)
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ 喝了！", callback_data="water:done"),
        InlineKeyboardButton("🥤 喝的饮料...", callback_data="water:soda"),
    ]])
    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=buttons)


async def evening_review(context: ContextTypes.DEFAULT_TYPE):
    """End-of-day review push."""
    monitor.info("[SCHEDULE] evening_review triggered")
    chat_id = context.job.chat_id
    tasks = await db.get_today_tasks()
    stats = await db.get_today_stats()

    if stats["total"] == 0:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🌙 今天没有任务记录\n\n明天见，早点休息 💤",
        )
        return

    review = await ai.daily_review(tasks, stats)
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🌙 今日复盘\n\n{review}",
    )
