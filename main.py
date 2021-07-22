from BibBot import BibBot
from Platzholder import Platzholder
from random import randint
import threading
import multiprocessing
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-fri', hour="14", minute="29")
def scheduled_job():
    platzholder = Platzholder()
    lock = threading.Lock()

    today = datetime.today()

    def get_bib_platz(index):
        if platzholder.get() != None:
            return

        bot = BibBot(index, platzholder, lock)
        bot.anmelden(username="@2374109", password="63182776")
        free_seats = bot.find_free_seats(
            jahr=str(today.year),
            monat=str(today.month),
            tag=str(today.day),
            period_param="1")
        platzholder.set(bot.platz_buchen(
            free_seats[randint(0, len(free_seats))-1]))

    while platzholder.get() == None:
        if datetime.today().minute == 32:
            return

        threads = list()
        for i in range(multiprocessing.cpu_count()):
            x = threading.Thread(target=get_bib_platz, args=(i,))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            thread.join()
            print("Bibot", index, "finished")

    print("=================")
    d = platzholder.get()
    for key in d:
        print(key, d[key])


sched.start()
