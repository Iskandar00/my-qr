from telegram import Bot
from django.conf import settings
from telegram.constants import ParseMode

bot = Bot(token=settings.TELEGRAM_TOKEN)


async def send_transaction_message(chat_id, trace_id, amount, purpose):
    message = (
        f"💰 <b>Tranzaksiya muvaffaqiyatli!</b>\n\n"
        f"🆔 <b>Trace ID:</b> {trace_id}\n"
        f"💵 <b>Amount:</b> {amount}\n"
        f"📌 <b>Purpose:</b> {purpose}\n\n"
    )

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode=ParseMode.HTML
    )
