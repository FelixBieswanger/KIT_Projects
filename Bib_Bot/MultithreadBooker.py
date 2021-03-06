
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
        thread_tryed_seats = list()
        #möglichkeit um die platzsuche neu zu starten
        plätze_leer =False
        #sodass wenn die zu buchenden möglichkeiten ausgegangen sind, nicht wieder die selbe area gescaned wird
        #kann hiermit der index incrementiert und so die nächste area aus der prio liste gescaned werden
        area_bonus = 0

        # Solange bis von einem der Threads ein Platz bebucht wurde
        while not self.platzholder.get_threds_stop():

            if self.platzholder.get_available_seat_count() == 0 or plätze_leer:
                if plätze_leer:
                    area_bonus += 1
                #durch den modulo operator wird sicher gestellt, dass der ausgesuchte index immer rotierend in der area prio bleibt
                area = bot.area_prio[(bot.index + area_bonus) % len(bot.area_prio)]

                free_seats = bot.find_free_seats(
                    jahr=self.year,
                    monat=self.month,
                    tag=self.day,
                    period_param=self.period,
                    area=area)

                print("bibot", bot.index, "sucht in", bot.area_names[area],"hat",len(free_seats),"plätze gefunden")

                for seat in free_seats:
                    self.platzholder.add_seat(seat)

            plätze_noch_nicht_versucht = self.platzholder.get_seats()
            for seat in thread_tryed_seats:
                if seat in plätze_noch_nicht_versucht:
                    plätze_noch_nicht_versucht.remove(seat)

            if len(plätze_noch_nicht_versucht) > 0:
                plätze_leer = False

                # pick platz
                platz_buchungs_versuch = None
                for area in BibBot.area_prio:
                    if platz_buchungs_versuch is None:
                        for seat in plätze_noch_nicht_versucht:
                            if seat["area"] == area:
                                platz_buchungs_versuch = seat
                                break

                potentieller_platz = bot.platz_buchen(platz_buchungs_versuch)
                # Es kann sein dass die Buchung nicht geklappt hat (dann wird Null zurückgegeben)
                if potentieller_platz != None:
                    # Defining critical area, dh nur ein thread kann sich in diesem Bereich befinden
                    # In diesem Thread hat die Buchung geklappt

                    self.platzholder.set(potentieller_platz)
                    print("Bibot", bot.index,
                          "hat gebucht und fährt nun runter..")
                    self.platzholder.set_threads_stop()
                    return
                else:
                    if self.platzholder.get() == None:
                        print("Bibot", bot.index,
                              "Buchung nicht geklappt, fängt jz neu an..")

            else:
                plätze_leer = True
                print("Bibot", bot.index, "hat schon alle Plätze versucht")

    def multithread_buchen(self, time_start,nachts=False, debug=False):

        vllt_schon_gebuchter_platz = self.bots[0].find_booked_seat(
            jahr=self.year,
            monat=self.month,
            tag=self.day,
            period_param=self.period)
        if vllt_schon_gebuchter_platz is not None:
            print("=================")
            print("Für:", self.user["name"])
            for key in vllt_schon_gebuchter_platz:
                print(key, vllt_schon_gebuchter_platz[key])
            return

  
        # Starte es um 30 nach, weil wenn davor (also 28 o 29) ein PLatz gebucht wird, wird dieser um 30 wieder gelöscht
        date_30 = datetime(time_start.year, time_start.month,
                           time_start.day, time_start.hour, 30)
        print(date_30,time_start)
        wait_seconds = (date_30-time_start).seconds

        if debug == False and nachts == False:
            print("Waiting ", wait_seconds, "seconds until its time to go...")
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
                self.platzholder.set_threads_stop()
                break
            time.sleep(1)
        # Synchronisation der Threads
        for thread in self.threads:
            thread.join()

        #wenn in der kit keiner gefunden wurde, dann schau in HKA
        if type(self.platzholder.get()) != dict:
            #try to get a seat in HKA
            for area in ["28","29"]:
                if self.platzholder.get() == None:
                    free_seats = self.bots[0].find_free_seats(
                            jahr=self.year,
                            monat=self.month,
                            tag=self.day,
                            period_param=self.period,
                            area=area)

                    for platz in free_seats:
                        potentieller_platz = self.bots[0].platz_buchen(platz)

                        if potentieller_platz is not None:
                            print("Bibot 0 (HKA) hat gebucht und fährt nun runter..")
                            self.platzholder.set(potentieller_platz) 
                            break


        if type(self.platzholder.get()) == dict:
            booked_platz = self.bots[0].find_booked_seat(
                jahr=self.year, monat=self.month, tag=self.day, period_param=self.period)
            print("=================")
            print("Für:", self.user["name"])
            for key in booked_platz:
                print(key, booked_platz[key])
        else:
            for i in range(5):
                print("=============")
            print("TIME IS UP")
