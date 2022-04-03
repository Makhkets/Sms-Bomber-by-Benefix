import asyncio
import json
import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from pyqiwip2p import QiwiP2P
import requests
from aiogram import *
from loguru import logger
import random
from kb import keyboards
from aiogram.types import *
from datetime import datetime
import datetime
from dateutil.relativedelta import *
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

# сделать остановку спама !

path_db = "database.db"
with open("settings.json", "r", encoding="utf-8") as file:
    settings = json.load(file)

loop = asyncio.get_event_loop()
bot = Bot(settings["telegram"]["token"], parse_mode="HTML")
dp = Dispatcher(bot, loop=loop, storage=MemoryStorage())


class Form(StatesGroup):

    getPhone = State()

    antispam = State()


@dp.callback_query_handler(lambda c: c.data == "oplata")
async def process_callback_button1(call: types.CallbackQuery):
    get_payment = (
        settings["telegram"]["qiwi"],
        settings["telegram"]["token_qiwi"],
        settings["telegram"]["private_key"],
        settings["telegram"]["qiwi_nickname"],
        "form",
        "True",
    )

    request = requests.session()
    request.headers["authorization"] = "Bearer " + get_payment[1]
    response_qiwi = request.get(
        f"https://edge.qiwi.com/payment-history/v2/persons/{get_payment[0]}/payments",
        params={"rows": 1, "operation": "IN"},
    )

    pay_amount = int(settings["telegram"]["price"])
    del_msg = await bot.send_message(
        call.from_user.id, "<b>♻ Подождите, бот генерируется...</b>"
    )
    min_input_qiwi = 1  # Минимальная сумма пополнения в рублях

    get_payments = (
        settings["telegram"]["qiwi"],
        settings["telegram"]["token_qiwi"],
        settings["telegram"]["private_key"],
        settings["telegram"]["qiwi_nickname"],
        "form",
        "True",
    )
    request = requests.Session()
    request.headers["authorization"] = "Bearer " + get_payments[1]
    response_qiwi = request.get(
        f"https://edge.qiwi.com/payment-history/v2/persons/{get_payments[0]}/payments",
        params={"rows": 1, "operation": "IN"},
    )
    if pay_amount >= min_input_qiwi:
        passwd = list("1234567890ABCDEFGHIGKLMNOPQRSTUVYXWZ")
        random.shuffle(passwd)
        random_chars = "".join([random.choice(passwd) for x in range(10)])
        generate_number_check = str(random.randint(100000000000, 999999999999))
        if get_payments[4] == "form":
            qiwi = QiwiP2P(get_payments[2])
            bill = qiwi.bill(
                bill_id=generate_number_check,
                amount=pay_amount,
                comment=generate_number_check,
            )
            way_pay = "Form"
            send_requests = bill.pay_url
            send_message = (
                f"<b>🆙 Пополнение баланса</b>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                f"❗ У вас имеется 30 минут на оплату счета.\n"
                f"🥝 Для пополнения баланса, нажмите на кнопку  <code>Перейти к оплате</code>\n"
                f"💵 Сумма пополнения: <code>{pay_amount}руб</code>\n"
                f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                f"🔄 После оплаты, нажмите на <code>Проверить оплату</code>"
            )

        await bot.delete_message(call.message.chat.id, del_msg.message_id)
        delete_msg = await call.message.answer(
            "🥝 <b>Платёж был создан.</b>",
        )
        await call.message.answer(
            send_message,
            reply_markup=keyboards.create_pay_qiwi_func(
                send_requests, generate_number_check, delete_msg.message_id, way_pay
            ),
        )


@dp.callback_query_handler(text_startswith="Pay:Form:")
async def check_qiwi_pay(call: CallbackQuery):
    receipt = call.data[9:].split(":")[0]
    message_id = call.data[9:].split(":")[1]
    get_payments = (
        settings["telegram"]["qiwi"],
        settings["telegram"]["token_qiwi"],
        settings["telegram"]["private_key"],
        settings["telegram"]["qiwi_nickname"],
        "form",
        "True",
    )

    if (
        get_payments[0] != "None"
        or get_payments[1] != "None"
        or get_payments[2] != "None"
    ):
        qiwi = QiwiP2P(get_payments[2])
        pay_comment = qiwi.check(
            bill_id=receipt
        ).comment  # Получение комментария платежа
        pay_status = qiwi.check(bill_id=receipt).status  # Получение статуса платежа
        pay_amount = float(
            qiwi.check(bill_id=receipt).amount
        )  # Получение суммы платежа в рублях
        pay_amount = int(pay_amount)
        if pay_status == "PAID":

            await bot.delete_message(call.message.chat.id, message_id)
            await call.message.delete()
            await call.message.answer(
                f"<b>✅ Вы успешно пополнили баланс на сумму {pay_amount}руб. Удачи ❤</b>\n"
                f"<b>📃 Чек:</b> <code>+{receipt}</code>",
                reply_markup=keyboards.functions_default,
            )

            use_date = datetime.datetime.now()
            use_date = str(use_date + relativedelta(months=+1)).split(" ")[0]
            with sqlite3.connect(path_db) as db:
                db.execute(
                    "UPDATE users SET time_subscribers = ? WHERE user_id = ?",
                    (
                        use_date,
                        str(call.from_user.id),
                    ),
                )

        elif pay_status == "EXPIRED":
            await bot.edit_message_text(
                "<b>❌ Время оплаты вышло. Платёж был удалён.</b>",
                call.message.chat.id,
                call.message.message_id,
            )
        elif pay_status == "WAITING":
            await call.message.answer("❗ Оплата не была произведена.")
        elif pay_status == "REJECTED":
            await bot.edit_message_text(
                "<b>❌ Счёт был отклонён.</b>",
                call.message.chat.id,
                call.message.message_id,
            )
    else:

        await bot.answer_callback_query(
            call.id,
            "❗ Извиняемся за доставленные неудобства,\n"
            "проверка платежа временно недоступна.\n"
            "⏳ Попробуйте чуть позже.",
        )


@dp.callback_query_handler(Text(startswith="profile"))
async def index(call: types.CallbackQuery):
    await call.message.delete()
    with sqlite3.connect(path_db) as db:
        user = db.execute(
            "SELECT * FROM users WHERE user_id = ?", (str(call.from_user.id),)
        ).fetchall()

    with sqlite3.connect(path_db) as db:
        find_user = db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (str(call.from_user.id),),
        ).fetchall()
    check_subscribe = find_user[0][2]

    await call.message.answer(
        f"🤖 Бот для отправки огромного количества смс и звонков в развлекательных целях.\n\n☎ Доступно сервисов: <code>10</code>\n"
        f"⌚ Подписка истекает: <code>{check_subscribe}</code>\n👤 Логин: @{call.from_user.username}\n🔑 Мой ID: {call.from_user.id}"
        f"\n\n❔ Не знаешь с чего начать?\nПрочти раздел '❗ Помощь'",
        reply_markup=keyboards.MAIN(call.from_user.id),
    )


@dp.message_handler(text="/start")
async def send_message(message: types.Message):
    await message.answer(text="⚡")

    with sqlite3.connect(path_db) as db:
        find_user = db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (str(message.from_user.id),),
        ).fetchall()

        if len(find_user) <= 0:
            with sqlite3.connect(path_db) as db:
                db.execute(
                    """INSERT INTO users(user_id, user_login, time_subscribers, banned)
                    VALUES(?,?,?,?);""",
                    (
                        str(message.from_user.id),
                        message.from_user.username,
                        "0",
                        "0",
                    ),
                )

        with sqlite3.connect(path_db) as db:
            find_user = db.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (str(message.from_user.id),),
            ).fetchall()
        check_subscribe = find_user[0][2]

        if len(check_subscribe) <= 2:
            await message.answer(
                "🛒 Оплатите доступ на месяц для работы с ботом\n\n✅Более 60 сервисов\n✅Многопоточность и Асинхронность выполнения атаки на номер\n✅ Возможность вписать свои приват прокси ЛЮБОГО вида\n✅ Анонимность, мы не храним информацию об атаках\n",
                reply_markup=keyboards.oplata,
            )

        elif len(check_subscribe) > 2:
            with sqlite3.connect(path_db) as db:
                user = db.execute(
                    "SELECT * FROM users WHERE user_id = ?",
                    (str(message.from_user.id),),
                ).fetchall()

            await message.answer(
                f"🤖 Бот для отправки огромного количества смс и звонков в развлекательных целях.\n\n☎ Доступно сервисов: <code>10</code>\n"
                f"⌚ Подписка истекает: <code>{check_subscribe}</code>\n👤 Логин: @{message.from_user.username}\n🔑 Мой ID: {message.from_user.id}"
                f"\n\n❔ Не знаешь с чего начать?\nПрочти раздел '❗ Помощь'",
                reply_markup=keyboards.MAIN(message.from_user.id),
            )


@dp.callback_query_handler(Text(startswith="antispam"))
async def send_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "<b>Введите ваш номер телефона</b>\n\n<code>Без +\nПример: 79999999999</code>"
    )
    await Form.antispam.set()


@dp.message_handler(state=Form.antispam)
async def send_message(message: types.Message, state: FSMContext):

    phone = message.text

    with sqlite3.connect(path_db) as db:
        db.execute(
            "INSERT INTO whitelist(user_id, username, phone) VALUES (?,?,?)",
            (message.from_user.id, message.from_user.username, phone),
        )

    await message.delete()
    await message.answer(
        "Успешно занес ваш номер в <b>WHITELIST</b>",
        reply_markup=keyboards.MAIN(message.from_user.id),
    )

    await state.finish()


@dp.callback_query_handler(Text(startswith="helpme"))
async def send_message(call: types.CallbackQuery):
    await call.answer(
        f"🔥 Актуальные контакаты администратора: {settings['admin_nickname']}"
    )
    await call.message.answer(
        f"🔥 Актуальные контакаты администратора: {settings['admin_nickname']}"
    )


@dp.callback_query_handler(Text(startswith="Zapusk"))
async def send_message(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.answer(
        "‼ Введите номер без +\nПример:\n<code>78255125961\n78252225261\n78555225961</code>"
    )
    await Form.getPhone.set()


@dp.message_handler(state=Form.getPhone)
async def send_message(message: types.Message, state: FSMContext):

    phone = message.text

    with sqlite3.connect(path_db) as db:
        tasks = db.execute(
            "SELECT * FROM tasks WHERE user_id = ?", (message.from_user.id,)
        ).fetchall()


        if len(tasks) >= 3:
            await message.answer(
                "❌ Вы не можете запустить спам на 4 номера, завершите 1 из номеров из вашего списка"
            )

        else:
            db.execute(
                "INSERT INTO tasks(username, user_id, timer, active, phone) VALUES (?,?,?,?,?)",
                (message.from_user.username, message.from_user.id, 3600, "True", phone),
            )

            await message.answer(
                f"✅ Успешно запустил бомбер на номер: <code>{phone}</code>\n✅ Бот выключит спам через 3600 секунд (1 час)"
            )

        await state.finish()


@dp.callback_query_handler(Text(startswith="my_rassilki"))
async def send_message(call: types.CallbackQuery, state: FSMContext):

    with sqlite3.connect(path_db) as db:
        tasks = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND active = ?",
            (call.from_user.id, "False"),
        ).fetchall()

    generate = InlineKeyboardMarkup()


    for task in tasks:
        generate.row(InlineKeyboardButton(text=f"ID: {task[0]} | PHONE: {task[5]}", callback_data=f"attack:{task[0]}"))

    await call.message.answer("✅ Активные атаки:", reply_markup=generate)


@dp.callback_query_handler(Text(startswith="attack"), state="*")
async def send_message(call: types.CallbackQuery, state: FSMContext):
    ID = call.data.split(":")[1]

    with sqlite3.connect(path_db) as db:
        db.execute("DELETE FROM tasks WHERE ID = ?", (ID,))

    await call.message.answer(f"✅ Успешно остановил спам на номер, ID операции: <b>{ID}</b>")

if __name__ == "__main__":
    executor.start_polling(dp)

