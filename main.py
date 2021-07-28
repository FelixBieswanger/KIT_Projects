
import multiprocessing
from datetime import date, datetime
import datetime as dt
import time
import os
import json
from MultithreadBooker import Booker
from Mensa_Bot import Mensa_Bot



MAX_THEAD_COUNT = multiprocessing.cpu_count()

try:
    user_data = json.loads(os.environ.get("login_data", None))
except:
    with open("local_logindata.json", "r") as file:
        user_data = json.loads(file.read())


def start_booking(date, period, nachts):

    bookers = list()
    for user in user_data.values():
        booker = Booker(
            thread_num=MAX_THEAD_COUNT,
            user=user,
            year=date.year,
            month=date.month,
            day=date.day,
            period=period)

        booker.multithread_buchen(
            debug=False, nachts=nachts, time_start=datetime.today())

while True:

    # get time now
    now = datetime.today()

    # es ist vor der nacht buchung
    if (now.hour >= 14 and now.minute >= 32) or now.hour > 14:
        # wait bis kurz vor mitternacht
        start_nacht = datetime(
            now.year, now.month, now.day, 0, 0) + dt.timedelta(days=1)

        print("wait until", start_nacht)
        diff = (start_nacht-now).seconds
        print("sleeping for", diff, "seconds")
        time.sleep(diff)

        date_2_tagen = start_nacht + dt.timedelta(days=1)
        print("Buche für", date_2_tagen)

        start_booking(date_2_tagen, "1", nachts=True)

    # es ist vor der morgens buchung
    elif now.hour >= 0 or (now.hour >= 8 and now.minute >= 32):
        # sleep to next day until 8.28
        start_morgens = datetime(
            now.year, now.month, now.day, 8, 28, 0)
        print("wait until", start_morgens)

        diff = (start_morgens - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        start_booking(start_morgens, "0", nachts=False)

        #send Mensa Menu
        Mensa_Bot.send_menu()

    # es ist nach der buchungsessions morgens
    else:
    #(now.hour >= 8 and now.minute >= 32) or now.hour > 8:
        # sleep bis 14.28
        start_nachmittag = datetime(
            now.year, now.month, now.day, 14, 28, 0)

        print("wait until", start_nachmittag)

        diff = (start_nachmittag - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        start_booking(now, "1", nachts=False)
