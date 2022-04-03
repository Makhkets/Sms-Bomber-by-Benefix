from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

with open("settings.json", "r", encoding="utf-8") as file:
    settings = json.load(file)

def create_pay_qiwi_func(send_requests, receipt, message_id, way):
    check_qiwi_pay_inl = InlineKeyboardMarkup()

    check_qiwi_pay_inl.row(
        InlineKeyboardButton(
            text="🌀 Проверить оплату", callback_data=f"Pay:{way}:{receipt}:{message_id}"
        ),
        InlineKeyboardButton(text="💸 Перейти к оплате", url=send_requests),
    )
    return check_qiwi_pay_inl

oplata = InlineKeyboardMarkup()
oplata.row(
    InlineKeyboardButton(text="💠 Оплатить доступ к боту 💠", callback_data=f"oplata")
)

def MAIN(user_id):
    main_menu = InlineKeyboardMarkup()

    zapusk = InlineKeyboardButton(text="🧨 Запустить", callback_data="Zapusk")
    helpme = InlineKeyboardButton(text="❗ Помощь", callback_data="helpme")

    telegram_channel = InlineKeyboardButton(text="💥 Telegram канал", url="t.me/benefixx")

    my_rassilk = InlineKeyboardButton(text="📲 Мои рассылки", callback_data="my_rassilki")
    antispam = InlineKeyboardButton(text="👑 Анти-спам", callback_data="antispam")

    profile = InlineKeyboardButton(text="💼 Профиль", callback_data="profile")

    tehPodderjka = InlineKeyboardButton(text="👨‍💻 Техническая поддержка", url="t.me/benefixx")

    admin = InlineKeyboardButton(text="👋 Админ панель", callback_data="admin_panel")


    main_menu.row(zapusk, profile)
    main_menu.row(telegram_channel, helpme)
    main_menu.row(my_rassilk, antispam)
    main_menu.row(tehPodderjka)

    if str(user_id) in settings["telegram"]["admins"]:
        main_menu.row(admin)

    return main_menu

