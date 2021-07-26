import threading
import multiprocessing
from datetime import datetime
import datetime as dt
import time
import os
import json
from MultithreadBooker import Booker


MAX_THEAD_COUNT = multiprocessing.cpu_count()

try:
    user_data = json.loads(os.environ.get("login_data", None))
except:
    with open("local_logindata.json", "r") as file:
        user_data = json.loads(file.read())


def start_booking(date, period):

    bookers = list()
    for user in user_data.values():
        booker = Booker(
            thread_num=2,
            user=user,
            year=date.year,
            month=date.month,
            day=date.day,
            period=period)

        booker.multithread_buchen(debug=True)


while True:

    # get time now
    now = datetime.today() - dt.timedelta(days=1)

    start_booking(now, period="1")

    # es ist nach der buchungssession mittags
    if (now.hour >= 14 and now.minute >= 32) or now.hour > 14:
        tomorrow = now + dt.timedelta(days=1)

        # sleep to next day until 8.28
        start_morgen_nächster_tag = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 8, 28, 0)

        print("wait until", start_morgen_nächster_tag)

        diff = (start_morgen_nächster_tag - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        start_booking(tomorrow, "0")

    # es ist nach der buchungsessions morgens
    if(now.hour >= 8 and now.minute >= 32) or now.hour > 8:
        # sleep bis 14.28
        start_nachmittag = datetime(
            now.year, now.month, now.day, 14, 28, 0)

        print("wait until", start_nachmittag)

        diff = (start_nachmittag - now)
        print("sleeping for", diff.seconds, "seconds")
        time.sleep(diff.seconds)

        start_booking(now, "1")
