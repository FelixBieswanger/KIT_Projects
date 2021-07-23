from BibBot import BibBot
from Platzholder import Platzholder
from random import randint
import threading
import multiprocessing
from datetime import datetime
import datetime as dt
import time
import os
import json

MAX_THEAD_COUNT = 8


def multithread_buchen(year, month, day, period, user, thread_num, time_start):
    platzholder = Platzholder()
    lock = threading.Lock()

    def controll_bot(index):
        if platzholder.get() != None:
            return

        bot = BibBot(index, platzholder, lock)
        bot.anmelden(username=user["username"], password=user["password"])
        free_seats = bot.find_free_seats(
            jahr=str(year),
            monat=str(month),
            tag=str(day),
            period_param=period)
        if len(free_seats) > 0:
            platzholder.set(bot.platz_buchen(
                free_seats[randint(0, len(free_seats))-1]))

    while platzholder.get() == None:
        if (datetime.today() - time_start).seconds > 150:
            for i in range(5):
                print("=============")
            print("TIME IS UP")
            return

        threads = list()
        for i in range(thread_num):
            x = threading.Thread(target=controll_bot, args=(i,))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()
            print("Bibot", index, "finished")

    print("=================")
    print("Für:", user["name"])
    d = platzholder.get()
    for key in d:
        print(key, d[key])


while True:

    # get time now
    now = datetime.today()
    user_data = json.loads(os.environ.get("login_data", None))

    for user in user_data:
        multithread_buchen(
            year=now.year,
            month=now.month,
            day=now.day,
            period=0,
            user=user,
            thread_num=MAX_THEAD_COUNT,
            time_start=datetime.today())

    # es ist nach der buchungssession mittags
    if (now.hour >= 14 and now.minute >= 32) or now.hour > 14:
        tomorrow = now + dt.timedelta(days=1)

        # sleep to next day until 8.28
        start_morgen_nächster_tag = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 8, 28, 0)

        diff = (start_morgen_nächster_tag - datetime.today())
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        for user in user_data:
            multithread_buchen(
                year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day,
                period=0,
                user=user,
                thread_num=MAX_THEAD_COUNT,
                time_start=datetime.today())

    # es ist nach der buchungsessions morgens
    if(now.hour >= 8 and now.minute >= 32) or now.hour > 8:
        # sleep bis 14.28
        start_nachmittag = datetime(
            now.year, now.month, now.day, 14, 28, 0)

        diff = (start_nachmittag - datetime.today())
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)
        for user in user_data:
            multithread_buchen(
                year=now.year,
                month=now.month,
                day=now.day,
                period=1,
                user=user,
                thread_num=MAX_THEAD_COUNT,
                time_start=datetime.today())
