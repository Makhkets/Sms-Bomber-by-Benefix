import sqlite3
import time
import trio
from loguru import logger
import bomber
import datetime
from dateutil.relativedelta import *

path_db = "database.db"


async def main():
    while True:
        with sqlite3.connect(path_db) as db:
            tasks = db.execute("SELECT * FROM tasks WHERE isStart = ? AND start = ?", ("True", "False",)).fetchall()

        logger.info(tasks)
        if len(tasks) > 0:
            for i in tasks:
                await start(i)

        time.sleep(10)


async def start(i):
    while True:
        use_date = datetime.datetime.now()
        use_date = str(use_date + relativedelta(hours=0)).split(".")[0].split()[1].split(":")

        timer = use_date[0] + use_date[1]
        user_time = i[1]
        if int(user_time) >= int(timer):
            bomb = bomber.Bomber(i[0])
            if bomb.check() == False:
                break

            services = [bomb.telegram, bomb.ok, bomb.citilink, bomb.mts, bomb.yota, bomb.megafon]
            # services = [bomb.ok]

            with sqlite3.connect(path_db) as db:
                db.execute("UPDATE tasks SET start = ? WHERE phone = ? AND isStart = ?", ("True", i[0], "True"))
            for _ in services:
                await _()

        else:
            logger.info("Закончилось время, выключаю спам.")
            break

            with sqlite3.connect(path_db) as db:
                db.execute("UPDATE tasks SET isStart = ? WHERE phone = ? AND isStart = ?", ("False", i[0], "True"))

            with sqlite3.connect(path_db) as db:
                db.execute("UPDATE tasks SET start = ? WHERE phone = ? AND isStart = ?", ("True", i[0], "True"))
            break

if __name__ == "__main__":
    trio.run(main)


