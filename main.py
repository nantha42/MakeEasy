from src.modules import *
from flask import Flask
import json


#app = Flask(__name__)
#
#
#@app.route("/")
#def home():
#    return "<p>Hello</p>"
#



if __name__ == '__main__':
    with open(".password.json", "r") as f:
        obj = json.load(f)
        user = obj["user"]
        password = obj["password"]
        project_name = obj["project_name"]
        db_name = obj["db_name"]

    #app = App(user, password, project_name, db_name)
    #customerid = app.add_user("Kannima Husband","1234567890",{})
    #debitid = app.add_debit(customer_id=customerid,amount=10000,reason="no interest")
