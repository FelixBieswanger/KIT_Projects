import json


class DataManager:

    def getPlatz(username):
        with open("db/"+username+".json", "r") as file:
            return json.loads(file.read())

    def setPlatz(username, data):
        with open("db/"+username+".json", "w") as file:
            file.seek(0)
            file.write(json.dumps(data))
            file.truncate()
