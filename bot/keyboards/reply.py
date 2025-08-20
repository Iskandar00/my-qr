from telegram import ReplyKeyboardMarkup, KeyboardButton

def phone_request_keyboard():
    contact_button = KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
    return ReplyKeyboardMarkup(
        [[contact_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )