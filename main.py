from BibBot import BibBot
from Platzholder import Platzholder
from random import randint
import threading
import multiprocessing

platzholder = Platzholder()
lock = threading.Lock()


def get_bib_platz(index):
    if platzholder.get() != None:
        return

    bot = BibBot(index, platzholder, lock)
    bot.anmelden(username="@2374109", password="63182776")
    free_seats = bot.find_free_seats(
        jahr="2021",
        monat="07",
        tag="22",
        period_param="1")
    platzholder.set(bot.platz_buchen(
        free_seats[randint(0, len(free_seats))-1]))


while platzholder.get() == None:
    threads = list()
    for i in range(multiprocessing.cpu_count()):
        x = threading.Thread(target=get_bib_platz, args=(i,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        thread.join()
        print("Bibot", index, "finished")

for i in range(3):
    print()
print("=================")
for key in (d:= platzholder.get()):
    print(key, d[key])
