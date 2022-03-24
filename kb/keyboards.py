from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

functions_default = ReplyKeyboardMarkup(resize_keyboard=True)
functions_default.row("👤 личный кабинет", "🌩 Начать атаку", "🎄 Связаться с администратором")
functions_default.row("⚙ Прокси")

proxy_choice = ReplyKeyboardMarkup(resize_keyboard=True)
proxy_choice.row("🔅 IPV4", "🔅 HTTP/HTTPS", "🔅 SOCKS4")
proxy_choice.row("⏮ Назад")

bomb = ReplyKeyboardMarkup(resize_keyboard=True)
bomb.row("🟢 Начать атаку", "🔴 Остановить атаку")
bomb.row("⏮ Назад")


def create_pay_qiwi_func(send_requests, receipt, message_id, way):
    check_qiwi_pay_inl = InlineKeyboardMarkup()

    check_qiwi_pay_inl.row(
        InlineKeyboardButton(
            text="🌀 Проверить оплату", callback_data=f"Pay:{way}:{receipt}:{message_id}"
        ),
        InlineKeyboardButton(text="💸 Перейти к оплате", url=send_requests),
    )
    return check_qiwi_pay_inl


# принятие платежа
#

oplata = InlineKeyboardMarkup()
oplata.row(
    InlineKeyboardButton(text="💠 Оплатить доступ к боту 💠", callback_data=f"oplata")
)

proxy_inline_choice = InlineKeyboardMarkup()
proxy_inline_choice.row(InlineKeyboardButton(text="🔹 IPV4", callback_data=f"ipv4"), InlineKeyboardButton(text="🔹 HTTP / HTTPS", callback_data=f"http"), InlineKeyboardButton(text="🔹 SOCKS4", callback_data=f"socks4"))
proxy_inline_choice.row(InlineKeyboardButton(text="🔸 None Proxy Mode", callback_data=f"none_proxy"))