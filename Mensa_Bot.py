import requests 
from datetime import date
from bs4 import BeautifulSoup
import os
import json
from twilio.rest import Client

class Mensa_Bot:
    phone_numbers = []

    def send_menu():
        today = date.today()

        if today.weekday() < 5:

            # Entferne +1 und -5
            calender_week_num = today.isocalendar()

            d = requests.get("https://www.sw-ka.de/en/essen/?kw="+str(calender_week_num))
            soup = BeautifulSoup(d.content, "html.parser")
            linie1 = soup.find("div", {"id": "fragment-c1-1"}).find(
                "table").find("td", {"class": "mensadata"}).find_all("tr")

            menu = list()
            for tr in linie1:
                fooddata = tr.find_all("td")
                food_name = fooddata[1].text
                food_name = food_name.split("[")[0]
                food_price = fooddata[2].find("span").text
                menu.append(food_name+" - "+food_price)

            s = "======================="
            s += "\n"
            s += today.strftime("%A der %d.%m %Y")
            s += "\n"
            s+="======================="
            s += "\n"
            for dish in menu:
                if (i:= menu.index(dish)) != len(menu)-1:
                    s += str(i+1) + ") "
                s += dish
                s += "\n"
                s += "\n"

            client = Client(os.environ.get("account_sid", None), os.environ.get("auth_token", None))
            for number in json.loads(os.environ.get("phone_numbers", None)):
                message = client.messages.create(
                    body=s,
                    from_='whatsapp:+14155238886',
                    to=number
                )

                print(message.status,"for",number)


