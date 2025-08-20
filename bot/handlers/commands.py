from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from bot.keyboards.reply import phone_request_keyboard
from telegram.ext import CommandHandler

from bot.utils.user_utils import get_by_phone_user, save_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.message.chat.first_name

    await update.message.reply_text(
        f"<b>Salom, {first_name}!</b> 🤖 <i>Botga xush kelibsiz!</i>\n\n"
        "<b>Iltimos</b>, telefon raqamingizni yuboring 👇",
        reply_markup=phone_request_keyboard(),
        parse_mode="HTML"
    )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone_number = contact.phone_number

    user = await get_by_phone_user(phone_number)

    if user:
        user.chat_id = update.effective_chat.id
        await save_user(user)

        await update.message.reply_text(
            f"✅ Raqamingiz qabul qilindi\n📱 {phone_number}"
        )
    else:
        await update.message.reply_text(
            "❌ Sizning raqamingiz tizimda topilmadi."
        )


def register(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
