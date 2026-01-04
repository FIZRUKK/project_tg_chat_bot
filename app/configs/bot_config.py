import os

from dotenv import load_dotenv



load_dotenv()

class TgChatBotConfig:

    BOT_TOKEN = os.getenv("BOT_TOKEN")

    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret")
    WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost")
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "http://localhost")
    WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", 8080))

tg_bot_config = TgChatBotConfig()