class Platzholder:
    def __init__(self):
        self.final_platz = None

    def set(self, platz):
        if self.final_platz == None:
            self.final_platz = platz

    def get(self):
        return self.final_platz
