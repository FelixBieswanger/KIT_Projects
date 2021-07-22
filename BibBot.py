# @ Felix Bieswanger
import requests
from bs4 import BeautifulSoup


class BibBot:
    def __init__(self, index, platzholder, lock):
        # Meta Data
        self.session = requests.Session()
        self.base_url = "https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/"
        self.ares_prio = ["34", "35", "21", "19", "20"]
        self.area_names = {
            "35": "altbau 2.OG (empore)",
            "34": "altbau 2.OG",
            "21": "neubau 3.OG",
            "19": "neubau 2.OG",
            "20": "neubau 1.OG"
        }
        self.zeiten = ["vormittags", "nachmittags", "abends"]
        self.index = index
        self.platzholder = platzholder
        self.lock = lock
        print("Bibot", self.index, "has started")

    def build_url(self, endpoint, **kwargs):
        params = "&".join(["=".join((key, kwargs[key])) for key in kwargs])
        return self.base_url + endpoint + ".php?" + params

    def extract_param(self, url, param):
        s = url.find(param+"=")+len(param)+1
        e = url.find("&", s)
        return url[s:e]

    def anmelden(self, username, password):
        anmelde_url = self.build_url(endpoint="admin")
        content_anmeldung = {
            "NewUserName": username,
            "NewUserPassword": password,
            "EULA": True,
            "Action": "SetName",
            "MIME-Typ": "application/x-www-form-urlencoded"
        }

        anmeldung = self.session.post(anmelde_url, data=content_anmeldung)
        soup = BeautifulSoup(anmeldung.content, "html.parser")
        logon_url = soup.find("div", {"id": "logon_box"}).find("a")["href"]
        self.bib_id = self.extract_param(logon_url, "creatormatch")

    def find_free_seats(self, jahr, monat, tag, period_param):
        for area in self.ares_prio:
            scan_url = self.build_url(
                endpoint="day", year=jahr, month=monat, day=tag, area=area)
            resp = requests.get(scan_url)
            sitzplätze_html = BeautifulSoup(resp.content, "html.parser")
            sitzplätze_tags = sitzplätze_html.find_all("td", {"class": "new"})
            free_seats_url = [tag.find("a")["href"] for tag in sitzplätze_tags]
            plätze_in_area = list()
            for url in free_seats_url:
                if self.extract_param(url, "period") == period_param:
                    plätze_in_area.append({
                        "area": area,
                        "area_name": self.area_names[area],
                        "period": period_param,
                        "period_name": self.zeiten[int(period_param)],
                        "room": self.extract_param(url, "room"),
                        "year": jahr,
                        "month": monat,
                        "day": tag
                    })
            if len(plätze_in_area) != 0:
                return plätze_in_area
        return []

    def platz_buchen(self, platz):
        platz_url = self.build_url(endpoint="edit_entry",
                                   area=platz["area"],
                                   period=platz["period"],
                                   room=platz["room"],
                                   year=platz["year"],
                                   month=platz["month"],
                                   day=platz["day"]
                                   )
        speicher_url = self.build_url(endpoint="edit_entry_handler")

        platz_resp = self.session.get(platz_url).content.decode("utf-8")
        soup = BeautifulSoup(platz_resp)
        content_speichern = dict()
        for inpu in soup.find("form", {"id": "main"}).find_all("input", {"type": "hidden"}):
            content_speichern[inpu["name"]] = inpu["value"]

        if self.platzholder.get() == None:
            with self.lock:
                buchung_abschicken = self.session.post(
                    speicher_url, data=content_speichern).content.decode("utf-8")
                soup = BeautifulSoup(buchung_abschicken, "html.parser")
                for td in soup.find_all("td", {"class": "K writable"}):
                    if str(self.zeiten.index(td.find("a")["title"])) == platz["period"]:
                        print("Bibot", self.index, "Platz erfolgreich gebucht")
                        return platz
                print("Bibot", self.index, "Fehler bei Buchung")
                return None
