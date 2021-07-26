
# Klasse die Speicherkopplung zwischen den Threads realisiert
import threading
from BibBot import BibBot


class Platzholder:
    def __init__(self):
        self.final_platz = None
        self.Lock = threading.Lock()
        self.stop = False
        self.seat_list = list()

    def set(self, platz):
        if self.final_platz == None:
            with self.Lock:
                self.final_platz = platz

    def add_seat(self, seat):
        if seat not in self.seat_list:
            # in prio adden
            self.seat_list.append(seat)

    def get_seats(self):
        self.seat_list = sorted(self.seat_list,
                                key=lambda x: BibBot.area_prio.index(x["area"]))
        return self.seat_list

    def get_available_seat_count(self):
        return len(self.seat_list)

    def get(self):
        return self.final_platz

    def set_threads_stop(self):
        self.stop = True

    def get_threds_stop(self):
        return self.stop
