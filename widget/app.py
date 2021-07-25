from flask import Flask
from flask import request
import os
import json
from DataManager import DataManager

app = Flask(__name__)

try:
    login_data = json.loads(os.environ.get("login_data", None))
except:
    with open(os.path.dirname(__file__)+"/../local_logindata.json", "r") as file:
        login_data = json.loads(file.read())


@app.route('/getplatz', methods=["GET"])
def get():
    user = request.args.get('username')

    if user in login_data.keys():
        return DataManager.getPlatz(user=user)
    else:
        return {}


if __name__ == '__main__':
    app.run(debug=True)
