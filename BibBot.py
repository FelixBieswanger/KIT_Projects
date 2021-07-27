# @ Felix Bieswanger
import requests
from bs4 import BeautifulSoup


class BibBot:
    area_prio = ["34", "35", "21", "19", "20", "29", "28"]

    def __init__(self, index=0):
        # Meta Data
        self.session = requests.Session()
        self.base_url = "https://raumbuchung.bibliothek.kit.edu/sitzplatzreservierung/"
        self.area_prio = ["34", "35", "21", "19", "20", "29", "28"]
        self.area_names = {
            "35": "altbau 2.OG (empore)",
            "34": "altbau 2.OG",
            "21": "neubau 3.OG",
            "19": "neubau 2.OG",
            "20": "neubau 1.OG",
            "29": "HS Ost",
            "28": "HS West"
        }
        self.zeiten = ["vormittags", "nachmittags", "abends"]
        self.index = index

    def build_url(self, endpoint, **kwargs):
        params = "&".join(["=".join((key, kwargs[key])) for key in kwargs])
        return self.base_url + endpoint + ".php?" + params

    def extract_param(self, url, param):
        s = url.find(param+"=")+len(param)+1
        e = url.find("&", s)
        return url[s:e]

    def extract_form_params(self, soup, form_id):
        params = dict()
        for inpu in soup.find("form", {"id": form_id}).find_all("input", {"type": "hidden"}):
            params[inpu["name"]] = inpu["value"]
        return params

    def anmelden(self, username, password):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
        }

        anmelde_url = self.build_url(endpoint="admin")

        anmelde_seite = self.session.get(
            anmelde_url, headers=headers).content.decode("utf-8")

        content_anmeldung = self.extract_form_params(soup=BeautifulSoup(
            anmelde_seite, "html.parser"), form_id="logon")

        params = {
            "NewUserName": username,
            "NewUserPassword": password,
            "EULA": True,
            "Action": "SetName",
            "MIME-Typ": "application/x-www-form-urlencoded"
        }

        for k in params:
            content_anmeldung[k] = params[k]

        anmeldung = self.session.post(
            anmelde_url, data=content_anmeldung, headers=headers)

        soup = BeautifulSoup(anmeldung.content.decode("utf-8"), "html.parser")
        logon_url = soup.find("div", {"id": "logon_box"}).find("a")["href"]
        self.bib_id = self.extract_param(logon_url, "creatormatch")

    def find_booked_seat(self, jahr, monat, tag, period_param):

        for area in self.area_prio:
            # URL Bauen und Request für Belegung der Etage an Server schicken
            scan_url = self.build_url(
                endpoint="day", year=jahr, month=monat, day=tag, area=area)
            resp = self.session.get(scan_url).content.decode("utf-8")

            # Alle Freien Plätze extrahieren
            soup = BeautifulSoup(resp, "html.parser")

            for td in soup.find_all("td", {"class": "K writable"}):
                a_tag = td.find("a")
                if str(self.zeiten.index(a_tag["title"].split(" ")[0])) == str(period_param):
                    buchungs_id = self.extract_param(
                        url=a_tag["href"], param="id")

                    buchungs_info_url = self.build_url(
                        endpoint="view_entry", id=buchungs_id, area=area, day=tag, month=monat, year=jahr)

                    buchungs_info = self.session.get(
                        buchungs_info_url).content.decode("utf-8")
                    soup2 = BeautifulSoup(buchungs_info, "html.parser")

                    table = soup2.find("tbody")
                    for tr in table.find_all("tr"):
                        tds = [td.text for td in tr.find_all("td")]
                        if tds[0] == "Sitzplatz:":
                            platz_str = [s.strip()
                                         for s in tds[1].split(" - ")]
                            return {
                                "area": area,
                                "area_name": platz_str[0],
                                "period": period_param,
                                "period_name": self.zeiten[int(period_param)],
                                "room": platz_str[1],
                                "year": jahr,
                                "month": monat,
                                "day": tag
                            }

        return None

    def find_free_seats(self, jahr, monat, tag, period_param, area):

        # URL Bauen und Request für Belegung der Etage an Server schicken
        scan_url = self.build_url(
            endpoint="day", year=jahr, month=monat, day=tag, area=area)
        resp = requests.get(scan_url).content.decode("utf-8")

        # Alle Freien Plätze extrahieren
        sitzplätze_html = BeautifulSoup(
            resp, "html.parser")
        sitzplätze_tags = sitzplätze_html.find_all("td", {"class": "new"})
        free_seats_url = [stag.find("a")["href"]
                          for stag in sitzplätze_tags]

        # Wenn der freie Platz für den gewüschten Zeitslot frei ist, der
        # liste von freien Plätzen der Etage hinzufügen
        plätze_in_area = list()
        for url in free_seats_url:
            if self.extract_param(url, "period") == str(period_param):
                # Platz-Struktur bauen (für die Buchung)
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
        # Wenn größer gleich 1 Plätze gefunden wurden, zurückgeben
        if len(plätze_in_area) != 0:
            return plätze_in_area
        # Wenn für keine der Etagen ein Plätz gefunden wurde, leere liste zurückgeben
        print("Bibot", self.index, "KEINE PLÄTZE")
        return []

    def platz_buchen(self, platz):
        platz_url = self.build_url(endpoint="edit_entry",
                                   area=platz["area"],
                                   period=platz["period"],
                                   room=platz["room"],
                                   year=platz["year"],
                                   month=platz["month"],
                                   day=platz["day"])
        speicher_url = self.build_url(endpoint="edit_entry_handler")
        platz_resp = self.session.get(platz_url).content.decode("utf-8")
        soup = BeautifulSoup(platz_resp, "html.parser")

        speichern_params = self.extract_form_params(soup=soup, form_id="main")
        buchung_abschicken = self.session.post(
            speicher_url, data=speichern_params).content.decode("utf-8")

        # Validieren ob für die gewünschte Periode ein Platz gebucht wurde
        soup = BeautifulSoup(buchung_abschicken, "html.parser")
        for td in soup.find_all("td", {"class": "K writable"}):
            # Nur zurückgeben, wenn tatsächlich gebucht wurde
            if str(self.zeiten.index(td.find("a")["title"])) == platz["period"]:
                print("Bibot", self.index, "Platz erfolgreich gebucht")
                return platz

        # Warsch wurde inzwichen zeit der platz belegt, sodass eine Buchung
        # nicht mehr möglich war. None wird zurückgeben
        print("Bibot", self.index, "Fehler bei Buchung")
        return None
