import asyncio
import json
import sqlite3
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
    ipv4 = State()
    http = State()
    socks4 = State()

    getPhone = State()


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

@dp.message_handler(text="/start")
async def send_message(message: types.Message):
    await message.answer(text="⚡")

    with sqlite3.connect(path_db) as db:
        find_user = db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (str(message.from_user.id),),
        ).fetchall()
        logger.success(find_user)

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
        logger.debug(len(check_subscribe))
        if len(check_subscribe) <= 2:
            await message.answer(
                "🛒 Оплатите доступ на месяц для работы с ботом\n\n✅Более 60 сервисов\n✅Многопоточность и Асинхронность выполнения атаки на номер\n✅ Возможность вписать свои приват прокси ЛЮБОГО вида\n✅ Анонимность, мы не храним информацию об атаках\n",
                reply_markup=keyboards.oplata,
            )

        elif len(check_subscribe) > 2:
            await message.answer(f"💣 Приветствую вас в мощнейшем бомбере во всем рунете\n\n⌛ Ваша подписка истекает: {check_subscribe}\nСоздатель {settings['admin_nickname']}", reply_markup=keyboards.functions_default)

@dp.message_handler(text="👤 личный кабинет")
async def send_message(message: types.Message):
    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchall()

    text = f"""
📱 Ваш профиль:
〰〰〰〰〰〰〰〰〰
🔑 Мой ID: {message.from_user.id}
👤 Логин: @{message.from_user.username}
〰〰〰〰〰〰〰〰〰
⌛ Подписка длиться до: {user[0][2]}
    """

    await message.answer(text)

@dp.message_handler(text="🎄 Связаться с администратором")
async def send_message(message: types.Message):
    await message.answer(f"🔥 Актуальные контакаты администратора: {settings['admin_nickname']}")

@dp.message_handler(text="⚙ Прокси")
async def send_message(message: types.Message):
    await message.delete()
    await message.answer("❓ Выберите какие прокси вы хотите загрузить", reply_markup=keyboards.proxy_choice)

    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(message.from_user.id),)).fetchall()
    proxy = user[0][4]

    await message.answer(f"💎 Сейчас используется этот вид прокси: <b>{proxy}</b>", reply_markup=keyboards.proxy_inline_choice)

@dp.message_handler(text="⏮ Назад", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await state.finish()
    await message.delete()
    await message.answer("Переместил вас в главное меню", reply_markup=keyboards.functions_default)

@dp.callback_query_handler(lambda c: c.data == "ipv4")
async def process_callback_button1(call: types.CallbackQuery):
    await call.message.delete()
    with sqlite3.connect(path_db) as db:
        db.execute("UPDATE users SET proxy = ? WHERE user_id = ?", ("ipv4", str(call.from_user.id),))


    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(call.from_user.id),)).fetchall()
    proxy = user[0][4]
    await call.message.answer(f"💎 Сейчас используется этот вид прокси: <b>{proxy}</b>", reply_markup=keyboards.proxy_inline_choice)

@dp.callback_query_handler(lambda c: c.data == "http")
async def process_callback_button1(call: types.CallbackQuery):
    await call.message.delete()
    with sqlite3.connect(path_db) as db:
        db.execute("UPDATE users SET proxy = ? WHERE user_id = ?", ("http", str(call.from_user.id),))

    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(call.from_user.id),)).fetchall()
    proxy = user[0][4]
    await call.message.answer(f"💎 Сейчас используется этот вид прокси: <b>{proxy}</b>", reply_markup=keyboards.proxy_inline_choice)

@dp.callback_query_handler(lambda c: c.data == "socks4")
async def process_callback_button1(call: types.CallbackQuery):
    await call.message.delete()
    with sqlite3.connect(path_db) as db:
        db.execute("UPDATE users SET proxy = ? WHERE user_id = ?", ("socks4", str(call.from_user.id),))

    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(call.from_user.id),)).fetchall()
    proxy = user[0][4]
    await call.message.answer(f"💎 Сейчас используется этот вид прокси: <b>{proxy}</b>", reply_markup=keyboards.proxy_inline_choice)

@dp.callback_query_handler(lambda c: c.data == "none_proxy")
async def process_callback_button1(call: types.CallbackQuery):
    await call.message.delete()
    with sqlite3.connect(path_db) as db:
        db.execute("UPDATE users SET proxy = ? WHERE user_id = ?", ("none_proxy", str(call.from_user.id),))

    with sqlite3.connect(path_db) as db:
        user = db.execute("SELECT * FROM users WHERE user_id = ?", (str(call.from_user.id),)).fetchall()
    proxy = user[0][4]
    await call.message.answer(f"💎 Сейчас используется этот вид прокси: <b>{proxy}</b>", reply_markup=keyboards.proxy_inline_choice)

# 🔅 IPV4
@dp.message_handler(text="🔅 IPV4")
async def send_message(message: types.Message):
    await Form.ipv4.set()
    await message.answer("❗ Введите прокси в таком виде:\n\n<code>1.0.1.0:6000\n1.0.1.0:6000\n1.0.1.0:6000</code>")


@dp.message_handler(state=Form.ipv4)
async def send_message(message: types.Message, state: FSMContext):
    proxies = message.text
    if len(proxies) > 5:
        with sqlite3.connect(path_db) as db:
            db.execute("UPDATE users SET ipv4_proxies = ? WHERE user_id = ?", (proxies, str(message.from_user.id)),)
    else:
        await message.answer("Вводите прокси!")

    await message.answer("⚜ Успешно обновил список прокси")
    await state.finish()

@dp.message_handler(text="🔅 HTTP/HTTPS", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await Form.http.set()
    await message.answer("❗ Введите прокси в таком виде:\n\n<code>1.0.1.0:6000\n1.0.1.0:6000\n1.0.1.0:6000</code>")


@dp.message_handler(state=Form.http)
async def send_message(message: types.Message, state: FSMContext):
    proxies = message.text
    if len(proxies) > 5:
        with sqlite3.connect(path_db) as db:
            db.execute("UPDATE users SET http_proxies = ? WHERE user_id = ?", (proxies, str(message.from_user.id)),)
    else:
        await message.answer("Вводите прокси!")

    await message.answer("⚜ Успешно обновил список прокси")
    await state.finish()

@dp.message_handler(text="🔅 SOCKS4", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await Form.socks4.set()
    await message.answer("❗ Введите прокси в таком виде:\n\n<code>1.0.1.0:6000\n1.0.1.0:6000\n1.0.1.0:6000</code>")


@dp.message_handler(state=Form.socks4)
async def send_message(message: types.Message, state: FSMContext):
    proxies = message.text
    if len(proxies) > 5:
        with sqlite3.connect(path_db) as db:
            db.execute("UPDATE users SET socks4_proxies = ? WHERE user_id = ?", (proxies, str(message.from_user.id)),)
    else:
        await message.answer("Вводите прокси!")

    await message.answer("⚜ Успешно обновил список прокси")
    await state.finish()

# 🌩 Начать атаку
@dp.message_handler(text="🌩 Начать атаку", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await state.finish()
    await  message.answer("Выберите пункт", reply_markup=keyboards.bomb)


@dp.message_handler(text="🟢 Начать атаку", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("‼ Введите номер без +\nПример:\n<code>78255125961\n78252225261\n78555225961</code>")
    await Form.getPhone.set()


@dp.message_handler(state=Form.getPhone)
async def send_message(message: types.Message, state: FSMContext):
    phone = message.text
    with sqlite3.connect(path_db) as db:
        user = db.execute("""SELECT * FROM tasks WHERE user_id = ? AND isStart = ?""", (str(message.from_user.id), "True",)).fetchall()

    try:
        if len(user[0]) > 3:
            await message.answer("У вас уже есть запущенный спам на номер!")
            await state.finish()
        else:
            if phone.isdigit():
                phone = phone.replace("+", "")
                await message.answer(f"🔥 Запускаю спам на номер <code>{phone}</code>")
                use_date = datetime.datetime.now()
                use_date = str(use_date + relativedelta(hours=+1)).split(".")[0].split()[1].split(":")
                timer = use_date[0] + use_date[1]
                with sqlite3.connect(path_db) as db:
                    db.execute("""INSERT INTO tasks
                                      (phone, timestop, isStart, username, user_id)
                                      VALUES (?, ?, ?, ?, ?);""", (phone, timer, "True", message.from_user.username, str(message.from_user.id),)) # True , надо включить
                await state.finish()
            else:
                await message.answer("Вы ввели не номер!")
                await state.finish()
    except IndexError:
        if phone.isdigit():
            phone = phone.replace("+", "")
            await message.answer(f"🔥 Запускаю спам на номер <code>{phone}</code>")
            use_date = datetime.datetime.now()
            use_date = str(use_date + relativedelta(hours=+1)).split(".")[0].split()[1].split(":")
            timer = use_date[0] + use_date[1]
            with sqlite3.connect(path_db) as db:
                db.execute("""INSERT INTO tasks
                                  (phone, timestop, isStart, username, user_id)
                                  VALUES (?, ?, ?, ?, ?);""", (phone, timer, "True", message.from_user.username,
                                                               str(message.from_user.id),))  # True , надо включить
            await state.finish()
        else:
            await message.answer("Введите номер!")


@dp.message_handler(text="🔴 Остановить атаку", state="*")
async def send_message(message: types.Message, state: FSMContext):
    await state.finish()
    with sqlite3.connect(path_db) as db:
        find_task = db.execute("SELECT * FROM tasks WHERE user_id = ? AND isStart = ?", (str(message.from_user.id), "True",)).fetchall()

    if len(find_task) >= 1:
        with sqlite3.connect(path_db) as db:
             db.execute("UPDATE tasks SET isStart = ? WHERE user_id = ?", ("False", str(message.from_user.id),))
        await message.answer(f"Успешно остановил атаку на номер: <code>{find_task[0][0]}</code>")
    else:
        await message.answer("У вас нет активных атак 😪")



if __name__ == "__main__":
    executor.start_polling(dp)
