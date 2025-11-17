import os


class Config:
    # Telegram
    BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

    # Gemini API Key and model
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Database
    DATABASE_NAME = os.getenv("DATABASE_NAME", "database.db")

    # Параметры генерации (по желанию)
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))

    # if not BOT_TOKEN:
    #     raise ValueError("❌ TELEGRAM_TOKEN не найден в .env")

    # if not GEMINI_API_KEY:
    #     raise ValueError("❌ GEMINI_API_KEY не найден в .env")
