"""Command handlers: /start, /help, /settings."""

import re
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from utils import safe_reply, PRIORITY_EMOJI
import database as db

logger = logging.getLogger(__name__)
monitor = logging.getLogger("monitor")


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await safe_reply(
        update.message,
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


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply(
        update.message,
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
        "/settings — 修改设置（时间/间隔）\n"
        "/help — 本帮助\n\n"
        "*快捷文字*\n"
        "「完成」或「做完了」 — 完成当前任务\n"
        "「休息」 — 休息一下\n"
        "「今天」 — 同 /today\n"
        "「现在」 — 同 /now\n"
        "「早报改到10点」 — 直接改设置",
        parse_mode="Markdown",
    )


async def cmd_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = await db.get_all_settings()
    morning_h = int(settings.get("morning_hour", Config.MORNING_REPORT_HOUR))
    morning_m = int(settings.get("morning_minute", Config.MORNING_REPORT_MINUTE))
    checkpoint = int(settings.get("checkpoint_interval", Config.CHECKPOINT_INTERVAL))
    rest_int = int(settings.get("rest_interval", Config.REST_REMINDER_INTERVAL))

    await safe_reply(
        update.message,
        f"⚙️ *当前设置*\n\n"
        f"🌅 早报时间：{morning_h:02d}:{morning_m:02d}\n"
        f"⏰ Checkpoint 间隔：{checkpoint} 分钟\n"
        f"☕ 连续工作提醒：{rest_int} 分钟\n\n"
        f"💡 直接说就能改，例如：\n"
        f"「早报改到10点」\n"
        f"「checkpoint改成3小时」\n"
        f"「连续工作2小时再提醒」",
        parse_mode="Markdown",
    )


async def handle_settings_change(update: Update, context: ContextTypes.DEFAULT_TYPE, parsed: dict):
    key = parsed.get("key", "")
    value = parsed.get("value", "")

    VALID_KEYS = {
        "morning_hour": ("早报小时", 0, 23),
        "morning_minute": ("早报分钟", 0, 59),
        "checkpoint_interval": ("Checkpoint间隔(分钟)", 15, 480),
        "rest_interval": ("连续工作提醒(分钟)", 30, 300),
    }

    if key not in VALID_KEYS:
        await safe_reply(update.message, "🤔 这个设置我暂时改不了\n\n可改的有：早报时间、Checkpoint间隔、连续工作提醒间隔\n发 /settings 查看当前设置")
        return

    try:
        int_value = int(value)
        label, min_v, max_v = VALID_KEYS[key]
        if not (min_v <= int_value <= max_v):
            await safe_reply(update.message, f"⚠️ {label} 的范围是 {min_v}-{max_v}，{int_value} 超出范围了")
            return
    except ValueError:
        await safe_reply(update.message, "⚠️ 数值格式不对，给个数字就行")
        return

    if key == "morning_hour" and "morning_minute" not in parsed:
        m = re.search(r'(\d{1,2})[:\uff1a](\d{2})', parsed.get("confirm_text", "") + update.message.text)
        if m:
            await db.set_setting("morning_hour", m.group(1))
            await db.set_setting("morning_minute", m.group(2))
            await safe_reply(update.message, f"✅ 早报时间已改为 {int(m.group(1)):02d}:{int(m.group(2)):02d}\n\n下次重启 bot 后生效，或者我现在帮你重新注册定时任务")
            await reschedule_jobs(context)
            return

    await db.set_setting(key, str(int_value))

    label, _, _ = VALID_KEYS[key]
    if key == "morning_hour":
        settings = await db.get_all_settings()
        minute = int(settings.get("morning_minute", Config.MORNING_REPORT_MINUTE))
        await safe_reply(update.message, f"✅ 早报时间已改为 {int_value:02d}:{minute:02d}")
    elif key in ("checkpoint_interval", "rest_interval"):
        await safe_reply(update.message, f"✅ {label}已改为 {int_value} 分钟")
    else:
        await safe_reply(update.message, f"✅ {label}已更新为 {int_value}")

    await reschedule_jobs(context)


async def reschedule_jobs(context: ContextTypes.DEFAULT_TYPE):
    from scheduler import setup_scheduled_jobs
    job_queue = context.application.job_queue

    current_jobs = job_queue.jobs()
    for job in current_jobs:
        job.schedule_removal()

    dynamic_settings = await db.get_all_settings()
    setup_scheduled_jobs(job_queue, dynamic_settings=dynamic_settings)
    logger.info("Scheduled jobs rescheduled with settings: %s", dynamic_settings)
