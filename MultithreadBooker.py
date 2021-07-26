
from Platzholder import Platzholder
from BibBot import BibBot
from random import randint
import threading
from datetime import datetime
import time


class Booker:
    def __init__(self, thread_num, user, year, month, day, period):
        self.thread_num = thread_num
        self.platzholder = Platzholder()
        self.lock = threading.Lock()
        self.user = user
        self.year = str(year)
        self.month = str(month)
        self.day = str(day)
        self.period = str(period)

        # Es werden so viele bots erstellt wie threads dem nutzer zugewiesen wurden
        # Diese Bots melden sich schonmal an (muss nur einmal durchgeführt werden und wird in einer Session gespeichert)
        self.bots = list()
        self.threads = list()
        for i in range(self.thread_num):
            bot = BibBot(i)
            bot.anmelden(
                username=self.user["username"], password=self.user["password"])
            self.bots.append(bot)
            self.threads.append(threading.Thread(
                target=self.bot_thread, args=(bot,)))
            print("Bibot", bot.index,
                  "was created and finished setting up for user", self.user["name"])

    """
    Methode die Defininiert was im Thread passieren soll
    """

    def bot_thread(self, bot):

        print("Bibot", bot.index, "has started working within a thread")

        # Solange bis von einem der Threads ein Platz bebucht wurde
        while self.platzholder.get() == None:

            free_seats = bot.find_free_seats(
                jahr=self.year,
                monat=self.month,
                tag=self.day,
                period_param=self.period)

            if len(free_seats) > 0:
                potentieller_platz = bot.platz_buchen(
                    free_seats[randint(0, len(free_seats))-1])
                # Es kann sein dass die Buchung nicht geklappt hat (dann wird Null zurückgegeben)
                if potentieller_platz != None:
                    # Defining critical area, dh nur ein thread kann sich in diesem Bereich befinden
                    # In diesem Thread hat die Buchung geklappt
                    with self.lock:
                        self.platzholder.set(potentieller_platz)
                        print("Bibot", bot.index,
                              "hat gebucht und fährt nun runter..")
                        return
                else:
                    if self.platzholder.get() == None:
                        print("Bibot", bot.index,
                              "Buchung nicht geklappt, fängt jz neu an..")

    def multithread_buchen(self, time_start=datetime.today(), debug=False):

        # Starte es um 30 nach, weil wenn davor (also 28 o 29) ein PLatz gebucht wird, wird dieser um 30 wieder gelöscht
        date_30 = datetime(time_start.year, time_start.month,
                           time_start.day, time_start.hour, 30)
        wait_seconds = (date_30-time_start).seconds

        if not debug:
            print("Waiting "+wait_seconds+"until its time to go...")
            time.sleep(wait_seconds)

        print("Starting " + str(self.thread_num) +
              " threads for user", self.user["name"])
        # Start all thread
        for thread in self.threads:
            thread.start()

        while self.platzholder.get() == None:
            # Um 33 (also 5min nach start) aufhören, dann sind eh alle gebucht. (2 Min extra um vllt noch Plätze wegzucrashen
            # die für andere gebucht wurden)
            if(datetime.today() - time_start).seconds > 150:
                self.platzholder.set("Stop Threads")
                break
            time.sleep(1)

        # Synchronisation der Threads
        for thread in self.threads:
            thread.join()

        if type(self.platzholder.get()) == dict:
            booked_platz = self.bots[0].find_booked_seat(
                jahr=self.year, monat=self.month, tag=self.day, period_param=self.period)
            booked_platz["area_name"] = booked_platz["area_name"].replace(
                "KIT-BIB", "")
            booked_platz["bisHalb"] = False
            booked_platz["when"] = time_start.strftime(
                '%A') + ", "+["vormittags", "nachmittags", "abends"][int(self.period)]
            print("=================")
            print("Für:", self.user["name"])
            for key in booked_platz:
                print(key, booked_platz[key])
            return booked_platz
        else:
            for i in range(5):
                print("=============")
            print("TIME IS UP")

            return {
                "area_name": "",
                "room": "KEINEN BEKOMMEN",
                "bisHalb": False,
                "when": time_start.strftime(
                    '%A') + ", "+["vormittags", "nachmittags", "abends"][int(self.period)]
            }
