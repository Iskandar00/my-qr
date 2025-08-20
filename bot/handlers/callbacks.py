from telegram import Update
from telegram.ext import ContextTypes


async def inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm":
        await query.edit_message_text("✅ Tasdiqlandi!")
    elif query.data == "cancel":
        await query.edit_message_text("❌ Bekor qilindi.")


def register(app):
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(inline_callback))
