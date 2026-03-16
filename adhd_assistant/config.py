import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://api.minimax.chat/v1")
    AI_MODEL: str = os.getenv("AI_MODEL", "MiniMax-Text-01")
    TELEGRAM_CHAT_ID: int = int(os.getenv("TELEGRAM_CHAT_ID") or "0")

    MORNING_REPORT_HOUR: int = int(os.getenv("MORNING_REPORT_HOUR", "9"))
    MORNING_REPORT_MINUTE: int = int(os.getenv("MORNING_REPORT_MINUTE", "0"))
    CHECKPOINT_INTERVAL: int = int(os.getenv("CHECKPOINT_INTERVAL", "120"))
    REST_REMINDER_INTERVAL: int = int(os.getenv("REST_REMINDER_INTERVAL", "90"))
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Shanghai")

    DB_PATH: str = str(Path(__file__).parent / "data" / "adhd.db")
