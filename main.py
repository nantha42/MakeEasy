from src.modules import *


#@app.route("/")
#def home():
#    return "<p>Hello</p>"
#

if __name__ == '__main__':
    # app = App(".password.json")
    # customerid = app.add_user("Kannima Husband","1234567890",{})
    app = App(".password.json")
    customerid = 1
    # debitid = app.add_debit_past(customer_id=customerid, time_str="2021:10:10", amount=10000, reason="no interest")
    app.get_user_debits(1, mode="production")
    pass
