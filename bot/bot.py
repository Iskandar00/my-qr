from telegram.ext import ApplicationBuilder
from django.conf import settings

from bot.handlers import commands, callbacks

TELEGRAM_TOKEN = getattr(settings, "TELEGRAM_TOKEN", None)

def run_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError("Telegram token not found!")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    commands.register(app)
    # callbacks.register(app)

    print("🤖 Telegram bot running...")
    app.run_polling()
