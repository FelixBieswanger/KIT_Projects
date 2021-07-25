from flask import Flask
from flask import request
import os
import json


app = Flask(__name__)

try:
    login_data = json.loads(os.environ.get("login_data", None))
except:
    with open(os.path.dirname(__file__)+"/../local_logindata.json", "r") as file:
        login_data = json.loads(file.read())


db = {
    "@2374109": {
        "ab": "14 oder 14:30",
        "area_name": "2. OG Altbau",
        "platz": "A420",
        "lastupdate": ""
    }
}


@app.route("/setplatz", methods=["POST"])
def set():

    user = request.args.get('username')
    pw = request.args.get("password")

    if user in login_data:
        if login_data[user]["password"] == pw:
            data = request.json
            db[user] = data
            return "1"
    return "0"


@app.route('/getplatz', methods=["GET"])
def get():
    user = request.args.get('username')

    if user in db:
        return db[user]
    else:
        return {}


if __name__ == '__main__':
    app.run(debug=True)
