from flask import Flask
from flask import request
import os
import json
from BibBot import BibBot
from datetime import datetime

bot = BibBot()


app = Flask(__name__)

try:
    login_data = json.loads(os.environ.get("login_data", None))
except:
    with open(os.path.dirname(__file__)+"/../local_logindata.json", "r") as file:
        login_data = json.loads(file.read())


@app.route('/getplatz', methods=["GET"])
def get():
    username = request.args.get('username')

    if username in login_data.keys():
        pw = login_data[username]["password"]

        bot.anmelden(username=username, password=pw)
        now = datetime.today()

        period = "0"
        if now.hour >= 12:
            period = "1"

        booked_platz = bot.find_booked_seat(
            jahr=str(now.year),
            monat=str(now.month),
            tag=str(now.day),
            period_param=period
        )

        if booked_platz is None:
            return {
                "area_name": "",
                "room": "No Seat",
                "bisHalb": False,
                "when": now.strftime(
                    '%a') + ", "+["vormittags", "nachmittags", "abends"][int(period)]
            }
        else:

            booked_platz["area_name"] = booked_platz["area_name"].replace(
                "KIT-BIB", "")
            booked_platz["bisHalb"] = False

            if period == "1" and now.hour >= 12:
                booked_platz["when"] = now.strftime(
                    '%A') + ", ab 14h!"
            elif period == "1":
                booked_platz["when"] = now.strftime(
                    '%A') + ", ab 14.30"
            elif period == "0" and now.hour >= 0:
                booked_platz["when"] = now.strftime(
                    '%A') + ", ab 8h!"

            return booked_platz
    else:
        return {}


if __name__ == '__main__':
    app.run(debug=True)
