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

booked_seats = list()


def multithread_buchen(year, month, day, period, user, thread_num, time_start):
    """
    SET UP (Static Part)
    Der Prozess wird allerdings 3min vor start der Buchungsphase gestatet, sodass Setup bereits durchgeführt werden kann
    """

    platzholder = Platzholder()
    lock = threading.Lock()

    # Es werden so viele bots erstellt wie threads dem nutzer zugewiesen wurden
    # Diese Bots melden sich schonmal an (muss nur einmal durchgeführt werden und wird in einer Session gespeichert)
    bots = list()
    for i in range(thread_num):
        bot = BibBot(i)
        bot.anmelden(username=user["username"], password=user["password"])
        bots.append(bot)
        print("Bibot", bot.index, "was created and finished setting up")

    """
    Methode die Defininiert was im Thread passieren soll
    """
    def bot_thread(bot):

        print("Bibot", bot.index, "has started working within a thread")

        # Solange bis von einem der Threads ein Platz bebucht wurde
        while platzholder.get() == None:

            free_seats = bot.find_free_seats(
                jahr=str(year),
                monat=str(month),
                tag=str(day),
                period_param=period)

            if len(free_seats) > 0:
                potentieller_platz = bot.platz_buchen(
                    free_seats[randint(0, len(free_seats))-1])
                # Es kann sein dass die Buchung nicht geklappt hat (dann wird Null zurückgegeben)
                if potentieller_platz != None:
                    # Defining critical area, dh nur ein thread kann sich in diesem Bereich befinden
                    # In diesem Thread hat die Buchung geklappt
                    with lock:
                        platzholder.set(potentieller_platz)
                        print("Bibot", bot.index,
                              "hat gebucht und fährt nun runter..")
                        return
                else:
                    if platzholder.get() == None:
                        print("Bibot", bot.index,
                              "Buchung nicht geklappt, fängt jz neu an..")

    threads = list()
    for bot in bots:
        x = threading.Thread(target=bot_thread, args=(bot,))
        threads.append(x)
        x.start()

    while platzholder.get() == None:
        # Um 33 (also 5min nach start) aufhören, dann sind eh alle gebucht. (2 Min extra um vllt noch Plätze wegzucrashen
        # die für andere gebucht wurden)
        if(datetime.today() - time_start).seconds > 150:
            platzholder.set("Stop Threads")
            break
        time.sleep(1)

    for thread in threads:
        thread.join()

    if type(platzholder.get()) == dict:
        print("=================")
        print("Für:", user["name"])
        d = platzholder.get()

        for key in d:
            print(key, d[key])
    else:
        for i in range(5):
            print("=============")
        print("TIME IS UP")


while True:

    # get time now
    now = datetime.today()
    try:
        user_data = json.loads(os.environ.get("login_data", None))
    except:
        with open("local_logindata.json", "r") as file:
            user_data = json.loads(file.read())

    for user in user_data:
        multithread_buchen(
            year=now.year,
            month=now.month,
            day=now.day,
            period="2",
            user=user,
            thread_num=MAX_THEAD_COUNT,
            time_start=datetime.today())

    # es ist nach der buchungssession mittags
    if (now.hour >= 14 and now.minute >= 32) or now.hour > 14:
        tomorrow = now + dt.timedelta(days=1)

        # sleep to next day until 8.28
        start_morgen_nächster_tag = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 8, 28, 0)

        diff = (start_morgen_nächster_tag - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        for user in user_data:
            multithread_buchen(
                year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day,
                period="0",
                user=user,
                thread_num=MAX_THEAD_COUNT,
                time_start=datetime.today())

    # es ist nach der buchungsessions morgens
    if(now.hour >= 8 and now.minute >= 32) or now.hour > 8:
        # sleep bis 14.28
        start_nachmittag = datetime(
            now.year, now.month, now.day, 14, 28, 0)

        diff = (start_nachmittag - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)
        for user in user_data:
            multithread_buchen(
                year=now.year,
                month=now.month,
                day=now.day,
                period="1",
                user=user,
                thread_num=MAX_THEAD_COUNT,
                time_start=datetime.today())
