from src.modules import *
from flask import Flask
import json


app = Flask(__name__)


@app.route("/")
def home():
    return "<p>Hello</p>"




if __name__ == '__main__':

    #app = App(".password.json")
    #customerid = app.add_user("Kannima Husband","1234567890",{})
    #debitid = app.add_debit(customer_id=customerid,amount=10000,reason="no interest")
    pass
