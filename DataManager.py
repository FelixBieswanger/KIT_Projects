import json


class DataManager:

    def getPlatz(user):
        with open("db/"+user["username"]+".json", "r") as file:
            return json.loads(file)

    def setPlatz(user, data):
        with open("db/"+user["username"]+".json", "w") as file:
            file.seek(0)
            file.write(json.dumps(data))
            file.truncate()
